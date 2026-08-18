#!/usr/bin/env python3
"""
MRDetect prototype — simplified reproduction of the core idea from
Zviran et al., Nature Medicine 2020 ("Genome-wide cell-free DNA mutational
integration enables ultra-sensitive cancer monitoring").

CORE IDEA ("breadth over depth"):
  A single somatic SNV site carries almost no signal at ultra-low tumor
  fraction (TF) and is dominated by sequencing error. But if we INTEGRATE the
  alt-supporting evidence across THOUSANDS of tumor-specific SNV sites, the
  cumulative true-tumor signal separates from the error background.

WHAT THIS PROTOTYPE DOES:
  1. Load a patient-specific somatic SNV list (the "compendium") from a VCF.
  2. For a plasma-like BAM, count alt-supporting reads at every SNV site.
  3. Aggregate signal across all sites -> genome-wide alt rate at tumor sites.
  4. Build a noise model from a control (TF=0) sample and bootstrap a noise
     distribution -> robust Z-score -> detected / not detected.

WHAT IS SIMPLIFIED vs full MRDetect (report these as "obstacles/simplifications"):
  - No read-centric SVM error suppression (MRDetect's key denoiser). We use
    simple base-quality / mapping-quality filters instead.
  - SNV only; no copy-number aberration (CNA) integration.
  - Simple aggregate-rate + bootstrap Z-score instead of their full noise model.

USAGE:
  # See the core logic work immediately, no real data needed:
  python mrdetect_prototype.py --demo

  # Real run (once you have a somatic VCF + plasma BAM + control BAM):
  python mrdetect_prototype.py \
      --snv-vcf tumor_somatic.vcf.gz \
      --plasma-bam plasma_spiked.bam \
      --control-bam plasma_control.bam \
      --chroms chr20 chr22
"""

import argparse
import numpy as np

# pysam is only needed for real BAM/VCF work, not for --demo.
try:
    import pysam
except ImportError:
    pysam = None


# --------------------------------------------------------------------------
# 1. Load the somatic SNV compendium (tumor-specific point mutations)
# --------------------------------------------------------------------------
def load_snvs(vcf_path, chroms=None):
    """Return list of (chrom, pos0, ref, alt). pos0 is 0-based."""
    if pysam is None:
        raise RuntimeError("pysam not installed; needed for real VCF input.")
    snvs = []
    vf = pysam.VariantFile(vcf_path)
    for rec in vf:
        if rec.alts is None or len(rec.alts) != 1:
            continue
        ref, alt = rec.ref, rec.alts[0]
        if len(ref) == 1 and len(alt) == 1:  # SNVs only
            if chroms and rec.chrom not in chroms:
                continue
            snvs.append((rec.chrom, rec.pos - 1, ref.upper(), alt.upper()))
    return snvs


# --------------------------------------------------------------------------
# 2. Count alt-supporting reads and depth at one site
# --------------------------------------------------------------------------
def count_site(bam, chrom, pos0, alt, min_bq=20, min_mapq=20):
    """Return (alt_count, depth) at a single position."""
    alt_count, depth = 0, 0
    for col in bam.pileup(chrom, pos0, pos0 + 1, truncate=True,
                          min_base_quality=0, stepper="samtools"):
        if col.reference_pos != pos0:
            continue
        for pr in col.pileups:
            if pr.is_del or pr.is_refskip or pr.query_position is None:
                continue
            aln = pr.alignment
            if aln.mapping_quality < min_mapq:
                continue
            bq = aln.query_qualities[pr.query_position]
            if bq < min_bq:
                continue
            base = aln.query_sequence[pr.query_position].upper()
            depth += 1
            if base == alt:
                alt_count += 1
    return alt_count, depth


# --------------------------------------------------------------------------
# 3. Score a sample: per-site (alt, depth) across the whole compendium
# --------------------------------------------------------------------------
def score_sample(bam_path, snvs, min_bq=20, min_mapq=20):
    """Return arrays (alt_counts, depths) over all SNV sites."""
    if pysam is None:
        raise RuntimeError("pysam not installed; needed for real BAM input.")
    bam = pysam.AlignmentFile(bam_path, "rb")
    alts = np.zeros(len(snvs), dtype=np.int64)
    deps = np.zeros(len(snvs), dtype=np.int64)
    for i, (chrom, pos0, ref, alt) in enumerate(snvs):
        a, d = count_site(bam, chrom, pos0, alt, min_bq, min_mapq)
        alts[i], deps[i] = a, d
    bam.close()
    return alts, deps


# --------------------------------------------------------------------------
# 4. Integrate signal + noise model -> robust detection Z-score
# --------------------------------------------------------------------------
def aggregate_rate(alt_counts, depths):
    """Genome-wide alt rate at tumor sites = sum(alt) / sum(depth)."""
    total_depth = depths.sum()
    return (alt_counts.sum() / total_depth) if total_depth > 0 else 0.0


