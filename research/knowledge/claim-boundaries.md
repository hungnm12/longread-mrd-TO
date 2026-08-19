# 05 — Claim boundaries

Status: **binding on every output of this project** — reports, figures, site pages, thesis text
Date: 2026-08-16

If a statement in any deliverable conflicts with this document, this document wins and the
statement is wrong.

---

## 1. The six boundaries

### 1.1 HCC1395 dilution is controlled low-TF method development

Mixing tumor cell-line reads into normal cell-line reads at 1%, 0.1%, and 0.01% creates a
controlled setting where the ground truth is known by construction. That is its value: it
permits clean ablation. It is a **methods testbed**, not a specimen.

- ✅ "At a 1% nominal tumor fraction in this controlled genomic dilution, model F recovered …"
- ❌ "At 1% tumor fraction, the method detects …"

### 1.2 It is not automatically real plasma cfDNA

Genomic DNA sheared or sampled from cultured cell lines differs from circulating cell-free
DNA in fragment-length distribution, end motifs, nucleosome positioning, chromatin-derived
fragmentation, and pre-analytical handling. PAPER-005 makes the methylation–fragmentation
coupling explicit; PAPER-003 makes pre-analytical methylation bias explicit. Both mean the
methylation signal observed here is **not** the methylation signal a plasma assay would see.

- ✅ "Whether this transfers to plasma cfDNA is untested and is a distinct question."
- ❌ "This shows the approach works on liquid biopsy."

### 1.3 It does not establish clinical MRD performance

No patient samples, no clinical endpoint, no outcome correlation, no prospective design,
n = 1 per dilution level, one cell line. Sensitivity, specificity, LoB and LoD in the
analytical-validation sense (PAPER-006) are **not estimable** from this data.

- ✅ "Relative model comparison under matched conditions."
- ❌ "Sensitivity of X% at Y% tumor fraction", ❌ "limit of detection of …", ❌ "clinically actionable"

### 1.4 Local molecular evidence does not equal a biological clone

If molecules cluster by methylation pattern, that is a **pattern in the data**. Calling it a
subclone requires evidence this design does not produce: independent clonal markers,
consistency across many loci, and a population-genetic argument. Methylation heterogeneity
also arises from cell-cycle state, culture passage, allele-specific methylation, imprinting,
and basecaller error.

- ✅ "Molecules separated into two methylation groups within this phase set."
- ❌ "Two clones were detected."

### 1.5 Phasing does not prove somatic status

A haplotype-consistent variant is consistent with somatic origin. It is equally consistent
with germline variation, loss of heterozygosity, a mapping artifact recurring in phase, or
a CNA-driven allelic imbalance. Haplotype consistency is **evidence**, weighted like any
other feature, never a label.

- ✅ "The variant was carried on a single haplotype, consistent with — but not demonstrating — somatic origin."
- ❌ "Phasing confirmed the variant is somatic."

### 1.6 Methylation association does not prove causality

If tumor-origin molecules carry different methylation, the difference may be caused by tumor
biology, or by copy number, or by which regions phase well, or by read-length differences
between the two source libraries, or by basecaller behaviour on different sequence contexts.
The ablation design measures **association after conditioning**. It does not establish cause.

- ✅ "Methylation was associated with tumor origin after conditioning on haplotype context."
- ❌ "Tumor methylation changes drive the signal."

---

## 2. Tumor-only means tumor-only

**Inference inputs** (allowed): the tumor/mixture BAM, the reference, population databases,
panels of normals, and models trained without evaluation labels.

**Evaluation-only resources** (never inference inputs):

- per-read source labels derived from `HCC1395.bam` / `HCC1395BL.bam`
- SEQC2 v1.2.1 truth sSNV/sINDEL VCFs and HC-region BEDs
- matched-normal (`HCC1395BL`) variant calls
- nominal dilution levels, when used as labels

Structural enforcement: the joint-molecule schema names the field
`source_label_for_evaluation_only` so that any appearance in a feature path is
self-evidently wrong in code review, and the leakage tests in
[`04_evaluation_plan.md`](../experiments/evaluation-plan.md#3-leakage-prevention) assert its absence
from the feature matrix.

---

## 3. The four-way statement discipline

Every finding is written under exactly one of these labels. Mixing them is the most common
way an honest analysis becomes an overclaim.

| Label | Means | Test |
|---|---|---|
| **Observed result** | A number produced by a run, with denominator and provenance | Could someone re-run and get this? |
| **Inferred interpretation** | What the observation suggests, given stated assumptions | Are the assumptions written down? |
| **Hypothesis** | What might be true, not yet tested | Is there a defined experiment that would falsify it? |
| **Unresolved question** | Known gap, no current plan | Is it recorded in the decision log? |

Site pages, weekly reports, and experiment manifests all carry these labels explicitly.
The `evidence_level` enum already in `site/src/content.config.ts`
(`preliminary` / `verified` / `reproduced` / `external_report`) is the machine-readable
form of the same discipline and must stay in sync.

---

## 4. Prohibited outputs

Absolutely never produced, under any circumstance, including for illustration:

- Fabricated results, metrics, thresholds, or figures.
- Placeholder numbers presented as measurements.
- Plots drawn from synthetic data that are not conspicuously labelled as such.
- `actual_results` filled in before an experiment has run.
- Citations to sources not verified to exist and to say what is claimed.
- Acceptance thresholds chosen after seeing results.

Where a result does not exist yet, the deliverable shows an explicit **"pending experiment"**
state. An empty, honest cell is a valid research artifact; an invented one is misconduct.

---

## 5. Scope reminders

Currently **out of scope** and not to be claimed, implied, or half-built: high-VAF clonality
investigation, CNA integration, fragmentomics, deep learning, cloud deployment, clinical
prediction.

---

## 6. Standing caveats to attach to results

| Result touches | Attach |
|---|---|
| any dilution level | "nominal mixing ratio; realized tumor fraction not independently measured" |
| any sample-level number | "n = 1 replicate per dilution level; within-level variance not estimable" |
| any methylation difference | "5mC and 5hmC reported separately; read-end CpGs excluded per configuration" |
| any haplotype-conditioned result | "haplotagging rate varies by heterozygous-variant density; conditioning is itself a selection" |
| any comparison to the 0% control | "single blank sample; LoB not estimable" |
| any candidate locus set | "ClairS-TO tumor-only PASS SNVs; precision 0.707 / recall 0.732 vs SEQC2 HC (`week4/phase0_results.md`) — candidates are not somatic truth" |
