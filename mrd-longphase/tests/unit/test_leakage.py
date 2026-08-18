"""Leakage rules — the tests ``docs/research/04_evaluation_plan.md`` §3 requires.

Leakage does not announce itself; it shows up as a suspiciously good result. These tests
are the only mechanism that makes the rules binding rather than aspirational, so each one
maps to a numbered rule in the evaluation plan.
"""
from __future__ import annotations

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from src.evaluation.splits import (  # noqa: E402
    CHROMOSOME,
    REGION,
    SAMPLE,
    Split,
    assert_disjoint,
    assert_no_region_crosses_split,
    group_of,
    make_split,
    selection_provenance,
)
from src.joint_evidence.record import EVALUATION_ONLY_FIELDS  # noqa: E402
from src.models.features import (  # noqa: E402
    ABLATION_GRID,
    assert_no_evaluation_fields,
    build_feature_matrix,
    extract_labels,
    feature_names,
)


def row(chrom="chr1", region="chr1_0_1000", sample="S1", label="tumor", **extra):
    base = {
        "sample_id": sample,
        "dilution": "1e-2",
        "source_label_for_evaluation_only": label,
        "chrom": chrom,
        "region_id": region,
        "candidate_id": "chr1:500:C>T",
        "candidate_position": "500",
        "read_id": "r1",
        "observed_allele": "T",
        "allele_quality": "30",
        "mapping_quality": "60",
        "read_length": "10000",
        "phase_set": "777",
        "haplotype_tag": "1",
        "cpg_positions": "10;20;30",
        "methylation_probabilities": "0.9;0.8;0.95",
        "methylation_probabilities_5hmc": "0.01;0.02;0.01",
        "methylated_cpg_count": "3",
        "unmethylated_cpg_count": "0",
        "distance_of_cpgs_to_read_ends": "100;200;300",
        "usable": "1",
        "exclusion_reason": "",
    }
    base.update(extra)
    return base


class Rule1NoRegionCrossesSplitTest(unittest.TestCase):
    """Rule 1: reads from one genomic region must never be split across train and test."""

    def test_chromosome_split_keeps_regions_intact(self):
        rows = [row(chrom="chr1", region="chr1_0_1000"), row(chrom="chr2", region="chr2_0_1000")]
        split = make_split(rows, CHROMOSOME, held_out=["chr2"])
        assert_no_region_crosses_split(rows, split)  # must not raise

    def test_detects_a_region_spanning_both_sides(self):
        """A sample-level split does not protect regions — the same region is in every sample."""
        rows = [
            row(sample="S1", region="chr1_0_1000"),
            row(sample="S2", region="chr1_0_1000"),
        ]
        split = make_split(rows, SAMPLE, held_out=["S2"])
        with self.assertRaises(ValueError) as ctx:
            assert_no_region_crosses_split(rows, split)
        self.assertIn("chr1_0_1000", str(ctx.exception))

    def test_region_level_split_is_disjoint(self):
        rows = [row(region=f"chr1_{i}_1000") for i in range(10)]
        split = make_split(rows, REGION, test_fraction=0.3, seed=7)
        assert_disjoint(split)
        assert_no_region_crosses_split(rows, split)


class Rule2SplitLevelsTest(unittest.TestCase):
    """Rule 2: only chromosome, region and sample splitting exist. Row-level does not."""

    def test_row_level_splitting_is_not_available(self):
        with self.assertRaises(ValueError) as ctx:
            group_of(row(), "read")
        self.assertIn("leaks", str(ctx.exception))

    def test_empty_side_is_refused(self):
        """An empty test set silently turns an evaluation into a training-set report."""
        rows = [row(chrom="chr1")]
        with self.assertRaises(ValueError) as ctx:
            make_split(rows, CHROMOSOME, test_fraction=0.5)
        self.assertIn("empty", str(ctx.exception))

    def test_overlapping_groups_are_caught(self):
        split = Split(level=CHROMOSOME, train_groups={"chr1", "chr2"}, test_groups={"chr2"})
        with self.assertRaises(ValueError) as ctx:
            assert_disjoint(split)
        self.assertIn("chr2", str(ctx.exception))

    def test_held_out_groups_must_exist(self):
        with self.assertRaises(ValueError):
            make_split([row(chrom="chr1"), row(chrom="chr2")], CHROMOSOME, held_out=["chr22"])

    def test_split_is_recorded_for_audit(self):
        rows = [row(chrom=f"chr{i}") for i in range(1, 6)]
        recorded = make_split(rows, CHROMOSOME, held_out=["chr5"]).as_dict()
        self.assertEqual(recorded["test_groups"], ["chr5"])
        self.assertEqual(recorded["level"], CHROMOSOME)


