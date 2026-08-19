# Tumor-only long-read MRD — research workspace

**Status: between directions.** The tumor-only candidate landscape is characterized and stands.
The direction built on it — SNV candidates combined with haplotype phase and native methylation
— was parked on 2026-08-19 and lives, intact, in
[`research/parked/snv-phase-methylation/`](./research/parked/snv-phase-methylation). The
project's full problem set is being written down before another direction is adopted.

Start with [`PROJECT.md`](./PROJECT.md) — charter, current phase, and what may not be claimed.
Then [`AGENTS.md`](./AGENTS.md) if you are an agent working in this repository.

---

## Layout

| Path | What it is |
|---|---|
| [`PROJECT.md`](./PROJECT.md) | The charter: question, phase, scope, claim boundaries |
| [`AGENTS.md`](./AGENTS.md) | Operating rules for anything working in this repository |
| [`.agents/`](./.agents) | Role definitions — orchestrator, analyst, data-qc, pi-reviewer, … |
| [`.skills/`](./.skills) | Invocable procedures — brainstorm, experiment-design, data-qc, grill-me, … (`.claude/skills` symlinks here) |
| [`orchestration/`](./orchestration) | How work moves: `workflow.yaml`, `permissions.yaml`, `state.yaml`, record `schemas/`, handoff `queue/` |
| [`research/`](./research) | The research itself — `knowledge/`, `ideas/`, `hypotheses/`, `experiments/`, `evidence/`, `findings/`, `decisions/`, `suggestions/`, `daily-logs/`, `weekly-reports/` |
| `src/` | Analysis library — candidates, phasing, methylation, joint evidence, models, evaluation |
| `scripts/` | Runnable entry points: `workflow/`, `run-tests.sh`, `run-site.sh`, `build_research_deck.py` |
| `tests/` | Unit and integration tests, all against synthetic fixtures |
| `configs/` | Dataset and experiment configuration; thresholds stay `null` until deliberately set |
| [`data/`](./data) | Manifests, metadata and governance — **no bulk data** |
| [`outputs/`](./outputs) | Run artifacts by status: `active/`, `accepted/`, `failed/`, `temporary/` |
| `site/` | The Astro research site and record viewer, deployed to Cloudflare |
| `archive/` | Superseded work, kept with its context |

## Where things stand

| | |
|---|---|
| Tumor-only candidates | 48,819 PASS SNVs from 3,169,996 ClairS-TO v0.5.0 records (1.54%) |
| Native methylation | present on every sampled read; 5mC and 5hmC as separate channels |
| Haplotags (`HP`/`PS`) | absent — phasing is unstarted work, not missing data |
| Dilution material | 14 BAMs at ~25×: 5 blanks + 3 replicates each at 1%, 0.1%, 0.01% |
| Experimental result | **none yet** |

What is blocking is a definition, not a measurement: the project's problem set. See
[`orchestration/state.yaml`](./orchestration/state.yaml).

## Commands

```bash
# checks
./scripts/run-tests.sh              # python unit + integration, then site lint and tests
./scripts/run-tests.sh python       # 113 unit + 6 integration, synthetic fixtures only
cd site && npm run lint             # astro check + content + research-record validation

# the record store
cd site && npm run new:log -- 2026-08-20
cd site && npm run new:suggestion -- "..."
cd site && npm run new:evidence -- "..."
cd site && npm run validate:research

# the site and the report
./scripts/run-site.sh dev           # or: build | preview | check | test
cd site && npm run deploy           # rebuild + publish to Cloudflare
python3 scripts/build_research_deck.py   # → outputs/accepted/mrd-research-report.pptx
```

Environment check before any run:

```bash
python3 scripts/workflow/tools/report_environment.py \
    --check-data configs/datasets/hcc1395_dilution.yaml
```

Python dependencies: `pip install -r requirements.txt`. No GPU on this host — see
[`research/knowledge/tools.md`](./research/knowledge/tools.md).

## The loop

```text
professor feedback → planned response → daily work → evidence → observation
→ interpretation → research decision → next commitment → weekly report
```

Stages, owners and exit conditions: [`orchestration/workflow.yaml`](./orchestration/workflow.yaml).
The daily and weekly procedure: [`orchestration/README.md`](./orchestration/README.md).

## Rules that are enforced, not merely stated

| Rule | Enforcement |
|---|---|
| Source data is read-only | Nothing opens a source path for writing; `.gitignore` blocks bulk formats; `orchestration/permissions.yaml` denies writes per agent |
| Evaluation labels never reach a model | The field is named `source_label_for_evaluation_only`; a test asserts two rows differing only in label produce identical features |
| No leakage across splits | Splitting is by chromosome, region or sample; a test asserts no region spans a split |
| No undefined threshold silently defaults | `ExtractionConfig.from_dict` raises; the funnel reports `BLOCKED` |
| Work is not "done" without evidence | `site/scripts/validate-research-os.mjs` rejects a completed record with no artifact and no written reason |
| Missing evidence is shown, not hidden | Dashboard, response matrix and deck render explicit gap labels |
| Evidence is not "verified" because an AI read it | `verified` requires `verified_by` and `verified_on` |
| No fabricated results | `actual_results` stays `null` until a run produces numbers |
| 5mC and 5hmC stay separate | Separate schema columns, separate features, never summed |
