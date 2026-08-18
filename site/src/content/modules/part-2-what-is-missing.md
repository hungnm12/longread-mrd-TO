---
id: MODULE-002
part: 2
title: What is missing for tumor-only long-read MRD
subtitle: Why removing the matched normal makes background suppression the binding constraint, and what a long read can offer in its place.
status: observed
evidence_level: external_report
reading_time_minutes: 14
learning_objectives:
  - Explain why tumor-only detection is harder than matched-normal detection, in terms of the five-stage pipeline.
  - State what sequence alone observes about a molecule, and what it cannot observe.
  - Describe what haplotype and phase-set context add, and why haplotype consistency is evidence rather than proof.
  - Say what native methylation might add that sequence and haplotype do not already carry.
  - Identify which of this lab's existing resources map onto which gap.
why_it_matters: >-
  This project has already measured how good the sequence-only tumor-only baseline is:
  precision 0.707 and recall 0.732 against SEQC2 high-confidence regions, against
  pre-registered targets of 0.90 and 0.80. That gap is not a bug to be tuned away — it is the
  reason there is a research question. Understanding exactly which evidence the baseline
  lacks is what makes the next step principled rather than opportunistic.
prerequisites:
  - "Part 1 — What existing MRD methods have in common"
previous_module: MODULE-001
next_module: MODULE-003
interpretation_boundaries:
  - The 0.707 / 0.732 caller figures are a measured property of one ClairS-TO run on one pure-tumor sample against one truth set. They do not generalise to other callers, samples, or regions.
  - Haplotype consistency is evidence compatible with somatic origin. It does not demonstrate somatic origin, and no statement here should be read as claiming otherwise.
  - Native methylation is described here as a candidate source of evidence. Whether it carries incremental information is the open question of this thesis, not an assumption of it.
  - The claim that this modality combination is unaddressed is scoped to seven indexed documents and is recorded as a candidate gap pending a systematic search.
open_questions:
  - Does a broader literature search find this modality combination already addressed?
  - How much of the sequence-only baseline's error is germline leakage, and how much is technical artifact? The two call for different remedies.
  - At 25x coverage, how long are phase blocks in practice, and what fraction of candidate-overlapping reads can be haplotagged at all?
  - Is 5hmC informative separately from 5mC, or does treating them separately merely cost statistical power?
questions:
  - RQ-001
hypotheses: []
papers:
  - PAPER-002
  - PAPER-003
  - PAPER-005
  - PAPER-006
glossary_terms:
  - GLOSSARY-003
  - GLOSSARY-004
  - GLOSSARY-001
  - GLOSSARY-005
sources:
  - label: "PAPER-006 — PhasED-Seq analytical validation"
    ref: PAPER-006
    note: the nearest published neighbour; phase-based background suppression
  - label: "PAPER-003 — cfDNA methylation profiling requirements"
    ref: PAPER-003
    note: pre-analytical and read-end methylation bias — a guardrail, not a method
  - label: "PAPER-005 — Methylation and expression as determinants of cfDNA fragmentation"
    ref: PAPER-005
    note: signal modalities are biologically coupled, not independent
  - label: "PAPER-002 — Nanopore consensus multimodal profiling"
    ref: PAPER-002
    note: long-read multimodal precedent, but SNV + CNA rather than per-molecule methylation
diagram:
  title: What is observable on one long read at a candidate locus
  caption: >-
    Sequence, haplotype and native methylation are co-observed on a single alignment record.
    The question is whether the third adds information the first two do not already carry.
  orientation: vertical
  stages:
    - label: One long read overlapping a candidate locus
      note: 10-50 kb on ONT R10
    - label: Sequence evidence
      note: the base at the candidate position, its quality, mapping quality
    - label: Haplotype and phase-set context
      note: HP/PS tags — which haplotype, relative to which phase block
    - label: Native methylation
      note: MM/ML tags — per-CpG 5mC and 5hmC probabilities, no separate assay
      emphasis: true
    - label: Technical quality and confounders
      note: read length, CpG distance to read ends, missingness
