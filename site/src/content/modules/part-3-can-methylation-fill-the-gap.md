---
id: MODULE-003
part: 3
title: Can haplotype-conditioned native methylation fill the gap?
subtitle: Four gated hypotheses, the joint-molecule unit they operate on, and the ablation design that would falsify them.
status: planned
evidence_level: preliminary
reading_time_minutes: 16
learning_objectives:
  - Define the joint-molecule unit and say why it is narrower than "one read" and narrower than "one variant".
  - Read the feasibility funnel and explain why stage survivals must not be multiplied together.
  - State the six-model ablation grid and identify which comparison answers which hypothesis.
  - Explain why the evaluation-only source label must never reach a model, and how that is enforced.
  - Name the acceptance and rejection condition for each of H1 through H4, and the pivot taken if it is rejected.
why_it_matters: >-
  A design that cannot fail is not a research design. This module lays out, before any result
  exists, exactly what would count as evidence for the thesis and what would count as evidence
  against it. If methylation turns out to be redundant with haplotype context, this design
  produces that answer cleanly — and that is a legitimate outcome, not a failure to avoid.
prerequisites:
  - "Part 1 — What existing MRD methods have in common"
  - "Part 2 — What is missing for tumor-only long-read MRD"
previous_module: MODULE-002
next_module: null
interpretation_boundaries:
  - No result on this page has been produced. Every hypothesis is untested and every threshold is deliberately unset.
  - HCC1395 genomic dilution is controlled low-TF method development. It is not plasma cfDNA and does not establish clinical MRD performance.
  - With one replicate per dilution level and one blank sample, limit of blank and limit of detection are not estimable. The dilution series supports relative comparison between models at matched conditions only.
  - If molecules cluster by methylation pattern, that is a pattern in the data. Calling it a biological clone requires evidence this design does not produce.
  - Methylation associated with tumor origin after conditioning is an association. This design does not establish causation.
  - Dilution levels are nominal mixing ratios; the realized tumor fraction in each BAM was not independently measured.
open_questions:
  - Are there enough molecules carrying allele, haplotype and methylation simultaneously at 0.01% for H2 to be testable at all?
  - Does the read-name labelling mechanism hold at genome scale, or do supplementary alignments and name collisions appear once the pilot window is left behind?
  - Should haplotagging be run on whole BAMs or only on candidate-region slices? Region-scoped is far cheaper but produces shorter phase blocks.
  - Which chromosomes should be held out for testing, and is that choice recorded before any model is fit?
  - If H3 accepts but H4 rejects, is the per-molecule result a sufficient thesis contribution?
questions:
  - RQ-001
hypotheses:
  - HYP-001
papers:
  - PAPER-005
  - PAPER-006
glossary_terms:
  - GLOSSARY-002
  - GLOSSARY-009
  - GLOSSARY-006
  - GLOSSARY-007
  - GLOSSARY-008
  - GLOSSARY-003
sources:
  - label: "PAPER-006 — PhasED-Seq analytical validation"
    ref: PAPER-006
    note: source of the LoB/LoD vocabulary this design deliberately does not claim
  - label: "PAPER-005 — Methylation and cfDNA fragmentation"
    ref: PAPER-005
    note: why the design is an ablation rather than feature stacking
diagram:
  title: The feasibility funnel
  caption: >-
    Every examined read-candidate pair is recorded, usable or not, tagged with the first check
    it failed. The funnel is therefore a grouping over one table rather than a second pipeline
    that could drift from the first.
  orientation: vertical
  stages:
    - label: All examined reads
      note: every read overlapping a candidate locus, before any filter
    - label: Candidate-overlapping
      note: primary alignments passing mapping-quality and flag checks
    - label: Allele-informative
      note: the candidate position is aligned and the base quality is sufficient
    - label: Haplotagged
      note: carries both HP and PS
    - label: Methylation-informative
      note: enough usable CpGs after read-end exclusion
    - label: Usable joint-evidence molecules
      note: all three signals present on one molecule — the quantity H1 turns on
      emphasis: true
