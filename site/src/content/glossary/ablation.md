---
id: GLOSSARY-006
term: Ablation
short_definition: Fitting the same task with modalities deliberately removed, to isolate what each one contributes.
---

An ablation study answers "does X add anything?" by fitting one model with X and one without,
holding everything else fixed. It is the only design that can answer an **incremental** question.

This project fits six models (A-F) over three modalities — sequence, haplotype, methylation. The
decisive comparison is **F − D**: the full model against sequence-plus-haplotype. A design that
simply added methylation features and reported an improved score could not distinguish real
contribution from added model capacity, which is why a permuted-methylation control is also fitted.
