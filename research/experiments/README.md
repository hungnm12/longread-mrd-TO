# Experiment registry

Every experiment has **two** files:

| File | Purpose |
|---|---|
| `registry/<EXP-ID>.yaml` | machine-readable manifest — the contract, pre-registered |
| `registry/<EXP-ID>.md` | short human report — what happened |

Templates live in `templates/`.

## The pre-registration rule

The manifest's **pre-run block** — including `acceptance_condition`, `rejection_condition`,
`expected_outcomes` and `split` — is completed **before** the experiment runs.
`actual_results`, `uncertainties` and `decision` stay `null` until it has finished.

This is not bureaucracy. It is the discipline the project already demonstrated in
`reports/weekly/2026-08-10_phase0_caller_and_detection_validation.md`, where thresholds were
locked first (precision ≥ 0.90, recall ≥ 0.80, F1 ≥ 0.85) and the result was then reported
as an honest failure (0.707 / 0.732 / 0.719). A threshold chosen after seeing results makes
a confirmatory claim out of an exploratory one, and
[`../../research/knowledge/claim-boundaries.md`](../../research/knowledge/claim-boundaries.md)
prohibits it.

## ID scheme

```
EXP-<HYPOTHESIS>-<NNN>        EXP-H1-001, EXP-H3-002
```

IDs are stable and never reused. A re-run with different parameters gets a new ID and
references the old one in `method`.

## Decisions

| Decision | Meaning |
|---|---|
| `ACCEPT` | acceptance condition met; proceed to the next gated hypothesis |
| `REJECT` | rejection condition met; take a documented pivot |
| `PARTIAL` | some strata accept, others reject — state which and why |
| `BLOCKED` | could not run or could not be decided (missing tool, undefined threshold, insufficient data). **Not** a soft rejection |
| `INCONCLUSIVE` | ran, but does not discriminate — usually too few molecules. Record the `n` that would have been needed |

`BLOCKED` and `INCONCLUSIVE` are distinct on purpose. Collapsing them hides whether the
problem is the setup or the data.

## Relationship to the site

`site/src/content/experiments/` holds the public-facing version of the same objects, with
zod-validated frontmatter and the shared `evidence_state` / `evidence_level` enums. The
registry here is the source of truth; site content mirrors it for reading. Keep the IDs
identical so the two can be joined.

## Current registry

| ID | Hypothesis | Status | Decision |
|---|---|---|---|
| `EXP-H1-001` | H1 | planned | — |

`EXP-H1-001` is **blocked** on haplotagging: no BAM in this project carries HP/PS
([`../../docs/repo_audit.md`](../../archive/repo_audit.md) §14.3), and its acceptance
thresholds are still `null` in `config/experiments/h1_feasibility.yaml` and must be set
before it runs.
