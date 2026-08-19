import { defineCollection, z } from "astro:content";
import { file, glob } from "astro/loaders";
import { parse as parseYaml } from "yaml";

const evidenceState = z.enum([
  "planned",
  "running",
  "observed",
  "verified",
  "rejected",
  "blocked"
]);

const evidenceLevel = z.enum([
  "preliminary",
  "verified",
  "reproduced",
  "external_report"
]);

const commonLinks = {
  datasets: z.array(z.string()).default([]),
  tools: z.array(z.string()).default([]),
  papers: z.array(z.string()).default([]),
  risks: z.array(z.string()).default([])
};

const weeks = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    period: z.string(),
    status: evidenceState,
    research_questions: z.array(z.string()),
    hypotheses: z.array(z.string()),
    experiments: z.array(z.string()),
    results: z.array(z.string()),
    decisions: z.array(z.string()),
    evidence_level: evidenceLevel,
    last_verified: z.string().nullable().optional(),
    blockers: z.array(z.string()).default([]),
    next_decision: z.string(),
    readiness: z.array(z.string()).default([])
  })
});

const papers = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    local_filename: z.string(),
    pdf_available: z.boolean(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    sequencing_modality: z.string(),
    strategy: z.string(),
    signal_modalities: z.array(z.string()),
    reusable_module: z.string(),
    non_transferable_module: z.string(),
    limitations: z.array(z.string()),
    role_in_map: z.string()
  })
});

const questions = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    hypotheses: z.array(z.string()),
    experiments: z.array(z.string()),
    results: z.array(z.string()),
    decisions: z.array(z.string()),
    current_week: z.string(),
    thesis_relevance: z.string(),
    ...commonLinks
  })
});

const hypotheses = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    research_questions: z.array(z.string()),
    experiments: z.array(z.string()),
    results_for: z.array(z.string()).default([]),
    results_against: z.array(z.string()).default([]),
    assumptions: z.array(z.string()).default([]),
    prediction: z.string(),
    ...commonLinks
  })
});

const experiments = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    research_questions: z.array(z.string()),
    hypotheses: z.array(z.string()),
    runs: z.array(z.string()),
    results: z.array(z.string()),
    success_criteria: z.array(z.string()),
    failure_criteria: z.array(z.string()),
    fallback_paths: z.array(z.string()),
    ...commonLinks
  })
});

const runs = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    experiment_id: z.string(),
    inputs: z.array(z.string()),
    outputs: z.array(z.string()),
    command_file: z.string().nullable(),
    tool_version: z.string(),
    model: z.string(),
    provenance_note: z.string(),
    last_verified: z.string().nullable().optional(),
    ...commonLinks
  })
});

const results = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    experiment_id: z.string(),
    run_id: z.string(),
    weekly_reports: z.array(z.string()),
    observation: z.string(),
    interpretation: z.string(),
    caveats: z.array(z.string()),
    denominator: z.string(),
    metric_definition: z.string(),
    takeaway: z.string(),
    last_verified: z.string().nullable().optional(),
    ...commonLinks
  })
});

const decisions = defineCollection({
  schema: z.object({
    id: z.string(),
    title: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    research_questions: z.array(z.string()),
    experiments: z.array(z.string()),
    results: z.array(z.string()),
    weeks: z.array(z.string()),
    impact: z.string(),
    revisit_trigger: z.string(),
    alternatives_considered: z.array(z.string()),
    ...commonLinks
  })
});

const glossary = defineCollection({
  schema: z.object({
    id: z.string(),
    term: z.string(),
    short_definition: z.string()
  })
});

