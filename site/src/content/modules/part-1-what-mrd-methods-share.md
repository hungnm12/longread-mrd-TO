---
id: MODULE-001
part: 1
title: What existing MRD methods have in common
subtitle: Every method for detecting rare tumor molecules solves the same five problems in the same order.
status: observed
evidence_level: external_report
reading_time_minutes: 12
learning_objectives:
  - Describe the five-stage pipeline that every minimal-residual-disease method follows, regardless of assay chemistry.
  - Explain why breadth of observation, rather than depth at a few sites, is the dominant strategy at low tumor fractions.
  - Distinguish background suppression from signal extraction, and say why they are separate problems.
  - State why analytical validation (limit of blank, limit of detection) is a stage in its own right and not a formality.
why_it_matters: >-
  Reading MRD papers one at a time produces a list of unrelated assays. Reading them by
  pipeline position shows that they are variations on one design, differing mainly in what
  they measure per molecule and how they suppress background. Once the shared structure is
  visible, a new method can be located precisely — and so can a gap.
prerequisites: []
previous_module: null
next_module: MODULE-002
interpretation_boundaries:
  - This module summarises method structure, not results. No performance figure from any cited work is reproduced here.
  - All seven indexed sources carry evidence_level "external_report" and have not been verified against their source PDFs, so no numeric claim is made from them.
  - The five-stage framing is an organising device chosen for this thesis, not a taxonomy taken from any single paper.
  - Describing methods as similar in structure does not imply they are interchangeable in performance or in clinical validity.
open_questions:
  - Does the five-stage framing survive contact with methods outside the seven indexed documents?
  - At what tumor fraction does breadth stop compensating for weak per-molecule evidence?
  - How much of each method's performance comes from background suppression versus from signal extraction? The published reports rarely separate them.
questions: []
hypotheses: []
papers:
  - PAPER-001
  - PAPER-002
  - PAPER-004
  - PAPER-006
  - PAPER-007
glossary_terms:
  - GLOSSARY-005
  - GLOSSARY-008
  - GLOSSARY-001
sources:
  - label: "PAPER-001 — Genome-wide cell-free DNA mutational integration"
    ref: PAPER-001
    note: breadth-over-depth; genome-wide integration of weak per-site evidence
  - label: "PAPER-002 — Nanopore consensus sequencing for multimodal cfDNA profiling"
    ref: PAPER-002
    note: long-read multimodal signal extraction
  - label: "PAPER-004 — Real-time cancer genome and fragmentome from cfDNA by nanopore"
    ref: PAPER-004
    note: native fragmentomics; ONT deployability
  - label: "PAPER-006 — Analytical validation of a ctDNA assay using PhasED-Seq"
    ref: PAPER-006
    note: phased multi-variant background suppression; LoB/LoD framework
  - label: "PAPER-007 — Ultrasensitive plasma monitoring with ML-guided signal enrichment"
    ref: PAPER-007
    note: learned enrichment of tumor-like signal
diagram:
  title: The five stages every MRD method passes through
  caption: >-
    Assays differ in what they measure and how they suppress background, not in the order of
    these stages. Stage 2 is where this thesis makes its contribution.
  orientation: vertical
  stages:
    - label: Rare tumor molecules
      note: at 0.01% tumor fraction, a handful of molecules per locus at best
    - label: Signal extraction
      note: what is measured off each molecule — allele, fragment, methylation
    - label: Background suppression
      note: preventing non-tumor molecules from looking tumor-like
      emphasis: true
    - label: Evidence aggregation
      note: combining weak per-molecule evidence across many loci
    - label: Sample-level score
      note: one number per sample, compared against a blank
    - label: LoB / LoD / specificity validation
      note: bounding what the number is allowed to claim
failure_modes:
  - title: Reading breadth-over-depth as "more data is better"
    looks_like: >-
      A plan that proposes deeper sequencing at the same loci and expects the same gain that
      genome-wide breadth delivers.
    severity: silent
    detail: >-
      Breadth works because independent weak observations accumulate. Depth at one locus
      accumulates correlated observations of the same molecule population, including its
      systematic errors, so it saturates far earlier.
  - title: Treating background suppression as a filtering step
    looks_like: >-
      A pipeline where "remove artifacts" is one filter near the end, with a threshold tuned
      until the numbers look reasonable.
    severity: silent
    detail: >-
      In every method surveyed, background suppression is structural — a property of what
      counts as evidence — not a threshold applied afterwards. PhasED-Seq requires multiple
      variants in phase; population panels require absence from known germline. These change
      what a positive observation is.
  - title: Reporting a sample-level score without a blank
    looks_like: >-
      A detection claim with no 0% control, or with a control that was run under different
      conditions from the samples.
    severity: loud
