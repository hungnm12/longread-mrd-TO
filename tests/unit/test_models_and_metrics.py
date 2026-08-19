"""Interpretable models, metrics, and the end-to-end label-shuffle leakage check."""
from __future__ import annotations

import os
import random
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from src.evaluation.metrics import (  # noqa: E402
    average_precision,
    bootstrap_by_group,
    brier_score,
    calibration_curve,
    evaluate,
    false_positives_per_informative,
    roc_auc,
    sensitivity_at_specificity,
)
from src.models.baselines import LikelihoodRatioClassifier, LogisticRegression  # noqa: E402
from src.models.features import ABLATION_GRID, build_feature_matrix, permute_methylation  # noqa: E402


class RocAucTest(unittest.TestCase):
    def test_perfect_separation(self):
        self.assertAlmostEqual(roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)

    def test_inverted_separation(self):
        self.assertAlmostEqual(roc_auc([1, 1, 0, 0], [0.1, 0.2, 0.8, 0.9]), 0.0)

    def test_all_ties_give_one_half(self):
        self.assertAlmostEqual(roc_auc([0, 1, 0, 1], [0.5] * 4), 0.5)

    def test_single_class_returns_none_not_a_number(self):
        """A missing metric must not masquerade as a measured 0.5."""
        self.assertIsNone(roc_auc([1, 1, 1], [0.1, 0.5, 0.9]))


class SensitivityAtSpecificityTest(unittest.TestCase):
    def test_perfect_scores_reach_full_sensitivity(self):
        sensitivity, _ = sensitivity_at_specificity([0] * 10 + [1] * 10,
                                                    [0.1] * 10 + [0.9] * 10, 0.95)
        self.assertAlmostEqual(sensitivity, 1.0)

    def test_returns_the_operating_point(self):
        _, threshold = sensitivity_at_specificity([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], 0.9)
        self.assertIsNotNone(threshold)

    def test_overlapping_distributions_lose_sensitivity(self):
        # Negatives spread over 0.00-0.99, positives over 0.50-0.995: the distributions
        # interleave heavily, so demanding 95% specificity costs most of the sensitivity
        # without eliminating it.
        negatives = [i / 100 for i in range(100)]
        positives = [0.5 + i / 200 for i in range(100)]
        labels = [0] * 100 + [1] * 100
        sensitivity, _ = sensitivity_at_specificity(labels, negatives + positives, 0.95)
        self.assertLess(sensitivity, 1.0)
        self.assertGreater(sensitivity, 0.0)

    def test_rejects_out_of_range_specificity(self):
        with self.assertRaises(ValueError):
            evaluate([0, 1], [0.1, 0.9], fixed_specificity=1.0)


class MetricBlockTest(unittest.TestCase):
    def test_every_rate_ships_with_its_denominator(self):
        block = evaluate([0] * 8 + [1] * 2, [0.1] * 8 + [0.9] * 2, 0.9).as_dict()
        self.assertEqual(block["denominators"]["n_molecules"], 10)
        self.assertEqual(block["denominators"]["n_positive"], 2)
        self.assertEqual(block["denominators"]["n_negative"], 8)

    def test_auc_is_never_returned_alone(self):
        block = evaluate([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], 0.9).as_dict()
        self.assertIn("primary", block)
        self.assertIn("calibration", block)
        self.assertIn("never the sole basis", block["note"])

    def test_single_class_yields_none_metrics_but_real_counts(self):
        block = evaluate([1, 1, 1], [0.2, 0.5, 0.9], 0.9)
        self.assertEqual(block.n_molecules, 3)
        self.assertIsNone(block.roc_auc)
        self.assertIsNone(block.sensitivity_at_fixed_specificity)

    def test_length_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([0, 1], [0.5], 0.9)