hypothesis_boxes:
  - id: h1
    name: H1 — Observation feasibility
    claim: >-
      Enough reads contain allele, haplotype and methylation information simultaneously for the
      central question to be testable on this data.
    gate: Gates everything. No modelling happens until H1 is accepted.
    accepts: >-
      Usable joint molecules at the 1% level meet the pre-registered minimum, no single funnel
      stage collapses below the minimum survival fraction, and enough candidate loci contribute
      at least one joint molecule. All three thresholds are set before the run.
    rejects: >-
      Joint molecule count at 1% falls below the minimum, or haplotagging yield is so low that
      haplotype context is unavailable for most candidate-overlapping reads.
    status: blocked
  - id: h2
    name: H2 — Biological separability
    claim: >-
      Tumor-origin and background reads show reproducible methylation differences within
      comparable haplotype context.
    gate: Requires H1 accepted.
    accepts: >-
      The within-haplotype methylation difference exceeds the pre-registered effect size with a
      confidence interval excluding zero, in enough independent strata, reproducing in direction
      on held-out chromosomes and surviving a copy-number sensitivity analysis.
    rejects: >-
      Effects vanish after conditioning on haplotype context, fail to reproduce across
      chromosomes, or are fully explained by coverage asymmetry, copy number, or read-end bias.
    status: pending
  - id: h3
    name: H3 — Incremental computational value
    claim: >-
      Adding methylation improves tumor-molecule classification beyond sequence and haplotype
      baselines.
    gate: Requires H2 accepted. This is the hypothesis the thesis title asserts.
    accepts: >-
      Model F exceeds model D on sensitivity at fixed specificity by the pre-registered margin,
      with non-overlapping intervals on held-out splits, exceeding the permuted-methylation
      control, and without degrading calibration.
    rejects: >-
      F is within uncertainty of D, or F's advantage disappears under the permutation control,
      or F improves ranking while degrading calibration.
    status: pending
  - id: h4
    name: H4 — Low-TF detection value
    claim: >-
      Per-molecule improvement produces sample-level detection improvement across dilution levels.
    gate: Requires H3 accepted.
    accepts: >-
      Model F's lowest detected tumor fraction is at least as low as model D's, F's separation
      from the 0% control exceeds D's by the pre-registered margin at matched specificity, and
      neither model calls the control detected.
    rejects: >-
      No difference in lowest detected level and no separation gain; or the methylation-using
      model calls the 0% control detected, which is disqualifying regardless of sensitivity.
    status: pending
predictions:
  - question: Which funnel stage will be the binding constraint on joint-molecule yield?
    prediction: >-
      Haplotagging, not methylation. Methylation coverage was near-universal in the audit — 100%
      of 200 sampled reads carried MM/ML in every dilution BAM — whereas no BAM carries HP/PS at
      all yet, and at roughly 25x coverage phase blocks should be short with substantial
      haplotagging failure in regions of low heterozygous-variant density.
  - question: How steeply will usable joint-molecule counts fall from 1% to 0.01%?
    prediction: >-
      Far less steeply than 100-fold. The funnel counts molecules at candidate loci regardless
      of source, and at every dilution the large majority of molecules are normal-derived. The
      quantity that falls roughly with tumor fraction is the count of *tumor-derived* joint
      molecules, and that is the number likely to become too small to support H2 at 0.01%.
  - question: Will model F beat model D?
    prediction: >-
      Genuinely uncertain, which is why the experiment is worth running. PAPER-005's coupling
      argument gives real reason to expect substantial redundancy between methylation and the
      context haplotype conditioning already captures. A finding that F is approximately equal to
      D, with E greater than A, would be the most informative negative result available.
