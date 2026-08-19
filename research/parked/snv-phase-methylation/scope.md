# 00 — Scope

Status: active research contract
Date: 2026-08-16
Supersedes the Week 1 framing in [`../RESEARCH_SCOPE.md`](../../../archive/RESEARCH_SCOPE.md) as the
*primary* storyline; that document's candidate-characterization work is retained as the
upstream baseline.

---

## Direction

**Tumor-only long-read MRD through haplotype-conditioned native methylation evidence.**

## Central question

> After accounting for sequence and haplotype context, does native methylation provide
> incremental evidence for detecting tumor-derived molecules at low tumor fractions?

The load-bearing word is **incremental**. The question is not "is methylation informative"
— it is "is methylation informative *after* sequence and haplotype have already been used".
A design that cannot separate those contributions cannot answer this question.

## Problem

Tumor-only detection has no matched normal to subtract. Germline and background artifacts
must be suppressed from within the tumor sample plus population resources. At tumor
fractions of 1%, 0.1%, and 0.01%, the number of genuinely tumor-derived molecules at any
given locus becomes small enough that a single allele observation is weak evidence.

Long reads carry three kinds of evidence on the *same physical molecule* that short reads
cannot co-observe at this range: the allele, its haplotype/phase-set context, and native
base modifications. The hypothesis under test is that combining them per molecule raises
the evidence per molecule enough to matter at low tumor fraction.

## Input

| Input | Path | Role |
|---|---|---|
| Pure tumor BAM | `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam` | candidate discovery, positive-control methylation reference |
| Normal BAM | `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395BL.bam` | **evaluation only** — source of per-read labels |
| Reference | `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` | alignment reference |
| Dilution 1% | `/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-2_25x/TF1e-2_25x.rep1.bam` | ~25×, 1 replicate |
| Dilution 0.1% | `.../TF1e-3_25x/TF1e-3_25x.rep1.bam` | ~25×, 1 replicate |
| Dilution 0.01% | `.../TF1e-4_25x/TF1e-4_25x.rep1.bam` | ~25×, 1 replicate |
| Control 0% | `.../TF0_25x/TF0_25x.rep1.bam` | ~25×, required negative control |
| Candidate SNVs | ClairS-TO v0.5.0 tumor-only output | defines the loci examined |

All of the above are **read-only**. Nothing in this project modifies, re-indexes, copies,
or moves them.

Platform: ONT R10.4.1, 5 kHz simplex, Dorado 5mCG/5hmCG modified-base calling.
Confirmed present in every dilution BAM: `MM:Z:C+m?` and `MM:Z:C+h?` with matching `ML`.
Confirmed **absent** in every BAM: `HP` and `PS` — haplotagging is work this project must do.

## Unit of analysis

**One informative molecule** = one read that overlaps a candidate locus and for which the
allele, the haplotype/phase-set context, and the native methylation evidence can all be
read off the same alignment record.

This is deliberately narrower than "one read" and narrower than "one variant". The joint
record is defined in [`../../orchestration/schemas/joint-molecule.schema.md`](../../../orchestration/schemas/joint-molecule.schema.md)
once Phase 3 lands.

## Expected output

1. A **feasibility funnel** — how many molecules survive from *all reads* to *usable joint
   evidence*, broken down by sample, dilution, region, candidate, phase set, haplotype.
2. A **joint-molecule evidence table** — sparse, region-partitioned, resumable, deterministic.
3. An **ablation comparison** across models A–F isolating the contribution of each modality.
4. A **claim-boundaried write-up** distinguishing observation, inference, hypothesis, and
   unresolved question.

The per-molecule target is conceptually

```text
P(tumor-origin molecule | allele, haplotype, methylation, quality)
```

and the sample-level MRD score aggregates across molecules. **Neither is implemented yet.**
The first decision is whether enough joint molecules exist to make the question testable.

## In scope

- Region-based extraction of joint-molecule records from candidate loci.
- LongPhase/WhatsHap phasing and haplotagging of the dilution BAMs.
- MM/ML parsing into per-CpG probabilities, counts, and read-end distances.
- Feasibility counting and missingness characterization.
- Interpretable per-molecule models: likelihood ratio, logistic regression, calibrated
  linear models.
- Leakage-safe splitting by chromosome, region, or sample.
- Ablation across the six sequence/haplotype/methylation combinations.
- Detection-rate reporting by dilution against the 0% control.
- Provenance: tool versions, input manifests, seeds, run logs.

## Out of scope

- Deep learning (until interpretable evidence justifies it).
- CNA integration, fragmentomics, structural variants.
- Cloud deployment, clinical prediction, patient-facing anything.
- High-VAF clonality investigation (deferred open question, not the storyline).
- Matched-normal calling as an *inference* input.
- Building a complete clinical MRD assay.
- Any claim of clinical MRD performance from HCC1395 genomic dilution data.

## Relationship to prior work in this repository

| Prior work | New role |
|---|---|
| Week 1 ClairS-TO candidate characterization | **upstream baseline** — supplies candidate loci |
| `week3/` tagging + compendium v1.0 | upstream baseline — candidate qualification, referenced not rebuilt |
| `week4/` Phase 0 caller + detection validation | **prior-evidence anchor** — establishes that ClairS-TO tumor-only precision is 0.707 and recall 0.732 against SEQC2 HC, i.e. the sequence-only baseline is far from perfect. That imperfection is precisely why incremental evidence is worth testing |
| `week4/expB/` titration scoring | upstream baseline for the sample-level aggregation step (H4) |
