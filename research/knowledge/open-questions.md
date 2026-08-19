# Open questions

What is not known, ordered by how much it blocks. Each entry names what would settle it, so a
question can be closed by doing something rather than by deciding it feels resolved.

> **Parked 2026-08-19.** Section A below, and B2–B5, were written for the SNV + haplotype phase
> + native methylation direction, which is parked in
> [`../parked/snv-phase-methylation/`](../parked/snv-phase-methylation). They are kept because
> they are good questions, not because they are current. **A1, B1, C and D stand on their own**
> and matter for any direction.
>
> The live blocking question is now: *what is the project's full problem set?* — see
> `orchestration/state.yaml`.

---

## A. Parked — the previous direction's blocking questions

| # | Question | What would settle it | Status |
|---|---|---|---|
| A1 | What is the somatic / germline / technical-artifact **composition** of the 48,819 PASS SNV candidates? | Class definitions first, then a composition estimate using the PoN and population resources in [`datasets.md`](./datasets.md) | Tracked as `SUG-2026-08-001` `[repo]` |
| A2 | What does **"tumor recognition"** mean as a measurable quantity — on what unit, against what positive class? | A written metric definition naming the unit (candidate / molecule / sample), the positive class and the label source | Tracked as `SUG-2026-08-002` `[repo]` |
| A3 | What exactly is the **SNV-only baseline** that "incremental" is measured against? | A frozen, versioned baseline configuration — features and scoring rule | Tracked as `SUG-2026-08-003` `[repo]` |
| A4 | Do phase and native methylation add **discriminative value**, or are they redundant? | The ablation grid, once A2 and A3 exist | Tracked as `SUG-2026-08-004`, blocked `[repo]` |
| A5 | What is the **full problem set** this project takes on? | A scope statement covering all the positions it addresses, not one grid cell | Raised 2026-08-19 when the project's row was pulled from the signal matrix |

## B. Feasibility — answerable with the data on disk

> B1 measures joint availability and stands whatever direction is chosen; B2–B5 came with the parked direction.

| # | Question | What would settle it |
|---|---|---|
| B1 | How many reads at a candidate locus carry **allele + phase + methylation together** at 1%, 0.1%, 0.01%? | The feasibility funnel, region-scoped, on one dilution BAM. This is the first number that decides whether the question is testable at all `[repo]` |
| B2 | Does **LongPhase 2.0.2** produce usable phase blocks on 25× ONT data, and how long are they? | Run it on one region; measure block N50 and the fraction of candidates falling inside a block. Nothing is phased today `[verified 2026-08-19]` |
| B3 | Whole-BAM or region-sliced haplotagging? | Cost comparison on one chromosome. Region-scoped is far cheaper but yields shorter blocks `[repo]` |
| B4 | What does the **methylation signal actually look like** on these reads — call rate per CpG, probability distribution, read-end behaviour? | Parse `MM`/`ML` with `pysam` over a region; no `modkit` needed `[verified 2026-08-19]` |
| B5 | Is the **tumor/normal methylation difference** large enough to separate molecules at all? | Compare pure `HCC1395.bam` against `HCC1395BL.bam` over matched regions — evaluation-only use of the normal |

## C. Provenance and data integrity

| # | Question | Why it matters |
|---|---|---|
| C1 | Which **basecaller and model** produced these modification calls? | No `@RG`, no basecaller `@PG` in the header; the "5 kHz simplex 5mCG/5hmCG" description is a naming claim only `[verified 2026-08-19]`. Methylation calibration depends on it |
| C2 | Do the other HCC1395 ONT trees (`ONT/`, `ONT_Dorado/`) carry `MM`/`ML`? | Decides whether the existing ClairS/DeepSomatic outputs there are usable alongside the methylation axis `[unverified]` |
| C3 | Is the **replicate structure** (5 blanks, 3 per level) usable for a limit-of-blank estimate? | The research contract assumes one replicate per level and rules an LoD claim out on that basis. The data on disk contradicts the assumption — see [`datasets.md`](./datasets.md) §2 `[verified 2026-08-19]` |
| C4 | Can per-read tumor/normal labels be recovered reliably at scale, and what is the collision rate? | Only demonstrated in one pilot window `[repo]`. Labels are evaluation-only |
| C5 | Is the v0.5.0 ClairS-TO run **reproducible today**? | The wrapper does not start in a bare shell (`python` missing) `[verified 2026-08-19]` |

## D. Literature

| # | Question | What would settle it |
|---|---|---|
| D1 | Do the seven indexed papers actually say what the records claim? | PDF-level verification. All seven are `external_report` / `pdf_available: false` `[repo]` |
| D2 | Does rolling-circle consensus really lose native base modifications (the NanoRCS trade-off)? | The NanoRCS methods section. This is currently an inference, flagged `[unverified]` in the signal matrix |
| D3 | Is the candidate gap real beyond these seven documents? | A documented systematic search with queries, databases and dates. Not started `[repo]` |

## E. Design questions deliberately left open

Not blocking, and deliberately not answered before the questions above:

- How haplotypes should be assigned, how methylation similarity should be computed, how phase
  blocks should be constructed, how evidence should be combined into a score, and how the
  configurations should be evaluated. `research/knowledge/` records these as design decisions to be
  made after the feasibility funnel, not before `[repo]`.

---

## Next thing to do

**B1 and B2 together, on one region of one dilution BAM.** They cost little, they are pure
measurement, and until B1 has a number the whole research question may be untestable on this
data — which is itself a publishable finding.
