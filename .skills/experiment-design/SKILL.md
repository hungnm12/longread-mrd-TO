---
name: experiment-design
description: Turn an accepted idea into an executable experiment specification with fixed thresholds, controls and falsification criteria. Use when the user says "design the experiment", "how would we test this", or before any run starts.
---

# Experiment design

Write the specification that execution will follow exactly.

## Steps

1. Read the idea, the hypothesis it serves (`research/hypotheses/`), and the constraints
   (`research/knowledge/constraints.md`, `datasets.md`, `tools.md`).
2. Fill `orchestration/schemas/experiment.schema.yaml` into
   `research/experiments/registry/EXP-<id>.yaml`:
   - **unit of analysis** — what one row of the result is;
   - **inputs** with paths and `read_only: true` for every source path;
   - **thresholds** — set now, or explicitly `null` so the runner blocks rather than defaults;
   - **success and failure criteria** — both, before results exist;
   - **controls** — the blank, the ablation, the negative case;
   - **leakage guard** — how the normal BAM and truth sets stay out of inference.
3. State the cheapest version that would still answer the question, and prefer it.
4. Hand to `data-qc` before execution.

## Rules

- A threshold chosen after seeing results turns an exploratory finding into a false
  confirmatory one. Fix them in the file, with the reasoning in `research/decisions/`.
- Every design names what result would make it abandon the hypothesis.
- Region-scoped and resumable by default; a whole-genome pass needs a written reason.
- Evaluation-only data (`HCC1395BL.bam`, SEQC2, orthogonal benchmark) may appear in the
  evaluation section only, never as an input.
