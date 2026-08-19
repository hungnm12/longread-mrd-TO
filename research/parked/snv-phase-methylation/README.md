# PARKED — SNV combined with haplotype phase and native methylation

Parked: 2026-08-19. Nothing here is retracted or wrong; it is set aside.

## What is parked

The direction that framed the project as: *take tumor-only SNV candidates, add haplotype phase
and native methylation read off the same molecule, and test whether that combination improves
recognition of tumor-derived molecules at low tumor fraction.*

| Document | What it holds |
|---|---|
| `scope.md` | The scope contract written around that direction — inputs, unit of analysis, in/out of scope |
| `hypotheses.md` | H1–H4 for the haplotype-conditioned methylation design |
| `research-gap.md` | The candidate gap statement, scoped to the seven supplied documents |
| `evaluation-plan.md` | The ablation and evaluation design for that combination |
| `EXP-H1-001.yaml` | The registered feasibility experiment (joint-molecule counting) |

## Why

The direction is one idea at one position in the method landscape: per-molecule background
suppression, for the single-variant tumor-only case. The project is expected to address a
broader problem set than that, and while a single direction sits in the active state files it
shapes every question asked around it. Parking it clears the room to state the wider scope
first.

This is the same reason the project's row was pulled from
[`../../knowledge/methods/signal-matrix.md`](../../knowledge/methods/signal-matrix.md) earlier
the same day.

## What stays active

Nothing here invalidates the descriptive work already done, which is direction-independent:

- the tumor-only candidate landscape — 48,819 PASS SNVs of 3,169,996 records, with its
  distributions;
- the environment survey in [`../../knowledge/`](../../knowledge) — datasets, tools, ONT
  capabilities, constraints;
- the method synthesis over the supplied literature;
- the open question of candidate **composition** (`SUG-2026-08-001`), which any direction needs.

## What would resume it

1. A scope statement covering the project's full problem set exists, and this direction is
   shown to be part of it rather than the whole of it.
2. The composition question has an answer, so "recognition" has something to recognise.
3. A definition of the evaluation metric exists that does not presuppose this design.

Resuming means moving these files back to `research/hypotheses/`, `research/knowledge/` and
`research/experiments/`, and restoring the entries in `orchestration/state.yaml` and
`research/research-os.json`.

## Related records

- `SUG-2026-08-002`, `SUG-2026-08-003`, `SUG-2026-08-004` — marked `not_pursued` on 2026-08-19
  with this as the reason.
- `research/decisions/2026-08-19-park-direction.md` — the decision record.
- The website's research narrative at `/research-narrative/` still presents this argument and
  carries a parked banner; it is kept as a record of the reasoning, not as a current position.
