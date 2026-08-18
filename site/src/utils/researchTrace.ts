// Pure traceability logic for the research OS.
//
// Deliberately free of `astro:content` imports so it can be unit-tested directly and reused
// by scripts. It works on structural record shapes: anything with the right fields — a
// content-collection entry, a parsed YAML file, a fixture — can be passed in.

export interface SuggestionData {
  id: string;
  suggestion: string;
  planned_actions: { action: string }[];
  evidence: string[];
  result: string | null;
  status: string;
  reason_not_completed: string | null;
  next_action: string | null;
  linked_daily_logs: string[];
}

export interface LogActionData {
  action: string;
  evidence: string[];
  evidence_note?: string | null;
  observation?: string | null;
  status: string;
}

export interface LogData {
  id: string;
  date: string;
  actions_completed: LogActionData[];
}

export interface EvidenceData {
  id: string;
  verification_status: string;
}

interface Entry<T> {
  data: T;
}

/* --- status vocabulary --------------------------------------------------- */

export type StatusTone = "open" | "active" | "done" | "blocked" | "dropped" | "neutral";

const suggestionTones: Record<string, StatusTone> = {
  captured: "open",
  planned: "open",
  in_progress: "active",
  completed: "done",
  blocked: "blocked",
  not_pursued: "dropped",
  dropped: "dropped"
};

export function suggestionTone(status: string): StatusTone {
  return suggestionTones[status] ?? "neutral";
}

export function statusLabel(status: string): string {
  return status.replace(/_/g, " ");
}

/** Statuses that still need work. The tracker must never hide these. */
export const OPEN_STATUSES = ["captured", "planned", "in_progress", "blocked"];

export function isOpen(suggestion: Entry<SuggestionData>): boolean {
  return OPEN_STATUSES.includes(suggestion.data.status);
}

/* --- ISO week bucketing --------------------------------------------------- */

/** ISO-8601 week label (`2026-W33`) for a `YYYY-MM-DD` string. */
export function isoWeek(date: string): string {
  const target = new Date(`${date}T00:00:00Z`);
  // Shift to the Thursday of the same ISO week, whose calendar year is the ISO year.
  target.setUTCDate(target.getUTCDate() + 3 - ((target.getUTCDay() + 6) % 7));
  const firstThursday = new Date(Date.UTC(target.getUTCFullYear(), 0, 4));
  firstThursday.setUTCDate(firstThursday.getUTCDate() + 3 - ((firstThursday.getUTCDay() + 6) % 7));
  const week = 1 + Math.round((target.getTime() - firstThursday.getTime()) / (7 * 86400000));
  return `${target.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
}

export function inPeriod(date: string, start: string, end: string): boolean {
  return date >= start && date <= end;
}

/* --- response matrix ------------------------------------------------------ */

export interface ResponseRow {
  id: string;
  suggestion: string;
  plannedResponse: string;
  whatWasDone: string[];
  evidence: string[];
  result: string | null;
  status: string;
  whyIncomplete: string | null;
  nextAction: string | null;
  /** True when a status implying work has no evidence attached to back it. */
  missingEvidence: boolean;
  logs: string[];
}

/**
 * Builds one row of the point-by-point response matrix — the table the weekly meeting opens
 * with.
 *
 * "What was done" is read from the linked daily logs rather than from the suggestion record,
 * so a suggestion cannot claim progress that no log supports. When the logs say nothing, the
 * row says nothing, and `missingEvidence` makes that visible instead of leaving a blank cell.
 */
export function buildResponseRow(
  suggestion: Entry<SuggestionData>,
  logById: Map<string, Entry<LogData>>
): ResponseRow {
  const logs = suggestion.data.linked_daily_logs;
  const whatWasDone = logs.flatMap((logId) => {
    const log = logById.get(logId);
    if (!log) {
      return [];
    }
    return log.data.actions_completed
      .filter((action) => action.status === "completed")
      .map((action) => action.action);
  });

  const claimsProgress = ["in_progress", "completed"].includes(suggestion.data.status);

  return {
    id: suggestion.data.id,
    suggestion: suggestion.data.suggestion,
    plannedResponse:
      suggestion.data.planned_actions.map((action) => action.action).join("; ") || "—",
    whatWasDone,
    evidence: suggestion.data.evidence,
    result: suggestion.data.result,
    status: suggestion.data.status,
    whyIncomplete: suggestion.data.reason_not_completed,
    nextAction: suggestion.data.next_action,
    missingEvidence: claimsProgress && suggestion.data.evidence.length === 0,
    logs
  };
}

/** Actions recorded as completed with no evidence id attached. */
export function actionsWithoutEvidence(log: Entry<LogData>): LogActionData[] {
  return log.data.actions_completed.filter(
    (action) => action.status === "completed" && action.evidence.length === 0
  );
}

export interface OsHealth {
  openSuggestions: number;
  blockedSuggestions: number;
  suggestionsMissingEvidence: string[];
  logsMissingEvidence: string[];
  unverifiedEvidence: number;
}

/**
 * The completeness picture shown on the dashboard. Every field counts something absent —
 * the system's job is to make gaps loud, so this is deliberately a list of what is missing
 * rather than a progress score.
 */
export function osHealth(
  suggestions: Entry<SuggestionData>[],
  logs: Entry<LogData>[],
  evidence: Entry<EvidenceData>[]
): OsHealth {
  return {
    openSuggestions: suggestions.filter(isOpen).length,
    blockedSuggestions: suggestions.filter((entry) => entry.data.status === "blocked").length,
    suggestionsMissingEvidence: suggestions
      .filter(
        (entry) =>
          ["in_progress", "completed"].includes(entry.data.status) &&
          entry.data.evidence.length === 0
      )
      .map((entry) => entry.data.id),
    logsMissingEvidence: logs
      .filter((log) => actionsWithoutEvidence(log).length > 0)
      .map((log) => log.data.id),
    unverifiedEvidence: evidence.filter((entry) => entry.data.verification_status !== "verified")
      .length
  };
}
