# Research OS — the weekly working loop

The site is the interface to a record store in `research/`. Its purpose is one traceable
loop:

```text
professor feedback → planned response → daily work → evidence → observation
→ interpretation → research decision → next commitment → weekly report
```

Nothing on the site is written twice: the dashboard, the response matrix and the weekly deck
are all views over the same records.

## Where things live

| What | Where | Rendered at |
|---|---|---|
| Dashboard state, phase, critical issues | `research/research-os.json` | `/` |
| Suggestions | `research/suggestions/*.yaml` | `/suggestions/` |
| Daily logs | `research/daily-logs/*.md` | `/logs/` |
| Evidence registry | `research/evidence/*.yaml` | `/evidence/` |
| Weekly reports | `research/weekly-reports/*.md` | `/weekly-reports/` |
| Record field reference | `research/schemas/record-shapes.md` | — |
| MRD scientific narrative | `site/src/pages/research-narrative/` | `/research-narrative/` |
| Older working notes | `site/src/content/` | `/research-notes/` |

## After each weekly meeting

1. **Capture each suggestion**, one record per suggestion:
   ```bash
   cd site && npm run new:suggestion -- "The suggestion as it was given"
   ```
2. **Interpret it** — fill `my_interpretation` and `why_it_matters`. If you cannot say why it
   matters, you have not understood it yet.
3. **Define planned actions and the evidence each would produce**, then set `status`,
   `next_action` and `target_week`.

Set `meeting_date` and `record_kind: recorded`. Update `next_meeting` in
`research/research-os.json`.

## Every day

1. **Record the research question** the day serves.
2. **Record actions and artifacts** — each completed action needs an evidence id, or an
   `evidence_note` saying why there is none.
3. **Separate observation from interpretation.** What the output shows is not what you think
   it means.
4. **Record failures and decisions.** A day where nothing worked is a valid log.
5. **Link the work to suggestion ids.**

```bash
cd site && npm run new:log -- 2026-08-18     # creates research/daily-logs/2026-08-18.md
cd site && npm run new:evidence -- "VAF distribution figure"
```

Or hand your rough notes to the skill and let it do the structuring:

```text
/daily-work-summary
```

It will ask for what is missing rather than filling it in.

## Before the weekly meeting

1. **Build the report** for the period:
   ```text
   /weekly-report-builder 2026-W34
   ```
2. **Review the gaps it labelled** — `Missing evidence`, `Not completed`, `Blocked`,
   `Requires researcher interpretation`. They are on the "Known gaps" slide.
3. **Correct any interpretation that outruns its observation.**
4. **Present the point-by-point response first** — it is slide 2, immediately after framing.
5. **Discuss critical unresolved issues afterwards**, from the dashboard.

## Running and presenting

```bash
cd site && npm run dev            # http://localhost:4321
cd site && npm run build          # static output in site/dist
cd site && npm run preview        # serve the built site
```

The weekly report at `/weekly-reports/<id>/` opens as a scrollable document. In the toolbar:

- **Presentation mode** — one slide at a time (or press <kbd>p</kbd>);
  <kbd>←</kbd>/<kbd>→</kbd> to navigate, <kbd>f</kbd> fullscreen, <kbd>Esc</kbd> to exit.
- **Print / PDF** — prints every slide, one per page, through the browser's own PDF export.

Every slide keeps its anchor (`#response`, `#results`, …) in both modes, so a link can point
at one slide, and each slide links back to the log or evidence record behind it.

## Validation

```bash
cd site && npm run lint           # astro check + content validation + research-os validation
cd site && npm run test           # record-store, traceability and guardrail tests
cd site && npm run build
```

`npm run validate:research` fails the build when:

- a suggestion, log, evidence record or report references an id that does not exist;
- a suggestion is `completed` with neither evidence nor a result;
- a suggestion is `blocked`/`not_pursued` without `reason_not_completed`;
- a completed action has no evidence and no `evidence_note`, or no observation;
- an evidence path does not exist, or is an absolute server path;
- an evidence record claims `verified` without `verified_by` and `verified_on`;
- a weekly-report result has no linked evidence, or a log falls outside the report period.

## What the system will not do

- It will not mark work complete because an AI summarized it.
- It will not hide an incomplete or blocked suggestion.
- It will not fill an empty report section — it labels it.
- It will not turn `PASS` into confirmed somatic truth, VAF into tumor fraction, or source
  coverage into low-tumor-fraction sensitivity.
