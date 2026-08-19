# 04 — Evaluation plan

Status: active
Date: 2026-08-16

---

## 1. Required ablations

The central question is about an **increment**, so the design is an ablation grid, not a
single model. Each model uses only the modalities marked `yes`.

| Model | Sequence | Haplotype | Methylation | Role |
|---|---:|---:|---:|---|
| **A** | yes | no | no | sequence-only baseline — what the project already does |
| **B** | no | no | yes | methylation-only — is there *any* standalone signal? |
| **C** | no | yes | no | haplotype-only — control for phasing-driven selection effects |
| **D** | yes | yes | no | **the baseline to beat** |
| **E** | yes | no | yes | methylation's value without haplotype conditioning |
| **F** | yes | yes | yes | the full proposal |

### The comparisons that decide the thesis

| Comparison | Answers | Feeds |
|---|---|---|
| **F − D** | Does methylation add anything *after* sequence and haplotype? | **H3 primary** |
| **E − A** | Does methylation add over sequence alone? | H3 secondary; the fallback finding if F ≈ D |
| **D − A** | Does haplotype add over sequence alone? | Establishes that the baseline is a fair one |
| **F − E** | Does haplotype *conditioning* matter, or just methylation presence? | The "haplotype-conditioned" claim in the thesis title |
| **B, C alone** | Are the single modalities informative in isolation? | Sanity floor; guards against artifacts |

If **F ≈ E**, the word "haplotype-conditioned" is not earned and the framing must change.
This comparison is not optional.

### Required controls

| Control | Purpose |
|---|---|
| **Permuted methylation** | Model F trained with methylation features shuffled across molecules within stratum. Any F−D gain must exceed this. Guards against capacity confound. |
| **0% dilution sample** | Specificity anchor. A model that detects the control fails regardless of sensitivity. |
| **Label-shuffle** | Whole pipeline with permuted source labels must produce null performance. Catches leakage. |

---

## 2. Metrics, in priority order

The brief's ordering is adopted verbatim and is binding on how results are reported.

### 2.1 Sensitivity at fixed specificity — **primary**

Specificity is fixed from configuration (`eval.fixed_specificity`) **before** the run.
Sensitivity is read off at that operating point. This is the primary metric because MRD is
a low-prevalence problem where the specificity operating point is not negotiable.

### 2.2 Precision–recall

PR curves and average precision. Reported in preference to ROC because the positive class
is extremely rare — at 0.01% TF, precision degrades in ways ROC hides.

### 2.3 False-positive molecules per informative molecule

```text
FP_rate = false-positive molecules / total informative molecules
```

The denominator is stated explicitly in every table. This metric is what actually propagates
into a sample-level score, so it is more decision-relevant than a normalized curve.

### 2.4 Calibration

Reliability diagrams and Brier score. A model whose probabilities are not calibrated cannot
be aggregated across molecules in any principled way — which is exactly what H4 requires.
**A ranking improvement paired with a calibration regression is not an improvement.**

### 2.5 Informative molecule count

The absolute number the model had to work with, per stratum, per dilution. A metric computed
on 12 molecules is reported with that number attached. Never a rate without its denominator.

### 2.6 Detection rate by dilution

Sample-level, for H4. Per level, against the 0% control.

### 2.7 ROC-AUC — reportable, never decisive

AUC may appear in tables. It **must not** be the sole basis of any accept/reject decision,
and no conclusion may rest on an AUC difference alone. Rationale: AUC is insensitive to
calibration, to the operating point that matters, and to severe class imbalance.

---

## 3. Leakage prevention

Reads from the same genomic region share alignment context, local error modes, phasing
state, and — for the mixture BAMs — potentially the same source molecule. Random read-level
splitting is therefore invalid.

### Rules

1. **Never split reads from the same genomic region across train and test.** Enforced in
   code, not by convention.
2. Supported split levels: **chromosome**, **region/block**, **sample**. Configured, not
   hard-coded.
3. **Methylation regions must never be selected using the evaluation dilutions.** Selection
   happens on the pure tumor / normal, or on a held-out chromosome set, and the choice is
   recorded in the manifest.
4. **Inference inputs and evaluation-only truth are structurally separated.** Source labels,
   SEQC2 truth VCFs, matched-normal results, and benchmark resources are loaded through a
   distinct code path that the model never receives. See Phase 3's schema: `source_label_for_evaluation_only`
   is named that way so that any use of it in a feature path is visible in review.
5. Thresholds and operating points are selected on validation data, never on test.

### Tests (Phase 5 deliverables)

| Test | Asserts |
|---|---|
| `test_no_region_crosses_split` | intersection of train/test region ids is empty |
| `test_chromosome_split_disjoint` | no chromosome appears in both sides |
| `test_label_column_absent_from_features` | the feature matrix has no evaluation-only column |
| `test_shuffled_labels_give_null_performance` | end-to-end run with permuted labels lands at chance |
| `test_selection_excludes_eval_dilutions` | region selection provenance never lists an evaluation sample |

These run on **synthetic fixtures**, not on real BAMs, so they are fast and deterministic.

---

## 4. Stratified reporting

Every result table is stratified. An aggregate number without strata is not a result.

| Dimension | Values |
|---|---|
| sample | HCC1395 pure, TF1e-2, TF1e-3, TF1e-4, TF0 |
| dilution | 100%(pure), 1%, 0.1%, 0.01%, 0% |
| model | A–F, + permuted-methylation control |
| split | which chromosomes/regions were held out |
| stratum | haplotype family, phase set, region class |

## 5. Uncertainty

- Bootstrap confidence intervals over molecules, resampled **by region** (not by molecule),
  to respect the correlation structure.
- Every point estimate carries an interval and an `n`.
- No claim of improvement without non-overlapping intervals or an explicit paired test.

## 6. What this plan cannot deliver

Stated here so it is not accidentally claimed later:

- **No LoB or LoD** in the PAPER-006 analytical sense. One replicate per dilution and one
  blank sample cannot support those estimates.
- **No clinical performance claim.** See [`05_claim_boundaries.md`](../knowledge/claim-boundaries.md).
- **No cross-sample generalization claim.** One cell line, one mixture series.
- **No within-level variance estimate.** n = 1 per dilution.

The dilution series supports **relative comparison between models under matched conditions**.
That is what H3 and H4 are written to ask, and nothing more.

## 7. Reporting order

Results are written in this order, always:

1. **Observed** — the numbers, with denominators and intervals.
2. **Inferred interpretation** — what they suggest, labelled as inference.
3. **Hypothesis** — what they would mean if a further assumption held, labelled as hypothesis.
4. **Unresolved** — what remains open.

`actual_results` in an experiment manifest is never filled before the experiment runs.
