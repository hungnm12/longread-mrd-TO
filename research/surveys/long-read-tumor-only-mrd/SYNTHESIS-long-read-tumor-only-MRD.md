# Long-read tumour-only MRD detection — how the existing papers actually handle it

A synthesis organised by **the problems any such method must solve**, not by tool name. Built from
13 held sources plus two prior systematic searches (2026-08-21, 2026-08-24).

**Provenance rule used throughout:** ※ marks a fact that reaches this document through a
synthesis/review document rather than the method's own paper. Nothing marked ※ may be quoted as
established without reading the primary text.

---

## 0. The topic is oddly empty, and that is the first finding

Asked directly whether any named tool is **long-read AND tumour-only AND aimed at MRD**, the
sources answer:

> *"There is no single software tool in these sources that is simultaneously classified as
> long-read, strictly tumour-only, and designed exclusively for MRD detection."*

The field splits instead into two populations that do not meet:

- **Long-read tumour-only somatic callers** — ClairS-TO, smrest, DeepSomatic. Built to call
  variants, benchmarked at **1–10% VAF** ※. They are not MRD tools and do not claim to be.
- **MRD detectors** — MRDetect, AccuScan, PhasED-seq, shearwater. Built for **10⁻⁵–10⁻⁶**, and
  almost all short-read, most tumour-informed.

Between "calls a variant at 1% VAF" and "detects a sample at 0.01% TF" lies two to three orders of
magnitude and a change of unit. **Whether long-read tumour-only tooling supports the second is
unestablished.** Two systems — NanoRCS and SIMMA ※ — are the only candidates.

---

## 1. Problem one: remove germline without a matched normal

Every tumour-only method must solve this, and the field has **four distinct strategies**. They are
not alternatives so much as layers; ClairS-TO ships three of them.

| Strategy | How it works | Who | Reported effect |
|---|---|---|---|
| **Population panels** | drop anything in gnomAD / dbSNP / 1000G / CoLoRSdb | ClairS-TO, GuardantOMNI, AccuScan | CoLoRSdb PoN raises somatic F1 by **10–20%** ※ |
| **Allele fraction + copy number** | model observed VAF against local CN, ploidy and purity; a het germline sits where CN says it should | **SGZ** (2018), **Verdict** (ClairS-TO) | Verdict described as *"similar to and improved from SGZ"* |
| **Haplotype consistency** | phase the germline background; a true somatic allele co-segregates with one haplotype, random error disperses across both | **smrest**, **ClairS-TO** (`MultiHap`/`NoAncestry`), **LongPhase-S** | **described, never benchmarked** ※ |
| **Learned discrimination** | train a network to separate the two classes directly | **ClairS-TO** dual CNN, **DeepSom** | ClairS-TO reports state-of-the-art vs DeepSomatic, Mutect2, Octopus, Pisces |

### What the papers do NOT do

They do not report **how much each layer removes**. Asked for isolated yields:

> ClairS-TO haplotype filter — *"described, not benchmarked"* ※
> smrest read-exclusion rule — *"described, not benchmarked"* ※

And the residual is large. The one source that audits its own failures finds **germline drives 75%
of false positives** in ONT tumour-only calling — 61% heterozygous, 14% homozygous ※. Independent
clinical figures for how much private germline survives into a tumour-only list: **41.6%**
(GuardantOMNI, 11,490 of 27,610 variants); **4–12%** misclassification in general tumour-only
pipelines.

---

## 2. Problem two: beat the platform's error floor

This is where long reads are weakest, and the sources say so plainly.

> *"Read length helps with mapping and phasing but **does not lower the per-base background that
> limits low-VAF calling**, and long-read platforms currently carry higher per-base error,
> particularly for indels."*

Benchmarked substitution error, difficult regions: **AVITI 0.04% · Illumina 0.12% · PacBio 0.23% ·
ONT 0.37%**. Homopolymer indels: ONT **~18%**.

