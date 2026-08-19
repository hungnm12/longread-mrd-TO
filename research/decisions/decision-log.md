# Decision log — research direction

Append-only. Newest entries at the top. Every entry records what was decided, why, what was
rejected, and what would reopen it.

Related: [`../DECISIONS.md`](./project-decisions.md) holds engineering/architecture decisions from
the earlier phase; this file holds **research-direction** decisions. Neither supersedes the
other.

---

## 2026-08-16 — Per-read source labels are recoverable; H2 is testable

- **Decision:** treat per-read tumor/normal source labels as **available, evaluation-only**
  ground truth, recovered by read-name membership against `HCC1395.bam` and `HCC1395BL.bam`.
- **Evidence:** the mixture BAMs carry no `@RG`, but their `@PG` chain shows they were built
  by `samtools view -s` subsampling of the two source BAMs followed by `samtools merge`,
  both of which preserve read names. Pilot check at `chr1:1,000,000-1,002,000` on
  `TF1e-2_25x`: 28/28 reads assigned (1 tumor, 27 normal), **0 unassigned**, **0 read-name
  collisions** between the two sources. Recorded in `../repo_audit.md` §14.4.
- **Why it matters:** without labels, H2 and H3 are untestable and the thesis reduces to
  descriptive work. With them, the ablation design becomes possible.
- **Rejected alternative:** using SEQC2 truth VCF as the only evaluation anchor — that
  labels *loci*, not *molecules*, and the unit of analysis here is the molecule.
- **Status:** mechanism confirmed, **rate not measured**. One 2 kb window proves nothing
  about genome-wide assignment rate or about tumor fraction.
- **Revisit trigger:** if genome-scale assignment finds unassigned reads (supplementary
  alignments, secondary alignments, or name collisions at scale), the labelling method needs
  revision before H2 runs.

## 2026-08-16 — Native methylation survives into the dilution series

- **Decision:** proceed with the haplotype-conditioned methylation direction; the data
  supports it.
- **Evidence:** 200-read samples at `chr1:1,000,000-1,010,000` in all four dilution BAMs and
  the pure tumor BAM: **100% of sampled reads carry `MM` and `ML`**, with both `C+m?` (5mC)
  and `C+h?` (5hmC) codes. `minimap2 -ax map-ont -y` preserved basecaller tags through
  alignment and `samtools merge` preserved them into the mixtures. Recorded in
  `../repo_audit.md` §14.2.
- **Why it matters:** this was the single largest binary risk to the whole direction. If the
  dilution BAMs had been built from a non-modified basecall, the central question would have
  been unanswerable on existing data and would have required regenerating ~325 GB of mixtures.
- **Rejected alternative:** planning a re-basecall / re-mixing effort as a prerequisite —
  unnecessary.
- **Revisit trigger:** if the per-CpG probability distribution turns out to be degenerate
  (e.g. all probabilities at the extremes, or systematic dropout in the mixtures relative to
  the pure tumor), re-examine whether tags survived *meaningfully* and not just structurally.

## 2026-08-16 — Haplotagging is the missing upstream step

- **Decision:** LongPhase/WhatsHap phasing + haplotagging of the four dilution BAMs is the
  first pipeline work of the new direction, and it gates H1.
- **Evidence:** zero reads carry `HP` or `PS` in any BAM inspected (`../repo_audit.md` §14.3).
- **Consequence:** H1 cannot be evaluated until this runs. It is compute the project has not
  yet spent, on ~325 GB of input.
- **Rejected alternative:** deriving haplotype context from the ClairS-TO internal phasing —
  ClairS-TO uses LongPhase internally for calling, but does not emit haplotagged BAMs for the
  dilution samples in any discovered output.
- **Open:** whether to haplotag whole BAMs or only candidate-region slices. Region-scoped
  haplotagging is far cheaper but produces shorter phase blocks. To be decided before H1 runs.
- **Revisit trigger:** if `haplotag_rate` is low, revisit tool choice and parameters before
  concluding H1 fails.

## 2026-08-16 — Direction changed to haplotype-conditioned native methylation

- **Decision:** the primary research storyline becomes *tumor-only long-read MRD through
  haplotype-conditioned native methylation evidence*. The Week 1 ClairS-TO candidate
  characterization is reclassified as **upstream baseline**.
- **Source:** the project brief at `/big8_disk/hung114/ONT_MRD/modify.md`.
- **Why it is not a discard:** the candidate landscape work supplies the loci the new
  pipeline iterates over, and `week4/phase0_results.md` — which honestly recorded
  ClairS-TO tumor-only precision 0.707 / recall 0.732 / F1 0.719 against pre-locked targets
  of ≥0.90 / ≥0.80 / ≥0.85 — is precisely the motivation: the sequence-only baseline is
  demonstrably imperfect, so asking whether other per-molecule evidence helps is well-founded.
- **Rejected alternatives:** continuing high-VAF clonality investigation (explicitly out of
  scope); adding CNA/fragmentomics (out of scope); jumping to a learned per-molecule model
  before feasibility is established (the gated H1→H4 structure exists to prevent this).
- **Revisit trigger:** H1 rejection with all pivots exhausted.

## 2026-08-16 — Gated hypotheses, configurable thresholds, no pre-filled results

- **Decision:** adopt the H1→H2→H3→H4 gate; set **no** numeric acceptance threshold in
  documentation; require every threshold to be resolved from experiment configuration and
  written into the manifest *before* the run; make an undefined threshold a hard stop rather
  than a defaulted value.
- **Reason:** the project already demonstrated the right instinct in `week4/phase0_results.md`
  by locking targets before results and then reporting an honest failure. This formalizes it.
- **Revisit trigger:** none — this is a process commitment, not a research choice.

---

## Open items awaiting a decision

| Item | Blocks | Owner decision needed |
|---|---|---|
| Repository layout: reuse `mrd-longphase/` vs. flatten to the brief's tree | Phases 3–8 file locations | see [`../migration_plan.md`](../../archive/migration_plan.md) §4 |
| Whole-BAM vs. region-scoped haplotagging | H1 cost and phase-block length | after a cost estimate |
| Joint-molecule storage format (TSV / JSONL / Parquet) | Phase 3 | `pyarrow` is absent from the environment; trade-off documented in the Phase 3 contract |
| Literature search to promote the candidate gap | citing the gap as established | [`02_research_gap.md`](../knowledge/research-gap.md) §"Next action" |
| Which chromosomes are held out for testing | Phase 5 splits | before any model is fit |

## Entries that must never appear here

A decision recorded *after* the result it was supposed to gate. If a threshold or split was
chosen after seeing data, the honest entry is "threshold set post hoc — this result is
exploratory, not confirmatory", and the experiment is re-run confirmatorily on held-out data.
