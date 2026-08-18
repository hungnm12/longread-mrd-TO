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
    for (const id of [
      "overview",
      "mrd-problem",
      "detection-barriers",
      "related-work",
      "synthesis",
      "clairs-to",
      "research-gap",
      "hypothesis",
      "references"
    ]) {
      expect(index).toContain(`id="${id}"`);
    }
  });
});
