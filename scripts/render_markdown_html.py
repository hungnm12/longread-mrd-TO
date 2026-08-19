#!/usr/bin/env python3
"""Render a Markdown daily report as a standalone, self-contained HTML page.

Self-contained is the point: one file with inline CSS and no external requests, so it can be
emailed, opened offline, or printed to PDF from a browser without anything breaking. The
styling matches the project website, so a report and the site read as one project.

    python3 scripts/render_markdown_html.py --daily                 # latest day
    python3 scripts/render_markdown_html.py --daily 2026-08-19      # a specific day
    python3 scripts/render_markdown_html.py path/to/file.md         # any Markdown file
    python3 scripts/render_markdown_html.py --daily --source log    # the internal log instead

Sources for `--daily`:

* `journal` (default) — the redacted entry already published to the journal repository. This is
  the shareable one: internal paths have been removed.
* `log` — the internal daily log, rendered through the *same* redactor before conversion, so an
  internal path cannot reach an HTML file by this route either.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from pathlib import Path

import markdown
import yaml

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "research" / "daily-logs"
JOURNAL_CONFIG = REPO / "configs" / "journal.yaml"
DEFAULT_OUT_DIR = REPO / "outputs" / "accepted" / "daily-html"

# The site's tokens, inlined. Kept in one string so the page carries its own styling.
STYLE = """
:root {
  --bg: #f7f3eb; --panel: #fffdf8; --ink: #1f1b16; --muted: #695f56; --line: #d4c8bb;
  --accent: #1f5c4e; --accent-soft: #d8ebe5; --warning: #8d5c14; --warning-soft: #f7ebc7;
  --serif: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
  --sans: "Segoe UI", Calibri, system-ui, sans-serif;
  --mono: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink); font-family: var(--sans);
  line-height: 1.6; font-size: 16px;
}
.page { width: min(52rem, calc(100% - 3rem)); margin: 0 auto; padding: 2.5rem 0 4rem; }
.masthead {
  border-bottom: 2px solid var(--accent); padding-bottom: 0.9rem; margin-bottom: 2rem;
  display: flex; flex-wrap: wrap; gap: 0.5rem 1.5rem; align-items: baseline;
  justify-content: space-between;
}
.masthead__project { font-family: var(--mono); font-size: 0.78rem; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--accent); }
.masthead__meta { font-size: 0.82rem; color: var(--muted); }
h1 { font-family: var(--serif); font-size: 2.1rem; line-height: 1.2; margin: 0 0 1.2rem; }
h2 {
  font-family: var(--mono); font-size: 0.82rem; letter-spacing: 0.07em; text-transform: uppercase;
  color: var(--accent); margin: 2.2rem 0 0.6rem; padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--line);
}
h3 { font-family: var(--serif); font-size: 1.15rem; margin: 1.5rem 0 0.5rem; }
p { margin: 0 0 0.9rem; }
/* The lead paragraph is the day's summary; it earns larger type. */
h1 + p { font-size: 1.1rem; color: var(--ink); border-left: 3px solid var(--accent-soft);
  padding-left: 1rem; }
ul, ol { margin: 0 0 1rem; padding-left: 1.3rem; }
li { margin-bottom: 0.35rem; }
li > ul { margin-top: 0.35rem; }
blockquote {
  margin: 0 0 1rem; padding: 0.7rem 1.1rem; background: var(--panel);
  border: 1px solid var(--line); border-left: 3px solid var(--accent); border-radius: 8px;
  font-family: var(--serif); font-size: 1.02rem;
}
code { font-family: var(--mono); font-size: 0.88em; background: var(--panel);
  border: 1px solid var(--line); border-radius: 4px; padding: 0.05rem 0.3rem; }
pre { background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
  padding: 0.9rem 1.1rem; overflow-x: auto; }
pre code { border: none; background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; font-size: 0.92rem; margin: 0 0 1.2rem; }
th, td { border-bottom: 1px solid var(--line); padding: 0.5rem 0.6rem; text-align: left;
  vertical-align: top; }
th { font-family: var(--mono); font-size: 0.74rem; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--muted); }
hr { border: none; border-top: 1px solid var(--line); margin: 2rem 0 1.2rem; }
a { color: var(--accent); }
em { color: var(--muted); }
.footer { margin-top: 2.5rem; padding-top: 0.9rem; border-top: 1px solid var(--line);
  font-size: 0.82rem; color: var(--muted); }
