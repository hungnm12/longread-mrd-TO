"""Read haplotype context off an alignment record.

LongPhase and WhatsHap both write:

* ``HP:i:1`` / ``HP:i:2`` — which haplotype the read was assigned to
* ``PS:i:<int>``          — the phase set (phase block) the assignment is relative to

``HP`` is only meaningful **within** its ``PS``. Haplotype 1 in phase set 12345 has no
relationship to haplotype 1 in phase set 67890 — phase blocks are independently oriented.
Any stratification that groups on ``HP`` alone silently pools unrelated haplotypes, so
:attr:`HaplotypeContext.family` is provided as the correct grouping key and used by the
funnel and by Phase 5's strata.

Neither tool emits a per-read confidence. ``confidence`` is therefore always ``None``. It
is kept as a named field rather than omitted so that its absence is visible in the schema
instead of being quietly forgotten — see ``docs/joint_molecule_schema.md``.

As of the Phase 0 audit no BAM in this project carries HP or PS; haplotagging is work the
project must still run (``docs/repo_audit.md`` §14.3). This module is written so the
funnel can count ``no_haplotype_tag`` correctly in the meantime.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class HaplotypeContext:
    """Haplotype assignment for one read."""

    haplotype: Optional[int]
    phase_set: Optional[int]
    confidence: Optional[float] = None

    @property
    def is_haplotagged(self) -> bool:
        return self.haplotype is not None

    @property
    def family(self) -> Optional[str]:
        """The only sound grouping key: ``<phase_set>:<haplotype>``.

        Returns None when either component is missing, so unphased reads cannot be
        accidentally pooled into a stratum.
        """
        if self.haplotype is None or self.phase_set is None:
            return None
        return f"{self.phase_set}:{self.haplotype}"


def read_haplotype(read) -> HaplotypeContext:
    """Extract HP/PS from a ``pysam.AlignedSegment``.

    A read carrying HP but no PS is treated as **not** haplotagged: without a phase set the
    tag cannot be interpreted, and admitting it would corrupt every stratum it entered.
    """
    haplotype = _int_tag(read, "HP")
    phase_set = _int_tag(read, "PS")
    if haplotype is not None and phase_set is None:
        return HaplotypeContext(haplotype=None, phase_set=None)
    return HaplotypeContext(haplotype=haplotype, phase_set=phase_set)


def _int_tag(read, tag: str) -> Optional[int]:
    try:
        value = read.get_tag(tag)
    except KeyError:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def phase_block_stats(contexts: Iterable[HaplotypeContext]) -> Dict[str, object]:
    """Summarize haplotagging for a region — feeds ``haplotag_rate`` in the H1 funnel."""
    contexts = list(contexts)
    total = len(contexts)
    tagged = [c for c in contexts if c.is_haplotagged]
    per_phase_set = Counter(c.phase_set for c in tagged)
    per_haplotype = Counter(c.haplotype for c in tagged)
    return {
        "reads_total": total,
        "reads_haplotagged": len(tagged),
        "haplotag_rate": (len(tagged) / total) if total else float("nan"),
        "n_phase_sets": len(per_phase_set),
        "n_haplotype_families": len({c.family for c in tagged}),
        "reads_per_haplotype": dict(sorted(per_haplotype.items(), key=lambda kv: (kv[0] is None, kv[0]))),
        "largest_phase_set_reads": max(per_phase_set.values()) if per_phase_set else 0,
    }