failure_modes:
  - title: Treating haplotype tags as somatic labels
    looks_like: >-
      A variant described as "confirmed somatic by phasing", or a pipeline that promotes
      haplotype-consistent variants without further evidence.
    severity: loud
    detail: >-
      A haplotype-consistent variant is equally consistent with germline variation, loss of
      heterozygosity, a mapping artifact recurring in phase, or copy-number-driven allelic
      imbalance. Haplotype is a feature, weighted like any other, never a label.
  - title: Comparing HP=1 across different phase sets
    looks_like: >-
      A stratified table grouped on the haplotype tag alone, pooling reads from many phase blocks.
    severity: silent
    detail: >-
      Phase blocks are independently oriented. Haplotype 1 in phase set 12345 has no
      relationship to haplotype 1 in phase set 67890. The only sound grouping key is the pair
      phase_set:haplotype, which is why the pipeline computes it as a derived field rather
      than leaving it to each analysis.
  - title: Summing 5mC and 5hmC into one methylation number
    looks_like: >-
      A single "methylation probability" per CpG, when the basecaller reported two codes.
    severity: silent
    detail: >-
      Dorado 5mCG/5hmCG calling reports C+m and C+h at every CpG. They are complementary,
      not independent — their sum plus P(unmodified) is one — and they may carry different
      biological information. Summing discards that before it can be tested.
  - title: Using read-end CpGs without exclusion
    looks_like: >-
      A methylation difference that tracks read length rather than source.
    severity: silent
    detail: >-
      Methylation near read ends is less reliable. If tumor and normal reads differ in length
      distribution, they differ in read-end fraction, and an apparent biological difference
      may be an artifact of that.
predictions: []
pending_experiments:
  - title: Haplotagging yield on the dilution BAMs
    blocked_on: >-
      Phasing and haplotagging have not been run. No BAM in this project currently carries
      HP or PS tags.
    experiment: EXP-H1-001
---

## Why removing the matched normal changes the problem

With a matched normal, germline variation is subtracted directly: anything present in the
normal is not somatic. The remaining problem is largely technical error.

Tumor-only removes that subtraction. Germline variants — of which a human genome carries
millions — must now be excluded from within the tumor sample plus population resources.
Population databases and panels of normals do most of this work, and they do it well for
common variants. They do it less well for rare private germline variants, which are
individually unusual and therefore look exactly like somatic ones.

Locating this on the Part 1 pipeline: **tumor-only does not change stages 1, 3, 4 or 5. It
makes stage 2 the binding constraint.**

## How good is the sequence-only baseline, actually

This project measured it rather than assuming it. Running ClairS-TO tumor-only on the pure
HCC1395 sample and comparing PASS SNVs against the SEQC2 v1.2.1 high-confidence sSNV set
within high-confidence regions:

| Metric | Observed | Pre-registered target | Met |
|---|---|---|---|
| Precision (SNV, HC) | 0.707 | ≥ 0.90 | no |
| Recall (SNV, HC, PASS) | 0.732 | ≥ 0.80 | no |
| F1 (SNV, HC) | 0.719 | ≥ 0.85 | no |

Roughly three in ten PASS calls are not in the truth set. That was checked rather than
explained away: only 5 of 11,975 false positives fell in the SEQC2 superset, so the
discrepancy is not an artifact of a conservative truth set.

Two things follow. First, the targets were **locked before the run** and then reported as
missed — the practice this project intends to keep. Second, a baseline that misclassifies
about 30% of its calls is a baseline with room above it. That is the practical motivation
for asking what other evidence a molecule carries.

## What sequence alone observes

At a candidate locus, sequence evidence is: the base this read carries, how confident the
basecaller was, and how confidently the read is placed. That is a small amount of
information, and crucially it is **the same information for every read carrying that base**.
Two reads with the same allele at the same locus are, to a sequence-only model, identical.

## What haplotype adds

Haplotagging assigns each read to one of two haplotypes within a phase block. This adds
information of a different kind: not *what* the molecule says, but *which physical copy of
the chromosome* it came from.

Why that helps:

- A somatic variant typically arises on one chromosome copy and should appear on one
  haplotype. Reads carrying it on both haplotypes are suspicious.
