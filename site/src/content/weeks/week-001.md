---
id: WEEK-001
title: Tumor-only candidate landscape
period: "2026-W33"
status: observed
research_questions: [RQ-001]
hypotheses: [HYP-001]
experiments: [EXP-001]
results: [RESULT-001]
decisions: [DEC-001]
evidence_level: preliminary
last_verified: null
blockers:
  - The full ClairS-TO model name still needs confirmation from the execution manifest or log.
  - The current week remains descriptive and does not yet score marker reliability.
next_decision: Define an evidence ladder for tumor-only marker reliability without depending on matched normal at discovery time.
readiness:
  - Research question is explicit.
  - Observation and interpretation are separated.
  - Provenance is linked to local outputs.
  - Caveats are visible on the weekly page.
---

## One-sentence research question

What does the tumor-only PASS SNV candidate landscape look like before any somatic interpretation?

## Why this matters to thesis and MRD

The retained candidate population is the substrate for later tumor-only marker qualification. If
its denominator, support range, and interpretation boundaries are unclear, later reliability or
dilution work becomes difficult to defend.

## Prior knowledge from papers

Breadth-over-depth thinking and phased or multimodal aggregation make later MRD detection
possible, but none of those later modules remove the need for a trustworthy baseline retained
population. Week 1 therefore focuses on describing the candidate landscape rather than claiming
biological truth.

## Hypothesis and prediction before analysis

PASS plus reasonable depth and ALT support should narrow technical noise enough to create a useful
analysis population, but those features alone should still be insufficient to separate somatic,
germline, and artifact classes.

## Dataset and configuration

- Tumor-only HCC1395 ONT data
- GRCh38 no-alt reference
- ClairS-TO tumor-only SNV output summarized from local repository artifacts
- Public-facing pages intentionally redact absolute server paths

## What the evidence does not establish

- It does not prove that PASS variants are somatic.
- It does not estimate false-positive rate for filtered calls.
- It does not prove sensitivity at low tumor fractions.

## Failure, uncertainty, blocker

- The exact full model name must still be verified from the run log.
- The current evidence is caller-derived and descriptive only.
- High-VAF interpretation remains an open question for later work rather than the main Week 1 story.

## Decision and next smallest test

Preserve the descriptive Week 1 baseline and move next into a feature ladder for marker reliability
instead of high-VAF storytelling or filtered-call rescue.

## Speaker notes

Emphasize that Week 1 is about defining the retained analysis population, not proving somatic
truth. The most important message is the boundary between useful descriptive evidence and stronger
claims that still require more validation work.
