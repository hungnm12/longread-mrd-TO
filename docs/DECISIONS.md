# Decisions

This file holds **engineering and architecture** decisions.
**Research-direction** decisions live in [`research/decision_log.md`](./research/decision_log.md).
Neither supersedes the other.

## DECISION LOG

### 2026-08-16 — reuse `mrd-longphase/` rather than flattening to the brief's tree

- Decision: add the new research direction's code into the existing `mrd-longphase/`
  workspace — `src/{io,phasing,methylation,joint_evidence,provenance}/` and
  `workflow/{joint_molecule,feasibility_funnel,tools}/` — rather than moving `src/` and
  `workflow/` to the repository root.
- Reason: `mrd-longphase/src/` already contained empty `evidence/`, `models/` and
  `evaluation/` packages, and `workflow/` already contained empty `phasing/` and
  `methylation/` stages — the exact slots the new phases need. Flattening would have moved
  ~45 tracked files and broken `build_candidates.py`'s `REPO_ROOT` computation, the
  smoke test, two READMEs, `RESEARCH_SCOPE.md` and `research/manifests/*.json`, to satisfy
  a diagram.
- Alternatives rejected: flattening to the brief's preferred tree; renaming
  `mrd-longphase/` to `analysis/` (deferred — cosmetic, and it costs six doc references).
- Net change: one file moved (the smoke test into `tests/integration/`), one repaired
  (`config/tumor_only_hcc1395.yaml`, whose `output.*` paths pointed at a directory that no
  longer exists), everything else additive.
- Full analysis: [`migration_plan.md`](./migration_plan.md).
- Revisit trigger: if a second analysis workspace appears alongside `mrd-longphase/`, the
  nesting stops paying for itself.

### 2026-08-16 — gzip TSV for joint-molecule storage, not Parquet

- Decision: store joint-molecule partitions as gzip-compressed TSV with a sidecar JSON
  manifest.
- Reason: `pyarrow` is not installed, every existing output in the repository is TSV, and
  the binding constraint at this stage is *whether enough molecules exist at all* (H1) rather
  than query throughput. The cost is encoding four list-valued columns with a `;` separator.
- Alternatives rejected: Parquet (new heavyweight dependency, not shell-inspectable);
  JSONL (3-5x larger, not columnar, awkward with `awk`/`cut`).
- Revisit trigger: a single dilution level exceeding ~10 GB of records, or Phase 5 model
  fitting becoming I/O-bound. The record definition is format-agnostic so the swap costs one
  module.
- Full analysis: [`../mrd-longphase/docs/joint_molecule_schema.md`](../mrd-longphase/docs/joint_molecule_schema.md) §3.

### 2026-08-16 — teaching blocks as schema-validated frontmatter, not MDX

- Decision: render hypothesis boxes, predictions, failure modes, pending-experiment states
  and pipeline diagrams from structured frontmatter, rather than adding `@astrojs/mdx` so
  components could be embedded in module bodies.
- Reason: it avoids a new build dependency, and — more usefully — it lets the content schema
  enforce the discipline. A hypothesis box without a rejection condition, or a prediction
  with a pre-filled outcome, now fails the build rather than passing review.
- Alternative rejected: adding MDX. Nicer to author; enforces nothing.
- Revisit trigger: if a module needs genuinely free-form component placement mid-prose.

### 2026-08-15 — static-first Phase 1 implementation

- Decision: implement Phase 0 and the smallest complete Phase 1 as a static Astro site under `site/`.
- Reason: there was no existing frontend stack to extend, while the brief explicitly prefers a static-first research notebook architecture.
- Alternatives rejected:
  - Reusing `mrd-longphase/` as the site root: it has analysis code and results, but no web stack.
  - Building a backend or database first: unjustified for the current reporting-heavy phase.
- Revisit trigger: if weekly content volume or run-manifest querying becomes cumbersome in flat files.

### 2026-08-15 — Week 1 evidence stays descriptive

- Decision: keep Week 1 focused on candidate landscape characterization only.
- Reason: the brief forbids letting high-VAF interpretation dominate the storyline before a reliability framework exists.
- Revisit trigger: once a feature ladder, validation framework, or matched-normal benchmark is in place.
