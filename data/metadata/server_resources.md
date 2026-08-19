# Server resource inventory for long-read MRD research

Survey of datasets, tools, and related projects on this server that are useful for a
tumor-only / long-read **minimal residual disease (MRD)** thesis.
Paths are absolute. "Used" = already used in this project (ONT_MRD / mrd-longphase).
Surveyed: 2026-08-14. Other users' directories are read-only references — **ask the owner
before using their data/code**.

---

## A. Datasets

### A1. Cancer cell lines with somatic truth (backbone for validation)
| Cell line | Cancer | Truth set | ONT data | Path |
|---|---|---|---|---|
| **HCC1395** | breast | **SEQC2 v1.2.1** — 39,447 sSNV, 1,625 sINDEL, HC-region BED, superset (212,366), CNV | 3 basecalls (`ONT`, `ONT_5khz_simplex_5mCG_5hmCG`, `ONT_Dorado`); tumor + `HCC1395BL` | `/big8_disk/data/HCC1395` |
| **COLO829** | melanoma | **NYGC v6** truth VCF (`colo829_truth.vcf.gz`) | `ONT_R10` (tumor 50x + BL 25x), `ONT_PAO` | `/big8_disk/data/COLO829`, `/big8_disk/data/colo829_nygc` |
| H1437 | lung | — | tumor + BL | `/big8_disk/data/H1437` |
| H2009 | lung | — | tumor + BL | `/big8_disk/data/H2009` |
| HCC1937 | breast | — | tumor + BL | `/big8_disk/data/HCC1937` |
| HCC1954 | breast | — | tumor + BL | `/big8_disk/data/HCC1954` |

- **Precomputed somatic caller outputs** per line (skip re-running for comparison):
  `ClairS_TO_v0_3_0`, `ClairS_TO_ss_v0_3_0`, `ClairS_v0_4_0`, `DeepSomatic_TO_v1_8_0`,
  `DeepSomatic_v1_8_0` under each `.../<line>/ONT*/`.
- HCC1395 coverage profile precomputed: `/big8_disk/data/HCC1395/ONT/depth/` (mosdepth).
- **Two truth-backed lines (HCC1395 + COLO829) enable cross-validation.**

### A2. Dilution / mixture series (core MRD asset — three independent kinds)
| Series | Levels | Coverage | Path | Status |
|---|---|---|---|---|
| Tumor-fraction ladder | TF0, 1e-2, 1e-3, 1e-4 (×3 reps) | 25x | `/bip7_disk/pingting114/mixed_bam/HCC1395/` | **Used** (week4 LoD) |
| Tumor:normal purity mix | `t00_n25 … t50_n00` | ~25x | `/big8_disk/data/HCC1395/ONT/subsample/` | not yet used |
| Google somatic titration | multi-line | — | `/big8_disk/Google_somatic_data/` (bams + benchmarking) | not yet used |

### A3. Normal / control cohorts (denoising, panel-of-normals)
- `/bip7_disk/pingting114/noise_cohort_25x/` — 4 blood-normal lines (H1437, H2009, HCC1937, HCC1954) @25x. **Used** (exact-ALT PoN, week4).
- `/bip8_disk/pingting114/noise_cohort_qc/` — QC of the above.

### A4. Population panel-of-normals databases
- `/big8_disk/data/PON/clairs-to_databases/` — gnomAD r2.1, dbSNP b138, 1000g-pon, **CoLoRSdb** (long-read). **Used** (ClairS-TO NonSomatic tagging).
- `/big8_disk/data/PON/deepsomatic-to_databases/` — DeepSomatic PoN VCFs.

### A5. Germline reference samples & hard regions (benchmark / controls)
- GIAB **HG002**: `/big8_disk/giab_lsk114_2022.12`, `/big8_disk/gm24385_2023.12`, `/big8_disk/hg002_revio` (PacBio Revio).
- `/big8_disk/CMRG_v1.00` — challenging medically-relevant genes.
- GIAB difficult-regions BED (used for artifact tagging): under `/big8_disk/data/PON/clairs-to_databases/`.

### A6. References
- `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` (**used**), `/big8_disk/T2T-CHM13v2.0`, `/big8_disk/clair3_models`.

