# Phase 0 — Validate pipeline (kết quả)

> Mục tiêu: chứng minh pipeline MRD **đáng tin** trước khi tin compendium/detection.
> A = validate caller (ClairS-TO tumor-only trên mẫu tinh khiết vs truth).
> B = validate detection (ladder 1%/0.1%/0.01% + control 0%, LoD).
> Cell line: **HCC1395** (5kHz ONT), truth **SEQC2 v1.2.1**.

---

## Setup

### S1. Tiêu chí "đạt" (định bằng số, khóa trước khi xem kết quả)
| Hạng mục | Ngưỡng đạt | Ghi chú |
|---|---|---|
| Caller precision (SNV, HC) | ≥ 0.90 | so trong HC regions |
| Caller recall (SNV, HC) | ≥ 0.80 | ONT high-cov pure tumor |
| Caller F1 (SNV, HC) | ≥ 0.85 | — |
| LoD (detection) | ≤ 1e-3 (0.1%) đạt tối thiểu | paper đạt 1e-5 ở coverage sâu hơn |
| Compendium size (HCC1395, HC) | ~1e4–4e4 SNV | HCC1395 hypermutated |
| Detected call | Z ≥ 3 vs control 0% | control phải "not detected" |

### S2. Validate truth-set & dữ liệu (đếm để chắc đúng file)
| Item | Đường dẫn | Số |
|---|---|---|
| Truth sSNV (HC) | `/big8_disk/data/HCC1395/SEQC2/high-confidence_sSNV_in_HC_regions_v1.2.1.vcf.gz` | 39,447 |
| Truth sINDEL (HC) | `.../high-confidence_sINDEL_in_HC_regions_v1.2.1.vcf.gz` | 1,625 |
| HC regions BED | `week3/resources/beds/HC_regions.bed.gz` | 709,209 interval / 2.485 Gbp |
| Pure tumor (truth sample) | `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam` | 272 GB, minimap2 map-ont 5kHz |
| Matched normal | `.../HCC1395BL.bam` | (Exp A tumor-only nên không dùng) |
| Ladder 1% / 0.1% / 0.01% | `/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-{2,3,4}_25x/*.rep1.bam` | 76 GB mỗi cái, 25x |
| Control 0% (bắt buộc) | `.../TF0_25x/TF0_25x.rep1.bam` | 77 GB, 25x |

### S3. Pin version (tái lập)
- ClairS-TO **v0.5.0** (`week1/experiment/external/ClairS_TO_latest`)
- ClairS-TO model: `r1041 ont_r10_dorado_sup_5khz_ssrs` (pkl); tumor-only, SNV-only (`--disable_indel_calling`)
- samtools **1.13**, bcftools **1.13**, pysam 0.24, numpy 2.2.6
- eval: `som.py` (hap.py somatic) — rtg/vcfeval không có trên máy
- Reference: `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`
- Harness tái dùng từ week3: `week3/run_clairs_to.sh`, `week3/tagging/pon_exact_alt.py`; scoring `week4/expB/mrd_score.py`

---

## Thí nghiệm A — validate caller  ✅ đã chạy

**A1.** ClairS-TO tumor-only full-genome trên pure tumor (~64m57s, 3,169,996 record; PASS SNV 48,819).
Coverage pure tumor ~**100x** (mẫu chr1 100kb). Model `ont_r10_dorado_sup_5khz_ssrs`, SNV-only.

**A2. Precision / Recall / F1** (query = PASS SNV, so SEQC2 sSNV trong HC regions).
`som.py` không build được trên máy → dùng `bcftools isec` (exact-match chrom+pos+ref+alt sau `norm`,
tương đương cho SNV). Đã kiểm: chỉ 5/11,975 FP nằm trong SEQC2 superset ⇒ FP là thật, không phải
do truth bảo thủ.

| Chỉ số | Giá trị | Ngưỡng S1 | Đạt? |
|---|---|---|---|
| Precision (SNV, HC) | **0.707** | ≥0.90 | ❌ |
| Recall (SNV, HC, PASS) | **0.732** | ≥0.80 | ❌ |
| F1 (SNV, HC) | **0.719** | ≥0.85 | ❌ |
| TP / FP / FN | 28,884 / 11,975 / 10,563 | — | — |

