# Research Scope

> **Superseded as the primary storyline (2026-08-16).** The project's main direction is now
> *tumor-only long-read MRD through haplotype-conditioned native methylation evidence* —
> see [`research/00_scope.md`](../research/knowledge/scope.md).
>
> Everything below remains accurate and is retained as the **upstream baseline**: it
> describes the tumor-only candidate characterization that supplies the candidate loci the
> new pipeline iterates over. The scientific guardrails in this document still apply.

## Canonical direction

- Topic: long-read MRD research.
- Starting point: reproduce and analyze concepts from "Genome-wide cell-free DNA mutational integration enables ultra-sensitive cancer monitoring."
- Current workstream: tumor-only HCC1395 candidate characterization.
- Intended discovery direction: tumor-only first, without making matched normal a prerequisite.

## Current Week 1 boundary

The active Week 1 question is:

> What does the tumor-only candidate landscape look like, and which evidence is sufficient to promote a candidate into a reliable tumor marker without matched-normal dependency at discovery time?

Week 1 deliverables stay descriptive:

- total candidates versus PASS SNVs
- VAF distribution
- read-depth distribution
- ALT-support distribution
- filter/tag composition
- interpretation boundaries and open questions

High-VAF interpretation is explicitly deferred; it may become a later open question about clonal somatic signal, residual germline, LOH/CNA, or technical effects.

## Scientific guardrails

- PASS SNV does not mean true somatic variant.
- Filtered candidates do not automatically mean false positives.
- VAF is not tumor fraction.
- High coverage in the source tumor sample does not prove low-tumor-fraction sensitivity.
- Tumor-only discovery does not prohibit later retrospective validation with matched normal or truth data.

## Seed evidence already present locally

- `mrd-longphase/results/tumor_only/HCC1395/variant_summary.tsv`
- `mrd-longphase/results/tumor_only/HCC1395/qc_stats.txt`
- `mrd-longphase/results/tumor_only/HCC1395/candidate_analysis.tsv`
- `mrd-longphase/reports/weekly/2026-08-13_hcc1395_phase1_tumor_only.md`

These files provide the current descriptive baseline and should be labeled `preliminary` until cross-checked against execution manifests and upstream run logs where needed.
