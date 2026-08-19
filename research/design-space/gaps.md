# Candidate gaps — tracking

Working companion to [`gaps.yaml`](./gaps.yaml), which stays the machine-readable source the
website renders. This file is for tracking a gap over time: what has been measured, what it
changed, and what the next move is.

**Scope limit, applying to every entry.** "Underexplored" means *not represented in the seven
documents reviewed in this repository*. No systematic literature search has been run, so nothing
here is a claim about the field, and nothing is novel until a search says so.

**Nothing here is selected.** Ordering is by identifier.

| Gap | Status | Evidence so far | Blocked on |
|---|---|---|---|
| [G1](#g1) — long-range same-molecule linkage | **premise measured** | `EXP-G1-001` / `FIND-0001` | Blank + dilution comparison; composition (G5) |
| [G2](#g2) — haplotype-conditioned methylation | candidate, unmeasured | — | Phase block length at 25×; joint availability per molecule |
| [G3](#g3) — native accuracy vs modality | candidate-limited | — | Only half runnable here: no amplified library exists |
| [G4](#g4) — blank-anchored decision rule | candidate, unmeasured | — | Nothing; the 5 blanks are on disk |
| [G5](#g5) — tumor-naive marker discovery | **promoted to precondition** | Implied by `FIND-0001` | Class definitions, then a composition estimate |

---

## G1 — Long-range same-molecule linkage for tumor-only detection {#g1}

**Axes:** evidence linkage · background suppression · marker discovery · detection unit
**Closest methods:** PhasED-Seq (short-fragment linkage, tumor-informed, matched normal) · NanoRCS
(long reads spent on consensus and multimodality instead)

### Claim ladder

| # | Claim | Status |
|---|---|---|
| 1 | Candidates are often close enough to share a read | **measured** — 34.8% within 10 kb, 21.3% within 5 kb, median read ~11.3 kb |
| 2 | Two candidates are actually observed as ALT on one molecule | **measured** — 67.9% of sampled pairs, 662 with ≥2 supporting reads (`FIND-0001`) |
| 3 | That co-occurrence is specific to somatic pairs | **contradicted so far** — 65.1% for confirmed-somatic pairs vs 78.6% where neither is confirmed |
| 4 | Co-occurrence persists at low tumor fraction | **not measured** |
| 5 | Co-occurrence suppresses background relative to blanks | **not measured** |

Claim 1 was where G1 stood when it was written; the objection that proximity is not co-occurrence
was correct, and claim 2 is the answer to it. Claims 3–5 are what remain.

### What the measurement changed

The physical premise is no longer an inference. But the specificity check failed in the direction
that matters: co-occurrence is *more* common among pairs where neither candidate is a confirmed
somatic SNV. The most economical explanation is germline heterozygous variants in cis — which is
what a candidate set of unknown composition would produce, and which is why G5 moved from
"foundational" to "precondition".

### Next measurements, in order

1. **Blank and dilution comparison.** The same statistic on TF0 replicates and on 1%, 0.1%, 0.01%.
   This is the one that decides G1: if the rate at low tumor fraction is indistinguishable from
   blanks, linkage carries no usable signal where it matters.
2. **Composition-aware stratification.** Repeat the SEQC2 stratification once the germline
   fraction is estimated (G5), so "neither" stops being a mixed bag.
3. **Trans versus cis.** 35.2% of reads carried exactly one ALT. Whether those pairs are in trans,
   subclonal, or one-artifact is unexamined and bears on whether linkage can suppress anything.

### Risks that are now concrete rather than hypothetical

- Germline haplotype structure produces co-occurrence indistinguishable from somatic linkage at
  this level of analysis. **Observed, not speculative.**
- SEQC2 covers high-confidence regions only, so "not in SEQC2" is not "not somatic"; the
  stratification is weaker than it looks.
- Pure tumor is the most favourable case by construction.

### Falsification

Unchanged: if ALT-ALT co-occurrence at 0.1% and 0.01% is indistinguishable from the TF0 blanks,
the direction dies on this data.

---

## G2 — Haplotype-conditioned native methylation {#g2}

**Axes:** evidence per observation · evidence linkage · background suppression · modality independence
**Closest methods:** PhasED-Seq · ONT cfDNA methylation requirements · methylation ↔ fragmentation

This was the project's direction before the design-space synthesis; it was parked on 2026-08-19
and appears here as one candidate among five. Its documents are intact in
[`../parked/snv-phase-methylation/`](../parked/snv-phase-methylation).

**Blocked on two unmeasured quantities**, both cheap: phase block length at 25× (nothing is phased
yet — LongPhase 2.0.2 is present and unrun), and how many molecules carry allele, phase and
methylation together.

**Note after `FIND-0001`.** G1's result bears on G2: if co-occurrence of two candidates is
dominated by germline haplotype structure, then "haplotype context" is demonstrably abundant in
this data — which is encouraging for the *availability* of G2's evidence and says nothing yet
about its discriminative value.

**Falsification:** ablate sequence alone, +phase, +methylation, all three, on the same molecules.
If the full configuration does not separate from the sequence-only baseline, the added modalities
are redundant here.

---

## G3 — Native-molecule accuracy versus modality {#g3}

**Axes:** measurement accuracy · evidence per observation · platform deployability
**Closest methods:** NanoRCS (accuracy through amplification) · real-time ONT (native)

Only half-runnable here: the native side is measurable, the consensus side is not, because no
amplified library exists. Comparing against published consensus performance would be exactly the
incompatible-numbers comparison this project forbids.

**Falsification:** quantify what per-read error costs at the candidate level, and whether
modification calls offset it. A null would mean the native trade is not worth taking.

---

## G4 — Blank-anchored decision rule for a tumor-only long-read detector {#g4}

**Axes:** decision threshold · validation · detection unit
**Closest method:** PhasED-Seq — the only blank-anchored framework in the reviewed set, and it is
short-read, targeted and tumor-informed.

Feasible now, cheap, and **independent of which evidence axis is eventually chosen** — which makes
it the safest thing to build early. Five TF0 replicates are on disk.

**Risks:** the five blanks come from one subsampling pipeline and share a source, so they are not
independent libraries and the estimated blank distribution will be narrower than a true one. A
limit of blank on cell-line dilution says nothing about plasma.

**Falsification:** if the blank distribution is so wide that no threshold separates 1% from 0%,
the detection question on this material is answered negatively — itself a result.

---

## G5 — Tumor-naive marker discovery {#g5}

**Axes:** marker discovery · background suppression
**Closest methods:** none in the reviewed set — every reviewed detector is tumor-informed.

**Promoted by `FIND-0001`.** It was already described as foundational; the co-occurrence result
made it operative. When co-occurrence is higher among *unconfirmed* pairs than confirmed-somatic
ones, the candidate set's composition is not a background detail — it is the thing that decides
what any subsequent count means.

**Next:** define the composition classes (somatic / germline / recurrent artifact / unknown) and
what resource estimates each, before counting anything. Tracked as `SUG-2026-08-001`.

**Risks:** estimating composition with the same population resources that produced the candidates
is circular for the germline fraction; SEQC2 may be used to evaluate composition but never to
select candidates.

**Falsification:** if the retained set proves to be dominated by germline and recurrent artifact,
tumor-naive discovery is not a viable base for the other gaps on this data.

---

## Not testable on this data

| | Why | Would need |
|---|---|---|
| Fragmentomics | Cell-line genomic DNA: fragment ends carry library preparation, not nuclease biology | Plasma cfDNA on the same platform |
| Consensus-accuracy designs | Simplex data, no amplification-based consensus | An RCA or duplex library — which would lose native modifications |
| Any clinical MRD performance claim | No cohort; dilution material is not plasma | A clinical cohort and a different study design |
