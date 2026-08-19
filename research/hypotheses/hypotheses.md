# 03 — Hypotheses

Status: active
Date: 2026-08-16

Four **gated** hypotheses. Gated means H(n+1) is not attempted until H(n) is accepted.
This ordering exists so the project fails cheaply and early rather than expensively and late.

```text
H1 observation feasibility  ──accept──▶  H2 biological separability
                                              │
                                          accept
                                              ▼
                                   H3 incremental computational value
                                              │
                                          accept
                                              ▼
                                   H4 low-TF detection value
```

## On thresholds

**No numeric acceptance threshold is set in this document.** Every threshold below is named
as a symbol and resolved from configuration at run time
(`configs/experiments/*.yaml`, key `thresholds:`). Thresholds must be written
into the experiment manifest **before** the experiment runs — the pattern already used in
`week4/phase0_results.md`, where targets were locked first and then honestly failed.

Setting a threshold after seeing the result is prohibited by
[`05_claim_boundaries.md`](../knowledge/claim-boundaries.md).

---

# H1 — Observation feasibility

> Enough reads contain allele, haplotype, and methylation information **simultaneously**.

The word doing the work is *simultaneously*. Each signal individually is known to be
available; the joint co-occurrence rate on one molecule is not.

**Required inputs**

- Candidate loci (ClairS-TO tumor-only PASS SNVs, per sample).
- Dilution BAMs at 1%, 0.1%, 0.01% and the 0% control.
- Haplotagged BAMs — **does not exist yet**, must be produced (LongPhase/WhatsHap).
- MM/ML tags — confirmed present on every dilution BAM (see `../repo_audit.md` §14.2).

**Observable outputs**

- The feasibility funnel: all reads → candidate-overlapping → allele-informative →
  haplotagged → methylation-informative → **usable joint-evidence molecules**.
- Stratified by sample, dilution, chromosome/region, candidate, phase set, haplotype family.
- CpGs per read; phase-block coverage and N50; read-length distribution; methylation
  missingness rate; read-end methylation distribution; exclusion-reason histogram.

**Metrics**

| Metric | Definition |
|---|---|
| `joint_yield` | usable joint molecules ÷ candidate-overlapping reads |
| `n_joint[TF]` | absolute usable joint molecules per dilution level |
| `n_joint_per_candidate` | distribution across candidate loci |
| `haplotag_rate` | reads with HP ÷ reads overlapping a phased block |
| `meth_informative_rate` | reads with ≥ `min_cpg_per_read` usable CpGs ÷ reads |
| `phase_block_n50` | phase-set contiguity |

**Confounders**

- Phasing quality degrades where heterozygous germline density is low → `haplotag_rate`
  varies by region for reasons unrelated to tumor biology.
- Read length drives both CpG count per read and haplotagging probability → the three
  filters are **not independent**; the funnel must report the joint survival, not the product.
- Depth is ~25× in dilution BAMs vs ~100× in the pure tumor — yields are not comparable
  across those two.
- Candidate loci come from the pure tumor and are not uniformly distributed.
- MM/ML absence may reflect basecaller behaviour rather than absence of CpGs.

**Acceptance condition**

`n_joint[TF]` ≥ `T_H1_min_molecules` at the 1% level **and** the funnel shows no single
stage collapsing below `T_H1_min_stage_survival`, **and** ≥ `T_H1_min_candidates`
candidate loci contribute at least one joint molecule.

**Rejection condition**

`n_joint` at 1% falls below `T_H1_min_molecules`, or haplotagging yield is so low that
haplotype context is unavailable for the majority of candidate-overlapping reads.

**Next action if accepted** → proceed to H2. Freeze the funnel configuration as the
definition of "usable molecule" for all downstream work.

**Pivot if rejected** — in order of preference:

1. Relax the joint definition: allow methylation from a window around the read rather than
   requiring it on the read (weakens the "same molecule" claim — must be stated).
2. Re-run phasing with alternate parameters / tool (LongPhase ↔ WhatsHap) before concluding.
3. Restrict to genomic regions with high heterozygous density where phasing succeeds, and
   report the reduced breadth honestly.
4. Move up-coverage: use the 100× pure tumor and a synthetic mixture at controlled depth to
   separate "not enough coverage" from "not enough joint information".
5. If none work: the thesis becomes a **negative feasibility result** — a documented account
   of why haplotype-conditioned methylation is not observable at 25× ONT. That is a real
   result and is written up as one, not hidden.

---

# H2 — Biological separability

> Tumor-origin and background reads show reproducible methylation differences **within
> comparable haplotype context**.

"Within comparable haplotype context" is what makes this different from ordinary
differential methylation. Comparing tumor reads to normal reads globally will find
differences; the question is whether differences survive conditioning.

