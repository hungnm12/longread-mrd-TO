# outputs/

Run artifacts, sorted by what has happened to them. The directory an artifact sits in is a
claim about its status, so moving it is a decision, not tidying.

| Directory | Meaning | Who moves things here |
|---|---|---|
| `active/` | Produced by a run that is current and still being worked on | implementer |
| `accepted/` | Reviewed and cited; other records point at these paths | analyst / pi-reviewer |
| `failed/` | A run that did not complete or did not pass QC, kept with its reason | cleaner |
| `temporary/` | Scratch, QC reports, anything safe to delete once nothing references it | any agent |

## Rules

- **Nothing here is deleted while a record cites it.** Evidence records in
  `research/evidence/` reference these paths, and `scripts/validate-research-os.mjs` fails the
  build when a cited path disappears.
- Large intermediates (`joint_evidence/`, `feasibility/`, `ablation/`, per-region shards) are
  git-ignored; only small curated summaries are tracked.
- Promotion to `accepted/` requires a review verdict, not just a finished run.
