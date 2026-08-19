---
name: code-review
description: Review analysis code against its experiment specification, with leakage and provenance checked first. Use when the user asks for a code review, or before results from new code are trusted.
---

# Code review

## Order of checks

1. **Leakage.** Does any inference path read `HCC1395BL.bam`, a truth VCF, or a label field?
   `source_label_for_evaluation_only` may reach evaluation only. Two rows differing only in
   label must produce identical features.
2. **Spec fidelity.** Does the code compute what `research/experiments/registry/<id>.yaml`
   specifies — same unit of analysis, same thresholds, same controls?
3. **Failure behaviour.** Does it stop on a missing threshold, or default silently? Defaults
   are unrecorded research decisions.
4. **Determinism and provenance.** Seeds recorded, versions captured, re-run reproducible,
   resumable where the spec says so.
5. **Correctness**, then **simplicity**.

## Output

Findings as `file:line`, each with the concrete failure it would cause. Write them to
`orchestration/queue/` for the implementer.

## Rules

- Report; do not silently fix.
- No test may read a real BAM — fixtures only (`tests/fixtures/`).
- Flag any write to a path under `/big8_disk/` or `/bip7_disk/` as blocking, without exception.
