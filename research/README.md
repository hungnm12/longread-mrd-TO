# research/

The research itself: what is known, what is proposed, what was run, and what it means.

| Directory | Holds | Schema |
|---|---|---|
| `knowledge/` | What exists — environment survey, dataset inventory, method synthesis, scope, gap, claim boundaries, open questions | — |
| `ideas/` | Proposals not yet earning an experiment | `idea.schema.yaml` |
| `hypotheses/` | Falsifiable statements the project tests | — |
| `experiments/` | Specifications, registry and templates | `experiment.schema.yaml` |
| `evidence/` | Artifacts with provenance and verification status | `record-shapes.md` |
| `findings/` | Observation and interpretation, kept apart | `analysis.schema.yaml` |
| `decisions/` | What changed, why, and the revisit trigger | — |
| `suggestions/` | Professor and lab feedback, answered point by point | `record-shapes.md` |
| `daily-logs/` | One record per working day | `record-shapes.md` |
| `weekly-reports/` | Compiled meeting reports | `record-shapes.md` |
| `research-os.json` | Dashboard state the website reads | — |

Schemas live in [`../orchestration/schemas/`](../orchestration/schemas). The stage each record
type belongs to is defined in [`../orchestration/workflow.yaml`](../orchestration/workflow.yaml).

Records are append-only in spirit: a wrong entry is corrected by a new entry, not by rewriting
the old one.
