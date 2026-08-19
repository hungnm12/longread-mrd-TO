"""MM/ML parsing and per-CpG evidence.

Uses ``unittest`` from the standard library rather than pytest, which is not installed in
this environment (``docs/repo_audit.md`` §11). pytest can still collect and run these files
if it is installed later.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tests", "fixtures"))

import pysam  # noqa: E402
import synthetic_bam as sb  # noqa: E402

from src.methylation.mod_bases import (  # noqa: E402
    CpGEvidence,
    read_cpg_evidence,
    summarize_calls,
)


class ProbabilityDecodingTest(unittest.TestCase):
    """The ML byte encodes an interval; we decode to its midpoint."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        seq = "ACGACGACGACG"  # 4 cytosines
        read = sb.SyntheticRead(
            "r1", 100, seq,
            prob_5mc=[0.0, 0.5, 0.9, 1.0],
            prob_5hmc=[0.0, 0.1, 0.02, 0.0],
        )
        self.bam_path = sb.write_bam(os.path.join(self.tmp.name, "p.bam"), [read])

    def tearDown(self):
        self.tmp.cleanup()

    def _evidence(self) -> CpGEvidence:
        with pysam.AlignmentFile(self.bam_path) as bam:
            read = next(bam.fetch("chr1", 90, 200))
            return read_cpg_evidence(read)

    def test_all_cytosines_reported(self):
        self.assertEqual(len(self._evidence()), 4)

    def test_probabilities_round_trip_within_one_quantum(self):
        evidence = self._evidence()
        for observed, encoded in zip(evidence.prob_5mc, [0.0, 0.5, 0.9, 1.0]):
            self.assertLess(abs(observed - encoded), 1 / 256.0 + 1e-9)

    def test_zero_probability_decodes_above_zero(self):
        """floor(0 * 256) = 0, but the byte means [0, 1/256) — the midpoint is not 0.0.

        Decoding to 0.0 would assert certainty the basecaller never expressed.
        """
        self.assertGreater(self._evidence().prob_5mc[0], 0.0)
        self.assertLess(self._evidence().prob_5mc[0], 1 / 256.0)

    def test_5mc_and_5hmc_kept_separate(self):
        evidence = self._evidence()
        self.assertNotEqual(evidence.prob_5mc, evidence.prob_5hmc)
        self.assertEqual(len(evidence.prob_5mc), len(evidence.prob_5hmc))

    def test_reference_positions_resolved(self):
        evidence = self._evidence()
        self.assertTrue(all(p is not None for p in evidence.ref_positions))
        # all-match CIGAR starting at 100 → ref == 100 + query offset
        self.assertEqual(evidence.ref_positions[0], 100 + evidence.query_positions[0])


class ReadWithoutTagsTest(unittest.TestCase):
    def test_absent_tags_yield_empty_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            read = sb.SyntheticRead("plain", 100, "ACGACG", with_modifications=False)
            path = sb.write_bam(os.path.join(tmp, "p.bam"), [read])
            with pysam.AlignmentFile(path) as bam:
                evidence = read_cpg_evidence(next(bam.fetch("chr1", 90, 200)))
            self.assertEqual(len(evidence), 0)
            self.assertEqual(evidence.prob_5mc, [])


class ReadEndExclusionTest(unittest.TestCase):
    def setUp(self):
        self.evidence = CpGEvidence(
            read_id="r",
            ref_positions=[10, 20, 30, 40],
            query_positions=[0, 10, 20, 99],
            prob_5mc=[0.9, 0.9, 0.9, 0.9],
            prob_5hmc=[0.01, 0.01, 0.01, 0.01],
            distance_to_read_end=[0, 10, 20, 0],
        )

    def test_excludes_both_ends(self):
        kept = self.evidence.exclude_read_ends(5)
        self.assertEqual(kept.distance_to_read_end, [10, 20])
        self.assertEqual(kept.ref_positions, [20, 30])

    def test_zero_window_is_a_no_op(self):
        self.assertEqual(len(self.evidence.exclude_read_ends(0)), 4)

    def test_all_lists_stay_index_aligned(self):
        kept = self.evidence.exclude_read_ends(15)
        for values in (kept.ref_positions, kept.query_positions, kept.prob_5mc,
                       kept.prob_5hmc, kept.distance_to_read_end):
            self.assertEqual(len(values), len(kept))


class SummarizeCallsTest(unittest.TestCase):
    def _evidence(self, probs):
        return CpGEvidence(
            read_id="r",
            ref_positions=list(range(len(probs))),
            query_positions=list(range(len(probs))),
            prob_5mc=list(probs),
            prob_5hmc=[0.0] * len(probs),
            distance_to_read_end=[100] * len(probs),
        )

    def test_counts_confident_calls_only(self):
        methylated, unmethylated = summarize_calls(self._evidence([0.95, 0.05, 0.5]), 0.9)
        self.assertEqual((methylated, unmethylated), (1, 1))

    def test_ambiguous_cpgs_counted_in_neither(self):
        """The gap is the read's ambiguity mass and must remain recoverable.

        A read with 100 uncertain CpGs must not look like one with 100 confident ones.
        """
        evidence = self._evidence([0.5] * 10)
        methylated, unmethylated = summarize_calls(evidence, 0.9)
        self.assertEqual((methylated, unmethylated), (0, 0))
        self.assertEqual(len(evidence), 10)

    def test_rejects_threshold_below_half(self):
        with self.assertRaises(ValueError):
            summarize_calls(self._evidence([0.9]), 0.4)


if __name__ == "__main__":
    unittest.main()
