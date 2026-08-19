# knowledge/

Durable facts about the environment this project runs in, and the method landscape it sits
in. Written to be read before planning work, not after.

| File | Answers |
|---|---|
| [`current-state.md`](./current-state.md) | **Start here** — where the project stands, what was measured, what changed and what is still unknown |
| [`methods/method-synthesis.md`](./methods/method-synthesis.md) | What the supplied methods do, and what the field's recurring move is |
| [`ont-capabilities.md`](./ont-capabilities.md) | What this ONT data physically gives us, checked against the BAMs |
| [`datasets.md`](./datasets.md) | Every dataset on the server, its role, size and provenance |
| [`tools.md`](./tools.md) | Installed tools and versions, what is missing, compute available |
| [`constraints.md`](./constraints.md) | Rules, limits and gotchas that bound any plan |
| [`open-questions.md`](./open-questions.md) | What is not known, and what would settle it |

## Convention

Every factual line carries its evidence status:

| Marker | Meaning |
|---|---|
| `[verified 2026-08-19]` | Checked directly on this server on that date, by the command shown |
| `[repo]` | Taken from a repository document; not independently re-checked |
| `[unverified]` | Inference or external claim with no local check |

A fact without a marker is a definition or a pointer, not a claim.

## Relationship to the rest of the repository

- `research/knowledge/` holds the **research contract** — scope, hypotheses, evaluation plan,
  claim boundaries. It says what the project intends.
- `knowledge/` holds the **ground truth about the environment** — what exists, what runs,
  what is measurable. It says what the project can actually do.
- `research/` holds the **working record** — suggestions, daily logs, evidence, reports.

Where a research document and a verified entry here disagree, this directory is the one that
was checked; the disagreement is called out in place rather than silently resolved.
