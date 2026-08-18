# Repository audit — Phase 0

Date: 2026-08-16
Auditor: automated inspection (metadata + small-region reads only; no full-genome runs)
Purpose: establish what exists before refactoring toward **tumor-only long-read MRD through
haplotype-conditioned native methylation evidence**.

---

## 1. Where the repository actually is

The working directory `/big8_disk/hung114/ONT_MRD` is **not** a Git repository. It is a
server workspace. The Git repository is one level down:

| Location | Git | Size | Nature |
|---|---|---|---|
| `/big8_disk/hung114/ONT_MRD` | no | ~704 GB | server workspace (data + run outputs + notes) |
| `/big8_disk/hung114/ONT_MRD/mrd` | **yes** (`origin` = `github.com/hungnm12/longread-mrd-TO.git`) | 241 MB | the versioned project |

Everything in this audit that says "the repository" means `ONT_MRD/mrd/`.

Git state: one commit (`30e3abe Initial MRD research OS`) on `main`, tracking `origin/main`.
Three modified files and one untracked file are uncommitted:

```
 M site/src/layouts/BaseLayout.astro
 M site/src/pages/index.astro
 M site/src/styles/global.css
?? run-site.sh
```

These are **user changes and are preserved untouched** by this audit.

---

## 2. Current repository structure

```
mrd/
├── README.md                    # two-layer explanation (analysis + site)
├── .gitignore
├── run-site.sh                  # untracked helper; dev/build/preview/check/test
├── .agent-context/              # git-ignored: AGENTS.md, brief, flow doc, skills-lock
├── docs/                        # ARCHITECTURE, DATA_GOVERNANCE, DECISIONS,
│                                # RESEARCH_SCOPE, USER_CONTEXT
├── research/                    # manifests/ schemas/ outputs/  (small derived evidence)
├── mrd-longphase/               # the analysis workspace
│   ├── config/                  # config.example.yaml, tumor_only_hcc1395.yaml
│   ├── src/                     # candidates/{extract,qc}.py + empty markers, evidence,
│   │                            # models, evaluation packages
│   ├── workflow/                # tumor_only/ populated; phasing, methylation, dilution,
│   │                            # marker_selection, matched_normal, truth_validation,
│   │                            # mrd_detection are .gitkeep only
│   ├── data/metadata/           # input TSV + server_resources.md
│   ├── results/tumor_only/HCC1395/   # 4 small tracked tables
│   ├── figures/tumor_only/      # 6 PNGs
│   └── reports/                 # change_log.tsv + weekly/2026-08-13_*.md
└── site/                        # Astro 5 static research site
    ├── src/content/             # weeks, papers, questions, hypotheses, experiments,
    │                            # runs, results, decisions, glossary  (Markdown + zod)
    ├── src/pages/               # index, literature, roadmap + 8 dynamic [slug] routes
    ├── src/components/          # Badge.astro, Callout.astro
    ├── scripts/validate-content.mjs
    └── tests/content.test.ts
```

---

## 3. Current scientific storyline

The repository today tells a **Week 1 tumor-only SNV candidate-characterization** story:

> What does the tumor-only ClairS-TO candidate landscape look like, and which evidence
> promotes a candidate to a reliable marker without matched normal at discovery time?

Recorded results (`research/manifests/week-001-candidate-landscape.json`,
`mrd-longphase/results/tumor_only/HCC1395/`):

- 3,169,996 ClairS-TO records → 48,819 PASS SNVs (1.54%)
- median depth 80× (IQR 59–106), median VAF 0.461 (IQR 0.292–0.779), median ALT support 35
- `corr(VAF, depth) = −0.419`, `corr(ALT, depth) = 0.328`, `corr(ALT, VAF) = 0.613`

The storyline is explicitly **descriptive**; `docs/RESEARCH_SCOPE.md` defers high-VAF
interpretation and forbids equating PASS SNV with true somatic.

**Relation to the new direction:** this is *upstream baseline*, not the main storyline.
It supplies the candidate loci that the joint-molecule extractor will iterate over. It is
kept, reframed, and cited — not deleted.

---

## 4. Existing scripts and their purpose