// Research-guide modules: the CCU Bioinformatics Lab tutorial format.
//
// The schema makes the pedagogical structure mandatory rather than conventional. A module
// cannot be published without learning objectives, a "why it matters" statement, explicit
// interpretation boundaries, and open questions — the sections that keep a teaching page
// from drifting into overclaiming.
const modules = defineCollection({
  schema: z.object({
    id: z.string(),
    part: z.number().int().positive(),
    title: z.string(),
    subtitle: z.string(),
    status: evidenceState,
    evidence_level: evidenceLevel,
    reading_time_minutes: z.number().int().positive(),
    learning_objectives: z.array(z.string()).min(1),
    why_it_matters: z.string(),
    // Every claim-bearing module must state what it does NOT establish.
    interpretation_boundaries: z.array(z.string()).min(1),
    open_questions: z.array(z.string()).min(1),
    prerequisites: z.array(z.string()).default([]),
    previous_module: z.string().nullable().default(null),
    next_module: z.string().nullable().default(null),
    ...commonLinks,
    hypotheses: z.array(z.string()).default([]),
    questions: z.array(z.string()).default([]),
    glossary_terms: z.array(z.string()).default([]),
    sources: z
      .array(
        z.object({
          label: z.string(),
          ref: z.string().nullable().default(null),
          note: z.string().nullable().default(null)
        })
      )
      .default([]),

    // Structured teaching blocks. Declared as data rather than embedded as components in
    // the body, so the site needs no MDX integration and — more usefully — so the schema
    // can enforce their internal discipline. A hypothesis box without a rejection
    // condition, or a prediction with a pre-filled outcome, fails the build.
    diagram: z
      .object({
        title: z.string(),
        caption: z.string().nullable().default(null),
        orientation: z.enum(["vertical", "horizontal"]).default("vertical"),
        stages: z
          .array(
            z.object({
              label: z.string(),
              note: z.string().nullable().default(null),
              emphasis: z.boolean().default(false)
            })
          )
          .min(2)
      })
      .nullable()
      .default(null),

    hypothesis_boxes: z
      .array(
        z.object({
          id: z.string(),
          name: z.string(),
          claim: z.string(),
          gate: z.string().nullable().default(null),
          // Both required: a hypothesis with no falsifying result is not a hypothesis.
          accepts: z.string(),
          rejects: z.string(),
          status: z
            .enum(["pending", "running", "accepted", "rejected", "blocked"])
            .default("pending")
        })
      )
      .default([]),

    predictions: z
      .array(
        z.object({
          question: z.string(),
          prediction: z.string(),
          // Stays null until an experiment produces it. See 05_claim_boundaries.md §4.
          outcome: z.string().nullable().default(null),
          verdict: z.enum(["matched", "contradicted", "partial"]).nullable().default(null)
        })
      )
      .default([]),

    failure_modes: z
      .array(
        z.object({
          title: z.string(),
          // Required: the actionable part of a warning is the symptom, not the risk.
          looks_like: z.string(),
          severity: z.enum(["silent", "loud"]).default("silent"),
          detail: z.string().nullable().default(null)
        })
      )
      .default([]),

    pending_experiments: z
      .array(
        z.object({
          title: z.string(),
          blocked_on: z.string().nullable().default(null),
          experiment: z.string().nullable().default(null)
        })
      )
      .default([])
  })
});

/* ------------------------------------------------------------------------ */
/* Research OS record store                                                   */
/* ------------------------------------------------------------------------ */
/*                                                                            */
/* These four collections are loaded from `../research/` rather than from     */
/* `src/content/`, because the records are repository data first and site     */
/* content second: the AI skills write them, `validate-content.mjs` checks    */
/* them, and the site renders them. Keeping them outside the site directory   */
/* means a record survives any future change of front-end.                    */
/*                                                                            */
/* The schemas below are the enforced contract. A record that omits a         */
/* required field fails the build rather than rendering as a blank cell —     */
/* which is the point: an incomplete record must be visible, not invisible.   */

const suggestionStatus = z.enum([
  "captured",
  "planned",
  "in_progress",
  "completed",
  "blocked",
  "not_pursued"
]);

/** Distinguishes real recorded material from the seeded examples shipped with the system. */
const recordKind = z.enum(["recorded", "real", "seeded_context", "template"]);

/**
 * `2026-08-13` in YAML parses to a Date, in JSON to a string. Both are normalised to an
 * ISO day string so every consumer — sorting, week bucketing, display — sees one type.
 */
const isoDate = z
  .union([z.string(), z.date()])
  .transform((value) => (typeof value === "string" ? value : value.toISOString().slice(0, 10)));

const nullableIsoDate = isoDate.nullable().default(null);

const suggestions = defineCollection({
  loader: glob({ base: "../research/suggestions", pattern: "**/*.{yaml,yml}" }),
  schema: z.object({
    id: z.string(),
    meeting_date: nullableIsoDate,
    source: z.string(),
    record_kind: recordKind.default("recorded"),
    suggestion: z.string(),
    my_interpretation: z.string(),
    why_it_matters: z.string(),
    planned_actions: z
      .array(
        z.object({
          action: z.string(),
          expected_evidence: z.string(),
          status: z.enum(["planned", "in_progress", "completed", "dropped"]).default("planned")
        })
      )
      .default([]),
    status: suggestionStatus,
    linked_daily_logs: z.array(z.string()).default([]),
    evidence: z.array(z.string()).default([]),
    result: z.string().nullable().default(null),
    // Required in spirit for blocked/not_pursued/incomplete work; enforced by the validator,
    // which can see the status and the evidence together.
    reason_not_completed: z.string().nullable().default(null),
    next_action: z.string().nullable().default(null),
    target_week: z.string().nullable().default(null)
  })
});

