import { defineCollection, z } from "astro:content";

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

export const collections = {
  weeks,
  papers,
  questions,
  hypotheses,
  experiments,
  runs,
  results,
  decisions,
  glossary
};