The field's two answers, and both cost something:

| Answer | Mechanism | Who | Result |
|---|---|---|---|
| **Physical consensus** | read the same molecule several times and take the consensus | **NanoRCS** (rolling-circle concatemers, long-read) ※; **CODEC**, **AccuScan** (duplex/RCA, short-read) | NanoRCS: raw error → **Q31 (0.07%)** ※; AccuScan: **4.2×10⁻⁷** |
| **Statistical modelling** | model the error rate instead of removing it | **shearwater**, **deepSNV**, **EBCall** (beta-binomial); **TNER** (trinucleotide context); **DREAMS-vc** (NN) | DREAMS-vc: ROC-AUC **0.808** tumour-naive |

**The cost of physical consensus on long reads is the thing this project cares about.** Rolling-circle
consensus reads the molecule multiple times — which means the native molecule is amplified, and
**native base modifications are lost**. That is the trade NanoRCS makes: error floor down,
methylation channel gone.

---

## 3. Problem three: set a decision threshold with no normal

Two families, and only one of them works tumour-only.

**Cross-individual (MRDetect).** Fit μ and σ of a detection-rate distribution over ~30 control
plasmas; call at Z>3 or Z>4; 95–98% clinical specificity. **Requires the compendium to be
germline-free**, because a tumour-informed list has already been subtracted against a matched
normal, so its residual background is *technical* — and technical background transfers between
people.

The sources state exactly why this breaks tumour-only:

> *"If a single heterozygous private germline variant is misclassified as somatic, its presence in a
> tumor-free sample at approximately 50% VAF will **overwhelm the somatic signal**, causing a
> catastrophic false-positive MRD call."* ※

**In-sample calibration.** What normal-free workflows use instead:

- per-locus μ and ρ from a **panel of normals**;
- global overdispersion tuned on **the patient's own heterozygous germline SNPs** — an internal
  calibrator ※;
- **split-sample** and **leave-one-out** self-calibration ※.

**And the field states the limit of that substitute:** split-sample *"cannot estimate
sample-to-sample (between-sample) biological variation"*; LOO likewise *"does not estimate
between-sample variance"*. So in-sample calibration checks the sampling model, **not the threshold**.
That gap is unsolved and openly acknowledged.

Asked directly whether anyone has ported MRDetect's construction to tumour-only: **absent from the
sources.**

---

## 4. Problem four: get from per-locus evidence to a sample-level call

MRDetect's founding argument, and it is the reason a tumour-only list of ~48,000 candidates is a
usable object at all:

> *"limited input material likely constitutes a major barrier to the effective application of deep
> targeted sequencing"*

Deep targeted sequencing is capped at **10⁻³ VAF** despite ~40,000× depth, because the ceiling is
the number of cfDNA molecules, not the depth. Early-stage median TF is **0.02%**, so the ceiling
misses **44% of stage I patients**. **Breadth beats depth** — integrate thousands of weak
observations rather than sequence a few loci deeply.

Long-read tumour-only methods that follow this route: **NanoRCS** (genome-wide multi-modal TF
estimation, **0.24% TF**) ※ and **SIMMA** (mutation + 5mC + fragmentomics classifier, **100 ppm**) ※.

**Nobody in these sources applies breadth-over-depth to a tumour-only long-read candidate list and
reports what the germline residual does to it.**

---

## 5. Problem five: what do you validate against

Largely unsolved, and the reason is material, not algorithmic.

- **CHIP.** 0–8 variants per plasma sample, median 1, and *"most of these variants were not in
  dbSNP"* — population panels do not remove them. The stated remedy is *"paired PBMC sequencing"* —
  which a tumour-only setting does not have. **No source offers a computational substitute.**
- **Blanks.** Guidance requires **10–50+ independent donor plasma blanks**. Cell-line gDNA is
  explicitly cautioned against: it lacks native nucleosomal fragmentation and lacks age-related
  backgrounds like CHIP, *"creating an artificially clean baseline that severely underestimates
  technical error rates and inflates clinical specificity"* ※.
