// Site-level metadata for the research narrative.
//
// `lastUpdated` is a written constant rather than a build-time `new Date()`: the footer
// should state when the *content* was last revised, not when the site was last compiled.

export const siteMeta = {
  title: "The MRD Detector Design Space",
  subtitle:
    "What dimensions are existing methods manipulating, and which regions of the space does the reviewed literature leave thin?",
  shortTitle: "Tumor-only long-read MRD",
  status: "Field synthesis — no direction selected, no detection result claimed",
  lastUpdated: "19 August 2026",
  repositoryUrl: "https://github.com/hungnm12/longread-mrd-TO",
  researchNotesHref: "/research-notes/"
} as const;

/** Anchored sections of the narrative, in reading order. Drives the table of contents. */
export const narrativeSections = [
  { id: "overview", label: "Overview", short: "Overview" },
  { id: "mrd-problem", label: "The MRD problem", short: "MRD problem" },
  { id: "design-space", label: "The detector design space", short: "Design space" },
  { id: "common-principles", label: "Common principles", short: "Common principles" },
  { id: "unique-mechanisms", label: "Unique mechanisms", short: "Unique mechanisms" },
  { id: "method-matrix", label: "Method × axis comparison", short: "Method × axis" },
  { id: "unresolved", label: "Unresolved challenges", short: "Unresolved" },
  { id: "ont-capabilities", label: "ONT capability space", short: "ONT capabilities" },
  { id: "resources", label: "Available experimental resources", short: "Resources" },
  { id: "explored", label: "Explored vs underexplored", short: "Explored vs not" },
  { id: "opportunities", label: "Candidate research opportunities", short: "Opportunities" },
  { id: "references", label: "References", short: "References" }
] as const;