| Path | Purpose | Verdict |
|---|---|---|
| `mrd-longphase/src/candidates/extract.py` (100 L) | ClairS-TO VCF → PASS-SNV candidate table; `summarize_counts` | **reusable as-is** — clean, side-effect-free, pysam, documents FORMAT derivation |
| `mrd-longphase/src/candidates/qc.py` (309 L) | depth/VAF/ALT stats, binning, 6 matplotlib plots | **reusable**; plotting helpers transfer to funnel reporting |
| `mrd-longphase/workflow/tumor_only/build_candidates.py` (151 L) | CLI wiring; writes tables, figures, weekly report, change-log append | **reusable pattern** — the `REPO_ROOT` sys.path insert and change-log append are the provenance idiom to keep |
| `mrd-longphase/workflow/tumor_only/run_clairs_to.sh` | ClairS-TO tumor-only invocation; externalizes tool paths via env vars; writes `tool_versions.txt` and `run.log` | **reusable**; already the correct env-var pattern |
| `mrd-longphase/workflow/tumor_only/smoke_test_build_candidates.py` | synthetic 4-record VCF → end-to-end CLI smoke | **reusable**; the only test on the Python side |
| `site/scripts/validate-content.mjs` | cross-reference + provenance validation of content collections | **reusable** — this is the site's correctness gate |
| `site/tests/content.test.ts` | vitest over the validator | **reusable** |
| `../mrd_reproduce.py` (outside repo, 9.8 kB) | earlier paper-reproduction scratch | **legacy** — untracked, outside Git |
| `../w1_redo/weekly_report_clairsto/scripts/*` | earlier duplicate of extract + QC + pptx | **duplicate/legacy** of `src/candidates` |

Empty-but-declared Python packages: `src/markers/`, `src/evidence/`, `src/models/`,
`src/evaluation/` (all `__init__.py` only). Empty workflow stages: `phasing/`,
`methylation/`, `dilution/`, `marker_selection/`, `matched_normal/`, `truth_validation/`,
`mrd_detection/` (`.gitkeep` only).

**These empty packages are exactly where the new direction lands** — `evidence/` for
joint-molecule records, `models/` for the ablation ladder, `evaluation/` for metrics,
`workflow/phasing` + `workflow/methylation` for the missing upstream steps.

---

## 5. Reusable components (ranked)

1. **Astro content-collection system** (`site/src/content.config.ts`) — zod schemas for
   weeks / papers / questions / hypotheses / experiments / runs / results / decisions /
   glossary, with `evidence_state` and `evidence_level` enums. This is already a working
   experiment registry front-end; Phase 6 should extend it rather than invent a parallel one.
