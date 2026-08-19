---
name: daily-journal-publish
description: Summarise a day's work for an outside reader and publish it to the separate journal git repository. Use when the user says "publish the journal", "push today's summary", "update the public log", or at the end of a day once the internal daily log exists.
---

# Daily journal publish

Publish one day to the journal repository — a **different repo** from this one.

## Preconditions

1. **The day is over and the researcher says so.** The log must carry `day_status: closed`.
   Publishing a day still being worked on presents part of it as the whole of it. If the log
   says `open`, ask — do not close it on the researcher's behalf.
2. The internal log exists at `research/daily-logs/<date>.md`. If not, run
   `daily-work-summary` first; this skill does not invent a day.
3. `configs/journal.yaml` has `target.remote` set. If it is `null`, the journal is local-only
   and `--push` will refuse — report that instead of working around it.

## Steps

1. **Confirm the day is closed.** If `day_status` is `open`, stop and ask whether the day is
   finished. Then read the log: what was done, what the output showed, what changed.
2. **Write `public_summary`** into the log's front matter — one or two sentences for a reader
   outside the project:
   - what was attempted, what came out, and what it changed;
   - no internal ids (`SUG-…`, `EV-…`), no file paths, no server names;
   - no claim the log does not make. A day with no result says so.
3. **Dry run** and read the output:
   ```bash
   python3 scripts/publish_daily_journal.py <date>
   ```
4. **Publish**:
   ```bash
   python3 scripts/publish_daily_journal.py <date> --write --push
   ```
   First time only, add `--init` to create the checkout.
5. **Report**: the entry path, the journal commit, whether it pushed, and anything the redactor
   replaced.

## Rules

- **Never push to this repository's remote.** The script enforces it; do not work around it
  with a manual `git push`.
- **Never publish** an internal path, a dataset location, a credential or an unpublished
  figure. If the redactor aborts, fix the source text — do not weaken the pattern list.
- **Never publish an open day**, and never set `day_status: closed` yourself. The researcher
  decides when the day is over.
- **Never soften a negative day.** "Nothing worked, here is what was ruled out" is a good entry.
- **Never edit the log's factual fields** to make the summary read better. Add the summary; leave
  observations, interpretations and decisions as recorded.
- Publishing is idempotent: re-running a day rewrites its entry and commits only if something
  changed.

## What the journal contains

One entry per day (`entries/YYYY/MM/YYYY-MM-DD.md`) with the day's summary, focus, what was
done, what the output showed, the interpretation, what did not work, decisions, next steps and
evidence titles — plus a regenerated index. Sections are configurable in `configs/journal.yaml`.
