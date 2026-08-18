# Research OS record shapes

The enforced definitions live in `site/src/content.config.ts` (shape) and
`site/scripts/validate-research-os.mjs` (cross-record rules). This file is the human-readable
copy the AI skills work from. If they disagree, the code wins.

Ids are the only linking mechanism. Nothing references another record by file path.

| Record | Directory | Format | Id |
|---|---|---|---|
| Suggestion | `research/suggestions/` | YAML | `SUG-YYYY-MM-NNN` |
| Daily log | `research/daily-logs/` | Markdown + frontmatter | `LOG-YYYY-MM-DD` |
| Evidence | `research/evidence/` | YAML | `EV-NNNN` |
| Weekly report | `research/weekly-reports/` | Markdown + frontmatter | `WR-YYYY-Www` |

Dashboard state lives in `research/research-os.json`.

## Suggestion

```yaml
id: SUG-2026-08-001
meeting_date: 2026-08-15        # null if not from a recorded meeting
source: Professor, weekly meeting
record_kind: recorded           # recorded | real | seeded_context | template
suggestion: What was said
my_interpretation: What I understand it to mean
why_it_matters: What changes if it is ignored
planned_actions:
  - action: What I will do
    expected_evidence: The artifact that would show it was done
    status: planned             # planned | in_progress | completed | dropped
status: captured                # captured | planned | in_progress | completed | blocked | not_pursued
linked_daily_logs: [LOG-2026-08-17]
evidence: [EV-0001]
result: null                    # required (with evidence) once status is completed
reason_not_completed: null      # required while not completed, and for blocked/not_pursued
next_action: The next concrete step
target_week: 2026-W34
```

## Daily log

```yaml
id: LOG-2026-08-17
date: 2026-08-17
record_kind: real
research_question: The question this day's work serves
linked_suggestions: [SUG-2026-08-001]
planned_work: [...]
actions_completed:
  - action: What was performed
    evidence: [EV-0001]         # ids; empty only with an evidence_note
    evidence_note: null         # why there is no artifact, if there is none
    observation: What the output shows          # neutral, not what it means
    status: completed           # completed | in_progress | abandoned
commands_or_scripts: [...]
inputs: [...]
outputs: [...]
evidence: [EV-0001]
observations: [...]
interpretation: What I think it means           # kept apart from observation
problems_and_failures:
  - problem: ...
    impact: ...
    resolution: ...
decisions:
  - decision: ...
    rationale: ...
    linked_suggestion: SUG-2026-08-001
next_actions:
  - action: ...
    suggestion: SUG-2026-08-001
    due: 2026-W34
```

Body: free text after the frontmatter, for anything that is not a field.

## Evidence

```yaml
id: EV-0001
created_at: 2026-08-13
type: analysis_result   # figure | table | command_output | analysis_result | script | commit |
                        # citation | negative_result | document | dataset
title: ...
description: ...
path_or_url: research/manifests/week-001-candidate-landscape.json   # repo-relative or URL
generated_by: script, command or person
input_data: [...]
linked_log: LOG-2026-08-13
linked_suggestion: SUG-2026-08-005
linked_claims: [claims that fall if this artifact is wrong]
verification_status: file_present   # missing | unverified | file_present | reviewed | verified
verified_by: null       # required for `verified`
verified_on: null       # required for `verified`
notes: null
```

`file_present` is checked by the validator: the path must exist in the repository. Absolute
server paths are rejected — provenance for read-only source data belongs in `docs/`.

## Weekly report

```yaml
id: WR-2026-W33
title: ...
period_label: 2026-W33
period_start: 2026-08-10
period_end: 2026-08-16
research_phase: ...
status: draft           # draft | ready | presented
record_kind: real
meeting_date: null
research_question: ...
hypothesis: ...
hypothesis_ref: HYP-001
suggestions_reviewed: [SUG-...]   # drives the response matrix; include open ones too
logs_in_period: [LOG-...]
work_completed:
  - summary: ...
    log: LOG-...
    evidence: [EV-...]
configuration:
  - label: Caller
    value: ClairS-TO v0.5.0
results:
  - claim: ...
    evidence: [EV-...]            # required — a result without evidence fails validation
    observation: ...
    interpretation: ...
difficulties:
  - title: ...
    detail: ...
    status: unresolved            # unresolved | resolved | deferred
decisions:
  - decision: ...
    rationale: ...
    log: LOG-...
next_commitments:
  - commitment: ...
    suggestion: SUG-...
    target: 2026-W34
appendix_commands: [...]
appendix_citations: [...]
known_gaps:
  - label: Missing evidence      # Missing evidence | Not completed | Blocked |
                                 # Requires researcher interpretation
    detail: ...
```
