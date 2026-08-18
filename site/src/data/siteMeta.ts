// Site-level metadata for the research narrative.
//
// `lastUpdated` is a written constant rather than a build-time `new Date()`: the footer
// should state when the *content* was last revised, not when the site was last compiled.

export const siteMeta = {
  title: "From Tumor-Only SNV Candidates to a Multimodal MRD Hypothesis",
  subtitle:
    "Can phase and native methylation evidence improve tumor-signal recognition beyond SNV-only evidence?",
  shortTitle: "Tumor-only long-read MRD",
  status: "Work in progress — hypothesis stage, no detection result claimed",
  lastUpdated: "17 August 2026",
  repositoryUrl: "https://github.com/hungnm12/longread-mrd-TO",
  researchNotesHref: "/research-notes/"
} as const;

/** Anchored sections of the narrative, in reading order. Drives the table of contents. */
export const narrativeSections = [
  { id: "overview", label: "Research overview", short: "Overview" },
  { id: "mrd-problem", label: "What problem does MRD address?", short: "MRD problem" },
  { id: "detection-barriers", label: "Why is MRD detection difficult?", short: "Detection barriers" },
  { id: "related-work", label: "What have the supplied studies done?", short: "Related work" },
  { id: "synthesis", label: "Cross-paper synthesis", short: "Synthesis" },
  { id: "clairs-to", label: "Current starting point: ClairS-TO", short: "ClairS-TO starting point" },
  { id: "research-gap", label: "From current output to the hypothesis", short: "Research gap" },
  { id: "hypothesis", label: "Research hypothesis", short: "Hypothesis" },
  { id: "references", label: "References", short: "References" }
] as const;
