"""The joint-molecule record — one read × one candidate locus.

The field list and its ordering are the data contract documented in
``docs/joint_molecule_schema.md``. Both are defined once, here, so the writer, the reader,
the funnel, and the tests cannot drift apart.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

#: TSV column order. Changing this is a schema change: bump the version in the run manifest.
FIELDS: List[str] = [
    "sample_id",
    "dilution",
    "source_label_for_evaluation_only",
    "chrom",
    "region_id",
    "candidate_id",
    "candidate_position",
    "read_id",
    "observed_allele",
    "allele_quality",
    "mapping_quality",
    "read_length",
    "phase_set",
    "haplotype_tag",
    "haplotype_confidence_if_available",
    "cpg_positions",
    "methylation_probabilities",
    "methylation_probabilities_5hmc",
    "methylated_cpg_count",
    "unmethylated_cpg_count",
    "distance_of_cpgs_to_read_ends",
    "usable",
    "exclusion_reason",
    "tool_versions",
    "input_manifest_id",
]

SCHEMA_VERSION = "1.0.0"

#: Separator inside list-valued columns. See the storage trade-off in the schema doc.
LIST_SEP = ";"

#: Columns that must never reach a model. Asserted by tests/unit/test_leakage.py.
EVALUATION_ONLY_FIELDS = frozenset({"source_label_for_evaluation_only", "dilution"})


class ExclusionReason:
    """Exclusion reasons, evaluated in this order so the funnel is a strict partition."""

    SECONDARY_OR_SUPPLEMENTARY = "secondary_or_supplementary"
    UNMAPPED = "unmapped"
    DUPLICATE_OR_QCFAIL = "duplicate_or_qcfail"
    LOW_MAPPING_QUALITY = "low_mapping_quality"
    ALLELE_NOT_ALIGNED = "allele_not_aligned"
    LOW_ALLELE_QUALITY = "low_allele_quality"
    NO_HAPLOTYPE_TAG = "no_haplotype_tag"
    NO_METHYLATION_TAG = "no_methylation_tag"
    INSUFFICIENT_CPGS = "insufficient_cpgs"

    #: Funnel stage order, from "all reads examined" to "usable joint molecule".
    ORDER: List[str] = [
        SECONDARY_OR_SUPPLEMENTARY,
        UNMAPPED,
        DUPLICATE_OR_QCFAIL,
        LOW_MAPPING_QUALITY,
        ALLELE_NOT_ALIGNED,
        LOW_ALLELE_QUALITY,
        NO_HAPLOTYPE_TAG,
        NO_METHYLATION_TAG,
        INSUFFICIENT_CPGS,
    ]


@dataclass
class JointMoleculeRecord:
    """One read's evidence at one candidate locus.

    A record is emitted whether or not it is usable: ``usable=0`` rows carry the first
    failed check in ``exclusion_reason``, which is what makes the feasibility funnel a
    ``GROUP BY`` over this table rather than a separate pipeline.
    """

    sample_id: str
    dilution: str
    chrom: str
    region_id: str
    candidate_id: str
    candidate_position: int
    read_id: str
    source_label_for_evaluation_only: str = ""
    observed_allele: str = ""
    allele_quality: Optional[int] = None
    mapping_quality: Optional[int] = None
    read_length: Optional[int] = None
    phase_set: Optional[int] = None
    haplotype_tag: Optional[int] = None
    haplotype_confidence_if_available: Optional[float] = None
    cpg_positions: List[int] = field(default_factory=list)
    methylation_probabilities: List[float] = field(default_factory=list)
    methylation_probabilities_5hmc: List[float] = field(default_factory=list)
    methylated_cpg_count: Optional[int] = None
    unmethylated_cpg_count: Optional[int] = None
    distance_of_cpgs_to_read_ends: List[int] = field(default_factory=list)
    usable: int = 0
    exclusion_reason: str = ""
    tool_versions: str = ""
    input_manifest_id: str = ""

    @property
    def sort_key(self):
        """Deterministic ordering within a partition: position, then read, then candidate."""
        return (self.candidate_position, self.read_id, self.candidate_id)

    def to_row(self) -> List[str]:
        """Render to TSV cells in :data:`FIELDS` order.

        Floats are fixed to 3 decimal places so a re-run byte-reproduces its partition.
        """
        return [
            self.sample_id,
            self.dilution,
            self.source_label_for_evaluation_only,
            self.chrom,
            self.region_id,
            self.candidate_id,
            str(self.candidate_position),
            self.read_id,
            self.observed_allele,
            _num(self.allele_quality),
            _num(self.mapping_quality),
            _num(self.read_length),
            _num(self.phase_set),
            _num(self.haplotype_tag),
            _num(self.haplotype_confidence_if_available),
            _int_list(self.cpg_positions),
            _float_list(self.methylation_probabilities),
            _float_list(self.methylation_probabilities_5hmc),
            _num(self.methylated_cpg_count),
            _num(self.unmethylated_cpg_count),
            _int_list(self.distance_of_cpgs_to_read_ends),
            str(self.usable),
            self.exclusion_reason,
            self.tool_versions,
            self.input_manifest_id,
        ]


def _num(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _int_list(values: List[int]) -> str:
    return LIST_SEP.join(str(v) for v in values)


def _float_list(values: List[float]) -> str:
    return LIST_SEP.join(f"{v:.3f}" for v in values)


def parse_int_list(cell: str) -> List[int]:
    """Inverse of :func:`_int_list`. Empty cell means empty list, never ``[0]``."""
    return [int(v) for v in cell.split(LIST_SEP)] if cell else []


def parse_float_list(cell: str) -> List[float]:
    return [float(v) for v in cell.split(LIST_SEP)] if cell else []
