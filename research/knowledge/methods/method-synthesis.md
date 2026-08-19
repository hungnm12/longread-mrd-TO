# MRD method synthesis — the field as a design space

What the reviewed methods are manipulating, what they share, what only one of them does, and
which regions of the space the reviewed set leaves thin.

Structured companions, which the website renders and which this document explains:

| File | Holds |
|---|---|
| [`../../design-space/detector-axes.yaml`](../../design-space/detector-axes.yaml) | The eleven axes, their strategies, and which method sits where |
| [`../../design-space/method-matrix.yaml`](../../design-space/method-matrix.yaml) | Each method positioned on every axis, with its unique contribution and limitation |
| [`../../design-space/gaps.yaml`](../../design-space/gaps.yaml) | Candidate gaps, scope-limited to the reviewed set |
| [`../ont-capabilities.yaml`](../ont-capabilities.yaml) | What this platform and this data actually provide |
| [`signal-matrix.md`](./signal-matrix.md) | The earlier seven-dimension reading, kept as written |

> **Verification.** All seven reviewed documents are indexed summaries, not source PDFs read
> locally. Every method claim below is therefore `[unverified]`. No performance figure appears
> anywhere: the studies use different assays, sample types and cohorts, so their numbers are not
> comparable.

---

## 1. The nine questions a detector answers

An MRD detector is a series of choices, and the reviewed methods differ by which choice they
make their contribution on:

1. **Marker discovery** — which loci are watched, and how many.
2. **Evidence per observation** — what is known about one molecule beyond its allele.
3. **Measurement accuracy** — how confident the platform is about that molecule.
4. **Background suppression** — how non-tumor observations are stopped from looking tumor-like.
5. **Evidence linkage** — whether two facts are known to share a molecule, and over what distance.
6. **Aggregation** — how per-observation evidence becomes a sample-level quantity.
7. **Detection unit** — locus, molecule, region, or sample.
8. **Decision** — how a score becomes a call, and against what reference.
9. **Validation** — what evidence is offered that it works.

Two more earn a place because a reviewed contribution sits on them and nowhere else:
**platform and deployability** (the real-time ONT work's contribution is turnaround and native
access, not a statistic) and **modality independence** (the methylation–fragmentation work
contributes no detector at all — it constrains how any multimodal detector may combine channels).

### Three things that are not the same axis

The most common confusion in this space, and one this synthesis keeps apart deliberately:

| | Question | Where it acts |
|---|---|---|
| **Signal enrichment** | Which observations are worth aggregating? | Selects a subset, before aggregation |
| **Background suppression** | How is a non-tumor observation stopped from imitating a tumor one? | Acts on each observation |
| **Aggregation** | How do many weak observations become one number? | Acts across observations |

MRD-EDGE is often described as doing all three; it enriches by *ranking*, which is a
suppression mechanism applied before aggregation. PhasED-Seq suppresses without enriching —
every fragment is judged by the same linkage rule. MRDetect aggregates without doing either.

## 2. Common principles — what genuinely crosses the set

A principle is listed only if at least three reviewed methods rest on it.

**P1 — Make each observation carry more before combining.** Present in all five detectors, and
the differences between them are almost entirely *how*: more loci (MRDetect), a learned prior
(MRD-EDGE), a second linked variant (PhasED-Seq), a physical consensus (NanoRCS), a second
signal class (real-time ONT). The disagreement in the field is not about the principle.

**P2 — Background is modelled, not merely filtered.** MRDetect models the error distribution,
MRD-EDGE learns it, PhasED-Seq requires it to fail twice, the ONT requirements document
constrains it at the bench. Nobody in the set treats a filter list as sufficient.

**P3 — The sample-level answer is a scalar over many weak observations.** MRDetect, MRD-EDGE
and NanoRCS all end with one number per sample. The unit at which evidence is *gathered*
differs; the unit at which it is *reported* does not.

**P4 — Evidence classes are not automatically independent.** Held explicitly by the
methylation–fragmentation work, implicitly violated by the multimodal methods, which combine
channels without testing independence `[unverified]`.

## 3. Unique mechanisms — what only one method does

| Method | Mechanism nothing else in the set uses |
|---|---|
| **MRDetect** [1] | Breadth as the primary lever: thousands of patient-specific loci integrated so that per-locus weakness stops mattering |
| **MRD-EDGE** [2] | A learned, ctDNA-specific feature space that ranks observations *before* aggregation |
| **PhasED-Seq** [3] | Multiplicative suppression by requiring co-occurrence in phase on one fragment — and the set's only analytical-validation framework (LoB, LoD, precision) |
| **Real-time ONT** [4] | Genomic and fragment-level readouts from one native library, fast enough to change clinical timing |
| **NanoRCS** [5] | A *physical* accuracy fix on long reads — rolling-circle consensus — rather than a statistical one |
| **Methylation ↔ fragmentation** [6] | Demonstrates coupling between channels, constraining every multimodal design in the space |
| **ONT cfDNA methylation** [7] | Makes methylation evidence conditional on library preparation instead of absolute |

## 4. Where the space is thin

Read down the axes rather than across the papers:

- **Background suppression** has two occupants, and both carry constraints that do not hold for
  tumor-only long reads: PhasED-Seq needs two somatic variants per short fragment and a
  matched-normal design; MRD-EDGE needs labelled training data and a short-read feature space.
- **Evidence linkage** is available on long-read platforms by construction — anything inside one
  read is co-observed — and no reviewed method uses it as a suppression mechanism. The two
  long-read methods spend the read length on consensus and multimodality instead.
- **Marker discovery** is tumor-informed in every reviewed detector. Tumor-naive discovery
  appears only in this project's own tooling, and it is a materially different problem: the
  marker set carries its own false-positive structure.
- **Decision and validation** for a tumor-naive long-read setting has no occupant. The only
  blank-anchored framework in the set is short-read, targeted and tumor-informed.
- **Modality independence** is asserted by two methods and tested by neither.

These are statements about *seven documents*. A systematic search has not been run
([open-questions.md](../open-questions.md) D3), so none of them is a claim about the field.

## 5. What this says for a long-read tumor-only project

Not a direction — a shape. The reviewed set leaves the combination *tumor-naive markers +
long-range linkage + blank-anchored decision* without an occupant, and the platform supplies the
linkage for free. Whether any of that survives contact with the data depends on measurements
that have not been made: phase block length, joint-molecule availability, and the composition of
the candidate set.

Candidate gaps, with their falsification conditions, are in
[`../../design-space/gaps.yaml`](../../design-space/gaps.yaml). None is selected.

## 6. References

Numbering matches `site/src/data/references.ts`.

1. Zviran et al., *Nat. Med.* 26(7):1114–1124, 2020 — MRDetect
2. Widman et al., *Nat. Med.* 30(6):1655–1666, 2024 — MRD-EDGE
3. Klimova et al., *Oncotarget* 16:329–336, 2025 — PhasED-Seq analytical validation
4. van der Pol et al., *EMBO Mol. Med.* 15(12):e17282, 2023 — real-time ONT cfDNA
5. Chen et al., *Genome Res.* 35(4):886–899, 2025 — NanoRCS
6. Noë et al., *Nat. Commun.* 15:6690, 2024 — methylation ↔ fragmentation
7. Oxford Nanopore Technologies plc — cfDNA methylation requirements
