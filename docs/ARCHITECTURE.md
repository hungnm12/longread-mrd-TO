# Architecture

## ADR-001: static-first Phase 1 site

- Status: accepted
- Date: 2026-08-15
- Decision: implement the MVP as an Astro-based static site with strict TypeScript, Markdown content collections, and a lightweight custom validator.

## Why this fits the brief

- The project is content-heavy and weekly-report oriented.
- Static output is simpler to build, inspect, and deploy than a database-backed app.
- Markdown collections keep research objects versioned, human-readable, and easy to diff.
- Astro supports content-first pages, route generation, and print-friendly output without introducing backend complexity.

## Boundaries

- No backend service, database, or file-upload system in Phase 1.
- No large-file ingestion inside the web build.
- Small derived research summaries may live under `research/manifests/` and be imported into the site.
- Future ingestion, APIs, or structured stores must be added behind clear pain points and migration plans.

## Validation strategy

- Frontmatter schemas are enforced in `site/src/content.config.ts`.
- Cross-reference and provenance rules are enforced by a custom validator script and unit tests.
- Production readiness is demonstrated through `npm run lint`, `npm run test`, and `npm run build`.
