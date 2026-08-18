#!/usr/bin/env python3
"""End-to-end smoke test: synthetic BAM → joint-molecule partitions → feasibility funnel.

Exercises both CLIs the way they are actually invoked, against a synthetic fixture. No real
BAM is touched: the real inputs are 80-300 GB, read-only, and owned by other users.

Also verifies the two guarantees that are easy to lose and expensive to discover late:
**resumability** (a second run skips completed regions) and **determinism** (a forced re-run
byte-reproduces the partition).
"""
from __future__ import annotations

import gzip
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tests", "fixtures"))

import synthetic_bam as sb  # noqa: E402

EXTRACT = os.path.join(REPO_ROOT, "workflow", "joint_molecule", "extract_joint_molecules.py")
FUNNEL = os.path.join(REPO_ROOT, "workflow", "feasibility_funnel", "report_funnel.py")

CONFIG_TEMPLATE = """\
id: EXP-SMOKE-001
title: synthetic smoke
hypothesis: H1
extraction:
  min_mapping_quality: 1
  min_allele_quality: 5
  min_cpg_per_read: 1
  read_end_exclusion_bp: 0
  methylation_call_threshold: 0.8
  require_haplotype: true
  require_methylation: true
thresholds:
  T_H1_min_molecules: {min_molecules}
  T_H1_min_stage_survival: {min_survival}
  T_H1_min_candidates: {min_candidates}
"""

UNSET_CONFIG = """\
id: EXP-SMOKE-002
extraction:
  min_mapping_quality: 1
  min_allele_quality: 5
  min_cpg_per_read: 1
  read_end_exclusion_bp: 0
  methylation_call_threshold: 0.8
thresholds:
  T_H1_min_molecules: null
  T_H1_min_stage_survival: null
  T_H1_min_candidates: null
"""


def run(cmd):
    env = dict(os.environ)
    env.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


class JointPipelineSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.fx = sb.simple_fixture(root)

        self.candidates = os.path.join(root, "candidates.tsv")
        with open(self.candidates, "w") as fh:
            fh.write("chrom\tpos\tref\talt\n")
            fh.write(f"{self.fx['contig']}\t{self.fx['candidate_position']}"
                     f"\t{self.fx['ref_base']}\t{self.fx['alt_base']}\n")

        self.config = os.path.join(root, "experiment.yaml")
        with open(self.config, "w") as fh:
            fh.write(CONFIG_TEMPLATE.format(min_molecules=1, min_survival=0.1, min_candidates=1))

        self.evidence_dir = os.path.join(root, "evidence")
        self.funnel_dir = os.path.join(root, "funnel")
        self.region = f"{self.fx['contig']}:{self.fx['region_start'] + 1}-{self.fx['region_end']}"

    def tearDown(self):
        self.tmp.cleanup()

    def _extract(self, *extra):
        return run([
            sys.executable, EXTRACT,
            "--bam", self.fx["bam"],
            "--candidates", self.candidates,
            "--config", self.config,
            "--sample-id", "SMOKE", "--dilution", "1e-2",
            "--region", self.region,
            "--outdir", self.evidence_dir,
            "--log-level", "WARNING",
            *extra,
        ])

    def test_extract_then_funnel(self):
        extract = self._extract()
        self.assertEqual(extract.returncode, 0, extract.stderr)
        self.assertIn("6 records", extract.stdout)

        partitions = os.listdir(os.path.join(self.evidence_dir, "regions"))
        self.assertEqual(len(partitions), 1)
        self.assertTrue(partitions[0].endswith(".tsv.gz"))

        manifest_path = os.path.join(self.evidence_dir, "manifest.json")
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path) as fh:
            manifest = json.load(fh)
        for key in ("tool_versions", "inputs", "config", "input_manifest_id", "command"):
            self.assertIn(key, manifest)

        funnel = run([
            sys.executable, FUNNEL,
            "--evidence-dir", self.evidence_dir,
            "--config", self.config,
            "--outdir", self.funnel_dir,
            "--log-level", "WARNING",
        ])
        self.assertEqual(funnel.returncode, 0, funnel.stderr)

        for name in ("by_sample", "by_dilution", "by_chromosome", "by_region",
                     "by_candidate", "by_phase_set", "by_haplotype_family"):
            self.assertTrue(os.path.exists(os.path.join(self.funnel_dir, f"funnel_{name}.tsv")), name)

        with open(os.path.join(self.funnel_dir, "funnel_summary.json")) as fh:
            summary = json.load(fh)

        stages = summary["overall_funnel"]["stage_counts"]
        self.assertEqual(stages["examined"], 6)
        self.assertEqual(stages["usable_joint_molecules"], 3)  # hap1_alt, hap1_ref, hap2_alt

        exclusions = summary["overall_funnel"]["exclusions"]
        self.assertEqual(exclusions["low_mapping_quality"], 1)
        self.assertEqual(exclusions["no_haplotype_tag"], 1)
        self.assertEqual(exclusions["no_methylation_tag"], 1)

        self.assertIn("methylation_profile", summary)
        self.assertIn("h1_evaluation", summary)

    def test_resumes_without_reprocessing(self):
        self.assertEqual(self._extract().returncode, 0)
        second = self._extract()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("0 records", second.stdout)  # every region already complete

    def test_forced_rerun_is_byte_identical(self):
        self.assertEqual(self._extract().returncode, 0)
        partition = os.path.join(
            self.evidence_dir, "regions",
            os.listdir(os.path.join(self.evidence_dir, "regions"))[0],
        )
        with open(partition, "rb") as fh:
            first = fh.read()

        self.assertEqual(self._extract("--force").returncode, 0)
        with open(partition, "rb") as fh:
            second = fh.read()
        self.assertEqual(first, second, "re-running a region must byte-reproduce its partition")

    def test_partition_contains_the_documented_columns(self):
        self.assertEqual(self._extract().returncode, 0)
        partition = os.path.join(
            self.evidence_dir, "regions",
            os.listdir(os.path.join(self.evidence_dir, "regions"))[0],
        )
        with gzip.open(partition, "rt") as fh:
            header = fh.readline().rstrip("\n").split("\t")
        for column in ("read_id", "observed_allele", "haplotype_tag", "phase_set",
                       "methylation_probabilities", "methylation_probabilities_5hmc",
                       "usable", "exclusion_reason", "tool_versions", "input_manifest_id"):
            self.assertIn(column, header)

    def test_missing_threshold_blocks_h1_instead_of_defaulting(self):
        """An undefined acceptance threshold must never silently become a pass."""
        self.assertEqual(self._extract().returncode, 0)
        unset = os.path.join(self.tmp.name, "unset.yaml")
        with open(unset, "w") as fh:
            fh.write(UNSET_CONFIG)

        result = run([
            sys.executable, FUNNEL,
            "--evidence-dir", self.evidence_dir,
            "--config", unset,
            "--outdir", os.path.join(self.tmp.name, "funnel_unset"),
            "--log-level", "WARNING",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BLOCKED", result.stdout)

        with open(os.path.join(self.tmp.name, "funnel_unset", "funnel_summary.json")) as fh:
            summary = json.load(fh)
        self.assertEqual(summary["h1_evaluation"]["decision"], "BLOCKED")

    def test_extraction_refuses_a_config_with_a_null_filter(self):
        broken = os.path.join(self.tmp.name, "broken.yaml")
        with open(broken, "w") as fh:
            fh.write("extraction:\n  min_mapping_quality: 1\n  min_allele_quality: null\n")
        result = run([
            sys.executable, EXTRACT,
            "--bam", self.fx["bam"], "--candidates", self.candidates, "--config", broken,
            "--sample-id", "SMOKE", "--dilution", "1e-2", "--region", self.region,
            "--outdir", os.path.join(self.tmp.name, "e2"), "--log-level", "WARNING",
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("min_allele_quality", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
