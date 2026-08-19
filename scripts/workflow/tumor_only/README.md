# workflow/tumor_only — SNV-calling phase

Tumor-only somatic **SNV candidate calling** from a long-read (ONT) tumor BAM.
Strictly tumor-only: **no matched normal** is used. ClairS-TO output is treated as
**candidate** somatic variants, not confirmed truth.

## Steps

1. **`run_clairs_to.sh`** — run ClairS-TO on the tumor BAM → `snv.vcf.gz`.
   Germline is removed by population panels-of-normals (gnomAD / dbSNP / 1000g / CoLoRSdb),
   since there is no matched normal. SNV-only (`--disable_indel_calling`).

   ```bash
   workflow/tumor_only/run_clairs_to.sh \
     --tumor  /path/HCC1395_tumor.bam \
     --ref    /path/GRCh38_no_alt_analysis_set.fasta \
     --outdir results/tumor_only/HCC1395 \
     --platform ont_r10_dorado_sup_5khz_ssrs --threads 32
   ```
   External deps (ClairS-TO install, models, PoN DBs, pypy/longphase/whatshap) are set via
   env vars at the top of the script — override them for your environment.

2. **`build_candidates.py`** — extract PASS SNVs + Phase 1 QC characterization (uses `src/candidates`).

   ```bash
   python workflow/tumor_only/build_candidates.py \
     --vcf     results/tumor_only/HCC1395/snv.vcf.gz \
     --outdir  results/tumor_only/HCC1395 \
     --figures-dir figures/tumor_only \
     --weekly-report reports/weekly/2026-08-13_hcc1395_phase1_tumor_only.md \
     --change-log reports/change_log.tsv
   ```

## Outputs (into `results/tumor_only/<sample>/` and `figures/tumor_only/`)
- `candidate_pass_snvs.tsv` — chrom, pos, ref, alt, filter, qual, depth, ref_count, alt_count, vaf
- `candidate_analysis.tsv` — candidate-level Phase 1 analysis table with derived ALT-support/depth bins
- `variant_summary.tsv` — total / PASS / PASS-SNV / PASS-indel / candidate counts plus median depth/VAF/ALT support
- `qc_stats.txt` — depth, VAF, ALT-support, correlation summaries, per-chromosome counts
- `vaf_distribution.png`, `depth_distribution.png`, `alt_support_distribution.png`
- `vaf_vs_depth.png`, `alt_support_vs_depth.png`, `variants_per_chromosome.png`
- optional weekly report + change-log append when CLI paths are supplied

## Library used
`src/candidates/` — `extract.py` (VCF → candidate table, count summary),
`qc.py` (stats + plots). Reusable, side-effect-free; import as `from src.candidates import ...`.

## Field derivation (ClairS-TO FORMAT `GT:GQ:DP:AF:AD:AU:CU:GU:TU`)
- `depth` = `FORMAT/DP` · `ref_count`/`alt_count` = `FORMAT/AD[0]`/`AD[1]` · `vaf` = `FORMAT/AF` · `qual` = VCF `QUAL`.

## Notes
- Indels disabled in this run → `PASS indels = 0` by configuration, not by absence.
- `snv_min_af = 0.05` floors VAF → candidate set biased toward clonal loci.
- This phase is descriptive only: no somatic, germline, or artifact labels are assigned.
- Next phase: build candidate reliability features for tumor-only marker qualification.
