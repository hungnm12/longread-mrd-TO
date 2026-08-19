#!/usr/bin/env python3
"""SNV-calling phase: turn a ClairS-TO tumor-only VCF into the candidate SNV
deliverables — candidate table, summary counts, QC stats and plots.

Thin CLI wiring `src.candidates`. Run from anywhere; it adds the repo root to
sys.path so `from src.candidates import ...` works without installation.

Example:
  python workflow/tumor_only/build_candidates.py \
      --vcf results/tumor_only/HCC1395/snv.vcf.gz \
      --outdir results/tumor_only/HCC1395 \
      --figures-dir figures/tumor_only
"""
import argparse
from datetime import date
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.candidates import write_candidate_tsv, summarize_counts, qc  # noqa: E402


def _write_summary(counts, candidate_count, stats, out_path):
    pass_pct = (100.0 * counts["pass_snvs"] / counts["total_calls"]) if counts["total_calls"] else 0.0
    with open(out_path, "w") as f:
        f.write("Metric\tValue\n")
        f.write(f"Total ClairS-TO calls\t{counts['total_calls']}\n")
        f.write(f"PASS calls\t{counts['pass_calls']}\n")
        f.write(f"PASS SNVs\t{counts['pass_snvs']}\n")
        f.write(f"PASS indels (indel calling disabled in run)\t{counts['pass_indels']}\n")
        f.write(f"PASS SNV proportion (%)\t{pass_pct:.2f}\n")
        f.write(f"Preliminary candidate SNVs\t{candidate_count}\n")
        f.write(f"Median depth\t{stats['depth_median']}\n")
        f.write(f"Median VAF\t{stats['vaf_median']}\n")
        f.write(f"Median ALT support\t{stats['alt_count_median']}\n")


def _write_weekly_report(sample_name, counts, stats, report_path, source_vcf):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    pass_pct = (100.0 * counts["pass_snvs"] / counts["total_calls"]) if counts["total_calls"] else 0.0
    with open(report_path, "w") as f:
        f.write(f"# {sample_name} Phase 1 Tumor-Only Candidate Landscape ({date.today().isoformat()})\n\n")
        f.write("## Research question\n\n")
        f.write("What does the tumor-only PASS SNV candidate landscape look like before any somatic interpretation?\n\n")
        f.write("## Why it matters\n\n")
        f.write("This phase defines the retained analysis population for later reliability scoring and tumor-only marker qualification without requiring a matched normal.\n\n")
        f.write("## Experiment / analysis\n\n")
        f.write(f"- Input VCF: `{source_vcf}`\n")
        f.write("- Extraction target: PASS single-nucleotide variants only\n")
        f.write("- Quantified dimensions: candidate count, depth, VAF, ALT support, and depth relationships\n\n")
        f.write("## Observation\n\n")
        f.write(f"- The retained population contains {counts['pass_snvs']:,} PASS SNVs from {counts['total_calls']:,} total ClairS-TO records ({pass_pct:.2f}% of all records).\n")
        f.write(f"- Candidate depth is centered at median {stats['depth_median']}x with IQR {stats['depth_q25']}-{stats['depth_q75']}x.\n")
        f.write(f"- Candidate VAF is centered at median {stats['vaf_median']} with IQR {stats['vaf_q25']}-{stats['vaf_q75']}.\n")
        f.write(f"- ALT-support is centered at median {stats['alt_count_median']} reads with IQR {stats['alt_count_q25']}-{stats['alt_count_q75']} reads.\n")
        f.write(f"- The VAF-depth correlation is {stats['corr_vaf_depth']}, while ALT-support vs depth correlation is {stats['corr_alt_depth']}.\n\n")
        f.write("## Interpretation\n\n")
        f.write("- The candidate count defines the retained analysis population, not a confirmed somatic set.\n")
        f.write("- Depth and allele balance do not collapse into a single simple coverage effect because VAF-depth correlation is moderately negative while ALT-support follows depth more directly.\n")
        f.write("- Broad VAF and ALT-support distributions show heterogeneity in retained calls, but they do not establish biological origin.\n\n")
        f.write("## Limitations\n\n")
        f.write("- This phase is descriptive only and does not classify calls as somatic, germline, or artifact.\n")
        f.write("- Metrics rely on ClairS-TO VCF fields and inherit their caller-specific assumptions.\n")
        f.write("- No matched-normal evidence is used here by design.\n\n")
        f.write("## Decision\n\n")
        f.write("- Phase 1 is ready once downstream work uses these documented distributions as the baseline candidate landscape.\n")
        f.write("- Phase 2 should focus on feature extraction for reliability analysis rather than additional biological interpretation.\n\n")
        f.write("## Next research question\n\n")
        f.write("Which tumor-only candidate features are associated with potentially reliable or unreliable SNV calls?\n")


