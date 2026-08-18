"""Assemble joint-molecule records for one region.

Pipeline per region::

    candidate loci in region
      → fetch overlapping reads (never the whole BAM)
      → read allele at the candidate position
      → read HP/PS
      → read MM/ML
      → apply quality checks in a fixed order
      → emit one record per (read, candidate), usable or not

Design notes
------------
* **Pileup, not per-read CIGAR walking, for the allele.** ``pysam.pileup`` handles CIGAR,
  indels and reference skips correctly and gives both the base and its quality. Walking
  ``get_aligned_pairs`` per candidate would repeat that work once per locus.
* **The query→reference map is built once per read and reused** across every candidate
  that read overlaps. On ONT reads of 10-50 kb overlapping several candidates this is the
  difference between one CIGAR walk and several.
* **Nothing is filtered away silently.** Every examined (read, candidate) pair produces a
  row. The funnel is a ``GROUP BY exclusion_reason`` over these rows.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional

from ..io.regions import Region
from ..methylation.mod_bases import (
    CpGEvidence,
    build_query_to_reference,
    read_cpg_evidence,
    summarize_calls,
)
from ..phasing.haplotype import read_haplotype
from .record import ExclusionReason, JointMoleculeRecord

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Candidate:
    """A candidate locus. ``position`` is 1-based, matching VCF."""

    chrom: str
    position: int
    ref: str
    alt: str

    @property
    def id(self) -> str:
        return f"{self.chrom}:{self.position}:{self.ref}>{self.alt}"

    @property
    def position0(self) -> int:
        return self.position - 1


@dataclass(frozen=True)
class ExtractionConfig:
    """Filters and thresholds. Every value is required — nothing defaults inside ``src/``.

    ``read_end_exclusion_bp`` drops CpGs near read ends (PAPER-003); ``min_cpg_per_read`` is
    applied *after* that exclusion, so a read whose only CpGs sit at its ends is correctly
    counted as ``insufficient_cpgs`` rather than as methylation-informative.
    """

    min_mapping_quality: int
    min_allele_quality: int
    min_cpg_per_read: int
    read_end_exclusion_bp: int
    methylation_call_threshold: float
    require_haplotype: bool = True
    require_methylation: bool = True

    @classmethod
    def from_dict(cls, cfg: Dict) -> "ExtractionConfig":
        """Build from a config mapping, raising on any missing required threshold.

        A missing threshold is a hard stop rather than a default, per
        ``docs/research/03_hypotheses.md`` — a defaulted threshold is an unrecorded
        research decision.
        """
        required = [
            "min_mapping_quality",
            "min_allele_quality",
            "min_cpg_per_read",
            "read_end_exclusion_bp",
            "methylation_call_threshold",
        ]
        missing = [key for key in required if cfg.get(key) is None]
        if missing:
            raise ValueError(
                "extraction config is missing required threshold(s): "
                + ", ".join(sorted(missing))
                + " — set them explicitly in config/experiments/<experiment>.yaml"
            )
        return cls(
            min_mapping_quality=int(cfg["min_mapping_quality"]),
            min_allele_quality=int(cfg["min_allele_quality"]),
            min_cpg_per_read=int(cfg["min_cpg_per_read"]),
            read_end_exclusion_bp=int(cfg["read_end_exclusion_bp"]),
            methylation_call_threshold=float(cfg["methylation_call_threshold"]),
            require_haplotype=bool(cfg.get("require_haplotype", True)),
            require_methylation=bool(cfg.get("require_methylation", True)),
        )


def extract_region(
    bam,
    region: Region,
    candidates: Iterable[Candidate],
    config: ExtractionConfig,
    sample_id: str,
    dilution: str,
    tool_versions: str = "",
    input_manifest_id: str = "",
    source_labels: Optional[Dict[str, str]] = None,
) -> List[JointMoleculeRecord]:
    """Build every joint-molecule record for one region.

    ``bam`` is an open ``pysam.AlignmentFile``. ``source_labels`` maps read id → ``tumor`` /
    ``normal``; it is evaluation-only metadata and is never consulted by any filter here.

    Records are returned sorted, so writing them produces a byte-reproducible partition.
    """
    in_region = [
        c
        for c in candidates
        if c.chrom == region.chrom and region.start <= c.position0 < region.end
    ]
    if not in_region:
        return []

    records: List[JointMoleculeRecord] = []
    query_maps: Dict[str, Dict[int, int]] = {}
    cpg_cache: Dict[str, CpGEvidence] = {}
    source_labels = source_labels or {}

    for candidate in in_region:
        for pileup_read in _pileup_at(bam, candidate):
            read = pileup_read.alignment
            record = JointMoleculeRecord(
                sample_id=sample_id,
                dilution=dilution,
                chrom=candidate.chrom,
                region_id=region.id,
                candidate_id=candidate.id,
                candidate_position=candidate.position,
                read_id=read.query_name,
                source_label_for_evaluation_only=source_labels.get(read.query_name, ""),
                mapping_quality=read.mapping_quality,
                read_length=read.query_length,
                tool_versions=tool_versions,
                input_manifest_id=input_manifest_id,
            )
            _populate(record, pileup_read, read, config, query_maps, cpg_cache)
            records.append(record)

    records.sort(key=lambda r: r.sort_key)
    return records


def _pileup_at(bam, candidate: Candidate):
    """Yield pileup reads at exactly one reference position.

    ``truncate=True`` restricts columns to the requested window; ``max_depth`` is set high
    because ONT coverage at a candidate can exceed pysam's default cap, and silently
    truncating depth would corrupt every funnel denominator.
    """
    for column in bam.pileup(
        candidate.chrom,
        candidate.position0,
        candidate.position0 + 1,
        truncate=True,
        stepper="nofilter",
        min_base_quality=0,
        max_depth=1_000_000,
    ):
        if column.reference_pos != candidate.position0:
            continue
        for pileup_read in column.pileups:
            yield pileup_read


def _populate(
    record: JointMoleculeRecord,
    pileup_read,
    read,
    config: ExtractionConfig,
    query_maps: Dict[str, Dict[int, int]],
    cpg_cache: Dict[str, CpGEvidence],
) -> None:
    """Run the checks in :data:`ExclusionReason.ORDER`, stopping at the first failure.

    The order is fixed so that stage survival rates partition cleanly and the funnel's
    stages sum to the total.
    """
    if read.is_secondary or read.is_supplementary:
        record.exclusion_reason = ExclusionReason.SECONDARY_OR_SUPPLEMENTARY
        return
    if read.is_unmapped:
        record.exclusion_reason = ExclusionReason.UNMAPPED
        return
    if read.is_duplicate or read.is_qcfail:
        record.exclusion_reason = ExclusionReason.DUPLICATE_OR_QCFAIL
        return
    if (read.mapping_quality or 0) < config.min_mapping_quality:
        record.exclusion_reason = ExclusionReason.LOW_MAPPING_QUALITY
        return

    # --- allele ---------------------------------------------------------------
    if pileup_read.is_del or pileup_read.is_refskip or pileup_read.query_position is None:
        record.observed_allele = "-" if pileup_read.is_del else ""
        record.exclusion_reason = ExclusionReason.ALLELE_NOT_ALIGNED
        return

    query_position = pileup_read.query_position
    record.observed_allele = read.query_sequence[query_position]
    qualities = read.query_qualities
    record.allele_quality = int(qualities[query_position]) if qualities is not None else None

    if record.allele_quality is not None and record.allele_quality < config.min_allele_quality:
        record.exclusion_reason = ExclusionReason.LOW_ALLELE_QUALITY
        return

    # --- haplotype ------------------------------------------------------------
    haplotype = read_haplotype(read)
    record.haplotype_tag = haplotype.haplotype
    record.phase_set = haplotype.phase_set
    record.haplotype_confidence_if_available = haplotype.confidence
    if config.require_haplotype and not haplotype.is_haplotagged:
        record.exclusion_reason = ExclusionReason.NO_HAPLOTYPE_TAG
        return

    # --- methylation ----------------------------------------------------------
    evidence = cpg_cache.get(read.query_name)
    if evidence is None:
        query_map = query_maps.get(read.query_name)
        if query_map is None:
            query_map = build_query_to_reference(read)
            query_maps[read.query_name] = query_map
        evidence = read_cpg_evidence(read, query_map)
        cpg_cache[read.query_name] = evidence

    if len(evidence) == 0:
        if config.require_methylation:
            record.exclusion_reason = ExclusionReason.NO_METHYLATION_TAG
            return
    else:
        usable_cpgs = evidence.with_reference_positions().exclude_read_ends(
            config.read_end_exclusion_bp
        )
        record.cpg_positions = [p for p in usable_cpgs.ref_positions if p is not None]
        record.methylation_probabilities = list(usable_cpgs.prob_5mc)
        record.methylation_probabilities_5hmc = list(usable_cpgs.prob_5hmc)
        record.distance_of_cpgs_to_read_ends = list(usable_cpgs.distance_to_read_end)
        methylated, unmethylated = summarize_calls(
            usable_cpgs, config.methylation_call_threshold
        )
        record.methylated_cpg_count = methylated
        record.unmethylated_cpg_count = unmethylated

        if len(usable_cpgs) < config.min_cpg_per_read:
            record.exclusion_reason = ExclusionReason.INSUFFICIENT_CPGS
            return

    record.usable = 1


def iter_candidates_from_tsv(path: str) -> Iterator[Candidate]:
    """Read candidates from the ``candidate_pass_snvs.tsv`` written by ``src.candidates``.

    Reusing that table is deliberate: the upstream ClairS-TO characterization stays the
    single definition of what a candidate locus is.
    """
    with open(path) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        index = {name: i for i, name in enumerate(header)}
        for required in ("chrom", "pos", "ref", "alt"):
            if required not in index:
                raise ValueError(f"{path}: candidate table lacks a {required!r} column")
        for line in fh:
            cells = line.rstrip("\n").split("\t")
            yield Candidate(
                chrom=cells[index["chrom"]],
                position=int(cells[index["pos"]]),
                ref=cells[index["ref"]],
                alt=cells[index["alt"]],
            )
