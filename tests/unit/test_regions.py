"""Region parsing, partitioning and merging.

``region_id`` is used as the partition filename, the resumability marker, the record column
and the Phase 5 split key at once, so these tests guard a load-bearing identifier.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from src.io.regions import (  # noqa: E402
    Region,
    merge_overlapping,
    parse_region,
    partition_contig,
    read_region_bed,
    region_id,
)


class RegionTest(unittest.TestCase):
    def test_rejects_empty_and_inverted(self):
        with self.assertRaises(ValueError):
            Region("chr1", 100, 100)
        with self.assertRaises(ValueError):
            Region("chr1", 200, 100)
        with self.assertRaises(ValueError):
            Region("chr1", -1, 100)

    def test_id_is_stable_and_filename_safe(self):
        self.assertEqual(Region("chr1", 0, 1000).id, "chr1_0_1000")
        self.assertEqual(region_id("chr1", 0, 1000), Region("chr1", 0, 1000).id)
        self.assertNotIn("/", Region("chr1", 0, 1000).id)
        self.assertNotIn(":", Region("chr1", 0, 1000).id)

    def test_str_is_one_based_samtools_style(self):
        self.assertEqual(str(Region("chr1", 0, 1000)), "chr1:1-1000")


class ParseRegionTest(unittest.TestCase):
    def test_converts_one_based_to_zero_based(self):
        self.assertEqual(parse_region("chr1:1001-2000"), Region("chr1", 1000, 2000))

    def test_tolerates_thousands_separators(self):
        self.assertEqual(parse_region("chr1:1,001-2,000"), Region("chr1", 1000, 2000))

    def test_bare_contig_rejected_with_actionable_message(self):
        with self.assertRaises(ValueError) as ctx:
            parse_region("chr1")
        self.assertIn("partition_contig", str(ctx.exception))


class PartitionContigTest(unittest.TestCase):
    def test_covers_contig_exactly_without_padding(self):
        regions = list(partition_contig("chr1", 2500, 1000))
        self.assertEqual([(r.start, r.end) for r in regions], [(0, 1000), (1000, 2000), (2000, 2500)])

    def test_partitions_do_not_overlap(self):
        regions = list(partition_contig("chr1", 10_000, 3_000))
        for earlier, later in zip(regions, regions[1:]):
            self.assertLessEqual(earlier.end, later.start)

    def test_rejects_non_positive_chunk(self):
        with self.assertRaises(ValueError):
            list(partition_contig("chr1", 1000, 0))


class MergeOverlappingTest(unittest.TestCase):
    def test_merges_overlapping_and_adjacent(self):
        merged = merge_overlapping([Region("chr1", 0, 100), Region("chr1", 50, 200)])
        self.assertEqual(merged, [Region("chr1", 0, 200)])

    def test_keeps_separate_contigs_apart(self):
        merged = merge_overlapping([Region("chr2", 0, 100), Region("chr1", 0, 100)])
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].chrom, "chr1")

    def test_merging_prevents_double_counting(self):
        """Overlapping partitions would emit the same read twice at one candidate."""
        merged = merge_overlapping(
            [Region("chr1", 0, 1000), Region("chr1", 900, 1500), Region("chr1", 1400, 1600)]
        )
        self.assertEqual(merged, [Region("chr1", 0, 1600)])

    def test_empty_input(self):
        self.assertEqual(merge_overlapping([]), [])


class ReadRegionBedTest(unittest.TestCase):
    def test_reads_zero_based_half_open_and_skips_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "r.bed")
            with open(path, "w") as fh:
                fh.write("# comment\ntrack name=x\n\nchr1\t100\t200\nchr2\t0\t50\tlabel\n")
            regions = read_region_bed(path)
        self.assertEqual(regions, [Region("chr1", 100, 200), Region("chr2", 0, 50)])

    def test_rejects_short_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "r.bed")
            with open(path, "w") as fh:
                fh.write("chr1\t100\n")
            with self.assertRaises(ValueError):
                read_region_bed(path)


if __name__ == "__main__":
    unittest.main()
