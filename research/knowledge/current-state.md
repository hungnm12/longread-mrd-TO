# Current state — what we know, as of 2026-08-19

A single consolidated read of where the project stands after the environment survey, the
design-space synthesis and the first linkage measurement. Everything here is drawn from the
artifacts listed at the end; where they disagree with this summary, they win.

Verification markers: `[verified]` checked directly on this server on 2026-08-19 · `[measured]`
produced by a registered experiment · `[repo]` from a repository document · `[unverified]`
external claim with no local check.

---

## 1. Position

**Between directions.** The descriptive tumor-only work stands. The direction built on it — SNV
candidates combined with haplotype phase and native methylation — was parked and now appears as
one candidate among five in a design-space map. No direction is selected, and the selection is a
researcher's decision rather than one the synthesis makes.

What is blocking is a definition, not a measurement: the project's full problem set.

## 2. What the data actually provides

Checked by reading the BAMs, not by asking what ONT supports in principle.

| | |
|---|---|
| Native 5mC **and** 5hmC, separate channels | on 224/224 sampled tumor reads and 300/300 dilution reads `[verified]` |
| Read span | median ~11.3 kb, max 70.2 kb, MAPQ median 60 `[verified]` |
| Haplotags (`HP`/`PS`) | **absent everywhere** — phasing is unstarted work, not missing data `[verified]` |
| Dilution material | **14 BAMs**: 5 blanks + 3 replicates each at 1%, 0.1%, 0.01% `[verified]` |
| Basecaller model | **not recorded** in the BAM header — the "5 kHz simplex 5mCG/5hmCG" description comes from directory names `[verified]` |
| Fragmentomics | **not obtainable** — cell-line genomic DNA, so fragment ends carry library preparation, not nuclease biology |
| Compute | 112 cores, 503 GB RAM, **no GPU** `[verified]` |

Two of these corrected the repository's own documents: the replicate count (the scope contract
assumed one per level and concluded no limit-of-blank was possible) and the provenance gap on the
basecaller.

## 3. What the field looks like

Eleven axes, eight methods positioned on each. The compressed reading:

**Every method makes each observation carry more before combining.** They differ only in how —
more loci, a learned prior, a second linked variant, a physical consensus, or a second signal
class. That is the field's shared move, not a point of disagreement `[unverified]`.

**Where the reviewed set is thin:**

- **Background suppression** has two occupants, both under constraints that do not hold here:
  PhasED-Seq needs two somatic variants in one short fragment and a matched normal; MRD-EDGE needs
  labelled training data and a short-read feature space.
- **Evidence linkage** is free on long-read platforms — anything inside one read is co-observed —
  and no reviewed method spends it on background suppression.
- **Marker discovery** is tumor-informed in every reviewed detector. Tumor-naive discovery appears
  only in this project's own tooling.
- **Decision and validation** for a tumor-naive long-read setting has no occupant.

Scope limit that applies to all of the above: this describes **seven documents**, not the field.
No systematic search has been run, and all seven are indexed summaries rather than source PDFs.

## 4. What we measured today

### 4.1 Proximity — the opportunity `[measured]`

34.8% of the 48,819 PASS SNV candidates have another PASS candidate within 10 kb; 21.3% within
5 kb; median nearest-neighbour distance 17.1 kb. Against a median read of ~11.3 kb, roughly a
third of candidates have a neighbour close enough to share a molecule.

### 4.2 Co-occurrence — the observation `[measured, EXP-G1-001]`

Proximity is not co-occurrence, so we counted what reads actually carry. 1,000 seeded candidate
pairs within 20 kb, pure tumor, every read spanning both positions classified:

| | |
|---|---|
| Pairs with ≥1 read carrying **both** ALT alleles | **678 / 999 = 67.9%** |
| Pairs with ≥2 such reads | **662** |
| Reads covering both positions | 50,756 — 23.9% ALT-ALT, 35.2% one-ALT, 40.2% REF-REF |
| Median per-pair ALT-ALT fraction | 0.41 (IQR 0.22–0.74) |
| By distance | 78% under 1 kb → 63% at 10–20 kb, tracking reads covering both (72 → 28) |

