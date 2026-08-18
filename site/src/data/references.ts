// IEEE reference list for the research narrative.
//
// The array order *is* the citation numbering: entry index 0 is `[1]`. Numbers are never
// written by hand in the pages — `CitationMarker` resolves a stable `key` to the number,
// so inserting a reference cannot silently desynchronise the in-text markers from the
// bibliography. `tests/references.test.ts` enforces that every key cited on the site
// exists here and that every entry here is cited at least once.
//
// Every field below was checked against the publisher record or Crossref metadata on
// 2026-08-17. Nothing in this file may be filled in from memory: an unverifiable field is
// omitted rather than guessed (see docs/research/05_claim_boundaries.md).

export interface Reference {
  /** Stable citation key used by CitationMarker; never shown to readers. */
  key: string;
  /** Short name used in prose and table rows, e.g. "MRDetect". */
  shortName: string;
  authors: string;
  title: string;
  /** Journal, publisher, or document series, already IEEE-abbreviated. */
  venue: string;
  /** Volume / issue / pages / article number, pre-formatted; null for non-serials. */
  locator: string | null;
  date: string;
  doi: string | null;
  url: string | null;
  /** Set for online-only sources that need an access date in IEEE style. */
  accessed: string | null;
}

export const references: Reference[] = [
  {
    key: "mrdetect",
    shortName: "MRDetect",
    authors: "A. Zviran et al.",
    title:
      "Genome-wide cell-free DNA mutational integration enables ultra-sensitive cancer monitoring",
    venue: "Nat. Med.",
    locator: "vol. 26, no. 7, pp. 1114–1124",
    date: "Jul. 2020",
    doi: "10.1038/s41591-020-0915-3",
    url: null,
    accessed: null
  },
  {
    key: "mrd-edge",
    shortName: "MRD-EDGE",
    authors: "A. J. Widman et al.",
    title:
      "Ultrasensitive plasma-based monitoring of tumor burden using machine-learning-guided signal enrichment",
    venue: "Nat. Med.",
    locator: "vol. 30, no. 6, pp. 1655–1666",
    date: "Jun. 2024",
    doi: "10.1038/s41591-024-03040-4",
    url: null,
    accessed: null
  },
  {
    key: "phased-seq",
    shortName: "PhasED-Seq validation",
    authors: "N. Klimova, S. Close, D. M. Kurtz, R. D. Hockett, and L. Hyland",
    title:
      "Analytical validation of a circulating tumor DNA assay using PhasED-Seq technology for detecting residual disease in B-cell malignancies",
    venue: "Oncotarget",
    locator: "vol. 16, pp. 329–336",
    date: "May 2025",
    doi: "10.18632/oncotarget.28719",
    url: null,
    accessed: null
  },
  {
    key: "ont-realtime",
    shortName: "Real-time ONT cfDNA",
    authors: "Y. van der Pol et al.",
    title:
      "Real-time analysis of the cancer genome and fragmentome from plasma and urine cell-free DNA using nanopore sequencing",
    venue: "EMBO Mol. Med.",
    locator: "vol. 15, no. 12, art. no. e17282",
    date: "Dec. 2023",
    doi: "10.15252/emmm.202217282",
    url: null,
    accessed: null
  },
  {
    key: "nanorcs",
    shortName: "NanoRCS",
    authors: "L.-T. Chen et al.",
    title:
      "Nanopore-based consensus sequencing enables accurate multimodal tumor cell-free DNA profiling",
    venue: "Genome Res.",
    locator: "vol. 35, no. 4, pp. 886–899",
    date: "Apr. 2025",
    doi: "10.1101/gr.279144.124",
    url: null,
    accessed: null
  },
  {
    key: "methyl-fragmentation",
    shortName: "Methylation and fragmentation",
    authors: "M. Noë et al.",
    title:
      "DNA methylation and gene expression as determinants of genome-wide cell-free DNA fragmentation",
    venue: "Nat. Commun.",
    locator: "vol. 15, no. 1, art. no. 6690",
    date: "Aug. 2024",
    doi: "10.1038/s41467-024-50850-8",
    url: null,
    accessed: null
  },
  {
    key: "ont-cfdna-methyl",
    shortName: "ONT cfDNA methylation requirements",
    // Corporate author, as required for a vendor technical document.
    authors: "Oxford Nanopore Technologies plc",
    title: "Updated method for cell-free DNA (cfDNA) methylation profiling",
    venue: "Requirements document, Oxford Nanopore Technologies plc, Oxford, U.K.",
    locator: null,
    // The published page carries no stable issue date, so IEEE's access-date form is used
    // instead of inventing one.
    date: "",
    doi: null,
    url: "https://nanoporetech.com/document/requirements/cfDNA-methyl-profile",
    accessed: "Aug. 17, 2026"
  },
  {
    key: "clairs-to",
    shortName: "ClairS-TO",
    authors: "HKU-BAL",
    title: "ClairS-TO — a deep-learning method for tumor-only somatic variant calling",
    venue: "GitHub repository",
    locator: "v0.5.0",
    date: "",
    doi: null,
    url: "https://github.com/HKU-BAL/ClairS-TO",
    accessed: "Aug. 17, 2026"
  }
];

const indexByKey = new Map(references.map((entry, index) => [entry.key, index + 1]));

/** Resolves a citation key to its IEEE number. Throws at build time on a typo. */
export function citationNumber(key: string): number {
  const number = indexByKey.get(key);
  if (!number) {
    throw new Error(`Unknown citation key "${key}" — add it to src/data/references.ts`);
  }
  return number;
}

export function referenceAnchor(key: string): string {
  return `ref-${citationNumber(key)}`;
}

/**
 * IEEE entry text up to and including the date: authors, "title," venue, locator, date.
 * The DOI or URL is rendered separately by ReferenceList so it can carry a link.
 */
export function formatReference(entry: Reference): string {
  // In IEEE style the comma that closes the title sits inside the quotation marks, and the
  // venue follows after a space — not after a second comma.
  const tail = [entry.venue, entry.locator, entry.date].filter(Boolean).join(", ");
  // A venue that already ends in an abbreviation ("… Oxford, U.K.") must not gain a second
  // period when the entry is closed.
  return `${entry.authors}, "${entry.title}," ${tail.replace(/\.$/, "")}.`;
}
