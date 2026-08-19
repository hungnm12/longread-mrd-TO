#!/usr/bin/env python3
"""EXP-G1-001 — do two PASS SNV candidates actually appear as ALT on the same molecule?

Proximity is an opportunity; this measures the observation. For each sampled candidate pair
close enough to share a read, every read covering both positions is classified by what it
carries at each: ALT-ALT, ALT-REF, REF-ALT, REF-REF, or other.

Read-only: the BAM and the truth VCF are opened for reading and nothing is written near them.
SEQC2 membership is attached *after* counting, and only to stratify the report — no pair is
selected or weighted by it.

    python3 scripts/workflow/linkage/measure_cooccurrence.py \\
        --config research/experiments/registry/EXP-G1-001.yaml \\
        --outdir outputs/active/results/linkage
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pysam  # noqa: E402
import yaml  # noqa: E402


def load_candidates(path: Path) -> dict[str, list[tuple[int, str, str]]]:
    """chrom -> sorted [(pos, ref, alt)] from the PASS candidate table."""
    by_chrom: dict[str, list[tuple[int, str, str]]] = {}
    with path.open() as handle:
        header = handle.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        for line in handle:
            f = line.rstrip("\n").split("\t")
            by_chrom.setdefault(f[idx["chrom"]], []).append(
                (int(f[idx["pos"]]), f[idx["ref"]], f[idx["alt"]])
            )
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return by_chrom


def build_pairs(by_chrom, window: int) -> list[tuple[str, tuple, tuple]]:
    """Every candidate pair whose positions are within `window` on the same contig."""
    pairs = []
    for chrom, entries in by_chrom.items():
        for i, first in enumerate(entries):
            for second in entries[i + 1 :]:
                if second[0] - first[0] > window:
                    break
                pairs.append((chrom, first, second))
    return pairs


def load_seqc2(path: Path) -> set[tuple[str, int]]:
    """Positions of high-confidence somatic SNVs. Used only to stratify the report."""
    sites: set[tuple[str, int]] = set()
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            f = line.split("\t", 3)
            sites.add((f[0], int(f[1])))
    return sites


def base_at(read, ref_pos: int, min_bq: int) -> str | None:
    """The read's aligned base at a reference position, or None if it is not covered."""
    for read_pos, pos in read.get_aligned_pairs(matches_only=True):
        if pos == ref_pos:
            if read.query_qualities and read.query_qualities[read_pos] < min_bq:
                return None
            return read.query_sequence[read_pos].upper()
    return None