@media print {
  body { background: #fff; font-size: 11pt; }
  .page { width: 100%; padding: 0; }
  h2 { break-after: avoid; }
  blockquote, pre, table { break-inside: avoid; }
  .no-print { display: none; }
}
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{style}</style>
</head>
<body>
<div class="page">
  <header class="masthead">
    <span class="masthead__project">{project}</span>
    <span class="masthead__meta">{meta}</span>
  </header>
{body}
  <p class="footer">{footer}</p>
</div>
</body>
</html>
"""


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_journal_config() -> dict:
    return yaml.safe_load(JOURNAL_CONFIG.read_text()) if JOURNAL_CONFIG.exists() else {}


def redact(text: str, config: dict) -> str:
    """Same redaction contract as the journal publisher: substitute, then refuse to pass."""
    rules = config.get("redaction", {})
    for rule in rules.get("substitutions", []):
        text = re.sub(rule["pattern"], rule["replacement"], text)
    leaks = [p for p in rules.get("forbidden", []) if re.search(p, text)]
    if leaks:
        fail("redaction failed; source still matches: " + ", ".join(leaks))
    return text


def strip_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    _, raw, body = text.split("---", 2)
    return yaml.safe_load(raw) or {}, body.strip()


def resolve_daily(date: str | None, source: str, config: dict) -> tuple[str, str, str]:
    """Return (markdown, title, resolved date) for a day, from the journal or the log."""
    if source == "journal":
        target = config.get("target", {})
        layout = config.get("layout", {})
        journal = (REPO / target.get("path", "")).resolve()
        pattern = layout.get("entry_path", "entries/{yyyy}/{mm}/{date}.md")
        if date:
            rel = pattern.format(yyyy=date[:4], mm=date[5:7], dd=date[8:10], date=date)
            path = journal / rel
            if not path.exists():
                fail(f"no journal entry for {date} at {path} — publish it first, or use --source log")
        else:
            root = journal / Path(pattern).parts[0]
            entries = sorted(root.rglob("*.md")) if root.exists() else []
            if not entries:
                fail(f"no journal entries under {journal} — publish one first, or use --source log")
            path = entries[-1]
            date = path.stem
        return path.read_text(encoding="utf-8"), date, date

    # source == "log": render the internal record, through the same redactor.
    if date:
        path = LOGS / f"{date}.md"
        if not path.exists():
            fail(f"no daily log for {date}")
    else:
        logs = sorted(LOGS.glob("*.md"))
        if not logs:
            fail("no daily logs found")
        path = logs[-1]
        date = path.stem
    front, body = strip_front_matter(path.read_text(encoding="utf-8"))
    parts = [f"# {date}", ""]
    if front.get("public_summary"):
        parts += [front["public_summary"].strip(), ""]
    if front.get("research_question"):
        parts += ["## Focus", "", f"> {front['research_question']}", ""]
    if front.get("actions_completed"):
        parts += ["## What was done", ""]
        for action in front["actions_completed"]:
            parts.append(f"- {action['action']}")
            if action.get("observation"):
                parts.append(f"  - Showed: {action['observation']}")
        parts.append("")
    if front.get("observations"):
        parts += ["## What the output showed", ""] + [f"- {o}" for o in front["observations"]] + [""]
    if front.get("interpretation"):
        parts += ["## What I take it to mean", "", front["interpretation"].strip(), ""]
    if front.get("problems_and_failures"):
        parts += ["## What did not work", ""]
        for problem in front["problems_and_failures"]:
            parts.append(f"- **{problem['problem']}**")
            if problem.get("impact"):
                parts.append(f"  - Impact: {problem['impact']}")
        parts.append("")
    if front.get("decisions"):
        parts += ["## Decisions", ""]
        parts += [f"- **{d['decision']}** — {d['rationale']}" for d in front["decisions"]] + [""]
    if front.get("next_actions"):
        parts += ["## Next", ""] + [f"- {n['action']}" for n in front["next_actions"]] + [""]
    if body:
        parts += ["## Note", "", body, ""]
    return "\n".join(parts), date, date


def normalise_list_indent(text: str) -> str:
    """Rewrite nested list indentation to the 4 spaces Python-Markdown requires.

    Our entries — and most Markdown written for GitHub — nest list items with 2 spaces, which
    CommonMark accepts and Python-Markdown silently flattens. The document's own indent unit is
    detected rather than assumed, so a file already written with 4 spaces is left alone.
    """
    item = re.compile(r"^( +)([-*+] |\d+\. )")
    indents = [len(m.group(1)) for m in (item.match(line) for line in text.splitlines()) if m]
    unit = min(indents) if indents else 0
    if unit == 0 or unit >= 4:
        return text

    out = []
    for line in text.splitlines():
        match = item.match(line)
        if match:
            level = len(match.group(1)) // unit
            line = " " * (4 * level) + line.lstrip(" ")
        out.append(line)
    return "\n".join(out)


def to_html(md_text: str, title: str, project: str, meta: str, footer: str) -> str:
    body = markdown.markdown(
        normalise_list_indent(md_text),
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )
    body = "\n".join("  " + line for line in body.splitlines())
    return PAGE.format(
        title=html.escape(title),
        style=STYLE,
        project=html.escape(project),
        meta=html.escape(meta),
        body=body,
        footer=html.escape(footer),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", type=Path, help="Markdown file to render")
    parser.add_argument("--daily", nargs="?", const="", metavar="DATE",
                        help="render a daily report; DATE defaults to the most recent")
    parser.add_argument("--source", choices=["journal", "log"], default="journal",
                        help="where --daily reads from (default: journal, the redacted entry)")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: outputs/accepted/daily-html/)")
    parser.add_argument("--title", help="page title; defaults to the first heading or the date")
    args = parser.parse_args()

    if not args.path and args.daily is None:
        fail("give a Markdown path, or --daily [DATE]")

    config = load_journal_config()

    if args.path:
        if not args.path.exists():
            fail(f"{args.path} does not exist")
        md_text = args.path.read_text(encoding="utf-8")
        front, stripped = strip_front_matter(md_text)
        md_text = stripped if front else md_text
        stem = args.path.stem
        title = args.title or stem
        meta = f"Rendered {dt.date.today().isoformat()}"
    else:
        date = args.daily or None
        md_text, title, date = resolve_daily(date, args.source, config)
        stem = date
        title = args.title or f"Daily report — {date}"
        origin = "journal entry" if args.source == "journal" else "internal log, redacted"
        meta = f"{date} · from the {origin} · rendered {dt.date.today().isoformat()}"

    # Redact whatever the source, so no route reaches HTML with an internal path in it.
    md_text = redact(md_text, config)

    footer = (
        "Observations are what an artifact showed; interpretations are the researcher's reading "
        "of them. Internal paths and dataset locations are redacted."
    )
    page = to_html(md_text, title, "Tumor-only long-read MRD — daily report", meta, footer)

    out = args.output or (DEFAULT_OUT_DIR / f"{stem}.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO) if REPO in out.resolve().parents else out} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