def bootstrap_noise(alt_counts, depths, n_boot=1000, seed=0):
    """Bootstrap the aggregate rate over SITES to get a noise distribution."""
    rng = np.random.default_rng(seed)
    n = len(alt_counts)
    rates = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)          # resample sites w/ replacement
        d = depths[idx].sum()
        rates[b] = (alt_counts[idx].sum() / d) if d > 0 else 0.0
    return rates


def detection_zscore(signal_alt, signal_dep, control_alt, control_dep,
                     n_boot=1000, seed=0):
    """Robust Z-score of the plasma signal vs the control noise distribution."""
    signal_rate = aggregate_rate(signal_alt, signal_dep)
    noise = bootstrap_noise(control_alt, control_dep, n_boot, seed)
    mu, sd = noise.mean(), noise.std()
    z = (signal_rate - mu) / sd if sd > 0 else float("inf")
    return {
        "signal_rate": signal_rate,
        "noise_mean": mu,
        "noise_std": sd,
        "zscore": z,
        "estimated_TF": max(signal_rate - mu, 0.0),  # crude TF estimate
    }


# --------------------------------------------------------------------------
# DEMO: synthetic data so you can see the core idea work with no real files
# --------------------------------------------------------------------------
def make_synthetic(n_sites, tf, mean_depth=30, error_rate=1e-3, seed=0):
    """Simulate per-site (alt, depth) for a plasma sample.
    True tumor SNV appears in plasma at VAF ~= TF; every read also has a
    baseline error chance. Control uses tf=0 (error only)."""
    rng = np.random.default_rng(seed)
    depths = rng.poisson(mean_depth, size=n_sites).clip(min=1)
    p_alt = tf + error_rate            # prob a read shows the alt allele
    alts = rng.binomial(depths, p_alt)
    return alts, depths


def run_demo():
    print("=" * 64)
    print("MRDetect prototype — synthetic demo")
    print("Shows how integrating across many sites beats the error floor.")
    print("=" * 64)
    n_sites, mean_depth, error = 5000, 30, 1e-3
    # control = pure error (TF = 0)
    c_alt, c_dep = make_synthetic(n_sites, tf=0.0, mean_depth=mean_depth,
                                  error_rate=error, seed=1)
    print(f"\nSites: {n_sites} | mean depth: {mean_depth}x | "
          f"error rate: {error} | total reads/sample ~ {c_dep.sum():,}")
    print(f"{'TF (spike)':>12} | {'signal rate':>11} | {'noise mean':>10} | "
          f"{'Z-score':>8} | detected?")
    print("-" * 64)
    for tf in [1e-2, 5e-3, 1e-3, 5e-4, 1e-4]:
        s_alt, s_dep = make_synthetic(n_sites, tf=tf, mean_depth=mean_depth,
                                      error_rate=error, seed=2)
        r = detection_zscore(s_alt, s_dep, c_alt, c_dep, n_boot=2000, seed=0)
        hit = "YES" if r["zscore"] >= 3 else "no"
        print(f"{tf:>12.5f} | {r['signal_rate']:>11.5f} | "
              f"{r['noise_mean']:>10.5f} | {r['zscore']:>8.2f} | {hit}")
    print("\nTakeaway: detection limit depends on (#sites x depth). More "
          "somatic\nSNVs and/or more depth push the detectable TF lower.\n"
          "This is exactly why MRDetect uses genome-wide breadth.\n")


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="MRDetect prototype")
    ap.add_argument("--demo", action="store_true",
                    help="Run synthetic demo (no real data needed).")
    ap.add_argument("--snv-vcf", help="Somatic SNV VCF (tumor-specific).")
    ap.add_argument("--plasma-bam", help="Plasma-like BAM (spiked/real).")
    ap.add_argument("--control-bam", help="Control plasma BAM (TF=0).")
    ap.add_argument("--chroms", nargs="*", default=None,
                    help="Restrict to these chromosomes (e.g. chr20 chr22).")
    ap.add_argument("--min-bq", type=int, default=20)
    ap.add_argument("--min-mapq", type=int, default=20)
    args = ap.parse_args()

    if args.demo:
        run_demo()
        return

    if not (args.snv_vcf and args.plasma_bam and args.control_bam):
        ap.error("Need --snv-vcf, --plasma-bam and --control-bam "
                 "(or use --demo).")

    print(f"Loading somatic SNVs from {args.snv_vcf} ...")
    snvs = load_snvs(args.snv_vcf, args.chroms)
    print(f"  {len(snvs):,} somatic SNV sites")

    print("Scoring plasma sample ...")
    p_alt, p_dep = score_sample(args.plasma_bam, snvs, args.min_bq, args.min_mapq)
    print("Scoring control sample ...")
    c_alt, c_dep = score_sample(args.control_bam, snvs, args.min_bq, args.min_mapq)

    r = detection_zscore(p_alt, p_dep, c_alt, c_dep)
    print("\n=== Result ===")
    for k, v in r.items():
        print(f"  {k:14s}: {v}")
    print(f"  detected      : {'YES' if r['zscore'] >= 3 else 'no'} "
          f"(Z >= 3 threshold)")


if __name__ == "__main__":
    main()