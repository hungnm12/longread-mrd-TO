#!/usr/bin/env python3
"""Report the H1 feasibility funnel from written joint-molecule partitions.

Reads the partitions produced by ``workflow/joint_molecule/extract_joint_molecules.py`` and
answers the first scientific question of the project: **are there enough molecules carrying
allele, haplotype and methylation evidence at once to test H2?**

It reports counts and distributions. It does **not** decide. Acceptance is compared against
thresholds that must already be recorded in the experiment config
(``docs/research/03_hypotheses.md``), and an undefined threshold is a hard stop.

  python workflow/feasibility_funnel/report_funnel.py \\
      --evidence-dir results/joint_evidence/HCC1395_TF1e-2_25x_rep1 \\
      --config       config/experiments/h1_feasibility.yaml \\
      --outdir       results/feasibility/HCC1395_TF1e-2_25x_rep1
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import yaml  # noqa: E402

from src.evaluation.funnel import (  # noqa: E402
    STAGES,
    count_funnel,
    format_funnel_tsv,
    profile_methylation,
    stratified_funnel,
)
from src.joint_evidence import JointEvidenceStore  # noqa: E402

LOGGER = logging.getLogger("report_funnel")

#: Strata H1 requires. Each becomes one TSV.
STRATIFICATIONS = {
    "by_sample": ("sample_id",),
    "by_dilution": ("sample_id", "dilution"),
    "by_chromosome": ("chrom",),
    "by_region": ("region_id",),
    "by_candidate": ("candidate_id",),
    "by_phase_set": ("phase_set",),
    "by_haplotype_family": ("haplotype_family",),
}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--evidence-dir", required=True, action="append",
                   help="joint-evidence output dir; repeat to pool several samples")
    p.add_argument("--config", required=True, help="experiment YAML holding thresholds.*")
    p.add_argument("--outdir", required=True)
    p.add_argument("--log-level", default="INFO")
    return p.parse_args(argv)


def load_records(evidence_dirs):
    """Stream every completed partition from every evidence directory."""
    records = []
    for directory in evidence_dirs:
        store = JointEvidenceStore(directory)
        region_ids = store.completed_regions()
        if not region_ids:
            LOGGER.warning("%s: no completed partitions", directory)
        for region_id in region_ids:
            records.extend(store.read_partition(region_id))
        LOGGER.info("%s: %d partitions loaded", directory, len(region_ids))
    return records


def evaluate_h1(counts, config):
    """Compare observed counts against the pre-registered H1 thresholds.

    Returns a verdict dict. A threshold left ``null`` produces ``BLOCKED``, never a
    silently-defaulted pass — see ``docs/research/03_hypotheses.md``.
    """
    thresholds = (config.get("thresholds") or {})
    required = ["T_H1_min_molecules", "T_H1_min_stage_survival", "T_H1_min_candidates"]
    missing = [key for key in required if thresholds.get(key) is None]
    if missing:
        return {
            "decision": "BLOCKED",
            "reason": (
                "H1 acceptance thresholds are undefined: " + ", ".join(missing)
                + ". Set them in the experiment config before running, not after."
            ),
            "thresholds": {k: thresholds.get(k) for k in required},
        }

    usable = counts.stage_counts["usable_joint_molecules"]
    weakest_stage, weakest_survival = min(
        ((s, counts.survival(s)) for s in STAGES[1:]), key=lambda kv: kv[1]
    )
    return {
        "decision": None,  # filled by a human or by the registry, never guessed here
        "observed": {
            "usable_joint_molecules": usable,
            "weakest_stage": weakest_stage,
            "weakest_stage_survival": weakest_survival,
        },
        "thresholds": {k: thresholds[k] for k in required},
        "checks": {
            "molecules_meet_threshold": usable >= thresholds["T_H1_min_molecules"],
            "no_stage_collapse": weakest_survival >= thresholds["T_H1_min_stage_survival"],
        },
        "note": (
            "Stage survivals are not independent — read length drives both CpG count and "
            "haplotagging probability — so they are reported separately and never multiplied."
        ),
    }


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s %(name)s | %(message)s")

    with open(args.config) as fh:
        config = yaml.safe_load(fh) or {}

    records = load_records(args.evidence_dir)
    if not records:
        raise SystemExit("no records found; run extract_joint_molecules.py first")
    LOGGER.info("loaded %d joint-molecule records", len(records))

    os.makedirs(args.outdir, exist_ok=True)

    overall = count_funnel(records)
    for name, by in STRATIFICATIONS.items():
        strata = stratified_funnel(records, by)
        path = os.path.join(args.outdir, f"funnel_{name}.tsv")
        with open(path, "w") as fh:
            fh.write(format_funnel_tsv(strata, by))
        LOGGER.info("wrote %s (%d strata)", path, len(strata))

    profile = profile_methylation(records)
    summary = {
        "overall_funnel": overall.as_dict(),
        "methylation_profile": profile.summary(),
        "h1_evaluation": evaluate_h1(overall, config),
    }
    summary_path = os.path.join(args.outdir, "funnel_summary.json")
    with open(summary_path, "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")

    print(f"[report_funnel] {len(records)} records -> {args.outdir}")
    for stage in STAGES:
        print(f"  {stage:26s} {overall.stage_counts[stage]:>10,}  survival={overall.survival(stage):.4f}")
    if overall.exclusions:
        print("  exclusions:")
        for reason, n in sorted(overall.exclusions.items(), key=lambda kv: -kv[1]):
            print(f"    {reason:28s} {n:>10,}")
    verdict = summary["h1_evaluation"]
    if verdict.get("decision") == "BLOCKED":
        print(f"\n  H1: BLOCKED — {verdict['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
