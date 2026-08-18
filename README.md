# Tumor-only long-read MRD — research workspace

**Research direction:** tumor-only long-read MRD through **haplotype-conditioned native
methylation evidence**.

> After accounting for sequence and haplotype context, does native methylation provide
> incremental evidence for detecting tumor-derived molecules at low tumor fractions?

The load-bearing word is *incremental*. The question is not whether methylation is
informative, but whether it is informative **after** sequence and haplotype have been used.

Start with [`docs/research/00_scope.md`](./docs/research/00_scope.md).

---

## Layout

| Path | What it is |
|---|---|
| [`docs/research/`](./docs/research) | the research contract — scope, paper patterns, gap, hypotheses, evaluation plan, claim boundaries, decision log |
| [`docs/repo_audit.md`](./docs/repo_audit.md) | Phase 0 audit, including the data-feasibility findings |
| [`docs/migration_plan.md`](./docs/migration_plan.md) | what moved, what did not, and why |
| `mrd-longphase/` | the analysis workspace — `src/` library, `workflow/` pipelines, `config/`, `tests/`, `experiments/` |
| `research/` | the research OS record store — `suggestions/`, `daily-logs/`, `evidence/`, `weekly-reports/`, plus derived manifests the site reads |
| `site/` | the Astro site: research dashboard, trackers and the weekly report deck |
| [`docs/RESEARCH_OS.md`](./docs/RESEARCH_OS.md) | the weekly working loop — after the meeting, every day, before the meeting |
| `tools/` | small repo-level generators — currently the PowerPoint research report |
| `legacy/` | preserved earlier work, not maintained ([`legacy/README.md`](./legacy/README.md)) |

Engineering context lives in `docs/ARCHITECTURE.md`, `docs/DATA_GOVERNANCE.md`,
`docs/DECISIONS.md`, `docs/USER_CONTEXT.md`.

## Where the project actually stands

| | |
|---|---|
| Native methylation present in every dilution BAM | **verified** — 100% of 200 sampled reads carry MM/ML, both `C+m` and `C+h` |
| Per-read evaluation-only source labels recoverable | **verified** — 28/28 assigned, 0 name collisions, in one pilot window |
| Haplotags (HP/PS) | **absent everywhere** — phasing has not been run. This gates H1 |
| H1 acceptance thresholds | **unset by design** — `config/experiments/h1_feasibility.yaml`, deliberately `null` |
| Any experimental result | **none yet** |

The single blocking task is haplotagging the four dilution BAMs.

---

## Execution guide

### 0. Check the environment first

```bash
cd mrd-longphase
python3 workflow/tools/report_environment.py \
    --check-data config/datasets/hcc1395_dilution.yaml
```

Reports every tool version, flags blocking absences, and confirms each input path is
readable. Paste the output into the run's experiment manifest.

Python dependencies: `pip install -r mrd-longphase/requirements.txt`
(`pysam`, `numpy`, `matplotlib`, `PyYAML` — nothing else is required).

### 1. Run the tests

```bash
./run-tests.sh            # everything
./run-tests.sh python     # 113 unit + 6 integration
./run-tests.sh site       # astro check + content validation + vitest
```

Every Python test runs against synthetic BAM fixtures in `mrd-longphase/tests/fixtures/`.
**No test touches a real BAM.**

### 2. Set the thresholds — before running anything

`config/experiments/h1_feasibility.yaml` ships with every threshold `null`, and the runner
**refuses to execute** rather than substituting a default. That is deliberate: a defaulted
threshold is an unrecorded research decision, and a threshold chosen after seeing results
turns an exploratory finding into a false confirmatory one. Record the reasoning in
[`docs/research/decision_log.md`](./docs/research/decision_log.md).

### 3. Haplotag the dilution BAMs *(not yet done — the blocking step)*

`longphase` is not on PATH; the binary is at
`week1/experiment/external/longphase_develop/longphase`. Decide and record whether to
haplotag whole BAMs or only candidate-region slices — region-scoped is far cheaper but
yields shorter phase blocks.

### 4. Extract joint-molecule evidence

Start with **one small region**, not a genome.

```bash
cd mrd-longphase
python3 workflow/joint_molecule/extract_joint_molecules.py \
    --bam        <haplotagged mixture BAM> \
    --candidates results/tumor_only/HCC1395/candidate_pass_snvs.tsv \
    --config     config/experiments/h1_feasibility.yaml \
    --sample-id  HCC1395_TF1e-2_25x_rep1 \
    --dilution   1e-2 \
    --region     chr1:1000000-2000000 \
    --outdir     results/joint_evidence/HCC1395_TF1e-2_25x_rep1
```

Add evaluation-only labels with `--label-tumor-bam` / `--label-normal-bam`. Scale up with
`--region-bed` or `--contig chr1 --chunk-size 1000000`.

Region-scoped, resumable (completed regions are skipped), deterministic (a re-run
byte-reproduces its partition). The BAM is never loaded whole.

### 5. Report the feasibility funnel — the first scientific decision