class OtherMetricsTest(unittest.TestCase):
    def test_average_precision_perfect(self):
        self.assertAlmostEqual(average_precision([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 1.0)

    def test_brier_rewards_confident_correct_predictions(self):
        good = brier_score([0, 1], [0.05, 0.95])
        bad = brier_score([0, 1], [0.95, 0.05])
        self.assertLess(good, bad)

    def test_fp_rate_denominator_is_all_molecules(self):
        # 10 molecules, 2 negatives scoring above threshold → 2/10, not 2/8
        labels = [0] * 8 + [1] * 2
        scores = [0.9, 0.9] + [0.1] * 6 + [0.9, 0.9]
        self.assertAlmostEqual(false_positives_per_informative(labels, scores, 0.5), 0.2)

    def test_calibration_omits_empty_bins(self):
        bins = calibration_curve([0, 1], [0.05, 0.95], n_bins=10)
        self.assertEqual(len(bins), 2)
        self.assertTrue(all(b["n"] > 0 for b in bins))

    def test_bootstrap_resamples_groups_not_rows(self):
        labels = [0, 1] * 20
        scores = [0.2, 0.8] * 20
        group_ids = [f"g{i // 4}" for i in range(40)]
        result = bootstrap_by_group(labels, scores, group_ids, roc_auc, n_resamples=50, seed=1)
        self.assertEqual(result["n_groups"], 10)
        self.assertIsNotNone(result["low"])
        self.assertLessEqual(result["low"], result["point"])


class LogisticRegressionTest(unittest.TestCase):
    def _separable(self, n=200):
        rng = random.Random(0)
        matrix, labels = [], []
        for _ in range(n):
            positive = rng.random() < 0.5
            matrix.append([rng.gauss(2.0 if positive else -2.0, 0.5), rng.gauss(0, 1)])
            labels.append(1 if positive else 0)
        return matrix, labels

    def test_learns_a_separable_signal(self):
        matrix, labels = self._separable()
        model = LogisticRegression().fit(matrix, labels, ["signal", "noise"])
        self.assertGreater(roc_auc(labels, model.predict_proba(matrix)), 0.95)

    def test_coefficients_are_inspectable_per_feature(self):
        matrix, labels = self._separable()
        described = LogisticRegression().fit(matrix, labels, ["signal", "noise"]).describe()
        self.assertTrue(described["fitted"])
        self.assertGreater(abs(described["coefficients"]["signal"]),
                           abs(described["coefficients"]["noise"]))

    def test_single_class_is_refused_with_an_explanation(self):
        with self.assertRaises(ValueError) as ctx:
            LogisticRegression().fit([[1.0], [2.0]], [1, 1])
        self.assertIn("single class", str(ctx.exception))

    def test_predicting_before_fitting_raises(self):
        with self.assertRaises(RuntimeError):
            LogisticRegression().predict_proba([[1.0]])

    def test_constant_feature_does_not_produce_nan(self):
        matrix = [[1.0, v] for v in range(20)]
        labels = [0] * 10 + [1] * 10
        scores = LogisticRegression().fit(matrix, labels).predict_proba(matrix)
        self.assertTrue(all(s == s for s in scores))  # NaN != NaN


class LikelihoodRatioTest(unittest.TestCase):
    def test_learns_a_separable_signal(self):
        rng = random.Random(1)
        matrix = [[rng.gauss(3.0, 0.5)] for _ in range(100)] + [[rng.gauss(-3.0, 0.5)] for _ in range(100)]
        labels = [1] * 100 + [0] * 100
        model = LikelihoodRatioClassifier().fit(matrix, labels, ["signal"])
        self.assertGreater(roc_auc(labels, model.predict_proba(matrix)), 0.95)

    def test_describes_its_independence_assumption(self):
        matrix = [[float(i)] for i in range(40)]
        labels = [0] * 20 + [1] * 20
        described = LikelihoodRatioClassifier().fit(matrix, labels, ["x"]).describe()
        self.assertIn("independent", described["assumption"])


class LabelShuffleLeakageTest(unittest.TestCase):
    """Rule 5: the whole pipeline on permuted labels must land at chance.

    If it does not, information is reaching the model through a path other than the
    features — the single most valuable end-to-end leakage check available.
    """

    def _rows(self, n=240):
        rng = random.Random(3)
        rows = []
        for i in range(n):
            tumor = i % 2 == 0
            rows.append({
                "sample_id": "S1",
                "dilution": "1e-2",
                "source_label_for_evaluation_only": "tumor" if tumor else "normal",
                "chrom": f"chr{(i % 6) + 1}",
                "region_id": f"chr{(i % 6) + 1}_0_1000",
                "candidate_id": "chr1:500:C>T",
                "read_id": f"r{i}",
                "observed_allele": "T" if tumor else "C",
                "allele_quality": str(rng.randint(20, 40)),
                "mapping_quality": "60",
                "read_length": "10000",
                "phase_set": "777",
                "haplotype_tag": "1" if tumor else "2",
                "cpg_positions": "10;20;30",
                "methylation_probabilities": "0.9;0.9;0.9" if tumor else "0.1;0.1;0.1",
                "methylation_probabilities_5hmc": "0.01;0.01;0.01",
                "methylated_cpg_count": "3" if tumor else "0",
                "unmethylated_cpg_count": "0" if tumor else "3",
                "distance_of_cpgs_to_read_ends": "100;200;300",
                "usable": "1",
                "exclusion_reason": "",
            })
        return rows

    def test_real_labels_are_learnable(self):
        """Control for the control: the fixture must contain signal to begin with."""
        rows = self._rows()
        matrix, names = build_feature_matrix(rows, ABLATION_GRID["F"])
        labels = [1 if r["source_label_for_evaluation_only"] == "tumor" else 0 for r in rows]
        model = LogisticRegression().fit(matrix, labels, names)
        self.assertGreater(roc_auc(labels, model.predict_proba(matrix)), 0.9)

    def test_shuffled_labels_give_chance_performance(self):
        rows = self._rows()
        matrix, names = build_feature_matrix(rows, ABLATION_GRID["F"])
        labels = [1 if r["source_label_for_evaluation_only"] == "tumor" else 0 for r in rows]

        rng = random.Random(11)
        shuffled = list(labels)
        rng.shuffle(shuffled)

        model = LogisticRegression().fit(matrix, shuffled, names)
        auc = roc_auc(shuffled, model.predict_proba(matrix))
        self.assertLess(abs(auc - 0.5), 0.15, f"shuffled-label AUC {auc:.3f} is not chance")


class PermutedMethylationControlTest(unittest.TestCase):
    """The capacity control for H3: model F must beat permuted methylation, not just D."""

    def _rows(self, n=40):
        return [
            {
                "sample_id": "S1", "dilution": "1e-2",
                "source_label_for_evaluation_only": "tumor" if i % 2 else "normal",
                "chrom": "chr1", "region_id": "chr1_0_1000",
                "candidate_id": "chr1:500:C>T", "read_id": f"r{i}",
                "observed_allele": "T", "allele_quality": "30", "mapping_quality": "60",
                "read_length": "10000", "phase_set": "777", "haplotype_tag": "1",
                "cpg_positions": f"{i}",
                "methylation_probabilities": f"0.{i % 10}",
                "methylation_probabilities_5hmc": "0.01",
                "methylated_cpg_count": str(i % 3), "unmethylated_cpg_count": "0",
                "distance_of_cpgs_to_read_ends": "100",
                "usable": "1", "exclusion_reason": "",
            }
            for i in range(n)
        ]

    def test_permutation_moves_methylation_columns_only(self):
        rows = self._rows()
        permuted = permute_methylation(rows, random.Random(5))
        self.assertEqual([r["read_id"] for r in permuted], [r["read_id"] for r in rows])
        self.assertEqual([r["observed_allele"] for r in permuted], [r["observed_allele"] for r in rows])
        self.assertNotEqual(
            [r["methylation_probabilities"] for r in permuted],
            [r["methylation_probabilities"] for r in rows],
        )

    def test_permutation_preserves_the_multiset_of_methylation_values(self):
        rows = self._rows()
        permuted = permute_methylation(rows, random.Random(5))
        self.assertEqual(
            sorted(r["methylation_probabilities"] for r in permuted),
            sorted(r["methylation_probabilities"] for r in rows),
        )

    def test_permutation_does_not_change_the_feature_count(self):
        rows = self._rows()
        original, names_a = build_feature_matrix(rows, ABLATION_GRID["F"])
        permuted, names_b = build_feature_matrix(permute_methylation(rows, random.Random(5)),
                                                 ABLATION_GRID["F"])
        self.assertEqual(names_a, names_b)
        self.assertEqual(len(original[0]), len(permuted[0]))


if __name__ == "__main__":
    unittest.main()
