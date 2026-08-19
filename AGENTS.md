# AGENTS.md

Operating rules for anything — human or agent — working in this repository. Read
[`PROJECT.md`](./PROJECT.md) first for what the project is trying to establish.

## Orient

| Question | File |
|---|---|
| What is my role allowed to do? | [`.agents/<role>.md`](./.agents) and [`orchestration/permissions.yaml`](./orchestration/permissions.yaml) |
| How does work move between stages? | [`orchestration/workflow.yaml`](./orchestration/workflow.yaml) |
| What is happening right now? | [`orchestration/state.yaml`](./orchestration/state.yaml) |
| What already exists on this server? | [`research/knowledge/`](./research/knowledge) — datasets, tools, ONT capabilities, constraints |
| What may I not claim? | [`research/knowledge/claim-boundaries.md`](./research/knowledge/claim-boundaries.md) |
| What shape must a record take? | [`orchestration/schemas/`](./orchestration/schemas) |

## Hard rules

- **Source data is read-only.** Never modify, re-index, move or re-sort anything under
  `/big8_disk/data/`, `/big8_disk/ref/` or `/bip7_disk/`. These are shared with other users.
- **The matched normal and the truth sets are evaluation-only.** `HCC1395BL.bam`, SEQC2 and the
  orthogonal benchmark may never enter a discovery or inference path.
- **No bulk data in the repository.** Manifests, summaries and small derived artifacts only.
- **No absolute server paths on the public site.** They belong in `research/knowledge/`,
  `data/` and manifests.
- **Never fabricate.** No invented command, output, count, citation or measurement. Ask instead.
- **Never mark work done without evidence** or a written reason there is none.
- **Never set an evidence record to `verified`.** That needs a named person and a date.
- **Thresholds are fixed before results are seen.** A defaulted threshold is an unrecorded
  research decision; the runner refuses rather than guessing.

## Scientific guardrails

Keep these true in every sentence written anywhere in this repository:

- `PASS` is a caller retention label, not confirmed somatic truth.
- Filtered ≠ false positive; 48,819 of 3,169,996 is a selection funnel.
- VAF ≠ tumor fraction.
- High source coverage ≠ low-tumor-fraction sensitivity.
- 5mC and 5hmC are separate channels and are never summed.
- No claim that phase or methylation improves tumor recognition before a baseline, a defined
  metric and an ablation exist.
- HCC1395 genomic dilution ≠ plasma cfDNA.

## Direction

- **Canonical:** tumor-only MRD discovery and characterization on long-read HCC1395 first;
  the matched normal enters only for retrospective validation or benchmarking.
- **Deprecated:** do not revive the seam-stitching / N50-preserving phasing proposal as the
  thesis storyline.
- **Priority order:** weekly research evidence → response to feedback → thesis progress →
  reproducibility → automation.

## Recording work

Every claim needs provenance, uncertainty and stable ids linking
question → hypothesis → experiment → evidence → finding → decision → week. Records live in
`research/`; the shapes are in `orchestration/schemas/record-shapes.md`.

Use the skills rather than improvising: `.skills/daily-work-summary` at the end of a day,
`.skills/experiment-design` before a run, `.skills/data-qc` before spending compute,
`.skills/research-analysis` after output exists, `.skills/weekly-report-builder` before a
meeting.

## Definition of done

Report: the outcome, the files changed, the verification commands and their results, any
unresolved assumption, and the next smallest useful step.

## Validate before committing

```bash
./scripts/run-tests.sh          # python tests, then site lint + tests
cd site && npm run lint         # includes research-record validation
```
