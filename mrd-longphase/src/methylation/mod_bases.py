"""Parse ONT MM/ML modified-base tags into per-CpG evidence on one read.

Background
----------
Dorado 5mCG/5hmCG basecalling writes two modification codes at every called CpG:

    MM:Z:C+m?,<deltas...>   ML:B:C,<quals...>    5-methylcytosine
    MM:Z:C+h?,<deltas...>   ML:B:C,<quals...>    5-hydroxymethylcytosine

pysam exposes these as ``AlignedSegment.modified_bases``::

    {('C', strand, 'm'): [(query_pos, qual), ...],
     ('C', strand, 'h'): [(query_pos, qual), ...]}

where ``strand`` is 0 for the read's forward strand, ``query_pos`` indexes the stored
(aligned-orientation) query sequence, and ``qual`` is a 0-255 scaled probability.

Probability convention
----------------------
ONT scales a probability ``p`` into a byte as ``floor(p * 256)`` clamped to 255, so the
byte ``q`` represents the interval ``[q/256, (q+1)/256)``. We decode to the interval
midpoint, ``(q + 0.5) / 256``, rather than ``q / 256``: the midpoint is the minimum-error
point estimate and, unlike ``q/256``, it cannot return exactly 0.0 for a base that was in
fact assigned nonzero probability.

The two codes are complementary, not independent: ``P(5mC) + P(5hmC) <= 1`` and the
remainder is ``P(unmodified)``. They are therefore returned separately and never summed.

What this module does not do
----------------------------
It applies no thresholds of its own and calls nothing methylated. Thresholds arrive from
experiment configuration and are applied in :func:`summarize_calls` by an explicit caller.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

MOD_5MC = "m"
MOD_5HMC = "h"

# ONT scales probabilities into a byte; decode to the represented interval's midpoint.
_ML_SCALE = 256.0


@dataclass
class CpGEvidence:
    """Per-CpG methylation evidence for one read, aligned to reference coordinates.

    All four lists are parallel and index-aligned. ``ref_positions`` may contain ``None``
    for a modified base that falls in an insertion (no reference coordinate); callers that
    need reference-anchored CpGs should use :meth:`with_reference_positions`.
    """

    read_id: str
    ref_positions: List[Optional[int]] = field(default_factory=list)
    query_positions: List[int] = field(default_factory=list)
    prob_5mc: List[float] = field(default_factory=list)
    prob_5hmc: List[float] = field(default_factory=list)
    distance_to_read_end: List[int] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.query_positions)

    def with_reference_positions(self) -> "CpGEvidence":
        """Drop CpGs that have no reference coordinate (insertions, soft-clipped bases)."""
        keep = [i for i, pos in enumerate(self.ref_positions) if pos is not None]
        return CpGEvidence(
            read_id=self.read_id,
            ref_positions=[self.ref_positions[i] for i in keep],
            query_positions=[self.query_positions[i] for i in keep],
            prob_5mc=[self.prob_5mc[i] for i in keep],
            prob_5hmc=[self.prob_5hmc[i] for i in keep],
            distance_to_read_end=[self.distance_to_read_end[i] for i in keep],
        )

    def exclude_read_ends(self, exclusion_bp: int) -> "CpGEvidence":
        """Drop CpGs within ``exclusion_bp`` of either read end.

        PAPER-003 flags read-end methylation as systematically less reliable. The window is
        configuration, not a constant, because the paper has not yet been verified at PDF
        level (see ``docs/research/01_paper_patterns.md``).
        """
        if exclusion_bp <= 0:
            return self
        keep = [i for i, d in enumerate(self.distance_to_read_end) if d >= exclusion_bp]
        return CpGEvidence(
            read_id=self.read_id,
            ref_positions=[self.ref_positions[i] for i in keep],
            query_positions=[self.query_positions[i] for i in keep],
            prob_5mc=[self.prob_5mc[i] for i in keep],
            prob_5hmc=[self.prob_5hmc[i] for i in keep],
            distance_to_read_end=[self.distance_to_read_end[i] for i in keep],
        )


def _decode_ml(qual: int) -> float:
    """Decode a 0-255 ML byte to the midpoint of the probability interval it represents."""
    return (qual + 0.5) / _ML_SCALE


def read_cpg_evidence(read, ref_position_of_query: Optional[Dict[int, int]] = None) -> CpGEvidence:
    """Extract per-CpG 5mC/5hmC evidence from one ``pysam.AlignedSegment``.

    Parameters
    ----------
    read
        A ``pysam.AlignedSegment`` that may carry MM/ML tags.
    ref_position_of_query
        Optional query-position → reference-position map. Supplying a shared map avoids
        rebuilding the CIGAR walk once per candidate when a read overlaps several loci.
        When omitted it is built here from ``read.get_aligned_pairs(matches_only=True)``.

    Returns an empty :class:`CpGEvidence` when the read carries no modification tags.
    """
    evidence = CpGEvidence(read_id=read.query_name)

    modified = read.modified_bases
    if not modified:
        return evidence

    per_position = _collect_by_query_position(modified)
    if not per_position:
        return evidence

    if ref_position_of_query is None:
        ref_position_of_query = build_query_to_reference(read)

    query_length = read.query_length or len(read.query_sequence or "")

    for query_pos in sorted(per_position):
        probs = per_position[query_pos]
        evidence.query_positions.append(query_pos)
        evidence.ref_positions.append(ref_position_of_query.get(query_pos))
        evidence.prob_5mc.append(probs.get(MOD_5MC, 0.0))
        evidence.prob_5hmc.append(probs.get(MOD_5HMC, 0.0))
        evidence.distance_to_read_end.append(
            min(query_pos, max(query_length - 1 - query_pos, 0)) if query_length else 0
        )
    return evidence


def _collect_by_query_position(modified) -> Dict[int, Dict[str, float]]:
    """Group pysam's per-(base, strand, code) lists into one dict per query position.

    Both codes report at the same positions, so grouping lets a CpG carry P(5mC) and
    P(5hmC) together instead of being split across two parallel structures.
    """
    per_position: Dict[int, Dict[str, float]] = {}
    for key, calls in modified.items():
        code = _normalize_code(key)
        if code is None:
            continue  # a modification this project does not model
        for query_pos, qual in calls:
            if qual is None or qual < 0:
                continue  # '.' in MM means "not called here", not "probability zero"
            per_position.setdefault(query_pos, {})[code] = _decode_ml(qual)
    return per_position


def _normalize_code(key: Tuple) -> Optional[str]:
    """Map a pysam modified_bases key to ``'m'``/``'h'``, or None if not a CpG modification.

    pysam reports the code as a str (``'m'``) or, for ChEBI-coded modifications, an int.
    Only 5mC and 5hmC are modelled here.
    """
    code = key[2] if len(key) >= 3 else None
    if code in (MOD_5MC, MOD_5HMC):
        return code
    return None


def build_query_to_reference(read) -> Dict[int, int]:
    """Map query positions to reference positions for aligned (non-indel) bases."""
    return {
        query_pos: ref_pos
        for query_pos, ref_pos in read.get_aligned_pairs(matches_only=True)
        if query_pos is not None and ref_pos is not None
    }


def summarize_calls(evidence: CpGEvidence, call_threshold: float) -> Tuple[int, int]:
    """Count confidently methylated and confidently unmethylated CpGs by P(5mC).

    Returns ``(methylated, unmethylated)``. These do **not** sum to ``len(evidence)``:
    CpGs whose probability falls in the ambiguous band between the thresholds are counted
    in neither, and that difference is the read's ambiguity mass. Dropping it would make
    a read with 100 uncertain CpGs indistinguishable from one with 100 confident ones.

    ``call_threshold`` must come from experiment configuration.
    """
    if not 0.5 <= call_threshold <= 1.0:
        raise ValueError(
            f"call_threshold must lie in [0.5, 1.0], got {call_threshold}"
        )
    methylated = sum(1 for p in evidence.prob_5mc if p >= call_threshold)
    unmethylated = sum(1 for p in evidence.prob_5mc if p <= 1.0 - call_threshold)
    return methylated, unmethylated
