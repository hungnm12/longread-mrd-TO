# MRD Long-read Research OS

This repository now carries two connected layers:

- `mrd-longphase/`: the existing analysis and reproducibility workspace for tumor-only MRD long-read work.
- `site/`: a static-first research website that turns weekly evidence, literature, and decisions into a navigable Research OS.

Long-form project context lives in [`docs/`](./docs). Local agent-specific instructions and the original canonical brief are kept under `.agent-context/` for local use and are ignored by Git in this folder.

## Current scope

Phase 0 and the smallest complete Phase 1 are implemented around the Week 1 tumor-only HCC1395 candidate landscape:

- Dashboard
- Research roadmap
- Literature matrix with the seven seed documents from the brief
- `WEEK-001` weekly report
- Linked research-question, hypothesis, experiment, run, result, and decision pages
- Content/reference validation
- Print-friendly weekly report styling

## Local commands

```bash
cd site
npm install
npm run dev
```

Quality gates:

```bash
cd site
npm run lint
npm run test
npm run build
```

## Content authoring workflow

1. Add or update durable project context in `docs/`.
2. Add research objects in `site/src/content/` using stable IDs such as `RQ-001`, `EXP-001`, and `WEEK-001`.
3. Keep small derived evidence snapshots and schemas under `research/`.
4. Run `npm run lint` before commit to catch broken references or missing provenance.
5. Run `npm run build` to confirm the production build.

## Data and provenance

- Source BAM/reference assets remain read-only and outside the site UI.
- Small summaries used by the site live in `research/manifests/`.
- Public-facing content uses redacted paths and explicit `preliminary` labels where local verification is not yet complete.

## What to push

- `docs/`
- `research/`
- `site/` source files and `package-lock.json`
- `mrd-longphase/` research code, reports, and small tracked outputs

Git will ignore `.agent-context/` and frontend/runtime artifacts such as `site/node_modules/`, `site/dist/`, `site/.astro/`, and `site/.config/`.
