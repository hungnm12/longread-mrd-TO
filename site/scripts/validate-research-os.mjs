// Validator for the research OS record store (`research/`).
//
// The content schemas in `src/content.config.ts` already enforce shape. This file enforces
// the rules that need to see several records at once, or the filesystem:
//
//   • every cross-reference resolves (suggestion ↔ log ↔ evidence ↔ weekly report);
//   • work that claims to be done has something behind it, or an explicit reason;
//   • evidence paths exist in the repository and are never absolute server paths;
//   • `verified` requires a person and a date — not an AI summary.
//
// A violation fails the build. That is the point: the system is only useful if an empty
// claim cannot survive a commit.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";
// js-yaml 5 is ESM-only with named exports; there is no default export to import.
import { load as parseYaml } from "js-yaml";

const here = path.dirname(fileURLToPath(import.meta.url));
const defaultRepoRoot = path.resolve(here, "..", "..");

function readYamlDir(dir) {
  if (!fs.existsSync(dir)) {
    return [];
  }
  return fs
    .readdirSync(dir)
    .filter((name) => /\.(ya?ml)$/.test(name))
    .map((name) => {
      const file = path.join(dir, name);
      return { file, data: parseYaml(fs.readFileSync(file, "utf8")) ?? {} };
    });
}

function readMarkdownDir(dir) {
  if (!fs.existsSync(dir)) {
    return [];
  }
  return fs
    .readdirSync(dir)
    .filter((name) => name.endsWith(".md"))
    .map((name) => {
      const file = path.join(dir, name);
      return { file, data: matter.read(file).data };
    });
}

/** YAML dates parse to Date objects; the record store speaks ISO day strings. */
function isoDay(value) {
  if (value instanceof Date) {
    return value.toISOString().slice(0, 10);
  }
  return value ?? null;
}