predictions: []
pending_experiments: []
---

## The problem every method starts from

At a tumor fraction of 1%, roughly one molecule in a hundred at any given locus carries
tumor-derived sequence. At 0.01%, it is one in ten thousand. Sequencing error rates on any
platform are comfortably above that. A single observation of a variant allele is therefore
not evidence of anything: it is far more likely to be an error than a tumor molecule.

Every method in this literature exists to solve that one problem, and they all attack it in
the same order.

## Stage 1 — Signal extraction

The first question is what can be measured off a molecule at all.

The dominant answer across these papers is **breadth**. Rather than measuring a few loci
very carefully, observe very many loci shallowly and integrate. PAPER-001 is the
reference point for this reasoning: if each site carries weak evidence, the useful quantity
is the aggregate over thousands of sites, not the confidence at any one of them.

Long-read platforms change what is available at this stage. PAPER-002 uses nanopore
consensus sequencing to raise per-molecule confidence; PAPER-004 shows that fragment-level
properties come off the same native molecule with no separate assay. Native base
modifications belong in the same category — they are read from the molecule as sequenced,
not from a second, chemically-converted library.

This is the structural fact this thesis builds on: **a long read carries several
independent-looking kinds of evidence about the same physical molecule.**

## Stage 2 — Background suppression

The second question is how to stop non-tumor molecules from looking tumor-like. This is a
different problem from stage 1, and conflating the two is the most common conceptual error
in this area.

Two strategies appear repeatedly:

**Population-level exclusion.** Remove anything that looks germline or recurrent, using
population databases and panels of normals. This is what tumor-only somatic callers do, and
it is what the upstream ClairS-TO step in this project already does.

**Within-molecule consistency.** Require that several things be simultaneously true *on one
molecule*. PAPER-006 is the clearest example: PhasED-Seq requires multiple mutations to
appear **in phase** on the same fragment. Because independent sequencing errors rarely
co-occur in phase, the background suppression is multiplicative rather than additive.

The second strategy is much stronger, and it is where the interesting design space is.

### The limit of the phasing strategy

Requiring two or more variants in phase works when a molecule is likely to carry two or
more variants. As tumor fraction falls, the number of tumor-derived molecules at any locus
falls with it, and the chance that one molecule carries two informative variants falls
faster still. The strategy weakens exactly where it is most needed.

That observation is the opening this thesis works in, and Part 2 develops it.

## Stage 3 — Evidence aggregation

Per-molecule evidence must become per-sample evidence. PAPER-001 and PAPER-007 both
integrate across many weak sites; PAPER-002 and PAPER-007 combine signal classes.

PAPER-005 supplies the essential warning here: methylation and fragmentation are
**biologically coupled**, not independent. Combining coupled signals as though they were
independent overstates confidence, because the second signal is partly a restatement of the
first. This is the reason the evaluation design in this project is built on ablation rather
than on adding features and reporting an improved score.

## Stage 4 — Sample-level score

One number per sample, compared against a background distribution. The methodological
requirement is that the comparison be against a *measured* blank, not an assumed one.

## Stage 5 — Analytical validation

PAPER-006 provides the vocabulary: limit of blank, limit of detection, precision, dilution
series, background error modelling. This stage is what separates a signal that exists from
a signal that can be relied on.

It is worth being explicit that **this thesis does not reach stage 5**. With one replicate
per dilution level and a single blank sample, limit of detection in this sense is not
estimable. Part 3 states what the dilution series can and cannot support.

## Where each paper sits

| Stage | Papers that address it |
|---|---|
| Signal extraction | PAPER-001 (breadth), PAPER-002 (consensus), PAPER-004 (fragmentomics) |
| Background suppression | PAPER-006 (phasing), PAPER-007 (ML enrichment) |
| Evidence aggregation | PAPER-001, PAPER-002, PAPER-007, PAPER-005 (coupling warning) |
| Sample-level score | PAPER-001, PAPER-007 |
| Validation | PAPER-006 |

Read this way, the seven documents stop being seven topics and become one pipeline with
five well-populated stages — and one cell that Part 2 argues is empty.
