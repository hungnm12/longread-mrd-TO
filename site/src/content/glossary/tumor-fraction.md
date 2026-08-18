---
id: GLOSSARY-005
term: Tumor fraction
short_definition: The proportion of molecules in a sample that are tumor-derived. Not the same as VAF.
---

Tumor fraction is a property of the **sample**: what share of its molecules came from tumor cells.
Variant allele fraction is a property of a **locus**: what share of reads there carry the variant.

They differ because a somatic variant may sit on one chromosome copy of a region present at varying
copy number, so VAF at a heterozygous somatic site in a pure tumor is typically near 0.5, not 1.0.

In this project the dilution levels — 1%, 0.1%, 0.01% — are **nominal mixing ratios**. The realized
tumor fraction in each BAM has not been independently measured, and every result derived from them
carries that caveat.
