#!/usr/bin/env python3
"""Publish a daily log as a journal entry in a separate git repository.

The journal is deliberately a *different* repo from this one: it has a different audience, so
it gets a different history and a redaction pass. This script renders one day's structured log
into a readable entry, refuses to emit anything that leaks an internal path, writes it into the
journal checkout, commits, and — only when asked — pushes.

    python3 scripts/publish_daily_journal.py                  # latest log, dry run
    python3 scripts/publish_daily_journal.py 2026-08-19        # a specific day, dry run
    python3 scripts/publish_daily_journal.py --write           # write + commit locally
    python3 scripts/publish_daily_journal.py --write --push    # ... and push to the journal remote
    python3 scripts/publish_daily_journal.py --init            # create the journal checkout

Safety properties, in order of importance:

1. It cannot publish into this repository. The journal path is resolved and rejected if it sits
   inside this working tree, and its `origin` is rejected if it matches this repo's `origin`.
2. It cannot push to this repository's remote — the only remote it ever pushes to is the one in
   `configs/journal.yaml`.
3. It aborts rather than publishing text that still matches a forbidden pattern after redaction.
4. It publishes nothing for a day whose log has no `public_summary`: an unsummarised day has
   nothing to say to an outside reader.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "research" / "daily-logs"
EVIDENCE = REPO / "research" / "evidence"
DEFAULT_CONFIG = REPO / "configs" / "journal.yaml"


# --------------------------------------------------------------------------- helpers
def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=check
    )


def read_front_matter(path: Path) -> tuple[dict, str]:
    """Split a Markdown file into its YAML front matter and its body."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    _, raw, body = text.split("---", 2)
    return yaml.safe_load(raw) or {}, body.strip()


def iso_day(value) -> str:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value)


# --------------------------------------------------------------------------- redaction
class Redactor:
    """Applies substitutions, then refuses to pass anything still matching `forbidden`."""

    def __init__(self, config: dict):
        rules = config.get("redaction", {})
        self.subs = [
            (re.compile(rule["pattern"]), rule["replacement"])
            for rule in rules.get("substitutions", [])
        ]
        self.forbidden = [re.compile(pattern) for pattern in rules.get("forbidden", [])]

    def scrub(self, text: str) -> str:
        for pattern, replacement in self.subs:
            text = pattern.sub(replacement, text)
        return text

    def verify(self, text: str) -> list[str]:
        return [p.pattern for p in self.forbidden if p.search(text)]


# --------------------------------------------------------------------------- rendering
def render_entry(log: dict, body: str, evidence: dict, config: dict) -> str:
    content = config["content"]
    sections = set(content.get("include_sections", []))
    date = iso_day(log["date"])
    out: list[str] = [f"# {date}", ""]

    summary = (log.get("public_summary") or "").strip()
    if summary:
        out += [summary, ""]

    if "focus" in sections and log.get("research_question"):
        out += ["## Focus", "", f"> {log['research_question']}", ""]

    if "what_was_done" in sections and log.get("actions_completed"):
        out += ["## What was done", ""]
        for action in log["actions_completed"]:
            status = action.get("status", "completed")
            mark = {"completed": "", "in_progress": " *(in progress)*", "abandoned": " *(abandoned)*"}
            out.append(f"- {action['action']}{mark.get(status, '')}")
            if action.get("observation"):
                out.append(f"  - Showed: {action['observation']}")
        out.append("")

    if "observations" in sections and log.get("observations"):
        out += ["## What the output showed", ""]
        out += [f"- {item}" for item in log["observations"]] + [""]

    if "interpretation" in sections and log.get("interpretation"):
        out += ["## What I take it to mean", "", log["interpretation"].strip(), ""]

    if "problems" in sections and log.get("problems_and_failures"):
        out += ["## What did not work", ""]
        for problem in log["problems_and_failures"]:
            out.append(f"- **{problem['problem']}**")
            if problem.get("impact"):
                out.append(f"  - Impact: {problem['impact']}")
            if problem.get("resolution"):
                out.append(f"  - Handling: {problem['resolution']}")
        out.append("")

    if "decisions" in sections and log.get("decisions"):
        out += ["## Decisions", ""]
        for decision in log["decisions"]:
            out.append(f"- **{decision['decision']}** — {decision['rationale']}")
        out.append("")

    if "next" in sections and log.get("next_actions"):
        out += ["## Next", ""]
        out += [f"- {item['action']}" for item in log["next_actions"]] + [""]

    if content.get("include_evidence_titles") and log.get("evidence"):
        out += ["## Evidence produced", ""]
        for eid in log["evidence"]:
            record = evidence.get(eid)
            if record:
                out.append(f"- `{eid}` — {record['title']} ({record['type'].replace('_', ' ')})")
            else:
                out.append(f"- `{eid}`")
        out.append("")

    if body.strip():
        out += ["## Note", "", body.strip(), ""]

    footer = (content.get("footer") or "").strip()
    if footer:
        out += ["---", "", f"*{footer}*", ""]
    return "\n".join(out).rstrip() + "\n"


