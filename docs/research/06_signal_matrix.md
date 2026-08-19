# 06 — Signal matrix

Status: comparison table over the supplied literature
Date: 2026-08-19

One row per supplied study, read along seven questions: what it measures, what it fixes,
where it sits in an MRD detector, what it shares with the others, what only it does, what it
cannot do, and what a native long-read platform could add on top of its idea.

> **Verification status.** Rows are built from the indexed records in
> [`01_paper_patterns.md`](./01_paper_patterns.md) and the site's `papers` collection, all of
> which carry `evidence_level: external_report` with `pdf_available: false`. **No claim below
> has been checked against a source PDF.** Items marked `[unverified]` are inferences from a
> method's description rather than statements the paper makes; they must be confirmed before
> being cited. No performance figure appears here — the studies use different assays, sample
> types and cohorts, so comparing their numbers would be unsupported.
>
> The last column is **speculative by construction**: it names what ONT *could* contribute to
> each idea, not what it has been shown to contribute.

---

## The matrix

| Study | Signal it uses | Problem it solves | Where in the MRD detector | Common idea | Unique idea | Limitation | What ONT may add (speculative) |
|---|---|---|---|---|---|---|---|
| **MRDetect** [1] | Genome-wide SNVs across thousands of patient-specific sites (cfDNA WGS) | One locus carries too little evidence when tumor content is very low | Signal extraction (breadth) → evidence aggregation → sample score | Sum many individually unconvincing observations rather than trusting one | Breadth over depth: observe very many loci shallowly and integrate genome-wide | Aggregation is *across loci*; each read still contributes a single allele observation. Tumor-informed: needs the tumor's mutation set first | Each observation could carry more than the allele — phase context and native methylation on the same read — so breadth and per-molecule depth stop being a trade-off |
| **MRD-EDGE** [2] | SNVs and copy-number changes, ranked by a learned model | Genome-wide sequencing produces far more artifact than true tumor signal | Background suppression (learned) → aggregation | Suppress background *before* summing, not after | Machine-learning-guided signal enrichment in a ctDNA-specific feature space | The feature space is built from short-read sequence context; native base modifications are not among its inputs. Needs training data | The same learned framing with new per-read features: haplotype consistency, methylation state, fragment ends — read off one molecule rather than inferred |
| **PhasED-Seq** [3] | Two or more somatic variants observed *in phase* on one fragment | Independent sequencing errors imitate single true mutations | Background suppression (primary) + analytical validation framework (LoB/LoD) | Demand more than one coincidence per molecule | Molecular linkage: background must fail twice on the same fragment, which is multiplicatively unlikely | Requires ≥2 somatic variants inside one short fragment — available in mutation-dense disease, scarce exactly where tumor fraction is lowest. Not tumor-only | Kilobase reads extend linkage far beyond a short fragment, and allow the *second* observation to be germline haplotype context or methylation rather than a second somatic mutation |
| **Real-time ONT cfDNA** [4] | Copy-number aberrations and cfDNA fragmentomics from native nanopore reads | Genomic and fragment-level readouts are usually separate, slow assays | Signal extraction (fragment/CNA) → sample score | Use signal classes that are informative at shallow depth | Genome and fragmentome analysed natively and quickly, from plasma and urine | CNA and fragmentomics need appreciable tumor fraction; the design does not address single-nucleotide evidence at low TF | Already ONT: it establishes deployability. The unused layers on the same reads are phase and native methylation |
| **NanoRCS** [5] | Consensus-corrected long reads carrying SNV, CNA and fragmentomic signal | Per-read nanopore error limits how confidently one molecule can be called tumor-derived | Signal extraction (accuracy) → aggregation (multimodal tumor-fraction estimate) | Raise confidence per molecule before aggregating | Rolling-circle consensus on long reads, with several signal classes estimated together | The combined modalities are sequence- and fragment-level; haplotype context and native methylation are not the axes being combined. Consensus is built from amplified copies, so native base modifications are not expected to survive the amplification `[unverified]` | The complementary trade: keep the molecule native — lower per-read accuracy, but methylation and fragment ends preserved and readable alongside the allele |
| **Methylation ↔ fragmentation** [6] | DNA methylation and gene expression against genome-wide fragmentation | What actually determines where cfDNA breaks | Not a detector — a constraint on the aggregation step | Interpret signal classes biologically before combining them | Evidence that methylation and fragmentation are *coupled*, not independent readouts | Population- and region-level, not per-molecule tumor-origin inference; supplies no detection method | Methylation and fragment ends measured on the *same* molecule, so the coupling can be quantified per read instead of assumed away |
| **ONT cfDNA methylation requirements** [7] | Native 5mC calling on cell-free DNA | Methylation measurements are distorted by pre-analytical and library-prep effects | Guardrail across every stage (QC and provenance) | Measurement validity precedes inference | States the protocol conditions under which cfDNA methylation profiling is supported | A vendor requirements document, not a detection study: it constrains interpretation without supplying comparative evidence | It *is* the boundary condition — it defines when methylation evidence from ONT may be used at all |
| **This project (proposed)** | Candidate ALT allele + haplotype phase + native 5mC/5hmC, co-observed on one molecule | Tumor-only detection at low TF with a *single* variant per molecule and no matched normal | Background suppression, per molecule, before any aggregation | Add evidence per observation so background must fail on several axes at once | Methylation conditioned on haplotype context, for the single-variant case, tumor-only | Untested. Requires phasing to succeed; modalities may be coupled [6]; no per-read truth labels; methylation is protocol-sensitive [7] | — (this is the ONT-native design being asked about) |

