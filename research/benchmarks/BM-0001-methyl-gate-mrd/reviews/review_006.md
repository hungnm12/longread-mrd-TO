# Benchmark Review — Panel

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v1.1_draft.md` (v1.1, DRAFT — design iteration 6)
Reviewer role: five-lens adversarial panel (grill-me), post-QC redesign review
Review iteration: 6
Review round: 1 of 3
Date: 2026-09-19

No panel member edited the protocol and no panel member executed any part of the benchmark.
`protocols/v1.0_locked.md` and the whole of `EXEC-001` were opened read-only and are unchanged.

This file is a transcription of the round-1 panel record. It performs no analysis of its own.

---

## Panel composition

Five lenses were run against one draft. Each lens returned an independent structured critique
with its own verdict, major issues, minor issues, and two standing checks.

```text
Lens 1  MECHANISM DISCRIMINATION
        "Does the new criterion actually discriminate the mechanism?" Construct adversarial
        filters that know only a methylation-PATTERN-BLIND read property and ask whether each
        new criterion is satisfied while methylation pattern contributes nothing.

Lens 2  STRICTNESS
        "Is every new criterion STRICTLY HARDER than what it replaces, or has the bar moved
        sideways?" Search for a data configuration that fails v1.0 and passes v1.1; audit
        qc_001.md constraint (c) item by item; check the reverse failure.

Lens 3  STATISTICAL VALIDITY AT THESE COUNTS
        Sampling distributions, nulls, intervals, pseudo-replication of the TF0 blanks,
        multiplicity, and whether UNRELIABLE / undefined cases propagate into the verdict.

Lens 4  EXECUTABILITY AND COST HONESTY
        Can EXEC-002 be run exactly as written with no judgement call, at a stated cost, with
        EXEC-001 preserved, QC-07's leakage guarantee re-earned, and determinism strong enough
        to reproduce EXEC-001 where the two overlap.

Lens 5  PRE-REGISTRATION HYGIENE AND CLAIM CONTROL
        v1.1 against qc_001.md constraint (b), QC-03, and AGENTS.md rules 3 and 8.
```

Two lenses independently used the identifiers `M1`-`M6`. They are disambiguated throughout this
file as `M1 (lens 2)` … and `M1 (lens 5)` … .

---

## Verdict rule

```text
ACCEPT  only if  zero REVISE  AND  zero REJECT  AND  zero major issues
```

The rule is a conjunction over the whole panel. A single REVISE, a single REJECT, or a single
surviving major issue from any lens blocks acceptance.

---

## Verdict

NOT ACCEPTED — REVISE

```text
Lens 1  mechanism discrimination      REVISE    7 major
Lens 2  strictness                    REVISE    6 major
Lens 3  statistical validity          REVISE    8 major
Lens 4  executability / cost          REVISE    7 major
Lens 5  pre-registration hygiene      REVISE    6 major
                                      -------------------
                                      5 REVISE, 0 REJECT, 0 ACCEPT, 34 major issues
```

No lens returned REJECT. Every lens recorded that the architecture is right and that the
preservation and post hoc labelling discipline is strong; every lens nonetheless found blocking
faults inside the criteria that carry the mechanism claim.

---

## Standing checks, per lens

```text
                         strictly_harder_check                 post_hoc_labelling_check