export function validateResearchOs(repoRoot = defaultRepoRoot) {
  const root = path.join(repoRoot, "research");
  const problems = [];

  const suggestions = readYamlDir(path.join(root, "suggestions"));
  const logs = readMarkdownDir(path.join(root, "daily-logs"));
  const evidence = readYamlDir(path.join(root, "evidence"));
  const reports = readMarkdownDir(path.join(root, "weekly-reports"));

  const rel = (file) => path.relative(repoRoot, file);
  const ids = (records) => new Set(records.map((record) => record.data.id));
  const suggestionIds = ids(suggestions);
  const logIds = ids(logs);
  const evidenceIds = ids(evidence);

  const requireRef = (value, known, kind, where) => {
    if (value && !known.has(value)) {
      problems.push(`${where}: unknown ${kind} reference "${value}"`);
    }
  };

  /* --- suggestions ------------------------------------------------------- */

  for (const { file, data } of suggestions) {
    const where = rel(file);
    if (!data.id) {
      problems.push(`${where}: missing id`);
      continue;
    }
    for (const logId of data.linked_daily_logs ?? []) {
      requireRef(logId, logIds, "daily log", where);
    }
    for (const evidenceId of data.evidence ?? []) {
      requireRef(evidenceId, evidenceIds, "evidence", where);
    }

    // A completed suggestion without evidence or a stated result is the exact failure mode
    // this system exists to prevent.
    if (data.status === "completed" && (data.evidence ?? []).length === 0 && !data.result) {
      problems.push(
        `${where}: status "completed" requires evidence or an explicit result statement`
      );
    }
    if (["blocked", "not_pursued"].includes(data.status) && !data.reason_not_completed) {
      problems.push(`${where}: status "${data.status}" requires reason_not_completed`);
    }
    if (data.status !== "completed" && !data.next_action && data.status !== "not_pursued") {
      problems.push(`${where}: open suggestion requires a next_action`);
    }
  }

  /* --- daily logs -------------------------------------------------------- */

  for (const { file, data } of logs) {
    const where = rel(file);
    if (!data.id || !data.date) {
      problems.push(`${where}: missing id or date`);
      continue;
    }
    if (data.id !== `LOG-${isoDay(data.date)}`) {
      problems.push(`${where}: id should be LOG-<date>, found "${data.id}"`);
    }
    for (const suggestionId of data.linked_suggestions ?? []) {
      requireRef(suggestionId, suggestionIds, "suggestion", where);
    }
    for (const evidenceId of data.evidence ?? []) {
      requireRef(evidenceId, evidenceIds, "evidence", where);
    }
    for (const action of data.actions_completed ?? []) {
      for (const evidenceId of action.evidence ?? []) {
        requireRef(evidenceId, evidenceIds, "evidence", where);
      }
      // "Ran the tool" is not a result. A completed action must point at an artifact or say
      // in writing why there is none.
      if (
        action.status === "completed" &&
        (action.evidence ?? []).length === 0 &&
        !action.evidence_note
      ) {
        problems.push(
          `${where}: completed action "${action.action}" has no evidence and no evidence_note`
        );
      }
      if (action.status === "completed" && !action.observation && !action.evidence_note) {
        problems.push(
          `${where}: completed action "${action.action}" records no observation`
        );
      }
    }
    for (const decision of data.decisions ?? []) {
      requireRef(decision.linked_suggestion, suggestionIds, "suggestion", where);
    }
    for (const next of data.next_actions ?? []) {
      requireRef(next.suggestion, suggestionIds, "suggestion", where);
    }
  }

  /* --- evidence ---------------------------------------------------------- */

  for (const { file, data } of evidence) {
    const where = rel(file);
    if (!data.id) {
      problems.push(`${where}: missing id`);
      continue;
    }
    requireRef(data.linked_log, logIds, "daily log", where);
    requireRef(data.linked_suggestion, suggestionIds, "suggestion", where);

    const target = data.path_or_url ?? "";
    const isUrl = /^https?:\/\//.test(target);
    if (!isUrl) {
      if (path.isAbsolute(target)) {
        // Absolute server paths must not reach the public site (see .agent-context/AGENTS.md).
        problems.push(`${where}: path_or_url must be repository-relative, found "${target}"`);
      } else if (data.verification_status !== "missing" && !fs.existsSync(path.join(repoRoot, target))) {
        problems.push(
          `${where}: path_or_url "${target}" does not exist — set verification_status: missing or fix the path`
        );
      }
    }
    if (data.verification_status === "verified" && !(data.verified_by && data.verified_on)) {
      problems.push(`${where}: verification_status "verified" requires verified_by and verified_on`);
    }
  }

  /* --- weekly reports ----------------------------------------------------- */

  for (const { file, data } of reports) {
    const where = rel(file);
    if (!data.id) {
      problems.push(`${where}: missing id`);
      continue;
    }
    for (const suggestionId of data.suggestions_reviewed ?? []) {
      requireRef(suggestionId, suggestionIds, "suggestion", where);
    }
    for (const logId of data.logs_in_period ?? []) {
      requireRef(logId, logIds, "daily log", where);
    }
    for (const item of data.work_completed ?? []) {
      requireRef(item.log, logIds, "daily log", where);
      for (const evidenceId of item.evidence ?? []) {
        requireRef(evidenceId, evidenceIds, "evidence", where);
      }
    }
    for (const result of data.results ?? []) {
      for (const evidenceId of result.evidence ?? []) {
        requireRef(evidenceId, evidenceIds, "evidence", where);
      }
      // A result slide without evidence is a claim without provenance.
      if ((result.evidence ?? []).length === 0) {
        problems.push(`${where}: result "${result.claim}" has no linked evidence`);
      }
    }
    for (const decision of data.decisions ?? []) {
      requireRef(decision.log, logIds, "daily log", where);
    }
    for (const commitment of data.next_commitments ?? []) {
      requireRef(commitment.suggestion, suggestionIds, "suggestion", where);
    }

    const start = isoDay(data.period_start);
    const end = isoDay(data.period_end);
    if (start && end && start > end) {
      problems.push(`${where}: period_start is after period_end`);
    }
    for (const logId of data.logs_in_period ?? []) {
      const log = logs.find((entry) => entry.data.id === logId);
      const day = log ? isoDay(log.data.date) : null;
      if (day && start && end && (day < start || day > end)) {
        problems.push(`${where}: ${logId} (${day}) is outside the reporting period`);
      }
    }
  }

  /* --- dashboard config --------------------------------------------------- */

  const configPath = path.join(root, "research-os.json");
  if (!fs.existsSync(configPath)) {
    problems.push("research/research-os.json is missing");
  } else {
    const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
    for (const issue of config.critical_issues ?? []) {
      for (const suggestionId of issue.blocks ?? []) {
        requireRef(suggestionId, suggestionIds, "suggestion", "research/research-os.json");
      }
    }
    if (config.latest_report) {
      const knownReports = new Set(reports.map((report) => report.data.id));
      requireRef(config.latest_report, knownReports, "weekly report", "research/research-os.json");
    }
  }

  return {
    counts: {
      suggestions: suggestions.length,
      logs: logs.length,
      evidence: evidence.length,
      reports: reports.length
    },
    problems
  };
}

// Executed directly by `npm run validate:research`.
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const { counts, problems } = validateResearchOs();
  if (problems.length > 0) {
    console.error("Research OS validation failed:");
    for (const problem of problems) {
      console.error(`- ${problem}`);
    }
    process.exit(1);
  }
  console.log(
    `Validated ${counts.suggestions} suggestions, ${counts.logs} daily logs, ${counts.evidence} evidence records and ${counts.reports} weekly reports.`
  );
}