**The physical premise holds.** Two candidates are not merely near each other; they are observed
on the same molecule with both ALT alleles, routinely and with multi-read support.

### 4.3 The pre-registered criterion that failed

The third success criterion — that co-occurrence be *more* common among confirmed-somatic pairs —
came out backwards:

| SEQC2 stratum | Pairs with ALT-ALT |
|---|---|
| Both candidates confirmed somatic | 65.1% |
| One confirmed | 54.7% |
| **Neither confirmed** | **78.6%** |

The economical explanation is germline heterozygous variants sitting in cis. Co-occurrence is
therefore **real but not specific**: as measured, it does not distinguish somatic linkage from
germline haplotype structure.

Fixing that criterion before running is what made this visible. Read alone, 67.9% would have
looked like a clean result.

## 5. What changed as a result

- **G1** moved from *argued* to *premise-measured*, with an explicit claim ladder: proximity
  (measured) → co-occurrence (measured) → somatic specificity (contradicted so far) → persistence
  at low tumor fraction (not measured) → background suppression vs blanks (not measured).
- **G5, candidate composition**, moved from foundational to **operative**. When co-occurrence is
  higher among unconfirmed pairs than confirmed-somatic ones, composition is not a background
  detail — it decides what any subsequent count means.
- **G2** (the parked phase + methylation direction) gained an incidental data point: haplotype
  context is demonstrably abundant here. That speaks to the *availability* of its evidence and
  says nothing about its discriminative value.

## 6. What we still do not know

| Question | What would settle it |
|---|---|
| Does co-occurrence survive at low tumor fraction? | The same statistic on TF0 blanks and the three dilutions — **the next measurement** |
| What is the candidate set made of? | Class definitions, then a composition estimate with population resources (`SUG-2026-08-001`) |
| How long are phase blocks at 25×? | One LongPhase run on one region; nothing is phased yet |
| Which basecaller model produced the modification calls? | Ask whoever produced the run |
| Do the seven papers say what the records claim? | PDF-level verification; none has been done |
| Is any of this a gap in the field rather than in our reading? | A documented systematic search |

## 7. What would change the picture

- **Blanks show the same co-occurrence rate as dilutions** → linkage carries no usable signal
  where it matters, and G1 dies on this data. That is a publishable negative.
- **Composition turns out to be dominated by germline and recurrent artifact** → tumor-naive
  discovery is not a viable base for any gap here, and G5's failure condition fires.
- **Phase blocks at 25× are short** → G2's evidence is unavailable regardless of its merit.

## 8. Where the detail lives

| Artifact | Holds |
|---|---|
| [`methods/method-synthesis.md`](./methods/method-synthesis.md) | The field synthesis in full |
| [`../design-space/detector-axes.yaml`](../design-space/detector-axes.yaml) | 11 axes, strategies, method positions |
| [`../design-space/method-matrix.yaml`](../design-space/method-matrix.yaml) | Each method on every axis |
| [`../design-space/gaps.yaml`](../design-space/gaps.yaml) · [`gaps.md`](../design-space/gaps.md) | Candidate gaps — machine-readable, and tracked |
| [`ont-capabilities.yaml`](./ont-capabilities.yaml) · [`ont-capabilities.md`](./ont-capabilities.md) | Capability inventory |
| [`datasets.md`](./datasets.md) · [`../../data/experimental-space.yaml`](../../data/experimental-space.yaml) | What material exists |
| [`../experiments/registry/EXP-G1-001.yaml`](../experiments/registry/EXP-G1-001.yaml) | The registered experiment |
| [`../findings/FIND-0001.md`](../findings/FIND-0001.md) | The co-occurrence result in full |
| [`tools.md`](./tools.md) · [`constraints.md`](./constraints.md) | What runs, and what bounds it |
| [`open-questions.md`](./open-questions.md) | The ranked question list |

The live site renders the synthesis at `/research-narrative/`.
