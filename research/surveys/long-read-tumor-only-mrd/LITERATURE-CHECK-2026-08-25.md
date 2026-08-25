# Literature check, 2026-08-25 — does the per-molecule direction survive contact with the sources?

Three questions put to NotebookLM against 24 + 17 held sources, after the 2026-08-24 falsification
of R1. Written by a second session; **no file owned by the concurrent session was modified.**

## Q1 — Is "haplotype consistency as a per-molecule background model" novel?

**No. It is published three times over.** The distinction this project drew between *haplotype as
tumour signal* (dead) and *haplotype as background model* (proposed as new) is real, but the second
half is not new.

| System | What it does | Quoted |
|---|---|---|
| **smrest** | phases germline SNPs, assigns each read to a haplotype by posterior probability, then **excludes** the read if its alleles mismatch >10% of its assigned haplotype, or assignment quality < 20 | *"a read is left unassigned (−) and excluded from somatic calling if its haplotype assignment quality score is less than 20, or if the alleles supported by the read mismatch more than 10% of the designated alleles in its assigned haplotype"* |
| **ClairS-TO** | *"verifies whether ancestral germline haplotypes can be identified for the reads containing the somatic alternate allele and filters out candidate variants that disperse randomly across different phased haplotypes"* — i.e. `MultiHap` / `NoAncestry` | as quoted |
| **LongPhase-S** | post-calling recalibration enforcing haplotype consistency on ClairS / DeepSomatic output | *"true somatic variants are expected to co-segregate with their reconstructed somatic haplotypes… false-positive candidates… disperse stochastically across different haplotypes and are discarded"* |

**Consequence.** A proposal framed as "we introduce per-molecule haplotype consistency for
tumour-only" would be pre-empted on arrival. `D4` is now answered: smrest does contain the
mechanism.

## Q3 — But has any of it been measured?

**No, and this is the opening.** Asked specifically for benchmarks, the sources return:

| | Verdict from the sources |
|---|---|
| ClairS-TO haplotype/phasing filter yield | **"described, not benchmarked"** — no isolated number, on any dataset |
| smrest's read-exclusion rule | **"described, not benchmarked"** — no count of excluded reads, no ablation |
| MRDetect's cross-patient threshold ported to tumour-only | **absent from the sources** |

The field ships the mechanism, describes it, and never publishes what it removes.

**This project has the number.** `01` §4.2: `MultiHap` and `NoAncestry` reach **0 of 48,819 PASS
candidates**, 0.002–0.011% of records, across **five independent ONT tumour-only runs** — against
**28.0%** private germline measured per candidate on chr1 (`FIND-0004`).

That is the missing benchmark, and it is unfavourable to the shipped implementation.

### The sources corroborate the structural argument independently

> *"The primary challenge of normal-free pipelines is setting an analytical decision threshold when
> the candidate somatic variant set retains the patient's own private germline variants. If a single
> heterozygous private germline variant is misclassified as somatic, its presence in a tumor-free
> sample at approximately 50% VAF will overwhelm the somatic signal, causing a catastrophic
> false-positive MRD call."*

The field states the problem. `FIND-0006` measured it: **99.0%** of the tumour-only background is
variation no control individual carries. Nobody has published that measurement.

### Independent figures for the contamination level

| Setting | Private-germline share | Source |
|---|---|---|
| GuardantOMNI targeted panel, 943 clinical samples | **41.6%** (11,490 / 27,610) | MYSTIC |
| Tumour-only vs paired, general | 4–12% misclassification | review |
| **ONT tumour-only, ClairS-TO, COLO829 50×** | germline drives **75%** of false positives (61% het + 14% hom) | ClairS-TO FP audit |

This project's 28.0% sits inside a range the field already reports. That is corroboration, not
novelty — the novelty is the **paired** measurement of contamination *and* filter yield on the same
call set.

## Q1 §2 — What IS absent

> **Combining same-molecule linkage of two variants with haplotype consistency, anchored to a
> germline phased background, in a tumour-only setting.** Explicitly absent.

PhasED-seq uses same-fragment linkage — *"multiple somatic mutations in individual DNA fragments to
lower the background noise to less than 10⁻⁶"* — but it is **tumour-informed**, and the sources
*"do not detail anchoring this somatic read-level linkage back to a germline/normal phased background
model."*

