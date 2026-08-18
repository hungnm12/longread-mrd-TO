"""Per-molecule models and the A-F ablation grid.

Interpretable methods only, in the order ``docs/research/03_hypotheses.md`` prescribes.
``src.joint_evidence.labels`` must never be imported from here — evaluation labels reach a
model only through the evaluation code path.
"""
from .baselines import LikelihoodRatioClassifier, LogisticRegression, calibrate_isotonic_free
from .features import (
    ABLATION_GRID,
    KEY_COMPARISONS,
    MODALITIES,
    ModelSpec,
    assert_no_evaluation_fields,
    build_feature_matrix,
    extract_labels,
    feature_names,
    permute_methylation,
)

__all__ = [
    "ABLATION_GRID",
    "KEY_COMPARISONS",
    "MODALITIES",
    "ModelSpec",
    "build_feature_matrix",
    "feature_names",
    "extract_labels",
    "permute_methylation",
    "assert_no_evaluation_fields",
    "LogisticRegression",
    "LikelihoodRatioClassifier",
    "calibrate_isotonic_free",
]