const dailyLogs = defineCollection({
  loader: glob({ base: "../research/daily-logs", pattern: "**/*.md" }),
  schema: z.object({
    id: z.string(),
    date: isoDate,
    record_kind: recordKind.default("real"),
    research_question: z.string(),
    // One or two sentences for an outside reader. The journal publisher refuses to publish a
    // day without one: an unsummarised log is internal material, not a journal entry.
    public_summary: z.string().nullable().default(null),
    // A day is `open` until the researcher says it is finished. The publisher refuses to
    // publish an open day: a log written at midday is a snapshot, not an account of the day.
    day_status: z.enum(["open", "closed"]).default("open"),
    linked_suggestions: z.array(z.string()).default([]),
    planned_work: z.array(z.string()).default([]),
    // The five-part separation the workflow depends on: an action is not a result, and a
    // completed action with neither evidence nor an explanation is rejected by the validator.
    actions_completed: z
      .array(
        z.object({
          action: z.string(),
          evidence: z.array(z.string()).default([]),
          evidence_note: z.string().nullable().default(null),
          observation: z.string().nullable().default(null),
          status: z.enum(["completed", "in_progress", "abandoned"]).default("completed")
        })
      )
      .default([]),
    commands_or_scripts: z.array(z.string()).default([]),
    inputs: z.array(z.string()).default([]),
    outputs: z.array(z.string()).default([]),
    evidence: z.array(z.string()).default([]),
    observations: z.array(z.string()).default([]),
    interpretation: z.string().nullable().default(null),
    problems_and_failures: z
      .array(
        z.object({
          problem: z.string(),
          impact: z.string().nullable().default(null),
          resolution: z.string().nullable().default(null)
        })
      )
      .default([]),
    decisions: z
      .array(
        z.object({
          decision: z.string(),
          rationale: z.string(),
          linked_suggestion: z.string().nullable().default(null)
        })
      )
      .default([]),
    next_actions: z
      .array(
        z.object({
          action: z.string(),
          suggestion: z.string().nullable().default(null),
          due: z.string().nullable().default(null)
        })
      )
      .default([])
  })
});

const evidenceRecords = defineCollection({
  loader: glob({ base: "../research/evidence", pattern: "**/*.{yaml,yml}" }),
  schema: z.object({
    id: z.string(),
    created_at: isoDate,
    type: z.enum([
      "figure",
      "table",
      "command_output",
      "analysis_result",
      "script",
      "commit",
      "citation",
      "negative_result",
      "document",
      "dataset"
    ]),
    title: z.string(),
    description: z.string(),
    // Repository-relative path or external URL. Absolute server paths are rejected by the
    // validator: the public site must not print them (see AGENTS.md).
    path_or_url: z.string(),
    generated_by: z.string(),
    input_data: z.array(z.string()).default([]),
    linked_log: z.string().nullable().default(null),
    linked_suggestion: z.string().nullable().default(null),
    linked_claims: z.array(z.string()).default([]),
    // `file_present` means only that the path exists. Nothing is `verified` because an AI
    // summarized it — that requires a named person and a date.
    verification_status: z.enum(["missing", "unverified", "file_present", "reviewed", "verified"]),
    verified_by: z.string().nullable().default(null),
    verified_on: nullableIsoDate,
    notes: z.string().nullable().default(null)
  })
});

