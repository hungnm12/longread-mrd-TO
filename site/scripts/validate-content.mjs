import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

const collections = [
  "weeks",
  "papers",
  "questions",
  "hypotheses",
  "experiments",
  "runs",
  "results",
  "decisions",
  "glossary",
  "modules"
];

const refFields = {
  weeks: [
    "research_questions",
    "hypotheses",
    "experiments",
    "results",
    "decisions"
  ],
  questions: [
    "hypotheses",
    "experiments",
    "results",
    "decisions",
    "papers"
  ],
  hypotheses: ["research_questions", "experiments", "results_for", "results_against"],
  experiments: ["research_questions", "hypotheses", "runs", "results"],
  runs: ["experiment_id"],
  results: ["experiment_id", "run_id", "weekly_reports"],
  decisions: ["research_questions", "experiments", "results", "weeks"],
  modules: [
    "hypotheses",
    "questions",
    "papers",
    "glossary_terms",
    "previous_module",
    "next_module"
  ]
};

function listMarkdownFiles(dir) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((entry) => {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        return listMarkdownFiles(full);
      }
      return entry.name.endsWith(".md") ? [full] : [];
    });
}

export function validateContent(root = process.cwd()) {
  const contentRoot = path.join(root, "src", "content");
  const allEntries = [];

  for (const collection of collections) {
    const dir = path.join(contentRoot, collection);
    if (!fs.existsSync(dir)) {
      continue;
    }
    for (const file of listMarkdownFiles(dir)) {
      const parsed = matter.read(file);
      allEntries.push({
        collection,
        file,
        id: parsed.data.id,
        data: parsed.data
      });
    }
  }

  const problems = [];
  const idToEntry = new Map();

  for (const entry of allEntries) {
    if (!entry.id) {
      problems.push(`Missing id in ${path.relative(root, entry.file)}`);
      continue;
    }
    if (idToEntry.has(entry.id)) {
      problems.push(
        `Duplicate id ${entry.id} in ${path.relative(root, entry.file)} and ${path.relative(
          root,
          idToEntry.get(entry.id).file
        )}`
      );
      continue;
    }
    idToEntry.set(entry.id, entry);
  }

  for (const entry of allEntries) {
    for (const field of refFields[entry.collection] ?? []) {
      const value = entry.data[field];
      const refs = Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
      for (const ref of refs) {
        if (!idToEntry.has(ref)) {
          problems.push(
            `Broken reference ${ref} from field ${field} in ${path.relative(root, entry.file)}`
          );
        }
      }
    }

    if (entry.collection === "results") {
      if (!entry.data.experiment_id || !entry.data.run_id) {
        problems.push(`Result ${entry.id} must link to both experiment_id and run_id`);
      }
      if (entry.data.evidence_level === "verified" && !entry.data.last_verified) {
        problems.push(`Verified result ${entry.id} must set last_verified`);
      }
    }

    if (entry.collection === "modules") {
      // A teaching module is the easiest place for an unsupported claim to slip in, so the
      // sections that bound its claims are required rather than encouraged.
      for (const field of ["learning_objectives", "interpretation_boundaries", "open_questions"]) {
        if (!Array.isArray(entry.data[field]) || entry.data[field].length === 0) {
          problems.push(`Module ${entry.id} must declare a non-empty ${field}`);
        }
      }
      // Modules describing published work must cite it. Modules that merely explain the
      // project's own design need not, so the requirement is tied to evidence_level.
      if (entry.data.evidence_level === "external_report" && (entry.data.sources ?? []).length === 0) {
        problems.push(`Module ${entry.id} reports external work but lists no sources`);
      }
    }
  }

  const moduleParts = new Map();
  for (const entry of allEntries.filter((e) => e.collection === "modules")) {
    const part = entry.data.part;
    if (moduleParts.has(part)) {
      problems.push(
        `Duplicate module part ${part} in ${entry.id} and ${moduleParts.get(part)}`
      );
    }
    moduleParts.set(part, entry.id);
  }

  return { allEntries, problems };
}

const { allEntries, problems } = validateContent();

if (problems.length > 0) {
  console.error("Content validation failed:");
  for (const problem of problems) {
    console.error(`- ${problem}`);
  }
  process.exit(1);
}

console.log(`Validated ${allEntries.length} content entries with no broken references.`);
