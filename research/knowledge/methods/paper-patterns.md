# 01 — Paper patterns

Status: methodology map, not a literature review
Date: 2026-08-16

This document organizes the provided literature **by methodology position**, not
paper-by-paper. Every method for detecting rare tumor molecules occupies one or more
positions on the same pipeline:

```text
rare tumor molecules
  → signal extraction
  → background suppression
  → evidence aggregation
  → sample-level score
  → LoB / LoD / specificity validation
```

> **Verification status.** All seven entries below are indexed from the project brief and
> the site's `papers` collection, where every record carries
> `evidence_level: external_report` and `pdf_available: false`. **No claim here has been
> verified against the source PDF.** Numeric claims, effect sizes, and stated performance
> are deliberately omitted rather than paraphrased. Placeholders marked
> `[unverified — needs PDF]` must be resolved before any of this is cited as thesis evidence.

---

## Position 1 — Signal extraction

*What is measured off the molecule at all.*

| Concept | Source | Position taken |
|---|---|---|
| **Genome-wide breadth** | PAPER-001 (cfDNA mutational integration) | Do not deepen a few loci; observe very many loci shallowly and integrate. Breadth converts individually-weak evidence into a usable aggregate. |
| **Nanopore consensus sequencing** | PAPER-002 (Genome Res. 2025) | Long reads can carry multiple signal classes at once; consensus construction raises per-molecule confidence. |
| **Native fragmentomics** | PAPER-004 (EMMM real-time ONT) | ONT observes fragment-level properties natively, without a separate assay. Motivates long reads beyond variant calling. |
| **Native methylation** | PAPER-003 (cfDNA methylation profiling) | Methylation can be read from the same native molecule — no bisulfite, no separate library. |

**Position this thesis takes:** breadth-over-depth (PAPER-001) applied to *long* molecules,
where the extra per-molecule signal is haplotype + native methylation rather than consensus
depth. The distinguishing move is that all three signals come off **one alignment record**.

## Position 2 — Background suppression

*How non-tumor molecules are prevented from looking tumor-like.*

| Concept | Source | Position taken |
|---|---|---|
| **Phased multi-variant detection** | PAPER-006 (PhasED-Seq) | Requiring multiple mutations *in phase* on the same molecule suppresses background multiplicatively — independent errors rarely co-occur in phase. This is the closest published analogue to the present design. |
| **ML-guided signal enrichment** | PAPER-007 (plasma monitoring) | A learned model can rank molecules or loci by how tumor-like they are, enriching signal before aggregation. |
| **Pre-analytical methylation bias** | PAPER-003 | Methylation measurements carry protocol- and position-dependent bias; read-end methylation is systematically less reliable. A guardrail, not a method. |

**Position this thesis takes:** the tumor-only setting has no matched normal, so background
suppression must come from (a) population panels + PoN, already handled upstream by
ClairS-TO, and (b) **within-molecule consistency**. PhasED-Seq suppresses background by
requiring *multiple variants* in phase; this project asks whether requiring *methylation
consistent with haplotype context* achieves an analogous suppression with **one** variant —
which is the only option when tumor fraction is low enough that co-occurring variants on
one molecule are vanishingly rare.

## Position 3 — Evidence aggregation

*How per-molecule evidence becomes per-locus and per-sample evidence.*

| Concept | Source | Position taken |
|---|---|---|
| Integration across many weak sites | PAPER-001 | Sum/integrate weak per-locus evidence genome-wide. |
| Multimodal integration | PAPER-002, PAPER-007 | Combine signal classes (SNV, CNA, …) into one readout. |
| **Methylation–fragmentation coupling** | PAPER-005 (Nat. Commun. 2024) | Methylation and fragmentation are **biologically coupled**, not independent. Stacking coupled signals as if independent inflates confidence. |

**Position this thesis takes:** PAPER-005 is the reason the evaluation plan is built on
**ablation** rather than on adding features and reporting an improved AUC. If methylation
merely re-encodes information already carried by sequence context or haplotype, an ablation
will show it and a naive stacked model will not.

## Position 4 — Sample-level score

*How a sample is declared positive.*

| Concept | Source | Position taken |
|---|---|---|
| Tumor-burden readout | PAPER-001, PAPER-007 | A single scalar per sample, trended over time. |
| Assay-grade scoring | PAPER-006 | Score must be defined against a blank/background distribution, not an arbitrary threshold. |

**Position this thesis takes:** deferred to H4. The existing `week4/expB/mrd_score.py`
titration scoring is the upstream baseline for this step. No sample-level score is
implemented before per-molecule evidence is shown to be real.

## Position 5 — LoB / LoD / specificity validation

*How the claim is bounded.*

| Concept | Source | Position taken |
|---|---|---|
| **Analytical validation framework** | PAPER-006 | Limit of Blank, Limit of Detection, precision, dilution series, blank samples, background error modelling. |

**Position this thesis takes:** PAPER-006 supplies the *vocabulary* and the *shape* of a
validation design. It does **not** license claiming those endpoints here: HCC1395 genomic
dilution is not plasma cfDNA, and one replicate per dilution level cannot support a
statistically meaningful LoD. The dilution series is used for **relative** comparison
between ablation models at matched conditions, and the 0% control is used as the required
specificity anchor.

---

## Where the gap sits on this map

| Pipeline position | Covered by provided literature | Covered for **tumor-only long-read at low TF** |
|---|---|---|
| Signal extraction | yes — breadth, ONT, native methylation | partially |
| Background suppression | yes — phasing (PhasED-Seq), ML enrichment | **phasing yes, methylation-conditioned-on-haplotype: not established** |
| Evidence aggregation | yes — with an explicit coupling warning | not for this modality combination |
| Sample-level score | yes | not for this modality combination |
| Validation | yes — framework | not applicable at this project's scale |

The unfilled cell in the "background suppression" row is the candidate research gap.
See [`02_research_gap.md`](../../parked/snv-phase-methylation/research-gap.md).

---

## Placeholders requiring resolution

| Item | Needed before | Status |
|---|---|---|
| PAPER-001 — actual integration statistic and its breadth/depth trade-off | citing breadth-over-depth as method precedent | `[unverified — needs PDF]` |
| PAPER-002 — consensus construction requirements and coverage assumptions | claiming ONT multimodal precedent | `[unverified — needs PDF]` |
| PAPER-003 — specific read-end methylation bias magnitude and direction | setting read-end exclusion windows in Phase 3 | `[unverified — needs PDF]` |
| PAPER-005 — direction and strength of methylation–fragmentation coupling | arguing modality non-independence quantitatively | `[unverified — needs PDF]` |
| PAPER-006 — LoB/LoD definitions and background-error model form | designing any validation claim | `[unverified — needs PDF]` |
| PAPER-007 — model class and what the enrichment actually selects on | positioning against ML enrichment | `[unverified — needs PDF]` |
| Broader literature sweep beyond these seven | promoting the candidate gap to an established gap | **not started** |

No citation is added to this document that is not backed by one of the seven indexed
records. Adding a citation without a verified source is a fabrication and is prohibited by
[`05_claim_boundaries.md`](../claim-boundaries.md).