---

## B. Tools
| Category | Tool | Location / note |
|---|---|---|
| Tumor-only somatic SNV | **ClairS-TO** v0.5.0 | `week1/experiment/external/ClairS_TO_latest` (**used**) |
| Paired somatic | ClairS, **DeepSomatic(-TO)** | ClairS in external/; DeepSomatic runs under `liaoyoyo2001`, `fenne113` |
| Germline | Clair3 | `external/Clair3_latest`; models `/big8_disk/clair3_models` |
| Phasing / haplotag | **LongPhase** (+ somatic & methylation builds), whatshap | `external/longphase_develop`, `chenhan112`, `liaoyoyo2001`; `whatshap` in PATH |
| Somatic SV | **Severus** | `/big8_disk/chenhan112/Severus` |
| Benchmarking | hap.py / som.py | `external/hap.py_latest` (build broken → used `bcftools isec` instead); **rtg/vcfeval absent** |
| Methylation | longphase-methylation + pipelines | `liaoyoyo2001` (`modkit` binary not found standalone) |
| Utilities | samtools 1.13, bcftools 1.13, tabix, mosdepth, pysam, numpy, scipy, matplotlib | in PATH / python env (**pandas & bedtools absent**) |

---

## C. Related projects (learn from / potentially reuse — ask owner)
| Owner | Focus | Relevance to MRD | Path |
|---|---|---|---|
| **pingting114** | dilution ladders + noise cohorts | the MRD data engineering (mixtures, controls) | `/bip7_disk/pingting114`, `/bip8_disk/pingting114` |
| **nitya114** | ML on somatic reads (CNN / autoencoder on read tensors & images), FP analysis, haplotag HCC1395 (t30n20) | directly targets **reducing false positives** in somatic calls (the ~30% FP problem) | `/big8_disk/nitya114` |
| **liaoyoyo2001** | somatic **methylation** analysis + longphase-methylation + DeepSomatic | **multi-modal MRD** (methylation as a signal) | `/big8_disk/liaoyoyo2001` |
| **chenhan112** | LongPhase (incl. somatic) dev + Severus | phasing + SV for MRD | `/big8_disk/chenhan112` |
| **fenne113** | caller filter comparison (DeepSomatic vs ClairS filters) | understanding PASS / filter behavior | `/big8_disk/fenne113` |
| — | `Somatic_calling/` — 5 lines × {ClairS, ClairS-TO, DeepSomatic} + Nature578 | consolidated caller outputs | `/big8_disk/Somatic_calling` |
| **hung114 (me)** | ONT_MRD (w1–w4) + `mrd-longphase` | this project | `/big8_disk/hung114/ONT_MRD` |

---

## D. Mapping to the MRD workflow
| MRD step | Available resource |
|---|---|
| Marker discovery (tumor-only calling) | ClairS-TO / DeepSomatic-TO + cell-line tumor BAMs |
| Truth validation | SEQC2 (HCC1395), NYGC (COLO829) |
| Detection & LoD | 3 independent dilution/titration series (A2) + 0% control |
| Denoising | noise cohort (A3) + population PoN (A4) |
| Multi-modal extension | methylation (liaoyoyo2001), SV (Severus), phasing (LongPhase) |
| FP reduction via ML | read-tensor / CNN approach (nitya114) |

## E. Suggested next uses
- **Cross-validate LoD** on COLO829 (has NYGC truth + tumor/BL) to check whether the HCC1395
  LoD (~1e-3 quantitative / 1e-4 statistical) generalizes across cell lines.
- **Compare dilution designs**: TF ladder vs `subsample` purity mixes vs Google titration —
  are LoD estimates consistent?
- **Investigate the tumor-only FP problem** using the precomputed multi-caller outputs
  (ClairS-TO vs DeepSomatic-TO) and fenne113's filter comparisons.
- **Multi-modal**: layer methylation / phasing evidence at candidate loci (fits `mrd-longphase`
  `workflow/{phasing,methylation}/`).

> Large raw data (BAMs, references) stays on shared disks; do not copy into the repo.
> Record any external path you rely on in `config/` and here in `data/metadata/`.
