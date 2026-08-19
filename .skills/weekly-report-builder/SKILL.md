---
name: weekly-report-builder
description: Compile a weekly research report record from the daily logs, suggestion tracker and evidence registry for a reporting period, rendered by the site as a slide deck. Use before a weekly meeting, or when the user says "build the weekly report", "prepare for the meeting", or names a week like 2026-W34.
---

# Weekly report builder

Compile one weekly report record. The report is a **view over records that already exist** —
if something is not in a daily log, a suggestion or an evidence record, it does not enter the
report; it becomes a labelled gap or a question for the user.

## Inputs

- Reporting period: an ISO week (`2026-W34`) or an explicit date range. Ask if unstated.
- `research/daily-logs/*.md` in the period.
- `research/suggestions/*.yaml` — all of them, not only the ones with progress.
- `research/evidence/*.yaml`.
- The previous report in `research/weekly-reports/`, for continuity of commitments.

## Steps

1. **Collect the period.** List every daily log whose `date` falls inside it. Note days with
   no log — a silent gap in the record is worth surfacing.

2. **Build the response matrix first.** It is the first thing the meeting discusses. For each
   suggestion reviewed:
   - what was planned;
   - what the linked logs actually record as completed;
   - the evidence ids behind it;
   - status, why it is incomplete, next action.
   The site derives this matrix from the tracker at render time, so your job is to set
   `suggestions_reviewed` correctly — include every suggestion that was open during the
   period, not only the ones with good news.

3. **Fill the record sections**, each traceable:
   - `work_completed[]` — one entry per real completed action, with `log` and `evidence`;
   - `configuration[]` — sample, caller and version, selection criteria, what truth resources
     were and were not used;
   - `results[]` — `claim`, `observation` (what the artifact shows) and `interpretation`
     (what it is taken to mean) kept strictly apart, with `evidence` on every result;
   - `difficulties[]` — failures, blockers and unresolved questions;
   - `decisions[]` — what changed in the plan and why;
   - `next_commitments[]` — each mapped back to a suggestion id and a target week;
   - `appendix_commands`, `appendix_citations` — preserve citations already present in the
     project; do not invent bibliography.

4. **Run the completeness check before finishing.** Report each finding, and record it in
   `known_gaps[]` using exactly one of these labels:
   - `Missing evidence` — a claim, a result or a suggestion with no artifact behind it;
   - `Not completed` — planned work that did not happen;
   - `Blocked` — work that could not proceed, with what blocks it;
   - `Requires researcher interpretation` — an observation nobody has interpreted yet.
   Also check for: suggestions with no implementation evidence, contradictions between logs,
   results whose interpretation exceeds the observation, missing provenance (no command, no
   input, no tool version), and commitments from the previous report that were not addressed.

5. **Write the record** as `research/weekly-reports/WR-<period>.md` following the frontmatter
   in `orchestration/schemas/record-shapes.md`, then validate and build:
   ```
   cd site && npm run validate:research && npm run build
   ```

6. **Report to the user**: the report route, the number of suggestions reviewed, every gap
   you labelled, and the specific questions that need the researcher's own judgement.

## Hard rules

- **Never fill a section silently.** An empty section is labelled, not smoothed over.
- **Never promote an interpretation to a result.** A result needs an observation and an
  artifact.
- **Never invent numbers, commands or citations.** Copy them from the records, or leave the
  field out and label the gap.
- **Never quietly drop a suggestion** because there is nothing good to say about it. A
  suggestion with no work is exactly what the professor needs to see.
- **Separate fact, interpretation and proposal** in the wording itself: "the figure shows…",
  "I read this as…", "I propose to…".

## Scientific guardrails for this project

- `PASS` is a caller retention label, not confirmed somatic truth; 48,819 of 3,169,996 is a
  selection funnel, not a false-positive rate.
- VAF is not tumor fraction; source coverage is not low-tumor-fraction sensitivity.
- Do not compare performance numbers across the supplied studies — different assays, sample
  types and cohorts.
- No claim that phase or methylation improves tumor recognition before a baseline, a metric
  and an ablation exist.

## Presenting

The site renders the record at `/weekly-reports/<id>/`. Press <kbd>p</kbd> for presentation
mode, arrow keys to move, <kbd>f</kbd> for fullscreen, <kbd>Esc</kbd> to exit; the toolbar's
print button produces the PDF through the browser.
