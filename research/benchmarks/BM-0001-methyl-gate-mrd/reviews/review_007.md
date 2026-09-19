# Benchmark Review — Panel

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v1.1_draft.md` (v1.1, DRAFT — design iteration 7)
Reviewer role: five-lens adversarial panel (grill-me), post-QC redesign review
Review iteration: 7
Review round: 2 of 3
Date: 2026-09-19

No panel member edited the protocol and no panel member executed any part of the benchmark.
`protocols/v1.0_locked.md` and the whole of `EXEC-001` were opened read-only and are unchanged.

This file is a transcription of the round-2 panel record. It performs no analysis of its own.

---

## Panel composition

The same five lenses as round 1, run against the iteration-7 draft:

```text
Lens 1  MECHANISM DISCRIMINATION
Lens 2  STRICTNESS
Lens 3  STATISTICAL VALIDITY AT THESE COUNTS
Lens 4  EXECUTABILITY AND COST HONESTY
Lens 5  PRE-REGISTRATION HYGIENE AND CLAIM CONTROL
```

---

## Verdict rule

```text
ACCEPT  only if  zero REVISE  AND  zero REJECT  AND  zero major issues
```

---

## Verdict

NOT ACCEPTED — REVISE

```text
Lens 1  mechanism discrimination      REVISE    5 major  (MAJ-L1-01 .. MAJ-L1-05)
Lens 2  strictness                    REVISE    4 major  (MAJ-L2-01 .. MAJ-L2-04)
Lens 3  statistical validity          REVISE    6 major  (SV-01 .. SV-06)
Lens 4  executability / cost          REVISE    5 major  (X-01 .. X-05)
Lens 5  pre-registration hygiene      REVISE    5 major  (PH-01 .. PH-05)
                                      -------------------
                                      5 REVISE, 0 REJECT, 0 ACCEPT, 25 major issues
```

Major-issue count fell from 34 to 25. No lens returned REJECT.

---

## What the designer recorded as resolved at this iteration

The iteration-7 handoff claimed resolution of all 34 round-1 major issues plus the round-1 minor
issues. The panel accepted most of those resolutions; the ones that survived, wholly or in a new
form, are recorded as round-2 major issues below. Notable round-1 items the panel confirmed
resolved:

```text
MAJ-01 (r1)  C3 exclusivity sentence DELETED; §18.1 "read length" claim struck;
             C4a/C4b arms added; S6 leg (iv); §16.7 diagnostics; F12
MAJ-02 (r1)  C2 given a 200-seed tie-break band with j = 0 = EXEC-001's seed
MAJ-05 (r1)  count ladder replaces the percentile grid; integer count matching;
             interpolation FORBIDDEN outright
MAJ-07 (r1)  §15.5.11 numeric region rule, frozen by §20.8 clause 3
M1     (r1, lens 2)  S5 leg (a) is now v1.0's S4 verbatim, both clauses; S4 restored to §20.6
X3     (r1)  §23.2 quotes the as-executed seed derivations verbatim
X4     (r1)  integer numerator/denominator stored; thresholds are ladder indices
M6     (r1, lens 5)  §22.5 normative layout; v1.0 block fenced
```

The panel also recorded one declared relaxation between drafts: S6's verdict-bearing rule moved
from the all-target intersection (iteration 6) to a pooled statistic (iteration 7), declared in
§20.9, justified by §15.5.9's operating characteristics, frozen by §20.8 clause 7, with the
intersection retained and reported as S6-STRICT. Four lenses recorded that this is a relaxation
between two POST HOC drafts and therefore does not breach qc_001.md rule 1, which governs v1.1
against v1.0.

---

## Standing checks, per lens

```text
                         strictly_harder_check                       post_hoc_labelling_check
Lens 1   PASS against v1.0, with one named exception             PASS
Lens 2   MIXED — PASS on every criterion's TEXT,
         FAIL on two of its PARAMETERS                           PASS with one omission
