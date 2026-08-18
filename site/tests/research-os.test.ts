import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { readFileSync, readdirSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { load as parseYaml } from "js-yaml";
import matter from "gray-matter";
import { validateResearchOs } from "../scripts/validate-research-os.mjs";
import { buildResponseRow, isoWeek } from "../src/utils/researchTrace";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
const researchRoot = resolve(repoRoot, "research");

type Record_ = { file: string; data: any };

function loadYaml(dir: string): Record_[] {
  return readdirSync(resolve(researchRoot, dir))
    .filter((name) => name.endsWith(".yaml"))
    .map((name) => ({
      file: name,
      data: parseYaml(readFileSync(resolve(researchRoot, dir, name), "utf8")) as any
    }));
}

function loadMarkdown(dir: string): Record_[] {
  return readdirSync(resolve(researchRoot, dir))
    .filter((name) => name.endsWith(".md"))
    .map((name) => ({
      file: name,
      data: matter.read(resolve(researchRoot, dir, name)).data as any
    }));
}

const suggestions = loadYaml("suggestions");
const evidence = loadYaml("evidence");
const logs = loadMarkdown("daily-logs");
const reports = loadMarkdown("weekly-reports");
const config = JSON.parse(readFileSync(resolve(researchRoot, "research-os.json"), "utf8"));

describe("research OS record store", () => {
  test("validator passes on the committed records", () => {
    const { problems } = validateResearchOs(repoRoot);
    expect(problems).toEqual([]);
  });

  test("record ids are unique within each store", () => {
    for (const store of [suggestions, evidence, logs, reports]) {
      const ids = store.map((record) => record.data.id);
      expect(new Set(ids).size).toBe(ids.length);
    }
  });

  test("every suggestion carries the tracker fields the meeting needs", () => {
    for (const { file, data } of suggestions) {
      for (const field of ["suggestion", "my_interpretation", "why_it_matters", "status", "source"]) {
        expect(data[field], `${file} is missing ${field}`).toBeTruthy();
      }
      expect(
        ["captured", "planned", "in_progress", "completed", "blocked", "not_pursued"]
      ).toContain(data.status);
    }
  });

  test("blocked and incomplete suggestions state a reason", () => {
    for (const { file, data } of suggestions) {
      if (data.status !== "completed") {
        expect(data.reason_not_completed, `${file} must explain what is not done`).toBeTruthy();
      }
    }
  });

  test("no evidence record is marked verified without a person and a date", () => {
    for (const { file, data } of evidence) {
      if (data.verification_status === "verified") {
        expect(data.verified_by, `${file} claims verification without verified_by`).toBeTruthy();
        expect(data.verified_on, `${file} claims verification without verified_on`).toBeTruthy();
      }
    }
  });

  test("evidence paths are repository-relative, never absolute server paths", () => {
    for (const { file, data } of evidence) {
      expect(data.path_or_url.startsWith("/"), `${file} exposes an absolute path`).toBe(false);
    }
  });

  test("a completed action has either an artifact or a written reason it has none", () => {
    for (const { file, data } of logs) {
      for (const action of data.actions_completed ?? []) {
        if (action.status !== "completed") continue;
        const supported = (action.evidence ?? []).length > 0 || Boolean(action.evidence_note);
        expect(supported, `${file}: "${action.action}" is unsupported`).toBe(true);
      }
    }
  });
});

describe("traceability", () => {
  test("a suggestion reaches its logs, its evidence and a weekly report", () => {
    const completed = suggestions.find((record) => record.data.status === "completed")!;
    expect(completed).toBeDefined();
    expect(completed.data.linked_daily_logs.length).toBeGreaterThan(0);
    expect(completed.data.evidence.length).toBeGreaterThan(0);

    const logIds = logs.map((record) => record.data.id);
    for (const logId of completed.data.linked_daily_logs) {
      expect(logIds).toContain(logId);
    }
    const evidenceIds = evidence.map((record) => record.data.id);
    for (const evidenceId of completed.data.evidence) {
      expect(evidenceIds).toContain(evidenceId);
    }
    const answering = reports.filter((report) =>
      report.data.suggestions_reviewed.includes(completed.data.id)
    );
    expect(answering.length).toBeGreaterThan(0);
  });

  test("the response matrix reports work only when a daily log supports it", () => {
    const suggestion = {
      data: {
        id: "SUG-TEST",
        suggestion: "test",
        planned_actions: [],
        evidence: [],
        result: null,
        status: "in_progress",
        reason_not_completed: null,
        next_action: null,
        linked_daily_logs: ["LOG-MISSING"]
      }
    } as any;
    const row = buildResponseRow(suggestion, new Map());
    expect(row.whatWasDone).toEqual([]);
    expect(row.missingEvidence).toBe(true);
  });

  test("the dashboard config points at records that exist", () => {
    const suggestionIds = suggestions.map((record) => record.data.id);
    for (const issue of config.critical_issues) {
      for (const id of issue.blocks) {
        expect(suggestionIds).toContain(id);
      }
    }
    expect(reports.map((record) => record.data.id)).toContain(config.latest_report);
  });
});

describe("scientific guardrails", () => {
  test("the ClairS-TO figures keep their meaning wherever they appear", () => {
    const text = [
      ...logs.map((record) => readFileSync(resolve(researchRoot, "daily-logs", record.file), "utf8")),
      ...reports.map((record) =>
        readFileSync(resolve(researchRoot, "weekly-reports", record.file), "utf8")
      ),
      ...suggestions.map((record) =>
        readFileSync(resolve(researchRoot, "suggestions", record.file), "utf8")
      )
    ].join("\n");

    // Both numbers must appear with their denominators intact, and PASS must never be
    // described as confirmed somatic.
    expect(text).toContain("3,169,996");
    expect(text).toContain("48,819");
    expect(text).toMatch(/PASS SNV candidates were retained from 3,169,996 total ClairS-TO records/);
    expect(text.toLowerCase()).not.toMatch(/confirmed somatic (variant|mutation)s? (were|are) (found|detected)/);
  });

  test("ISO week bucketing matches the calendar", () => {
    expect(isoWeek("2026-08-13")).toBe("2026-W33");
    expect(isoWeek("2026-08-16")).toBe("2026-W33");
    expect(isoWeek("2026-08-17")).toBe("2026-W34");
  });
});
