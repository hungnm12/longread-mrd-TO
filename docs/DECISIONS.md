# Decisions

## DECISION LOG

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
