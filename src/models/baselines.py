"""Interpretable per-molecule classifiers.

Deliberately simple, in the order ``research/hypotheses/hypotheses.md`` prescribes: likelihood
ratio, logistic regression, calibrated linear model. **No deep learning** until interpretable
evidence justifies it.

scikit-learn is absent from this environment (``docs/repo_audit.md`` §11), so logistic
regression is implemented here on numpy. That is not a workaround — for H3 the model must be
inspectable coefficient by coefficient, because the question is *which modality contributes*,
not *how high can the score go*.

Every model exposes the same three-method interface (``fit`` / ``predict_proba`` /
``describe``) so the ablation driver can swap them without special-casing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np


@dataclass
class LogisticRegression:
    """L2-regularized logistic regression fitted by gradient descent on standardized features.

    Standardization is fitted on the **training** data only and reapplied at predict time;
    fitting it on the full dataset would leak test-set distribution into training.
    """

    learning_rate: float = 0.1
    n_iterations: int = 2000
    l2: float = 1.0
    fit_intercept: bool = True

    coefficients: Optional[np.ndarray] = None
    intercept: float = 0.0
    feature_names: List[str] = field(default_factory=list)
    _mean: Optional[np.ndarray] = None
    _scale: Optional[np.ndarray] = None

    def fit(self, matrix: Sequence[Sequence[float]], labels: Sequence[int],
            feature_names: Optional[Sequence[str]] = None) -> "LogisticRegression":
        X = np.asarray(matrix, dtype=float)
        y = np.asarray(labels, dtype=float)
        if X.ndim != 2:
            raise ValueError(f"feature matrix must be 2-D, got shape {X.shape}")
        if len(np.unique(y)) < 2:
            raise ValueError(
                "cannot fit on a single class — at these tumor fractions an empty positive "
                "class is expected and must be handled by the caller, not silently fitted"
            )

        self.feature_names = list(feature_names or [f"f{i}" for i in range(X.shape[1])])
        self._mean = X.mean(axis=0)
        scale = X.std(axis=0)
        scale[scale == 0] = 1.0  # a constant feature carries no information; leave it at 0
        self._scale = scale
        Xs = (X - self._mean) / self._scale

        weights = np.zeros(Xs.shape[1])
        intercept = 0.0
        n = len(y)
        for _ in range(self.n_iterations):
            predictions = _sigmoid(Xs @ weights + intercept)
            error = predictions - y
            gradient = (Xs.T @ error) / n + (self.l2 / n) * weights
            weights -= self.learning_rate * gradient
            if self.fit_intercept:
                intercept -= self.learning_rate * error.mean()

        self.coefficients = weights
        self.intercept = float(intercept)
        return self

    def predict_proba(self, matrix: Sequence[Sequence[float]]) -> List[float]:
        if self.coefficients is None:
            raise RuntimeError("model is not fitted")
        X = (np.asarray(matrix, dtype=float) - self._mean) / self._scale
        return _sigmoid(X @ self.coefficients + self.intercept).tolist()

    def describe(self) -> Dict[str, object]:
        """Per-feature coefficients — the point of using this model class.

        Coefficients are on the standardized scale, so magnitudes are comparable across
        features and a modality's contribution can be read directly.
        """
        if self.coefficients is None:
            return {"fitted": False}
        return {
            "fitted": True,
            "model": "logistic_regression",
            "intercept": self.intercept,
            "coefficients": {
                name: float(value)
                for name, value in zip(self.feature_names, self.coefficients)
            },
            "note": "coefficients are on the standardized feature scale",
        }


@dataclass
class LikelihoodRatioClassifier:
    """Naive-Bayes-style likelihood ratio over binned features.

    The simplest model that can express "this molecule looks more tumor-like than
    background", and the most transparent: every contribution is a log-ratio of two
    observed bin frequencies. Independence across features is assumed and is **wrong** —
    PAPER-005 says methylation and other signals are coupled — which is exactly why this is
    a baseline and the logistic model is the one H3 compares on.
    """

    n_bins: int = 10
    pseudocount: float = 1.0

    feature_names: List[str] = field(default_factory=list)
    _edges: List[np.ndarray] = field(default_factory=list)
    _log_ratios: List[np.ndarray] = field(default_factory=list)
    _prior_log_odds: float = 0.0

    def fit(self, matrix, labels, feature_names=None) -> "LikelihoodRatioClassifier":
        X = np.asarray(matrix, dtype=float)
        y = np.asarray(labels, dtype=int)
        if len(np.unique(y)) < 2:
            raise ValueError("cannot fit a likelihood ratio on a single class")

        self.feature_names = list(feature_names or [f"f{i}" for i in range(X.shape[1])])
        self._edges = []
        self._log_ratios = []

        n_positive = int((y == 1).sum())
        n_negative = int((y == 0).sum())
        self._prior_log_odds = math.log(n_positive / n_negative)

        for column in range(X.shape[1]):
            values = X[:, column]
            edges = np.unique(np.quantile(values, np.linspace(0, 1, self.n_bins + 1)))
            if len(edges) < 2:
                edges = np.array([values.min(), values.min() + 1.0])
            self._edges.append(edges)

            indices = np.clip(np.digitize(values, edges[1:-1], right=False), 0, len(edges) - 2)
            n_used = len(edges) - 1
            positive = np.bincount(indices[y == 1], minlength=n_used) + self.pseudocount
            negative = np.bincount(indices[y == 0], minlength=n_used) + self.pseudocount
            self._log_ratios.append(np.log(positive / positive.sum()) - np.log(negative / negative.sum()))
        return self

    def predict_proba(self, matrix) -> List[float]:
        if not self._log_ratios:
            raise RuntimeError("model is not fitted")
        X = np.asarray(matrix, dtype=float)
        log_odds = np.full(X.shape[0], self._prior_log_odds)
        for column in range(X.shape[1]):
            edges = self._edges[column]
            indices = np.clip(np.digitize(X[:, column], edges[1:-1], right=False), 0, len(edges) - 2)
            log_odds += self._log_ratios[column][indices]
        return _sigmoid(log_odds).tolist()

    def describe(self) -> Dict[str, object]:
        if not self._log_ratios:
            return {"fitted": False}
        return {
            "fitted": True,
            "model": "likelihood_ratio",
            "prior_log_odds": self._prior_log_odds,
            "max_abs_log_ratio": {
                name: float(np.abs(ratios).max())
                for name, ratios in zip(self.feature_names, self._log_ratios)
            },
            "assumption": "features independent given class — violated by design (PAPER-005)",
        }


def calibrate_isotonic_free(scores: Sequence[float], labels: Sequence[int],
                            n_bins: int = 10) -> Dict[str, object]:
    """Histogram (binning) calibration map, fitted on validation data only.

    Deliberately not isotonic regression: with very few positives at low tumor fraction,
    isotonic overfits into a step function that looks perfectly calibrated in-sample and
    generalizes badly.
    """
    if len(scores) != len(labels):
        raise ValueError("scores and labels differ in length")
    mapping = []
    for index in range(n_bins):
        low, high = index / n_bins, (index + 1) / n_bins
        members = [y for y, s in zip(labels, scores) if low <= s < high or (index == n_bins - 1 and s == 1.0)]
        if members:
            mapping.append({"low": low, "high": high, "n": len(members),
                            "calibrated": sum(members) / len(members)})
    return {"bins": mapping, "method": "histogram_binning"}


def _sigmoid(z):
    """Overflow-safe logistic function."""
    z = np.asarray(z, dtype=float)
    out = np.empty_like(z)
    positive = z >= 0
    out[positive] = 1.0 / (1.0 + np.exp(-z[positive]))
    exp_z = np.exp(z[~positive])
    out[~positive] = exp_z / (1.0 + exp_z)
    return out
