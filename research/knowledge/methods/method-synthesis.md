# MRD method synthesis

What the supplied literature does, compressed to the parts that constrain design choices here.
The full seven-dimension table lives in
[`signal-matrix.md`](./signal-matrix.md); this page is the
distilled version and is not a substitute for it.

> `[unverified]` Every method claim below comes from indexed summaries, not from source PDFs.
> No performance figure is repeated anywhere, because the studies use different assays, sample
> types and cohorts.

---

## 1. The recurring move

Every method makes **each molecule count for more before aggregating**. They differ only in
what "more" means:

| Way to add evidence | Method | Cost of that choice |
|---|---|---|
| More loci | MRDetect [1] | Needs a tumor-informed mutation set; each read still yields one allele bit |
| A learned prior | MRD-EDGE [2] | Needs training data; features are short-read sequence context |
| A second linked variant | PhasED-Seq [3] | Needs ≥2 somatic variants on one fragment — scarcest at low tumor fraction |
| A consensus of copies | NanoRCS [5] | Amplification-based; native base modifications are not expected to survive `[unverified]` |
| A second signal class | Real-time ONT [4], methylation work [6][7] | Classes may be biologically coupled, so they do not add independently [6] |

## 2. Positions in an MRD detector

```text
signal extraction      MRDetect (breadth) · NanoRCS (accuracy) · Real-time ONT (fragmentome) · ONT methylation (validity)
background suppression PhasED-Seq (linkage) · MRD-EDGE (learned)
evidence aggregation   MRDetect · MRD-EDGE · NanoRCS        [constraint: methylation ↔ fragmentation coupling, 6]
sample-level score     MRDetect · MRD-EDGE · NanoRCS
validation             PhasED-Seq (LoB / LoD / precision framework)
```

**Background suppression is the least crowded position**, and both occupants sit under
constraints that do not hold in a tumor-only long-read setting: PhasED-Seq needs two somatic
variants per fragment and a matched normal design; MRD-EDGE needs training data and a
short-read feature space.

## 3. What the literature imposes on any design here

| Constraint | Source | Practical effect |
|---|---|---|
| Modalities are **coupled**, not independent | [6] | Stacking methylation and fragmentation as independent evidence inflates confidence. Ablation, not addition |
| Methylation is **protocol-sensitive** | [7] | Methylation evidence is conditional on library prep; read-end positions are the fragile ones |
| Validation needs a **blank distribution** | [3] | Any score must be defined against blanks — the `TF0` replicates exist for exactly this (see [`datasets.md`](../datasets.md)) |
| Tumor-informed designs assume a **tumor mutation set** | [1][2] | Not available in the tumor-only setting; background suppression must come from population resources plus within-molecule consistency |

## 4. Where this project's placement stands

**Pending.** The project's own row was removed from the signal matrix on 2026-08-19: a single
row framed it as one idea at one grid cell, and the work is expected to address several of
these problems at once. A scope statement covering the full problem set must exist before it
re-enters the table. See the pending section in
[`signal-matrix.md`](./signal-matrix.md).

What is *not* pending is the platform fact underneath: ONT reads carry allele, heterozygous
context and native methylation on one molecule ([`ont-capabilities.md`](../ont-capabilities.md)),
which is the raw material none of the five approaches above uses in that combination.

## 5. References

Numbering matches `site/src/data/references.ts` and the project website.

1. Zviran et al., *Nat. Med.* 26(7):1114–1124, 2020 — MRDetect
2. Widman et al., *Nat. Med.* 30(6):1655–1666, 2024 — MRD-EDGE
3. Klimova et al., *Oncotarget* 16:329–336, 2025 — PhasED-Seq analytical validation
4. van der Pol et al., *EMBO Mol. Med.* 15(12):e17282, 2023 — real-time ONT cfDNA
5. Chen et al., *Genome Res.* 35(4):886–899, 2025 — NanoRCS
6. Noë et al., *Nat. Commun.* 15:6690, 2024 — methylation ↔ fragmentation
7. Oxford Nanopore Technologies plc — cfDNA methylation requirements