**Required inputs**

- H1's usable joint-molecule table.
- **Evaluation-only** per-read source labels. Mechanism confirmed in `../repo_audit.md` §14.4:
  mixed BAMs carry no `@RG`, but read names are preserved through `samtools view -s` +
  `samtools merge`, and membership against `HCC1395.bam` / `HCC1395BL.bam` assigned 28/28
  reads with 0 collisions in the pilot window.
- Haplotype/phase-set assignment per molecule.

**Observable outputs**

- Methylation summaries (mean probability, methylated-CpG fraction, per-CpG patterns) by
  source label, stratified by haplotype family and phase set.
- Effect sizes with uncertainty, per stratum.
- Reproducibility across chromosomes and across dilution levels.

**Metrics**

| Metric | Definition |
|---|---|
| `delta_meth_within_hap` | tumor-vs-normal methylation difference computed within haplotype strata |
| `effect_size_ci` | bootstrap CI on the above |
| `cross_chrom_consistency` | agreement in sign/magnitude across held-out chromosomes |
| `cross_TF_consistency` | agreement across dilution levels |
| `n_strata_informative` | strata with sufficient molecules on both labels |

**Confounders** — this is the most confounded hypothesis in the set:

- **Coverage asymmetry.** At 1% TF there are ~100× more normal than tumor molecules.
  Unequal group sizes bias naive difference estimates.
- **Copy-number.** HCC1395 is aneuploid. Tumor reads over-represent amplified regions,
  which have their own methylation character. A difference may be a CNA artifact.
- **Region selection.** Candidate loci are somatic-mutation sites, not random genome — they
  are not a neutral background for methylation comparison.
- **Read-end bias.** PAPER-003 warns methylation near read ends is unreliable; tumor and
  normal reads may differ in length distribution, hence in read-end fraction.
- **Cell-line vs. tissue.** Both HCC1395 and HCC1395BL are cultured lines; passage-related
  methylation drift is not tumor biology.
- **Phasing asymmetry.** Tumor reads may haplotag at a different rate than normal reads,
  making the conditioned comparison itself selected.
- **5mC vs 5hmC.** Both codes are present; they must be handled separately, not summed.

**Acceptance condition**

`|delta_meth_within_hap|` exceeds `T_H2_min_effect` with a CI excluding zero, in
≥ `T_H2_min_strata` independent strata, **and** the direction reproduces on held-out
chromosomes, **and** the effect survives a CNA-region sensitivity analysis.

**Rejection condition**

Effects vanish after conditioning on haplotype context, or fail to reproduce across
chromosomes, or are fully explained by coverage asymmetry / CNA / read-end bias in
sensitivity analysis.

**Next action if accepted** → proceed to H3. Record which strata carry the signal; those
become the ablation's focus.

**Pivot if rejected**

1. Test whether *unconditioned* methylation separates (i.e. the haplotype conditioning is
   what kills it) — a different, weaker, still-reportable finding.
2. Test 5hmC and 5mC separately if only the summed signal was tested.
3. Re-examine whether the confounder analysis was too aggressive (over-conditioning).
4. If genuinely negative: report that native methylation does **not** separate tumor from
   background within haplotype context at these tumor fractions on this data. Stop the
   ladder. This is the cleanest possible negative result and is a legitimate thesis outcome.

---

# H3 — Incremental computational value

> Adding methylation improves tumor-molecule classification **beyond** sequence and
> haplotype baselines.

**Required inputs**

- H1 joint-molecule table, H2's identified informative strata.
- Evaluation-only labels.
- Leakage-safe splits (chromosome / region / sample level — never random read-level).

**Observable outputs**

- The six ablation models A–F defined in [`04_evaluation_plan.md`](../experiments/evaluation-plan.md).
- Per-model performance with uncertainty, on held-out splits.
- Calibration curves.
- The specific comparisons: **D vs F** (does methylation add over sequence+haplotype?) and
  **A vs E** (does methylation add over sequence alone?).

**Metrics** — ranked by priority (see `04_evaluation_plan.md`):

1. sensitivity at fixed specificity
2. precision–recall
3. false-positive molecules per informative molecule
4. calibration (Brier / reliability)
5. informative-molecule count
6. ROC-AUC — **reportable, never the sole conclusion**

**Confounders**

- **Leakage.** Reads from the same region are correlated; a random split inflates every
  metric. Splitting is enforced structurally, and tested.
- **Class imbalance.** At 0.01% the positive class is minuscule; accuracy is meaningless and
  AUC is unstable.
- **Model capacity confound.** Model F has more features than D; any improvement must be
  shown to exceed what an equally-sized set of *permuted* methylation features achieves.