```bash
python3 workflow/feasibility_funnel/report_funnel.py \
    --evidence-dir results/joint_evidence/HCC1395_TF1e-2_25x_rep1 \
    --config       config/experiments/h1_feasibility.yaml \
    --outdir       results/feasibility/HCC1395_TF1e-2_25x_rep1
```

Produces stage counts stratified seven ways, methylation distributions, and an H1 verdict
block. With thresholds unset it reports `BLOCKED` — it never guesses a pass.

**Do not proceed to modelling until H1 is accepted.**

### 6. The site — a research operating system

```bash
./run-site.sh dev     # or: build | preview | check | test
```

| Route | What it is |
|---|---|
| `/` | **dashboard** — current question, hypothesis, phase, unresolved issues, suggestions awaiting action, work and evidence this period, link to the latest weekly report |
| `/suggestions/` | **suggestion tracker** — every professor/lab suggestion, answered point by point; incomplete and blocked items stay visible |
| `/logs/` | **daily logs** — action, evidence, observation, interpretation, decision and failure kept apart |
| `/evidence/` | **evidence registry** — artifacts with provenance and an honest verification level |
| `/weekly-reports/` | **weekly report** — a slide deck compiled from the records, with presentation mode and print/PDF |
| `/research-narrative/` | the MRD scientific narrative: problem → literature → ClairS-TO candidates → hypothesis, with IEEE references. A normal scrolling page, not a deck |
| `/research-notes/` | older working notebook — weekly walkthrough, research objects, literature map, teaching modules, roadmap |

Daily and weekly work:

```bash
cd site
npm run new:log -- 2026-08-18            # new daily log record
npm run new:suggestion -- "..."          # capture a suggestion from the meeting
npm run new:evidence -- "..."            # register an artifact
npm run validate:research                # cross-record + provenance checks
```

### 7. The PowerPoint research report

```bash
python3 tools/build_research_deck.py        # → research/reports/mrd-research-report.pptx
```

Twelve slides covering the same narrative as `/research-narrative/`, built entirely from
native PowerPoint objects — shapes, tables and charts with their own embedded worksheets —
so every element stays editable. Candidate counts and distributions are read from
`research/manifests/week-001-candidate-landscape.json`, and the bibliography is checked
against `site/src/data/references.ts` before the file is written, so the deck cannot quietly
disagree with the site.

---

Or use the project skills: `/daily-work-summary` to turn a day's notes into a structured log,
`/weekly-report-builder 2026-W34` to compile the meeting deck. Both refuse to invent evidence
and label what is missing. The loop is documented in
[`docs/RESEARCH_OS.md`](./docs/RESEARCH_OS.md).

---

## Rules that are enforced, not merely stated

| Rule | Enforcement |
|---|---|
| Source data is read-only | nothing in the code opens a source path for writing; `.gitignore` blocks `*.bam`, `*.vcf.gz`, `*.fasta` and generated output trees |
| Evaluation labels never reach a model | the field is named `source_label_for_evaluation_only`; no feature builder reads it; a test asserts two rows differing only in label produce identical features |
| No leakage across splits | there is no random-split function; splitting is by chromosome, region or sample, and a test asserts no region spans a split |
| No undefined threshold silently defaults | `ExtractionConfig.from_dict` raises; the funnel reports `BLOCKED` |
| No fabricated results | `actual_results` stays `null` until a run produces numbers; site pages render explicit pending-experiment states |
| Work is not "done" without evidence | `validate:research` rejects a completed suggestion with no evidence or result, and a completed daily-log action with no artifact and no written reason |
| Missing evidence is shown, not hidden | the dashboard, the response matrix and the weekly deck render explicit `Missing evidence` / `Not completed` / `Blocked` / `Requires researcher interpretation` labels |
| Evidence is not "verified" because an AI read it | `verified` requires `verified_by` and `verified_on`; the validator and a test enforce it |
| 5mC and 5hmC stay separate | separate schema columns, separate features, never summed |
| Runs are reproducible | tool versions and an input-manifest id on every record; gzip `mtime=0` and fixed float precision make partitions byte-reproducible |

## What this project cannot claim

HCC1395 genomic dilution is **controlled low-tumor-fraction method development**. It is not
plasma cfDNA, and it does not establish clinical MRD performance. With one replicate per
dilution level and a single blank, limit of blank and limit of detection are **not
estimable**. See [`docs/research/05_claim_boundaries.md`](./docs/research/05_claim_boundaries.md),
which is binding on every output of this project.

## Upstream baseline

The Week 1 ClairS-TO tumor-only candidate characterization (48,819 PASS SNVs) is retained as
the upstream baseline that supplies candidate loci. The Phase 0 validation
(`mrd-longphase/reports/weekly/2026-08-10_phase0_caller_and_detection_validation.md`) recorded
precision 0.707 / recall 0.732 / F1 0.719 against pre-locked targets of ≥0.90 / ≥0.80 / ≥0.85 —
an honest miss, and the practical reason for asking whether other per-molecule evidence helps.