failure_modes:
  - title: Splitting reads from the same region across train and test
    looks_like: >-
      An unexpectedly strong result that does not reproduce when the split is changed.
    severity: silent
    detail: >-
      Reads from one region share alignment context, error modes, phasing state, and possibly the
      same source molecule. Random read-level splitting places correlated observations on both
      sides and inflates every metric. The codebase provides no random-split function; splitting
      is by chromosome, region or sample, and a test asserts that no region spans the split.
  - title: Letting the evaluation label reach the model
    looks_like: >-
      Near-perfect performance, or a feature whose importance is implausibly high.
    severity: loud
    detail: >-
      The per-read source label is evaluation-only. It is named
      source_label_for_evaluation_only precisely so that its appearance in a feature path is
      obvious in review, and a test asserts that two otherwise identical rows differing only in
      label produce identical features.
  - title: Selecting methylation regions using the evaluation dilutions
    looks_like: >-
      Nothing. This leak happens before any split exists, so no train/test check catches it.
    severity: silent
    detail: >-
      Region selection must happen on the pure tumor and normal, or on a held-out chromosome set,
      and the provenance of that choice is recorded and checked.
  - title: Concluding from a difference in ROC-AUC
    looks_like: >-
      A results table whose only comparison column is AUC.
    severity: silent
    detail: >-
      AUC is insensitive to calibration and to the operating point that matters, and is unstable
      under the class imbalance present at 0.01% tumor fraction. It may be reported; it may not
      be the sole basis of any accept or reject decision.
  - title: Setting a threshold after seeing the result
    looks_like: >-
      An acceptance condition that the observed value happens to meet exactly.
    severity: loud
    detail: >-
      Every threshold in the experiment config is null by default and the runner refuses to
      execute rather than substituting a value. A threshold chosen after the fact turns an
      exploratory result into a false confirmatory one.
pending_experiments:
  - title: H1 — joint-molecule feasibility across the dilution series
    blocked_on: >-
      Haplotagging has not been run; longphase is not on PATH; and the H1 acceptance thresholds
      in config/experiments/h1_feasibility.yaml are still null.
    experiment: EXP-H1-001
  - title: H2 — within-haplotype methylation separability
    blocked_on: H1 acceptance.
  - title: H3 — the A-F ablation
    blocked_on: H2 acceptance, and a pre-declared held-out chromosome set.
  - title: H4 — sample-level detection across dilutions
    blocked_on: H3 acceptance, and a frozen model and operating point.
---

## The unit of analysis

**One joint-molecule record = one read × one candidate locus.**

A read overlapping three candidate loci produces three records. The record is usable only
when the allele, the haplotype and phase-set context, and the native methylation evidence can
all be read off the *same alignment record*.

This is narrower than "one read", because a read that never overlaps a candidate carries no
allele evidence. It is narrower than "one variant", because the question is about molecules,
not sites. Choosing this unit is what makes "on the same molecule" a checkable property
rather than a figure of speech.

Records are written whether or not they are usable. Unusable ones carry the first check they
failed. That single decision is what lets the feasibility funnel be a grouping over one table
instead of a second pipeline that could quietly disagree with the first.

## Reading the funnel honestly

The stages are correlated. Read length drives both the number of CpGs on a read and the
probability that the read can be haplotagged. Multiplying the individual stage survival rates
would therefore give a number that is not the joint survival, and generally a wrong one.

Only the **observed joint count** is reported as the joint count. Stage survivals are
reported separately, each beside its denominator, and never combined.

## The ablation grid

The question is whether methylation adds evidence *after* sequence and haplotype. A single
model cannot answer that, so six are fitted, differing only in which modalities they may use.

| Model | Sequence | Haplotype | Methylation | Role |
|---|:---:|:---:|:---:|---|
| A | yes | no | no | sequence-only baseline |
| B | no | no | yes | methylation alone — is there any standalone signal? |
| C | no | yes | no | haplotype alone — controls for phasing-driven selection |
| D | yes | yes | no | **the baseline to beat** |
| E | yes | no | yes | methylation without haplotype conditioning |
| F | yes | yes | yes | the full proposal |

