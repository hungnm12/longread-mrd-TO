"""Feasibility-funnel counting.

The funnel is the evidence H1 turns on, so these tests mostly guard against ways it could
silently overstate the usable count.
"""
from __future__ import annotations

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from src.evaluation.funnel import (  # noqa: E402
    STAGES,
    count_funnel,
    format_funnel_tsv,
    profile_methylation,
    stratified_funnel,
)
from src.joint_evidence.record import ExclusionReason  # noqa: E402


def record(reason="", **overrides):
    base = {
        "sample_id": "S1",
        "dilution": "1e-2",
        "chrom": "chr1",
        "region_id": "chr1_0_1000",
        "candidate_id": "chr1:500:C>T",
        "read_id": "r1",
        "phase_set": "777",
        "haplotype_tag": "1",
        "read_length": "1000",
        "cpg_positions": "10;20;30",
        "distance_of_cpgs_to_read_ends": "100;200;300",
        "exclusion_reason": reason,
        "usable": "0" if reason else "1",
    }
    base.update(overrides)
    return base


class FunnelStageTest(unittest.TestCase):
    def test_usable_record_reaches_every_stage(self):
        counts = count_funnel([record()])
        for stage in STAGES:
            self.assertEqual(counts.stage_counts[stage], 1, stage)

    def test_exclusion_stops_the_record_at_the_right_stage(self):
        counts = count_funnel([record(ExclusionReason.NO_HAPLOTYPE_TAG)])
        self.assertEqual(counts.stage_counts["examined"], 1)
        self.assertEqual(counts.stage_counts["candidate_overlapping"], 1)
        self.assertEqual(counts.stage_counts["allele_informative"], 1)
        self.assertEqual(counts.stage_counts["haplotagged"], 0)
        self.assertEqual(counts.stage_counts["usable_joint_molecules"], 0)

    def test_early_exclusion_stops_everything_downstream(self):
        counts = count_funnel([record(ExclusionReason.LOW_MAPPING_QUALITY)])
        self.assertEqual(counts.stage_counts["examined"], 1)
        for stage in STAGES[1:]:
            self.assertEqual(counts.stage_counts[stage], 0, stage)

    def test_stages_are_monotonically_non_increasing(self):
        records = [
            record(),
            record(ExclusionReason.NO_HAPLOTYPE_TAG),
            record(ExclusionReason.LOW_MAPPING_QUALITY),
            record(ExclusionReason.INSUFFICIENT_CPGS),
            record(ExclusionReason.ALLELE_NOT_ALIGNED),
        ]
        counts = count_funnel(records)
        values = [counts.stage_counts[s] for s in STAGES]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_exclusions_partition_the_examined_pairs(self):
        """Every non-usable record is counted under exactly one reason."""
        records = [
            record(),
            record(ExclusionReason.NO_HAPLOTYPE_TAG),
            record(ExclusionReason.NO_METHYLATION_TAG),
            record(ExclusionReason.LOW_ALLELE_QUALITY),
        ]
        counts = count_funnel(records)
        self.assertEqual(
            counts.stage_counts["examined"],
            counts.stage_counts["usable_joint_molecules"] + sum(counts.exclusions.values()),
        )

    def test_unmapped_exclusion_reason_refuses_to_be_counted(self):
        """An unmapped reason must not default to 'survived'; that would inflate H1."""
        with self.assertRaises(ValueError) as ctx:
            count_funnel([record("a_reason_nobody_registered")])
        self.assertIn("_STAGE_BLOCKERS", str(ctx.exception))

    def test_survival_is_nan_when_nothing_examined(self):
        counts = count_funnel([])
        self.assertNotEqual(counts.survival("usable_joint_molecules"),
                            counts.survival("usable_joint_molecules"))  # NaN != NaN


class StratifiedFunnelTest(unittest.TestCase):
    def test_groups_by_single_field(self):
        strata = stratified_funnel(
            [record(dilution="1e-2"), record(dilution="1e-3"), record(dilution="1e-3")],
            ("dilution",),
        )
        self.assertEqual(strata[("1e-2",)].stage_counts["examined"], 1)
        self.assertEqual(strata[("1e-3",)].stage_counts["examined"], 2)

    def test_haplotype_family_combines_phase_set_and_tag(self):
        """Grouping on haplotype_tag alone would pool unrelated phase blocks."""
        strata = stratified_funnel(
            [
                record(phase_set="777", haplotype_tag="1"),
                record(phase_set="888", haplotype_tag="1"),
            ],
            ("haplotype_family",),
        )
        self.assertEqual(set(strata), {("777:1",), ("888:1",)})

    def test_untagged_reads_get_an_empty_family_not_a_shared_one(self):
        strata = stratified_funnel(
            [record(phase_set="", haplotype_tag=""), record(phase_set="777", haplotype_tag="1")],
            ("haplotype_family",),
        )
        self.assertIn(("",), strata)
        self.assertIn(("777:1",), strata)

    def test_tsv_reports_every_rate_beside_its_denominator(self):
        strata = stratified_funnel([record(), record(ExclusionReason.NO_HAPLOTYPE_TAG)], ("dilution",))
        text = format_funnel_tsv(strata, ("dilution",))
        header = text.splitlines()[0].split("\t")
        for stage in STAGES:
            self.assertIn(stage, header)
        for stage in STAGES[1:]:
            self.assertIn(f"survival_{stage}", header)


class MethylationProfileTest(unittest.TestCase):
    def test_counts_each_molecule_once_across_candidates(self):
        """One read overlapping three candidates is one molecule, not three."""
        records = [
            record(read_id="r1", candidate_id="chr1:1:A>T"),
            record(read_id="r1", candidate_id="chr1:2:A>T"),
            record(read_id="r2", candidate_id="chr1:1:A>T"),
        ]
        profile = profile_methylation(records)
        self.assertEqual(profile.reads_total, 2)

    def test_missing_methylation_is_measured(self):
        profile = profile_methylation([
            record(read_id="r1", cpg_positions=""),
            record(read_id="r2", cpg_positions="10;20"),
        ])
        self.assertEqual(profile.reads_with_missing_methylation, 1)
        self.assertAlmostEqual(profile.methylation_missingness, 0.5)

    def test_summary_reports_quartiles_with_n(self):
        summary = profile_methylation([record(read_id=f"r{i}") for i in range(5)]).summary()
        self.assertEqual(summary["cpgs_per_read"]["n"], 5)
        self.assertEqual(summary["cpgs_per_read"]["median"], 3)

    def test_empty_distribution_reports_none_not_zero(self):
        """A missing statistic must not look like a measured zero."""
        summary = profile_methylation([]).summary()
        self.assertEqual(summary["cpgs_per_read"]["n"], 0)
        self.assertIsNone(summary["cpgs_per_read"]["median"])


if __name__ == "__main__":
    unittest.main()
