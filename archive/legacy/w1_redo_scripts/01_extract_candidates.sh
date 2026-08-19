#!/usr/bin/env bash
# Extract tumor-only PASS SNV candidate set from the existing ClairS-TO VCF.
# Reuses the week4 Exp-A run (pure HCC1395 tumor, strictly tumor-only, no matched normal).
# Does NOT modify the original BAM/VCF. SNV-only (ClairS-TO run used --disable_indel_calling).
set -euo pipefail

ROOT=/big8_disk/hung114/ONT_MRD
VCF="$ROOT/week4/expA_full/HCC1395_pure/snv.vcf.gz"   # original ClairS-TO output (read-only)
OUT="$ROOT/w1_redo/weekly_report_clairsto"

# --- candidate table: PASS SNVs only ---
# Fields from ClairS-TO FORMAT (GT:GQ:DP:AF:AD:AU:CU:GU:TU):
#   depth      = FORMAT/DP  (read depth in tumor BAM)
#   ref_count  = FORMAT/AD[0], alt_count = FORMAT/AD[1]  (ref/alt allelic depths)
#   vaf        = FORMAT/AF   (ClairS-TO estimated allele frequency in tumor BAM)
#   qual       = VCF QUAL column (ClairS-TO model confidence)
echo -e "chrom\tpos\tref\talt\tfilter\tqual\tdepth\tref_count\talt_count\tvaf" > "$OUT/candidate_pass_snvs.tsv"
bcftools view -f PASS -v snps "$VCF" 2>/dev/null \
  | bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%FILTER\t%QUAL\t[%DP]\t[%AD{0}]\t[%AD{1}]\t[%AF]\n' \
  >> "$OUT/candidate_pass_snvs.tsv"

N_CAND=$(( $(wc -l < "$OUT/candidate_pass_snvs.tsv") - 1 ))

# --- summary counts ---
TOTAL=$(zcat "$VCF" | grep -vc '^#')
PASS=$(zcat "$VCF" | awk -F'\t' '$7=="PASS"' | wc -l)
PASS_SNV=$(zcat "$VCF" | awk -F'\t' '$7=="PASS" && length($4)==1 && length($5)==1' | wc -l)
PASS_INDEL=$(zcat "$VCF" | awk -F'\t' '$7=="PASS" && (length($4)>1 || length($5)>1)' | wc -l)

{
  echo -e "Metric\tValue"
  echo -e "Total ClairS-TO calls\t$TOTAL"
  echo -e "PASS calls\t$PASS"
  echo -e "PASS SNVs\t$PASS_SNV"
  echo -e "PASS indels (indel calling disabled in run)\t$PASS_INDEL"
  echo -e "Preliminary candidate SNVs\t$N_CAND"
} > "$OUT/variant_summary.tsv"

echo "wrote candidate_pass_snvs.tsv ($N_CAND rows) and variant_summary.tsv"
cat "$OUT/variant_summary.tsv"
