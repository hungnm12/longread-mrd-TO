#!/usr/bin/env python3
"""MRDetect-style detection scoring + LoD from an exact-ALT-per-site table.

Input: TSV from pon_exact_alt.py with columns
  chrom pos ref alt <S>_alt <S>_dp ... support_samples pon_recurrent
where one of the samples is the 0% control (--control).

Method (Zviran 2020 flavor, ref week2/key.md):
  1. Denoise: drop compendium sites whose control ALT-fraction exceeds --noise-cutoff
     (germline leakage / systematic ONT error) — these are not clean somatic markers.
  2. Per sample, integrate exact-ALT genome-wide over clean sites:
       TAR = sum(alt) / sum(dp)                      (tumor allele rate)
       excess_reads = sum_i max(0, alt_i - e_pool*dp_i)   (background-subtracted)
     with e_pool = pooled control error = sum(control_alt)/sum(control_dp).
  3. Null from the control by bootstrapping sites -> distribution of control TAR;
     Z = (TAR_sample - null_mean)/null_sd ; empirical p = P(null >= TAR_sample).
     detected := Z >= --z-threshold.
  4. Titration: TAR vs TF, step ratios, LoD = lowest TF detected.
"""
import argparse
import sys
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", required=True)
    ap.add_argument("--samples", nargs="+", required=True,
                    help="sample labels in TF order high->low, e.g. TF1e2 TF1e3 TF1e4")
    ap.add_argument("--tf", nargs="+", type=float, required=True,
                    help="tumor fraction for each --samples entry, e.g. 1e-2 1e-3 1e-4")
    ap.add_argument("--control", required=True, help="0% control sample label, e.g. TF0")
    ap.add_argument("--noise-cutoff", type=float, default=0.02,
                    help="drop sites with control ALT-fraction above this (default 0.02)")
    ap.add_argument("--z-threshold", type=float, default=3.0)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", required=True, help="output summary TSV")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    # ---- load ----
    with open(args.tsv) as fh:
        header = fh.readline().rstrip("\n").split("\t")
    idx = {c: i for i, c in enumerate(header)}
    allcols = args.samples + [args.control]
    for s in allcols:
        if f"{s}_alt" not in idx or f"{s}_dp" not in idx:
            sys.exit(f"missing columns for sample {s}")
    data = np.loadtxt(args.tsv, delimiter="\t", skiprows=1,
                      usecols=[idx[f"{s}_{k}"] for s in allcols for k in ("alt", "dp")])
    ncol = len(allcols)
    alt = data[:, 0::2]  # sites x samples(alt)
    dp = data[:, 1::2]
    ctrl_j = ncol - 1

    total_sites = alt.shape[0]
    # ---- denoise using control ----
    with np.errstate(divide="ignore", invalid="ignore"):
        ctrl_vaf = np.where(dp[:, ctrl_j] > 0, alt[:, ctrl_j] / dp[:, ctrl_j], 0.0)
    covered = (dp > 0).all(axis=1)
    clean = covered & (ctrl_vaf <= args.noise_cutoff)
    n_clean = int(clean.sum())
    n_drop_noise = int((covered & ~(ctrl_vaf <= args.noise_cutoff)).sum())
    n_drop_cov = int((~covered).sum())

    alt_c = alt[clean]
    dp_c = dp[clean]
    e_pool = alt_c[:, ctrl_j].sum() / max(1.0, dp_c[:, ctrl_j].sum())

    # ---- bootstrap null from control ----
    rng = np.random.default_rng(args.seed)
    ctrl_alt = alt_c[:, ctrl_j]
    ctrl_dp = dp_c[:, ctrl_j]
    null_tar = np.empty(args.boot)
    n = n_clean
    for b in range(args.boot):
        take = rng.integers(0, n, n)
        d = ctrl_dp[take].sum()
        null_tar[b] = ctrl_alt[take].sum() / d if d > 0 else 0.0
    null_mean, null_sd = float(null_tar.mean()), float(null_tar.std(ddof=1))

    # ---- per-sample metrics ----
    rows = []
    for j, s in enumerate(allcols):
        a = alt_c[:, j].sum()
        d = dp_c[:, j].sum()
        tar = a / d if d > 0 else 0.0
        excess = np.maximum(0.0, alt_c[:, j] - e_pool * dp_c[:, j]).sum()
        z = (tar - null_mean) / null_sd if null_sd > 0 else float("inf")
        p = float((null_tar >= tar).mean())
        tf = 0.0 if s == args.control else args.tf[args.samples.index(s)]
        detected = (s != args.control) and (z >= args.z_threshold)
        rows.append(dict(sample=s, tf=tf, total_alt=int(a), total_dp=int(d),
                         TAR=tar, excess_reads=float(excess), Z=z, emp_p=p,
                         detected=detected))

    # ---- LoD ----
    det_tfs = [r["tf"] for r in rows if r["detected"]]
    lod = min(det_tfs) if det_tfs else None

    # ---- write ----
    cols = ["sample", "tf", "total_alt", "total_dp", "TAR", "excess_reads", "Z", "emp_p", "detected"]
    with open(args.out, "w") as out:
        out.write("\t".join(cols) + "\n")
        for r in rows:
            out.write("\t".join(str(r[c]) for c in cols) + "\n")

    # ---- stderr report ----
    e = sys.stderr.write
    e(f"[mrd_score] sites total={total_sites} clean={n_clean} "
      f"drop_noise={n_drop_noise} drop_uncovered={n_drop_cov} "
      f"(noise_cutoff={args.noise_cutoff})\n")
    e(f"[mrd_score] pooled control error e_pool={e_pool:.3e} ; "
      f"null TAR mean={null_mean:.3e} sd={null_sd:.3e}\n")
    e(f"{'sample':8} {'TF':>7} {'TAR':>11} {'excess':>10} {'Z':>10} {'emp_p':>7} detected\n")
    for r in rows:
        e(f"{r['sample']:8} {r['tf']:>7.0e} {r['TAR']:>11.3e} "
          f"{r['excess_reads']:>10.0f} {r['Z']:>10.1f} {r['emp_p']:>7.3f} {r['detected']}\n")
    # titration step ratios (consecutive TAR - background)
    e("[mrd_score] background-subtracted TAR by TF (linearity check):\n")
    for r in rows:
        if r["sample"] != args.control:
            e(f"    TF={r['tf']:.0e}: TAR-bg={max(0.0, r['TAR']-null_mean):.3e}\n")
    e(f"[mrd_score] LoD (lowest detected TF, Z>={args.z_threshold}): "
      f"{lod if lod is not None else 'none detected'}\n")


if __name__ == "__main__":
    main()