- **Cohort power.** AccuScan, reporting 90% landmark sensitivity, still states *"the sample size of
  this study was insufficient"* — at **117 plasma samples from 57 patients**.

---

## 6. The synthesis in one grid

Rows are methods; columns are the five problems. **Empty cells are where the field has not gone.**

| | germline w/o normal | error floor | threshold | breadth→sample | long-read native |
|---|---|---|---|---|---|
| **MRDetect** | (informed — subtracted) | SVM read filter | **cross-patient Z** | **yes, founding** | no |
| **AccuScan** | population + PoN | RCA consensus | sample-level 99% spec | yes | no |
| **PhasED-seq** ※ | (informed) | **same-molecule linkage** | — | yes | no |
| **ClairS-TO** | **4 layers incl. haplotype** | hard filters | — | **no** | yes |
| **smrest** ※ | **haplotype + internal calibrator** | read exclusion | — | **no** | yes |
| **LongPhase-S** ※ | (informed) haplotype recalibration | — | — | no | yes |
| **NanoRCS** ※ | population panel | **RCA consensus** | — | yes | **loses methylation** |
| **SIMMA** ※ | — | multi-omic | — | yes | **yes — 5mC + fragmentomics** |
| **shearwater / DREAMS / TNER** | PoN | **beta-binomial / NN error model** | PoN-based | yes | no |
| **this project** | measured the layers **fire on nothing**; gate on ALT-count instead | — | **measured why cross-patient fails; made it valid post-gate** | yes | haplotag + 5mC on disk, unused |

Reading the grid: the long-read rows are **empty in the threshold column** and **empty or "no" in
the breadth column**. The MRD rows are **empty in the long-read column**. That gap is the topic.

---

## 7. What no paper in these sources has done

Two cells, each returned empty by two independent searches with different engines and dates:

1. **Same-molecule co-occurrence of ≥2 tumour-only candidate variants on one long read, used as a
   background-suppression statistic for MRD.** PhasED-seq does the linkage but is tumour-informed
   and short-read; the sources *"do not detail anchoring this somatic read-level linkage back to a
   germline/normal phased background model."*
2. **A published benchmark of what any matched-normal-free haplotype filter removes in practice.**

Both are *absence of found work*, not proof of absence. Item 2 rests on a synthesis's silence and is
the weaker of the two.

---

## 8. Where this project sits, stated without inflation

**What it has that the papers do not:** the missing benchmark of §1 — `MultiHap` and `NoAncestry`
reaching **0 of 48,819 PASS candidates** across five independent ONT tumour-only runs, against
**28.0%** measured private germline. And the measurement of §3 — **99.0%** of a tumour-only
background is variation no control individual carries, which is why the cross-patient construction
does not port, and what makes it port again once the observation is gated.

**What it does not have:** plasma, donor blanks, CHIP, and any answer to §2 — the platform's error
floor is the worst of four, and read length does not lower it.

**The comparison to avoid:** the 1–10% VAF figures are **per-variant calling limits**; this
project's 0.1% is a **sample-level aggregate**. Different units, different axis. Saying "10–100×
better" would be a denominator error a reviewer will catch immediately.

---

## 9. Read before quoting

| Priority | Paper | Why |
|---|---|---|
| **1** | **SIMMA** | long-read + tumour-only + 100 ppm + methylation. If real, it occupies this project's target cell |
| 2 | **NanoRCS** | 0.24% TF, and it shows the consensus/methylation trade explicitly |
| 3 | **smrest** (PMC10925087) | whether the haplotype filter's yield is reported anywhere |
| 4 | **ClairS-TO** (Nat Commun 2025) | same, for `MultiHap` / `NoAncestry` |

All four currently reach this document through synthesis documents or are WAF-blocked.
