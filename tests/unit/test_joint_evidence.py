"""Joint-molecule extraction, exclusion ordering, and the writer's guarantees."""
from __future__ import annotations

import gzip
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tests", "fixtures"))

import pysam  # noqa: E402
import synthetic_bam as sb  # noqa: E402

from src.io.regions import Region  # noqa: E402
from src.joint_evidence import (  # noqa: E402
    Candidate,
    ExtractionConfig,
    JointEvidenceStore,
    JointMoleculeRecord,
    extract_region,
    input_manifest_id,
)
from src.joint_evidence.record import FIELDS, ExclusionReason  # noqa: E402

PERMISSIVE = dict(
    min_mapping_quality=1,
    min_allele_quality=5,
    min_cpg_per_read=1,
    read_end_exclusion_bp=0,
    methylation_call_threshold=0.8,
)


class ExtractionConfigTest(unittest.TestCase):
    def test_missing_threshold_is_a_hard_stop(self):
        """A defaulted threshold would be an unrecorded research decision."""
        broken = dict(PERMISSIVE)
        broken["min_cpg_per_read"] = None
        with self.assertRaises(ValueError) as ctx:
            ExtractionConfig.from_dict(broken)
        self.assertIn("min_cpg_per_read", str(ctx.exception))
        self.assertIn("config/experiments", str(ctx.exception))

    def test_lists_every_missing_threshold_at_once(self):
        with self.assertRaises(ValueError) as ctx:
            ExtractionConfig.from_dict({})
        message = str(ctx.exception)
        for key in PERMISSIVE:
            self.assertIn(key, message)


class ExtractRegionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx = sb.simple_fixture(self.tmp.name)
        self.bam = pysam.AlignmentFile(self.fx["bam"])
        self.region = Region(self.fx["contig"], self.fx["region_start"], self.fx["region_end"])
        self.candidate = Candidate(
            self.fx["contig"], self.fx["candidate_position"],
            self.fx["ref_base"], self.fx["alt_base"],
        )

    def tearDown(self):
        self.bam.close()
        self.tmp.cleanup()

    def _extract(self, **overrides):
        cfg = dict(PERMISSIVE)
        cfg.update(overrides)
        return extract_region(
            self.bam, self.region, [self.candidate],
            ExtractionConfig.from_dict(cfg),
            sample_id="S1", dilution="1e-2",
        )

    def _by_read(self, records):
        return {r.read_id: r for r in records}

    def test_emits_one_record_per_examined_read(self):
        records = self._extract()
        self.assertEqual(len(records), 6)

    def test_unusable_reads_are_recorded_not_dropped(self):
        """The funnel is a GROUP BY over these rows, so exclusions must be present."""
        by_read = self._by_read(self._extract())
        self.assertEqual(by_read["no_hp"].exclusion_reason, ExclusionReason.NO_HAPLOTYPE_TAG)
        self.assertEqual(by_read["no_mm"].exclusion_reason, ExclusionReason.NO_METHYLATION_TAG)
        self.assertEqual(by_read["low_mapq"].exclusion_reason, ExclusionReason.LOW_MAPPING_QUALITY)
        for name in ("no_hp", "no_mm", "low_mapq"):
            self.assertEqual(by_read[name].usable, 0)

    def test_usable_reads_carry_all_three_modalities(self):
        by_read = self._by_read(self._extract())
        for name in ("hap1_alt", "hap1_ref", "hap2_alt"):
            record = by_read[name]
            self.assertEqual(record.usable, 1, name)
            self.assertEqual(record.exclusion_reason, "")
            self.assertTrue(record.observed_allele)
            self.assertIsNotNone(record.haplotype_tag)
            self.assertIsNotNone(record.phase_set)
            self.assertGreater(len(record.cpg_positions), 0)

    def test_alleles_are_read_correctly(self):
        by_read = self._by_read(self._extract())
        self.assertEqual(by_read["hap1_alt"].observed_allele, self.fx["alt_base"])
        self.assertEqual(by_read["hap1_ref"].observed_allele, self.fx["ref_base"])

    def test_haplotype_families_are_distinguished(self):
        by_read = self._by_read(self._extract())
        self.assertEqual(by_read["hap1_alt"].haplotype_tag, 1)
        self.assertEqual(by_read["hap2_alt"].haplotype_tag, 2)
        self.assertEqual(by_read["hap1_alt"].phase_set, by_read["hap2_alt"].phase_set)

    def test_first_failure_wins_so_reasons_partition(self):
        """low_mapq also lacks nothing else, but MAPQ is checked first and must win."""
        by_read = self._by_read(self._extract(min_mapping_quality=60))
        self.assertEqual(by_read["low_mapq"].exclusion_reason, ExclusionReason.LOW_MAPPING_QUALITY)

    def test_min_cpg_threshold_excludes_low_cpg_reads(self):
        by_read = self._by_read(self._extract(min_cpg_per_read=10_000))
        self.assertEqual(by_read["hap1_alt"].exclusion_reason, ExclusionReason.INSUFFICIENT_CPGS)
        # counts are still populated, so the funnel can report how close it came
        self.assertGreater(len(by_read["hap1_alt"].cpg_positions), 0)

    def test_require_haplotype_false_admits_untagged_reads(self):
        by_read = self._by_read(self._extract(require_haplotype=False))
        self.assertEqual(by_read["no_hp"].usable, 1)
        self.assertIsNone(by_read["no_hp"].haplotype_tag)

    def test_records_are_sorted_deterministically(self):
        records = self._extract()
        self.assertEqual([r.sort_key for r in records], sorted(r.sort_key for r in records))

    def test_candidates_outside_region_are_ignored(self):
        far = Candidate(self.fx["contig"], 19_000, "A", "T")
        records = extract_region(
            self.bam, self.region, [far],
            ExtractionConfig.from_dict(PERMISSIVE), sample_id="S1", dilution="1e-2",
        )
        self.assertEqual(records, [])

    def test_evaluation_labels_are_attached_but_do_not_filter(self):
        cfg = ExtractionConfig.from_dict(PERMISSIVE)
        labelled = extract_region(
            self.bam, self.region, [self.candidate], cfg,
            sample_id="S1", dilution="1e-2",
            source_labels={"hap1_alt": "tumor", "hap1_ref": "normal"},
        )
        unlabelled = extract_region(
            self.bam, self.region, [self.candidate], cfg, sample_id="S1", dilution="1e-2",
        )
        by_read = self._by_read(labelled)
        self.assertEqual(by_read["hap1_alt"].source_label_for_evaluation_only, "tumor")
        self.assertEqual(by_read["hap2_alt"].source_label_for_evaluation_only, "")
        # labels must not change which reads are usable
        self.assertEqual(
            [(r.read_id, r.usable, r.exclusion_reason) for r in labelled],
            [(r.read_id, r.usable, r.exclusion_reason) for r in unlabelled],
        )


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JointEvidenceStore(os.path.join(self.tmp.name, "evidence"))
        self.records = [
            JointMoleculeRecord(
                sample_id="S1", dilution="1e-2", chrom="chr1", region_id="chr1_0_1000",
                candidate_id="chr1:500:C>T", candidate_position=500, read_id=name,
                observed_allele="T", usable=1,
                methylation_probabilities=[0.9012345],
                cpg_positions=[10, 20],
            )
            for name in ("read_b", "read_a")
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def test_round_trip_preserves_columns(self):
        self.store.write_partition("chr1_0_1000", self.records)
        rows = self.store.read_partition("chr1_0_1000")
        self.assertEqual(len(rows), 2)
        self.assertEqual(set(rows[0]), set(FIELDS))
        self.assertEqual(rows[0]["read_id"], "read_a")  # sorted

    def test_writes_are_byte_reproducible(self):
        """gzip mtime=0 and fixed float precision, so a re-run diffs to nothing."""
        self.store.write_partition("chr1_0_1000", self.records)
        with open(self.store.partition_path("chr1_0_1000"), "rb") as fh:
            first = fh.read()
        self.store.write_partition("chr1_0_1000", list(reversed(self.records)))
        with open(self.store.partition_path("chr1_0_1000"), "rb") as fh:
            second = fh.read()
        self.assertEqual(first, second)

    def test_floats_are_fixed_precision(self):
        self.store.write_partition("chr1_0_1000", self.records)
        with gzip.open(self.store.partition_path("chr1_0_1000"), "rt") as fh:
            body = fh.read()
        self.assertIn("0.901", body)
        self.assertNotIn("0.9012345", body)

    def test_list_columns_use_the_documented_separator(self):
        self.store.write_partition("chr1_0_1000", self.records)
        rows = self.store.read_partition("chr1_0_1000")
        self.assertEqual(rows[0]["cpg_positions"], "10;20")

    def test_completion_marker_gates_resumability(self):
        self.assertFalse(self.store.is_complete("chr1_0_1000"))
        self.store.write_partition("chr1_0_1000", self.records)
        self.assertTrue(self.store.is_complete("chr1_0_1000"))
        self.assertEqual(self.store.completed_regions(), ["chr1_0_1000"])

    def test_marker_without_data_is_not_complete(self):
        """Guards against a stale marker being trusted after its partition is removed."""
        self.store.write_partition("chr1_0_1000", self.records)
        os.remove(self.store.partition_path("chr1_0_1000"))
        self.assertFalse(self.store.is_complete("chr1_0_1000"))

    def test_no_temp_file_survives_a_successful_write(self):
        self.store.write_partition("chr1_0_1000", self.records)
        leftovers = [n for n in os.listdir(self.store.regions_dir) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])


class ManifestIdTest(unittest.TestCase):
    def test_same_inputs_give_same_id(self):
        a = input_manifest_id({"bam": "/x.bam"}, {"min_cpg_per_read": 3})
        b = input_manifest_id({"bam": "/x.bam"}, {"min_cpg_per_read": 3})
        self.assertEqual(a, b)

    def test_config_change_changes_id(self):
        a = input_manifest_id({"bam": "/x.bam"}, {"min_cpg_per_read": 3})
        b = input_manifest_id({"bam": "/x.bam"}, {"min_cpg_per_read": 4})
        self.assertNotEqual(a, b)

    def test_key_order_does_not_change_id(self):
        a = input_manifest_id({"bam": "/x.bam", "vcf": "/y.vcf"})
        b = input_manifest_id({"vcf": "/y.vcf", "bam": "/x.bam"})
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
