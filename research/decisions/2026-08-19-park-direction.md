# Park the SNV + haplotype phase + native methylation direction

Date: 2026-08-19
Status: applied
Decided by: researcher

## Decision

The direction combining tumor-only SNV candidates with haplotype phase and native methylation
on the same molecule is **parked**, and cleared out of the repository's active state.

## Why

It is one idea at one position in the method landscape — per-molecule background suppression
for the single-variant tumor-only case. The project is expected to address a broader problem
set. While a single direction occupies the active state files, every question asked gets shaped
around it, which is how the scope narrowed in the first place.

Parked, not retracted: the argument may well be right, and it is intact.

## What changed

| Where | Before | After |
|---|---|---|
| `research/parked/snv-phase-methylation/` | — | scope contract, hypotheses, gap statement, evaluation plan, `EXP-H1-001`, and a README with resume conditions |
| `orchestration/state.yaml` | Blocking question was the feasibility funnel | `parked_directions` entry; blocking question is now the project's problem set; next action reserved for the researcher |
| `research/research-os.json` | Question and hypothesis were the parked ones | Broad question, no active hypothesis, issues rewritten to the direction-independent ones |
| `SUG-2026-08-002/003/004` | open | `not_pursued`, with the parking as the recorded reason |
| `PROJECT.md`, `README.md` | Led with the parked question | Lead with the parked state and what still stands |
| `research/knowledge/open-questions.md` | Section A was the blocking set | Section A and B2–B5 marked parked; A1, B1, C, D stand |
| Site `/research-narrative/` | Presented as the current position | Carries a parked banner; kept as a record |

## What still stands

The descriptive tumor-only candidate landscape (48,819 PASS SNVs of 3,169,996 records and its
distributions), the environment survey in `research/knowledge/`, the method synthesis over the
supplied literature, and the composition question `SUG-2026-08-001` — none of which depend on
the parked direction.

## Revisit trigger

A scope statement covering the project's full problem set exists, and this direction is shown to
be part of it rather than the whole of it. Resuming is a file move plus restoring two state
entries; the README in the parked directory says exactly which.
