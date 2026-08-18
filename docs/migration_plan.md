# Migration plan — Phase 0

Date: 2026-08-16
Companion to [`repo_audit.md`](./repo_audit.md).
Status: **proposed — awaiting approval for the rows marked `needs approval`.**

---

## 1. The one structural decision

The brief lists a preferred logical structure (`src/`, `pipelines/`, `configs/`,
`experiments/`, `results/`, `site/`, `legacy/` at the repository root) **and also** says:

> Adapt to the existing repository instead of blindly forcing a new structure. …
> If the current repository already has equivalent locations, reuse them.

These pull in opposite directions here, because `mrd-longphase/` already *is* that
structure, one level down. Two options:

### Option A — Reuse `mrd-longphase/` as the analysis root  ✅ recommended

Keep every existing path. Add the new subpackages into the empty slots that already exist.

```
mrd/
├── docs/            research/, weekly/, glossary/, repo_audit.md, migration_plan.md
├── mrd-longphase/
│   ├── config/      + datasets/, experiments/, models/
│   ├── src/         candidates/ (exists) + io/, phasing/, methylation/,
│   │                joint_evidence/, provenance/  and fill evidence/, models/, evaluation/
│   ├── workflow/    tumor_only/ (exists) + joint_molecule/, feasibility_funnel/,
│   │                separability/, ablation/, dilution_eval/  and fill phasing/, methylation/
│   ├── tests/       unit/, integration/, fixtures/            ← new
│   ├── experiments/ registry/, templates/                     ← new
│   ├── data/, results/, figures/, reports/, notebooks/        (exist)
├── research/        (exists — small derived evidence for the site)
├── site/            (exists)
└── legacy/                                                    ← new
```

- **Files moved: 0.** No import breaks, no path rewrites, no invalidated documentation.
- `workflow/` plays the role the brief calls `pipelines/`; the numbered stage names
  (`00_data_audit` … `04_dilution_evaluation`) become subdirectory names inside it.
- Cost: the tree is one level deeper than the brief's sketch, and the name
  `mrd-longphase` is now slightly off (the project is no longer only about LongPhase).

### Option B — Flatten to the brief's tree

Move `mrd-longphase/src` → `src/`, `mrd-longphase/workflow` → `pipelines/`,
`mrd-longphase/config` → `configs/`, and so on.

- **Files moved: ~45 tracked + all untracked results/figures.**
- Breaks: `build_candidates.py`'s `REPO_ROOT` computation, `smoke_test_build_candidates.py`'s
  path assembly, `mrd-longphase/README.md` (whole structure section), `docs/RESEARCH_SCOPE.md`
  seed-evidence paths, `research/manifests/week-001-*.json` `source_files[].path`,
  `site/src/content/**` any path references, `reports/change_log.tsv` semantics.
- Gains: matches the brief's diagram literally; one less nesting level.

**Recommendation: Option A.** The brief's own adaptation clause covers it, priority order
puts "preservation of existing work" at #2 against "website/UI structure" at #6, and the
existing empty packages (`src/evidence/`, `src/models/`, `src/evaluation/`,
`workflow/phasing/`, `workflow/methylation/`) were clearly designed for exactly this
direction. Option B spends a large breakage budget to satisfy a diagram.

If Option A is chosen, an optional cosmetic follow-up is `git mv mrd-longphase analysis`
— a single directory rename, 6 documentation references to update. Listed separately below
so it can be approved or refused independently.

---

## 2. Migration table

`action` values: `keep` · `rename` · `move` · `wrap` · `deprecate` · `archive` ·
`remove only after approval`

### 2.1 Inside the Git repository — no approval needed (additive / repair)

