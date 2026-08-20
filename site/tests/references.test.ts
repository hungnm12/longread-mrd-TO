import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { readFileSync, readdirSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { citationNumber, formatReference, references } from "../src/data/references";
import { relatedWork, paperIdToRefKey } from "../src/data/relatedWork";

const here = dirname(fileURLToPath(import.meta.url));
const siteRoot = resolve(here, "..");

function readSourceFiles(): string[] {
  const files: string[] = [];
  const walk = (dir: string) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = resolve(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (/\.(astro|ts)$/.test(entry.name)) {
        files.push(readFileSync(full, "utf8"));
      }
    }
  };
  walk(resolve(siteRoot, "src"));
  return files;
}

describe("IEEE reference list", () => {
  test("citation keys are unique", () => {
    const keys = references.map((entry) => entry.key);
    expect(new Set(keys).size).toBe(keys.length);
  });

  test("numbering matches array order", () => {
    references.forEach((entry, index) => {
      expect(citationNumber(entry.key)).toBe(index + 1);
    });
  });

  test("an unknown key fails loudly rather than rendering a wrong number", () => {
    expect(() => citationNumber("not-a-real-key")).toThrow();
  });

  test("every entry carries the bibliographic fields IEEE requires", () => {
    for (const entry of references) {
      expect(entry.authors.length).toBeGreaterThan(0);
      expect(entry.title.length).toBeGreaterThan(0);
      expect(entry.venue.length).toBeGreaterThan(0);
      // A source is identified either by DOI, or — for online documents — by URL plus an
      // access date. Neither present means the entry cannot be checked by a reader.
      expect(Boolean(entry.doi) || Boolean(entry.url && entry.accessed)).toBe(true);
      if (entry.doi) {
        expect(entry.doi).toMatch(/^10\.\d{4,9}\//);
      }
    }
  });

  test("formatted entries end in a single period", () => {
    for (const entry of references) {
      expect(formatReference(entry)).toMatch(/[^.]\.$/);
    }
  });

  test("every reference is cited somewhere on the site", () => {
    const sources = readSourceFiles().join("\n");
    for (const entry of references) {
      expect(sources.includes(`"${entry.key}"`)).toBe(true);
    }
  });

  test("related-work rows and paper mappings only cite known references", () => {
    for (const row of relatedWork) {
      expect(() => citationNumber(row.ref)).not.toThrow();
    }
    for (const key of Object.values(paperIdToRefKey)) {
      expect(() => citationNumber(key)).not.toThrow();
    }
  });

  test("related work covers every supplied study exactly once", () => {
    const refs = relatedWork.map((row) => row.ref);
    expect(new Set(refs).size).toBe(refs.length);
    expect(refs).toHaveLength(7);
  });
});

describe("website format", () => {
  // Two different artifacts, two different rules. The research narrative is a normal
  // scrolling website and must stay one; the weekly report is explicitly a slide deck for
  // the meeting. The check is therefore on the narrative page, not on file names.
  test("the research narrative is not a slide deck", () => {
    const narrative = readFileSync(
      resolve(siteRoot, "src", "pages", "research-narrative", "index.astro"),
      "utf8"
    );
    expect(narrative).not.toMatch(/ReportDeck|ReportSlide|presentation mode/i);
    expect(narrative).toContain("ResearchLayout");
  });

  test("the narrative's TOC matches the section ids it renders", () => {
    const meta = readFileSync(resolve(siteRoot, "src", "data", "siteMeta.ts"), "utf8");
    const narrative = readFileSync(
      resolve(siteRoot, "src", "pages", "research-narrative", "index.astro"),
      "utf8"
    );
    const tocIds = [...meta.matchAll(/\{ id: "([a-z-]+)"/g)].map((m) => m[1]);
    expect(tocIds.length).toBeGreaterThan(5);
    for (const id of tocIds) {
      expect(narrative, `section ${id} is in the TOC but not on the page`).toContain(`id="${id}"`);
    }
  });

  test("research integrity: the map does not overstate what G1 showed", () => {
    // Whitespace is collapsed first: these phrases wrap across source lines, and a line break
    // must not be the reason an integrity check passes or fails.
    const narrative = readFileSync(
      resolve(siteRoot, "src", "pages", "research-narrative", "index.astro"),
      "utf8"
    ).replace(/\s+/g, " ");
    // Physical linkage must never be presented as tumor specificity.
    expect(narrative).toMatch(/linkage alone is not tumor-specific/i);
    expect(narrative).toMatch(/does not show that G1 improves MRD detection/i);
    // The unconfirmed stratum is described by what it is, not by an inferred origin.
    expect(narrative).toMatch(/neither confirmed by SEQC2/);
    expect(narrative).not.toMatch(/germline pairs|non-somatic pairs|false pairs/i);
    // G5 is a prerequisite, not a peer hypothesis.
    expect(narrative).toMatch(/PREREQUISITE/);
  });

  test("gap state stays multi-dimensional rather than collapsing to pass\/fail", () => {
    const gaps = readFileSync(
      resolve(siteRoot, "..", "research", "design-space", "gaps.yaml"),
      "utf8"
    );
    // Every gap carries several dimensions; G1's two headline ones disagree, which is the point.
    expect((gaps.match(/- dimension:/g) ?? []).length).toBeGreaterThanOrEqual(15);
    expect(gaps).toMatch(/Physical linkage feasibility[\s\S]{0,60}SUPPORTED/);
    expect(gaps).toMatch(/Somatic specificity[\s\S]{0,60}NOT-SUPPORTED/);
  });

  test("the previously proposed direction stays demoted to a candidate", () => {
    const narrative = readFileSync(
      resolve(siteRoot, "src", "pages", "research-narrative", "index.astro"),
      "utf8"
    );
    // It may appear as one gap among others; it may not become the page's own conclusion.
    expect(narrative).toMatch(/candidate/i);
    expect(narrative).not.toMatch(/HypothesisPanel/);
  });

  test("deck behaviour is confined to the weekly report route", () => {
    const deckUsers: string[] = [];
    const walk = (dir: string) => {
      for (const entry of readdirSync(dir, { withFileTypes: true })) {
        const full = resolve(dir, entry.name);
        if (entry.isDirectory()) {
          walk(full);
        } else if (entry.name.endsWith(".astro") && /ReportDeck/.test(readFileSync(full, "utf8"))) {
          deckUsers.push(full.replace(`${siteRoot}/`, ""));
        }
      }
    };
    walk(resolve(siteRoot, "src", "pages"));
    expect(deckUsers).toEqual(["src/pages/weekly-reports/[id].astro"]);
  });

  test("the narrative page renders its sections with stable anchors", () => {
    const index = readFileSync(
      resolve(siteRoot, "src", "pages", "research-narrative", "index.astro"),
      "utf8"
    );
    // The section list is the research map: components first, then the active branch.
    for (const id of [
      "map",
      "active",
      "g1",
      "branches",
      "literature",
      "design-space",
      "references"
    ]) {
      expect(index).toContain(`id="${id}"`);
    }
  });
});