def _append_change_log(change_log_path, sample_name, args, counts, stats):
    os.makedirs(os.path.dirname(change_log_path), exist_ok=True)
    record = "\t".join([
        str(date.today()),
        "PHASE_1",
        sample_name,
        "workflow/tumor_only/build_candidates.py;src/candidates/extract.py;src/candidates/qc.py",
        f"--vcf {args.vcf} --outdir {args.outdir} --figures-dir {args.figures_dir or args.outdir}",
        "PASS SNVs only; hist_bins=default; percentiles=5/25/50/75/95",
        args.outdir,
        f"n={counts['pass_snvs']}; depth_median={stats['depth_median']}; vaf_median={stats['vaf_median']}; alt_median={stats['alt_count_median']}",
        "Descriptive phase only; no somatic truth labels.",
    ])
    existing = []
    if os.path.exists(change_log_path):
        with open(change_log_path) as f:
            existing = [line.rstrip("\n") for line in f]
    if record in existing:
        return
    with open(change_log_path, "a") as f:
        f.write(record + "\n")


def main():
    ap = argparse.ArgumentParser(description="Build tumor-only PASS SNV candidate set + QC")
    ap.add_argument("--vcf", required=True, help="ClairS-TO tumor-only VCF (snv.vcf.gz)")
    ap.add_argument("--outdir", required=True, help="output dir for tables/stats")
    ap.add_argument("--figures-dir", default=None, help="dir for QC plots (default: <outdir>)")
    ap.add_argument("--sample-name", default=None, help="sample identifier for docs/log outputs")
    ap.add_argument("--weekly-report", default=None, help="optional markdown report path")
    ap.add_argument("--change-log", default=None, help="optional TSV change log path")
    args = ap.parse_args()

    if not os.path.exists(args.vcf):
        raise FileNotFoundError(f"Missing input VCF: {args.vcf}")

    os.makedirs(args.outdir, exist_ok=True)
    figdir = args.figures_dir or args.outdir
    os.makedirs(figdir, exist_ok=True)
    sample_name = args.sample_name or os.path.basename(os.path.abspath(args.outdir))

    cand_tsv = os.path.join(args.outdir, "candidate_pass_snvs.tsv")
    n = write_candidate_tsv(args.vcf, cand_tsv)

    counts = summarize_counts(args.vcf)
    cols = qc.load_table(cand_tsv)
    stats = qc.compute_stats(cols)
    summ = os.path.join(args.outdir, "variant_summary.tsv")
    _write_summary(counts, n, stats, summ)
    qc.write_stats(stats, os.path.join(args.outdir, "qc_stats.txt"))
    qc.write_analysis_table(cols, os.path.join(args.outdir, "candidate_analysis.tsv"))
    qc.plot_vaf(cols, os.path.join(figdir, "vaf_distribution.png"))
    qc.plot_depth(cols, os.path.join(figdir, "depth_distribution.png"))
    qc.plot_alt_support(cols, os.path.join(figdir, "alt_support_distribution.png"))
    qc.plot_vaf_vs_depth(cols, os.path.join(figdir, "vaf_vs_depth.png"))
    qc.plot_alt_vs_depth(cols, os.path.join(figdir, "alt_support_vs_depth.png"))
    qc.plot_per_chrom(cols, os.path.join(figdir, "variants_per_chromosome.png"))

    if args.weekly_report:
        _write_weekly_report(sample_name, counts, stats, args.weekly_report, args.vcf)
    if args.change_log:
        _append_change_log(args.change_log, sample_name, args, counts, stats)

    print(f"[build_candidates] {n} PASS SNV candidates")
    print(f"  table   : {cand_tsv}")
    print(f"  analysis: {os.path.join(args.outdir, 'candidate_analysis.tsv')}")
    print(f"  summary : {summ}")
    print(f"  qc stats: {os.path.join(args.outdir, 'qc_stats.txt')}")
    print(f"  figures : {figdir}/ (vaf, depth, alt_support, vaf_vs_depth, alt_support_vs_depth, variants_per_chromosome)")
    if args.weekly_report:
        print(f"  weekly  : {args.weekly_report}")
    if args.change_log:
        print(f"  changelog: {args.change_log}")


if __name__ == "__main__":
    main()
