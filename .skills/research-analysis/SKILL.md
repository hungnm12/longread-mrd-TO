---
name: research-analysis
description: Turn run output into a finding with observation and interpretation kept separate, evidence registered, and limits stated. Use after an experiment produces output, or when the user asks "what does this result mean".
---

# Research analysis

## Steps

1. **Register the artifacts** as evidence records (`research/evidence/EV-NNNN.yaml`): path,
   generator, inputs, linked log, verification status. `file_present` means the path exists and
   nothing more. Never `verified` — that needs a named person and a date.
2. **Write the observation.** What the artifact shows, in neutral terms, with its denominator.
   No causal language, no "improves", no "confirms".
3. **Write the interpretation, separately.** What it is taken to mean, and — required — what it
   does *not* show.
4. **Name the rival explanation** and what would distinguish it. If nothing would, say so.
5. Write the finding to `research/findings/FIND-NNNN.md`
   (`orchestration/schemas/analysis.schema.yaml`) and hand it to review.

## Rules

- A null or negative result is written up with the same care as a positive one.
- No comparison of numbers across incompatible assays, samples or cohorts.
- Keep the guardrails true in every sentence: PASS is a caller retention label, filtered is not
  a false positive, VAF is not tumor fraction, source coverage is not low-TF sensitivity.
- If the analysis contradicts an earlier finding, cite it in `contradicts` rather than quietly
  replacing it.