Lens 1   PASS on structure, one leg unverifiable            PASS
Lens 2   FAIL on one criterion (S5)                         PASS, with one gap
Lens 3   PASS on the criteria, two exceptions               PASS
Lens 4   PASS, with one qualification                       PASS
Lens 5   PASS in logical form, one open exception           FAIL (repairable)
```

Round-1 summary of the two checks, transcribed:

- **Strictness.** Four lenses found S6, S7, C3 and F9-F11 purely additive and no forbidden-list
  item moved (primary level 0.1%, call threshold 3.0, the `1 <= alt <= 2` gate, V1/V2, S1-S3 all
  carried verbatim). Lens 2 found the one provable sideways move: v1.1's S5 leg (a) reproduces
  only clause (i) of v1.0's S4, and §20.6 drops S4 from the verdict conjunction, so a
  configuration exists that fails v1.0 and passes v1.1. Lens 1, lens 3 and lens 5 each recorded
  that S5's `LOW_COUNT` escape clause is undefined, so that leg cannot be shown to be harder.
- **Post hoc labelling.** Four lenses passed it: the banner, §1's `posthoc: true` and
  `posthoc_scope`, the per-section POST HOC callouts, §22.2's mandatory
  `posthoc = POST_HOC_2026-09-19` column, §20.0's verbatim reproduction of
  `results/registered_outcome.txt`, §24 item 14, and §22.4's prohibition on overwriting any
  EXEC-001 artifact. Lens 5 failed it on three inconsistent registers (banner vs §1 vs §24
  item 14), on unlabelled post hoc numeric constants, and on §15.5.8 calling a post hoc rule
  "a preregistered-in-this-document consistency rule".

---

## Lens 1 — MECHANISM DISCRIMINATION

Verdict: **REVISE**

> "Under the assigned test — construct a scenario in which each new criterion is satisfied while
> methylation PATTERN contributes nothing — C3, S5 leg (c) and S6 leg (ii) fall to a filter that
> knows only per-read error rate, and the EXEC-001 data already point at that filter: B1 retains
> 40% of scorable ALT reads in a TF0 blank while keeping 4.91% of reads overall, an 8.1x
> enrichment of error-carrying reads at zero tumour fraction, and the locked cutoff is exactly
> 1/13 so that one discordant methylation call on a low-CpG read is sufficient to keep it. …
> REJECT would be wrong — the architecture is right and the preservation and labelling discipline
> is exemplary. ACCEPT would repeat the S4 mistake one level up."

### MAJ-01
Section: §10.1 (C3 definition), §10.2, §18.1, §20.4 S6 leg (ii), §20.3 S5 leg (c), §15.5.8 NULL-2
Issue:
  C3 is a null for CpG DENSITY only, but the draft asserts exclusivity: §10.1 says "Therefore
  `B1 > C3` cannot be produced by CpG density, by read length, by filter aggressiveness, or by
  counting statistics … It can be produced only by the methylation pattern on the individual
  read." That is false. `score_b1 = d/t` (run_sample.py line 91) is a PER-READ METHYLATION-CALL
  DISCORDANCE RATE, maximised by a noisy read, not only by an aberrantly methylated one. C3's
  within-stratum permutation destroys the read-to-error-rate correspondence exactly as thoroughly
  as it destroys the read-to-pattern correspondence, so a filter that knows ONLY per-read error
  rate passes leg (ii). The data already say this is the live explanation: at TF0 on HCC1395 —
  zero tumour DNA present — B1 keeps 10/25, 8/22 and 8/20 scorable ALT reads while keeping
  `K_B1/n_scorable = 2895/58990 = 4.91%` of all scorable reads, an 8.1x enrichment of ALT-carrying
  reads in the top-5% discordance tail IN A SAMPLE WITH NO TUMOUR. Second mechanism, same
  direction: `cut = 0.076923 = 1/13` exactly, so any read with `t <= 12` and a SINGLE discordant
  call is kept. Read length is likewise NOT held fixed by C3.
Why blocking:
  This is QC-01 repeating one level up. The whole mechanism half of the verdict — S5 leg (c),
  S6 leg (ii), NULL-2, §20.7's "MECHANISM UNSUPPORTED — PATTERN NOT ISOLATED" branch — rests on
  that assertion. If the advantage is per-read error rate, every v1.1 criterion can pass and the
  benchmark reports MECHANISM ESTABLISHED for a filter that is selecting noisy reads.
Required change:
  Add a deterministic, methylation-PATTERN-blind read-property comparator arm (C4) built in the
  same BAM pass, on the same scorable set, swept over the same percentile grid, and add it as a
  further necessary leg to S5 and S6 with an uncertainty band. Candidates: per-read disagreement
  against the consensus at confident NON-CpG positions; per-read fraction of modified-base calls
  in the ambiguous band; per-read NM/aligned-length or mean BQ. Additionally emit the joint
  distribution of `d` and `t` among kept ALT reads at TF0 and 0.1%; emit per arm per sample
  (ALT retention)/(global keep fraction) at TF0 as a standing diagnostic; and delete or restate
  the exclusivity sentences in §10.1 and §18.1, striking §18.1's "read length" claim.

### MAJ-02
Section: §20.3 S5 leg (b), §20.4 S6 leg (i), §15.5.8, §16.2
Issue:
  C2 is the comparator that killed v1.0 and is the only arm in v1.1 with no uncertainty band.
  S5 leg (b) and S6 leg (i) are bare inequalities, while legs (ii) and (iii) get 200-draw 95th
  percentile bands. C2's top-k boundary is resolved by a seeded shuffle of a heavy tie block.
  C2's HCC1395 blank ALT retention 0.037706 is the mean over five TF0 replicates of kept counts
  0, 1, 1, 1, 1 — four reads. COLO829's 0.021429 is 0, 1, 0, 0, 2 — three reads. If C2's
  tie-break had kept ONE more blank ALT read on HCC1395 TF0 rep1, C2's ratio falls from 1.6839 to
  1.389 and B1's 1.6741 WINS leg (b).
Why blocking:
  §20.7 makes S5's outcome a named verdict and a leg-(i) failure "MECHANISM REFUTED BY THE
  DENSITY CONTROL". Both verdicts are decided by a margin narrower than the arm's own tie-break
  noise — the S4 failure mode restored.
Required change:
  Re-run C2 over at least 200 tie-break seeds (free in aggregation, the BAM pass is shared) and
  emit `retention_ratio_p05/p50/p95` and `zlo_min_p05/p50/p95` as for C1 and C3. Rewrite S5 leg
  (b) as "> 95th percentile of retention_ratio(C2) across tie-break seeds" and S6 leg (i) as
  "> 95th percentile of Z(C2, tau) across tie-break seeds". Report per sample the number of reads
  tied at the C2 top-k boundary.

### MAJ-03
Section: §16.5 (significant-figure floor), §20.3 S5 (LOW_COUNT clause), §20.10
Issue:
  The protocol adjudicates S5 at a precision it forbids itself to report, and leaves the tie
  undefined. §16.5 caps HCC1395's B1 ratio at 2 significant figures (blank totals 10/8/8, mean
  8.67), at which B1 is 1.7 and C2 is 1.7 — EQUAL — yet §20.10 adjudicates leg (b) at four
  figures ("FAILS (by -0.0098)"). On COLO829 the stated fallback — "evaluated on the counts as an
  inequality … flagged LOW_COUNT" — names no quantity. §16.2 also never names the blank set;
  EXEC-001 used all FIVE TF0 replicates while §15.5.1/§15.5.4 use rep1-3, and under a 3-blank
  convention the same data give B1 1.5687 vs C2 1.9955 on HCC1395 and B1 4.164 vs C2 3.734 on
  COLO829 — same signs, margins swinging by more than an order of magnitude.
Why blocking:
  S5 is a gate in §20.7's outcome ladder and that gate has no defined bar on either individual.
Required change:
  (1) State the blank set normatively and use one convention everywhere. (2) Define the tie rule:
  equality at the permitted precision returns UNDECIDABLE, never HELD and never FAILED.
  (3) Replace the LOW_COUNT hand-wave with an explicit rule on one named pair of counts.
  (4) Re-derive §20.10 under whichever rule is adopted.

### MAJ-04
Section: §15.5.4 (AXIS-L), §15.5.5 (replicate aggregation), §10.3
Issue:
  The sweep matches on the MEAN retention over the three 0.1% replicates while the statistic is
  the MIN over those replicates. B1's per-replicate R at 0.1% on HCC1395 is
  0.488889 / 0.714286 / 0.622222 — a spread of 0.225, more than twice T's 0.10 target spacing —
  and the replicate carrying the minimum `lo` is rep1, the LOWEST-retention replicate. Two arms
  matched on the mean can be mismatched by 0.1-0.2 at the single replicate that determines Z.
  §10.3 forbids the obvious repair.
Why blocking:
  QC-02's finding was that the arms were compared at different points on a precision curve.
  Matching the mean while deciding on the min re-opens that door at the replicate level, in the
  criterion the draft calls "THE DECIDING CRITERION".
Required change:
  Either (a) permit arm- and sample-specific PCT for the sweep only, so each 0.1% replicate is
  matched to tau individually; or (b) keep mean matching but emit per-replicate realised retention
  for every arm at every target, require `max_r |R_B1 - R_comparator| <= one ALT read`, return
  UNDECIDABLE otherwise, and record which replicate carried the min for each arm.

### MAJ-05
Section: §15.5.7 (comparison at matched retention), §15.5.2 (refinement bound)
Issue:
  "At the same retention" is defined loosely enough to re-admit the count mismatch the sweep
  exists to remove. Step 3 admits a nearest-point estimate if `|x - tau| <= 0.05` and §15.5.2 only
  guarantees adjacent grid points within 0.10; nothing requires the two ARMS to be matched to each
  other. At the observed scorable_ALT (35/45/45 and 51/55/63), 0.05 is ±1.8 to ±3.2 ALT reads and
  0.10 is ±3.5 to ±6.3, against a count floor of 5 kept reads. Separately, step 2's linear
  interpolation of Z interpolates a step function of integer counts: at kept counts of 5-9 one
  read moves z by roughly 0.5-1.0.
Why blocking:
  S6 leg (i) can return HELD on a margin generated entirely by residual retention mismatch and
  interpolation artefact, and the protocol never reports the residual or its sign.
Required change:
  Match on the integer kept-ALT count: `n_tau = round(tau * scorable_ALT)`, each arm's grid point
  selected to realise `n_tau` exactly, achieved count recorded; where exact matching is impossible
  require `|kept_ALT(B1) - kept_ALT(comparator)| <= 1` and return UNDECIDABLE otherwise. Emit both
  arms' retentions, kept counts and their signed difference on every row. Drop linear
  interpolation of Z, or justify it against the observed step size.

### MAJ-06
Section: §15.5.5, §15.5.7 step 1, §15.5.8 NULL-1/NULL-2, §20.4 S6 legs (ii) and (iii)
Issue:
  For the stochastic arms, "95th percentile of { Z(C3, tau) } over 200 draws" has no single
  meaning, because tau is located on a curve that is itself random. Two admissible readings:
  (a) match every draw to tau on its own realised-retention curve and take the 95th percentile of
  the per-draw `Z_hat(tau)`; (b) locate tau on the median curve and take the 95th percentile at
  those fixed grid points. Reading (a) raises the bar; reading (b) lowers it.
Why blocking:
  Legs (ii) and (iii) are decided against that percentile, and leg (ii) is the only leg the draft
  says bears on the mechanism claim. Leaving the reading to the executor leaves the height of the
  bar to be set after the curves are visible.
Required change:
  Mandate per-draw matching (reading (a)): each draw bracketed and interpolated to tau on its own
  retention curve, band = 5th/95th percentile of the per-draw `Z_hat(tau)`, count floor applied
  per draw with the fraction of excluded draws reported. Add the same rule to NULL-1 and NULL-2.

### MAJ-07
Section: §20.4 (region column), §20.7 (UNDECIDABLE branch), §24 item 15
Issue:
  A verdict-bearing label is never defined. §20.4 requires a `region` column marking each target
  `DEGENERATE_HIGH`, `DISCRIMINATING` or `EXCLUDED_UNDERPOWERED`, and §20.7 makes "zero
  DISCRIMINATING targets" an UNDECIDABLE verdict. The only guidance in 1,264 lines is the prose
  "The discriminating region is the middle of T"; a grep returns lines 804, 805, 871, 1170, 1192,
  1257 with no threshold in any of them.
Why blocking:
  This is the one place where a post hoc choice made with the results in view changes the reported
  outcome. It also leaves ambiguous whether a FAILING target labelled DEGENERATE_HIGH still fails
  S6.
Required change:
  Fix the region rule mechanically and before EXEC-002 in the protocol text (e.g. DEGENERATE_HIGH
  iff `|Z(B1,tau) - Z(B0)| < delta` for a stated delta, or iff tau >= a stated value;
  EXCLUDED_UNDERPOWERED iff the count floor fires; DISCRIMINATING otherwise). State that a failing
  leg at ANY evaluable target fails S6 regardless of region label, and that region gates only the
  UNDECIDABLE branch.

### Lens 1 minor issues

1. §15.5.6 clause (a) says "both compared arms" but S6 has three legs with three comparators;
   whether a target excluded for leg (ii) remains evaluable for leg (i) is unstated. Say per-leg.
2. §15.5.6 clause (b) sets the blank floor on the MEAN kept_ALT over TF0 rep1-3 being >= 1. A mean
   of 1 is satisfied by 0/0/3. Observed precedent: COLO829 B1 blank totals 2/0/4. The floor should
   be on the number of nonzero blank replicates, not the mean.
3. The count floor systematically removes the targets the draft advertises as discriminating: at
   HCC1395's mean scorable_ALT of 41.7, tau = 0.10 gives 4.2 kept reads, below the floor of 5.
4. §10.2's trigger (median within-stratum score variance below 1% of global) is arbitrary and
   one-sided: nothing catches a C3 whose 10 strata are too coarse. Report the within-stratum RANGE
   of score_C2, not only the variance of score_b1.
5. §15.5.8's "No p-value is computed" while thresholding against the 95th percentile of 200 draws
   is a one-sided alpha = 0.05 permutation test under another name. Say what it is.
6. Numeric audit: every figure checked is correct and traceable — §20.4's 0.49/0.71/0.62 and
   0.18/0.35/0.29 match per_sample_metrics.tsv; §20.10's 1.6741/1.6839/2.9127/2.9041 match
   ablation_results.tsv; §15.5.1's 35-45 and 51-63 match; §15.5.7's +2.2995 and +0.7396 match;
   §22.1's n_scorable_reads = 58,879 matches execution/raw. No fabricated number found.
7. §22.1's feasibility claim is correct as stated; the extended schema is specified adequately,
   except that it must also carry whatever per-read quantity MAJ-01's C4 arm needs.

### Lens 1 supporting record

Confounders named: per-read basecall/modification-call error rate (8.1x blank enrichment
measured); integer granularity of the score (`cut` = 1/13 exactly); read length; C2's tie-break
seed; replicate-level variance interacting with the min-over-replicates statistic; library /
flow-cell batch differences between tumour and normal components; integer count granularity at
1-9 reads on COLO829.

Missing controls: a methylation-PATTERN-blind read-quality comparator arm (the central defect);
a read-length comparator; a tie-break-seed band for C2; a within-stratum adequacy check for C3 in
the over-coarse direction; a negative control on the sweep machinery itself.

Missing metrics: joint `(d, t)` distribution among kept ALT reads; (ALT retention)/(global keep
fraction) at TF0 per arm per sample; realised kept-ALT counts for both arms at every matched
target and their signed difference; per-replicate realised retention and the argmin replicate;
C2's tie-break band; number of reads tied at the C2 top-k boundary; fraction of C3/C1 draws
excluded by the count floor.

---

## Lens 2 — STRICTNESS

Verdict: **REVISE**

> "M1 exhibits a concrete configuration that fails v1.0 and passes v1.1 §20.6 … M3, M4, M5 and M6
> are not loosenings but under-specifications inside the two criteria that carry the mechanism
> claim, each of which leaves a decision to be made after the curves are seen — which for post hoc
> criteria is the same failure by another route. M2 is the reverse failure the lens asks about."

### M1 (lens 2)
Section: §20.3 (S5 leg a), §20.6 (verdict rule), §20.9 (strictness argument)
Issue:
  S5 does not contain v1.0's S4, although §20.9 asserts it does, and §20.6 removes S4 from the
  verdict conjunction altogether. v1.0 §20 reads "H1 is supported only if S1, S2, S3 and S4 all
  hold", and v1.0's S4 has TWO clauses: (i) B1's ALT retention at 0.1% exceeds its TF0 retention
  on both individuals, AND (ii) this must NOT hold for C1 beyond its own sampling noise. v1.1's S5
  leg (a) reproduces clause (i) only — §20.10 confirms the reading by evaluating it as
  "1.6741 > 1.0 : holds". Clause (ii) survives nowhere in the verdict path. §20.9's line
  "S5 = S4 AND (b) AND (c). … Strictly harder." is therefore false as written. §21 F7 and F8 are
  carried over verbatim, so the protocol now contains two contradictory rules for the same data.
Why blocking:
  This is the one place where the bar provably moves sideways. Failure scenario: EXEC-002 returns
  C1 retention ratio 1.45 with a 5-95 band of [1.20, 1.80] on HCC1395 while S5 legs (a)(b)(c), S6
  and S7 all hold. Under v1.0, S4 clause (ii) fails and F7 names it MECHANISM UNSUPPORTED. Under
  v1.1 §20.6 the verdict is "H1 SUPPORTED, MECHANISM ESTABLISHED".
Required change:
  Either (a) write S5 leg (a) as the whole of v1.0's S4, both clauses, quoted verbatim, or (b)
  keep S4 itself in §20.6's conjunction as a named necessary condition and restrict the word
  "demoted" to what S4 LICENSES. Correct §20.9's S5 line. State explicitly that F7 and F8 remain
  binding and say which of F7 and §20.6 controls when they disagree.

### M2 (lens 2)
Section: §20.3/§20.4 (S5, S6), §20.7 (named outcomes), §21 F9/F11, §23.1
Issue:
  S5 leg (b) is already decided against B1 by data the protocol REQUIRES EXEC-002 to reproduce
  exactly, so the v1.1 verdict is fixed before EXEC-002 runs, and the criterion the draft calls
  "THE DECIDING CRITERION" cannot affect it. F11 requires exact reproduction of EXEC-001's
  ablation values; `retention_ratio` IS an ablation-row value (HCC1395 B1 1.6741, C2 1.6839). So
  S5 leg (b) must fail on HCC1395. §20.7 then short-circuits: row 2 fires and rows 3 and 4, both
  conditioned on "S5 holds", are unreachable. S6 legs (i) and (ii) therefore have NO named outcome
  in a section titled "Named outcomes, fixed in advance, which may not be relabelled".
Why blocking:
  The benchmark spends a full re-run to compute a criterion its own verdict architecture cannot
  consult, whose result will have to be described under a label not fixed in advance.
Required change:
  Record in §20.3 that S5's outcome is DETERMINED IN ADVANCE by preserved EXEC-001 values plus
  F11, and state the determined value. Restructure §20.7 so S6 and S7 carry their own named
  outcomes independently of S5 — every combination of {S5 pass/fail} x {S6 leg outcomes} must map
  to a fixed label. If S6 is genuinely not deciding, withdraw the §20.4 claim that it is.

### M3 (lens 2)
Section: §20.3 (S5 legs b, c), §16.5, §20.10
Issue:
  S5 has no defined comparison rule at any precision the protocol permits, on either individual.
  §16.5 caps HCC1395 at 2 significant figures, at which B1 is 1.7 and C2 is 1.7 against a strict
  ">". On COLO829 §16.5 forbids a ratio entirely; C2's HCC1395 blank kept counts are 0/1/1, mean
  0.67, so §16.5 forbids C2's HCC1395 ratio as well — meaning §20.10's audit comparison is
  computed at a precision §16.5 forbids on BOTH sides. The stated fallback names no quantity.
Why blocking:
  A verdict-bearing criterion whose evaluation rule is undetermined on both individuals is
  decidable after the fact. The draft's own demonstration that the redesign is conservative
  violates the reporting floor it introduces in the same document.
Required change:
  For each leg of S5, name the exact quantity compared, the exact precision at which the
  COMPARISON is made (as distinct from the precision at which the value is REPORTED), and the tie
  rule (a tie must be a FAIL, since the criterion is strict). Define the LOW_COUNT fallback as one
  specific inequality on one specific pair of counts. Re-derive §20.10 at the permitted precision
  or state that it is a full-precision audit note excluded from §16.5.

### M4 (lens 2)
Section: §20.4, §20.7 (UNDECIDABLE row), §22.2, §20.8 clause 3
Issue:
  The `region` label is never defined anywhere in the document, yet it decides between the
  benchmark's best and its most ambiguous outcome. §20.8 clause 3 freezes T and P against
  post-hoc change but says nothing about the region assignment. Separately, S6 requires dominance
  "at EVERY evaluable target" with no exclusion of DEGENERATE_HIGH, so a target the protocol
  itself calls degenerate can also produce a refutation.
Why blocking:
  Both directions let the benchmark report a conclusion its own design says is unsupported: a pass
  carried entirely by near-degenerate targets reported as MECHANISM ESTABLISHED, or a hair's
  breadth loss at a near-degenerate target reported as "MECHANISM REFUTED BY THE DENSITY CONTROL".
Required change:
  Define `region` mechanically and numerically in §15.5, before execution, from quantities
  computable without seeing the comparison outcome. Add it to §20.8 clause 3's frozen list.
  Exclude DEGENERATE_HIGH targets from S6's conjunction in BOTH directions; their exclusion counts
  toward the 3-evaluable-target floor as an exclusion, never as a pass.

### M5 (lens 2)
Section: §15.5.4 (axes), §15.5.5 (curves), §15.5.6 (count floor)
Issue:
  The matching and the count floor are defined on replicate MEANS while the statistic is a
  MINIMUM over replicates. B1's retention at 0.1% is 0.489/0.714/0.622 on HCC1395 and
  0.176/0.345/0.286 on COLO829. Two arms can share a mean R and differ by a factor of two at the
  minimum replicate — QC-02's complaint reappearing one level down, inside the fix written for it.
  The floor compounds it: mean kept >= 5 admits a replicate with kept = 0, which under V1 gives
  `sample_sd = 0` and "no estimate", making Z UNDEFINED and therefore a failure — so an empty
  replicate produces MECHANISM REFUTED. This case is live: COLO829 TF0 rep2 already has
  `alt_kept = 0`, `G = 0`, `sample_sd = 0` at PCT=95.
Why blocking:
  S6 is the criterion supposed to remove count scale as a free variable; matching on the mean and
  deciding on the min does not remove it at the point of decision.
Required change:
  Match on the replicate structure that carries the statistic, or state that x is the MINIMUM
  replicate's R. Set the count floor on the minimum replicate. Add an explicit rule that a target
  where Z is UNDEFINED because of counts is EXCLUDED_UNDERPOWERED — never a pass and never a
  refutation. Emit per-replicate kept counts and per-replicate R.

### M6 (lens 2)
Section: §15.5.7 steps 3-4, §15.5.2 (refinement cap)
Issue:
  The nearest-point estimate has an undefined branch and the default resolution is the permissive
  one. Step 4 covers only the case where both estimates exist and disagree; nothing says what
  happens when `Z_near` is INADMISSIBLE. §15.5.2's refinement triggers only on gaps > 0.10 and is
  capped at 6 bisections, so `|x - tau| > 0.05` is reachable, especially on COLO829 where R is
  quantised in steps of ~1/55.
Why blocking:
  The two-estimate agreement requirement is the draft's stated protection against interpolation
  artefacts in the deciding criterion, and it switches itself off silently in exactly the region
  where the curve is least resolved.
Required change:
  State the branch explicitly: if no admissible nearest point exists for either compared arm, the
  target is UNDECIDABLE for that leg (or EXCLUDED_UNDERPOWERED with bracket widths recorded) —
  never interpolation-only. Add `nearest_admissible_B1`, `nearest_admissible_C2` and the realised
  `|x - tau|` values to the comparison artifact, and state what happens when the 6-bisection cap is
  exhausted before the 0.10 gap bound is met.

### Lens 2 minor issues

1. §10.2 cites the wrong leg: an uninformative C3 is said to disable S6 leg (iii), which is the
   C1/NULL-1 leg; the C3 leg is (ii). As written an uninformative C3 disables the leg it does not
   affect and leaves the C3 leg live.
2. S7 is vacuous. S5 says "On BOTH individuals" and S6 "For BOTH individuals", so S7 adds no
   condition and §20.9's "purely additive … Strictly harder" is false — it is exactly as hard.
   §20.7's one-individual row is unreachable.
3. §10.2's 1%-of-global-variance trigger is an unjustified round number applied to the MEDIAN
   across strata, so four of ten near-identity strata pass the check.
4. §16.5's 30/10/5 bands are asserted with no derivation and were evidently written without
   checking against S5.
5. §20.3 leg (a) is malformed against §16.2's own definition; §20.10 silently reads it as "> 1.0".
6. `posthoc_scope` omits §16.1-§16.6, §22.1's extended raw schema and §22.3's amended columns.
7. §12.1 asserts that matching realised retention "is the same thing as comparing them at matched
   kept-ALT count" — true per sample, false for the axes as defined.

### Lens 2 supporting record

Missing controls: a positive control for the sweep itself (nothing distinguishes "no mechanism"
from "no power at these counts"); a control on the replicate dimension.

Missing metrics: per-replicate realised retention and kept-ALT counts at every grid point; the
minimum-replicate kept-ALT count; the MARGIN of each S6 leg as a number rather than a boolean;
`|x - tau|` and realised bracket width; the number of bisections actually performed.

Untested assumptions: linear interpolation of `zlo_min` adequacy; monotone realised retention for
C2's top-k rule under the seeded tie-break; that C3's permutation moves score_B1 at all; that 200
draws resolve a 95th percentile stably enough to be a decision boundary across ~336 comparisons.

---

## Lens 3 — STATISTICAL VALIDITY AT THESE COUNTS

Verdict: **REVISE**

> "The deciding leg — B1 versus C2 at matched retention — is explicitly declared to carry 'no
> uncertainty of its own' and is given no null, while the difference it adjudicates has a null sd
> of roughly 2 z-units at these read counts; S5's leg (b) is decided at about 0.03 of one standard
> error and its precision guard is applied to the wrong blank set; the pseudo-replication excuse
> carried over from v1.0 §24 item 3 stops holding the moment arms are compared at matched
> retention; and the whole criterion is an intersection of hundreds of zero-tolerance inequalities
> with no power analysis."

### MAJ-1 (lens 3)
Section: §15.5.8 ("The null the comparison is tested against"), §20.4 S6 leg (i), §17
Issue:
  The deciding leg of the deciding criterion has no null and no interval. §15.5.8 states
  "`B1 > C2` at matched retention is a contrast between two deterministic curves; it carries no
  uncertainty of its own." That is false — Z is deterministic in the arm's integer read counts,
  but those counts are random. Simulation under the null that the two arms are statistically
  identical (HCC1395-like counts: 42 scorable ALT per 0.1% replicate, 22 per blank, V2,
  t95(df=2)=4.3027) gives an sd of the difference in `zlo_min` of 1.98 z-units at tau=0.30
  (central 90% [-3.25, +3.28]) and 2.22 at tau=0.10; COLO829-like counts give 2.01-2.28. Against
  that, the whole observed advantage at the locked operating point is `delta_vs_C2` = 2.37 (V1) /
  3.68 (V2) on HCC1395 and 0.53 / 1.03 on COLO829.
Why blocking:
  §20.7 converts a single failure of leg (i) at any evaluable target into "MECHANISM REFUTED BY
  THE DENSITY CONTROL", and a win by 0.01 z-units at every target into "MECHANISM ESTABLISHED".
  Both conclusions are drawn from a difference whose null sd is about 2 z-units, with no band.
Required change:
  Specify a paired null for leg (i) and evaluate leg (i) against it, not against zero: resample
  the gate-passing candidates (and, independently, the blank replicate assignment) with
  replacement, recompute both arms' `zlo_min` on the same resample at the same matched tau, and
  take the distribution of the paired difference. Then (a) leg (i) HOLDS only if B1 exceeds the
  upper limit of C2's interval; (b) a difference inside the band routes to UNDECIDABLE, never
  REFUTED; (c) add `delta_lo`, `delta_hi` and `null_sd` columns.

### MAJ-2 (lens 3)
Section: §16.5, §20.3 S5 leg (b), §20.10
Issue:
  Two faults. (i) FACTUAL: §16.5's worked example uses the three primary blanks, but
  `retention_ratio` is built on all FIVE TF0 replicates — HCC1395 `retention_blank` = 0.363463 =
  mean(10/25, 8/22, 8/20, 8/21, 6/22) and COLO829 = 0.092428 = mean(2/33, 0/20, 4/30, 3/31, 6/35).
  So 1.6741 rests on 40 kept blank reads and 2.9127 on 15, not 26 and 6; under §16.5's own bands
  that licenses 4 significant figures on HCC1395 — precisely the reporting QC-04 rejected.
  (ii) STRUCTURAL: significant figures are not an uncertainty statement. A log-scale delta-method
  interval gives sd(log ratio) ≈ 0.20 on HCC1395 and ≈ 0.30 on COLO829, while leg (b) adjudicates
  gaps of 0.59% and 0.30% — about 0.03 and 0.01 of one standard error.
Why blocking:
  S5 failing routes to "MECHANISM UNSUPPORTED", and the draft's proof of good faith rests on a
  0.03-sigma difference presented to five figures.
Required change:
  Replace the significant-figure floor with an interval. Attach a resampling or delta-method
  interval to `retention_ratio` for every arm including B1 and C2, with `n_blank_kept` and
  `n_level_kept`. Evaluate leg (b) as interval dominance and route overlap to UNDECIDABLE. State
  which TF0 set the ratio uses and make §16.5's and §20.10's worked examples agree with
  aggregate.py. Keep the significant-figure rule as a display convention only.

### MAJ-3 (lens 3)
Section: §20.4 S6, §20.7, §15.5.8
Issue:
  S6 is an intersection of on the order of 7 targets x 2 axes x 2 constructions x 2 individuals x
  3 legs x 2 estimators ≈ 336 zero-tolerance inequalities, with no power analysis anywhere.
  §15.5.8's "no multiplicity correction arises" is correct for the pass direction and silent about
  the failure direction, where every named outcome except the first lives. Taking the observed
  `delta_vs_C2` as the alternative and the null sd above, per-comparison pass probabilities are
  roughly 0.88 and 0.60. The design returns a non-success under the null and under a genuine
  modest effect alike, and §20.7 maps most non-successes to affirmative negative claims.
Why blocking:
  An experiment whose outcome is determined by its read counts rather than by the biology cannot
  support either verdict it names.
Required change:
  Compute and write into the protocol, before EXEC-002, the operating characteristics of S6 at
  these counts, per target, axis, construction and individual, under equivalence and under a
  stated alternative. Report both figures in §20 beside the criterion. Split §20.7's outcome map:
  REFUTED requires C2 (or the C1/C3 band) to beat B1 by more than the null band; a failure inside
  the band is MECHANISM UNDECIDABLE. If no alternative is detectable at these counts, say so and
  do not run EXEC-002 as the deciding experiment.

### MAJ-4 (lens 3)
Section: §15.5.4 AXIS-L, §15.5.1, §15.5.6 floor (b), §20.3 reason 3
Issue:
  On AXIS-L under V2 the deciding statistic collapses algebraically to the arm's three blank
  counts: the denominator is arm-independent, V2 sets `sample_sd = sqrt(mean_blank)`, so
  `lo = [G - mb - t95*sd_b/sqrt(3)] / sqrt(mb)` with G matched is a function of the blank triple
  alone. Those triples are 2/0/4 (B1) and 0/1/0 (C2) on COLO829 and 10/8/8 and 1/1/1 on HCC1395.
  §15.5.6's floor admits targets at mean kept_ALT over TF0 rep1-3 >= 1, where
  `sqrt(mean_blank) = 1` and `z = G - 1`. EXEC-001 already shows the pathology: COLO829 C2 under
  V2 at 0.1% rep3 returns `z_lo = +9.0627` and `detected` from 7 kept ALT reads against a blank
  mean of 0.333 reads, and C1 is credited with detecting 1% under V2 on HCC1395 and under both
  constructions on COLO829.
Why blocking:
  The criterion installed to escape QC-02's count-scale artefact reintroduces it through the blank
  leg.
Required change:
  State the algebraic reduction in §15.5.4. Raise floor (b) to a count at which
  `sqrt(mean_blank)` is a usable scale estimate and justify the number. Report per target whether
  leg (i) is decided by G or by the blank triple, and mark AXIS-L x V2 targets as
  non-discriminating where G is matched to within the count granularity.

### MAJ-5 (lens 3)
Section: §24 item 3 carried over from v1.0, §15.5.8, §17
Issue:
  The sentence that licensed v1.0 to ignore the pseudo-replication ("the interval is therefore
  optimistic — equally, for every arm") does not transfer. In v1.1 the half-width is
  `t95*sd_b/sqrt(3)/sample_sd` and BOTH `sd_b` and `sample_sd` are arm-specific; at matched
  retention the arms differ precisely in their blank counts. EV-0036 gives between-library sd
  89.08 against the five pseudo-blanks' 7.64, an 11.7-fold understatement; EV-0045 adds that the
  three TF0 replicates share ~90% of their normal reads on HCC1395 and ~45% on COLO829. Inflating
  `sd_b` by that factor on HCC1395 B1 V1 turns half = 0.63 into about 7.4 and `lo = +2.2995` into
  roughly -4.5.
Why blocking:
  S5, S6 and S7 are cross-arm claims built entirely on an interval known to be about an order of
  magnitude too narrow, in a construction where the narrowness no longer cancels.
Required change:
  Add a required sensitivity analysis: recompute every S6 leg with the blank spread inflated by
  the EV-0036 factor and at intermediate factors, and report whether each leg's ORDERING survives.
  Amend the carried-over §24 item 3 to state that "equally, for every arm" does not hold for
  retention-matched cross-arm comparison. If no leg survives the inflation, S6 may not be reported
  as establishing a mechanism.

### MAJ-6 (lens 3)
Section: §15.5.5, §15.5.4, §22.2 schema
Issue:
  The arms are matched on a mean and judged on a minimum, and the minima are not even taken from
  the same replicate across arms — HCC1395 B1 V1's `zlo_min = +2.2995` comes from rep1 while
  C2 V1's -0.073 comes from rep2 — so v1.0 §17's "paired difference" language, carried over
  verbatim and binding, describes a quantity that is not paired. v1.0 §17 further requires the
  effect size to be reported with the three per-replicate paired differences; §22.2's schema
  carries no per-replicate columns at all.
Why blocking:
  The matching the redesign rests on does not apply to the statistic the verdict is read from, and
  the artifact that carries the verdict removes the evidence that would show the mismatch.
Required change:
  Either match per replicate or report both aggregations at every target. Add `lo_B1_rep1..3`,
  `lo_C2_rep1..3`, the three per-replicate paired differences, and `argmin_replicate` per arm.

### MAJ-7 (lens 3)
Section: §15.5.8 NULL-1 / NULL-2, §20.4 S6 legs (ii) and (iii), §17
Issue:
  Four defects in the permutation machinery. (a) Thresholding B1 against the 95th percentile of
  200 draws IS a one-sided permutation test at alpha = 0.05; calling the exceedance fraction
  "descriptive" changes the label, not the device, and leaves §17's carried-over record
  `statistical_tests.tsv … method NONE` false. (b) Tie handling is undefined; with small integer
  counts P(tie) is not negligible and a tie FAILS under the strict ">". (c) Undefined draws are
  unhandled: `aggregate.py` already drops NA draws silently, so the band is conditioned on the
  blank being non-empty — EXEC-001's HCC1395 C1 V1 `zlo_min_p05` = -6.0491 with
  `retention_ratio_p05` = 0.0. (d) B = 200 gives a 95th percentile resting on the 190th/191st
  order statistics.
Why blocking:
  Legs (ii) and (iii) carry the pattern-versus-composition claim and their threshold is undefined
  at ties, silently conditioned, and resolved to about a tenth of the band width.
Required change:
  Name the device a one-sided permutation test with alpha and B stated, in §15.5.8 and in
  `statistical_tests.tsv`. Raise B to at least 2000. Define tie handling with ties routing to
  UNDECIDABLE. Define the rule for undefined draws, report `n_draws_undefined` per grid point, and
  declare the band inadmissible above a stated undefined fraction. Report the Monte Carlo error.

### MAJ-8 (lens 3)
Section: §15.5.6 floor (b), §16.5, §15.5.7 steps 2-4, §15.5.5 vs §15.5.6(c)
Issue:
  Incompatible evidential standards applied to the same counts, then interpolated across.
  (a) §16.5 forbids reporting a RATIO backed by fewer than 5 kept blank reads while §15.5.6(b)
  admits a target for a VERDICT-carrying z comparison at mean kept_ALT >= 1. (b) When the three
  blank counts coincide `sd_b = 0`, half = 0, and `lo` jumps to z discontinuously — EXEC-001
  already contains an instance (HCC1395 TF0 rep1 C1 V1, `blank_sd = 0.0`, `z_lo = z_hi = 0.0`);
  simulation gives P(sd = 0) of about 2% at tau = 0.3 and 5% at tau = 0.1 per arm per cell, and
  across ~112 blank triples several such jumps are near certain. (c) Step 2 interpolates Z
  linearly across exactly these jumps. (d) Step 3's inadmissible branch is undefined. (e) §15.5.5
  says an undefined Z is "a failure to demonstrate … never a pass" while §15.5.6(c) makes the same
  condition EXCLUDED_UNDERPOWERED — opposite verdicts, no precedence.
Why blocking:
  Each decides S6 legs by machinery rather than by evidence, and the draft's strictest outcomes
  hang on them.
Required change:
  Set one count floor at least as strict as §16.5's and apply it to both. Add `blank_sd` and a
  `zero_spread_blank` flag, and treat a zero-spread blank triple as UNDECIDABLE. Forbid
  interpolation of Z across any interval in which the blank triple or any per-replicate kept count
  changes. Write the rule for an inadmissible nearest-point estimate. Resolve §15.5.5 against
  §15.5.6(c) in one direction in the protocol text.

### Lens 3 minor issues

1. §15.5.4's AXIS-B blank set (TF0 rep1-3) differs from §16.2's `retention_ratio` blank set (all
   five TF0 replicates, as `aggregate.py` computes it); S5 and S6 are anchored on different blank
   sets and the draft never says so.
2. §10.2's C3-informativeness diagnostic is the wrong statistic: what determines whether the
   permutation can move the kept set is the number of ALT reads in strata that straddle `cut`, not
   within-stratum variance.
3. §15.5.5 does not state whether a draw is matched to tau on its OWN retention curve or on the
   median curve; the two give materially different 95th percentiles.
4. §16.3 puts "verdict per replicate" in the outputs but no criterion consults it, so a MECHANISM
   ESTABLISHED verdict may rest entirely on UNRELIABLE cells — at the locked operating point
   HCC1395 B1 V1 is UNRELIABLE / UNRELIABLE / detected and its headline `zlo_min = +2.2995` comes
   from an UNRELIABLE replicate.
5. §1's `posthoc_scope` omits §16.1, §16.5 and §16.6.
6. §20.3's "evaluated on the counts as an inequality" does not say which counts or which
   inequality.
7. §23.1's cost model budgets 200 draws x 17 grid points, but §15.5.2's adaptive refinement makes
   the point count draw-dependent for a stochastic arm.
8. §21 F9 fires on a bare point comparison of the same two numbers criticised in MAJ-2.
9. §16.5's bands are a display convention, not a resolution; "2 significant figures" renders both
   1.6741 and 1.6839 as 1.7 with no stated rule for evaluating the leg.

### Lens 3 supporting record

Missing controls: a positive control for the S6 machinery; a null-versus-null calibration
(C1 vs C3, or C2 vs a second independent C2 draw) through the entire S6 rule; a paired resampling
null for leg (i); a blank-spread sensitivity arm at the EV-0036 factor; an arm-order / label-swap
check on the sweep implementation.

Missing metrics: an interval on `retention_ratio` for B1 and C2; an interval or null sd on
`delta_interp`/`delta_near`; per-replicate lower bounds and the three paired differences;
`blank_sd`, `n_blank_kept` and a zero-spread indicator; `n_draws_undefined` per grid point; the
ALT-read count in cut-straddling strata; a pre-execution power figure for S6; the Monte Carlo
error of the 95th percentile at B = 200.

---

## Lens 4 — EXECUTABILITY AND COST HONESTY

Verdict: **REVISE**

> "It cannot be executed exactly as written. Four things are underspecified in ways that change
> the numbers rather than the prose … and two of the protocol's own guard rails are broken: the
> V-a/F11 reproduction check is vacuous against the new machinery and collides with §16.5, and V-c
> asserts a convergence that is false by construction and unattainable. On top of that the
> `region` label that decides ESTABLISHED versus UNDECIDABLE has no definition anywhere."

### X1
Section: §15.5.2 (grid P), §15.5.3 (targets T), §15.5.7 step 1
Issue:
  The percentile grid P = {99.5 … 5} is not guaranteed to reach the target retentions
  T = {0.10 … 0.70}, and no behaviour is defined for a target that no grid point brackets. The
  refinement rule inserts midpoints and can never extend P beyond 99.5 or below 5. B1's realised
  ALT retention at 0.1% is already 0.4889 / 0.7143 / 0.6222 on HCC1395 while keeping
  `K_B1/n_scorable = 2895/58879 = 4.92%` of scorable reads. §15.5.6 covers count failure but not
  unreachability.
Why blocking:
  If the aggressive targets are unreachable for B1, the executor must invent an extension rule or
  silently drop them, leaving S6 decided only on the high-retention end that §20.4 itself concedes
  degenerates into S1's B0 leg.
Required change:
  Add a grid-extension rule fixed before EXEC-002: extend P by a stated mechanical schedule until
  each arm's realised R brackets min(T) and max(T) on both axes, or until the arm's attainable
  range is provably exhausted. Add a named per-target outcome TARGET_UNREACHABLE(arm) with the
  attainable `[R_min, R_max]` recorded; never a pass, counting against the 3-target rule.

### X2
Section: §15.5.2 (refinement), §15.5.7 steps 2-4
Issue:
  Realised retention is a step function with large atoms, so the bisection rule has no termination
  guarantee and linear interpolation can span a genuine discontinuity. From EXEC-001's raw files:
  COLO829_TF0_rep1 has `cut = 0.100000` with `K_B1 = 3020`, while rep2 has `cut = 0.096774` with
  `K_B1 = 3821` at essentially identical `n_scorable` (76,594 vs 76,583) — a cut difference of
  0.0032 moving ~800 reads, because `score_b1 = d/t` is a discrete rational multiset with heavy
  atoms (the observed cuts are literally 1/10, 1/13, 3/31). Bisecting the percentile cannot place
  a cut inside an atom.
Why blocking:
  S6's verdict would rest on an interpolation across a jump — a value corresponding to no cutoff
  any arm can operate at.
Required change:
  Sweep the attainable operating points, not the percentile: enumerate the distinct realised
  `(cut, kept-ALT)` states per arm and sample and report R at each. State (i) GAP_UNRESOLVED
  returns the target UNDECIDABLE; (ii) a target with no nearest point within 0.05 is UNDECIDABLE
  rather than decided on the interpolant alone; (iii) a maximum bracket width beyond which
  interpolation is forbidden outright.

### X3
Section: §23.2 "Concurrency and determinism"
Issue:
  The determinism specification is factually wrong about C1 and incomplete about C3. §23.2 states
  "C1's draw seeds `20260831 + j` are unchanged." The code that produced EXEC-001 does not do
  that: `aggregate.py:101-106` computes
  `seed = int(hashlib.sha256(f'20260831|C1|{ind}|{j}'.encode()).hexdigest()[:12], 16)`, creates
  one `np.random.default_rng(seed)` per (individual, draw) and advances it over the individual's
  samples in a fixed key order; `execution/random_seeds.yaml` records exactly this and is not in
  §1's `created_from`. C3's seed is given only as "20260919 + j hashed with the sample id" — no
  hash function, input format, digest width or sample ordering. Nothing requires one permutation
  per (draw, sample) reused at every grid point.
Why blocking:
  C1's `zlo_min` is the median over draws and feeds S1's preregistered control leg, S6 leg (iii)
  and F8's band. Any change in seeding or RNG consumption order changes those numbers, so F11
  fires on a correct run — or the executor "fixes" the mismatch by copying EXEC-001's values and
  the sweep's C1 band is then unverified.
Required change:
  Quote the as-executed derivations verbatim in §23.2 for C2's tie-break and C1's generator, give
  C3 the same explicit form, and mandate that for each (draw, sample) exactly one permutation is
  drawn and reused at every grid point so the PCT=95 slice is bit-identical to EXEC-001. Add
  `execution/random_seeds.yaml` to §1 `created_from`.

### X4
Section: §22.1 extended raw schema
Issue:
  `score_b1[] float, 6 decimal places` is a lossy encoding of a rational `d/t` whose own order
  statistics define `cut`, under the strict keep rule `score_b1 > cut`; two distinct scores that
  round to the same 6-dp value become tied and a tie at the cut is dropped. §22.1 specifies no
  precision at all for `cut_b1_grid`, while EXEC-001 stores `cut` as full float64
  (0.07692307692307693).
Why blocking:
  Every sweep number, including the PCT = 95 reproduction that F11 makes the licence for the run,
  is derived from these two quantities, and a silent one-read difference in a kept set of 8-28 ALT
  reads moves z materially.
Required change:
  Store the score exactly: add `score_b1_num[] int` (the disagreement count `d`) and define
  `score_b1 = score_b1_num / score_c2` exactly, or require float64 with repr round-trip. State
  that `cut_b1_grid` values are the exact stored score values the percentile rule selects, and
  require the executor to assert that reconstructing PCT = 95 reproduces `K_B1` and `k_C2` exactly.

### X5
Section: §15.5.7 V-a, §21 F11
Issue:
  The reproduction check called the licence for the re-run does not test the new machinery. Under
  §22.1 "everything else in the raw schema is unchanged", so the PCT = 95 kept sets are still
  produced by the same unmodified code path and reproducing those values is automatic. The check
  that would test the sweep — rebuild the PCT = 95 kept sets from `score_b1[]`/`c2_order[]` and
  require per-candidate equality — is required nowhere. Separately, F11's "and every other
  ablation row" collides with §16.5, which forbids reporting COLO829's ratio as a ratio at all.
Why blocking:
  A sweep whose reconstruction logic is wrong at every PCT passes V-a and F11 and then produces
  the S6 curves the mechanism verdict rests on; and the F11/§16.5 collision means a correct run
  can be declared an implementation fault.
Required change:
  Rewrite V-a as a reconstruction identity with zero mismatches per gate-passing candidate before
  any curve is read, retaining the aggregate equality as a weaker second check. Name in F11 the
  exact columns compared and at what precision, and exempt the §16.5-floored ratio columns
  explicitly.

### X6
Section: §20.4 (region column), §20.7, §22.2
Issue:
  The classification that gates whether a verdict is issued at all is never defined. A grep finds
  `region` only at lines 802-805, 1061, 1170, 1192 and 1257, never with a rule.
Why blocking:
  The executor would have to invent the rule that decides between "MECHANISM ESTABLISHED" and
  "MECHANISM UNDECIDABLE", after seeing the curves — the exact post-hoc freedom §20.8 forbids.
Required change:
  Fix a numeric classification in the protocol before EXEC-002, written into §15.5 or §20.4 with
  its constant, and listed in §20.8 clause 3 among the things that cannot be changed afterwards.

### X7
Section: §15.5.7 V-c
Issue:
  V-c requires every arm's curve to converge on B0's `zlo_min` as R -> 1 and calls divergence an
  implementation fault. Two problems. (i) B0's G is every ALT read on a gate-passing candidate
  while any filtered arm at R = 1 keeps only the SCORABLE ALT reads — the content of deviation D3;
  B0's literal retention is 1.19-1.67, so B0's G is 19-67% larger than scorable_ALT. (ii) R = 1 is
  not attainable: B1/C1/C3 use the strict rule `score > cut`, so every read at the minimum score
  is always dropped, and C2 would need PCT = 0, which is not in P.
Why blocking:
  An executor applying V-c literally returns a correct execution as faulty; one who does not must
  reinterpret a validation the protocol calls mandatory, leaving the high-retention end
  unvalidated.
Required change:
  Restate V-c against a defined `B0_scorable` anchor (G = scorable ALT reads on gate-passing
  candidates, `retention_scorable_only = 1.0` by construction), state each arm's attainable
  maximum explicitly, and check convergence there rather than at an unreachable R = 1.

### Lens 4 minor issues

1. Output paths contradict: §22.2 lists new artifacts under `results/` while §22.4 requires
   `execution_v1_1/` and `results_v1_1/` "or an equivalently distinct location".
2. §14's leakage requirement needs scoping: EXEC-002's aggregation must open EXEC-001's raw JSON
   and `results/ablation_results.tsv` to run V-a/F11, so the guarantee is unsatisfiable as written
   unless the capture is declared per-worker and those reads declared non-leaking.
3. §23.1 omits the determinism re-run pass that §23.2 and the §26 checklist require (~16 min).
4. §10.1 step 2's stratum boundary rule is ambiguous ("nearest" to a percentile of a tied integer),
   with no minimum stratum size; coarse strata make C3 behave like C1, loosening leg (ii).
5. §15.5.6 leg (a) collides with §20.4's own strictness argument: at HCC1395's scorable_ALT of
   45/35/45, tau = 0.10 yields 3.5-4.5 reads and is auto-excluded — the exact target §20.4
   advertises as where B1 can lose.
6. `retention_sweep.tsv`'s declared key is per-grid-point but its columns mix per-level and
   per-individual quantities.
7. §1 `created_from` omits `execution/random_seeds.yaml`.
8. Neither §22.1 nor §26 states that the sweep's Z must come from the checksummed
   `mrdz.score.z_interval` rather than a reimplementation.
9. "Negligible against /big8_disk's free space" is asserted, not measured; measured now, /big8_disk
   is 94% full with 1.7 TB free, so ~40 MB is indeed negligible — carry the figure.
10. §15.5.2's refinement trigger does not say which level/axis drives it, nor, for C1 and C3,
    whether the gap is evaluated on the median curve or per draw.

### Lens 4 supporting record

Verified correct: the feasibility claim (run_sample.py:82-92 computes and discards the scores;
raw rows carry only counts and indices); the index-space claim (`scorable = sorted(score_b1)`);
the `c2_order` trick (`keep_c2 = set(order[:k_c2])`); the storage estimate (~1.3 MB/sample on top
of 0.47-0.50 MB, ~40 MB total against 1.7 TB free); the runtime figures against
`execution_log.md`; EXEC-001 preserved and v1.1 a new file; the extended schema sample-internal so
QC-07's leakage guarantee survives.

Missing metrics: a per-sample reconstruction-identity mismatch count; the attainable
realised-retention range per arm per sample per axis; the number of DISTINCT attainable cut values
and k values; the realised bracket width beside every interpolated `Z_hat`; a measured aggregation
runtime; the realised on-disk size of the extended raw JSON.

Missing controls: an independent-implementation check on the sweep reconstruction; a
`B0_scorable` anchor arm.

---

## Lens 5 — PRE-REGISTRATION HYGIENE AND CLAIM CONTROL

Verdict: **REVISE**

> "The draft's post hoc discipline is real and in places exemplary … It fails this lens on six
> specific points, all fixable without weakening anything."

### M1 (lens 5)
Section: §20.6 (l.835) and §20.7 first branch (l.845-847), against §1 `v1_0_relationship` (l.104-105)
Issue:
  The draft invents a POSITIVE outcome stronger than anything v1.0 registered and reaches it
  entirely through post hoc criteria. §20.6: "H1 is SUPPORTED IN FULL only if S1, S2, S3 hold
  (they do) AND S5, S6, S7 all hold." §20.7 branch 1: "-> H1 SUPPORTED, MECHANISM ESTABLISHED
  (post hoc)." This contradicts the draft's own §1 field — "v1.1 adds post hoc criteria that may
  QUALIFY or WITHDRAW … It cannot strengthen it" — and qc_001.md constraint 2.
Why blocking:
  A criterion written after the confounding measurement was seen cannot establish a mechanism.
  Left as written, the benchmark can publish "SUPPORTED IN FULL" and "MECHANISM ESTABLISHED" — a
  conclusion strictly above its preregistered ceiling — with the post hoc tag reduced to a
  parenthesis that will not survive being quoted.
Required change:
  Rename branch 1 to a non-establishing label, e.g. "MECHANISM NOT WITHDRAWN — post hoc, NOT
  ESTABLISHED", and delete "SUPPORTED IN FULL". Add a binding clause to §20.6: no v1.1 outcome may
  raise the project's claim above what v1.0 registered; the maximum positive result is that the
  claim survived two post hoc tests and requires a preregistered replication. Name that follow-up
  preregistration as a required output of branch 1.

### M2 (lens 5)
Section: §20.3 S5 leg (b)/(c) escape clause (l.742-744) colliding with §16.5 (l.561-576) and §20.10 (l.936-938)
Issue:
  "Where the floor forbids a ratio, leg (b) and leg (c) are evaluated on the counts as an
  inequality and the evaluation is flagged `LOW_COUNT`." No inequality is defined — not the
  statistic, not the direction test, not the tie rule. On COLO829 this is the ONLY case that
  arises. On HCC1395 §16.5 permits only 2 significant figures, at which both ratios are 1.7, yet
  §20.10 adjudicates leg (b) as "FAILS (by -0.0098)".
Why blocking:
  This is AGENTS.md rule 3 in its purest form: the decision rule for a post hoc criterion is left
  to be chosen after the counts are seen, at exactly the two cells where the verdict is decided.
  Either polarity is available to a later evaluator.
Required change:
  (1) State that S5's comparison arithmetic is performed at full stored precision and that §16.5
  governs REPORTING only — or, if the floor is to bind the decision, say so and accept the
  consequence. (2) Define the LOW_COUNT inequality now, numerically and in advance, with a rule
  that a leg which cannot clear the margin returns UNDECIDABLE routed to a non-success.
  (3) Justify §16.5's 30/10/5 boundaries from a stated principle independent of the observed blank
  totals, and label §16.5 POST HOC in §1 `posthoc_scope`.

### M3 (lens 5)
Section: §20.7 branch list (l.849-874), read against §20.3, §20.5 (l.814-818) and §20.10 (l.934-938)
Issue:
  The branches are conditionally nested but not mutually exclusive, and no precedence rule is
  given. On the data §20.10 predicts, TWO branches fire at once ("S5 fails -> MECHANISM
  UNSUPPORTED" and "S5 or S6 holds on one individual only -> MECHANISM NOT REPLICATED") and the
  reporter picks. Because branches 3, 4 and 5 are gated on "S5 holds", the strongest named
  outcomes — "MECHANISM REFUTED BY THE DENSITY CONTROL" and "REFUTED BY THE PERMUTATION CONTROL" —
  become UNREACHABLE on the very data path the draft predicts.
Why blocking:
  REFUTED is structurally masked, and "NOT REPLICATED" — which reads to any reader as "it worked on
  one individual" — is available as an alternative label for a criterion that failed.
Required change:
  Add an explicit precedence rule: every applicable branch label must be computed and reported, not
  one chosen; when several apply, the most severe governs the headline
  (REFUTED > UNSUPPORTED > NOT REPLICATED > UNDECIDABLE). De-nest S6's legs from S5 so its
  refutation labels are reachable independently. Add a `branch_labels_applicable` column. Reprint
  v1.0 §20's named-outcome block inside §20, which the draft currently drops.

### M4 (lens 5)
Section: Header banner (l.5-8), §1 `posthoc_scope` (l.119-120), §15.5.8 (l.492), §24 item 14 (l.1162)
Issue:
  Three different, mutually inconsistent registers of what is post hoc. The banner says only S5,
  S6, S7; §1 says [S5, S6, S7, C3, F9, F10, F11, §15.5]; §24 item 14 says "S5, S6, S7, C3 and
  §15.5", silently dropping F9-F11 — and F9 alone can fire MECHANISM UNSUPPORTED. Several post hoc
  decision constants are labelled nowhere: §10.2's 1% trigger, §15.5.6's floors (5 / 1 / 3),
  §15.5.7's 0.05 admissibility, §15.5.2's 0.10 refinement gap, and all of §16.4-§16.6.
  §15.5.8 describes the S6 decision device as "a preregistered-in-this-document consistency rule".
Why blocking:
  Constraint (b) requires the post hoc label to be PERMANENT and to travel with the criteria. A
  label complete only in one YAML field will not survive one round of summarisation.
Required change:
  Create one canonical post hoc register (e.g. §1.1) listing every post hoc criterion, control,
  failure criterion, reporting rule and numeric constant with its date, and make the banner, §20
  and §24 item 14 cite that one list. Replace "preregistered-in-this-document" with "pre-specified
  in this post hoc protocol before EXEC-002 runs, and NOT preregistered with respect to the
  EXEC-001 result". Extend the `posthoc` column requirement to every row derived from any listed
  item.

### M5 (lens 5)
Section: §10.1 (l.183-185) against §18.1 (l.631-639)
Issue:
  §10.1 asserts as protocol text that `B1 > C3` "can be produced only by the methylation pattern
  on the individual read". That is false as stated and the draft contradicts it 450 lines later:
  C3 does NOT preserve the association between score_B1 and other read-level covariates (read
  length, basecall quality, error rate, local coverage, allele-specific germline methylation), and
  §18.1's "because C3 preserves all of them" is wrong for read length for the same reason.
Why blocking:
  The "only" sentence is the entire warrant for §20.7 branch 1's mechanism outcome. It is also an
  AGENTS.md rule 8 violation: an interpretation, and an overreaching one, asserted inside normative
  protocol text.
Required change:
  Delete the sentence and replace it with the enumerated exclusion set actually earned:
  "B1 > C3 excludes CpG density (at stratum resolution), filter aggressiveness and counting
  statistics as explanations; it does not exclude other read-level properties correlated with
  score_B1 within a stratum, which this design does not control." Correct §18.1 to drop "read
  length". Bind §20.7's positive branch wording to the corrected exclusion set.

### M6 (lens 5)
Section: §20.0 (l.681-683), §22.2 (l.1043), §26 checklist (l.1231)
Issue:
  `results/registered_outcome_v1_1.txt` "MUST open with the §20.0 v1.0 block, verbatim and
  unedited". That block's last line is `REGISTERED_OUTCOME: H1 SUPPORTED`. The v1.1 verdict is
  written below it with no specified delimiter, no distinct key and no ordering rule.
Why blocking:
  Constraint (b) is satisfied in letter and defeated in practice: the file's first machine-readable
  verdict line reads `REGISTERED_OUTCOME: H1 SUPPORTED`, in a file whose actual finding may be that
  the mechanism half is withdrawn.
Required change:
  Specify the layout normatively: line 1 is the v1.1 verdict under distinct keys (`V1_1_OUTCOME:`,
  `MECHANISM_VERDICT:`, `POSTHOC: POST_HOC_2026-09-19`); the v1.0 block follows inside explicit
  `--- BEGIN V1.0 PREREGISTERED OUTCOME (EXEC-001, PRESERVED VERBATIM) ---` / `--- END ---`
  fences; the withdrawal sentence appears above the fence. Apply the same fencing wherever §20.6
  requires the v1.0 block beside a verdict.

### Lens 5 minor issues

1. §20.6 l.835 writes "S1, S2, S3 hold (they do)", pre-granting EXEC-002's reproduction inside the
   verdict rule; it should read "(held in EXEC-001; EXEC-002 must reproduce them or F11 fires)".
2. §20.10 states S5 leg (b) fails on HCC1395 but never states the verdict §20.7 assigns to that
   fact: MECHANISM UNSUPPORTED, hence withdrawal. Say it, so the expected outcome is on the record
   before EXEC-002 runs.
3. §20.7's withdrawal clause names no artifact. Name `orchestration/research_state.yaml`, the FIND
   ids and `workflow_state.yaml` as required updates.
4. §15.5.7 item 3's inadmissible nearest-point branch is uncovered; the permissive reading will be
   taken.
5. The protocol's own prose quotes four-figure ratios that §16.5 forbids; add a one-line carve-out
   stating these are verbatim quotations retained for audit.
6. §20.5 S7's trigger does not cover mixed leg-level splits.
7. §16.4's mandatory detection table is EXEC-001's; require EXEC-002's own table beside it, with
   any difference treated under F11.

### Lens 5 supporting record

QC-03 recorded as well bound: §16.4 forbids the unqualified sentence, mandates the verbatim
four-cell table in every artifact and summary, and §24 item 11 repeats it; withdrawal of the
mechanism half is named in advance in §20.7 and is genuinely reachable — indeed near-certain, since
S5 leg (b) fails on HCC1395 on numbers verified in `results/ablation_results.tsv` and F11 forces
EXEC-002 to reproduce them.

---

## Consolidated major-issue index (round 1)

```text
Lens 1  MAJ-01  C3 exclusivity overclaim; per-read error-rate confound unexcluded
        MAJ-02  C2 has no uncertainty band; one-read seed-determined margins
        MAJ-03  sig-fig floor vs four-figure adjudication; unnamed blank set; undefined LOW_COUNT
        MAJ-04  mean-matched retention vs min-over-replicates statistic
        MAJ-05  0.05 tolerance re-admits count mismatch; interpolation of a step function
        MAJ-06  two readings of the stochastic-arm percentile
        MAJ-07  region label undefined but verdict-bearing

