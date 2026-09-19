# Theme map — 2026-09-01

**Through-line.** A day spent turning SIMMA into something presentable and something bounded: the
deck was cut from 13 slides to 11 by stripping every number that did not earn its place, while a
parallel reading of the paper's Methods established what the paper actually measures and how low
it can honestly go — ending on the same verdict the deck's last slide carries, that only two of
SIMMA's four signals transfer to this project.

| Theme | Theme summary | Tasks | Why they are one theme | Representative evidence | Open items |
|---|---|---|---|---|---|
| **Deck construction** | An 11-slide SIMMA weekly report built by subtraction: two written feedback rounds removed a slide, a framing device, three closing slides and most of the numbers, leaving each slide with one job | T1, T2, T3, T4, T5, T6, T7 | All seven advance one deliverable, `SIMMA-weekly-report-2026-W35.pptx`, along one editing chain; T3 and T5 are the judgement calls that decided what T6 and T7 then cut | 13 → 14 → 11 slides; `0.5×`, `R=0.97`, `792/277`, `500 trees`, `76-gene` dropped, `2,282×` and `5 × 10⁻⁴` promoted to a 34 pt band; ecDNA slide rebuilt to answer one question with mirrored pictures | The `GENOME-WIDE SIGNAL` → `BROAD COPY NUMBER` relabel was proposed twice and never applied; the deck now ends on a finding with no closing slide |
| **Paper interrogation** | Read SIMMA's Methods directly to establish what each signal axis is actually measured with, what enters the model, and how low each axis has been shown to go | T8, T10, T11, T12 | Each answers one part of the same question — what is really behind SIMMA's numbers — and T12's LOD gap is only visible once T11's per-axis inventory exists | Seven RF feature blocks, none of them ecDNA; Guppy v6.5.7 / Dorado v7.4.14 / minimap2 v2.24 / mosdepth v0.3.3 / modkit v0.3.2 / SAVANA v1.3.7 / hifiasm v0.25.0; fragmentomics is a `samtools`+`perl` one-liner; only 2 of 6 axes report an LOD | None of this reached `sauer-2026-simma.md`, which records the analysis tools but no versions and no basecalling/alignment/coverage chain |
| **Bounds on this project** | Two independent limits were argued and accepted: which SIMMA signals can transfer to this dataset at all, and how low a dilution series built on them can honestly aim | T9, T13 | Both convert a SIMMA fact into a constraint on this project's own experiments, and both were reached by correcting a premise the user had brought; together they set what the next dilution design may claim | Copy number and methylation transfer and are already on disk; fragmentomics does not (machine-sheared library); ecDNA "not yet". 0.001% = 1×10⁻⁵ is 10× below the reported LOD, and the paper's own 10⁻⁶ simulation plateaued | The tissue-WGS question behind any ecDNA route is unanswered; no paired dilution design was drafted |

## Coverage checklist

| Task | Theme |
|---|---|
| T1 PCR-free grounding | Deck construction |
| T2 restructure round 1 | Deck construction |
| T3 critical-reading role | Deck construction |
| T4 ecDNA slide added and reframed | Deck construction |
| T5 speaking script + overclaim caught | Deck construction |
| T6 slidenote, 5 items | Deck construction |
| T7 second feedback block, 7 items | Deck construction |
| T8 ecDNA is not an RF input | Paper interrogation |
| T9 short-read/ecDNA premise corrected | Bounds on this project |
| T10 COPYBARA-focal | Paper interrogation |
| T11 per-axis toolchain | Paper interrogation |
| T12 LOD survey | Paper interrogation |
| T13 dilution feasibility at 1e-5 / 1e-4 | Bounds on this project |

Every task is in a theme. No task was excluded.

## Carried forward from 2026-08-31

`BM-0001-methyl-gate-mrd` did not move today: `workflow_state.yaml` is still
`current_stage: DESIGN`, `last_status: REDESIGN_REQUIRED`, and no `v1.1` draft exists in
`protocols/`. It stays on the open-items page.
