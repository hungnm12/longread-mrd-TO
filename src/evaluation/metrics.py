"""Metrics, in the priority order fixed by ``research/experiments/evaluation-plan.md`` §2.

1. sensitivity at fixed specificity  ← primary
2. precision-recall
3. false-positive molecules per informative molecule
4. calibration
5. informative molecule count
6. ROC-AUC — reportable, never decisive

Two conventions are enforced rather than left to discipline:

* **No rate without its denominator.** Every returned rate ships beside the count it was
  computed from, so a metric on 12 molecules cannot be reported as though it were solid.
* **AUC is not returned alone.** :func:`evaluate` always returns the full block, so a
  caller cannot accidentally reduce a comparison to AUC.

numpy is used where available but is not required — the environment lacks scikit-learn
(``docs/repo_audit.md`` §11), so everything here is plain Python.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass
class MetricBlock:
    """Every metric for one model on one split, with denominators attached."""

    n_molecules: int
    n_positive: int
    n_negative: int
    sensitivity_at_fixed_specificity: Optional[float] = None
    fixed_specificity: Optional[float] = None
    threshold_at_fixed_specificity: Optional[float] = None
    average_precision: Optional[float] = None
    fp_per_informative_molecule: Optional[float] = None
    brier_score: Optional[float] = None
    calibration_bins: List[Dict[str, float]] = field(default_factory=list)
    roc_auc: Optional[float] = None

    def as_dict(self) -> Dict[str, object]:
        return {
            "denominators": {
                "n_molecules": self.n_molecules,
                "n_positive": self.n_positive,
                "n_negative": self.n_negative,
            },
            "primary": {
                "sensitivity_at_fixed_specificity": self.sensitivity_at_fixed_specificity,
                "fixed_specificity": self.fixed_specificity,
                "threshold": self.threshold_at_fixed_specificity,
            },
            "average_precision": self.average_precision,
            "fp_per_informative_molecule": self.fp_per_informative_molecule,
            "calibration": {"brier_score": self.brier_score, "bins": self.calibration_bins},
            "roc_auc": self.roc_auc,
            "note": (
                "ROC-AUC is reported but is never the sole basis of a decision "
                "(research/experiments/evaluation-plan.md §2.7)."
            ),
        }


def evaluate(
    labels: Sequence[int],
    scores: Sequence[float],
    fixed_specificity: float,
    n_calibration_bins: int = 10,
) -> MetricBlock:
    """Compute the full metric block. ``fixed_specificity`` must be chosen before the run."""
    if len(labels) != len(scores):
        raise ValueError(f"labels ({len(labels)}) and scores ({len(scores)}) differ in length")
    if not 0.0 < fixed_specificity < 1.0:
        raise ValueError(f"fixed_specificity must lie in (0, 1), got {fixed_specificity}")

    n_positive = sum(1 for y in labels if y == 1)
    n_negative = len(labels) - n_positive

    block = MetricBlock(
        n_molecules=len(labels),
        n_positive=n_positive,
        n_negative=n_negative,
        fixed_specificity=fixed_specificity,
    )
    if not labels or n_positive == 0 or n_negative == 0:
        # One-class data yields no meaningful discrimination metric. Returning None is
        # honest; returning 0.5 or 0.0 would look like a measurement.
        return block

    sensitivity, threshold = sensitivity_at_specificity(labels, scores, fixed_specificity)
    block.sensitivity_at_fixed_specificity = sensitivity
    block.threshold_at_fixed_specificity = threshold
    block.average_precision = average_precision(labels, scores)
    block.fp_per_informative_molecule = false_positives_per_informative(labels, scores, threshold)
    block.brier_score = brier_score(labels, scores)
    block.calibration_bins = calibration_curve(labels, scores, n_calibration_bins)
    block.roc_auc = roc_auc(labels, scores)
    return block


def sensitivity_at_specificity(
    labels: Sequence[int], scores: Sequence[float], target_specificity: float
) -> Tuple[Optional[float], Optional[float]]:
    """Sensitivity at the lowest threshold meeting ``target_specificity``.

    Returns ``(sensitivity, threshold)``. The threshold is returned so the operating point
    is recorded rather than re-derived later on different data.
    """
    negatives = sorted((s for y, s in zip(labels, scores) if y == 0), reverse=True)
    positives = [s for y, s in zip(labels, scores) if y == 1]
    if not negatives or not positives:
        return None, None

    # Allow this many negatives above the threshold while still meeting the target.
    allowed_fp = int((1.0 - target_specificity) * len(negatives))
    threshold = negatives[0] + 1e-12 if allowed_fp == 0 else negatives[min(allowed_fp, len(negatives)) - 1]

    true_positives = sum(1 for s in positives if s >= threshold)
    return true_positives / len(positives), threshold


def average_precision(labels: Sequence[int], scores: Sequence[float]) -> Optional[float]:
    """Area under the precision-recall curve, by the step-wise (interpolation-free) rule."""
    n_positive = sum(labels)
    if n_positive == 0:
        return None
    ordered = sorted(zip(scores, labels), key=lambda pair: -pair[0])
    true_positives = 0
    total = 0.0
    for rank, (_, label) in enumerate(ordered, start=1):
        if label == 1:
            true_positives += 1
            total += true_positives / rank
    return total / n_positive


def false_positives_per_informative(
    labels: Sequence[int], scores: Sequence[float], threshold: Optional[float]
) -> Optional[float]:
    """False-positive molecules divided by all informative molecules.

    The denominator is *every* molecule scored, not just the negatives — this is the rate
    that propagates into a sample-level score, which is why it is reported separately from
    the false-positive rate.
    """
    if threshold is None or not labels:
        return None
    false_positives = sum(1 for y, s in zip(labels, scores) if y == 0 and s >= threshold)
    return false_positives / len(labels)


def brier_score(labels: Sequence[int], scores: Sequence[float]) -> Optional[float]:
    """Mean squared error of the predicted probabilities. Lower is better."""
    if not labels:
        return None
    return sum((s - y) ** 2 for y, s in zip(labels, scores)) / len(labels)


def calibration_curve(
    labels: Sequence[int], scores: Sequence[float], n_bins: int = 10
) -> List[Dict[str, float]]:
    """Reliability diagram data. Empty bins are omitted rather than reported as zero."""
    bins: List[Dict[str, float]] = []
    for index in range(n_bins):
        low = index / n_bins
        high = (index + 1) / n_bins
        members = [
            (y, s)
            for y, s in zip(labels, scores)
            if (low <= s < high) or (index == n_bins - 1 and s == 1.0)
        ]
        if not members:
            continue
        bins.append(
            {
                "bin_low": low,
                "bin_high": high,
                "n": len(members),
                "mean_predicted": sum(s for _, s in members) / len(members),
                "observed_fraction": sum(y for y, _ in members) / len(members),
            }
        )
    return bins


def roc_auc(labels: Sequence[int], scores: Sequence[float]) -> Optional[float]:
    """AUC by the rank-sum identity, with ties averaged.

    Reportable, never decisive: it is insensitive to calibration and to the operating point
    that matters, and unstable under the severe class imbalance at 0.01% tumor fraction.
    """
    n_positive = sum(labels)
    n_negative = len(labels) - n_positive
    if n_positive == 0 or n_negative == 0:
        return None

    ordered = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores)
    position = 0
    while position < len(ordered):
        end = position
        while end + 1 < len(ordered) and scores[ordered[end + 1]] == scores[ordered[position]]:
            end += 1
        average_rank = (position + end) / 2.0 + 1.0
        for index in range(position, end + 1):
            ranks[ordered[index]] = average_rank
        position = end + 1

    positive_rank_sum = sum(rank for rank, label in zip(ranks, labels) if label == 1)
    return (positive_rank_sum - n_positive * (n_positive + 1) / 2.0) / (n_positive * n_negative)


def bootstrap_by_group(
    labels: Sequence[int],
    scores: Sequence[float],
    group_ids: Sequence[str],
    statistic,
    n_resamples: int = 200,
    seed: int = 0,
    confidence: float = 0.95,
) -> Dict[str, Optional[float]]:
    """Bootstrap a statistic by resampling **groups**, not individual molecules.

    Resampling molecules would treat correlated same-region reads as independent and
    produce intervals that are too narrow — the same error a random split makes
    (``research/experiments/evaluation-plan.md`` §5).
    """
    import random as _random

    by_group: Dict[str, List[int]] = {}
    for index, group in enumerate(group_ids):
        by_group.setdefault(str(group), []).append(index)
    group_names = sorted(by_group)
    if len(group_names) < 2:
        return {"point": statistic(labels, scores), "low": None, "high": None, "n_groups": len(group_names)}

    rng = _random.Random(seed)
    estimates: List[float] = []
    for _ in range(n_resamples):
        indices: List[int] = []
        for _ in group_names:
            indices.extend(by_group[group_names[rng.randrange(len(group_names))]])
        value = statistic([labels[i] for i in indices], [scores[i] for i in indices])
        if value is not None:
            estimates.append(value)

    if not estimates:
        return {"point": statistic(labels, scores), "low": None, "high": None, "n_groups": len(group_names)}

    estimates.sort()
    tail = (1.0 - confidence) / 2.0
    return {
        "point": statistic(labels, scores),
        "low": estimates[int(tail * (len(estimates) - 1))],
        "high": estimates[int((1.0 - tail) * (len(estimates) - 1))],
        "n_groups": len(group_names),
        "n_resamples": len(estimates),
    }