### Which comparison answers what

| Comparison | Question | Feeds |
|---|---|---|
| **F − D** | Does methylation add after sequence and haplotype? | H3 primary |
| **E − A** | Does methylation add over sequence alone? | H3 fallback finding |
| **D − A** | Does haplotype add over sequence alone? | Is the baseline fair? |
| **F − E** | Does haplotype *conditioning* matter, or only methylation's presence? | Earns the thesis title |

**F − E is not optional.** If F is approximately equal to E, the phrase
"haplotype-conditioned" is not earned and the framing must change. Building the comparison
into the design, before results exist, is what stops that discovery from being quietly
skipped later.

### Required controls

- **Permuted methylation.** Model F has more parameters than D, so some F − D gain is expected
  from capacity alone. Refitting F with methylation shuffled across molecules measures that
  floor; a real gain must exceed it.
- **The 0% control.** A model that detects the blank fails, regardless of its sensitivity.
- **Label shuffle.** The whole pipeline run on permuted labels must land at chance. If it does
  not, information is reaching the model through some path other than the features.

## Metrics, and why AUC is not the answer

In priority order: sensitivity at a specificity fixed before the run; precision–recall;
false-positive molecules per informative molecule; calibration; informative-molecule count;
and only then ROC-AUC.

Calibration is load-bearing rather than decorative. H4 aggregates per-molecule probabilities
into a sample-level score, and aggregating uncalibrated probabilities is not meaningful. **A
model that improves ranking while degrading calibration has not improved.**

Every rate is reported with its denominator. A metric computed on twelve molecules is
reported with the number twelve attached.

## The evaluation-only firewall

Per-read source labels are recoverable because the mixtures were built by subsampling and
merging two source BAMs, both of which preserve read names. A pilot check assigned 28 of 28
reads with zero collisions.

Those labels are **evaluation-only** and must never reach a model. Three mechanisms enforce
that rather than one:

1. The schema field is named `source_label_for_evaluation_only`, so its appearance in a
   feature path is conspicuous in code review.
2. No feature builder reads it, and the feature-name check refuses any name containing it.
3. A test asserts that two rows differing *only* in their label produce byte-identical
   feature vectors.

The nominal dilution level is treated the same way. Using the experimental condition as a
feature would be circular.

## What this design cannot deliver

Stated here, before any result exists, so it cannot be quietly claimed later:

- **No limit of blank or limit of detection** in the PAPER-006 sense. One replicate per level
  and one blank sample cannot support those estimates.
- **No clinical performance claim.** No patients, no endpoints, no outcomes.
- **No cross-sample generalisation.** One cell line, one mixture series.
- **No within-level variance.** n = 1 per dilution.

What it can deliver is a clean relative comparison between six models under matched
conditions, with the increment attributable to methylation isolated by design.

## Pivot branches

Each hypothesis has a documented pivot, so rejection produces a next step rather than a stall.

| If rejected | Pivot |
|---|---|
| **H1** | Relax the joint definition; retry phasing with other parameters or tools; restrict to high-heterozygosity regions and report reduced breadth; or write up a documented negative feasibility result. |
| **H2** | Test whether unconditioned methylation separates; test 5mC and 5hmC separately; check whether the confounder analysis over-conditioned; otherwise report a clean negative. |
| **H3** | Check E > A — methylation and haplotype may carry overlapping information, which directly supports PAPER-005's coupling argument; try richer interpretable features before concluding the signal is absent; do not jump to deep learning. |
| **H4** | Try alternative aggregation functions; report the per-molecule result as the contribution and the sample-level non-transfer as a limitation. Do not tune until significance appears. |

Two of these branches end in a negative result being written up as the thesis contribution.
That is intentional. **H3 accepted with H4 rejected is a complete and honest story**, and so
is a well-characterised demonstration that native methylation is redundant with haplotype
context at these tumor fractions.
