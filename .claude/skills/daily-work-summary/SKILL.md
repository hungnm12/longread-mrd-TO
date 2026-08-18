---
name: daily-work-summary
description: Turn a day's research notes into a structured daily log in research/daily-logs/, linked to suggestion ids and evidence records. Use when the user says "log today", "summarize my work", "record what I did", or hands over rough notes at the end of a working day.
---

# Daily work summary

Write one structured daily log from the user's notes. Record what happened; never
reconstruct what probably happened.

## Inputs

- The user's notes for the day (may be rough, unordered, in any language).
- Repository changes the user names, or `git status` / `git diff --stat` when the user asks
  you to look.
- Artifacts the user points at.

Do **not** browse the repository looking for work to attribute to the day. If it was not
mentioned or pointed at, it does not go in the log.

## Steps

1. **Read the existing store first.**
   - `research/suggestions/*.yaml` — the ids and open statuses.
   - `research/daily-logs/` — the most recent log, for unfinished `next_actions`.
   - `research/evidence/*.yaml` — existing evidence ids, so you reuse rather than duplicate.

2. **Separate the notes into five kinds of statement.** This is the core of the task.
   | Kind | Question it answers | Goes into |
   |---|---|---|
   | Action | What was performed? | `actions_completed[].action` |
   | Evidence | Which file, figure, command output or commit shows it? | `actions_completed[].evidence`, `evidence` |
   | Observation | What does the output *show*, in neutral terms? | `actions_completed[].observation`, `observations` |
   | Interpretation | What does the researcher think it *means*? | `interpretation` |
   | Decision | What changes in the next experiment? | `decisions[]` |
   Failures and blockers go in `problems_and_failures[]` — never omitted, never softened.

3. **Link to suggestions.** Match each action to an existing `SUG-…` id and set
   `linked_suggestions`. If work does not serve any tracked suggestion, leave it unlinked and
   say so in your report — an unlinked stream of work is worth noticing.

4. **Register new evidence.** For each artifact the user produced:
   `cd site && npm run new:evidence -- "Title"`, then fill the record. `path_or_url` must be
   repository-relative; absolute server paths are rejected by the validator.
   `verification_status` starts at `unverified` or `file_present`. Never `verified` — that
   requires a named person and date.

5. **Write the log.** `cd site && npm run new:log -- YYYY-MM-DD`, then fill the template.
   Remove every `TODO` you can answer and ask about the ones you cannot.

6. **Carry unfinished work forward.** Any `next_actions` entry from the previous log that was
   not done reappears in today's `planned_work`, or is explicitly dropped with a reason.

7. **Validate.** `cd site && npm run validate:research`. Fix what it reports.

8. **Report to the user**: the log path, which suggestions it advanced, which evidence was
   registered, and — separately — the list of questions you need answered.

## Hard rules

- **Never invent** a command, an output, a file path, a count or a measurement. If the user
  says "ran ClairS-TO", the log says that; it does not acquire a runtime, a version or a
  result the user did not state.
- **Never mark work completed without evidence or an explicit statement from the user.** If
  an action has no artifact, fill `evidence_note` with the reason ("working tree only, not
  committed") — the site will show it as *Missing evidence*, which is correct.
- **Never turn an assumption into an observation.** "The distribution looks bimodal" is an
  observation only if a figure shows it; otherwise it is interpretation.
- **Never hide a negative result or a failure.** A day where nothing worked is a valid log.
- **Never write "read papers" or "ran the tool" as a finished item** without an observation
  or an explicit note that no observation was produced.
- **Ask rather than guess.** Missing information is a question for the user, not a gap for
  you to fill.

## Scientific guardrails for this project

Keep these true in anything you write:

- `PASS` is a caller retention label, not confirmed somatic truth.
- 48,819 PASS SNV candidates out of 3,169,996 ClairS-TO records is a selection funnel, not a
  false-positive rate.
- VAF is an allele fraction, not tumor fraction.
- High coverage in the source sample is not low-tumor-fraction sensitivity.
- No claim that phase or methylation improves tumor recognition before a baseline, a metric
  and an ablation exist.

## Record shape

See `research/schemas/record-shapes.md` for the full field list of each record type.