- Errors are not haplotype-aware, so haplotype consistency is harder for noise to fake than
  allele identity is.
- It gives a natural stratum for comparison: reads sharing a phase block share local
  sequence context, mappability, and coverage, so comparisons within a stratum control for
  those without modelling them.

The last point is what "haplotype-conditioned" means in this thesis, and it is the reason
haplotype enters as a conditioning variable rather than only as a feature.

**What haplotype does not do** is establish somatic status. See the failure modes below.

## What native methylation might add

ONT R10 with 5mCG/5hmCG basecalling reports, for every CpG on every read, a probability of
5-methylcytosine and of 5-hydroxymethylcytosine. This comes off the same molecule as the
sequence, in the same run, with no bisulfite conversion and no second library.

Verified on this project's data during the repository audit: **every one of 200 sampled
reads in each of the four dilution BAMs carries MM and ML tags**, with both `C+m` and `C+h`
codes present. The tags survived subsampling and merging because the alignment used
`minimap2 -y`.

The reason to think methylation might carry information sequence and haplotype do not:

- Methylation is a different physical property. It is not derivable from the base sequence
  at the locus, nor from which chromosome copy the read came from.
- Tumor and normal cells differ in methylation state at many loci, for reasons unrelated to
  the somatic mutations being called.
- It is available on **every** read, including reads carrying the reference allele — a
  category from which sequence evidence extracts almost nothing.

The reason to doubt it, which the design must take seriously: PAPER-005 shows methylation is
coupled to other molecular properties. If it is largely redundant with what haplotype
context already encodes, an ablation will show that. That outcome is a result, not a failure.

## What remains latent

Even with all three, some things are not observed and must be handled as confounders rather
than measured:

- **Copy number.** HCC1395 is aneuploid. Tumor reads over-represent amplified regions, which
  have their own methylation character.
- **Cell state.** Culture passage and cell-cycle position affect methylation without being
  tumor biology.
- **Realized tumor fraction.** The dilution levels are nominal mixing ratios; what is
  actually in each BAM was not independently measured.
- **Fragmentation biology.** Cell-line genomic DNA does not fragment like circulating cfDNA,
  so a methylation–fragmentation relationship observed here need not transfer.

## Which lab resources map onto which gap

| Gap | Resource available | State |
|---|---|---|
| Candidate loci without a matched normal | ClairS-TO v0.5.0 tumor-only, run genome-wide | done — 48,819 PASS SNVs |
| Baseline quality measurement | SEQC2 v1.2.1 truth + HC regions | done — 0.707 / 0.732 / 0.719 |
| Low tumor fractions | HCC1395 dilution series at 1%, 0.1%, 0.01% + 0% control | available, ~25x, one replicate each |
| Native methylation | 5mCG/5hmCG basecalls, MM/ML preserved into every mixture | **verified present** |
| Haplotype context | LongPhase binary present in the lab tree | **not yet run** — no BAM carries HP/PS |
| Per-molecule evaluation truth | Read names recoverable against the two source BAMs | **mechanism verified**, 28/28 assigned in a pilot window, 0 collisions |
| Analytical validation | — | not achievable: one replicate per level, one blank |

One row is the whole of the near-term work: haplotagging. It is the only missing input, and
it gates everything downstream.

## The candidate gap

> Existing provided studies do not establish whether native methylation measured on the same
> haplotagged molecule provides incremental tumor-origin evidence for tumor-only long-read
> detection at low tumor fractions.

This is recorded as a **candidate** gap. It is scoped to the seven indexed documents, none of
which has been verified at PDF level. Promoting it to an established gap requires a
systematic search whose queries and results are recorded, and that search has not been run.

The nearest neighbour is PhasED-Seq (PAPER-006), which suppresses background by requiring
multiple variants in phase. Part 1 noted where that strategy weakens: it needs a molecule to
carry two or more informative variants, which becomes unlikely exactly when tumor fraction
is low. The question this thesis asks is whether methylation conditioned on haplotype
context can play a similar background-suppressing role using a **single** variant.

Part 3 turns that question into four gated hypotheses and states what would falsify each.