This is the one direction that survived the check. It is also narrower than what was proposed
yesterday.

## Q2 — Methylation: where it sits, and a correction

**1. Methylation downstream of a mutation-based candidate filter is absent.** Existing multi-omic
pipelines (SPOT-MAS, SIMMA, NanoRCS, MRD-EDGE) treat mutation and methylation as **parallel
genome-wide channels combined at sample level**, never as filter-then-confirm.

**2. Joint per-read mutation + methylation exists**, on short reads: BiSeqS, MASD-seq,
Methyl-CODEC — all duplex constructions preserving strand complementarity through conversion. For
long reads the capability is stated: *"Long nanopore reads enable co-detection of SNPs and
methylation on the same DNA molecule."*

**3. Correction to this project's own caution.** The claim that cell-line gDNA makes methylation
uninterpretable is **too strong**. Measured in the held source:

- **Global methylation survives shearing.** Mononucleosomal-range 5mC is *"approximately 3.5% in
  cfDNA"* and *"comparable between Raji-derived fragments and native cfDNA"*.
- **Fragmentomic architecture does not.** The mononucleosomal peak shifts to ~120–130 bp against
  native ~160 bp, and *"higher-order periodic peaks are absent in the model samples."*

So the correct boundary is narrower than "methylation is inflated here": a methylation statistic
that **does not depend on fragment length** retains its footing on this material; anything coupling
methylation to fragmentation does not. `EV-0034`'s warning stands for fragmentomics and for
specificity claims, not for global methylation level.

## A circularity trap, recorded

Two of NotebookLM's citations in the Q2 answer resolve to **`SURVEY_SUMMARY.md` — this project's own
document**, uploaded to the notebook on 2026-08-24. When the assistant quoted *"there is no tumor
read population at a locus to assign a haplotype to"* it was quoting **us**, not the literature.

Any future notebook answer must be checked for this. A project document inside the corpus makes the
corpus agree with the project.

## What this does to the plan

| Was | Now |
|---|---|
| P3 = per-molecule haplotype consistency, "nobody has tried it" | **Dead as a novelty claim.** smrest, ClairS-TO and LongPhase-S all do it |
| P1 = a negative about one tool | **Stronger.** The whole filter family is *described, never benchmarked*; this project has the first measurement |
| P2 = cross-individual controls don't transfer | **Corroborated by the sources' own framing**, and still unmeasured by anyone else |
| — | **New:** linkage × haplotype-consistency in tumour-only is the one absent combination |
| Methylation blocked by material | **Partially lifted** — global level survives shearing; fragment-coupled statistics do not |

## Open questions this closes and opens

- **D4 — closed.** smrest contains the per-molecule haplotype mechanism. Novelty of that framing: 1.
- **D11 — new.** Has anyone benchmarked *any* matched-normal-free haplotype filter's yield? Sources
  say no. If that holds outside this corpus, P1 is a paper on its own.
- **D12 — new.** Does PhasED-seq's linkage framework have a tumour-only analogue anywhere?

---

# Round 2 — open problems in tumour-only MRD, taken from the sources

Query scoped to **12 external sources only**; the project's own five Vietnamese notes and
`key.md` were excluded by id, and NotebookLM was required to flag synthesis vs primary and to
answer "no stated limitation" where a source only describes.

## Provenance correction to Round 1

`3e533198` — the source behind every smrest / ClairS-TO / LongPhase-S quote in Round 1 — is a
**markdown synthesis document**, not a primary paper. Its own summary reads *"This comprehensive
source explores…"* and its citations are internal `[cite: N]` markers. The same is true of
`528151cf`.

**Therefore the Round 1 verdict "described, not benchmarked" is weaker than stated.** It is
supported by a synthesis's silence, not by having read ClairS-TO's and smrest's primary texts. The
claim stands as *"no benchmark found in this corpus"*, which is not the same as *"none exists"*.
Closing it needs the smrest and ClairS-TO primary PDFs — still WAF-blocked.

## The problems, ranked by independent mentions

### R1a · ctDNA scarcity — the input ceiling  ·  4 sources  ·  PRIMARY