---

## Reading the matrix by pipeline position

```text
signal extraction     → MRDetect (breadth) · NanoRCS (accuracy) · Real-time ONT (fragmentome) · ONT methylation (validity)
background suppression → PhasED-Seq (linkage) · MRD-EDGE (learned) · [this project: per-molecule consistency]
evidence aggregation  → MRDetect · MRD-EDGE · NanoRCS      [constraint: methylation ↔ fragmentation coupling]
sample-level score    → MRDetect · MRD-EDGE · NanoRCS
validation            → PhasED-Seq (LoB / LoD / precision framework)
```

The recurring move across all seven is **make each molecule count for more before summing**.
They differ in what "more" means: more loci, a learned prior, a second linked variant, a
consensus, or a second signal class.

## What the matrix does *not* establish

- That any listed limitation is fatal — each is a limitation *relative to the tumor-only,
  low-tumor-fraction, long-read setting of this project*, not a criticism of the study.
- That ONT would in fact add what the last column suggests. That column is a list of
  hypotheses; the project's own hypothesis
  ([`03_hypotheses.md`](./03_hypotheses.md)) is the first of them to be tested.
- That the combination proposed in the last row is absent from the wider field. The scoping
  claim remains the one in [`02_research_gap.md`](./02_research_gap.md): it is unaddressed
  *within these seven documents*, and a systematic search has not been run.

## References

Numbering matches the project website and `site/src/data/references.ts`.

1. A. Zviran et al., *Nat. Med.* 26(7):1114–1124, 2020. doi:10.1038/s41591-020-0915-3
2. A. J. Widman et al., *Nat. Med.* 30(6):1655–1666, 2024. doi:10.1038/s41591-024-03040-4
3. N. Klimova et al., *Oncotarget* 16:329–336, 2025. doi:10.18632/oncotarget.28719
4. Y. van der Pol et al., *EMBO Mol. Med.* 15(12):e17282, 2023. doi:10.15252/emmm.202217282
5. L.-T. Chen et al., *Genome Res.* 35(4):886–899, 2025. doi:10.1101/gr.279144.124
6. M. Noë et al., *Nat. Commun.* 15:6690, 2024. doi:10.1038/s41467-024-50850-8
7. Oxford Nanopore Technologies plc, "Updated method for cell-free DNA (cfDNA) methylation
   profiling," requirements document.
