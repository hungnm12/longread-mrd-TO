#!/usr/bin/env python3
"""EXP-G1-002, supplementary — POST-HOC, added after Arm B was seen and before Arm A finished.

Not pre-registered and not scored against any threshold. It exists because Arm B came back null
and that raised a question the registered design does not answer: the "neither" stratum mixes two
very different things.

  A candidate INSIDE a SEQC2 high-confidence region but absent from the sSNV list is confidently
  not somatic. A candidate OUTSIDE those regions is simply unassessed — SEQC2 says nothing about
  it either way. EXP-G1-001 treated both as "neither", which is what makes the stratum weak.

This splits them, and describes what is left once the germline arms have taken what they can:
per-pair ALT-ALT read fraction (0.5 is a heterozygous pair in cis, 1.0 a homozygous one, low and
scattered is subclonal or artefactual) and candidate VAF.

    python3 scripts/workflow/linkage/characterise_residual.py \\
        --table outputs/active/results/linkage/germline_confound_pure_tumor.tsv \\
        --outdir outputs/active/results/linkage
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

HC_BED = Path("/big8_disk/data/HCC1395/SEQC2/High-Confidence_Regions_v1.2.bed")
CANDIDATES = Path("outputs/active/results/tumor_only/HCC1395/candidate_pass_snvs.tsv")


def load_hc_regions(path: Path) -> dict[str, tuple[list[int], list[int]]]:
    starts: dict[str, list[int]] = defaultdict(list)
    ends: dict[str, list[int]] = defaultdict(list)
    with path.open() as handle:
        for line in handle:
            f = line.split("\t")
            if len(f) < 3:
                continue
            starts[f[0]].append(int(f[1]))
            ends[f[0]].append(int(f[2]))
    return {c: (starts[c], ends[c]) for c in starts}


def in_hc(regions, chrom: str, pos: int) -> bool:
    """BED is 0-based half-open; a 1-based VCF position p sits at offset p-1."""
    if chrom not in regions:
        return False
    starts, ends = regions[chrom]
    i = bisect.bisect_right(starts, pos - 1) - 1
    return i >= 0 and ends[i] > pos - 1


def describe(rows, label) -> dict:
    if not rows:
        return {"label": label, "pairs": 0}
    frac = [r["alt_alt"] / r["covers_both"] for r in rows if r["covers_both"] > 0]
    hit = [r for r in rows if r["alt_alt"] > 0]
    out = {
        "label": label,
        "pairs": len(rows),
        "pairs_with_alt_alt": len(hit),
        "pct_with_alt_alt": round(100 * len(hit) / len(rows), 2),
        "median_alt_alt_read_fraction": round(st.median(frac), 3) if frac else None,
        "near_half_0.35_0.65": round(sum(1 for f in frac if 0.35 <= f <= 0.65) / len(frac), 3) if frac else None,
        "near_one_ge_0.85": round(sum(1 for f in frac if f >= 0.85) / len(frac), 3) if frac else None,
        "below_0.15": round(sum(1 for f in frac if f < 0.15) / len(frac), 3) if frac else None,
    }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    rows = list(csv.DictReader(args.table.open(), delimiter="\t"))
    for r in rows:
        for k in ("pos_a", "pos_b", "distance", "covers_both", "alt_alt", "n_covers_both", "n_alt_alt"):
            r[k] = int(r[k])
        r["normal_germline_pair"] = r["normal_germline_pair"] == "True"
        r["popdb_germline_pair"] = r["popdb_germline_pair"] == "True"
        r["germline_supported"] = r["germline_supported"] == "True"

    vaf = {}
    with CANDIDATES.open() as handle:
        for c in csv.DictReader(handle, delimiter="\t"):
            vaf[(c["chrom"], int(c["pos"]))] = float(c["vaf"])

    regions = load_hc_regions(HC_BED)
    for r in rows:
        r["hc_a"] = in_hc(regions, r["chrom"], r["pos_a"])
        r["hc_b"] = in_hc(regions, r["chrom"], r["pos_b"])
        r["hc_pair"] = r["hc_a"] and r["hc_b"]

    evaluable = [r for r in rows if r["covers_both"] > 0]
    neither = [r for r in evaluable if r["seqc2_stratum"] == "neither"]

    report = {
        "note": "POST-HOC descriptive analysis. No pre-registered threshold applies to anything here.",
        "pairs_evaluable": len(evaluable),
        "hc_split_of_neither_stratum": {
            "both_candidates_in_hc_regions": describe(
                [r for r in neither if r["hc_pair"]], "neither, assessed by SEQC2 and not somatic"),
            "at_least_one_outside_hc": describe(
                [r for r in neither if not r["hc_pair"]], "neither, but SEQC2 never assessed it"),
        },
        "by_stratum_and_germline": {},
        "residual_after_germline_arms": {},
        "vaf_by_group": {},
    }

    for stratum in ("both", "one", "neither"):
        sub = [r for r in evaluable if r["seqc2_stratum"] == stratum]
        report["by_stratum_and_germline"][stratum] = {
            "germline_supported": describe([r for r in sub if r["germline_supported"]], "germline-supported"),
            "not_germline_supported": describe([r for r in sub if not r["germline_supported"]], "residual"),
        }

    residual = [r for r in evaluable if not r["germline_supported"]]
    report["residual_after_germline_arms"] = {
        "total": len(residual),
        "in_hc_and_not_somatic": len([r for r in residual
                                      if r["seqc2_stratum"] == "neither" and r["hc_pair"]]),
        "unassessed": len([r for r in residual
                           if r["seqc2_stratum"] == "neither" and not r["hc_pair"]]),
        "confirmed_somatic": len([r for r in residual if r["seqc2_stratum"] == "both"]),
    }

    for name, rowset in (("germline_supported", [r for r in evaluable if r["germline_supported"]]),
                         ("residual", residual)):
        vals = []
        for r in rowset:
            for pos in (r["pos_a"], r["pos_b"]):
                v = vaf.get((r["chrom"], pos))
                if v is not None:
                    vals.append(v)
        report["vaf_by_group"][name] = {
            "candidates": len(vals),
            "median_vaf": round(st.median(vals), 3) if vals else None,
            "frac_0.40_0.60": round(sum(1 for v in vals if 0.40 <= v <= 0.60) / len(vals), 3) if vals else None,
            "frac_ge_0.85": round(sum(1 for v in vals if v >= 0.85) / len(vals), 3) if vals else None,
        }

    args.outdir.mkdir(parents=True, exist_ok=True)
    path = args.outdir / "germline_confound.residual.json"
    path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