| Current path | Proposed path | Reason | Action |
|---|---|---|---|
| `mrd-longphase/src/candidates/` | unchanged | upstream baseline still needed to enumerate candidate loci | keep |
| `mrd-longphase/src/evidence/` (empty) | same, populated | becomes the joint-molecule record layer (Phase 3) | keep + fill |
| `mrd-longphase/src/models/` (empty) | same, populated | becomes the A–F ablation ladder (Phase 5) | keep + fill |
| `mrd-longphase/src/evaluation/` (empty) | same, populated | becomes metrics + leakage-safe splitting (Phase 5) | keep + fill |
| `mrd-longphase/src/markers/` (empty) | same | compendium/marker logic from `week3` lands here later | keep |
| — | `mrd-longphase/src/io/` | BAM/VCF region readers shared by phasing + methylation | create |
| — | `mrd-longphase/src/phasing/` | HP/PS parsing, phase-set bookkeeping | create |
| — | `mrd-longphase/src/methylation/` | MM/ML → per-CpG probabilities, read-end distances | create |
| — | `mrd-longphase/src/joint_evidence/` | assembles allele + haplotype + methylation + QC per molecule | create |
| — | `mrd-longphase/src/provenance/` | tool versions, input manifest ids, run hashing | create |
| `mrd-longphase/workflow/tumor_only/` | unchanged | the ClairS-TO candidate stage | keep |
| `mrd-longphase/workflow/phasing/` (.gitkeep) | same, populated | LongPhase phase + haplotag on dilution BAMs | keep + fill |
| `mrd-longphase/workflow/methylation/` (.gitkeep) | same, populated | methylation extraction stage | keep + fill |
| `mrd-longphase/workflow/dilution/` (.gitkeep) | same, populated | dilution-level evaluation driver | keep + fill |
| `mrd-longphase/workflow/{matched_normal,truth_validation,marker_selection,mrd_detection}/` | unchanged | out of current scope but part of the thesis arc; empty scaffolds cost nothing and are documented | keep |
| — | `mrd-longphase/workflow/joint_molecule/` | Phase 3 extraction CLI | create |
| — | `mrd-longphase/workflow/feasibility_funnel/` | Phase 4 funnel CLI | create |
| — | `mrd-longphase/workflow/ablation/` | Phase 5 driver | create |
| — | `mrd-longphase/tests/{unit,integration,fixtures}/` | no test tree exists today | create |
| `mrd-longphase/workflow/tumor_only/smoke_test_build_candidates.py` | `mrd-longphase/tests/integration/test_build_candidates_smoke.py` | belongs in the test tree; keeps working via the same `REPO_ROOT` idiom | **move** (needs approval — 1 file, 1 doc reference) |
| — | `mrd-longphase/config/datasets/`, `config/experiments/`, `config/models/` | dilution BAM paths currently exist in no config file | create |
| `mrd-longphase/config/tumor_only_hcc1395.yaml` | same, `output.*` repaired | the four `output.*` paths point at `ONT_MRD/mrd-longphase/`, which **does not exist** | **repair in place** |
| — | `mrd-longphase/experiments/{registry,templates}/` | Phase 6 manifests | create |
| `docs/{ARCHITECTURE,DATA_GOVERNANCE,DECISIONS,RESEARCH_SCOPE,USER_CONTEXT}.md` | unchanged | still accurate; `RESEARCH_SCOPE.md` gains a pointer to the new direction | keep + amend |
| — | `docs/research/*.md` (7 files) | Phase 1 research contract | create |
| — | `docs/weekly/`, `docs/glossary/` | brief's preferred doc layout | create when first used |
| `research/manifests/`, `research/schemas/`, `research/outputs/` | unchanged | already the small-derived-evidence channel the site reads | keep |
| `site/**` | unchanged | stack reused; Phase 7 adds routes + content, edits nothing existing destructively | keep + extend |
| `site/src/{layouts/BaseLayout.astro,pages/index.astro,styles/global.css}` | unchanged | **uncommitted user work in progress** — build on top, never revert | keep (protected) |
| `run-site.sh` | unchanged, then `git add` | untracked helper the user wrote; useful | keep + track |
| `.gitignore` | extended | no defensive rules for `*.bam`, `*.vcf.gz`, `*.parquet`, results trees | amend |
| — | `mrd-longphase/pyproject.toml` or `requirements.txt` | no Python dependency declaration exists | create |
| `.agent-context/` | unchanged | git-ignored local agent context | keep |

### 2.2 Outside the Git repository — needs approval

Everything below lives in `/big8_disk/hung114/ONT_MRD/` but not in Git. Nothing is deleted.