2. **`src/candidates/`** — VCF parsing and QC statistics.
3. **`run_clairs_to.sh` env-var pattern** — external tool locations are overridable.
4. **`reports/change_log.tsv`** — append-only provenance row per run.
5. **Smoke-test-with-synthetic-VCF pattern** — extends directly to synthetic BAM fixtures.
6. **`data/metadata/server_resources.md`** — a genuine lab resource registry (truth sets,
   PoN databases, cell lines, other students' work). High value; keep and extend.

---

## 6. Duplicated or obsolete components

| Item | Status | Note |
|---|---|---|
| `../w1_redo/weekly_report_clairsto/scripts/{01_extract_candidates.sh,02_qc_plots.py}` | duplicate | superseded by `src/candidates/` |
| `../w1_redo/weekly_report_clairsto/*.png,*.tsv,qc_stats.txt` | duplicate outputs | same analysis as `mrd-longphase/results/tumor_only/HCC1395/` |
| `../struct.md` | superseded | it is the `mrd-longphase/` tree, already realized and documented in that README |
| `../mrd_reproduce.{py,md}` | legacy | paper-reproduction scratch from the original direction |
| `../AI_AGENT_MRD_TUMOR_ONLY_FLOW.md` | duplicated | a copy already lives in `mrd/.agent-context/` |
| `src/markers/`, `src/models/`, `src/evaluation/`, `src/evidence/` | empty scaffolds | keep — they are the target of Phases 3–5 |
| 14 × `week1/experiment/clairs_smoke_server*/` | run detritus | outside Git; disk only |

Nothing here is deleted by this audit.

---

## 7. Existing website implementation

- **Stack:** Astro `^5.12.0`, TypeScript strict, zod `^4.1.5`, vitest `^3.2.4`,
  `@astrojs/check`. Static output (`build.format: "directory"`). No backend, no database.
- **Content model:** 9 collections, 15 content files today (7 papers, 1 each of
  week/question/hypothesis/experiment/run/result/decision, 1 glossary term).
- **Routes:** `index`, `literature`, `roadmap`, plus `[slug]` routes for 8 collections.
- **Quality gates:** `npm run lint` (= `astro check` + `validate-content.mjs`),
  `npm run test`, `npm run build`.
- **Local hygiene:** `XDG_CONFIG_HOME=$PWD/.config` and `ASTRO_TELEMETRY_DISABLED=1` are
  set on every script — a deliberate sandboxing choice worth preserving.
- **Uncommitted work:** `BaseLayout.astro`, `index.astro`, `global.css` have substantial
  in-progress edits (+334 / −96). Any Phase 7 work must build on top of these, not revert them.

**Verdict: reuse.** The stack already matches the Phase 7 requirements (static, content-first,
print-friendly, route generation). Replacing it would violate the brief and discard the
validator.

---

## 8. Existing results and provenance

| Artifact | Provenance quality |
|---|---|
| `results/tumor_only/HCC1395/{variant_summary,candidate_analysis,candidate_pass_snvs}.tsv`, `qc_stats.txt` | **good** — regenerable from `build_candidates.py`; source VCF recorded in `change_log.tsv` |
| `figures/tumor_only/*.png` (6) | good — regenerable |
| `reports/weekly/2026-08-13_hcc1395_phase1_tumor_only.md` | good — auto-generated, records input VCF |
| `reports/change_log.tsv` | **the provenance backbone** — date, phase, sample, scripts, args, params, outdir, key numbers, caveat |
| `research/manifests/week-001-candidate-landscape.json` | good — points back at source files, `evidence_level: preliminary` |
| `../week4/phase0_results.md` | **high value, outside Git** — thresholds locked *before* results; records ClairS-TO precision 0.707 / recall 0.732 / F1 0.719 vs. the pre-set ≥0.90/≥0.80/≥0.85 targets, i.e. an honest fail |
| `../week3/tagging.md`, `../week3/pipeline.md` | high value, outside Git — the 5-tag compendium mechanism |
| `../week4/expB/*` | MRD titration scoring + `titration.png` — outside Git |

**Gap:** the strongest existing evidence (`week3/`, `week4/`) is **not in the repository**
and not referenced by any manifest. It exists only as server files.

---

## 9. Hard-coded paths

Found by `grep -rn "/big8_disk"` over tracked files:

| File | Line | Path | Problem |
|---|---|---|---|
| `mrd-longphase/config/tumor_only_hcc1395.yaml` | 19–22 | `/big8_disk/hung114/ONT_MRD/mrd-longphase/results/...` | **BROKEN** — that directory no longer exists; the workspace moved to `ONT_MRD/mrd/mrd-longphase/` |
| same | 2, 7, 13 | reference FASTA, tumor BAM, ClairS-TO VCF | acceptable — inputs belong in config, but should be relative-izable |
| `mrd-longphase/reports/change_log.tsv` | 2 | same stale `ONT_MRD/mrd-longphase/...` outdir | historical record — **leave as written**, it documents what actually ran |
| `mrd-longphase/data/metadata/hcc1395_tumor_only_inputs.tsv` | 2–4 | source BAM / FASTA / VCF | correct by design — this file *is* the pointer registry |
| `mrd-longphase/data/metadata/server_resources.md` | many | lab resource inventory | correct by design |
| `mrd-longphase/workflow/tumor_only/run_clairs_to.sh` | 15–18 | ClairS-TO, pypy, longphase under `week1/experiment/` | acceptable — all are `: "${VAR:=default}"` overridable |
| `mrd-longphase/reports/weekly/2026-08-13_*.md` | 13 | input VCF | historical record — leave |

`src/` is clean: **no hard-coded paths in library code**. The existing convention
("never hard-code paths in `src/`") is being followed.

**Action required:** fix the four broken `output.*` lines in `tumor_only_hcc1395.yaml`.

---

## 10. Missing tests and configuration

**Tests**

- Python: one smoke test (`smoke_test_build_candidates.py`), invoked manually. No
  `pytest` installed, no `tests/` directory, no unit tests for `qc.py`'s statistics or
  binning functions, no CI.
- Site: `vitest` covers the content validator only; no route/render tests.

**Configuration**

- No `pyproject.toml` / `setup.py` — `src` is importable only via the `sys.path` hack in
  `build_candidates.py`.
- No Python dependency file (`requirements.txt` / lock). Site has `package-lock.json`. ✅
- No environment capture (conda env / lock) despite multi-tool dependencies.
- No random-seed policy — irrelevant today (nothing stochastic) but required for Phase 5.
- No `configs/datasets/` — dilution BAM paths are not in any config file in the repo.

---

## 11. Dependencies and environment problems

Verified on this server:

| Dependency | State |
|---|---|
| Python | 3.10.12 |
| `pysam` 0.24.0, `numpy` 2.2.6, `matplotlib` 3.10.8, `pyyaml` | ✅ present |
| `pandas`, `pyarrow`, `scikit-learn`, `pytest` | ❌ **absent** |
| `samtools` 1.13, `bcftools`, `tabix` | ✅ on PATH |
| `whatshap` | ✅ `~/.local/bin/whatshap` |
| `longphase` | ⚠️ **not on PATH** — binary exists at `week1/experiment/external/longphase_develop/longphase` |
| `modkit` | ❌ **absent** — no ONT methylation-tag toolkit installed |
| `node` 22.22.2, `npm` | ✅ |
| ClairS-TO v0.5.0 + models + PoN DBs | ✅ under `week1/experiment/` |

**Implications for the new direction**

- Phase 5 (logistic regression / calibrated linear model) needs `scikit-learn`, or must be
  implemented on `numpy` alone.
- Phase 3 storage: `pyarrow` absent → Parquet is not free. See the format trade-off in
  Phase 3's contract document.
- `pytest` absent → the leakage tests required by Phase 5 need it (or `unittest`).
- Methylation parsing can be done directly with `pysam` (`MM`/`ML` tags are readable via
  `read.modified_bases`), so `modkit` is **not** a hard blocker.

---

## 12. Data that must never enter Git

| Path | Size | Why |
|---|---|---|
| `/big8_disk/data/**` (incl. `HCC1395.bam` 292 GB, `HCC1395BL.bam` 149 GB) | ~440 GB | read-only source data, another user's ownership |
| `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` | — | read-only reference |
| `/bip7_disk/pingting114/mixed_bam/HCC1395/**` (4 × ~81 GB) | ~325 GB | read-only dilution BAMs, another user's ownership |
| `ONT_MRD/week1/` | 278 GB | run outputs, tool installs, models |
| `ONT_MRD/week4/` | 268 GB | run outputs |
| `ONT_MRD/week3/` | 158 GB | run outputs incl. 205 MB `markers.tsv`, 98 MB `tagged.vcf.gz` |
| `week1/experiment/external/`, `resources/`, `runtime/` | multi-GB | third-party tools, models, PoN DBs |

The current `.gitignore` covers `node_modules`, `dist`, `.astro`, `.config`,
`__pycache__`, `.agent-context/`. It does **not** yet defensively exclude `*.bam`,
`*.vcf.gz`, `*.fasta`, `*.parquet`, or a `results/` output tree. Phase 8 must add these.

---

## 13. Files that would need migration

Nothing inside `mrd/` requires a move for the new direction: `src/` and `workflow/`
already contain the exact empty slots (`evidence/`, `models/`, `evaluation/`, `phasing/`,
`methylation/`) that Phases 3–5 fill. The migration questions are all about material
**outside** Git. See `migration_plan.md`.

---

## 14. Feasibility findings for the new direction

These were established by direct inspection during this audit (metadata and ≤10 kb region
reads only; no file was modified).

### 14.1 Dilution data — **located**

Not guessed; discovered from `week4/phase0_results.md` and confirmed on disk:

```
/bip7_disk/pingting114/mixed_bam/HCC1395/TF0_25x/TF0_25x.rep1.bam        81.7 GB  (0%, control)
/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-2_25x/TF1e-2_25x.rep1.bam  81.3 GB  (1%)
/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-3_25x/TF1e-3_25x.rep1.bam  81.3 GB  (0.1%)
/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-4_25x/TF1e-4_25x.rep1.bam  81.3 GB  (0.01%)
```

All ~25× coverage, one replicate each, all indexed. Owned by `yulin112`/`pingting114` —
**read-only to this project**.

### 14.2 Native methylation is present in every dilution BAM — **H1 input confirmed**

Sampling 200 reads at `chr1:1,000,000-1,010,000`:

| BAM | reads sampled | with `MM` | with `ML` | with `HP` | with `PS` |
|---|---|---|---|---|---|
| `HCC1395.bam` (pure tumor) | 152 | 152 | 152 | 0 | 0 |
| `TF0_25x` (0%) | 54 | 54 | 54 | 0 | 0 |
| `TF1e-2_25x` (1%) | 59 | 59 | 59 | 0 | 0 |
| `TF1e-3_25x` (0.1%) | 55 | 55 | 55 | 0 | 0 |
| `TF1e-4_25x` (0.01%) | 55 | 55 | 55 | 0 | 0 |

Modification codes present: **`C+m?` (5mC) and `C+h?` (5hmC)**, both on every read
carrying tags. `minimap2 -ax map-ont -y` in the `@PG` chain explains why: `-y` carried the
basecaller tags through alignment, and `samtools merge` preserved them into the mixtures.

This is the single most important feasibility fact in this audit: **the methylation
signal survives into the dilution series**, so the central research question is
observable on the data the project already has.

### 14.3 Haplotags are absent — **the missing upstream step**

No read in any BAM carries `HP` or `PS`. LongPhase/WhatsHap phasing and haplotagging have
**not** been run on the dilution BAMs. This is the main new pipeline work, and it gates H1.

### 14.4 Per-read source labels are recoverable — **evaluation-only truth confirmed**

The mixtures carry **no `@RG` lines**, so source is not directly labelled. But the `@PG`
chain records how they were built:

```
tumor : samtools view -s 201.0030826141  ← HCC1395.tumor.dedup.bam
normal: samtools view -s 111.9382107657  ← HCC1395BL.normal.dedup.bam
        samtools merge -o TF1e-2_25x.rep1.bam <tumor> <normal>
```

The intermediate `dedup_source_v2/` BAMs are **gone**, but the two originals survive at
`/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/{HCC1395.bam, HCC1395BL.bam}`.
Subsampling and merging preserve read names, so source can be recovered by name membership.

Verified at `chr1:1,000,000-1,002,000` on `TF1e-2_25x` (primary alignments only):

| Quantity | Count |
|---|---|
| Reads in mixture | 28 |
| Assigned to tumor source (`HCC1395.bam`) | 1 |
| Assigned to normal source (`HCC1395BL.bam`) | 27 |
| **Unassigned** | **0** |
| **Read-name collisions between the two sources** | **0** |

100% assignment, zero ambiguity. This gives the project a **per-molecule, evaluation-only
`source_label`** — the ground truth H2 and H3 need, without ever entering inference.

> Caveat: this is one 2 kb window. The check must be repeated at scale, and the
> tumor/normal ratio in a window this small carries no information about the true tumor
> fraction. Treat 14.4 as *mechanism confirmed*, not *rate measured*.

### 14.5 Consequence for the research plan

The four gated hypotheses in `docs/research/03_hypotheses.md` inherit these facts:

- **H1** is partly answered already: methylation ✅ present, allele ✅ available from
  ClairS-TO candidates, haplotype ❌ **must be produced**. The open part of H1 is the
  *joint* count — reads carrying all three simultaneously.
- **H2/H3** are testable because 14.4 supplies labels.
- **H4** is testable because 14.1 supplies four tumor fractions plus a 0% control.

---

## 15. Known blockers

1. **Haplotagging not run** on the four dilution BAMs (~325 GB input). This is compute the
   project has not yet spent, and it gates every downstream phase.
2. **`longphase` not on PATH** — the binary exists but is unregistered.
3. **No candidate call set for the dilution BAMs** in the repository. `week3/full_to/` has
   a ClairS-TO run for `TF1e-2` only; `TF1e-3` and `TF1e-4` have none discovered.
4. **`scikit-learn`, `pandas`, `pyarrow`, `pytest` absent** from the Python environment.
5. **Broken output paths** in `config/tumor_only_hcc1395.yaml`.
6. **Strongest prior evidence (`week3/`, `week4/`) is outside Git** and unreferenced by any
   manifest, so it cannot be cited reproducibly.
7. **One replicate per dilution** — no within-level variance is measurable, which caps what
   H4 can claim.

---

## 16. Summary verdict

| Dimension | State |
|---|---|
| Code quality | good; small, documented, side-effect-free library code |
| Structure | already close to the target; empty slots match the new phases |
| Provenance discipline | strong intent (`change_log.tsv`, `evidence_level`, pre-locked thresholds in `week4`), weak coverage (best evidence outside Git) |
| Test coverage | thin — one Python smoke test, one site validator test |
| Environment reproducibility | weak on the Python side, good on the site side |
| Data safety | source data correctly treated as read-only; `.gitignore` needs defensive rules |
| **Feasibility of the new direction** | **supported by the data** — methylation present at all dilutions, evaluation labels recoverable; haplotagging is the missing step |

The refactor is **additive, not destructive**. See `migration_plan.md`.
