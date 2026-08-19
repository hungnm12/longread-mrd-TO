# Repository restructured to the agent-oriented layout

Date: 2026-08-19
Status: applied
Trigger: `reconstruct_repo.md`

## Decision

The repository now follows the layout in `reconstruct_repo.md`: role definitions in
`.agents/`, procedures in `.skills/`, process state and record schemas in `orchestration/`,
research objects under `research/`, code flattened to `src/` `tests/` `scripts/` `configs/`,
artifacts under `outputs/` by status, and superseded material in `archive/`.

## Why

The previous layout was organised by *when* work happened (`week1/`, `mrd-longphase/`,
`docs/`) rather than by *what a record is*. The new one makes the workflow legible to an
agent: a stage in `orchestration/workflow.yaml` names an owner in `.agents/`, a permission
grant in `orchestration/permissions.yaml`, and a record shape in `orchestration/schemas/`.

## What moved

| From | To |
|---|---|
| `mrd-longphase/src`, `tests`, `workflow`, `config` | `src/`, `tests/`, `scripts/workflow/`, `configs/` |
| `mrd-longphase/results`, `figures`, `reports` | `outputs/active/results/`, `outputs/accepted/figures/`, `outputs/accepted/reports/` |
| `research/manifests`, `research/schemas/*.json` | `data/manifests/` |
| `knowledge/` | `research/knowledge/` (method synthesis into `methods/`) |
| `docs/research/00…06`, `decision_log` | `research/knowledge/`, `research/hypotheses/`, `research/experiments/`, `research/decisions/` |
| `docs/RESEARCH_OS.md` | `orchestration/README.md` |
| `docs/DATA_GOVERNANCE.md` | `data/GOVERNANCE.md` |
| `.agent-context/AGENTS.md` | `AGENTS.md` (rewritten) |
| `.claude/skills/` | `.skills/`, with `.claude/skills` symlinked to it |
| `legacy/`, `docs/{ARCHITECTURE,RESEARCH_SCOPE,migration_plan,repo_audit}.md` | `archive/` |

## Deviations from `reconstruct_repo.md`, and why

1. **The directory keeps its name** (`mrd/`, not `mrd-research/`). Renaming the checkout
   changes every absolute path in the user's shell history and notes for no functional gain;
   the git remote and history are unaffected either way.
2. **`site/` is kept at the root**, though the target tree does not list it. It is deployed
   and live, and it is the interface through which the records are read.
3. **`research/suggestions/` is kept**, though the target tree does not list it. The
   suggestion tracker is the professor-feedback half of the loop; dropping it would break the
   response matrix, the dashboard and the weekly report.

## Verification

`./scripts/run-tests.sh` — 113 unit + 6 integration Python tests pass; site lint, 25 vitest
tests and the production build pass; `validate-research-os` passes with all evidence paths
resolving; `scripts/build_research_deck.py` regenerates the deck at its new location; every
relative link outside `archive/` resolves.

## Revisit trigger

If a second front-end or a second analysis workspace appears, `site/` and `src/` stop being
singular and the layout needs a `packages/`-style split instead.