- Recall nếu tính **mọi FILTER** (không chỉ PASS) = **0.772** → filter chỉ làm mất 1,556 TP; nghĩa là
  **22.8% truth không được gọi ra kể cả dạng candidate** (giới hạn độ nhạy thật của caller, không phải filter).
- **Best-F1 (quét ngưỡng QUAL) = 0.720 tại QUAL≥2.40** — gần y hệt điểm PASS ⇒ **F1 thấp không phải do
  chọn ngưỡng**; đây là giới hạn thực của caller trên mẫu này.

**A3. So published ClairS-TO.** README/docs chỉ có demo chr17 100kb (P/R/F1=0.9655, 30 biến thể — không
đại diện genome-wide). Genome-wide họ báo "best achievable F1" từ PR-curve ở 25/50/75x cho ONT HCC1395
(kỳ vọng ~0.8–0.9 ở coverage cao). Kết quả của ta (**F1=0.72 ở ~100x**) **thấp hơn rõ** so kỳ vọng published.

**⚠️ Kết luận A: KHÔNG đạt tiêu chí.** Nghi ngờ chính (cần điều tra Phase tiếp):
1. **Model mismatch**: BAM là basecall methylation-aware `5khz_simplex_5mCG_5hmCG`, còn model ClairS-TO
   `ssrs` train trên sup chuẩn → có thể lệch đặc trưng pileup.
2. Có thể mẫu pure tumor này khác batch mà ClairS-TO benchmark.
3. Giới hạn thật của tumor-only ONT (FP cao khi thiếu matched normal).

---

## Thí nghiệm B — validate detection

**Phương pháp (MRDetect-style, ref week2/key.md):** score exact-ALT tại từng site compendium trên
{TF1e-2, TF1e-3, TF1e-4, TF0-control}; **denoise** loại site có control-VAF > 2% (germline leakage /
lỗi ONT hệ thống); tích hợp toàn genome → TAR = ΣALT/ΣDP; **bootstrap** control 2000 lần → null;
Z=(TAR−null_mean)/null_sd; detected nếu Z≥3. Ladder mỗi BAM 25x, control 0% **bắt buộc**.

### Compendium 1 = SEQC2 truth sSNV (39,447 site)  ✅
Denoise: **35,712 site sạch** (loại 3,735 site nhiễu cao). Nền control gộp e_pool=**3.19e-5**
(sau denoise; trước denoise ~0.43% — nhiễu do thiểu số site germline/CN chi phối).

| Sample | TF | TAR (exact-ALT) | excess reads | Z | emp_p | detected |
|---|---|---|---|---|---|---|
| TF1e-2 | 1% | 4.01e-3 | 3,768 | **414** | 0 | ✅ |
| TF1e-3 | 0.1% | 6.18e-4 | 579 | **61** | 0 | ✅ |
| TF1e-4 | 0.01% | 2.37e-4 | 222 | **21** | 0 | ✅ |
| TF0 | 0% (control) | 3.19e-5 | 30 | ≈0 | 0.47 | ❌ (đúng) |

- **LoD (Z≥3) = 1e-4 (0.01%)** — cả 3 mức đều detected; control 0% đúng là *not detected*.
- **Linearity (cảnh báo)**: 1e-2→1e-3 tụt ~7x (gần lý tưởng 10x), nhưng 1e-3→1e-4 chỉ tụt ~3x →
  tín hiệu ở 1e-4 chạm **sàn nhiễu dư** (~2e-4 không scale theo TF). ⇒ **định lượng đáng tin đến ~1e-3**;
  ở 1e-4 detect được về mặt thống kê nhưng không còn tuyến tính (thận trọng khi diễn giải).
- Titration curve: `week4/expB/titration_truth.png` (log-log TAR vs TF + đường nền control).

### Compendium 2 = calls ClairS-TO pure tumor (40,859 PASS SNV in HC)  ✅
Denoise: **26,439 site sạch** (loại **14,420** = 35% — chính là FP + germline của caller bị control bắt).
e_pool=**7.2e-6**.

