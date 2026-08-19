- mrd = molecular residual disease 
- cfDNA = cell-free DNA (total free DNA in blood)
- ctDNA = circulating tumor DNA (cfDNA but cancer)
- TF = Tumor Fraction
- VAF = Variant Allele Frequency (tần suất allele đột biến — tỉ lệ read mang allele đột biến tại một vị trí). Một đột biến somatic clonal xuất hiện trong plasma ở VAF ≈ TF.
- MRD = Minimal Residual Disease
- TP / FP / FN / TN = True Positive / False Positive / False Negative / True Negative

### Depth 

- tại một locus xem trên các dải read dựa theo độ sâu của sequencing 
--> VAF = number of reads with variant / total reads 

### Breadth 

- thay vì dùng độ sâu của sequencing --> dùng nhiều locus 

- WGS tumor + matched normal/germline được dùng để ra danh sách indel 

- tại mỗi locus sẽ chỉ có 0 hoặc 1 (giá trị tumor-like detection)

- Total observed  tumor-like reads /detections = observed singal
- sau khi có observed 


### Step 1: Whole genome Sequencing (WGS) + matched normal  --> danh sách SNV somatic calling

- CNA = Copy Number Alteration
thay đổi số bản sao của một đoạn genome trong tế bào ung thư.


#### Criteria to be cleared 

Truth set local tham chiếu GRCh38.d1.vd1.fa, còn BAM/reference hiện tại là GRCh38_no_alt_analysis_set.fasta

 R10.4.1, Dorado SUP, 5 kHz

 
  /big8_disk/hung114/ONT_MRD/week1/experiment/external/ClairS_latest/run_clairs \
    --tumor_bam_fn /big8_disk/Google_somatic_data/bams/HCC1395/HCC1395_Tumor_ONT.GRCh38.sorted.bam \
    --normal_bam_fn /big8_disk/Google_somatic_data/bams/HCC1395/HCC1395_Normal_ONT.GRCh38.sorted.bam \
    --ref_fn /big8_disk/ref/GRCh38_no_alt_analysis_set.fasta \
    --threads 8 \
    --platform ont_r10_dorado_sup_5khz_ssrs \
    --output_dir /big8_disk/hung114/ONT_MRD/week1/experiment/clairs_smoke_server3 \
    --pileup_model_path /big8_disk/hung114/ONT_MRD/week1/experiment/resources/clairs_models/ont_r10_dorado_sup_5khz_ssrs/pileup.pkl \
    --full_alignment_model_path /big8_disk/hung114/ONT_MRD/week1/experiment/resources/clairs_models/ont_r10_dorado_sup_5khz_ssrs/full_alignment.pkl \
    --region chr22 \
    --output_prefix out \
    --indel_pileup_model_path /big8_disk/hung114/ONT_MRD/week1/experiment/resources/clairs_models/ont_r10_dorado_sup_5khz_ssrs/indel/pileup.pkl \
    --indel_full_alignment_model_path /big8_disk/hung114/ONT_MRD/week1/experiment/resources/clairs_models/ont_r10_dorado_sup_5khz_ssrs/indel/
  full_alignment.pkl \
    --clair3_model_path /big8_disk/clair3_models/r1041_e82_400bps_sup_v420 \
    --whatshap /home/hung114/.local/bin/whatshap


 Tumor-only ONT HCC1395 BAM was analyzed with ClairS-TO v0.5.0 on GRCh38_no_alt_analysis_set, using platform/model ont_r10_dorado_sup_5khz_ssrs and truth
  sets high-confidence_sSNV_in_HC_regions_v1.2.vcf.gz, high-confidence_sINDEL_in_HC_regions_v1.2.vcf.gz, and High-Confidence_Regions_v1.2.bed.

---
**Goal:** Simulated purification at 0,001% can I detect the MRD 

Reproducing MRDetect 

Step 1:
ClairS-TO --> somatic SNV conpendium 

- detect and sort leakage, CHIP leakage vs germline leakage 

- real somatic site - setting sentivity floor 

- Recalibration is a knob, not a stable choice

- Keeping annotation per-SNV which will be needed for 0,001%

- Context error of each site 
