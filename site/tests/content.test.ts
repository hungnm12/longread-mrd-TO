import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { describe, expect, test } from "vitest";
import summary from "../../research/manifests/week-001-candidate-landscape.json";
import { validateContent } from "../scripts/validate-content.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
const siteRoot = resolve(repoRoot, "site");

describe("week 001 evidence snapshot", () => {
  test("keeps the expected descriptive baseline", () => {
    expect(summary.summary.total_calls).toBe(3169996);
    expect(summary.summary.pass_snvs).toBe(48819);
    expect(summary.summary.pass_snv_fraction_pct).toBeCloseTo(1.54, 2);
  });

  test("content validator passes", () => {
    const { problems } = validateContent(siteRoot);
    expect(problems).toEqual([]);
  });
});
