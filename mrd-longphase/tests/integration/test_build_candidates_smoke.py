#!/usr/bin/env python3
"""Smoke test for the Phase 1 tumor-only candidate builder."""
import os
import subprocess
import sys
import tempfile


VCF_TEMPLATE = """##fileformat=VCFv4.2
##FILTER=<ID=PASS,Description="All filters passed">
##FILTER=<ID=LowQual,Description="Low quality">
##contig=<ID=chr1>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype quality">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Depth">
##FORMAT=<ID=AF,Number=A,Type=Float,Description="Allele fraction">
##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tHCC1395
chr1\t100\t.\tA\tG\t12.5\tPASS\t.\tGT:GQ:DP:AF:AD\t0/1:20:40:0.25:30,10
chr1\t101\t.\tC\tT\t7.0\tPASS\t.\tGT:GQ:DP:AF:AD\t0/1:18:50:0.60:20,30
chr1\t102\t.\tG\tGA\t3.0\tPASS\t.\tGT:GQ:DP:AF:AD\t0/1:12:20:0.10:18,2
chr1\t103\t.\tT\tC\t2.0\tLowQual\t.\tGT:GQ:DP:AF:AD\t0/1:10:10:0.10:9,1
"""


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    script = os.path.join(repo_root, "workflow", "tumor_only", "build_candidates.py")
    with tempfile.TemporaryDirectory(prefix="mrd_longphase_smoke_") as tmpdir:
        vcf_path = os.path.join(tmpdir, "smoke.vcf")
        outdir = os.path.join(tmpdir, "results")
        figdir = os.path.join(tmpdir, "figures")
        report = os.path.join(tmpdir, "weekly.md")
        changelog = os.path.join(tmpdir, "change_log.tsv")
        with open(vcf_path, "w") as f:
            f.write(VCF_TEMPLATE)

        env = dict(os.environ)
        env.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")
        cmd = [
            sys.executable,
            script,
            "--vcf", vcf_path,
            "--outdir", outdir,
            "--figures-dir", figdir,
            "--sample-name", "SMOKE_SAMPLE",
            "--weekly-report", report,
            "--change-log", changelog,
        ]
        subprocess.run(cmd, check=True, cwd=repo_root, env=env)

        expected = [
            os.path.join(outdir, "candidate_pass_snvs.tsv"),
            os.path.join(outdir, "candidate_analysis.tsv"),
            os.path.join(outdir, "variant_summary.tsv"),
            os.path.join(outdir, "qc_stats.txt"),
            os.path.join(figdir, "vaf_distribution.png"),
            os.path.join(figdir, "depth_distribution.png"),
            os.path.join(figdir, "alt_support_distribution.png"),
            os.path.join(figdir, "vaf_vs_depth.png"),
            os.path.join(figdir, "alt_support_vs_depth.png"),
            os.path.join(figdir, "variants_per_chromosome.png"),
            report,
            changelog,
        ]
        missing = [path for path in expected if not os.path.exists(path)]
        if missing:
            raise SystemExit(f"Missing smoke-test outputs: {missing}")

        with open(os.path.join(outdir, "candidate_pass_snvs.tsv")) as f:
            rows = [line.rstrip("\n") for line in f]
        if len(rows) != 3:
            raise SystemExit(f"Expected header + 2 PASS SNVs, observed {len(rows)} lines")

        with open(os.path.join(outdir, "variant_summary.tsv")) as f:
            summary = f.read()
        if "PASS SNVs\t2" not in summary:
            raise SystemExit("Summary file did not report 2 PASS SNVs")

        print("smoke test passed")


if __name__ == "__main__":
    main()
