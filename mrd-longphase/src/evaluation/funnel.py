"""The feasibility funnel — the first scientific decision of the project.

H1 asks whether enough reads carry allele, haplotype **and** methylation information at the
same time. This module answers it by counting, and by counting in a way that cannot
accidentally overstate the answer.

The funnel::

    all examined (read × candidate) pairs
      → candidate-overlapping reads
      → allele-informative
      → haplotagged
      → methylation-informative
      → usable joint-evidence molecules

Why it is a GROUP BY, not a pipeline
------------------------------------
``src.joint_evidence`` emits a row for *every* examined pair, usable or not, tagging the
**first** failed check in ``exclusion_reason``. Because the checks run in a fixed order, the
exclusion reasons partition the examined pairs exactly, so stage counts are derived by
grouping rather than by re-running filters. A separately-implemented funnel could drift
from the extractor it is supposed to describe; this one cannot.

What it deliberately does not do
--------------------------------
It reports no rate without its denominator, and it does not multiply per-stage rates
together. Read length drives both CpG count and haplotagging probability, so the stages are
correlated and the product of their individual rates is not the joint survival. Only the
observed joint count is reported as the joint count.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

from ..joint_evidence.record import ExclusionReason

#: Funnel stages, in order. Each stage counts pairs that reached it.
STAGES: List[str] = [
    "examined",
    "candidate_overlapping",
    "allele_informative",
    "haplotagged",
    "methylation_informative",
    "usable_joint_molecules",
]

#: Which exclusion reasons remove a pair *before* each stage is reached.
_STAGE_BLOCKERS: Dict[str, Sequence[str]] = {
    "candidate_overlapping": (
        ExclusionReason.SECONDARY_OR_SUPPLEMENTARY,
        ExclusionReason.UNMAPPED,
        ExclusionReason.DUPLICATE_OR_QCFAIL,
        ExclusionReason.LOW_MAPPING_QUALITY,
    ),
    "allele_informative": (
        ExclusionReason.ALLELE_NOT_ALIGNED,
        ExclusionReason.LOW_ALLELE_QUALITY,
    ),
    "haplotagged": (ExclusionReason.NO_HAPLOTYPE_TAG,),
    "methylation_informative": (
        ExclusionReason.NO_METHYLATION_TAG,
        ExclusionReason.INSUFFICIENT_CPGS,
    ),
}


@dataclass
class FunnelCounts:
    """Stage counts and exclusion reasons for one stratum."""

    stage_counts: Dict[str, int] = field(default_factory=lambda: {s: 0 for s in STAGES})
    exclusions: Counter = field(default_factory=Counter)

    def survival(self, stage: str) -> float:
        """Fraction of examined pairs surviving to ``stage``. NaN when nothing was examined."""
        examined = self.stage_counts["examined"]
        return self.stage_counts[stage] / examined if examined else float("nan")

    def as_dict(self) -> Dict[str, object]:
        return {
            "stage_counts": dict(self.stage_counts),
            "stage_survival": {s: self.survival(s) for s in STAGES},
            "exclusions": dict(sorted(self.exclusions.items())),
        }


def count_funnel(records: Iterable) -> FunnelCounts:
    """Count one flat collection of joint-molecule records.

    Accepts either :class:`~src.joint_evidence.record.JointMoleculeRecord` objects or the
    string dicts returned by ``JointEvidenceStore.read_partition``, so the funnel can be
    recomputed from written partitions without re-extracting.
    """
    counts = FunnelCounts()
    for record in records:
        reason = _get(record, "exclusion_reason") or ""
        counts.stage_counts["examined"] += 1
        if reason:
            counts.exclusions[reason] += 1
        for stage in STAGES[1:]:
            if _reached(stage, reason):
                counts.stage_counts[stage] += 1
    return counts


def _reached(stage: str, reason: str) -> bool:
    """True when a pair excluded for ``reason`` still reached ``stage``.

    A pair reaches a stage if its exclusion reason is not a blocker for that stage or any
    earlier one. Walking the stage list makes the containment explicit rather than relying
    on the reasons' textual order.
    """
    if not reason:
        return True
    for candidate_stage in STAGES[1:]:
        if reason in _STAGE_BLOCKERS.get(candidate_stage, ()):  # blocked here
            return STAGES.index(candidate_stage) > STAGES.index(stage)
    # An exclusion reason with no registered blocker stage. Counting it as surviving would
    # silently inflate the usable count, which is the one number H1 turns on, so refuse.
    raise ValueError(
        f"exclusion_reason {reason!r} is not mapped to a funnel stage; "
        "add it to _STAGE_BLOCKERS when adding a new check"
    )


def stratified_funnel(records: Iterable, by: Sequence[str]) -> Dict[tuple, FunnelCounts]:
    """Funnel counts grouped by one or more record fields.

    ``by`` names record attributes/keys, e.g. ``("dilution",)`` or
    ``("dilution", "candidate_id")``. H1 requires reporting by sample, dilution,
    chromosome/region, candidate, phase set, and haplotype family.
    """
    grouped: Dict[tuple, List] = defaultdict(list)
    for record in records:
        key = tuple(_stratum_value(record, field_name) for field_name in by)
        grouped[key].append(record)
    return {key: count_funnel(rows) for key, rows in sorted(grouped.items(), key=_sort_key)}


def _sort_key(item):
    return tuple(str(part) for part in item[0])


def _stratum_value(record, field_name: str):
    """Resolve a stratum value, including the derived ``haplotype_family``.

    ``haplotype_family`` is ``phase_set:haplotype``. Grouping on ``haplotype_tag`` alone
    would pool haplotype 1 of unrelated phase blocks, which are independently oriented and
    have no relationship to each other.
    """
    if field_name == "haplotype_family":
        phase_set = _get(record, "phase_set")
        haplotype = _get(record, "haplotype_tag")
        if phase_set in (None, "") or haplotype in (None, ""):
            return ""
        return f"{phase_set}:{haplotype}"
    value = _get(record, field_name)
    return "" if value is None else value


def _get(record, name: str):
    if isinstance(record, dict):
        return record.get(name)
    return getattr(record, name, None)


@dataclass
class MethylationProfile:
    """Distributional facts H1 requires beyond the stage counts."""

    cpgs_per_read: List[int] = field(default_factory=list)
    read_lengths: List[int] = field(default_factory=list)
    read_end_distances: List[int] = field(default_factory=list)
    reads_with_missing_methylation: int = 0
    reads_total: int = 0

    @property
    def methylation_missingness(self) -> float:
        return (
            self.reads_with_missing_methylation / self.reads_total
            if self.reads_total
            else float("nan")
        )

    def summary(self) -> Dict[str, object]:
        return {
            "reads_total": self.reads_total,
            "methylation_missingness": self.methylation_missingness,
            "cpgs_per_read": _describe(self.cpgs_per_read),
            "read_length": _describe(self.read_lengths),
            "cpg_distance_to_read_end": _describe(self.read_end_distances),
        }


def profile_methylation(records: Iterable) -> MethylationProfile:
    """Collect the per-read distributions H1 reports alongside the funnel."""
    profile = MethylationProfile()
    seen_reads = set()
    for record in records:
        read_id = _get(record, "read_id")
        if read_id in seen_reads:
            continue  # one read may appear at several candidates; count the molecule once
        seen_reads.add(read_id)
        profile.reads_total += 1

        cpgs = _as_int_list(_get(record, "cpg_positions"))
        distances = _as_int_list(_get(record, "distance_of_cpgs_to_read_ends"))
        if not cpgs:
            profile.reads_with_missing_methylation += 1
        profile.cpgs_per_read.append(len(cpgs))
        profile.read_end_distances.extend(distances)

        length = _get(record, "read_length")
        if length not in (None, ""):
            profile.read_lengths.append(int(length))
    return profile


def _as_int_list(value) -> List[int]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [int(v) for v in value.split(";") if v]
    return [int(v) for v in value]


def _describe(values: Sequence[int]) -> Dict[str, Optional[float]]:
    """Median and quartiles without numpy, so the funnel has no hard numeric dependency."""
    if not values:
        return {"n": 0, "min": None, "q25": None, "median": None, "q75": None, "max": None}
    ordered = sorted(values)
    return {
        "n": len(ordered),
        "min": ordered[0],
        "q25": _quantile(ordered, 0.25),
        "median": _quantile(ordered, 0.50),
        "q75": _quantile(ordered, 0.75),
        "max": ordered[-1],
    }


def _quantile(ordered: Sequence[int], q: float) -> float:
    """Linear-interpolation quantile on a pre-sorted sequence."""
    if len(ordered) == 1:
        return float(ordered[0])
    position = q * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def format_funnel_tsv(strata: Dict[tuple, FunnelCounts], by: Sequence[str]) -> str:
    """Render a stratified funnel as TSV — the repository's standard table format.

    Every rate is emitted beside its denominator, never alone.
    """
    header = list(by) + STAGES + [f"survival_{s}" for s in STAGES[1:]]
    lines = ["\t".join(header)]
    for key, counts in strata.items():
        cells = [str(part) for part in key]
        cells += [str(counts.stage_counts[s]) for s in STAGES]
        cells += [f"{counts.survival(s):.4f}" for s in STAGES[1:]]
        lines.append("\t".join(cells))
    return "\n".join(lines) + "\n"
