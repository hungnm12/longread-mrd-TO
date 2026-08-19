"""Leakage-safe train/test splitting.

Reads from the same genomic region share alignment context, local error modes, phasing
state, and — in a mixture BAM — potentially the same underlying molecule. A random
read-level split therefore places correlated observations on both sides and inflates every
metric. This module makes the correct split the only one available: there is no
``random_split`` function to reach for.

Supported levels (``research/experiments/evaluation-plan.md`` §3):

* ``chromosome`` — strongest; use for the headline H3 comparison
* ``region``     — finer, still leakage-safe with respect to local context
* ``sample``     — for generalization across dilution levels

Groups, not rows, are assigned. Assignment is seeded and recorded, so a split is
reproducible and auditable after the fact.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set

CHROMOSOME = "chromosome"
REGION = "region"
SAMPLE = "sample"

_GROUP_FIELD = {
    CHROMOSOME: "chrom",
    REGION: "region_id",
    SAMPLE: "sample_id",
}


@dataclass
class Split:
    """A train/test partition expressed as group memberships, not row indices."""

    level: str
    train_groups: Set[str] = field(default_factory=set)
    test_groups: Set[str] = field(default_factory=set)
    seed: Optional[int] = None

    def assign(self, row: Dict[str, str]) -> Optional[str]:
        """Return ``'train'``, ``'test'``, or None when the row's group is in neither."""
        group = group_of(row, self.level)
        if group in self.train_groups:
            return "train"
        if group in self.test_groups:
            return "test"
        return None

    def rows(self, rows: Sequence[Dict[str, str]], side: str) -> List[Dict[str, str]]:
        return [row for row in rows if self.assign(row) == side]

    def as_dict(self) -> Dict[str, object]:
        """Serializable form, for the experiment manifest."""
        return {
            "level": self.level,
            "seed": self.seed,
            "train_groups": sorted(self.train_groups),
            "test_groups": sorted(self.test_groups),
        }


def group_of(row: Dict[str, str], level: str) -> str:
    """The group a row belongs to at ``level``."""
    if level not in _GROUP_FIELD:
        raise ValueError(
            f"unknown split level {level!r}; use one of {sorted(_GROUP_FIELD)} — "
            "row-level splitting is not supported because it leaks"
        )
    return str(row.get(_GROUP_FIELD[level], ""))


def groups(rows: Iterable[Dict[str, str]], level: str) -> List[str]:
    """Sorted distinct groups present in ``rows``."""
    return sorted({group_of(row, level) for row in rows})


def make_split(
    rows: Sequence[Dict[str, str]],
    level: str,
    test_fraction: float = 0.3,
    seed: Optional[int] = None,
    held_out: Optional[Sequence[str]] = None,
) -> Split:
    """Assign whole groups to train or test.

    ``held_out`` pins specific groups to the test side — the preferred mode for the headline
    comparison, because a pre-declared held-out chromosome set is auditable in a way a
    seeded draw is not (``research/decisions/decision-log.md`` records which chromosomes).

    Raises rather than returning a degenerate split when either side would be empty: an
    empty test set silently turns an evaluation into a training-set report.
    """
    available = groups(rows, level)
    if not available:
        raise ValueError("no rows to split")

    if held_out is not None:
        test_groups = {str(g) for g in held_out}
        unknown = test_groups - set(available)
        if unknown:
            raise ValueError(f"held-out groups absent from the data: {sorted(unknown)}")
        train_groups = set(available) - test_groups
    else:
        if not 0.0 < test_fraction < 1.0:
            raise ValueError(f"test_fraction must lie in (0, 1), got {test_fraction}")
        shuffled = list(available)
        random.Random(seed).shuffle(shuffled)
        n_test = max(1, int(round(len(shuffled) * test_fraction)))
        test_groups = set(shuffled[:n_test])
        train_groups = set(shuffled[n_test:])

    if not train_groups or not test_groups:
        raise ValueError(
            f"split at level {level!r} leaves one side empty "
            f"({len(train_groups)} train / {len(test_groups)} test groups from "
            f"{len(available)} available) — an empty test set is a training-set report"
        )

    split = Split(level=level, train_groups=train_groups, test_groups=test_groups, seed=seed)
    assert_disjoint(split)
    return split


def assert_disjoint(split: Split) -> None:
    """Fail loudly if any group appears on both sides."""
    overlap = split.train_groups & split.test_groups
    if overlap:
        raise ValueError(
            f"leakage: {len(overlap)} group(s) in both train and test at level "
            f"{split.level!r}: {sorted(overlap)[:5]}"
        )


def assert_no_region_crosses_split(rows: Sequence[Dict[str, str]], split: Split) -> None:
    """Verify no *region* spans the split, whatever level the split was made at.

    A chromosome-level split satisfies this automatically. A sample-level split does not —
    the same region appears in every sample — so this check states the property that
    actually matters rather than trusting the level name.
    """
    sides: Dict[str, Set[str]] = {}
    for row in rows:
        side = split.assign(row)
        if side is None:
            continue
        sides.setdefault(str(row.get("region_id", "")), set()).add(side)
    crossing = sorted(region for region, seen in sides.items() if len(seen) > 1)
    if crossing:
        raise ValueError(
            f"leakage: {len(crossing)} region(s) appear in both train and test: "
            f"{crossing[:5]} — reads from one region are correlated and must not be split"
        )


def selection_provenance(
    selected_from: Sequence[str],
    evaluation_samples: Sequence[str],
) -> Dict[str, object]:
    """Record where methylation regions were selected, and check it excludes eval samples.

    Selecting regions using the evaluation dilutions is leakage that no train/test split
    catches, because it happens before the split exists
    (``research/experiments/evaluation-plan.md`` §3 rule 3).
    """
    overlap = sorted(set(selected_from) & set(evaluation_samples))
    if overlap:
        raise ValueError(
            "region selection used evaluation sample(s): "
            + ", ".join(overlap)
            + " — select on the pure tumor/normal or a held-out chromosome set instead"
        )
    return {
        "selected_from": sorted(set(selected_from)),
        "evaluation_samples": sorted(set(evaluation_samples)),
        "disjoint": True,
    }