Lens 2  M1      S5 leg (a) is S4 clause (i) only; S4 dropped from the conjunction
        M2      S5 determined in advance by F11; S6's outcomes unreachable and unnamed
        M3      no defined comparison rule at any permitted precision
        M4      region undefined; S6 does not exclude degenerate targets in either direction
        M5      mean-matched / min-statistic; floor admits empty replicates -> false refutation
        M6      undefined inadmissible-nearest-point branch

Lens 3  MAJ-1   leg (i) has no null and no interval (null sd ~2 z-units)
        MAJ-2   sig figs are not uncertainty; §16.5 applied to the wrong blank set
        MAJ-3   ~336 zero-tolerance inequalities, no power analysis
        MAJ-4   AXIS-L x V2 collapses to the blank triple
        MAJ-5   v1.0 §24 item 3's "equally, for every arm" does not transfer
        MAJ-6   matched on mean, judged on min; per-replicate evidence dropped from the schema
        MAJ-7   permutation test mislabelled; ties, undefined draws, B = 200
        MAJ-8   incompatible standards, zero-spread blanks, interpolation across steps,
                §15.5.5 vs §15.5.6(c) contradiction

Lens 4  X1      percentile grid may not reach the targets
        X2      retention is a step function with heavy atoms; bisection cannot terminate
        X3      determinism spec factually wrong about C1, silent on C3 and RNG order
        X4      6-dp score storage is lossy under a strict `>` rule
        X5      V-a vacuous where it matters; F11 collides with §16.5
        X6      region undefined
        X7      V-c false by construction and unattainable

Lens 5  M1      invented a positive outcome above the preregistered ceiling
        M2      escape clause colliding with §16.5 and §20.10; §16.5 bands unjustified/unlabelled
        M3      branches not mutually exclusive; REFUTED structurally masked
        M4      three inconsistent post hoc registers
        M5      exclusivity asserted in normative text (AGENTS.md rule 8)
        M6      outcome file opens with `REGISTERED_OUTCOME: H1 SUPPORTED`
```

---

## The single objection most likely to be raised

> "You installed C3 to exclude the confound QC-01 found, and then asserted that excluding one
> confound excludes all of them. B1 retains 40% of scorable ALT reads in a blank with no tumour in
> it, against a 4.91% global keep rate, and the cutoff is exactly 1/13 — one discordant call keeps
> a low-CpG read. That is a noise filter, and C3 cannot see it."

Round 1 has no answer in the draft. Lens 1 named the fix (a pattern-blind read-property comparator
arm entering S5 and S6 as a further necessary leg); lens 5 independently required the exclusivity
sentence deleted.

---

Routing: return to `benchmark-designer`. Panel verdict NOT ACCEPTED (5 REVISE, 0 REJECT,
34 major issues); the ACCEPT rule requires zero of each.