const weeklyReports = defineCollection({
  loader: glob({ base: "../research/weekly-reports", pattern: "**/*.md" }),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    period_label: z.string(),
    period_start: isoDate,
    period_end: isoDate,
    research_phase: z.string(),
    status: z.enum(["draft", "ready", "presented"]).default("draft"),
    record_kind: recordKind.default("real"),
    meeting_date: nullableIsoDate,
    research_question: z.string(),
    hypothesis: z.string(),
    hypothesis_ref: z.string().nullable().default(null),
    // The response matrix is derived from these ids rather than copied into the report, so a
    // suggestion cannot say one thing on its own page and another in the deck.
    suggestions_reviewed: z.array(z.string()).default([]),
    logs_in_period: z.array(z.string()).default([]),
    work_completed: z
      .array(
        z.object({
          summary: z.string(),
          log: z.string().nullable().default(null),
          evidence: z.array(z.string()).default([])
        })
      )
      .default([]),
    configuration: z.array(z.object({ label: z.string(), value: z.string() })).default([]),
    results: z
      .array(
        z.object({
          claim: z.string(),
          evidence: z.array(z.string()).default([]),
          observation: z.string(),
          interpretation: z.string()
        })
      )
      .default([]),
    difficulties: z
      .array(
        z.object({
          title: z.string(),
          detail: z.string(),
          status: z.enum(["unresolved", "resolved", "deferred"]).default("unresolved")
        })
      )
      .default([]),
    decisions: z
      .array(
        z.object({
          decision: z.string(),
          rationale: z.string(),
          log: z.string().nullable().default(null)
        })
      )
      .default([]),
    next_commitments: z
      .array(
        z.object({
          commitment: z.string(),
          suggestion: z.string().nullable().default(null),
          target: z.string().nullable().default(null)
        })
      )
      .default([]),
    appendix_commands: z.array(z.string()).default([]),
    appendix_citations: z.array(z.string()).default([]),
    // Labelled gaps, printed on their own slide. The report builder must fill this in rather
    // than leaving a section silently empty.
    known_gaps: z
      .array(
        z.object({
          label: z.enum([
            "Missing evidence",
            "Not completed",
            "Blocked",
            "Requires researcher interpretation"
          ]),
          detail: z.string()
        })
      )
      .default([])
  })
});

/**
 * Every design-space artifact is a document — metadata keys, then one list — so a loader names
 * the list it wants rather than assuming the file is a bare array.
 */
function yamlList(key: string) {
  return (text: string): Record<string, unknown>[] => {
    const doc = parseYaml(text) as Record<string, unknown>;
    return (doc?.[key] as Record<string, unknown>[]) ?? [];
  };
}

/* ------------------------------------------------------------------------ */
/* Design space                                                               */
/* ------------------------------------------------------------------------ */
/*                                                                            */
/* The synthesis artifacts in research/design-space/ are the source of truth;  */
/* the site renders them. A YAML list file is loaded with `file()`, so adding  */
/* an axis or a gap changes the page without touching a component.            */

const designAxes = defineCollection({
  loader: file("../research/design-space/detector-axes.yaml", {
    parser: yamlList("axes")
  }),
  schema: z.object({
    name: z.string(),
    order: z.number(),
    added: z.boolean().default(false),
    justification: z.string().optional(),
    definition: z.string(),
    why_it_matters: z.string(),
    strategies: z
      .array(
        z.object({
          name: z.string(),
          detail: z.string().optional(),
          methods: z.array(z.string()).default([]),
          note: z.string().optional(),
          cost: z.string().optional()
        })
      )
      .default([]),
    open_position: z.string().optional(),
    note: z.string().optional(),
    tension: z.string().optional(),
    constraint: z.string().optional(),
    measured_locally: z.string().optional()
  })
});

const designMethods = defineCollection({
  loader: file("../research/design-space/method-matrix.yaml", {
    parser: yamlList("methods")
  }),
  schema: z.object({
    name: z.string(),
    ref: z.number().nullable().default(null),
    in_reviewed_set: z.boolean().default(true),
    is_detector: z.boolean().default(true),
    axes: z.record(z.string(), z.string()),
    unique_contribution: z.string(),
    limitation_here: z.string()
  })
});

const designGaps = defineCollection({
  loader: file("../research/design-space/gaps.yaml", {
    parser: yamlList("gaps")
  }),
  schema: z.object({
    title: z.string(),
    axes_combined: z.array(z.string()),
    closest_methods: z.array(z.string()).default([]),
    what_is_actually_different: z.string(),
    required_ont_capability: z.array(z.string()).default([]),
    required_data: z.string(),
    feasibility: z.string(),
    confounding_risks: z.array(z.string()).default([]),
    falsification: z.string(),
    status: z.string(),
    note: z.string().optional()
  })
});

const ontCapabilities = defineCollection({
  loader: file("../research/knowledge/ont-capabilities.yaml", {
    parser: yamlList("capabilities")
  }),
  schema: z.object({
    capability: z.string(),
    status: z.enum(["AVAILABLE", "DERIVABLE", "UNKNOWN", "MISSING"]),
    evidence: z.string(),
    path: z.string().optional(),
    caveat: z.string().optional(),
    note: z.string().optional(),
    blocks: z.string().optional(),
    resolution: z.string().optional(),
    consequence: z.string().optional(),
    restriction: z.string().optional()
  })
});

export const collections = {
  designAxes,
  designMethods,
  designGaps,
  ontCapabilities,
  suggestions,
  dailyLogs,
  evidenceRecords,
  weeklyReports,
  weeks,
  papers,
  questions,
  hypotheses,
  experiments,
  runs,
  results,
  decisions,
  glossary,
  modules
};
