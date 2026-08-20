#!/usr/bin/env python3
"""EXP-G1-002 — is the ALT-ALT excess in the non-somatic stratum germline haplotype structure?

EXP-G1-001 found same-molecule ALT-ALT co-occurrence *less* often among SEQC2-confirmed somatic
pairs than among pairs where neither candidate is confirmed. FIND-0001 read that as germline
variants in cis. This tests the reading rather than repeating it:

  Arm A  the same 1,000 pairs, classified on the matched normal BAM (evaluation only).
         Germline alleles are on normal molecules; somatic ones are not.
  Arm B  each candidate looked up in four population / panel-of-normals databases.
  Arm C  the EXP-G1-001 tumor rates recomputed on pairs that neither arm marks germline.

The tumor counts are never recomputed — they are joined from EXP-G1-001's table, so nothing
about the original measurement can shift under a re-run.

    python3 scripts/workflow/linkage/test_germline_confound.py \\
        --config research/experiments/registry/EXP-G1-002.yaml \\
        --outdir outputs/active/results/linkage
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pysam  # noqa: E402
import yaml  # noqa: E402

# Reuse EXP-G1-001's own functions verbatim rather than reimplementing them, so the read
# classification cannot silently drift between the two experiments. Loaded by path because
# scripts/ is a directory of entry points, not a package.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "measure_cooccurrence", Path(__file__).with_name("measure_cooccurrence.py"))
_g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_g1)
build_pairs, classify_pair = _g1.build_pairs, _g1.classify_pair
load_candidates, load_seqc2 = _g1.load_candidates, _g1.load_seqc2

POPDB_KEYS = ["gnomad", "dbsnp", "1000g_pon", "colorsdb"]


def popdb_hit(tabix, chrom: str, pos: int, ref: str, alt: str) -> str | None:
    """'exact' if the database records this ref>alt, 'position' if it records the site only."""
    try:
        rows = list(tabix.fetch(chrom, pos - 1, pos))
    except ValueError:  # contig absent from this database
        return None
    seen_site = False
    for row in rows:
        f = row.split("\t")
        if int(f[1]) != pos:
            continue
        seen_site = True
        if f[3].upper() == ref.upper() and alt.upper() in f[4].upper().split(","):
            return "exact"
    return "position" if seen_site else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--tumor-table", type=Path,
                        default=Path("outputs/active/results/linkage/cooccurrence_pure_tumor.tsv"))
    parser.add_argument("--skip-arm-a", action="store_true", help="annotation only, no BAM pass")
    args = parser.parse_args()

    spec = yaml.safe_load(args.config.read_text())
    params = spec["parameters"]
    paths = {item["role"].split(",")[0].strip().lower(): item["path"] for item in spec["inputs"]}
    by_role = [item["path"] for item in spec["inputs"]]
    candidates_path = Path(REPO_ROOT) / by_role[0]
    normal_bam = Path(by_role[2])
    popdb_paths = dict(zip(POPDB_KEYS, by_role[3:7]))
    truth_path = Path(by_role[7])

    # --- the identical pair sample -------------------------------------------------------
    by_chrom = load_candidates(candidates_path)
    pairs = build_pairs(by_chrom, params["pair_window_bp"])
    rng = random.Random(params["seed"])
    sampled = rng.sample(pairs, min(params["sample_pairs"], len(pairs)))
    sampled.sort()
    print(f"{sum(len(v) for v in by_chrom.values()):,} candidates -> {len(pairs):,} pairs; "
          f"{len(sampled):,} sampled at seed {params['seed']}")

    tumor_rows = list(csv.DictReader(args.tumor_table.open(), delimiter="\t"))
    for row in tumor_rows:
        for key in ("pos_a", "pos_b", "distance", "covers_both", "alt_alt", "alt_ref",
                    "ref_alt", "ref_ref", "other", "covers_one_only", "unreadable"):
            row[key] = int(row[key])

    # Provenance guard: the regenerated sample must be the EXP-G1-001 sample, pair for pair.
    regenerated = [(c, a[0], b[0]) for c, a, b in sampled]
    recorded = [(r["chrom"], r["pos_a"], r["pos_b"]) for r in tumor_rows]
    if regenerated != recorded:
        sys.exit(f"pair set does not reproduce EXP-G1-001: {len(regenerated)} vs {len(recorded)}, "
                 f"first mismatch at {next(i for i, (x, y) in enumerate(zip(regenerated, recorded)) if x != y)}")
    print("pair set reproduces EXP-G1-001 exactly (1000/1000)")

    # --- Arm A: the matched normal -------------------------------------------------------
    normal_by_pair: dict[tuple, Counter] = {}
    if not args.skip_arm_a:
        print(f"\nARM A  {normal_bam}")
        bam = pysam.AlignmentFile(str(normal_bam), "rb")
        for index, (chrom, first, second) in enumerate(sampled, start=1):
            normal_by_pair[(chrom, first[0], second[0])] = classify_pair(
                bam, chrom, first, second, params)
            if index % 100 == 0:
                print(f"  {index}/{len(sampled)} pairs")
        bam.close()

    # --- Arm B: population databases -----------------------------------------------------
    print("\nARM B  population / panel-of-normals lookup")
    candidates_in_pairs: dict[tuple, tuple[str, str]] = {}
    for chrom, first, second in sampled:
        candidates_in_pairs[(chrom, first[0])] = (first[1], first[2])
        candidates_in_pairs[(chrom, second[0])] = (second[1], second[2])
    print(f"  {len(candidates_in_pairs):,} distinct candidate positions")

    popdb: dict[tuple, dict[str, str | None]] = {k: {} for k in POPDB_KEYS}
    for name, path in popdb_paths.items():
        tabix = pysam.TabixFile(path)
        hits = Counter()
        for (chrom, pos), (ref, alt) in candidates_in_pairs.items():
            hit = popdb_hit(tabix, chrom, pos, ref, alt)
            popdb[name][(chrom, pos)] = hit
            hits[hit] += 1
        tabix.close()
        print(f"  {name:10s} exact {hits['exact']:5d}  position-only {hits['position']:5d}  absent {hits[None]:5d}")

    # --- truth, read last, report only ---------------------------------------------------
    seqc2 = load_seqc2(truth_path)

    def germline_supported(chrom, pos) -> bool:
        """Either arm says this candidate is not somatic-specific."""
        if any(popdb[name].get((chrom, pos)) == "exact" for name in POPDB_KEYS):
            return True
        return False

    out_rows = []
    for row in tumor_rows:
        key = (row["chrom"], row["pos_a"], row["pos_b"])
        n = normal_by_pair.get(key, Counter())
        rec = dict(row)
        rec.update({
            "n_covers_both": n.get("covers_both", 0),
            "n_alt_alt": n.get("alt_alt", 0),
            "n_alt_ref": n.get("alt_ref", 0),
            "n_ref_alt": n.get("ref_alt", 0),
            "n_ref_ref": n.get("ref_ref", 0),
        })
        for which, pos in (("a", row["pos_a"]), ("b", row["pos_b"])):
            for name in POPDB_KEYS:
                rec[f"{name}_{which}"] = popdb[name].get((row["chrom"], pos)) or "-"
            rec[f"popdb_{which}"] = "exact" if germline_supported(row["chrom"], pos) else "-"
            rec[f"seqc2_{which}"] = "yes" if (row["chrom"], pos) in seqc2 else "no"
        rec["popdb_germline_pair"] = (rec["popdb_a"] == "exact") or (rec["popdb_b"] == "exact")
        rec["normal_germline_pair"] = rec["n_alt_alt"] >= params["normal_germline_min_alt_alt_reads"]
        rec["germline_supported"] = rec["popdb_germline_pair"] or rec["normal_germline_pair"]
        out_rows.append(rec)

    # --- summarise -----------------------------------------------------------------------
    evaluable = [r for r in out_rows if r["covers_both"] > 0]
    strata = ("both", "one", "neither")

    def arm_a(stratum: str) -> dict:
        """Of tumor ALT-ALT pairs in this stratum, how many are ALT-ALT in the normal too?"""
        subset = [r for r in evaluable if r["seqc2_stratum"] == stratum and r["alt_alt"] > 0]
        in_normal = [r for r in subset if r["n_covers_both"] > 0]
        hit = [r for r in in_normal if r["normal_germline_pair"]]
        return {
            "tumor_alt_alt_pairs": len(subset),
            "evaluable_in_normal": len(in_normal),
            "alt_alt_in_normal": len(hit),
            "pct": round(100 * len(hit) / len(in_normal), 2) if in_normal else None,
        }

    def arm_b(stratum: str) -> dict:
        """Population-database membership of the candidates in this stratum."""
        cands = set()
        for r in evaluable:
            if r["seqc2_stratum"] != stratum:
                continue
            for which, pos in (("a", r["pos_a"]), ("b", r["pos_b"])):
                cands.add((r["chrom"], pos, r[f"popdb_{which}"], r[f"seqc2_{which}"]))
        total = len(cands)
        hit = sum(1 for c in cands if c[2] == "exact")
        return {"candidates": total, "in_popdb_exact": hit,
                "pct": round(100 * hit / total, 2) if total else None}

    def by_seqc2_membership() -> dict:
        """Population-DB membership split by whether the candidate itself is confirmed somatic."""
        cands: dict[tuple, tuple[str, str]] = {}
        for r in evaluable:
            for which, pos in (("a", r["pos_a"]), ("b", r["pos_b"])):
                cands[(r["chrom"], pos)] = (r[f"popdb_{which}"], r[f"seqc2_{which}"])
        out = {}
        for label in ("yes", "no"):
            subset = [v for v in cands.values() if v[1] == label]
            hit = sum(1 for v in subset if v[0] == "exact")
            out["seqc2_" + label] = {"candidates": len(subset), "in_popdb_exact": hit,
                                     "pct": round(100 * hit / len(subset), 2) if subset else None}
        return out

    def arm_c(rows) -> dict:
        out = {}
        for stratum in strata:
            subset = [r for r in rows if r["seqc2_stratum"] == stratum]
            hit = [r for r in subset if r["alt_alt"] > 0]
            out[stratum] = {"pairs_evaluable": len(subset), "pairs_with_alt_alt": len(hit),
                            "pct": round(100 * len(hit) / len(subset), 2) if subset else None}
        return out

    residual = [r for r in evaluable if not r["germline_supported"]]
    popdb_membership = by_seqc2_membership()
    enrich = None
    if popdb_membership["seqc2_yes"]["pct"]:
        enrich = round(popdb_membership["seqc2_no"]["pct"] / popdb_membership["seqc2_yes"]["pct"], 2)

    summary = {
        "experiment": spec["id"],
        "normal_bam": str(normal_bam),
        "parameters": params,
        "thresholds": spec["thresholds"],
        "pairs_evaluable_in_tumor": len(evaluable),
        "arm_a_normal": {s: arm_a(s) for s in strata},
        "arm_b_popdb_by_stratum": {s: arm_b(s) for s in strata},
        "arm_b_popdb_by_candidate_seqc2": popdb_membership,
        "arm_b_enrichment_ratio_nonsomatic_over_somatic": enrich,
        "germline_supported_pairs": sum(1 for r in evaluable if r["germline_supported"]),
        "germline_by_popdb_only": sum(1 for r in evaluable
                                      if r["popdb_germline_pair"] and not r["normal_germline_pair"]),
        "germline_by_normal_only": sum(1 for r in evaluable
                                       if r["normal_germline_pair"] and not r["popdb_germline_pair"]),
        "germline_by_both": sum(1 for r in evaluable
                                if r["normal_germline_pair"] and r["popdb_germline_pair"]),
        "arm_c_all_pairs": arm_c(evaluable),
        "arm_c_residual_pairs": arm_c(residual),
        "residual_pairs": len(residual),
    }

    args.outdir.mkdir(parents=True, exist_ok=True)
    tsv = args.outdir / "germline_confound_pure_tumor.tsv"
    with tsv.open("w") as handle:
        handle.write("\t".join(out_rows[0].keys()) + "\n")
        for row in out_rows:
            handle.write("\t".join(str(v) for v in row.values()) + "\n")
    (args.outdir / "germline_confound.summary.json").write_text(json.dumps(summary, indent=2))

    print("\n--- EXP-G1-002 summary ---")
    print("ARM A  of tumor ALT-ALT pairs, how many are ALT-ALT in the matched normal:")
    for s in strata:
        a = summary["arm_a_normal"][s]
        print(f"  {s:8s} {a['alt_alt_in_normal']:4d}/{a['evaluable_in_normal']:4d} = {a['pct']}%")
    print("ARM B  population-DB membership per candidate:")
    for label in ("seqc2_yes", "seqc2_no"):
        b = popdb_membership[label]
        print(f"  {label:10s} {b['in_popdb_exact']:5d}/{b['candidates']:5d} = {b['pct']}%")
    print(f"  enrichment (non-somatic / somatic) = {enrich}x")
    print("ARM C  tumor ALT-ALT rate, all pairs then germline-free residual:")
    for s in strata:
        allp, res = summary["arm_c_all_pairs"][s], summary["arm_c_residual_pairs"][s]
        print(f"  {s:8s} all {allp['pct']}% (n={allp['pairs_evaluable']})   "
              f"residual {res['pct']}% (n={res['pairs_evaluable']})")
    print(f"\nwrote {tsv}")


if __name__ == "__main__":
    main()
