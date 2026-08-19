"""Build tiny synthetic BAMs with known MM/ML, HP/PS and alleles.

Every test in this repository runs against these fixtures, never against a real BAM. The
real inputs are 80-300 GB, read-only, and owned by other users; a test suite that touches
them is neither fast, nor reproducible, nor safe.

MM/ML encoding
--------------
``MM:Z:C+m?,<d0>,<d1>,...;C+h?,<d0>,<d1>,...;`` where each ``d`` counts the C bases
*skipped* before the next modified C. ``ML:B:C,<q0>,<q1>,...`` concatenates the
probabilities of every MM entry in order, as bytes.

Here every C in the read is modified, so all deltas are 0 and the two code blocks are the
same length. That keeps the fixture readable while still exercising the two-code path.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence

import pysam

DEFAULT_CONTIG = "chr1"
DEFAULT_CONTIG_LENGTH = 20_000


def make_reference_sequence(length: int = 2_000, seed_motif: str = "ACGTACGCGTTA") -> str:
    """A deterministic sequence with a healthy CpG density."""
    repeats = (length // len(seed_motif)) + 1
    return (seed_motif * repeats)[:length]


class SyntheticRead:
    """One read to place into a fixture BAM."""

    def __init__(
        self,
        name: str,
        start: int,
        sequence: str,
        haplotype: Optional[int] = None,
        phase_set: Optional[int] = None,
        prob_5mc: Optional[Sequence[float]] = None,
        prob_5hmc: Optional[Sequence[float]] = None,
        mapping_quality: int = 60,
        base_quality: int = 30,
        with_modifications: bool = True,
        is_reverse: bool = False,
        is_secondary: bool = False,
        is_supplementary: bool = False,
        is_duplicate: bool = False,
    ):
        self.name = name
        self.start = start
        self.sequence = sequence
        self.haplotype = haplotype
        self.phase_set = phase_set
        self.prob_5mc = prob_5mc
        self.prob_5hmc = prob_5hmc
        self.mapping_quality = mapping_quality
        self.base_quality = base_quality
        self.with_modifications = with_modifications
        self.is_reverse = is_reverse
        self.is_secondary = is_secondary
        self.is_supplementary = is_supplementary
        self.is_duplicate = is_duplicate

    def cytosine_positions(self) -> List[int]:
        return [i for i, base in enumerate(self.sequence) if base == "C"]


def _encode_ml_byte(probability: float) -> int:
    """Inverse of the decoder in ``src.methylation.mod_bases``: ``floor(p * 256)``, capped."""
    return max(0, min(255, int(probability * 256)))


def _build_mm_ml(read: SyntheticRead):
    cytosines = read.cytosine_positions()
    if not cytosines:
        return None, None

    n = len(cytosines)
    prob_5mc = list(read.prob_5mc) if read.prob_5mc is not None else [0.9] * n
    prob_5hmc = list(read.prob_5hmc) if read.prob_5hmc is not None else [0.02] * n
    if len(prob_5mc) != n or len(prob_5hmc) != n:
        raise ValueError(
            f"read {read.name}: expected {n} probabilities per code, "
            f"got {len(prob_5mc)} 5mC and {len(prob_5hmc)} 5hmC"
        )

    deltas = ",".join("0" for _ in cytosines)  # every C is modified
    mm = f"C+m?,{deltas};C+h?,{deltas};"
    ml = [_encode_ml_byte(p) for p in prob_5mc] + [_encode_ml_byte(p) for p in prob_5hmc]
    return mm, ml


def write_bam(
    path: str,
    reads: Sequence[SyntheticRead],
    contig: str = DEFAULT_CONTIG,
    contig_length: int = DEFAULT_CONTIG_LENGTH,
) -> str:
    """Write and index a BAM containing ``reads``. Returns the BAM path."""
    header = {
        "HD": {"VN": "1.6", "SO": "coordinate"},
        "SQ": [{"SN": contig, "LN": contig_length}],
    }
    ordered = sorted(reads, key=lambda r: (r.start, r.name))

    with pysam.AlignmentFile(path, "wb", header=header) as out:
        for read in ordered:
            out.write(_to_segment(read, out.header))

    pysam.index(path)
    return path


def _to_segment(read: SyntheticRead, header) -> pysam.AlignedSegment:
    segment = pysam.AlignedSegment(header)
    segment.query_name = read.name
    segment.query_sequence = read.sequence
    segment.flag = 0
    if read.is_reverse:
        segment.flag |= 16
    if read.is_secondary:
        segment.flag |= 256
    if read.is_duplicate:
        segment.flag |= 1024
    if read.is_supplementary:
        segment.flag |= 2048
    segment.reference_id = 0
    segment.reference_start = read.start
    segment.mapping_quality = read.mapping_quality
    segment.cigar = [(0, len(read.sequence))]  # all match, so query pos == ref offset
    segment.query_qualities = pysam.qualitystring_to_array(
        chr(33 + read.base_quality) * len(read.sequence)
    )

    if read.haplotype is not None:
        segment.set_tag("HP", read.haplotype, value_type="i")
    if read.phase_set is not None:
        segment.set_tag("PS", read.phase_set, value_type="i")

    if read.with_modifications:
        mm, ml = _build_mm_ml(read)
        if mm is not None:
            segment.set_tag("MM", mm, value_type="Z")
            segment.set_tag("ML", ml)

    return segment


def simple_fixture(
    tmpdir: str,
    contig: str = DEFAULT_CONTIG,
    reference: Optional[str] = None,
) -> Dict[str, object]:
    """A small, fully-specified scenario used by most tests.

    Six reads at a single candidate locus, covering the interesting cases:

    ================  ====  ====  ============  =========================================
    read              HP    MM    allele        exercises
    ================  ====  ====  ============  =========================================
    ``hap1_alt``      1     yes   ALT (T)       the usable, tumor-like case
    ``hap1_ref``      1     yes   REF           usable, reference allele
    ``hap2_alt``      2     yes   ALT (T)       second haplotype family
    ``no_hp``         -     yes   ALT (T)       ``no_haplotype_tag``
    ``no_mm``         1     no    ALT (T)       ``no_methylation_tag``
    ``low_mapq``      1     yes   ALT (T)       ``low_mapping_quality`` (MAPQ 0)
    ================  ====  ====  ============  =========================================

    The candidate sits at 1-based position ``start + 51`` where the reference base is C and
    the ALT reads carry T, so allele reading is unambiguous.
    """
    reference = reference or make_reference_sequence(600)
    start = 1_000
    length = 400
    candidate_offset = 50

    def sequence_with(allele: str) -> str:
        seq = list(reference[:length])
        seq[candidate_offset] = allele
        return "".join(seq)

    ref_base = reference[candidate_offset]
    alt_base = "T" if ref_base != "T" else "A"

    reads = [
        SyntheticRead("hap1_alt", start, sequence_with(alt_base), haplotype=1, phase_set=777),
        SyntheticRead("hap1_ref", start, sequence_with(ref_base), haplotype=1, phase_set=777),
        SyntheticRead("hap2_alt", start, sequence_with(alt_base), haplotype=2, phase_set=777),
        SyntheticRead("no_hp", start, sequence_with(alt_base)),
        SyntheticRead(
            "no_mm", start, sequence_with(alt_base), haplotype=1, phase_set=777,
            with_modifications=False,
        ),
        SyntheticRead(
            "low_mapq", start, sequence_with(alt_base), haplotype=1, phase_set=777,
            mapping_quality=0,
        ),
    ]

    bam_path = write_bam(os.path.join(tmpdir, "synthetic.bam"), reads, contig=contig)

    return {
        "bam": bam_path,
        "contig": contig,
        "reads": reads,
        "candidate_position": start + candidate_offset + 1,  # 1-based
        "ref_base": ref_base,
        "alt_base": alt_base,
        "region_start": start,
        "region_end": start + length,
    }