def render_index(journal: Path, config: dict) -> str:
    layout = config["layout"]
    entries: list[tuple[str, str]] = []
    root = journal / Path(layout["entry_path"]).parts[0]
    if root.exists():
        for path in sorted(root.rglob("*.md"), reverse=True):
            entries.append((path.stem, str(path.relative_to(journal))))

    out = [f"# {layout['index_title']}", "", (layout.get("index_intro") or "").strip(), ""]
    out += ["## Entries", ""]
    if entries:
        current_month = None
        for date, rel in entries:
            month = date[:7]
            if month != current_month:
                out += ["", f"### {month}", ""]
                current_month = month
            out.append(f"- [{date}]({rel})")
    else:
        out.append("*No entries yet.*")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------- journal repo
def resolve_journal(config: dict, initialise: bool) -> Path:
    target = config["target"]
    journal = (REPO / target["path"]).resolve() if not Path(target["path"]).is_absolute() else Path(target["path"]).resolve()

    # Guard 1: the journal must not live inside this repository.
    if journal == REPO or REPO in journal.parents:
        fail(f"journal path {journal} is inside this repository — it must be a separate repo")

    if not journal.exists():
        if not initialise:
            fail(f"journal checkout {journal} does not exist — run with --init to create it")
        journal.mkdir(parents=True)
        run_git(journal, "init", "-b", target.get("branch", "main"))
        print(f"initialised journal repository at {journal}")

    if not (journal / ".git").exists():
        if not initialise:
            fail(f"{journal} exists but is not a git repository — run with --init")
        run_git(journal, "init", "-b", target.get("branch", "main"))

    # Guard 2: the journal's remote must differ from this repository's.
    this_remote = run_git(REPO, "remote", "get-url", "origin", check=False).stdout.strip()
    journal_remote = run_git(journal, "remote", "get-url", "origin", check=False).stdout.strip()
    if journal_remote and this_remote and journal_remote == this_remote:
        fail("the journal repo points at the same remote as this repository")

    configured = target.get("remote")
    if configured and journal_remote != configured:
        if journal_remote:
            run_git(journal, "remote", "set-url", "origin", configured)
        else:
            run_git(journal, "remote", "add", "origin", configured)
        print(f"journal remote set to {configured}")

    return journal


# --------------------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("date", nargs="?", help="YYYY-MM-DD; defaults to the most recent daily log")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write", action="store_true", help="write the entry and commit it locally")
    parser.add_argument("--push", action="store_true", help="push to the journal remote (implies --write)")
    parser.add_argument("--init", action="store_true", help="create the journal checkout if missing")
    args = parser.parse_args()
    write = args.write or args.push

    config = yaml.safe_load(args.config.read_text())

    # --- pick the day -------------------------------------------------------
    if args.date:
        log_path = LOGS / f"{args.date}.md"
        if not log_path.exists():
            fail(f"no daily log for {args.date}")
    else:
        candidates = sorted(LOGS.glob("*.md"))
        if not candidates:
            fail("no daily logs found")
        log_path = candidates[-1]

    log, body = read_front_matter(log_path)
    date = iso_day(log["date"])

    if config["content"].get("require_public_summary") and not (log.get("public_summary") or "").strip():
        fail(
            f"{log_path.name} has no `public_summary`. Add one or two sentences for an outside "
            "reader — the journal publishes a summary, not the raw internal log."
        )

    # --- evidence titles (never paths) --------------------------------------
    evidence: dict[str, dict] = {}
    for path in EVIDENCE.glob("*.yaml"):
        record = yaml.safe_load(path.read_text()) or {}
        if record.get("id"):
            evidence[record["id"]] = record

    # --- render + redact ----------------------------------------------------
    redactor = Redactor(config)
    entry = redactor.scrub(render_entry(log, body, evidence, config))
    leaks = redactor.verify(entry)
    if leaks:
        fail("redaction failed; entry still matches: " + ", ".join(leaks))

    if not write:
        print(f"--- dry run: {date} ---\n")
        print(entry)
        print("--- end dry run (use --write to commit, --push to publish) ---")
        return

    # --- write into the journal repo ---------------------------------------
    journal = resolve_journal(config, args.init)
    layout = config["layout"]
    rel = layout["entry_path"].format(yyyy=date[:4], mm=date[5:7], dd=date[8:10], date=date)
    entry_path = journal / rel
    entry_path.parent.mkdir(parents=True, exist_ok=True)
    entry_path.write_text(entry, encoding="utf-8")

    index = redactor.scrub(render_index(journal, config))
    if redactor.verify(index):
        fail("redaction failed on the index")
    (journal / layout["index_path"]).write_text(index, encoding="utf-8")

    run_git(journal, "add", "-A")
    if not run_git(journal, "status", "--porcelain").stdout.strip():
        print(f"{date}: journal already up to date, nothing to commit")
        return

    message = f"{config['target'].get('commit_prefix', 'journal:')} {date}".strip()
    commit_cmd = ["commit", "-m", message]
    author = config["target"].get("commit_author")
    if author:
        commit_cmd += ["--author", author]
    run_git(journal, *commit_cmd)
    print(f"{date}: committed {rel} in {journal}")

    if not args.push:
        print("not pushed (use --push)")
        return

    remote = config["target"].get("remote")
    if not remote:
        fail("target.remote is null in the config — set the journal repository URL before pushing")
    branch = config["target"].get("branch", "main")
    result = run_git(journal, "push", "-u", "origin", branch, check=False)
    if result.returncode != 0:
        fail("push failed:\n" + (result.stderr or result.stdout))
    print(f"pushed to {remote} ({branch})")


if __name__ == "__main__":
    main()
