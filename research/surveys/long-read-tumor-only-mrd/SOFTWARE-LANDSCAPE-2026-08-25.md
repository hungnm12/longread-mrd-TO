# Software landscape for MRD / ctDNA detection — where the tumour-only long-read direction sits

Built for the 2026-08-26 meeting, to be readable beside a colleague's survey of the same field.
Sources: 13 held sources in the MRD notebook. **Rows marked ※ come from a synthesis/review
document, not the method's own paper** — those numbers are second-hand and must be verified before
they are quoted in writing.

---

## 1. The answer, first

**No source describes a tool that is simultaneously long-read, tumour-only, and aimed at MRD
detection.** Verbatim: *"There is no single software tool in these sources that is simultaneously
classified as long-read, strictly tumour-only, and designed exclusively for MRD detection."*

Two systems border that cell, and one of them claims this project's target number:

| | Platform | Normal needed | Purpose | Detection limit |
|---|---|---|---|---|
| **NanoRCS** ※ | long-read ONT | no | genome-wide TF profiling / MRD surveillance | **0.24% TF** |
| **SIMMA** ※ | long-read | no | multi-omic liquid-biopsy classifier | **100 ppm = 0.01% TF** |

**SIMMA is the threat to this direction and it must be read before Wednesday.** Long-read,
tumour-only, multi-omic (mutation + 5mC + fragmentomics), claiming exactly the tumour fraction this
project targets. Everything known about it here comes from a synthesis document.

---

## 2. The named methods

| Name | What it computes | Matched normal | Informed / naive | Platform | Headline number |
|---|---|---|---|---|---|
| **MRDetect** | read-centric SVM over SNVs + bin-wise coverage skew for CNAs | yes | informed | short | **10⁻⁵ TF**, ROC-AUC 0.97 |
| **AccuScan** | rolling-circle concatemer consensus; ALT required in ≥2 copies | no | naive | short | 96% detection at **2.5×10⁻⁵ cTAF** |
| **ClairS-TO** | dual CNNs (affirmative + negational) + PoN + Verdict + haplotype filters | **no** | naive | **long** | VAF LoD **1–5%** |
| **DeepSomatic** ※ | multi-channel pileup tensors → CNN | optional | naive | either | VAF LoD **3–5%** |
| **smrest** ※ | assigns each read to a parental haplotype; excludes mismatching reads | **no** | naive | **long** | VAF LoD **5–10%** |
| **LongPhase-S** ※ | anchors somatic reads to germline haplotypes; recalibrates another caller | yes | informed | **long** | +4.5% SNV F1, +7.1% indel F1 |
| **NanoRCS** ※ | concatemer intramolecular consensus | no | naive | **long** | **0.24% TF**, Q31 |
| **SIMMA** ※ | multi-omic classifier: mutation + native 5mC + fragmentomics | no | naive | **long** | **100 ppm** |
| **deepSNV** | hierarchical beta-binomial + likelihood-ratio test | yes | informed | short | 0.01% VAF |
| **shearwater** | beta-binomial across a panel of normals, Bayes factor | no | optional | short | ROC-AUC **0.984** (informed) |
| **DREAMS-vc** | NN trained on controls → per-base error probability | no | naive | short | ROC-AUC **0.808** (naive) |
| **PhasED-seq** ※ | **same-molecule co-occurrence of ≥2 somatic mutations on one fragment** | yes | informed | short | background **<10⁻⁶**, PPM LoD |
| **CODEC** ※ | intramolecular duplex linkage before sequencing | no | naive | short | ~10⁻⁶ error, 100× fewer reads |
| **TNER** ※ | trinucleotide-context background error from the sample's own non-candidate loci | no | naive | short | — |
| **EBCall** ※ | empirical-Bayes beta-binomial | yes | informed | short | — |
| **GuardantOMNI** | population filters + beta-binomial germline/somatic split + CHIP masking | no | naive | short | 98.7% SNV accuracy |
| **MSIsensor-ct** ※ | ML classifier on microsatellite distributions | no | naive | short | 100% acc. at 0.05% TF |
| **MobiCT** ※ | Nextflow UMI pipeline, empirical error model | no | naive | short | — |
| **Mutect2** | local de Bruijn reassembly | optional | naive | either | baseline |
| **VarScan2** | Fisher's exact on tumour/normal counts | yes | informed | short | baseline |