Lens 3   PASS on the criteria, two exceptions                    PASS
Lens 4   PASS, scoped                                            PASS
Lens 5   PASS in logical form, one open exception (M3/PH-03)     PASS with one gap
```

Round-2 summary of the two checks, transcribed:

- **Strictness.** Round 1's provable sideways move is closed: S5 leg (a) is v1.0's S4 verbatim,
  both clauses, and S4 is restored to §20.6's conjunction. Lens 2 found two NEW sideways moves,
  both through a PARAMETER rather than a criterion's text: C1's draw count raised 200 -> 2000
  changes the numeric input of preregistered S1, S4 clause (ii) and F8 (aggregate.py line 16 sets
  `N_DRAWS = 200` and lines 129-133 take `np.median` over those draws), and §15.5.10's sd-inflation
  factor is never pinned to f = 1 for the HOLDS decision while the inflation is structurally biased
  toward B1 under V2 at matched counts (0.782 z-units per unit f on HCC1395's operating-point
  triples; 9.15 at f = 11.7). Lens 2 also recorded the reverse failure as the dominant defect: the
  installed criterion's power is misreported.
- **Post hoc labelling.** Round 1's lens-5 FAIL is repaired: §1.1 is a single canonical register,
  the banner and §20/§24 cite it rather than restate it, §22.5 fences the v1.0 block so
  `REGISTERED_OUTCOME: H1 SUPPORTED` cannot be the first verdict line, §20.6 clause 0 forbids
  "SUPPORTED IN FULL" and "MECHANISM ESTABLISHED". All five lenses passed the check this round.
  Lens 2's omission: the C1 200 -> 2000 draw change is a post hoc change to a PREREGISTERED
  criterion's numeric input and is not in §1.1. Lens 3 recorded a provenance error, reported as
  SV-06 rather than as a labelling failure.

---

## Lens 1 — MECHANISM DISCRIMINATION

Verdict: **REVISE**

> "The single criterion that carries the mechanism claim against the confound QC-01's failure mode
> points to — S6 leg (iv) / S5 leg (d) / F12, the pattern-blind comparator set — is satisfied by
> the very confound §10.2 installs it to exclude. … That is QC-01 repeated one level down."

### MAJ-L1-01
Section: §10.2 (C4a, C4b), §10.1 licensing paragraph, §12.1, §16.7(c), §18.1, §20.3 leg (d),
§20.4 leg (iv), §21 F12, §24 item 16, U6
Issue:
  The pattern-blind comparator set omits exactly the read property that GENERATES score_b1.
  `score_b1 = d/t` is discordance against the population consensus, and §10.2 itself says it "is
  maximised by a noisy read as readily as by an aberrantly methylated one". The noise that inflates
  d/t is MODIFICATION-CALL noise — reads whose per-position ML probabilities sit near the 128/255
  decision boundary. Neither installed arm can see that: C4a is NM/alignment length (a different
  noise channel) and C4b is declared "invariant to every modification call ON the read". §12.1's
  "C4a and C4b isolate it" is false, and §10.1's "the two of those that this design can measure" is
  false as a matter of fact — read length is C4a's own denominator, mapping quality is already
  filtered at MIN_MQ = 20, local coverage is already stored per candidate, and per-read
  modification-call confidence is read by `ref_calls` and discarded. Related: §16.7(c) requires the
  Spearman correlation of score_b1 against the comparators and attaches NO consequence, so leg (iv)
  can HOLD in a sample where the correlation shows it tested nothing.
Why blocking:
  ADVERSARY: define `F(read)` = mean over the read's confident-consensus CpG positions of
  `1 - |2p/255 - 1|`, i.e. mean modification-call UNCERTAINTY. F is invariant under flipping any
  call to its confident opposite, so it carries ZERO methylation-pattern information, and it is
  correlated with d/t by construction. A filter using only F satisfies S4/S5(a), beats C2 (F is not
  density), beats C3 (the within-stratum permutation destroys the read-to-F correspondence as
  thoroughly as the read-to-pattern one — §10.1 concedes this), beats C4a and beats C4b trivially.
  F12 never fires, and the benchmark reaches L-I. The same construction runs on read length and
  mapping quality, and it is especially live because §6 states the mixtures are tumour subsampled
  into that individual's own matched normal — so any read property that discriminates library of
  origin produces both differential retention and a matched-count z advantage with no tumour
  biology.
Required change:
  (1) Add the missing pattern-blind arms, all computable in the same pass with no new file:
  C4c = per-read mean modification-call uncertainty (with the invariance proof stated in §10.2),
  C4d = read length, C4e = mapping quality. (2) Redefine S6 leg (iv) and S5 leg (d) as the max over
  the WHOLE declared pattern-blind set, and redefine F12 to fire on any member. (3) Delete §12.1's
  "C4a and C4b isolate it" and §10.1's "the two of those that this design can measure". (4) Store
  `query_alignment_length[]`, `mapq[]` and a per-read call-confidence summary. (5) Give §16.7(c) a
  consequence mirroring §10.5: below a constant fixed in §1.1, that comparator's leg returns
  UNDECIDABLE, never HOLDS. (6) Name the library-of-origin confound explicitly in §18.1 and §24.

### MAJ-L1-02
Section: §10.1 step 2 (density strata), §10.5, §20.4 leg (ii), §18.1
Issue:
  C3's strata are approximate DECILES of the scorable reads by `score_C2`, which is a per-read
  count of confident CpG positions and therefore scales with read length, so the upper strata span
  a wide range of t. Inside a stratum of heterogeneous t, keeping reads with `d/t > cut` is NOT
  density-neutral: at EXEC-001's HCC1395 cut of exactly 1/13, a read with `t <= 12` is kept on a
  SINGLE discordant call while a read with t = 40 needs `d >= 4` and t = 200 needs `d >= 16`. B1
  therefore systematically prefers LOW-t reads within the stratum, purely from the arithmetic.
  §10.1 step 2c records the within-stratum MIN and MAX of score_C2 and attaches no criterion.
Why blocking:
  A filter that knows only t and keeps low-t reads reproduces B1's within-stratum keep pattern and
  satisfies leg (ii). §20.4 leg (ii) is the criterion whose purpose is "pattern beyond density",
  and §20.7 L-D is the outcome that fires when it fails. §10.5's only guard is a POWER trigger, not
  a VALIDITY one.
Required change:
  Stratify on the EXACT integer value of `score_C2`, merging only adjacent t values and only below
  a read count fixed in §1.1, recording every merge. Add a VALIDITY trigger: where a realised
  stratum's `score_C2` MAX/MIN exceeds a constant fixed in §1.1, or where its t range straddles
  `1/cut`, leg (ii) returns UNDECIDABLE at that target — never HELD and never a refutation. State
  in §18.1 that B1 > C3 excludes CpG density only at the realised stratum resolution, and report
  that resolution numerically.

### MAJ-L1-03
Section: §15.5.4 (AXIS-L and AXIS-B matching rules), §15.5.2 (ladder definition), §10.3
Issue:
  "At the same retention" does not have one meaning, because the protocol never defines how a
  threshold chosen in one sample transfers to the other samples that enter the same z computation.
  §15.5.4 says "at the nominal threshold rule of g(A, r)"; §15.5.2 defines the ladder point as an
  INDEX into that sample's own sorted score array, and index i is meaningless in a blank with a
  different `n_scorable`. §15.5.2's own worked example shows the transfer is not a detail: COLO829
  TF0 rep1 `cut = 0.100000` with `K_B1 = 3020` against rep2 `cut = 0.0967741935483871` with
  `K_B1 = 3821` at essentially identical `n_scorable` — "a cut difference of 0.0032 moving about
  800 reads". At least four inequivalent transfers exist (same percentile, same global keep
  fraction, same cut VALUE, same ladder index) and the protocol picks none. AXIS-B is worse: a
  single ladder point is asked to span three samples, and the mean of three integers need not be
  attainable.
Why blocking:
  On AXIS-L the kept ALT count at 0.1% is matched by construction, so every S6 leg (i), (ii) and
  (iv) outcome on that axis is decided by the arms' BLANK counts, produced by exactly this
  undefined transfer. Two executors obeying §15.5.4 to the letter can produce different verdicts.
  And the candidate transfers are not neutral between arms — transferring a cut VALUE is natural
  for the strict-`>` arms and impossible for C2 — so a mixed rule reintroduces QC-02's defect at
  the blank end.
Required change:
  Define the transfer normatively and identically for every arm, in the same count coordinates the
  rest of §15.5 uses; the construction consistent with the draft's own rejection of percentiles is
  to match on the GLOBAL KEPT-READ COUNT (keep fraction `K/n_scorable`). Record the realised
  per-sample threshold and keep fraction for both arms on every row, and add a validation asserting
  that the two arms' blank thresholds were derived by the same rule. Apply the same definition to
  AXIS-B and state how the mean-of-three target is attained.

### MAJ-L1-04
Section: §15.5.4 (algebraic reduction paragraph), §20.4 (BLANK_TRIPLE clause), §15.5.9 RESULT 1
Issue:
  The protocol disqualifies leg (i) from carrying a positive S6 result where the statistic has
  collapsed into the arm's blank triple, but confines that safeguard to ONE cell — AXIS-L under V2.
  The same reduction holds under V1 and the draft's own measurement proves it: §15.5.9 records
  `sample_sd/sqrt(G)` at 0.97 ± 0.02 across B1 and C2 rows, so with G matched by construction
  `sample_sd` is fixed to within 2% across arms and `lo` is, to within 2%, a function of the arm's
  three blank counts under V1 as well.
Why blocking:
  A positive S6 can rest entirely on AXIS-L x V1 cells whose statistic the protocol's own reasoning
  says adds nothing to the comparison QC-01 already ran and found to be a tie to within 0.6% / 0.3%.
  It is the only place in §15.5 where the safeguard is narrower than the draft's own measurement
  supports, and the asymmetry is in the permissive direction.
Required change:
  Apply the BLANK_TRIPLE determination symmetrically under BOTH constructions, by a rule fixed in
  §1.1 before EXEC-002 (e.g. mark a row BLANK_TRIPLE whenever the matched kept-ALT counts agree
  within tolerance AND the `sample_sd` values agree within a stated fraction, the 0.97 ± 0.02
  measurement giving the natural constant). Extend §20.4: if every DISCRIMINATING target carrying a
  positive leg-(i) result is BLANK_TRIPLE under EITHER construction, S6 returns UNDECIDABLE on that
  individual. If that leaves AXIS-L unable to carry a positive result, say so in §15.5.9 in advance.

### MAJ-L1-05
Section: §15.5.8 (a) NULL-0 paired candidate bootstrap; §15.5.8 (d) family-wise bar; §22.2
Issue:
  The null that decides every leg (i) and leg (iv) outcome is under-specified at the one point that
  determines its width. The resample draws gate-passing candidates with replacement, which changes
  `scorable_ALT(r)`, and `n_tau(r) = round(tau * scorable_ALT(r))` is defined FROM it — so "the
  SAME matched target" admits two readings: re-derive `n_tau` from the resample, or hold it at its
  observed value. `scorable_ALT` at 0.1% is 45/35/45 and 51/55/63, so a resample moves it by order
  10%, shifting `n_tau` by one to two reads, and §15.5.7 step 1 states that at kept counts of 5 to
  9 one read moves z by roughly 0.5 to 1.0 — against a measured `null_sd` of 0.83 to 3.1. The
  choice changes the interval width by a factor comparable to the effect being tested.
Why blocking:
  `delta_lo > 0` is the sole support rule for legs (i) and (iv), `delta_hi < 0` the sole failure
  rule, and the min-over-targets statistic built from the same resamples is the sole gate on every
  REFUTED and UNSUPPORTED label. An executor choosing the narrower reading can turn UNDECIDABLE
  into HOLDS or REFUTATION-ELIGIBLE on a leg whose point difference is a fraction of one null sd —
  the regime §15.5.8 itself measures on COLO829 (`delta_vs_C2` = 0.5255 under V1 against a null sd
  of 0.83).
Required change:
  State which quantity is held fixed across resamples and why; the conservative reading is to
  re-derive `n_tau` from each resample's own `scorable_ALT` so matching noise is inside the
  interval. Record per resample the realised `n_tau` and the realised inter-arm count difference.
  State whether the score distribution, ladder and cut are recomputed; what happens when a resample
  cannot attain the matched count within the one-read tolerance (excluded and counted, under the
  same 20% inadmissibility ceiling); and that `null_sd` is the bootstrap sd of the paired
  difference, not a null-model sd.

### Lens 1 minor issues

1. §20.3 subjects every S5 leg to §16.2's interval rule, but leg (a) has no comparator ratio — the
   rule is undefined for it as written.
2. §20.7 RULE 4 ("the PREREGISTERED rule controls") can convert a post hoc UNDECIDABLE on S5 leg
   (a) back into v1.0's point-comparison HELD; scope RULE 4 to the failure direction only.
3. `Z = min_r lo(r)`, so the paired difference is a difference of minima, not a paired statistic,
   and the two minima may come from different replicates; `argmin_replicate` is stored but no rule
   uses it.
4. §11 calls C4b a "per-read ambiguous-call fraction" while §10.2 says it is invariant to every
   modification call on the read — it is a property of the read's genomic FOOTPRINT. Rename it.
5. §10.5's C3 trigger is a power trigger only; the recorded stratum width should be promoted to a
   reported gating quantity.
6. §15.5.4's AXIS-B sets a mean of three integers equal to an integer target while the tolerance is
   stated in whole reads; attainability and tie-breaking for a mean are undefined.
7. §1.1's REPORTING RULES list omits §22.3 and §22.4; §22.3's heading "Amendments to v1.0 artifacts"
   reads as licensing edits that §22.4 forbids.
8. U6 concludes that no structurally exact twin of score_b1 is computable from a single premise
   that rules out one candidate twin only; the call-uncertainty twin is computable from the same tag.

---

## Lens 2 — STRICTNESS

Verdict: **REVISE**

> "The conjunctive architecture is sound … But the bar has moved sideways in two places, both
> through a PARAMETER rather than through a criterion's text. … Separately, on the reverse failure:
> this is the over-hard, not the over-easy, design — L-I is unreachable by arithmetic, and the
> operating characteristics the protocol prints describe a criterion it does not install."

### MAJ-L2-01
Section: §10.1 (line 532), §15.5.8 (b), §20.1, §20.2, §21 F8, §21 F11, §23.2, §26
Issue:
  C1's permutation draw count is raised from 200 to 2000, which silently re-parameterises the
  preregistered S1, S4 clause (ii) and F8, and deterministically contradicts F11. v1.1 quotes
  v1.0's S1 verbatim — "zlo_min(B1) > zlo_min(C1) [C1 = median over 200 draws]" — and v1.0's S4 —
  "C1's 5th and 95th percentiles across its 200 draws as the noise band" — then raises C1 to
  B = 2000 in §10.1, §15.5.8 (b), §23.2 and §26. `aggregate.py` line 16 sets `N_DRAWS = 200` and
  lines 129-133 derive C1's G, `sample_sd`, retention and blank triple as `np.median` over those
  draws. Nothing states which draw vector feeds S1's C1 term, S4 clause (ii)'s band or F8's band.
Why blocking:
  S1 is named on forbidden list (c). A configuration in which the 200-draw C1 median sits just
  above `zlo_min(B1)` (S1 FAILS under v1.0) and the 2000-draw median sits just below it (S1 PASSES
  under v1.1) is admitted on identical data. It is also self-contradictory: F11 requires C1's
  columns to reproduce EXEC-001 exactly, and EXEC-001's C1 values ARE the 200-draw medians
  (`retention_ratio` 0.8566 on HCC1395, 1.1605 on COLO829), so a correct EXEC-002 computing C1 over
  2000 draws fires F11 and voids the whole run.
Required change:
  State normatively in §20.1, §20.2, §21 F8 and §23.2 that S1's C1 term, S4 clause (ii)'s band,
  F8's band and every F11-checked C1 column are computed from draws j = 0..199 only — the preserved
  aggregation, reproduced bit for bit — and that the 2000-draw vector is used solely for post hoc
  S5 leg (c), S6 leg (iii) and §15.5.8's nulls. Emit the two aggregations as distinctly named
  columns. Add the draw-count change to §1.1 as a post hoc modification of a preregistered
  criterion's input, and correct §20.9's "S1, S2, S3 unchanged, verbatim. Neither easier nor
  harder". Also fix the related F11 defect that `aggregate.py` returns C1's `alt_kept` as a median
  that need not be an integer while F11 demands integers.

### MAJ-L2-02
Section: §15.5.10, §20.4, §21 F14, §22.2 (`sd_inflation` column)
Issue:
  §15.5.10's blank-spread inflation factor is never pinned to f = 1 for the HOLDS decision, and the
  inflation is structurally biased in B1's favour, so it can license a pass rather than only
  disqualify one. F14 names only one direction (HOLDS at f = 1, reverses at f = 11.7); the
  complement is unspecified and the unspecified reading is permissive. Writing
  `lo(A) = z(A) - f*t95(2)*sd_b(A)/sqrt(3)/sample_sd(A)`, the paired difference is
  `D = [z(B1) - z(comp)] - f*[h(B1) - h(comp)]`. On HCC1395's operating-point blank triples
  (B1 10/8/8, C2 0/1/1) under V2, `h(B1) = 0.974` and `h(C2) = 1.757`, so D gains 0.782 z-units per
  unit f and 9.15 at f = 11.7, entirely in B1's favour. This is structural: S6's hypothesis is that
  B1 retains MORE blank ALT reads, so B1 necessarily has the larger `mean_blank`, hence the larger
  V2 `sample_sd`, hence the smaller half-width, hence the larger gain from inflation.
Why blocking:
  Inflating `sd_b` re-parameterises the preregistered variance constructions, which forbidden list
  (c) names explicitly; it is safe only if it can strictly remove passes, and here it cannot be. A
  leg UNDECIDABLE or FAILING under the preregistered V2 can be reported as HOLDING at an inflated
  `sd_b`, and F14 — sold as a rule that "can only disqualify a leg" — is close to vacuous under V2
  in the cell §15.5.4 identifies as decisive.
Required change:
  State in §20.4 and §15.5.10 that every S6 leg outcome that can contribute to a HOLD is read at
  f = 1 and only f = 1, that a leg not HOLDING at f = 1 can never HOLD at any other factor, and
  that f in {2, 4, 11.7} rows are disqualifying-only. Add the F14 clause: a leg holding only under
  inflation is INFLATION-ONLY and may not contribute to a positive S6. Correct §15.5.10's framing
  with the per-unit-f algebra and state that F14's test is weak in that cell.

### MAJ-L2-03
Section: §15.5.9 (model block and RESULT 3), §20.5, §24 item 18
Issue:
  §15.5.9's operating characteristics are computed for a criterion the protocol does not install,
  and the resulting power figure is nevertheless made mandatory reporting. The model block states
  "AXIS-L only; AXIS-B is not simulated" and every table is leg (i) only, while §20.4's S6 requires
  four legs to HOLD in EVERY cell — 4 legs x 2 axes x 2 constructions x 2 individuals = 32 cell-leg
  conjunctions — and applies §15.5.11's region filter, which §15.5.9 does not. §24 item 18 and
  §20.5 then state "the probability of a positive S6 + S7 under a 1.5x alternative is of order
  0.06", which is RESULT 3's per-cell pooled power squared for two individuals: one leg, one axis,
  one construction.
Why blocking:
  The protocol MANDATES printing that 0.06 beside any NOT REPLICATED outcome and rests §20.7's
  UNDECIDABLE routing and §24 item 18's "EXEC-002 remains worth running" on it. The installed
  16-fold-per-individual conjunction has a holding probability orders of magnitude below the quoted
  figure. The benchmark is required to report an interpretive conclusion its own design cannot
  support.
Required change:
  Extend `protocols/support/s6_operating_characteristics.py` to simulate the criterion §20.4
  installs — all four legs, both axes, both constructions, with the region filter applied — and
  print P(S6 HOLDS) per individual and P(S6 + S7). Replace every "of order 0.06" with the figure
  for the installed rule, or label it unambiguously as "leg (i), AXIS-L, pooled, both individuals".
  Where AXIS-B and legs (ii)-(iv) cannot be simulated, state that the power of S6 as installed is
  UNKNOWN AND LOWER.

### MAJ-L2-04
Section: §16.2 decision rule, §20.3, §20.6, §20.7 (L-H, L-I, WITHDRAWAL), §20.10, §24 item 18
Issue:
  The only positive branch, L-I, is unreachable by arithmetic, while §20.7 converts every other
  outcome — including UNDECIDABLE — into an affirmative withdrawal that propagates to the project's
  evidence base. F11 freezes `retention_ratio` to EXEC-001's values; on HCC1395 under the
  five-blank convention those are B1 1.6741 and C2 1.6839, and §16.2's rule is
  `retention_ratio_lo(B1) > retention_ratio_hi(comparator)`, so
  `lo(B1) <= point(B1) < point(C2) <= hi(C2)`. S5 leg (b) cannot hold, S5 cannot hold, S7 cannot
  hold, L-I cannot be reached. §20.3 and §20.10 say as much but hedge with "likely" and neither
  states that the positive branch is closed.
Why blocking:
  Two conclusions the design cannot support. First, the withdrawal and its propagation are
  determined by EXEC-001's preserved numbers before EXEC-002 runs; presenting it as the outcome of a
  retention sweep attributes to EXEC-002 a conclusion it did not produce. Second, it contradicts
  §24 item 18 and §15.5.9 point 5, which forbid a negative mechanism claim from a failure to clear a
  bar the design cannot clear — and an UNDECIDABLE propagating as a withdrawal is exactly that.
Required change:
  State as a finding of the DESIGN (not of EXEC-002) that L-I is unreachable given F11, that the
  mechanism half is therefore withdrawn on the strength of EXEC-001 plus qc_001.md, and that
  EXEC-002's purpose is limited to determining WHICH non-success label applies. Split the withdrawal
  rule in two: WITHDRAWN-ON-EVIDENCE for labels backed by a family-wise-eligible refutation or a
  determined S5 failure, and WITHDRAWN-AS-UNDECIDABLE for L-H, the latter propagating as "not
  established by this benchmark, and not shown false". Loosening S5 or §16.2 is the forbidden
  direction and is explicitly NOT the required change.

### Lens 2 minor issues

1. §20.3 subjects all of S5's legs to interval dominance including leg (a), which §20.10 then
   evaluates as a point comparison; §20.6's S4 conjunct must be pinned to v1.0's point rule.
2. §16.2's dominance rule is written only for the B1-versus-comparator form; leg (a) compares a
   ratio against 1.0 and "dominates" is undefined there.
3. F9 has been made materially weaker than its iteration-6 point form; §20.9 declares the S6
   recalibration and should declare this weakening of a failure criterion too.
4. §15.5.4's AXIS-L rule never defines what transfers across samples (cut value, percentile or
   ladder index) — the same defect lens 1 raises as MAJ-L1-03.
5. §15.5.11's DEGENERATE_HIGH rule removes the lowest-contrast targets from a POOLED MEAN, which
   mechanically raises the pooled statistic, while §15.5.9 simulates without the region filter — so
   the tabulated size of 0.05 is not the size of the installed rule.
6. `aggregate.py` returns C1's `alt_kept` as a median that need not be an integer while F11 requires
   integers; F11 will trip on C1 rows on an otherwise correct run.
7. S6-STRICT is computed and printed but §20.7 attaches no branch to it; §20.4 should say plainly
   that it is a diagnostic with zero verdict weight.

---

## Lens 3 — STATISTICAL VALIDITY AT THESE COUNTS

Verdict: **REVISE**

> "The architecture is right and should survive … But the statistics that would carry the new
> criteria are not specified at the counts this benchmark has."

### SV-01
Section: §15.5.8 (d) FAMILY-WISE CONTROL IN THE REFUTATION DIRECTION (lines 1172-1180); consumed by
§20.4, §20.7 L-C/L-D/L-E/L-F, §21 F12
Issue:
  A bootstrap resampling distribution is used as if it were a null distribution, so the refutation
  bar is not a test of anything. The bootstrap of (a) resamples the OBSERVED data; its distribution
  is centred on the observed effect, not on zero, and it is never recentred anywhere in §15.5.8.
  With `M_obs = min_t D/null_sd` and `M*` the bootstrap min, `M*` is centred near `M_obs`, so
  `q05(M*) ≈ M_obs - 1.645*se(M)`, BELOW `M_obs`. The target attaining the observed minimum has
  `D/null_sd = M_obs` exactly, so the condition "observed < q05(M*)" is failed by construction at
  the one target with the best chance of satisfying it, and a fortiori at every other target.
Why blocking:
  REFUTATION-ELIGIBLE is the sole gate on every refutation label the protocol names — L-C, L-D,
  L-E, L-F and F12 — and §20.7 RULE 3 puts REFUTED at the top of the precedence ladder. If the gate
  cannot fire, every S6 failure, including C2 or C4a beating B1 outright at matched count (the exact
  outcome QC-02 asked the sweep to look for) falls through to L-H MECHANISM UNDECIDABLE. The
  benchmark's strongest negative outcome is structurally unreachable.
Required change:
  Replace the bootstrap-as-null with an actual null. Either (i) centre it — build the family-wise
  reference from `D* - D_obs` (or studentised `(D* - D_obs)/null_sd*`) and declare
  REFUTATION-ELIGIBLE when the observed min falls below the 5th percentile of the centred min; or
  (ii) use a within-sample randomisation null that exchanges the two arms' kept-set labels at
  matched count. Either way §15.5.9 must add a RESULT block reporting the refutation rule's size
  under exact equivalence and its power against the 1.5x and 2x alternatives.

### SV-02
Section: §15.5.8 (a) and (d); §20.4 THE VERDICT-BEARING RULE; §22.2 column list
Issue:
  `null_sd` is never defined anywhere in the document, yet it is the denominator of the statistic
  that decides S6. It appears at exactly four places and at none of them is it given an estimator.
  Three readings are all admissible: (a) the sd of `D*` across the 2000 resamples on the observed
  data, held fixed; (b) the same recomputed inside each resample (studentised); (c) §15.5.9's
  simulated `null_sd` imported as a constant. These are not interchangeable: `null_sd` is a
  per-target weight in a weighted mean across targets whose `null_sd` values in §15.5.9's own table
  range from 0.83 to 3.10 — a 3.7-fold spread — so the choice can flip the sign of the pooled mean.
Why blocking:
  §20.8 clause 3 freezes the matching rule, the count floors, the tolerance, B, alpha and the
  undefined-draw ceiling, and does not freeze `null_sd`, because it was never written down. The one
  quantity the mechanism verdict is divided by is left to the executor to invent after the curves
  exist, and S6 becomes non-reproducible.
Required change:
  Define `null_sd` normatively in §15.5.8, name which reading applies, and add it to §1.1 and to
  §20.8 clause 3. The self-consistent choice is studentisation inside the resample with the
  observed-data sd used for the reported point statistic; if reading (a) is chosen, say so and state
  that the interval is first-order only. Relabel §15.5.9's simulated column so it cannot be mistaken
  for the executor's estimator, and make §22.2 say which estimator fills it.

### SV-03
Section: §15.5.8 (a); §16.2; §22.2 column list
Issue:
  The bootstrap has no undefined-resample rule, no admissibility ceiling and no reporting column,
  although the counts guarantee that a large fraction of resamples is undefined. §15.5.8 (c) imposes
  exactly such a rule on the permutation bands and criticises `aggregate.py` for dropping NA draws
  silently; no counterpart exists for the 2000 bootstrap resamples. Under the three-blank convention
  C2's denominator is HCC1395 0/25, 1/22, 1/20 — two kept blank reads — and COLO829 0/33, 1/20, 0/30
  — ONE kept blank read. `n_gate_pass` in COLO829 TF0 rep2 is 22, so the single carrying candidate is
  absent from `(21/22)^22 = 36%` of resamples, giving `retention_blank = 0` and an undefined ratio;
  on HCC1395 the two carrying candidates are both absent from 13%. Nor does the protocol say whether
  the DISCRIMINATING evaluable target set is held fixed or recomputed per resample.
Why blocking:
  S5 leg (b) and F9 are decided by interval dominance on exactly these intervals. An interval
  computed from the 64% of resamples in which the denominator survived is conditional on a
  non-random event correlated with the quantity being estimated.
Required change:
  Extend §15.5.8 (c)'s machinery to the bootstrap: define what makes a resample undefined; report
  `n_boot_undefined` and `n_boot_floored`; apply the same 20% ceiling above which the interval is
  INADMISSIBLE and the comparison returns UNDECIDABLE; and state that the DISCRIMINATING evaluable
  target set is fixed on the observed data across resamples. On these numbers COLO829's three-blank
  C2 interval is INADMISSIBLE in advance and §20.3 should say so.

### SV-04
Section: §15.5.8 (a) decision rule; §15.5.9 MODEL and RESULT 1/RESULT 3; §15.5.5
Issue:
  The decision statistic is a difference of two min-over-replicates functionals, the percentile
  bootstrap is not reliable for a min under near-ties, and near-ties are present: COLO829 C2 under
  V1 has per-replicate `lo` = 0.1684 / 0.1676 / 2.0485, an 0.0008 z-unit gap between the two
  candidate argmins, so the argmin switches between resamples and the bootstrap distribution is a
  mixture. Second, §15.5.9's decision proxy is "HOLDS iff D > 1.645*null_sd" whereas §15.5.8 (a)
  decides on the EMPIRICAL 5th percentile of `D*`; for a min-of-min functional at kept counts of 5
  to 9 these differ materially. Third, §15.5.8 (a) asserts without support that the rule is
  "strictly harder than the point comparison it replaces, in BOTH directions" — a percentile
  bootstrap that is too narrow is EASIER in the support direction.
Why blocking:
  §20.9 and §20.8 clause 7 justify choosing the pooled rule over S6-STRICT entirely by RESULT 3's
  power figures. If the simulation models a rule the protocol does not apply, those figures are not
  the design's operating characteristics, and the one place iteration 7 made a criterion easier
  rests on numbers that do not describe it.
Required change:
  (1) Simulate the ACTUAL rule — per-replicate counts, `min_r lo(r)` for both arms, the
  2000-resample percentile bootstrap inside each simulation replicate — and report realised size and
  power for the empirical-percentile rule. (2) Report, as a required column and an admissibility
  condition, the fraction of resamples in which `argmin_replicate` differs from the observed argmin;
  above a stated fraction the target returns UNDECIDABLE. (3) Delete or prove the "strictly harder
  in BOTH directions" sentence; the honest alternative is to decide the leg on the three
  per-replicate paired differences the schema already stores.

### SV-05
Section: §15.5.8 (a); §15.5.9 MODEL bullets 2 and 5; §15.5.10; §24 item 18 and §15.5.9 point 6
Issue:
  The pseudo-replication is carried into the statistic but not into the resampling distribution, and
  the size claim that justifies the whole run is computed under the independence model the draft
  itself refutes. §15.5.10 quotes EV-0036 (between-library sd 89.08 against the pseudo-blanks' 7.64,
  an 11.7-fold understatement) and EV-0045 (~90% / ~45% read sharing, "effective replicate count
  nearer one than three"), but (i) §15.5.8 (a) resamples candidates WITHIN each sample, which cannot
  generate between-library variance; (ii) §15.5.9's model draws three independent blank replicates;
  (iii) §15.5.10's inflation is applied inside the statistic but §15.5.9's size and power table is
  never recomputed at f > 1. §15.5.9 point 6 and §24 item 18 nonetheless justify EXEC-002 on "the
  size is controlled at 0.05 in both directions".
Why blocking:
  The size of the HOLD rule is the single load-bearing number in the protocol and it is asserted at
  0.05 on a model that contradicts §15.5.10 and §24 item 17 of the same document.
Required change:
  Recompute RESULT 1 and RESULT 3 under a correlated-blank model — an explicit shared-read
  correlation calibrated to EV-0045, or the conservative substitution of an effective blank count of
  1 — and print both the f = 1 and f = 11.7 tables with the realised size in each. If the size is
  materially above 0.05, either add a between-library variance component to the resampling scheme or
  scope every interval explicitly as conditional on this blank library and remove the 0.05 claim.

### SV-06
Section: §16.5 carve-out for quotation; the numbers it licenses in §16.2, §20.3 and §20.10
Issue:
  The document quotes five significant figures on one and two kept blank reads and licenses it with
  a provenance claim that is false. §16.5's carve-out says the four-figure ratios in §0, §12.1,
  §16.2, §20.2, §20.3 and §20.10 "are verbatim quotations of qc_001.md's measurements and of
  results/ablation_results.tsv". The three-blank numbers 1.5687 / 1.9955 and 4.1644 / 3.7338 are in
  neither source: `retention_ratio_3blank` is a v1.1 quantity introduced by §16.2, and
  `results/ablation_results.tsv` has no such column. They are new designer computations, reproducible
  from `per_sample_metrics.tsv`: HCC1395 C2 three-blank = 1.9955 on 0+1+1 = 2 kept blank reads;
  COLO829 C2 three-blank = 3.7338 on 0+1+0 = ONE kept blank read. §16.2 then uses those numbers to
  make a quantitative design argument binding S5.
Why blocking:
  QC-04 is the finding this section exists to bind, and its complaint is precisely that four
  significant figures overstate what three reads can support. The draft reproduces the fault at one
  read, inside the section that forbids it, under a carve-out whose stated provenance does not hold.
Required change:
  Correct the carve-out to state truthfully which numbers are EXEC-001 quotations and which are new
  v1.1 computations. Apply §16.5's own rule to the new ones: display the three-blank C2 quantities as
  raw counts, not as 1.9955 and 3.7338, in §16.2, §20.3 and §20.10. Re-derive §16.2's justification
  for requiring both blank conventions without reference to an "order of magnitude" disagreement
  measured on one read.

### Lens 3 minor issues

1. §20.10 adjudicates S5 leg (a) by a point comparison although §20.3 states every leg is decided by
   §16.2's interval rule; state which one §20.10 is answering.
2. §16.2 calls `sqrt(1/40 + 1/75) = 0.196` and `sqrt(1/15 + 1/46) = 0.297` a delta-method SE for the
   B1-versus-C2 gap, but those are B1's own single-arm SEs; the SE of the DIFFERENCE is 0.643 and
   0.716, so the observed gaps are 0.009 and 0.004 of one SE, not 0.030 and 0.010.
3. §15.5.6 clause (b) requires all three blank replicates non-empty, but §15.5.4's AXIS-L induces a
   DIFFERENT threshold per 0.1% replicate and therefore three blank triples per arm; which triple the
   floor applies to is unstated. At COLO829's 2/0/4 this decides evaluability.
4. §16.3 requires the per-replicate verdict tally beside any S6 claim but no criterion consults it; a
   positive S6 resting entirely on UNRELIABLE cells is admissible as written.
5. §15.5.9's printed table omits rows; §20.8 clause 7 freezes the choice on these characteristics, so
   print all 28 cells or state that the frozen basis is the script plus its recorded seed.
6. §10.6 folds the C2 tie-break seed into the bootstrap by drawing a seed index per resample, so the
   interval describes a seed-averaged comparator while the point value, F11 and §20.10's one-read
   argument all concern j = 0; report the seed-only and bootstrap-only components separately.
7. §22.2 lists band-side admissibility columns but no bootstrap-side counterparts.

---

## Lens 4 — EXECUTABILITY AND COST HONESTY

Verdict: **REVISE**

> "Most of this draft is executable, and on the single strongest check available to my lens it
> passes: it requires the re-run to reproduce EXEC-001 exactly … But it cannot be executed exactly
> as written, for one blunt reason and four specification reasons."

### X-01
Section: §2-9, §22.1, §23.1 (whole section), §1 `created_from`, §26
Issue:
  The inputs EXEC-002 re-runs on do not exist. All 28 dilution BAMs named in
  `execution/inputs_manifest.tsv` and in every `execution/raw/*.json` `bam` field are absent from
  disk (0 of 29 raw-recorded BAM paths resolve;
  `/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-3_25x/` now holds `.cram` + `.crai` +
  `.cram.meta.json` and no `.bam`). `research/evidence/EV-0052.yaml`, created 2026-09-19 in this
  repository, records a lossless conversion to CRAM on 2026-09-12 and states that
  `run_sample.py` line 40 is `pysam.AlignmentFile(bam_path, 'rb')` — BAM mode, no
  `reference_filename` — while CRAM requires mode `'rc'` and the reference. The draft contains no
  occurrence of CRAM, reference, EV-0052 or `inputs_manifest`, and §2-9 states normatively "The
  BAMs, paths, levels, replicates and roles are identical. Nothing in §6 changes."
Why blocking:
  EXEC-002 aborts on the first of its 28 passes. Worse, an executor taking §2-9 at face value has no
  instruction covering the format change, so it gets resolved at the keyboard. The re-cost is not
  cosmetic: the 941-1,180 s/pass figures were measured decoding 82 GB BAMs; the replacements are
  43 GB reference-compressed CRAMs whose pileup over ~4,000 discrete positions requires container
  decode against a reference.
Required change:
  Add an input section naming the actual inputs: the 28 CRAM paths, their `.crai`, the decode
  reference `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` with md5
  `a6da8681616c05eb542f1d91606a7b2f`, and the pysam open as mode `'rc'` with `reference_filename`.
  Record the open-mode change as a deviation with `Methodology changed: NO`. Add EV-0052 and
  `execution/inputs_manifest.tsv` to §1 `created_from`. Delete or correct the §2-9 sentence. Add an
  input-availability precheck as the first §26 item. Re-cost §23.1 against CRAM decode, measuring
  one pass first or stating explicitly that the per-pass figure is an unverified lower bound. Add an
  F11 branch for the case where reproduction fails because the input format changed rather than the
  sweep code.

### X-02
Section: §14 (PER-WORKER CAPTURE block), §10.2 (C4a), §11, §26
Issue:
  The per-worker leakage guarantee cannot be satisfied by the run this protocol requires. §14 states
  that across the 28 workers no path may appear that is absent from EXEC-001's per-worker set; under
  the actual inputs each worker must open a `.cram`, its `.crai` and the reference FASTA — three
  path classes absent from that set — so §26's per-worker check fails by construction. A second
  route to the same collision: §10.2 says that where the NM tag is absent the executor computes the
  mismatch count from `get_aligned_pairs(matches_only=True, with_seq=True)`, which requires an MD tag
  and raises otherwise; the only way out is to open the reference, which §14 forbids. The draft never
  establishes that NM or MD is present on these reads, and the CRAM conversion EV-0052 records was
  run with `store_md=1 store_nm=1`, so what a worker sees is a product of the conversion.
Why blocking:
  QC-07 is the one leakage finding verified by evidence rather than declaration. If the stated
  expectation cannot be met, the executor either declares a deviation against the one guard that
  should never take one, or silently widens the expected set, destroying the audit value of
  `files_opened.txt`.
Required change:
  Rewrite §14's per-worker expectation to enumerate the paths the run actually opens, and state
  explicitly why the reference is non-leaking in QC-07's own four named classes. Add a precheck that
  samples reads from each input and records NM/MD presence with counts; make NM_SPARSE fire off that
  measured number; and state what happens if both tags are absent (C4a is not computed and every
  C4a leg returns UNDECIDABLE — not that the executor reaches for the reference).

### X-03
Section: §15.5.4 (AXIS-L and AXIS-B), §15.5.2, §15.5.7 step 3
Issue:
  "At that same nominal rule" is undefined across samples, and it is the quantity that decides the
  cell the draft itself identifies as reducing to the blank triple. The ladder is defined per arm per
  sample with LADDER INDEX i into that sample's own sorted score array, and `n_scorable_reads`
  differs sample to sample — 58,879 / 58,957 / 58,872 at HCC1395 0.1% against blanks
  58,990 / 59,041 / 58,972, and 76,709 / 76,904 / 77,039 against 76,594 / 76,583 / 76,926 on
  COLO829. "The same nominal rule" admits at least three readings — same ladder index, same
  `pct_equivalent` re-derived, same cut VALUE — and §22.1 rules out the percentile but does not
  choose between the other two, while §22.2 emits both `ladder_index_B1` and `pct_equiv_B1` without
  saying which transfers. AXIS-B is worse: a single "canonical ladder point" is asked to span three
  samples and the mean of three integers need not be attainable.
Why blocking:
  §15.5.4 states its own consequence — on AXIS-L with G matched and V2's
  `sample_sd = sqrt(mean_blank)`, `lo(r)` is a function of the arm's three blank counts alone. Those
  counts are 10/8/8 against 1/1/1 and 2/0/4 against 0/1/0, where one read moves `lo` by roughly 0.5
  to 1.0 z-units by the draft's own arithmetic. S6 leg (i) in that cell, and the §15.5.6 floor test,
  are decided by an implementation choice the protocol does not make.
Required change:
  Choose one transfer rule normatively for both axes and say so; the cut-value rule is consistent
  with §22.1's exactness argument. State that the other readings are forbidden, make the comparison
  artifact record the realised blank counts under it, extend the canonical-ladder-point definition to
  the cross-sample case AXIS-B needs, and say what happens when no point realises the target mean.

### X-04
Section: §15.5.8 (a) NULL-0 PAIRED CANDIDATE BOOTSTRAP, and §16.2 INTERVAL
Issue:
  The paired candidate bootstrap does not say what is resampled and what is held fixed.
  `n_tau = round(tau * scorable_ALT(r))` and `scorable_ALT` is a sum over gate-passing candidates, so
  resampling candidates changes `n_tau`; "the SAME matched target" is ambiguous between holding the
  observed integer, re-deriving it, and holding the ladder index. The draft is also silent on whether
  the score arrays, cut and ladder are recomputed under a resample — they should not be, since a cut
  is an order statistic over 58,879-77,039 scorable reads which are not the candidate set, but
  nothing says so.
Why blocking:
  This bootstrap decides S6 leg (i), leg (iv) and F12, the family-wise refutation bar, and via
  §16.2 both S5 and F9. `n_gate_pass` is 22-36 in the blanks and 45-63 at 0.1%, so whether `n_tau` is
  re-derived or pinned is a first-order effect on `delta_lo` and `delta_hi`.
Required change:
  State normatively that the scorable-read set, score arrays, cut and ladder are FIXED across
  resamples and only the gate-passing candidate rows are drawn; which of the observed `n_tau` or a
  re-derived `n_tau*` is used, and that the other is forbidden; and that the same rule governs the
  `retention_ratio_lo/hi` construction §16.2 borrows. Add the chosen rule to §26.

### X-05
Section: §23 (mrdz import rule) against §15.5.10 and §21 F14
Issue:
  §23's import rule and §15.5.10's mandatory sd-inflation cannot both be obeyed. §23 forbids
  reimplementation, including a vectorised re-derivation, of every z, lo, hi, `blank_mean`,
  `blank_sd` and verdict; §15.5.10 requires every S6 leg recomputed with `sd_b` multiplied by each
  f in {1, 2, 4, 11.7}. The normative implementation `z_interval(sample_total, blank_totals,
  sample_sd)` derives sd internally via `blank_spread(blank_totals)` and exposes no inflation
  parameter — there is no call that returns `lo` at f != 1.
Why blocking:
  The executor must resolve a direct contradiction and the two natural resolutions are not
  equivalent: post-multiplying the half-width outside mrdz is exact but unauthorised, while rescaling
  `blank_totals` also moves `blank_mean` and therefore moves z itself. F14 turns on it, and a wrong
  inflation arithmetic can let a leg that should be SD-DEPENDENT contribute to a positive S6.
Required change:
  Write the inflation arithmetic explicitly in §15.5.10 as `lo_f = z - f*(z - lo)` and
  `hi_f = z + f*(hi - z)` over mrdz's own f = 1 outputs, and add one sentence to §23 carving this out
  as arithmetic on mrdz outputs rather than a reimplementation. State that rescaling `blank_totals`
  is forbidden, and why.

### Lens 4 minor issues

1. `c2_tie_rank[]` is justified as the array that lets the 200 tie-break seeds run in aggregation,
   but a read's rank within its j = 0 tie block does not determine its order under j != 0; say
   explicitly that the shuffle is over the stored index array.
2. `attainable_alt_counts` is listed as a sample-level key of the BAM pass, but C1 and C3 have a
   per-draw ladder and C2's attainable set depends on the seed; name which arms the key covers.
3. §22.4's read-only list omits `execution/scripts/`; §22.1 says "EXEC-002's run_sample.py must
   emit …" without naming a path. Name `execution_v1_1/scripts/`.
4. §22.1 and §23.1 both say "nine arrays"; the block lists eight.
5. §10.2 asserts `score_C4b` is invariant to every modification call on the read; the consensus is
   built from the calls of every read touched, including this one, so the invariance is approximate.
6. §15.5.9's support script uses `T95 = 4.302652729696142` while the normative implementation uses a
   truncated table (4.303); say that a fourth-decimal disagreement is not the finding.
7. NOT AN OBJECTION: the aggregation budget is sound and honest — `mrdz.score.z_interval` measured at
   1.45 microseconds per call on this host, so ~5.4 million calls are about 8 seconds, and 112,000
   numpy permutations of 59k-77k elements are minutes. Keep the "report the measured figure / record
   a deviation rather than reducing B" clause verbatim.
8. NOT AN OBJECTION: §22.1's disk claim checks out — /big8_disk reports 1.7 TB free of 27 TB, and
   eight arrays over 58,879-77,039 entries are ~3 MB/sample, ~90 MB across 28.

---

## Lens 5 — PRE-REGISTRATION HYGIENE AND CLAIM CONTROL

Verdict: **REVISE**

> "The design survives this lens; the labelling does not. Every finding is a claim-control or
> register defect, not a methodological one … But three of them are individually sufficient to let
> the benchmark publish a claim its own design cannot support."

### PH-01
Section: §20.0 ("v1.0 §20's named outcomes, reprinted in full")
Issue:
  The reprint of v1.0's named-outcome block is labelled "reprinted in full" and is abridged. Every
  dropped clause is the clause that says what the non-success MEANS, and three of the four are the
  ones that negate the mechanism. `v1.0_locked.md` lines 714-727 read "Named outcomes, which may not
  be relabelled:" / "S1 holds but S4 fails -> MECHANISM UNSUPPORTED. Not a success. The z-win is
  attributable to filter aggressiveness rather than to methylation selecting the tumour-derived
  reads." / "S1 holds on HCC1395 only -> NOT REPLICATED. Not a success. …" / "S1 fails against C1 ->
  REFUTED: the gain is filter aggressiveness, not methylation identifying reads." / "S1 fails against
  C2 -> REFUTED: the gain is CpG density, not methylation pattern." v1.1 §20.0 lines 1705-1708 render
  these as bare labels and drop the introducing injunction entirely.
Why blocking:
  Constraint (b) requires v1.0's preregistered outcome to be reported beside the new criteria IN
  FULL. A block that announces itself as full and is not is the exact failure the constraint exists
  to prevent, and it is the block a downstream reporter will copy rather than re-derive.
Required change:
  Replace §20.0's named-outcome block with `v1.0_locked.md` lines 714-728 byte-for-byte, including
  the introducing line and all four trailing clauses. Apply §22.5's fencing rule to it and forbid
  paraphrase, truncation or re-wrapping in any artifact. Add a §26 item requiring a byte comparison
  of both reprinted v1.0 blocks against their sources before EXEC-002 reports anything.

### PH-02
Section: §1.1 CANONICAL POST HOC REGISTER (with §1, §24 item 14 and the banner)
Issue:
  The register the banner, §20, §24 and every artifact are told to cite is not complete, and the
  omissions are the verdict apparatus: §20.6 clause 0, the whole of §20.7 (RULES 1-4 and labels
  L-A..L-J including the positive label L-I), §20.8 clauses 2/3/4/7, §20.9, §10.3, §12.1, §14's two
  new guards, §17's new comparison rows, §18.1, §22.3, §22.4, §23.2's new derivations, §24 items
  11-20, §25 U4-U6. A reader partitioning the document by §1's three statements gets an unregistered
  residue containing every rule deciding and naming a v1.1 verdict — and that residue is where the
  most preregistration-sounding sentences live (§20.8's "Anti-goalpost-moving clauses (binding)" and
  "FROZEN BEFORE EXECUTION, and part of the checksummed protocol").
Why blocking:
  The worst omission is §20.8 clause 7, which freezes the choice between S6 and S6-STRICT on
  §15.5.9's operating characteristics — a choice made from a model calibrated on EXEC-001's realised
  counts, and which §20.9 concedes is "EASIER to satisfy in the support direction". It is the most
  goalpost-sensitive decision in the document and it sits under a "frozen before execution" heading
  with no post hoc registration. Second: L-I, the only non-negative label, is produced by an
  unregistered rule.
Required change:
  (1) Add a seventh block to §1.1, VERDICT AND CLAIM-CONTROL RULES, enumerating the sections above.
  (2) Add a catch-all: "Any section, clause, constant or label in this document that is not carried
  over verbatim from v1.0_locked.md is POST HOC whether or not it is enumerated above; enumeration is
  for navigation, not for scope." (3) Add to the head of §20.8: "Every freeze in this section is
  relative to EXEC-002 only. Every constant and rule frozen here is POST HOC with respect to
  EXEC-001 and none of it may be described as preregistered." (4) Replace §1's prose
  `preregistered_scope` with an explicit section list.

### PH-03
Section: §20.7 labels L-B and L-H with RULE 3, and §20.10's expected headline
Issue:
  A post hoc UNDECIDABLE is headlined under v1.0's preregistered label string. L-B fires when S5
  does not HOLD (any leg FAILS **or is UNDECIDABLE**) and returns MECHANISM UNSUPPORTED; L-H fires on
  an UNDECIDABLE S5 leg; RULE 3 ranks UNSUPPORTED above UNDECIDABLE, so identical data fires both and
  the headline is the stronger negative. §20.10 pre-commits to exactly this. Three consequences:
  (a) it contradicts §15.5.5, §15.5.6, §15.5.9 point 5 and §24 item 18 in the same document;
  (b) the emitted string is character-identical to v1.0 §21 F7's preregistered label, so a reader
  cannot tell a preregistered decided failure from a post hoc undecided comparison resting on 40 vs 4
  and 15 vs 3 kept blank reads; (c) L-B's gloss is true for the UNDECIDABLE trigger and false for the
  FAILS trigger.
Why blocking:
  It lets the benchmark publish a conclusion its own operating characteristics forbid, by borrowing a
  preregistered label for a post hoc, weaker trigger — and §20.10 makes this the protocol's stated
  expected result.
Required change:
  (1) Split L-B: L-B1 fires only when some S5 leg FAILS by the §16.2 rule -> MECHANISM UNSUPPORTED;
  L-B2 fires when no leg FAILS but at least one is UNDECIDABLE -> routed to L-H. Remove UNDECIDABLE
  from L-B's trigger. (2) Suffix every label string with its register, e.g. "MECHANISM UNSUPPORTED
  (v1.0 §21 F7 — PREREGISTERED)" versus "MECHANISM UNSUPPORTED (POST HOC §1.1, via S5)", required in
  `V1_1_OUTCOME`, `branch_labels_applicable` and every propagated copy. (3) Correct §20.10's expected
  headline to MECHANISM UNDECIDABLE. (4) Add to RULE 3 that no label whose trigger includes an
  UNDECIDABLE comparison may outrank MECHANISM UNDECIDABLE.

### PH-04
Section: §20.7 WITHDRAWAL propagation block, with §20.7 L-I and §26
Issue:
  Mandatory propagation is defined for one branch only. The withdrawal must propagate to
  `orchestration/research_state.yaml`, `workflow_state.yaml`, FIND-0021 and
  `research/research-os.json`; there is no corresponding requirement on the L-I branch. Nothing
  requires the label "MECHANISM NOT WITHDRAWN — POST HOC, NOT ESTABLISHED", the POST_HOC_2026-09-19
  marker, the v1.0 block or §16.4's one-of-four-cells restriction to be written into any of the four
  files where the project's claims live. §26 mirrors the asymmetry.
Why blocking:
  Permanence that stops at `results_v1_1/` is not permanence, and the positive branch is where the
  qualifier is load-bearing and most likely to be dropped in transit: `research_state.yaml`'s
  `current_hypothesis` STATUS currently says the mechanism half is UNDERDETERMINED, and the natural
  edit on an L-I result is to strike that.
Required change:
  Rewrite the propagation block to bind EVERY headline. For L-I specify the exact text for each of
  the four targets: the §20.7 label verbatim with its register suffix, the literal
  POST_HOC_2026-09-19 marker, a pointer to the §20.0 v1.0 block, and §16.4's sentence naming the
  single cell in which the detection outcome changed. Add: "No v1.1 result may be entered into
  `research_state.yaml` known_evidence, `research-os.json` or any FIND record without the
  POST_HOC_2026-09-19 marker and the §16.4 restriction in the same entry." Replace §26's
  withdrawal-only item with one item per branch.

### PH-05
Section: §22.2 (`posthoc` column rule), §22.3, §17 and §26 (`statistical_tests.tsv`)
Issue:
  The permanent label is defined per row, but the register it must carry is per column and per file.
  (a) `criteria_evaluation_v1_1.tsv` carries S1-S7 rows and the rule stamps the preregistered S1-S4
  rows POST_HOC. (b) §22.3's `ablation_results.tsv` puts preregistered quantities (`zlo_min`,
  `retention_ratio`, `levels_detected_replicate_rule`) and post hoc ones (`delta_vs_C3`,
  `delta_vs_C4a`, `retention_ratio_3blank`, `retention_ratio_lo/hi`) on the SAME row under ONE
  `posthoc` value. (c) `statistical_tests.tsv` — the one artifact enumerating which comparison used
  which method — has no defined home: v1.0 §22 puts it at `results/`, §17 requires it to carry v1.0's
  NONE row and the v1.1 named-method rows, §22.4 forbids writing outside `execution_v1_1/` and
  `results_v1_1/`, §22.2's tree does not list it, and no `posthoc` column is specified for it.
Why blocking:
  This is the machine-readable layer the site build, the dashboards and any later agent will read. A
  label provably wrong on at least one column of every mixed artifact does not satisfy constraint (b).
Required change:
  (1) Make `posthoc` two-valued per row: `POST_HOC_2026-09-19` or `PREREGISTERED_V1_0`, never blank.
  (2) For artifacts carrying both registers on one row, require a column-level manifest — a
  `_posthoc` suffix on every post hoc column name, or a header comment line listing them verbatim —
  named explicitly for `ablation_results.tsv` and `per_sample_metrics.tsv`. (3) Name
  `results_v1_1/statistical_tests.tsv` in §22.2's tree, state that EXEC-001's row is copied in
  unmodified carrying `PREREGISTERED_V1_0`, and confirm `results/statistical_tests.tsv` is read-only.
  (4) Add the corresponding §26 items.

### Lens 5 minor issues

1. §20.0 and §16.4 state rules unsatisfiable for the artifacts they govern (a twelve-line text block
   and a four-cell table cannot live inside a TSV that states a verdict or a `zlo_min`); scope both to
   human-readable artifacts and give the TSVs a `v1_0_registered_outcome` column and a
   `detection_table_ref` pointer.
2. The banner and §20.6 clause 0 both say "two post hoc tests" while L-I requires S5, S6 AND S7;
   replace with "the post hoc tests of §1.1".
3. AGENTS.md rule 8 is violated inside §10.2's normative arm-definition text: "ALT reads in a
   pure-normal blank under the gate are basecall or alignment errors by construction" is an assumption
   stated as a construction, and the sentence that follows is an interpretation of the 8.15x
   observation asserted as fact. Keep the number, move the inference to a labelled interpretation
   note, and state the assumption as an assumption.
4. §20.5's closing paragraph pre-emptively weights a named non-success outcome ("carries very little
   evidential weight") inside a success-criterion section; keep the requirement to print §15.5.9's
   figure, move the weighting to §24.
5. §20.4 says S6-STRICT produces no verdict but §20.7 attaches no label to it, so its outcome floats
   outside RULE 1's applicable-label set; add a citation rule.
6. §1's `preregistered_scope` puts prose inside a machine-readable list.

---

## Consolidated major-issue index (round 2)

```text
Lens 1  MAJ-L1-01  pattern-blind set omits the property that GENERATES score_b1 (call uncertainty),
                   plus read length, MAPQ, local coverage; §16.7(c) has no consequence
        MAJ-L1-02  C3's decile strata do not hold density fixed; d/t against a fixed cut prefers low-t
        MAJ-L1-03  "at the same retention" has no defined cross-sample threshold transfer
        MAJ-L1-04  BLANK_TRIPLE safeguard confined to AXIS-L x V2 though the reduction holds under V1
        MAJ-L1-05  paired bootstrap under-specified at the point that sets its width

Lens 2  MAJ-L2-01  C1 draw count 200 -> 2000 re-parameterises preregistered S1 / S4(ii) / F8; F11
        MAJ-L2-02  sd-inflation not pinned to f = 1; the inflation is biased toward B1 under V2
        MAJ-L2-03  operating characteristics computed for a criterion the protocol does not install
        MAJ-L2-04  L-I unreachable by arithmetic while every other outcome propagates as a withdrawal

Lens 3  SV-01      bootstrap used as a null; every refutation label structurally unreachable
        SV-02      null_sd never defined, yet it is the verdict statistic's denominator
        SV-03      no undefined-resample rule, ceiling or column; 36% undefined on COLO829 C2
        SV-04      min-of-min functional; simulated rule is not the installed rule
        SV-05      size claim computed under three-independent-blanks the same document refutes
        SV-06      five significant figures on one kept blank read under a false provenance carve-out

Lens 4  X-01       the 28 input BAMs no longer exist (CRAM since 2026-09-12, EV-0052)
        X-02       per-worker leakage expectation unsatisfiable under CRAM; NM/MD fallback needs the
                   reference §14 forbids
        X-03       "at that same nominal rule" undefined across samples with differing n_scorable
        X-04       bootstrap does not say what is resampled and what is held fixed
        X-05       §23's import rule and §15.5.10's sd inflation cannot both be obeyed

Lens 5  PH-01      v1.0's named-outcome block labelled "reprinted in full" and abridged
        PH-02      §1.1 declared canonical and complete; omits the whole verdict apparatus
        PH-03      post hoc UNDECIDABLE headlined under v1.0's preregistered label string
        PH-04      propagation defined for the withdrawal branch only
        PH-05      per-row `posthoc` rule cannot label mixed-register artifacts; statistical_tests.tsv
                   has no home
```

---

## The single objection most likely to be raised

> "You cannot re-run the 28 BAM passes. The BAMs were converted to CRAM on 2026-09-12 and EV-0052,
> written in this repository on the same date as this draft, says so. The protocol asserts the
> opposite in §2-9 and prices the whole run against a format that is gone."

Recorded by lens 4 as X-01. Independently of the scientific findings, it makes the draft
non-executable as written.

---

Routing: return to `benchmark-designer`. Panel verdict NOT ACCEPTED (5 REVISE, 0 REJECT,
25 major issues); the ACCEPT rule requires zero of each.
