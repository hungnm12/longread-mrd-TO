---
id: GLOSSARY-007
term: Data leakage
short_definition: Information reaching a model that would not be available at prediction time, inflating every metric.
---

Two forms matter here.

**Correlated splitting.** Reads from one genomic region share alignment context, error modes and
phasing state. A random read-level split places correlated observations on both sides, so the model
is effectively tested on data it has seen. Splitting is therefore by chromosome, region or sample —
never by read.

**Label leakage.** The per-read tumor/normal source label is evaluation-only. It is deliberately
named `source_label_for_evaluation_only` so that its appearance in a feature path is conspicuous, and
a test asserts that two rows differing only in their label produce identical feature vectors.

Leakage does not announce itself. It presents as a suspiciously good result.
