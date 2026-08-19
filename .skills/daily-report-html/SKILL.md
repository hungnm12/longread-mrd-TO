---
name: daily-report-html
description: Render a daily report from Markdown into a standalone, self-contained HTML page for reading, sharing or printing to PDF. Use when the user asks for an HTML version of a daily report, wants to print or email a day's work, or says "convert the md to html".
---

# Daily report → HTML

One command produces one file: inline CSS, no external requests, opens offline, prints cleanly.

## Steps

1. **Pick the source.** By default this renders the *published journal entry* — already
   redacted, already the version an outside reader gets:
   ```bash
   python3 scripts/render_markdown_html.py --daily              # most recent day
   python3 scripts/render_markdown_html.py --daily 2026-08-19   # a specific day
   ```
   If the day has not been published yet, render the internal log instead — it goes through the
   same redactor before conversion:
   ```bash
   python3 scripts/render_markdown_html.py --daily 2026-08-19 --source log
   ```
   Any other Markdown file works too:
   ```bash
   python3 scripts/render_markdown_html.py research/knowledge/datasets.md -o /tmp/datasets.html
   ```

2. **Check what came out.** Open the file, or confirm the structure:
   ```bash
   grep -c "<h2>" outputs/accepted/daily-html/<date>.html
   ```
   The default output directory is `outputs/accepted/daily-html/`; override with `-o`.

3. **Report** the path, the source used (journal or log), and anything the redactor replaced.

## For PDF

Open the HTML in a browser and print. The page carries a `@media print` block: white
background, 11pt type, headings kept with their sections, and tables and quotes not split
across pages. No PDF toolchain is involved, so what you see in the browser is what prints.

## Rules

- **Never hand-write the HTML.** The script is the single renderer; a page written by hand
  drifts from the others and skips redaction.
- **Never bypass the redactor** to make something render. If it aborts, fix the source text —
  an internal path in an HTML file is a leak whether or not the file is committed.
- **Never edit a rendered page.** It is a build artifact. Change the Markdown and re-render.
- Rendering is not publishing. `scripts/publish_daily_journal.py` is what puts a day in the
  journal repository; this skill only produces a local file.

## What the page contains

The masthead names the project, the date and which source it came from. Then the day's summary
as a lead paragraph, the focus as a quote, and the sections of the entry — what was done, what
the output showed, the interpretation, what did not work, decisions, next steps, evidence
titles. The footer repeats the standing distinction: observations are what an artifact showed,
interpretations are the researcher's reading of them.

## Implementation notes

- Nested list indentation is normalised to the four spaces Python-Markdown needs; entries are
  written with the two spaces GitHub accepts, and the difference silently flattens sub-bullets
  otherwise. The document's own indent unit is detected, so 4-space Markdown is left alone.
- Extensions enabled: `extra` (tables, fenced code, definition lists), `sane_lists`, `smarty`.
- Styling uses the project website's colour tokens, so a report and the site read as one project.