> *"limited input material likely constitutes a major barrier to the effective application of deep
> targeted sequencing"* — Zviran/MRDetect, primary

Quantified: deep targeted sequencing is capped at **10⁻³ VAF** despite ~40,000× depth; early-stage
median TF is **0.02%**; the ceiling misses **44% of stage I patients**. AccuScan adds that
post-treatment TF is *"significantly lower than 0.01%"*.

**Status for this project: already rediscovered, independently.** `EXP-S1-002` measured ~2 expected
signal reads at 0.01%. That is corroboration of a known ceiling, **not** a novel finding, and it
must be cited as such rather than presented as new.

### R1b · Clonal haematopoiesis  ·  4 sources  ·  PRIMARY  ·  ⬅ **untouched by this project**

> *"Paired PBMC sequencing analysis may be needed to remove CHIP variants… to identify true somatic
> mutations."* — Yaung et al., JCO PO 2020, primary

Quantified: **0–8 CHIP variants per plasma sample, median 1**, and *"most of these variants were not
in the Database of Single Nucleotide Polymorphisms (dbSNP)"* — so population databases do not remove
them, exactly as they failed to remove private germline here (`FIND-0002` Arm B).

Two consequences this project has never considered:

1. **CHIP is a second oracle-free problem with the same shape as germline.** A non-tumour somatic
   signal, patient-specific, invisible to population panels, requiring a matched WBC sample the
   tumour-only setting does not have.
2. **CHIP sits at low VAF — so it would pass this project's gate.** The gate keeps sites with 1–2
   ALT reads. Germline (≈50% VAF) is removed by construction; CHIP (typically low VAF) is not. This
   is a **falsifiable prediction about the gate that has never been tested**, and the material
   cannot test it: cell-line gDNA has no CHIP at all, which is precisely why the blanks are
   artificially clean (`EV-0034`).

### R3a · Threshold calibration and the germline leak  ·  3 sources

Already this project's P2. One new external number worth having:

> *"without prior tumor information, tumor-agnostic classification achieved a maximum ROC-AUC of
> **0.808**"* against **>0.89–0.984** tumour-informed — Lin et al., IJMS 2024, primary

That is a **published oracle gap**, in AUC, on short-read targeted cfDNA. This project's oracle-gap
work (`FIND-0005`) now has a comparator it did not have.

### R3b · Standardisation and cohort power  ·  3 sources

Pipeline choice alone moves diagnostic F1 by **up to 8%**. AccuScan, having reported 90% landmark
sensitivity, still states *"the sample size of this study was insufficient"* at **117 plasma samples
from 57 patients** — a useful calibration for what "insufficient" means to reviewers.

### R5 · Long-read-specific limits  ·  2 sources  ·  ⬅ **attacks this project's premise**

> *"Read length helps with mapping and phasing but does not lower the per-base background that
> limits low-VAF calling, and long-read platforms currently carry higher per-base error,
> particularly for indels."*

> *"Biological constraints: cfDNA fragment size (~150–200 bp) limits the utility of ultra-long
> reads"*

Benchmarked error rates: ONT SNV error in non-easy regions **0.37%**, the worst of four platforms
(AVITI 0.04%, Illumina 0.12%, PacBio 0.23%); ONT homopolymer indel **~18%**.

**This is the sharpest thing found today.** The project's platform premise is that long reads carry
more per-molecule evidence. These sources say read length does not touch the quantity that limits
MRD, and that cfDNA fragments are too short to exploit read length anyway. Both are quoted, both are
benchmarked, and neither has been answered in this repository.

## Selection rule proposed, so this list does not become another week

A problem enters only if all three hold:

1. **falsifiable in one afternoon** on files already on disk;
2. **a number at both ends** — how big the problem is, and how much the method moves it;
3. **a named baseline can lose**.

Against that rule: R1b (CHIP) fails (2) on this material — no CHIP exists in cell lines. R5 passes
all three and is the only untouched problem that does.

## Open questions added

- **D13.** Does the gate retain CHIP-like low-VAF non-tumour variants? Untestable on this material;
  testable the day plasma arrives. Register it now, before the answer is known.
- **D14.** If read length does not lower the per-base background, what does this platform buy that
  Illumina does not — measured, not asserted?
