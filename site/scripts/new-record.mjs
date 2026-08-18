// Creates an empty record in the research store.
//
//   npm run new:log -- 2026-08-18
//   npm run new:suggestion -- "Short suggestion text"
//   npm run new:evidence -- "Title of the artifact"
//
// The templates are intentionally full of `null` and `TODO`: an unfilled field must be
// visible in review, and the validator will refuse the ones that matter. This script never
// invents content — it only creates the shape a human or the daily-work-summary skill fills.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "..", "..");
const [, , kind, ...rest] = process.argv;
const argument = rest.join(" ").trim();

const today = new Date().toISOString().slice(0, 10);

function write(file, contents) {
  if (fs.existsSync(file)) {
    console.error(`Refusing to overwrite ${path.relative(repoRoot, file)}`);
    process.exit(1);
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, contents);
  console.log(`Created ${path.relative(repoRoot, file)}`);
}

function nextId(dir, prefix, width) {
  const existing = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
  const numbers = existing
    .map((name) => Number.parseInt(name.replace(/[^0-9]/g, "").slice(-width), 10))
    .filter((value) => Number.isFinite(value));
  const next = (numbers.length ? Math.max(...numbers) : 0) + 1;
  return `${prefix}${String(next).padStart(width, "0")}`;
}

if (kind === "log") {
  const date = argument || today;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    console.error(`Expected a YYYY-MM-DD date, got "${date}"`);
    process.exit(1);
  }
  write(
    path.join(repoRoot, "research", "daily-logs", `${date}.md`),
    `---
id: LOG-${date}
date: ${date}
record_kind: real
research_question: TODO — the question this day's work serves
linked_suggestions: []
planned_work:
  - TODO
actions_completed:
  - action: TODO — what was actually performed
    evidence: []
    evidence_note: TODO — remove once an evidence id is attached, or explain why there is none
    observation: TODO — what the output shows, not what it means
    status: completed
commands_or_scripts: []
inputs: []
outputs: []
evidence: []
observations: []
interpretation: null
problems_and_failures: []
decisions: []
next_actions: []
---

TODO — free-text notes. Keep observation and interpretation separate above.
`
  );
} else if (kind === "suggestion") {
  const dir = path.join(repoRoot, "research", "suggestions");
  const id = nextId(dir, `SUG-${today.slice(0, 7)}-`, 3);
  write(
    path.join(dir, `${id}.yaml`),
    `id: ${id}
meeting_date: ${today}
source: TODO — who said it (professor, lab meeting, self)
record_kind: recorded
suggestion: ${argument ? JSON.stringify(argument) : "TODO — the suggestion as it was given"}
my_interpretation: TODO — what I understand it to mean
why_it_matters: TODO — what changes if it is ignored
planned_actions:
  - action: TODO
    expected_evidence: TODO — the artifact that would show this was done
    status: planned
status: captured
linked_daily_logs: []
evidence: []
result: null
reason_not_completed: TODO — required while this is not completed
next_action: TODO — the next concrete step
target_week: null
`
  );
} else if (kind === "evidence") {
  const dir = path.join(repoRoot, "research", "evidence");
  const id = nextId(dir, "EV-", 4);
  write(
    path.join(dir, `${id}.yaml`),
    `id: ${id}
created_at: ${today}
type: analysis_result
title: ${argument ? JSON.stringify(argument) : "TODO"}
description: TODO — what this artifact is
path_or_url: TODO — repository-relative path or URL, never an absolute server path
generated_by: TODO — script, command or person
input_data: []
linked_log: null
linked_suggestion: null
linked_claims: []
verification_status: unverified
verified_by: null
verified_on: null
notes: null
`
  );
} else {
  console.error("Usage: node scripts/new-record.mjs <log|suggestion|evidence> [argument]");
  process.exit(1);
}