| Current path | Proposed path | Reason | Action |
|---|---|---|---|
| `week1/`, `week3/`, `week4/` (704 GB) | **unchanged** | run outputs and tool installs; moving 704 GB is expensive and pointless. Instead register them | keep (register only) |
| `week3/compendium/v1.0/`, `week3/tagging/`, `week3/tagging.md`, `week3/pipeline.md` | referenced from `mrd-longphase/data/metadata/run_registry.tsv` | the tumor-only tagging/compendium mechanism is real prior work with no repository pointer | wrap (add manifest entry) |
| `week4/phase0_results.md`, `week4/phase0_conduct.md` | copy → `mrd-longphase/reports/weekly/2026-08-10_phase0_caller_and_detection_validation.md` | the honest pre-locked-threshold caller validation (P 0.707 / R 0.732 / F1 0.719 vs. ≥0.90/≥0.80/≥0.85) is the project's strongest provenance artifact and is invisible to Git | **archive into repo** (copy, ~10 kB, original untouched) |
| `week4/expB/{mrd_score.py,mrd_calls.tsv,score_calls_compendium.tsv,titration.png}` | copy small files → `legacy/week4_expB/` | earlier sample-level MRD scoring; upstream baseline for H4's aggregation step | **archive into repo** (copy) |
| `week2/key.md`, `week2/note.md`, `week1/note.md`, `rand/phases.md` | `legacy/notes/` | study notes; keep readable, keep out of the new storyline | archive (copy) |
| `w1_redo/weekly_report_clairsto/scripts/*` | `legacy/w1_redo_scripts/` | duplicate of `src/candidates/`; preserve history/purpose, do not maintain | deprecate + archive (copy) |
| `w1_redo/weekly_report_clairsto/*.{png,tsv,txt,pptx}` | **unchanged** | duplicate outputs of tracked results; no value in copying | keep in place |
| `mrd_reproduce.py`, `mrd_reproduce.md` | `legacy/mrd_reproduce/` | scratch from the original paper-reproduction direction; superseded | deprecate + archive (copy) |
| `struct.md` | — | superseded by `mrd-longphase/README.md`, which documents the realized tree | deprecate (leave in place, note in `legacy/README.md`) |
| `AI_AGENT_MRD_TUMOR_ONLY_FLOW.md` | — | identical copy already at `mrd/.agent-context/` | deprecate (leave in place) |
| `modify.md` | `docs/research/decision_log.md` cites it | the brief that triggered this refactor | keep in place, cite |
| `.agents/skills/` | unchanged | local agent skill cache | keep |
| any file under `/big8_disk/data`, `/big8_disk/ref`, `/bip7_disk` | **unchanged** | read-only, other users' ownership | keep — never touch |

### 2.3 Explicitly not proposed

- No `git rm`, `git reset --hard`, `git checkout --force`, rebase, or history rewrite.
- No deletion of any file, in or out of Git.
- No re-indexing, copying, or moving of any BAM, FASTA, or reference file.
- No commit or push (the brief requires an explicit request).

---

## 3. Impact assessment

| Option A row class | Files touched | Breakage risk |
|---|---|---|
| Additive creation (new dirs/modules/docs) | ~0 existing | none |
| `config/tumor_only_hcc1395.yaml` repair | 1 | none — the current values are already broken |
| Smoke-test move | 1 + 1 doc line | low, single reference |
| `legacy/` archival copies | 0 originals modified | none — copies only |
| `.gitignore` extension | 1 | none |

Under Option A this migration is **low impact**: one file moved, one file repaired,
everything else additive or a copy. The brief's stop-and-ask rule
("if a reorganization would move many files, overwrite files, break paths, or invalidate
existing workflows") is therefore triggered only by **Option B**.

---

## 4. Approval requested

1. **Option A or Option B?** (recommendation: A)
2. If A: also rename `mrd-longphase/` → `analysis/`? (recommendation: no, for now)
3. Approve moving `smoke_test_build_candidates.py` into `tests/integration/`?
4. Approve copying `week4/phase0_results.md`, `week4/expB/` small files, and the study
   notes into the repository under `legacy/` and `reports/weekly/`?

Phases 3–8 all land in locations decided by question 1, so it is the only genuinely
blocking one.