- **Feature selection leakage.** Methylation regions must never be selected using the
  evaluation dilutions.
- **Threshold selection.** Operating points chosen on test data invalidate the comparison.

**Acceptance condition**

Model F exceeds model D by ≥ `T_H3_min_delta` on the primary metric (sensitivity at fixed
specificity), with non-overlapping uncertainty intervals, on held-out splits, **and** the
improvement exceeds the permuted-methylation control by `T_H3_min_permutation_margin`,
**and** F's calibration is not worse than D's.

**Rejection condition**

F ≈ D within uncertainty, or F's advantage disappears under the permutation control, or
F improves ranking but degrades calibration.

**Next action if accepted** → proceed to H4. Freeze the model and the operating point
before touching sample-level evaluation.

**Pivot if rejected**

1. Check whether E > A (methylation adds over sequence alone even if not over
   sequence+haplotype). If so, the finding becomes "methylation and haplotype carry
   overlapping information" — genuinely interesting, and directly supports PAPER-005's
   coupling warning.
2. Check whether the interpretable model class is the limitation before concluding the
   *signal* is absent — but do not jump to deep learning; try richer interpretable features first.
3. If genuinely negative: report that methylation is **redundant** with haplotype context
   for this task. This is a strong, useful, publishable negative result.

---

# H4 — Low-TF detection value

> Per-molecule improvement produces **sample-level** detection improvement across dilution
> levels.

Per-molecule gains do not automatically survive aggregation. This hypothesis exists because
they might not.

**Required inputs**

- Frozen H3 model and operating point.
- All four samples: 1%, 0.1%, 0.01%, and the **0% control**.
- An aggregation function (upstream baseline: `week4/expB/mrd_score.py`).

**Observable outputs**

- Sample-level score per dilution, per ablation model.
- Detection rate by dilution level.
- Score on the 0% control — the specificity anchor.
- Separation between each dilution and the control.

**Metrics**

| Metric | Definition |
|---|---|
| `detection_rate[TF]` | detected samples ÷ samples, per level |
| `separation_vs_control` | score distance between dilution and 0%, in control-distribution units |
| `specificity_at_0pct` | the control must not be called detected |
| `lowest_detected_TF` | lowest level meeting the detection criterion |

**Confounders**

- **n = 1 per dilution level.** One replicate cannot estimate within-level variance. This is
  a hard structural limitation of the available data and caps every claim here.
- **Control adequacy.** A single 0% sample gives a poor estimate of the blank distribution;
  LoB in the PAPER-006 sense is not estimable.
- **Aggregation choice** can dominate the per-molecule model's contribution.
- **Nominal vs actual TF.** The dilution levels are nominal mixing ratios; the realized
  tumor fraction in each BAM has not been independently measured.
- Multiple-testing across models × dilution levels.

**Acceptance condition**

Model F's `lowest_detected_TF` is at least as low as model D's, **and** F's
`separation_vs_control` exceeds D's by ≥ `T_H4_min_separation_gain` at matched
specificity, **and** the 0% control is not detected by either.

**Rejection condition**

No difference in `lowest_detected_TF` and no separation gain; or the 0% control is called
detected by the methylation-using model (a specificity failure, which is disqualifying
regardless of sensitivity).

**Next action if accepted** → write up as controlled low-TF method development, bounded by
[`05_claim_boundaries.md`](../knowledge/claim-boundaries.md). Then, and only then, consider
replicates, additional cell lines, or richer models.

**Pivot if rejected**

1. Test alternative aggregation functions — the per-molecule result may be real but the
   aggregation lossy.
2. Report the per-molecule result (H3) as the thesis contribution and the sample-level
   non-transfer as a documented limitation. **This is an acceptable thesis outcome**: H3
   accepted with H4 rejected is a complete and honest story.
3. Do not chase sample-level significance by tuning until it appears. That is the failure
   mode this gated structure exists to prevent.

---

## Configuration surface

All symbols above resolve from configuration; none has a value in this document.

```yaml
# configs/experiments/<experiment>.yaml
thresholds:
  T_H1_min_molecules:            null   # required before H1 runs
  T_H1_min_stage_survival:       null
  T_H1_min_candidates:           null
  T_H2_min_effect:               null
  T_H2_min_strata:               null
  T_H3_min_delta:                null
  T_H3_min_permutation_margin:   null
  T_H4_min_separation_gain:      null
filters:
  min_cpg_per_read:              null
  min_mapping_quality:           null
  min_allele_quality:            null
  read_end_exclusion_bp:         null   # informed by PAPER-003 once verified
```

A `null` threshold is a **hard stop**: the runner must refuse to execute an experiment whose
acceptance condition is undefined, rather than defaulting to a value. Recorded as a design
requirement for Phase 6.