---

## 3. The 2×2 this project actually lives in

| | **Tumour-informed** | **Tumour-only** |
|---|---|---|
| **Short-read** | MRDetect · PhasED-seq · deepSNV · EBCall · VarScan2 | AccuScan · shearwater · DREAMS-vc · GuardantOMNI · TNER · CODEC · MSIsensor-ct · MobiCT |
| **Long-read** | LongPhase-S | **ClairS-TO · smrest · DeepSomatic** *(callers, not MRD)*<br>**NanoRCS · SIMMA** *(MRD, but ※)* |

The bottom-right cell has five entries. **Three are somatic variant callers, not MRD detectors.**
Two are MRD-capable and both reach this project only through a synthesis document.

---

## 4. Who already does each mechanism this project uses

| Mechanism | Who does it | Same as here? |
|---|---|---|
| **Haplotype phase as a per-molecule background/consistency filter** | **smrest**, **ClairS-TO**, **LongPhase-S** | **Yes — three times.** Not novel |
| **Same-molecule co-occurrence of ≥2 variants** | **PhasED-seq** only | **Partly.** PhasED-seq is tumour-**informed** and short-read; the tumour-only long-read version is unclaimed |
| **Patient's own heterozygous germline SNPs as internal calibrator** | **smrest**; also the beta-binomial normal-free workflows | **Yes.** This project's `EXP-S1-005` calibrator is the same idea |
| **Sample's own non-candidate loci as the background model** | **TNER** | **Yes in spirit.** Named prior art for "background from the sample itself" |
| **Cross-individual controls to anchor a threshold** | **MRDetect** (informed only) | **This project measured why it does not port.** Nobody else has |
| **Gate on observed ALT-read count before scoring** | *not found* | **Unclaimed in these sources** |

---

## 5. What is empty, stated carefully

Two cells returned nothing across two independent searches (2026-08-21 systematic, 2026-08-24 deep
research) plus this enumeration:

1. **Same-molecule co-occurrence of ≥2 tumour-only candidates on one long read, as a
   background-suppression statistic for MRD.**
2. **A published benchmark of what any matched-normal-free haplotype filter actually removes.**

Both are *absence of found work*, not proof of absence — and item 2 rests on a synthesis's silence
(see `LITERATURE-CHECK-2026-08-25.md`).

---

## 6. The comparison that must NOT be made on the slide

It is tempting to write: *"published tumour-only long-read callers reach 1–10% VAF; we detect at
0.1%; therefore we are 10–100× better."*

**That comparison is invalid.** ClairS-TO's and smrest's numbers are **per-variant calling limits** —
the VAF at which one variant can be called. This project's 0.1% is a **sample-level aggregate**
across thousands of candidate positions. MRDetect's entire argument is that aggregation beats
per-locus sensitivity; the two quantities are not on the same axis.

The defensible sentence is the narrow one: *"tumour-only long-read tooling is built for variant
calling at percent-level VAF; whether it supports sample-level MRD detection at 0.01% is unestablished,
and cell D of the landscape is empty."*

---

## 7. What to check before quoting anything here

| Priority | Item | Why |
|---|---|---|
| **1** | **SIMMA** primary paper | Long-read + tumour-only + 100 ppm. If real, it occupies this project's target cell |
| 2 | **NanoRCS** primary paper | 0.24% TF is 24× above MRD need — confirm, since it bounds the honest claim |
| 3 | **smrest** primary (PMC10925087) | The haplotype mechanism and whether its filter yield is reported |
| 4 | **ClairS-TO** primary (Nat Commun 2025) | Same, for `MultiHap` / `NoAncestry` |

All four are ※ or WAF-blocked. Downloading them by hand is the highest-value hour available.
