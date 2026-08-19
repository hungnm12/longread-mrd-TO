# PROJECT — tumor-only long-read MRD

The charter. What this project is trying to establish, what it is allowed to claim, and where
it currently stands. Everything else in the repository serves this file.

---

## Question

> After accounting for sequence and haplotype context, does native methylation provide
> incremental evidence for detecting tumor-derived molecules at low tumor fractions?

The load-bearing word is **incremental**: not "is methylation informative", but "is it
informative *after* sequence and haplotype have already been used". A design that cannot
separate those contributions cannot answer this.

## Current phase

**Phase 1 — tumor-only candidate characterization (descriptive).** Complete for the pure
tumor sample; evaluation design has not started. Live process state is in
[`orchestration/state.yaml`](./orchestration/state.yaml), and the dashboard state the website
reads is [`research/research-os.json`](./research/research-os.json).

## Where it stands

| | |
|---|---|
| Tumor-only candidate set | 48,819 PASS SNV candidates from 3,169,996 ClairS-TO v0.5.0 records (1.54%) |
| Native methylation in the data | present on every sampled read, 5mC and 5hmC as separate channels |
| Haplotags (`HP`/`PS`) | absent everywhere — phasing is unstarted work, not missing data |
| Dilution material | 14 BAMs at ~25×: 5 blanks, 3 replicates each at 1%, 0.1%, 0.01% |
| Experimental result | **none yet** |

The blocking measurement is the feasibility funnel: how many molecules carry allele, phase and
methylation *together* at each tumor fraction. Until that has a number, the question may be
untestable on this data — which is itself a result.

## Scope

**In:** region-scoped extraction of joint-molecule records; phasing and haplotagging;
`MM`/`ML` parsing into per-CpG evidence; feasibility counting; interpretable per-molecule
models; leakage-safe splitting; ablation across sequence / phase / methylation; detection-rate
reporting against the 0% control; provenance throughout.

**Out:** deep learning (until interpretable evidence justifies it); CNA, fragmentomics and
structural variants; clinical prediction; building a complete clinical MRD assay; any claim of
clinical MRD performance from HCC1395 genomic dilution data.

**Pending:** the project's own position in the method landscape. Its row was removed from
[`research/knowledge/methods/signal-matrix.md`](./research/knowledge/methods/signal-matrix.md)
on 2026-08-19 because one row framed it as a single idea at a single position; a scope
statement covering the full problem set must exist before it goes back in.

## What may not be claimed

- `PASS` is a caller retention label, **not** confirmed somatic truth.
- Filtered ≠ false positive. The 98.46% not retained is a selection funnel.
- VAF ≠ tumor fraction.
- High coverage in the source sample ≠ low-tumor-fraction sensitivity.
- No claim that phase or methylation improves tumor recognition before a baseline, a defined
  metric and an ablation exist.
- HCC1395 genomic dilution ≠ plasma cfDNA.

Full list with enforcement: [`research/knowledge/claim-boundaries.md`](./research/knowledge/claim-boundaries.md).

## Data rules

Source sequencing data, the reference and the dilution series are **read-only** and shared with
other users of this server. Nothing in this repository writes to them. The matched normal is an
**evaluation-only** input and may never enter a discovery or inference path. See
[`data/GOVERNANCE.md`](./data/GOVERNANCE.md).

## Open questions

Ranked, with what would settle each:
[`research/knowledge/open-questions.md`](./research/knowledge/open-questions.md).
