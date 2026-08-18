import { getCollection } from "astro:content";
import type { CollectionEntry } from "astro:content";
import researchOsConfig from "../../../research/research-os.json";

// Traceability logic lives in researchTrace.ts, which has no Astro dependency and is unit
// tested directly. This module is the Astro-facing half: it loads the collections, indexes
// them, and re-exports the pure helpers so pages import from one place.
export * from "@utils/researchTrace";

export type Suggestion = CollectionEntry<"suggestions">;
export type DailyLog = CollectionEntry<"dailyLogs">;
export type EvidenceRecord = CollectionEntry<"evidenceRecords">;
export type WeeklyReport = CollectionEntry<"weeklyReports">;

export const researchOs = researchOsConfig;

/**
 * The whole record store, loaded once and indexed by record id (`SUG-…`, `LOG-…`, `EV-…`).
 *
 * Records reference each other by these ids, never by file path, so a record can be renamed
 * or moved without breaking the traceability chain. Lookups return `undefined` for unknown
 * ids; `validate-research-os.mjs` is what turns a dangling id into a build failure, so pages
 * can render defensively without each one re-implementing the check.
 */
export async function loadResearchOs() {
  const [suggestions, logs, evidence, reports] = await Promise.all([
    getCollection("suggestions"),
    getCollection("dailyLogs"),
    getCollection("evidenceRecords"),
    getCollection("weeklyReports")
  ]);

  const sortedSuggestions = [...suggestions].sort((a, b) => a.data.id.localeCompare(b.data.id));
  const sortedLogs = [...logs].sort((a, b) => b.data.date.localeCompare(a.data.date));
  const sortedEvidence = [...evidence].sort((a, b) => a.data.id.localeCompare(b.data.id));
  const sortedReports = [...reports].sort((a, b) =>
    b.data.period_end.localeCompare(a.data.period_end)
  );

  return {
    suggestions: sortedSuggestions,
    logs: sortedLogs,
    evidence: sortedEvidence,
    reports: sortedReports,
    suggestionById: new Map(sortedSuggestions.map((entry) => [entry.data.id, entry])),
    logById: new Map(sortedLogs.map((entry) => [entry.data.id, entry])),
    evidenceById: new Map(sortedEvidence.map((entry) => [entry.data.id, entry])),
    reportById: new Map(sortedReports.map((entry) => [entry.data.id, entry]))
  };
}

/* --- routes ------------------------------------------------------------- */

export const suggestionHref = (id: string) => `/suggestions/${id.toLowerCase()}/`;
export const logHref = (id: string) => `/logs/${id.toLowerCase()}/`;
export const evidenceHref = (id: string) => `/evidence/${id.toLowerCase()}/`;
export const reportHref = (id: string) => `/weekly-reports/${id.toLowerCase()}/`;