class Rule3SelectionProvenanceTest(unittest.TestCase):
    """Rule 3: methylation regions must not be selected using the evaluation dilutions.

    This leak happens before any split exists, so no train/test check can catch it.
    """

    def test_selecting_on_an_evaluation_sample_is_refused(self):
        with self.assertRaises(ValueError) as ctx:
            selection_provenance(
                selected_from=["HCC1395_TF1e-3_25x_rep1"],
                evaluation_samples=["HCC1395_TF1e-3_25x_rep1", "HCC1395_TF1e-4_25x_rep1"],
            )
        self.assertIn("HCC1395_TF1e-3_25x_rep1", str(ctx.exception))

    def test_selecting_on_pure_sources_is_allowed_and_recorded(self):
        provenance = selection_provenance(
            selected_from=["HCC1395_pure", "HCC1395BL_pure"],
            evaluation_samples=["HCC1395_TF1e-3_25x_rep1"],
        )
        self.assertTrue(provenance["disjoint"])
        self.assertEqual(provenance["selected_from"], ["HCC1395BL_pure", "HCC1395_pure"])


class Rule4LabelFirewallTest(unittest.TestCase):
    """Rule 4: evaluation-only truth must be structurally separated from inference inputs."""

    def test_no_ablation_model_exposes_an_evaluation_field(self):
        for name, spec in ABLATION_GRID.items():
            names = feature_names(spec)
            for forbidden in EVALUATION_ONLY_FIELDS:
                for feature in names:
                    self.assertNotIn(forbidden, feature, f"model {name} leaks {forbidden}")

    def test_feature_matrix_never_contains_the_label(self):
        rows = [row(label="tumor"), row(label="normal")]
        for spec in ABLATION_GRID.values():
            matrix, names = build_feature_matrix(rows, spec)
            self.assertEqual(len(matrix), 2)
            assert_no_evaluation_fields(names)

    def test_identical_rows_differing_only_in_label_give_identical_features(self):
        """The strongest form of the firewall: the label is invisible to feature building."""
        tumor = build_feature_matrix([row(label="tumor")], ABLATION_GRID["F"])[0]
        normal = build_feature_matrix([row(label="normal")], ABLATION_GRID["F"])[0]
        self.assertEqual(tumor, normal)

    def test_dilution_is_treated_as_evaluation_only(self):
        """Dilution is the experimental condition; using it as a feature would be circular."""
        self.assertIn("dilution", EVALUATION_ONLY_FIELDS)
        for spec in ABLATION_GRID.values():
            for feature in feature_names(spec):
                self.assertNotIn("dilution", feature)

    def test_explicit_check_rejects_a_smuggled_field(self):
        with self.assertRaises(ValueError) as ctx:
            assert_no_evaluation_fields(["sequence__supports_alt", "meta__dilution"])
        self.assertIn("05_claim_boundaries", str(ctx.exception))

    def test_labels_come_from_a_separate_function(self):
        rows = [row(label="tumor"), row(label="normal"), row(label="")]
        self.assertEqual(extract_labels(rows), [1, 0, 0])


class AblationGridIntegrityTest(unittest.TestCase):
    """The grid must match the table in docs/research/04_evaluation_plan.md exactly."""

    EXPECTED = {
        "A": {"sequence"},
        "B": {"methylation"},
        "C": {"haplotype"},
        "D": {"sequence", "haplotype"},
        "E": {"sequence", "methylation"},
        "F": {"sequence", "haplotype", "methylation"},
    }

    def test_grid_matches_the_documented_design(self):
        self.assertEqual(
            {name: set(spec.modalities) for name, spec in ABLATION_GRID.items()},
            self.EXPECTED,
        )

    def test_each_model_uses_only_its_own_modalities(self):
        for name, spec in ABLATION_GRID.items():
            prefixes = {feature.split("__")[0] for feature in feature_names(spec)}
            self.assertEqual(prefixes, set(spec.modalities), f"model {name}")

    def test_feature_order_is_deterministic(self):
        for spec in ABLATION_GRID.values():
            self.assertEqual(feature_names(spec), feature_names(spec))


if __name__ == "__main__":
    unittest.main()
