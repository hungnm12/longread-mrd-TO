// Site-level metadata for the research narrative.
//
// `lastUpdated` is a written constant rather than a build-time `new Date()`: the footer
// should state when the *content* was last revised, not when the site was last compiled.

export const siteMeta = {
  title: "MRD Research OS",
  subtitle:
    "What a complete MRD detector must solve, which component we are working in, and what the last experiment changed.",
  shortTitle: "Tumor-only long-read MRD",
  status: "Field synthesis — no direction selected, no detection result claimed",
  lastUpdated: "20 August 2026",
  repositoryUrl: "https://github.com/hungnm12/longread-mrd-TO",
  researchNotesHref: "/research-notes/"
} as const;


