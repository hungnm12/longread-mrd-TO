# legacy/

Preserved earlier work. **Nothing here is maintained, and nothing here is part of the
current research storyline** ([`../docs/research/00_scope.md`](../../research/knowledge/scope.md)).

Every file is a **copy**. The originals are untouched in the server workspace at
`/big8_disk/hung114/ONT_MRD/`. Copies were made on 2026-08-16 so that this work is
citable from a Git-tracked location instead of existing only as loose server files.

## Classification

| Directory | Classification | Origin | Why kept |
|---|---|---|---|
| `week4_expB/` | **upstream baseline** | `week4/expB/` | Sample-level MRD titration scoring. `mrd_score.py` is the aggregation step H4 will build on — the existing baseline for turning per-locus evidence into a per-sample score. |
| `w1_redo_scripts/` | **duplicate / deprecated** | `w1_redo/weekly_report_clairsto/scripts/` | Superseded by `mrd-longphase/src/candidates/`. Kept to preserve the history of how the candidate QC was first written, including the PowerPoint report generator, which has no equivalent in the current codebase. |
| `mrd_reproduce/` | **legacy / unrelated to current direction** | `ONT_MRD/mrd_reproduce.{py,md}` | Scratch work from the original direction (reproducing the cfDNA mutational-integration paper, PAPER-001). Superseded when the project moved to tumor-only long-read work. |
| `notes/` | **study notes** | `week1/`, `week2/`, `rand/`, `week4/`, `struct.md` | Learning notes and planning documents. Readable context for how the project's understanding developed. |

## Notes on specific files

- **`week4_expB/mrd_score.py`** — the only file here with forward relevance. H4's aggregation
  step should be compared against it rather than written from scratch.
- **`week4_expB/score_{calls,truth}_compendium.tsv`** were **not** copied (1.7 MB and 1.6 MB,
  regenerable). They remain at `../../week4/expB/`.
- **`notes/struct.md`** — the proposed directory tree that `mrd-longphase/` now realizes.
  Superseded by `mrd-longphase/README.md`, which documents the tree that actually exists.
- **`notes/week4_phase0_conduct.md`** — the *protocol* for the Phase 0 validation. Its
  *results* were judged important enough to live in the reports tree rather than here:
  see [`../mrd-longphase/reports/weekly/2026-08-10_phase0_caller_and_detection_validation.md`](../mrd-longphase/reports/weekly/2026-08-10_phase0_caller_and_detection_validation.md).

## Files deliberately left in place, not copied

| Path | Reason |
|---|---|
| `../../w1_redo/weekly_report_clairsto/*.{png,tsv,txt,pptx}` | duplicate outputs of the tracked `mrd-longphase/results/tumor_only/HCC1395/` tables |
| `../../AI_AGENT_MRD_TUMOR_ONLY_FLOW.md` | an identical copy already exists at `../.agent-context/` |
| `../../week1/`, `../../week3/`, `../../week4/` (704 GB) | run outputs, tool installs, models — registered by manifest, never copied into Git |

## Rule

Do not import from `legacy/`. If something here is needed, port it deliberately into
`mrd-longphase/src/` with tests, and record the decision in
[`../docs/research/decision_log.md`](../../research/decisions/decision-log.md).
