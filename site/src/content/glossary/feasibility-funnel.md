---
id: GLOSSARY-009
term: Feasibility funnel
short_definition: The stage-by-stage count from all examined reads down to usable joint-evidence molecules.
---

The funnel counts how many read-candidate pairs survive each check: candidate-overlapping →
allele-informative → haplotagged → methylation-informative → usable joint molecules.

It is computed as a grouping over the joint-molecule table rather than as a second pipeline. Every
examined pair is written to that table whether or not it is usable, tagged with the **first** check
it failed, so the exclusion reasons partition the examined pairs exactly.

Stage survivals are **not** multiplied together. Read length drives both CpG count and haplotagging
probability, so the stages are correlated and the product of their rates is not the joint survival.
