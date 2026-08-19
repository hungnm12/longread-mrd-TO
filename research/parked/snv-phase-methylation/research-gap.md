# 02 — Research gap

Status: **CANDIDATE GAP — requires broader literature verification**
Date: 2026-08-16

---

## The candidate gap

> Existing provided studies do not establish whether native methylation measured on the
> same haplotagged molecule provides incremental tumor-origin evidence for tumor-only
> long-read detection at low tumor fractions.

## Why this is marked "candidate" and not "gap"

This statement is scoped to **the seven documents indexed in this project** (see
[`01_paper_patterns.md`](../../knowledge/methods/paper-patterns.md)). That is not a literature review. Three
things must happen before the word "candidate" is removed:

1. **A systematic search** covering, at minimum: long-read MRD, nanopore ctDNA, haplotype-aware
   somatic detection, read-level methylation classification, methylation-based tumor-origin
   calling, and tumor-only somatic calling.
2. **PDF-level verification** of the seven indexed papers — all currently carry
   `evidence_level: external_report` and `pdf_available: false`.
3. **An explicit negative result**: a search that *found nothing* doing this specific
   combination, documented with the queries used, not merely an absence of awareness.

Until then this is a hypothesis about the literature, and it is recorded as one.

## What each word in the gap statement is doing

| Phrase | Why it is load-bearing | If dropped |
|---|---|---|
| **native** methylation | read directly from ONT MM/ML on the same molecule, no bisulfite, no separate assay | becomes ordinary methylation-marker work, which is well covered |
| on the **same haplotagged molecule** | allele, phase, and methylation co-observed on one alignment record | becomes region-level or sample-level methylation, which is well covered |
| **incremental** | measured *after* sequence and haplotype baselines | becomes "is methylation informative", which is known to be true and therefore not a gap |
| **tumor-only** | no matched normal as an inference input | matched-normal designs have a different and easier background problem |
| **long-read** | co-observation across kilobases is what makes the joint record possible | short-read designs cannot form this unit at range |
| **at low tumor fractions** | 1% → 0.01%, where per-locus molecule counts get small | at high TF, sequence alone already works and the increment is uninteresting |

Remove any one and the gap either closes (someone has done it) or stops being a research
question. This is a useful stress test to re-run whenever the framing drifts.

## Nearest neighbours in the indexed set

| Paper | How close it gets | What it does not do |
|---|---|---|
| PAPER-006 (PhasED-Seq) | Uses **phase** to suppress background — the same structural idea | Requires *multiple variants* in phase; short-read; not tumor-only; no methylation |
| PAPER-002 (ONT consensus, multimodal) | Long-read, multimodal, cfDNA | Multimodality is SNV + CNA; not per-molecule methylation conditioned on haplotype |
| PAPER-003 (cfDNA methylation profiling) | Native methylation as a signal class | Profiling/protocol guidance; not per-molecule tumor-origin inference |
| PAPER-005 (methylation–fragmentation) | Methylation as tumor-informative and its coupling to other signals | Fragmentation, not allele/haplotype; population-level, not per-molecule |
| PAPER-007 (ML signal enrichment) | Learned enrichment of tumor-like signal | Plasma, short-read framing; modality set does not include native methylation on haplotagged molecules |

PAPER-006 is the closest. The thesis's distinguishing claim relative to it is stated in
[`01_paper_patterns.md`](../../knowledge/methods/paper-patterns.md#position-2--background-suppression):
PhasED-Seq needs *two or more variants in phase*, which becomes unavailable exactly when
tumor fraction is low enough to matter; this project asks whether *methylation conditioned
on haplotype context* can play the same background-suppressing role with a single variant.

## Risks to the gap

| Risk | Consequence | Mitigation |
|---|---|---|
| A broader search finds this already done | The gap closes | Do the search early (see next action) — before Phase 5 model work, not after |
| Methylation turns out to be redundant with haplotype context | H3 rejects; the gap is real but the answer is "no" | This is a valid, publishable result. The ablation design produces it cleanly |
| Too few joint molecules exist at 0.01% | H1 fails; the question is unanswerable on this data | Feasibility funnel runs first, before any modelling (Phase 4) |
| HCC1395 dilution is not a valid proxy for the setting of interest | External validity limited | Already bounded in [`05_claim_boundaries.md`](../../knowledge/claim-boundaries.md) |

## Next action on this document

Run a documented literature search and record the queries, databases, date, and results in
[`decision_log.md`](../../decisions/decision-log.md). Until that entry exists, every downstream document
must keep describing this as a **candidate** gap.