def classify_pair(bam, chrom, first, second, params) -> Counter:
    """Count how reads covering both positions behave at each."""
    (pos_a, ref_a, alt_a), (pos_b, ref_b, alt_b) = first, second
    counts: Counter = Counter()
    for read in bam.fetch(chrom, pos_a - 1, pos_a):
        if read.is_unmapped or read.is_secondary or read.is_supplementary:
            continue
        if read.mapping_quality < params["min_mapping_quality"]:
            continue
        # Only reads that actually span both positions can speak to co-occurrence.
        if read.reference_start > pos_b - 1 or read.reference_end < pos_b:
            counts["covers_one_only"] += 1
            continue
        base_a = base_at(read, pos_a - 1, params["min_base_quality"])
        base_b = base_at(read, pos_b - 1, params["min_base_quality"])
        if base_a is None or base_b is None:
            counts["unreadable"] += 1
            continue
        counts["covers_both"] += 1
        is_alt_a, is_alt_b = base_a == alt_a.upper(), base_b == alt_b.upper()
        is_ref_a, is_ref_b = base_a == ref_a.upper(), base_b == ref_b.upper()
        if is_alt_a and is_alt_b:
            counts["alt_alt"] += 1
        elif is_alt_a and is_ref_b:
            counts["alt_ref"] += 1
        elif is_ref_a and is_alt_b:
            counts["ref_alt"] += 1
        elif is_ref_a and is_ref_b:
            counts["ref_ref"] += 1
        else:
            counts["other"] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--bam", type=Path, help="override the BAM in the config")
    parser.add_argument("--label", default="pure_tumor")
    args = parser.parse_args()

    spec = yaml.safe_load(args.config.read_text())
    params = spec["parameters"]
    inputs = {item["role"].split()[0].lower(): item["path"] for item in spec["inputs"]}
    candidates_path = Path(REPO_ROOT) / spec["inputs"][0]["path"]
    bam_path = Path(args.bam) if args.bam else Path(spec["inputs"][1]["path"])
    truth_path = Path(spec["inputs"][2]["path"])

    print(f"candidates: {candidates_path}")
    by_chrom = load_candidates(candidates_path)
    total_candidates = sum(len(v) for v in by_chrom.values())

    pairs = build_pairs(by_chrom, params["pair_window_bp"])
    print(f"{total_candidates:,} candidates → {len(pairs):,} pairs within {params['pair_window_bp']:,} bp")

    rng = random.Random(params["seed"])
    sampled = rng.sample(pairs, min(params["sample_pairs"], len(pairs)))
    sampled.sort()

    bam = pysam.AlignmentFile(str(bam_path), "rb")
    rows = []
    for index, (chrom, first, second) in enumerate(sampled, start=1):
        counts = classify_pair(bam, chrom, first, second, params)
        rows.append(
            {
                "chrom": chrom,
                "pos_a": first[0],
                "pos_b": second[0],
                "distance": second[0] - first[0],
                "ref_a": first[1], "alt_a": first[2],
                "ref_b": second[1], "alt_b": second[2],
                **{k: counts.get(k, 0) for k in
                   ("covers_both", "alt_alt", "alt_ref", "ref_alt", "ref_ref", "other",
                    "covers_one_only", "unreadable")},
            }
        )
        if index % 100 == 0:
            print(f"  {index}/{len(sampled)} pairs")
    bam.close()

    # Truth is read only now, after every count exists.
    seqc2 = load_seqc2(truth_path)
    for row in rows:
        in_a = (row["chrom"], row["pos_a"]) in seqc2
        in_b = (row["chrom"], row["pos_b"]) in seqc2
        row["seqc2_stratum"] = "both" if in_a and in_b else ("one" if in_a or in_b else "neither")

    args.outdir.mkdir(parents=True, exist_ok=True)
    tsv = args.outdir / f"cooccurrence_{args.label}.tsv"
    with tsv.open("w") as handle:
        handle.write("\t".join(rows[0].keys()) + "\n")
        for row in rows:
            handle.write("\t".join(str(v) for v in row.values()) + "\n")

    evaluable = [r for r in rows if r["covers_both"] > 0]
    with_alt_alt = [r for r in evaluable if r["alt_alt"] > 0]
    with_support2 = [r for r in evaluable if r["alt_alt"] >= 2]

    def stratum(name):
        subset = [r for r in evaluable if r["seqc2_stratum"] == name]
        hit = [r for r in subset if r["alt_alt"] > 0]
        return {
            "pairs_evaluable": len(subset),
            "pairs_with_alt_alt": len(hit),
            "pct": round(100 * len(hit) / len(subset), 2) if subset else None,
        }

    summary = {
        "experiment": spec["id"],
        "label": args.label,
        "bam": str(bam_path),
        "parameters": params,
        "candidates_total": total_candidates,
        "pairs_within_window": len(pairs),
        "pairs_sampled": len(sampled),
        "pairs_evaluable": len(evaluable),
        "pairs_with_alt_alt": len(with_alt_alt),
        "pairs_with_alt_alt_pct": round(100 * len(with_alt_alt) / len(evaluable), 2) if evaluable else None,
        "pairs_with_alt_alt_support_2plus": len(with_support2),
        "reads_covering_both": sum(r["covers_both"] for r in rows),
        "reads_alt_alt": sum(r["alt_alt"] for r in rows),
        "reads_alt_ref": sum(r["alt_ref"] for r in rows),
        "reads_ref_alt": sum(r["ref_alt"] for r in rows),
        "reads_ref_ref": sum(r["ref_ref"] for r in rows),
        "by_seqc2_stratum": {name: stratum(name) for name in ("both", "one", "neither")},
    }
    (args.outdir / f"cooccurrence_{args.label}.summary.json").write_text(json.dumps(summary, indent=2))

    print("\n--- EXP-G1-001 summary ---")
    for key in ("pairs_sampled", "pairs_evaluable", "pairs_with_alt_alt",
                "pairs_with_alt_alt_pct", "pairs_with_alt_alt_support_2plus",
                "reads_covering_both", "reads_alt_alt", "reads_alt_ref",
                "reads_ref_alt", "reads_ref_ref"):
        print(f"  {key}: {summary[key]}")
    print("  by SEQC2 stratum:")
    for name, stats in summary["by_seqc2_stratum"].items():
        print(f"    {name:8s} evaluable {stats['pairs_evaluable']:4d}  with ALT-ALT {stats['pairs_with_alt_alt']:4d}  {stats['pct']}%")
    print(f"\nwrote {tsv}")


if __name__ == "__main__":
    main()
