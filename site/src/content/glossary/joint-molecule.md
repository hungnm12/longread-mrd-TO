---
id: GLOSSARY-002
term: Joint molecule
short_definition: One read at one candidate locus, carrying allele, haplotype and methylation evidence together.
---

A **joint molecule** is the unit of analysis for this thesis: one read paired with one candidate
locus, where the observed allele, the haplotype and phase-set context, and the native methylation
evidence can all be read off the *same* alignment record.

It is narrower than "one read" — a read that overlaps no candidate carries no allele evidence — and
narrower than "one variant", because the question is about molecules rather than sites. Choosing
this unit is what makes "on the same molecule" a checkable property rather than a figure of speech.

A read overlapping three candidates produces three joint-molecule records.
