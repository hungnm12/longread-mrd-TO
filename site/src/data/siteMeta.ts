// Site-level metadata for the research narrative.
//
// `lastUpdated` is a written constant rather than a build-time `new Date()`: the footer
// should state when the *content* was last revised, not when the site was last compiled.

export const siteMeta = {
  title: "MRD Research Map",
  subtitle:
    "What a complete MRD detector must solve, which component we are working in, and what the last experiment changed.",
  shortTitle: "Tumor-only long-read MRD",
  status: "Field synthesis — no direction selected, no detection result claimed",
  lastUpdated: "20 August 2026",
  repositoryUrl: "https://github.com/hungnm12/longread-mrd-TO",
  researchNotesHref: "/research-notes/"
} as const;

/** Anchored sections of the narrative, in reading order. Drives the table of contents. */
export const narrativeSections = [
  { id: "map", label: "Research map", short: "Research map" },
  { id: "active", label: "Active research", short: "Active research" },
  { id: "g1", label: "G1 — molecular linkage", short: "G1 drill-down" },
  { id: "branches", label: "G2–G5 by component", short: "Other branches" },
  { id: "literature", label: "Methods by component", short: "Literature" },
  { id: "design-space", label: "Design space", short: "Design space" },
  { id: "references", label: "References", short: "References" }
] as const;