| Sample | TF | TAR | Z | detected |
|---|---|---|---|---|
| TF1e-2 | 1% | 4.98e-3 | 1324 | ✅ |
| TF1e-3 | 0.1% | 7.18e-4 | 189 | ✅ |
| TF1e-4 | 0.01% | 2.25e-4 | 58 | ✅ |
| TF0 | 0% | 7.2e-6 | ≈0 | ❌ (đúng) |

- **LoD = 1e-4**, cùng pattern non-linear ở 1e-4 như compendium-truth.
- **Phát hiện quan trọng**: dù compendium self-derived dính ~30% FP (từ Exp A), **detection/LoD KHÔNG bị
  phá** — vì bước denoise dùng control 0% tự loại 35% site (đúng phần FP/germline). ⇒ detection **bền vững
  với FP của compendium** khi có control 0% tốt. (Đây là lý do control 0% là *bắt buộc*.)

### So sánh 2 compendium + đường titration
`week4/expB/titration.png` (log-log, cả 2 compendium + đường nền + vùng non-linear). Cả hai hội tụ:
**LoD thống kê 1e-4, định lượng tuyến tính ~1e-3.**

### So paper (10⁻⁵)
Paper (Zviran 2020) đạt LoD ~1e-5 nhờ coverage sâu + molecular/short-read. Ở đây ONT **25x**, nền exact-ALT
cao → LoD thống kê ~**1e-4**, định lượng tin cậy ~**1e-3**. Kém paper ~1–2 bậc, **đúng kỳ vọng** cho ONT 25x
không molecular barcoding.

---

## Kết luận đạt/không đạt vs S1

| Tiêu chí (S1) | Kết quả | Đạt? |
|---|---|---|
| Precision ≥0.90 | 0.707 | ❌ |
| Recall ≥0.80 | 0.732 (PASS) / 0.772 (all) | ❌ |
| F1 ≥0.85 | 0.719 (best-F1 sweep 0.720) | ❌ |
| LoD ≤1e-3 | 1e-3 (định lượng) / 1e-4 (thống kê) | ✅ |
| Control 0% *not detected* | Z≈0, đúng | ✅ |
| Compendium size ~1e4–4e4 | 48,819 genome / 40,859 HC | ✅ (hơi trên biên) |

### Chốt Phase 0
1. **Detection pipeline ĐẠT**: LoD định lượng ~**1e-3**, detect thống kê tới **1e-4**; control 0% sạch;
   **bền vững với FP của compendium** nhờ denoise bằng control (bắt buộc). Kém paper (1e-5) ~1–2 bậc —
   đúng kỳ vọng cho ONT 25x không molecular barcoding.
2. **Caller KHÔNG ĐẠT** ngưỡng precision/recall đặt ra (F1=0.72 ở ~100x, best-F1 sweep xác nhận không
   phải lỗi ngưỡng). Nghi **model `ssrs` lệch basecaller methylation-aware `5mCG_5hmCG`** của BAM — cần thử
   lại với BAM sup chuẩn hoặc COLO829 để phân biệt "lỗi caller" vs "lỗi mẫu/model".
3. **Điểm mấu chốt**: detection MRD vẫn chạy tốt *dù* caller chưa hoàn hảo — vì tích hợp đa-site + denoise
   bằng control kéo tín hiệu ra khỏi nhiễu. Nghĩa là compendium không cần precision hoàn hảo để detect được.

### Việc tiếp (đề xuất, ngoài Phase 0)
- Chạy lại Exp A trên BAM sup chuẩn (`/big8_disk/data/HCC1395/ONT/HCC1395.bam`) và/hoặc COLO829 để kiểm giả thuyết model-mismatch.
- Thêm replicate rep2/rep3 cho ladder → CI cho LoD.
- Cân nhắc molecular/consensus (duplex) để hạ nền, tiến gần 1e-5.

### Artifacts
- Exp A calls: `week4/expA_full/HCC1395_pure/snv.vcf.gz`; eval: `week4/expA_eval/`
- Exp B scoring: `week4/expB/score_{truth,calls}_compendium.tsv`, `mrd_{truth,calls}.tsv`, `titration.png`
- Scripts: `week4/expB/mrd_score.py`, tái dùng `week3/run_clairs_to.sh`, `week3/tagging/pon_exact_alt.py`
