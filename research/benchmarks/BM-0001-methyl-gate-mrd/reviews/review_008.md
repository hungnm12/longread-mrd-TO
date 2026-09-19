# Benchmark Review — Panel

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v1.1_draft.md` (v1.1, DRAFT — design iteration 8, 4,933 lines)
Reviewer role: five-lens adversarial panel (grill-me), post-QC redesign review
Review iteration: 8
Review round: 3 of 3 — final round within the loop budget
Date: 2026-09-19

No panel member edited the protocol and no panel member executed any part of the benchmark.
`protocols/v1.0_locked.md` and the whole of `EXEC-001` were opened read-only and are unchanged.

This file is a transcription of the round-3 panel record. It performs no analysis of its own.

---

## Panel composition

The same five lenses as rounds 1 and 2:

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

NOT ACCEPTED — REVISE. Round budget exhausted.

```text
Lens 1  mechanism discrimination      REVISE    3 major  (GR3-MAJ-01 .. GR3-MAJ-03)
Lens 2  strictness                    REVISE    3 major  (R3-L2-01 .. R3-L2-03)
Lens 3  statistical validity          REVISE    4 major  (SV3-01 .. SV3-04)
Lens 4  executability / cost          REVISE    3 major  (L4-MAJ-01 .. L4-MAJ-03)
Lens 5  pre-registration hygiene      REVISE    4 major  (PH8-01 .. PH8-04)
                                      -------------------
                                      5 REVISE, 0 REJECT, 0 ACCEPT, 17 major issues
```

Major-issue trajectory across the three rounds: **34 -> 25 -> 17**. No lens returned REJECT at any
round. The design/review loop limits (`max_design_iterations: 8`, `max_review_iterations: 8`) are
reached at this iteration, so the draft is NOT ACCEPTED within the round budget and the loop stops
here rather than continuing to a fourth round.

---

## What the designer recorded as resolved at this iteration

The iteration-8 handoff claimed resolution of all 25 round-2 major issues and of 28 round-2 minor
issues. The panel accepted most of those resolutions. Confirmed resolved, with the panel's own
verification where recorded:

```text
MAJ-L1-01  P = {C4a, C4b, C4c, C4d, C4e}; C4c is per-read modification-call uncertainty with the
           invariance proof u(p) = u(255-p); F12 fires on ANY member; §16.7(c) given a RHO_MIN
           consequence
MAJ-L1-02  C3 stratifies on EXACT integer score_C2 with STRATUM_MIN = 30, STRATUM_WIDTH_MAX = 1.25
           and a 1/cut straddle VALIDITY trigger
MAJ-L1-03  GLOBAL KEEP FRACTION transfer; ladder-index, percentile and cut-VALUE transfer named as
           FORBIDDEN; V-e asserts both arms' blank thresholds were derived by the same rule
MAJ-L2-01  C1 split into a preserved j = 0..199 vector (feeding S1, S4 clause (ii), F8, F11) and a
           post hoc j = 0..1999 vector; `_200` / `_2000` suffixes; no unsuffixed C1 column
MAJ-L2-02  f = 1 is the only factor at which a leg may HOLD; f in {2, 4, 11.7} disqualifying-only;
           F14 (b) INFLATION-ONLY; the per-unit-f algebra stated
SV-01      centred family-wise refutation rule (D* - D_obs)/null_sd*, making every refutation label
           reachable for leg (i)
X-01       §6.1 names the 28 CRAM paths, the .crai, the decode reference and its md5, pysam mode
           'rc', recorded as a deviation with Methodology changed: NO; EV-0052 added to created_from
PH-01      v1.0's named-outcome block verified byte-for-byte against v1.0_locked.md lines 713-731,
           including "which may not be relabelled" and all four trailing clauses
PH-02      §1.1 given a CATCH-ALL so enumeration is navigational, not scope-defining
PH-03      L-B split into L-B1 / L-B2; RULE 3b; RULE 5 register suffixes; §20.10's expected headline
           corrected to MECHANISM UNDECIDABLE
PH-05      two-valued per-row register + `# POSTHOC_COLUMNS:` manifest for mixed-register artifacts
```

Two structural changes made at this iteration were recorded by the panel as declared rather than
smuggled, and as not breaching qc_001.md rule 1 (which governs v1.1 against v1.0):

- **§20.6 clause 0b — the positive branch is closed.** Stated as a finding of the DESIGN, not of
  EXEC-002: F11 freezes EXEC-001's retention ratios, HCC1395 has point(B1) 1.6741 < point(C2)
  1.6839, so under §16.2's interval rule S5 leg (b) cannot HOLD, S5 cannot HOLD, S7 cannot HOLD and
  L-I is unreachable. The withdrawal rests on EXEC-001 plus qc_001.md, and §20.7 splits it into
  WITHDRAWN-ON-EVIDENCE and WITHDRAWN-AS-UNDECIDABLE.
- **The rewritten and re-run `s6_operating_characteristics.py`.** Its measurement is worse than
  iteration 7 reported: the pooled rule's size is 0.093-0.182 (independent blanks) and 0.269-0.343
  (correlated blanks), not 0.05; the centred family-wise refutation rule's size is 0.158-0.417.
  Both are printed in §15.5.9 and must be reported beside every HOLD and every refutation label.

---

## Standing checks, per lens

```text
                         strictly_harder_check                          post_hoc_labelling_check
Lens 1   PASS in the support direction, against v1.0,
         for every new criterion; one named exception
         (RULE 4 must not convert a post hoc UNDECIDABLE
         into v1.0's HELD)                                          PASS
Lens 2   PASS in the support direction — no configuration
         found that fails v1.0 and passes v1.1;
         FAIL on the reverse test (R3-L2-01)                        PASS
Lens 3   PASS against v1.0, with two recorded caveats               PASS
Lens 4   PASS, scoped                                               PASS
Lens 5   PASS                                                       FAIL, on two strings (PH8-01,
                                                                    PH8-02)
```

Round-3 summary of the two checks, transcribed:

- **Strictness.** Four lenses independently verified the conjunction: v1.1's only non-withdrawal
  branch is "S1, S2, S3 and S4 all hold [v1.0 §20, verbatim] AND S5, S6 and S7 all hold", S5 leg (a)
  is v1.0's S4 verbatim with both clauses decided by v1.0's POINT rule, and §16.2 explicitly refuses
  to make S4 harder by the interval reading (`leg_a_interval_reading` is non-verdict-bearing), so S4
  is neither strengthened nor weakened. Forbidden list (c) was audited item by item and nothing moved:
  primary level 0.1%, call threshold 3.0, the `1 <= alt <= 2` gate on the unfiltered count, V1/V2,
  S1-S3 all carried verbatim with their INPUTS pinned. The two internal relaxations (S6-STRICT ->
  pooled; F9 point -> interval) are between post hoc drafts and are declared in §20.9. Lens 2's FAIL
  is the reverse failure: the BLANK_TRIPLE determination fires by construction in at least one
  (axis x construction) cell on any data, so S6 may be unsatisfiable regardless of the biology, and
  the protocol neither says so nor computes the quantity it claims decides it.
- **Post hoc labelling.** Four lenses passed. Lens 5 failed it on two strings: §21's post hoc F9 and
  F12 emit v1.0's preregistered label string with no RULE 5 register suffix, and §22.5's normative
  `WITHDRAWAL_BASIS` field attributes the withdrawal to "EXEC-001 plus qc_001.md" when it follows
  only from post hoc S5 leg (b) under post hoc §16.2 — and cites a QC document that states "QC does
  not overturn it" and "This is not a claim that H1 is false".

---

## Lens 1 — MECHANISM DISCRIMINATION

Verdict: **REVISE**

> "The draft survives most of the lens that killed v1.0 … But three faults remain, and all three are
> the QC-01 failure mode reappearing."

### GR3-MAJ-01
Section: §20.4 S6 leg (iv); §21 F12; §20.7 L-C / L-E; §15.5.8 (d); §15.5.9 RESULT 4 and RESULT 5;
§22.2 `familywise_size_model_c`
Issue:
  The refutation direction is decided by a maximum over seven comparator variants (C4a, C4b, C4c,
  C4d+, C4d-, C4e+, C4e-) and is allowed to fire in any of 32 cells, with no correction for either
  selection and no measured size outside one cell type. Centring on `D_obs` removes the observed
  effect but NOT the selection offset: under exact per-comparator equivalence
  `E[max_X Z(X)] > E[Z(B1)]`, so `D_obs(t)` is negative by construction (order one null sd; the
  per-target sd of the paired difference is 0.615-2.150 z-units), and the centred reference is
  centred on that already-offset statistic. §15.5.8 (a)'s FIXED/MOVES list does not say whether the
  argmax member is re-selected inside each resample. §15.5.9 RESULT 5 states "This script simulates
  LEG (i) ON AXIS-L ONLY", so the size of the rule deciding legs (ii), (iii), (iv) and all of AXIS-B
  is unmeasured — while §22.2 requires `familywise_size_model_c` beside every refutation label from a
  script that cannot produce it, and §15.5.8 (d) itself says "A refutation rule with no stated
  operating characteristics may not decide a verdict in this document". Finally F12 and §16.7 (c)
  permit a comparator flagged UNINFORMATIVE, MAPQ_DEGENERATE or uncomputable to FIRE F12.
Why blocking:
  ADVERSARIAL SCENARIO, and the likeliest one on these counts: methylation pattern contributes
  nothing AND no named pattern-blind property contributes anything either. C4e is MAPQ, which §10.2
  concedes is heavily atomic, so at matched count it selects an essentially arbitrary subset of the
  35-63 scorable ALT reads. Across 7 variants, 3-7 targets, 2 axes, 2 constructions and 2
  individuals, one beats B1 by chance; F12 fires, L-E is emitted naming mapping quality, §20.7 RULE 3
  headlines "MECHANISM UNSUPPORTED — PATTERN-BLIND READ PROPERTY", and the propagation block writes
  WITHDRAWN-ON-EVIDENCE into `research_state.yaml`, `research-os.json` and FIND-0021 — a causal claim
  about a named read property that contributed nothing. This is QC-01 with the sign reversed, and it
  defeats the draft's own WITHDRAWN-ON-EVIDENCE / WITHDRAWN-AS-UNDECIDABLE safeguard.
Required change:
  (a) Make the refutation statistic PER MEMBER and PER DIRECTION, and define the family-wise
  reference over the SAME index set the label may fire on — `M* = min` over
  {targets x members x directions} of the centred studentised `W*`, per cell. Keep the max-over-P
  form for the HOLD direction only, where it is conservative. (b) Extend the family-wise reference
  across the cells a label may fire in, or restrict the labels to a single pre-named cell. (c) State
  normatively whether the argmax over P is re-selected inside each resample; re-selection is the only
  admissible reading. (d) Extend `s6_operating_characteristics.py` to simulate the refutation rule
  for legs (ii), (iii), (iv) and AXIS-B, or delete `familywise_size_model_c` and make the affected
  labels unreachable. (e) Reverse the clause letting an UNINFORMATIVE / MAPQ_DEGENERATE /
  uncomputable member fire a refutation: route it to L-H or to a separate non-propagating label,
  never to WITHDRAWN-ON-EVIDENCE.

### GR3-MAJ-02
Section: §15.5.8 (a), (b), (c), (d); §20.4's leg table; §20.7 L-D and L-F; §10.5
Issue:
  REFUTATION-ELIGIBLE has no computable definition for the permutation legs. §15.5.8 (a) is headed
  "the interval for legs (i) and (iv)" and is the only place `D*`, `null_sd*` and a FAILS rule are
  defined; §15.5.8 (d) builds the family-wise bar entirely out of those quantities. Legs (ii) and
  (iii) are permutation-band legs: (b) and (c) define a HOLD threshold, a TIE rule and an
  admissibility ceiling, and NO FAILS threshold and no family-wise construction at all. Yet §20.4
  says every leg "returns HOLDS, FAILS, UNDECIDABLE or EXCLUDED by the rules of … §15.5.8", and
  §20.7 defines L-D and L-F on a quantity that cannot be computed for those legs.
Why blocking:
  Two of the four named refutation labels are structurally unreachable — the precise defect §21's
  closing paragraph says iteration 8's "single most important repair" removed. SV-01 survives for
  legs (ii) and (iii). The consequence is worst where it matters most: leg (ii) is the C3 leg, the
  control installed to answer QC-01's "pattern beyond density" question, and as written it can return
  HOLDS or UNDECIDABLE and nothing else. A leg that cannot register its own negative outcome is not a
  criterion. The alternative reading is worse: an executor with a required `refutation_eligible`
  column and no rule will improvise one, and the improvised rule will decide a published label.
Required change:
  Define the FAILS and REFUTATION-ELIGIBLE rules for the permutation legs explicitly in §15.5.8 (b)
  and (c), in the same normative register as (a): a leg FAILS at a target iff `Z(B1, tau)` lies below
  the band's 5th percentile, and the family-wise reference is the min over evaluable DISCRIMINATING
  targets of the standardised permuted difference built from the same 2000 draws (per draw j form
  `W_j(t) = (Z(B1,t) - Z_j(arm,t)) / sd_j(t)`, take `min_t`, compare the observed `min_t` to that
  distribution's 5th percentile). Simulate its size and power in §15.5.9 alongside RESULT 4. If no
  such construction is adopted, §20.7 must state that L-D and L-F are UNREACHABLE, in the same
  explicit form §20.6 clause 0b uses for L-I.

### GR3-MAJ-03
Section: §10.1 (C3); §10.2 (P); §20.3 S5 legs (b)-(d); §20.4 S6 legs (i)-(iv); §18.1; §22.5
Issue:
  No criterion in v1.1 can be satisfied only by methylation PATTERN, because the design contains no
  null that holds a read's own modification calls fixed and destroys only the pattern. §10.1 claims
  otherwise — "C3 is that null, and only that null" — and §10.2 immediately contradicts it: "C3
  destroys the read-to-error-rate correspondence exactly as thoroughly as it destroys the
  read-to-pattern correspondence. So a filter that knows only per-read error rate passes C3." The
  same hole runs through the other legs: leg (i) is satisfied by any filter with a higher differential
  ALT enrichment than C2 whatever drives it; leg (iv) by any filter that is a BETTER noise detector
  than the five named proxies, which `score_b1 = d/t` plausibly is by construction. The missing device
  is not another comparator arm but a REFERENCE-SIDE permutation, computable in the same pass from
  what `run_sample.py` already builds (`conf` and `d += (me != (1 if b >= 0.5 else 0))`, lines 76,
  82-86): permuting the binary consensus calls across the positions of `conf` leaves every read's own
  call vector, its t, its length, its uncertainty, its MAPQ and the whole ladder untouched and
  destroys only the position-specific correspondence.
Why blocking:
  The whole purpose of v1.1 is to install a criterion that can carry the mechanism claim after QC-01
  showed S4 could not. As drafted, every leg of S5 and S6 is satisfiable in full by a filter that
  knows only per-read modification-call noise. The draft's defences (§18.1's licensing paragraph,
  §24 items 16, 19, 21, §20.6 clause 0b) are prose fences around a verdict machinery that still emits
  leg-level HOLDs into the artifacts, and §22.5's normative layout does NOT require §18.1's licensing
  block for "B1 > C3" or "B1 > every member of P". And the false sentence in §10.1 is the same species
  of error QC-01 found in S4: a control described as excluding a confound it does not exclude.
Required change:
  Either (a) install the reference-side permutation as C5 and add it as a further necessary condition
  — S6 leg (v) against C5's 2000-draw band and S5 leg (e) — with §10.5-style POWER and VALIDITY
  triggers, stating in §18.1 that B1 > C5 licenses "not explained by per-read modification-call noise
  or by the read's global methylation level" and licenses nothing about library of origin; this is
  purely additive, costs no new I/O and is strictly harder in the support direction. Or (b) if C5 is
  out of scope for EXEC-002: delete "C3 is that null, and only that null" from §10.1; add a binding
  clause to §20.4 that no S6 leg HOLD may be stated anywhere without §18.1's licensing block for that
  leg in the same block; add that licensing block to §22.5's normative layout; and record in §25 as a
  new unresolved decision that the pattern-isolating null was identified, specified and deferred.
  Fixing §10.1's sentence is required under either option.

### Lens 1 minor issues

1. §20.7 L-D's gloss mischaracterises C3 in the same way §10.1 does ("a permutation that preserves
   density and destroys pattern"); reword to "preserves density at the realised stratum resolution and
   destroys the read-to-score correspondence within a stratum".
2. C2 is swept in one direction only, but §10.1's own arithmetic shows the pattern-blind density twin
   of B1 points the OTHER way (at cut = 1/13, a read with t <= 12 is kept on a single discordant
   call). C4d and C4e are swept in both directions for exactly this reason; a bottom-k density arm is
   free in the same pass.
3. RHO_MIN = 0.10 is a very low bar for "informative": a Spearman of 0.10 over 20-63 scorable ALT
   reads shares about 1% of rank variance. Print every member's rho beside any leg (iv) HOLD.
4. §16.7 (a)'s 8.15x blank ALT-enrichment observation is reported per arm but never contrasted
   between B1 and the members of P; the contrast costs nothing and would show whether B1 is simply the
   sharpest available error detector.
5. The BLANK_TRIPLE safeguard is scoped to leg (i) only though its algebra applies to every AXIS-L
   leg; require `decided_by` beside every AXIS-L leg verdict.
6. §24 items 21 and 22 assert rather than measure that no per-read field distinguishes source library;
   require the executor to RECORD, once, whether any per-read field (RG, read-name provenance, tag)
   does, since library of origin "bounds every mechanism statement this benchmark can make".
7. §20.8 clause 3's block heading still reads "FROZEN BEFORE EXECUTION" and depends on the heading
   clause three paragraphs above it; inline "(before EXEC-002; POST HOC with respect to EXEC-001)".
8. §15.5.9's RESULT 1 table omits rows and points at `protocols/support/s6_operating_characteristics.py`
   and its `.out.txt` as the frozen basis; both must exist and be checksummed with the protocol before
   v1.1 locks.

---

## Lens 2 — STRICTNESS

Verdict: **REVISE**

> "Through this lens the draft passes the test it was most likely to fail … The bar has not moved
> sideways. It has, however, moved into the reverse failure the lens also asks about, and in a place
> the draft has not identified."

### R3-L2-01
Section: §15.5.4 (final consequences block), §20.4 (the BLANK_TRIPLE clause), §15.5.9 point 7
Issue:
  The BLANK_TRIPLE determination fires by construction in at least one (axis x construction) cell,
  and its consequence clause has no stated scope. §15.5.4 marks a row BLANK_TRIPLE iff the arms'
  matched kept-ALT counts agree within the count tolerance AND their `sample_sd` agree within
  SAMPLE_SD_TOL = 0.05. On AXIS-L the first condition holds at EVERY evaluable target by definition
  (`n_tau(r)` is the SAME integer for every arm and the count match is a condition of evaluability),
  and the second holds under V1 by the protocol's own measurement (`sample_sd/sqrt(G)` = 0.97 ± 0.02,
  inside a tolerance §15.5.4 says was chosen as "the natural constant from the 0.97 ± 0.02
  measurement") — so AXIS-L x V1 is BLANK_TRIPLE on every row, on any data. Symmetrically, on AXIS-B
  the blank triples are matched to within one read in total, so under V2 the two arms' `sample_sd`
  agree EXACTLY and AXIS-B x V2 is BLANK_TRIPLE on every row. §20.4 requires every leg to HOLD in
  EVERY cell while the BLANK_TRIPLE clause is scoped to "an individual" — and the iteration-8 note
  beneath it says "the rule now names the determination, not the cell", i.e. the scope was deliberately
  deleted and not replaced. §15.5.9 point 7 half-sees this and mislocates it ("exactly under V2" is
  wrong for AXIS-L, where B1's triple is 10/8/8 against C2's 1/1/1, a 66% `sample_sd` difference), then
  discharges the problem onto a computation that does not exist: `s6_operating_characteristics.py` and
  its frozen `.out.txt` contain RESULT 1-5 and no BLANK_TRIPLE quantity anywhere.
Why blocking:
  This is the reverse failure, on the one criterion written to answer QC-02. Under the per-cell reading
  EXEC-002 cannot return HOLDS for S6 on any data — the sweep's outcome is fixed before it runs by an
  arithmetic property of the matching rule — and every downstream statement that S6 "did not hold" is
  uninterpretable, including WITHDRAWN-AS-UNDECIDABLE, which asserts that the benchmark did not resolve
  the comparison when the design guaranteed non-resolution. Under the per-individual reading, S6 can be
  reported as HOLDING while three of four cells are the QC-01 tie restated. It also contaminates every
  power number quoted: RESULT 3 / RESULT 5 are computed with the count floor and region filter but with
  no BLANK_TRIPLE determination, so "P(hold)|1.5x 0.457-0.589" is the power of a rule that is not the
  rule §20.4 installs, and RESULT 5's correctly-labelled UPPER BOUND may be 0.
Required change:
  (1) State the scope of the BLANK_TRIPLE consequence clause NORMATIVELY in §20.4: whether it ranges
  over an (individual x axis x construction) cell or over the individual across all four cells, and
  which cells. (2) Add to §15.5.4 the advance statement the algebra forces, cell by cell — AXIS-L x V1
  and AXIS-B x V2 are BLANK_TRIPLE at every evaluable target by construction — and correct §15.5.9
  point 7's "exactly under V2" on AXIS-L. Then state the consequence for §20.4's conjunction
  explicitly: if those cells can never carry a non-BLANK_TRIPLE positive leg (i), say in the protocol
  that S6 CANNOT HOLD on any data, that L-I is therefore closed a second time and independently of
  clause 0b, and that the only reachable S6 outcomes are UNDECIDABLE and the refutation labels. That is
  an acceptable design if declared; it is not acceptable discovered afterwards. (3) Either extend the
  script to compute P(a cell carries a non-BLANK_TRIPLE positive leg (i)) per cell and re-freeze it
  under §20.8 clause 7, or delete the §15.5.9 point 7 sentence claiming it reports it.

### R3-L2-02
Section: §15.5.6 clause (g) and its disposition sentence; §15.5.11 step 1; §21 F12; §16.7 (c);
§20.4 leg (iv)
Issue:
  Four sections give two contradictory rules for the same data, and the mechanical chain kills the
  refutation the other three promise. §16.7 (c), §21 F12 and §20.4 leg (iv) all state that an
  UNINFORMATIVE comparator "may still contribute a REFUTATION". But §15.5.6 makes informativeness a
  COUNT-FLOOR clause (g), and §15.5.11 step 1 says "EXCLUDED_UNDERPOWERED iff any clause of the
  §15.5.6 count floor fires … applied FIRST and takes precedence", with "Exclusion is never a pass and
  never a refutation." F12 fires only "at any DISCRIMINATING target" and §15.5.8 (d)'s minimum is over
  "evaluable DISCRIMINATING targets". So an uninformative, MAPQ_DEGENERATE or NM-uncomputable member's
  targets are EXCLUDED_UNDERPOWERED, never DISCRIMINATING, and F12 cannot fire on them. The section is
  also internally inconsistent about which clauses produce an exclusion: §15.5.6's disposition sentence
  names (a)-(e) while §15.5.11 step 1 says "any clause"; (f) and (g) have no stated disposition.
Why blocking:
  The direction is permissive: it deletes a refutation route and leaves the softer label standing. On a
  run where a pattern-blind comparator beats B1 at matched count while being weakly rank-correlated
  with score_b1, the protocol can report L-H "MECHANISM UNDECIDABLE … NOT a refutation", propagating as
  WITHDRAWN-AS-UNDECIDABLE, while three other sections say that run is F12/L-E, WITHDRAWN-ON-EVIDENCE.
  Two rules for the same data with a reporter free to pick is the defect §21's own preamble says it
  removed for S4/F7 at iteration 6.
Required change:
  Make clause (g) asymmetric in the section that decides: either (i) move it out of the count floor and
  into §15.5.11 as a HOLD-direction-only disqualifier, so the target stays DISCRIMINATING and
  refutation-eligible while its HOLD contribution is forced to UNDECIDABLE; or (ii) delete the "may
  still FIRE F12" sentences from §21 F12, §16.7 (c) and §20.4 leg (iv). (i) is the direction
  qc_001.md rule 1 requires. Either way, reconcile §15.5.11 step 1 with §15.5.6's disposition sentence
  so clauses (f) and (g) have one stated disposition and the (a)-(e) / "any clause" mismatch is closed.

### R3-L2-03
Section: §20.4 leg (iv), §21 F12, §15.5.8 (d), §15.5.9 RESULT 4 and RESULT 5, §20.9
Issue:
  Expanding P from two members to five is declared in ONE direction only, and the refutation side it
  makes easier has no stated operating characteristics — which the same document forbids. §20.9
  declares leg (iv) "STRICTLY HARDER … the max is taken over five named comparators instead of two,
  and F12 fires on any of them." The first half is right for the HOLD direction; the second half is a
  loosening of the REFUTATION bar not declared as one, since F12 "fires on ONE member" and C4d/C4e
  enter at the better of two directions, making the refutation side a maximum over seven comparator
  instances per target per axis per construction. §15.5.8 (d)'s family-wise minimum is over targets
  within one leg against one comparator and contains no minimum over members of P. RESULT 4 measures
  size and power for leg (i) against C2 alone (RESULT 5: "AXIS-B's blank-matched draws and legs (ii),
  (iii) and (iv)'s comparators are NOT simulated") and its single-comparator size is already
  0.158-0.417 against a nominal 0.05.
Why blocking:
  L-E / F12 is a verdict-bearing, headline-eligible refutation that propagates as WITHDRAWN-ON-EVIDENCE
  into the project's evidence base. With a per-comparator family-wise size already up to 0.417 and a
  maximum over seven instances with no control across them and no simulated size, the benchmark can
  emit an affirmative negative mechanism claim, naming a specific read property, at an error rate it has
  never measured — the mirror image of the SV-01 defect iteration 8 says it repaired. The §20.9 entry is
  also incomplete by the document's own standard; the §15.5.8 (d) entry immediately above it models the
  right practice by declaring both directions.
Required change:
  Pick one and fix §20.9 either way. (1) Extend §15.5.8 (d)'s centred statistic so the minimum ranges
  over members of P as well as over targets for leg (iv); or (2) keep F12 firing on any single member
  and give it stated operating characteristics by simulating leg (iv)'s max-over-P statistic and
  reporting its size under exact equivalence, re-freezing the script under §20.8 clause 7; or (3) demote
  F12/L-E to SIZE-QUALIFIED-ONLY and forbid it from being the headline. In all three cases §20.9 must
  declare that enlarging P is harder in the support direction AND easier in the refutation direction,
  and by how much.

### Lens 2 minor issues

1. §20.1 pins S1's C1 term to the preserved 200-draw vector but gives C2 no equivalent pin, although
   §10.6 has just made C2 a 200-seed object; a one-line NORMATIVE clause mirroring the C1 pin would
   close it. Harmless on this data, hence minor.
2. §15.5.4's BLANK_TRIPLE condition (a) does not say whether it tests arm-to-arm difference or each arm
   against `n_tau`, and on AXIS-B "matched kept-ALT counts" is ambiguous between the blank counts and
   the 0.1% counts — a choice that decides whether AXIS-B x V2 is BLANK_TRIPLE everywhere.
3. §20.7 RULE 3b is not scoped to named labels; on its face a reporter could apply it to L-C, L-E or
   L-F and demote a firing refutation to L-H. Enumerate the labels it governs.
4. §20.9's declaration that F9's point form is replaced by an interval form is correct and honestly
   declared, and creates no escape (F9 is post hoc, L-B2 routes to L-H, clause 0b closes the positive
   branch independently). Recorded so the next reviewer does not re-litigate it.
5. §16.1's switch to `retention_scorable_only` changes the column a PREREGISTERED criterion reads; the
   consequence is null (the two columns differ only for B0 and no preregistered criterion reads B0's
   retention), but one sentence in §20.9's "AGAINST v1.0" block should say exactly that.

---

## Lens 3 — STATISTICAL VALIDITY AT THESE COUNTS

Verdict: **REVISE**

> "The draft survives most of this lens, and it survives it honestly … That is a serious piece of
> statistical self-criticism and I am not manufacturing objections to it. It does not pass, for four
> reasons."

### SV3-01
Section: §15.5.8 (a) "null_sd — DEFINED NORMATIVELY"; §20.4 "THE VERDICT-BEARING RULE"; §15.5.9 RESULT
3 and RESULT 4; §20.8 clause 3 and clause 7; `protocols/support/s6_operating_characteristics.py`
Issue:
  The denominator of every verdict-bearing standardised statistic is named but never operationally
  defined, and the frozen advance simulation that justifies the rule computes it by the reading the
  protocol explicitly forbids. §15.5.8 (a) says `null_sd*` is "the sd of the paired difference computed
  INSIDE each resample (an inner studentising estimate)" and names the other two readings FORBIDDEN. An
  sd computed inside a resample requires a third resampling level, and the protocol fixes no inner
  resample count, no inner draw rule, no inner seed and no cost for it (`B_inner = 300` appears once,
  inside a parenthetical describing the simulation's own parameters). The script has no third level:
  `null_sd_star = np.nanstd(D_star, axis=1, ddof=1)` is the same functional as the line below it,
  `null_sd_obs = np.nanstd(np.where(undef, np.nan, D_star), axis=1, ddof=1)`, and RESULT 3 divides by it
  as a per-dataset scalar. So RESULT 3, 4 and 5 are computed with `null_sd*` held at `null_sd_obs`, the
  forbidden reading, while §15.5.9 promises "THE RULE AS INSTALLED, not a proxy".
Why blocking:
  §20.4's pooled rule and §15.5.8 (d)'s family-wise statistic both divide by a quantity the executor
  cannot compute from the text, so two executors following this protocol produce different verdicts from
  the same data — the defect SV-02 raised and this iteration claims to have closed. Independently,
  §20.8 clause 7 freezes the CHOICE of S6 over S6-STRICT on these tables and RESULT 4 requires the
  measured size printed beside every refutation label; both rest on characteristics measured for a rule
  other than the installed one.
Required change:
  Either (a) define the inner estimator operationally in §15.5.8 (a) — what is resampled at the inner
  level, how many inner resamples, the seed derivation, and the aggregation cost added to §23.1, noting
  that 2000 outer x `B_inner` inner recomputations is `B_inner`-fold more work than budgeted — and
  re-run the script with that third level so RESULT 3/4/5 are the rule as installed; or (b) install
  `null_sd_obs` as the normative estimator, delete it from the forbidden list, and say why a
  non-studentised percentile interval is acceptable. Either way the frozen table and §20.8 clause 7's
  frozen choice must be re-derived under the estimator actually installed, and §1.1 updated.

### SV3-02
Section: §15.5.10; §15.5.9 MODEL-C justification and every f = 11.7 row; §24 item 17; §1.1; §21 F14
Issue:
  The inflation factor that carries the entire pseudo-replication analysis is an UNGATED measurement
  applied to a statistic that is gated everywhere, and it comes from a record its own source declares
  superseded. §15.5.10 reads: "EV-0036: depth-normalised **ungated** blanks across three independent
  HCC1395BL libraries are 11,770.9 / 11,671.3 / 11,849.0, giving a between-library standard deviation of
  89.08 against the five pseudo-blanks' 7.64 — an 11.7-fold understatement." But §15.5.1 applies the
  gate first at every ladder point, so every count inflated here is gated. FIND-0018's own table gives
  the gated figures: 3 independent libraries sd 8.39, 5 pseudo-blanks sd 3.16 — a factor of 2.65, not
  11.7. And FIND-0018's first caveat reads: "CORRECTED 2026-08-25 by EV-0038 … the GATED sd falls from
  8.39 to 1.57 because duplication moves sites across the gate's 1-to-2 ceiling. Every figure in this
  finding should be read from EV-0038 instead." On the corrected gated numbers the between-library sd
  (1.57) is BELOW the five pseudo-blanks' gated sd (3.16). The draft cites EV-0038 once, for the
  pseudo-replication prohibition, and never for this correction.
Why blocking:
  f = 11.7 is not a decoration. F14 (a) makes it a disqualification rule ("If no leg survives f = 11.7,
  S6 may not be reported as leaving the mechanism claim standing, on any individual"); §15.5.9 uses it
  to state that "under V2 the design is INERT — P(hold) is 0.000 at every HCC1395 target"; and §24 item
  18 converts that into "THIS DESIGN CANNOT RESOLVE A MODEST TRUE EFFECT". Applying an inflation ~4.4x
  too large, or inapplicable altogether, makes the design declare itself inert on a number that does not
  describe its own statistic, and drives the choice between WITHDRAWN-AS-UNDECIDABLE and
  WITHDRAWN-ON-EVIDENCE off a mis-specified variance.
Required change:
  Recompute the inflation grid from GATED quantities. State both the uncorrected gated ratio
  (8.39/3.16 = 2.65) and the EV-0038-corrected one (1.57/3.16 < 1), cite EV-0038 as the governing record
  wherever EV-0036 is cited for this factor, and carry FIND-0018's own caveat that an sd from n = 3 has
  a 95% interval of 0.52x to 6.3x, so no single f is a "measured factor". If f = 11.7 is retained it must
  be labelled an UNGATED upper bound, and §15.5.9's inert-design conclusion and §24 item 18's resolution
  statement must be re-derived at the gated factors. §1.1 and §20.8 clause 3 update accordingly.

### SV3-03
Section: §20.3 S5; §21 F9; §20.7 L-B1 and RULE 3; §15.5.10; §15.5.9 RESULT 5
Issue:
  S5's refutation direction is verdict-bearing, headline-taking and propagating, and it has none of the
  three guards S6's refutation direction has. (i) No multiplicity control: §15.5.8 (d)'s centred
  family-wise bar is written for S6 and every label gated on it is an S6 label, while L-B1 fires when
  SOME S5 leg FAILS and S5 ranges over 2 individuals x 2 blank conventions x {leg (b) against C2, leg (c)
  against C3, leg (d) against each of five members of P} — roughly 28 uncorrected one-sided interval
  comparisons. (ii) No stated operating characteristics: §15.5.9 simulates leg (i) on AXIS-L only, so
  §16.2's interval-dominance rule has no simulated size or power anywhere, against §15.5.8 (d)'s own
  binding principle. (iii) No blank-spread sensitivity: §15.5.10 and F14 bind S6 legs only, and S5's
  intervals are built by resampling candidates inside each of the five TF0 replicates at its own size,
  i.e. as five independent samples, when EV-0014 / EV-0017 / EV-0045 record ~90% / ~45% read sharing and
  §24 item 20 of this same draft calls them "the single effective blank".
Why blocking:
  An interval built from overlapping pseudo-replicates treated as independent is narrower than the
  sampling distribution, and "FAILS iff `retention_ratio_lo(comparator) > retention_ratio_hi(B1)`" fires
  too easily when the intervals are too narrow. L-B1 is in the UNSUPPORTED tier of RULE 3, so it outranks
  L-H, and RULE 3b does not protect against it because L-B1's trigger is a FAILS. It becomes the headline
  and propagates under WITHDRAWN-ON-EVIDENCE — an affirmative negative claim from an uncontrolled
  multiple comparison on 40 vs 4 and 15 vs 3 kept blank reads, with no stated error rate and no
  sensitivity to a variance the document itself says is understated.
Required change:
  Give S5's interval rule the three guards S6's has before it may emit L-B1 or fire F9: a family-wise
  reference across the legs and comparators S5 ranges over, using the same centred construction with the
  min taken over legs and comparators; a simulated size and power for §16.2's interval-dominance rule
  under both MODEL-I and MODEL-C, printed beside L-B1 and F9; and either an explicit f-inflation of the
  retention-ratio interval or a normative statement that an S5 FAILS may not headline above L-H without
  it. Also state in §16.2 that the retention-ratio bootstrap resamples the five TF0 replicates as
  independent samples and understates the interval by the read-overlap factor.

### SV3-04
Section: §20.4 S6 leg (iv); §20.3 S5 leg (d); §21 F12; §20.7 L-E; §15.5.9 RESULT 4 consequence (3)
Issue:
  The refutation direction of leg (iv) ranges over five comparators with family-wise control across
  targets only. §21 F12 states "F12 fires on ONE member; it does not require all five". §15.5.8 (d)'s
  minimum contains no minimum over members of P. RESULT 4's simulated size is produced against a single
  comparator arm, yet RESULT 4 consequence (3) makes that figure mandatory beside the label: "EVERY
  refutation label … must be reported with RESULT 4's size figure for its own cell beside it."
Why blocking:
  RESULT 4 already measures the one-comparator size at 0.158-0.417 against a nominal 0.05. Taking a
  minimum over five comparators raises it further by an unstated amount, and the protocol then requires
  the label to be printed with the one-comparator number attached. L-E is a WITHDRAWN-ON-EVIDENCE label
  naming a member of P and propagating to the project evidence base; emitting it with an error rate that
  demonstrably does not belong to the rule that produced it is reporting a conclusion with a fabricated
  error rate. The HOLD side of leg (iv) is correctly conservative, so the asymmetry falls entirely on the
  refutation side — and the multiplicity was introduced in this iteration without its refutation-side
  cost being priced.
Required change:
  Extend §15.5.8 (d)'s centred statistic so `M*` and `M_obs` are minima over (DISCRIMINATING target x
  member of P) jointly for leg (iv), and over (target x leg) where a label can fire on several legs, and
  re-run RESULT 4 for the rule as installed so the size printed beside L-E and F12 is the size of the
  rule that emitted them. The same correction is needed for S5 leg (d) under SV3-03.

### Lens 3 minor issues

1. §15.5.9 describes MODEL-C as "effective blank count 1, i.e. perfectly dependent", but the script
   implements a nested-prefix model (`base = rng.random((NSIM, max(nB)))` then
   `U[arm] = [base[:, :nB[j]] …]`), so replicate 3's reads are a strict subset of replicate 1's, the
   counts obey b1 >= b2 >= b3 and `sd_b > 0`. Describe the implemented model.
2. §15.5.8 (a) states "§15.5.9 measures the null spread … at 0.83 to 3.1 z-units"; RESULT 1's MODEL-I
   range is 0.615 to 2.150 and MODEL-C's 0.324 to 1.495. The 0.83-3.1 figure is the superseded
   iteration-7 proxy.
3. §15.5.11 justifies DEGENERATE_HIGH's 0.50 constant against MODEL-I's smallest sd (0.615) while
   §15.5.9 declares MODEL-C the design's stated model (smallest 0.324). Re-anchor the justification or
   state that it is deliberately anchored on the wider model.
4. RESULT 1's `sim_sd_D` column is computed as the median over simulated datasets of the BOOTSTRAP sd,
   not the sd of `D_obs` across datasets; relabel it, or compute `sd(D_obs)` beside it.
5. §16.5 keys its significant-figure bands on the SUM of kept blank ALT reads across five TF0 replicates
   (40 reads -> 4 significant figures) while §24 item 20 calls those five a single effective blank.
   Display-only, so nothing is decided on it, but it is the direct response to QC-04.
6. §16.2's sizing SE `sqrt(1/40 + 1/75 + 1/4 + 1/8) = 0.643` assumes Poisson counts and independent
   replicates; at denominators of 3 and 4 kept reads the delta method is poor and independence is what
   EV-0045 refutes. It is quoted three times as "the corrected SE", which invites an inferential reading.
7. §15.5.9's approximation A4 states the two arms' blank draws are independent and "errs toward a WIDER
   null", true of the outer draws; the inner bootstrap shares `Lstar`, `Bstar` and the random-effect array
   between arms, which couples them positively and narrows `D*`. Faithful to the paired design, but not
   among the stated approximations, and it bears on the size inflation RESULT 4 reports.

---

## Lens 4 — EXECUTABILITY AND COST HONESTY

Verdict: **REVISE**

> "The draft is strong on the four things this lens cares most about, and I want that on the record
> because it is unusual. … It is REVISE and not ACCEPT because the artifact the entire re-run exists to
> produce is not executable as written."

### L4-MAJ-01
Section: §22.2 (`retention_sweep.tsv` columns), against §15.5.2 and §15.5.4
Issue:
  The sweep artifact — the whole product of the re-run — is keyed on an object the protocol elsewhere
  declares forbidden and meaningless. §22.2 lists `ladder_index, pct_equivalent, keep_fraction` under
  "PER-INDIVIDUAL (constant within the key)" while listing `n_scorable_reads` and `cut_or_k` under
  "PER-LEVEL / PER-REPLICATE". But §15.5.2 defines the ladder per arm per sample with
  `i95 = int(0.95*(n-1))` on that sample's own n, and §15.5.4 states outright: "FORBIDDEN, and named as
  forbidden: transferring the LADDER INDEX i (meaningless across differing n_scorable)". The 14 samples
  of one individual do have differing n — 58,879 / 58,990 / 76,594 / 76,583 measured from
  `execution/raw` — so one `ladder_index` cannot address an individual's 14 samples, and the only
  per-individual transferable abscissa §15.5.4 admits is the global keep fraction phi.
Why blocking:
  The executor cannot emit the artifact as specified without silently picking which sample's ladder
  defines the shared index — exactly the free choice §15.5.4 was written to close, and the one that
  decides which blank counts each curve point rests on. QC-02's deciding question is read off this file;
  a curve whose abscissa is ambiguous cannot answer it, and the ambiguity is invisible in the output
  because `ladder_index` prints as a single number either way.
Required change:
  Make `keep_fraction` (phi) the curve's abscissa and the per-individual key component. Demote
  `ladder_index` and `pct_equivalent` to the PER-LEVEL / PER-REPLICATE block as realised per-sample
  values beside `cut_or_k` and `n_scorable_reads`. State in §22.2 that the curve is indexed by the phi
  values attainable in every sample of that individual, and that `ladder_index` on a row is the realised
  canonical index in that row's own sample.

### L4-MAJ-02
Section: §15.5.2 last line and §22.2, against §23.1
Issue:
  The size and cost of the sweep artifact are never stated, and the two clauses that bound it contradict
  each other with the reconciliation left to the executor. §15.5.2: "`retention_sweep.tsv` reports the
  whole ladder, not only the matched points"; §22.2: "the full ladder, per individual x arm x ladder
  point"; §23.1: "the executor may exploit provided `retention_sweep.tsv` still reports the full curve at
  a stated stride and the reported stride is recorded" — "full curve" and "a stride" are not the same
  object, and the stride is a number the protocol never fixes. At the measured n (58,879-76,594) times
  ~10 deterministic arm-directions, 2 constructions, 14 level x replicate rows and 2 individuals, the
  full ladder is tens of millions of rows and a multi-GB file — while §22.1 is scrupulous about the raw
  cost ("of order 200 MB across 28 samples", against 1.7 TB free) and no section does the same for
  `results_v1_1/`. Almost the entire ladder is uninformative: only 36-50 gate-passing candidates per
  sample (HCC1395 TF1e-3 rep1: 50; COLO829 TF0 rep1: 36), each contributing at most 2 ALT reads, so
  `kept_ALT` takes at most ~60-100 distinct values and z is a step function — a 59,000-point ladder
  carries on the order of 63 distinct rows of information.
Why blocking:
  V-b, V-c and V-d, and F10 through them, are written "at every ladder point" / "in every arm and
  sample". If the reported ladder is an executor-chosen stride, the resolution of the three
  implementation-fault checks that gate reading any curve becomes an undeclared executor parameter, and a
  sweep with a real fault can pass validation. The alternative reading — the literal full ladder — is a
  multi-GB artifact the 2-hour budget was not derived against.
Required change:
  Delete "at a stated stride". Define the reported ladder normatively in §15.5.2's own vocabulary: for
  each arm and individual, the canonical ladder points for the union of attainable kept-ALT counts across
  that individual's three 0.1% replicates and three primary blanks, plus each arm's `n_max` anchor point.
  State the resulting row count and file size in §23.1 as §22.1 states the raw size. Re-scope V-b, V-c,
  V-d and F10 to that defined set, and give the aggregation the same measured-first treatment §23.1
  already mandates for the BAM pass.

### L4-MAJ-03
Section: §26 executor checklist, item "files_opened.txt checked PER WORKER against EXEC-001's
per-worker set", against §14
Issue:
  The checklist reinstates verbatim the leakage expectation §14 deleted as unsatisfiable. §14 records
  that the iteration-7 expectation could NOT be met because the inputs are now CRAM and CRAM decoding
  requires an index and a reference, and that leaving it would force the executor either to declare a
  deviation against the one guard that may never take one, or to widen the expected set silently. §26
  then says: "files_opened.txt checked PER WORKER against EXEC-001's per-worker set". EXEC-001's
  per-worker set contains a `.bam` and two candidate frames and no `.crai` and no reference; §6.1's
  worker opens a `.cram`, a `.cram.crai`, the two frames, the decode reference and its `.fai`. The check
  as worded fails on every one of the 28 workers.
Why blocking:
  The checklist is the document the executor works from at the keyboard, so its wording governs. It
  routes the executor into precisely the two bad outcomes §14 identified, and a silently widened
  expectation makes the file-open capture vacuous — QC-07's guarantee would then be reported as
  re-earned when nothing was actually checked.
Required change:
  Rewrite the §26 item to point at §14's enumerated set rather than EXEC-001's: "files_opened.txt checked
  PER WORKER against §14's ENUMERATED EXPECTED SET — the worker's own input CRAM, its `.cram.crai`, the
  two candidate frames, `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` (md5
  a6da8681616c05eb542f1d91606a7b2f) and its `.fai` — and against nothing else; any path outside that set
  or outside §14's declared aggregation-side reads is a LEAKAGE FAULT and the execution is RETURNED,
  never a deviation."

### Lens 4 minor issues

1. §22.1's bolded correction says "TEN ARRAYS (the iteration-7 text said 'nine' and listed eight …)";
   the block lists twelve entries and the size paragraph four lines later says "The twelve array
   entries". A miscount inside the sentence that exists to fix a miscount.
2. §22.1 calls `score_c4b_den` a "diagnostic" but §10.2 defines `score_C4b = n_amb / n_cov`, so it IS the
   denominator and C4b is uncomputable without it. Also, §10.2's definitions make `n_amb = n_cov - t`
   exactly, so `score_C4b = 1 - t/n_cov` is a function of two stored integers; say so, or two
   implementations will differ on the `cons[r] == CONF_LO` / `== CONF_HI` boundary cases.
3. `tag_precheck.tsv` has two homes: §14 and §26 put it in `execution_v1_1/`, §22.2's tree in
   `results_v1_1/`, against §22.4's "ONE location and no alternative".
4. §23.2's C3 rule does not pin the order in which a stratum's reads are enumerated, nor how the
   permutation is applied (`values[perm]` vs its inverse). No F11 consequence (C3 has no EXEC-001
   counterpart) but it leaves a new arm's numbers unreproducible by a second implementation.
5. `attainable_keep_fractions` is an O(n_scorable) object per arm and is excluded from the size estimate,
   which is derived explicitly from "the twelve array entries"; bound it to the phi values at which
   `kept_ALT` changes, or state its size.
6. §22.1 requires `attainable_alt_counts` per arm, a gate-dependent quantity, but EXEC-001's
   `run_sample.py` declares `GLO, GHI = 1, 2` and never uses them — the gate is applied downstream in
   `aggregate.py`'s `prep()`. State that `execution_v1_1/scripts/run_sample.py` applies the §9 gate when
   computing the attainable sets.
7. §26's "Gate-passing candidate set verified identical across B0/B1/C1/C2/C3/C4a/C4b and all ladder
   points" omits C4c, C4d and C4e; §20.9's strictness table has the same omission. The iteration-8
   additions were not swept through every enumerated list.
8. §6.1 should state that `pileup()` is called with no `fastafile` argument and `compute_baq` left at its
   no-reference default, exactly as EXEC-001 called it. Verified on pysam 0.24.0
   (`libcalignmentfile.pyx` line 2462: `self.fastafile = kwargs.get("fastafile", None)`) — the pileup's
   BAQ reference comes only from an explicit `fastafile=` kwarg, not from `AlignmentFile.reference_filename`,
   so BAQ stays off; that is the right outcome but it is currently luck rather than specification, and it
   is load-bearing for V-f.

### Lens 4 supporting record

Recorded as passing, verbatim from the lens: the draft proves rather than asserts that the sweep is not
computable from saved output (run_sample.py lines 80-92 and 119-143, both verified); the per-read schema
is concrete (integer numerator `score_b1_num` and integer denominator `score_c2` rather than a rounded
score, float64 `repr` round-trip for the two genuine floats, index space pinned to
`scorable = sorted(score_b1)`); EXEC-001 is preserved completely (`execution/scripts/` read-only,
EXEC-002's scripts at new paths, writes confined to `execution_v1_1/` and `results_v1_1/`); and
reproduction of EXEC-001 is required at three levels (F13/V-a at zero per-candidate mismatches, V-f on
every sweep-independent quantity before any curve is read, F11 on named columns at named precisions with
the C1 median-of-even-draws exemption and the `_200`/`_2000` split). The leakage story is handled properly:
the guarantee is re-earned not inherited, the decode reference is enumerated with an md5 and argued
non-leaking in QC-07's own four named classes, and the C4a fallback is routed through
`get_aligned_pairs(with_seq=True)` with an explicit prohibition on opening the reference.

---

## Lens 5 — PRE-REGISTRATION HYGIENE AND CLAIM CONTROL

Verdict: **REVISE**

> "The iteration-8 apparatus is genuinely strong and PH-01 through PH-05 are substantively fixed … But
> four defects remain, each of which would let a post hoc conclusion leave the benchmark carrying
> preregistered provenance or a restriction that does not restrict."

### PH8-01
Section: §20.6 clause 0b consequence 1; §20.7 "IN EITHER CASE" block; §22.5 `WITHDRAWAL_BASIS` field;
§26 propagation item
Issue:
  The single most-propagated sentence in the document attributes a POST HOC conclusion to PREREGISTERED
  artifacts, and misstates what qc_001.md says. §22.5 makes it a normative field: "WITHDRAWAL_BASIS:
  §20.6 clause 0b — EXEC-001 plus qc_001.md. EXEC-002 determined WHICH label applies; it could not change
  the withdrawal." But the withdrawal does not follow from EXEC-001 or from qc_001.md. It follows from
  applying S5 leg (b) (§20.3) under §16.2's INTERVAL DOMINANCE rule — both written 2026-09-19, both in
  §1.1 — to EXEC-001's preserved retention_ratio values. qc_001.md states the opposite of what it is cited
  for: "QC does not overturn it and it is preserved verbatim" and "This is not a claim that H1 is false.
  It is a claim that this benchmark, as locked, does not establish the mechanism half of its own research
  question." Per §26 and §20.7 this exact sentence is written into `research_state.yaml`,
  `workflow_state.yaml`, FIND-0021 and `research-os.json`.
Why blocking:
  qc_001.md constraint (b) forbids reporting post hoc material as preregistered. This is that failure at
  the one string that leaves the benchmark directory: a reader of `research-os.json` or FIND-0021 meets a
  withdrawal of H1's mechanism half whose stated basis is the preregistered execution plus the QC review.
  The POST_HOC_2026-09-19 marker in the same entry names the RESULT as post hoc, not the BASIS, so the two
  fields read as "a post hoc report of a preregistered withdrawal" — the exact inversion constraint (b)
  exists to prevent. It also lets a downstream reader take the withdrawal as robust when it rests on a
  0.009-of-one-SE point ordering that §20.10 itself shows one tie-break read reverses (C2 1.6839 ->
  1.3891, B1 would win).
Required change:
  Rewrite the `WITHDRAWAL_BASIS` string in §22.5, §20.6 clause 0b consequence 1 and §20.7's IN EITHER
  CASE block to name the post hoc basis, e.g.: "WITHDRAWAL_BASIS: §20.6 clause 0b — POST HOC criterion S5
  leg (b) (§20.3) decided by §16.2's POST HOC interval-dominance rule, both written 2026-09-19, applied to
  EXEC-001's preserved retention_ratio values. qc_001.md did not itself withdraw the claim; it records
  'QC does not overturn it' and 'This is not a claim that H1 is false'. EXEC-002 determined WHICH label
  applies; it could not change the withdrawal." The margin on which leg (b) is closed (-0.0098, 0.030 of
  one SE, one tie-break read reverses it) must travel in the same field or be pointed at from it. §26's
  propagation items must check the corrected string verbatim.

### PH8-02
Section: §21 F9 and §21 F12, against §20.7 RULE 5
Issue:
  §21's post hoc failure criteria emit v1.0's PREREGISTERED label string with no register suffix. F9's
  consequence line reads "-> MECHANISM UNSUPPORTED. The differential-retention signature is not specific
  to methylation pattern."; F12's reads "-> MECHANISM UNSUPPORTED — PATTERN-BLIND READ PROPERTY. NOT A
  SUCCESS." Both are registered POST HOC in §1.1. The same document carries v1.0's F7 verbatim at §21's
  head — "S4 fails while S1 holds -> MECHANISM UNSUPPORTED" — preregistered and binding. Three rules in
  one document emit the identical string, one preregistered and two post hoc, and §21 prints all three
  unsuffixed. §20.7 RULE 5 declares "An unsuffixed label is non-compliant with this protocol" and gives
  the reason; RULE 5's enumeration of where the suffix is required does not name §21, and §21 contains no
  reference to RULE 5.
Why blocking:
  This is PH-03's defect surviving in the section PH-03 did not sweep. An executor implements the failure
  criteria from §21's text; §21 tells it to emit a bare preregistered label string for a post hoc
  comparison whose HCC1395 margin is -0.0098 on 40 vs 4 kept blank reads.
Required change:
  Add the RULE 5 suffix to every label-emitting line in §21: F9 -> "MECHANISM UNSUPPORTED (POST HOC §1.1,
  via F9 / S5 leg (b))"; F12 -> "MECHANISM UNSUPPORTED — PATTERN-BLIND READ PROPERTY (POST HOC §1.1, via
  S6 leg (iv) / F12)". Add at §21's head: "§20.7 RULE 5 governs every label string this section emits;
  F1-F8 carry '(v1.0 §21 F<n> — PREREGISTERED)' and F9-F14 carry '(POST HOC §1.1, via <criterion>)'."
  Audit F10, F11, F13 and F14 for the same omission and add §21 to RULE 5's enumerated list.

### PH8-03
Section: §16.4 (Forbidden paragraph), against §20.7 PROPAGATION block and §26's propagation checklist
Issue:
  The propagation block and §26 both require a verbatim string that §16.4 does not contain. §20.7
  mandates, for every branch, "§16.4's sentence naming the one individual x construction cell in which the
  detection outcome changed", and §26 checks for "§16.4's cell sentence". §16.4 contains the four-cell
  table and this sentence: "The detection outcome changes in **one of four** individual x construction
  cells. Any sentence about detection must name that cell." That sentence does not name the cell. It is
  also the only sentence in §16.4 an executor can copy verbatim, so the letter of the propagation rule is
  satisfiable by an entry that says the detection outcome changed in one of four cells without saying
  which, and without the second half of QC-03's restriction. §24 item 11 does name it ("HCC1395 under V2")
  but nothing routes item 11 into the propagated entry.
Why blocking:
  QC-03 routes explicitly to claim control and says "The evidence summary must say so." The propagation
  block is the only rule that carries the one-of-four-cells restriction out of `results_v1_1/` into the
  project's evidence base. A mandatory verbatim string that does not exist gets improvised, and PH-01
  already established in this document that paraphrase is how a qualifying clause dies.
Required change:
  Write the sentence literally into §16.4 as a fenced, quotable string matching §24 item 11: "The
  detection outcome under the frozen replicate rule changed in exactly ONE of four individual x
  construction cells: HCC1395 under V2. Under V1 on HCC1395 it did not, and on COLO829 neither
  construction changed." Mark it as the string §20.7 and §26 require verbatim, and add it to §22.5's
  normative layout beside the §16.4 table.

### PH8-04
Section: §16.7 (a), §16.7 (b), §20.0, §20.7 RULE 1, §22.5 — all referring to "the evidence summary";
against §22.2 and §22.4
Issue:
  Five binding claim-control obligations are discharged into an artifact the protocol never requires to
  exist. §16.7 (a): the 8.15x enrichment number "may not be omitted from the evidence summary"; §16.7 (b):
  "Required derived columns in the evidence summary: `frac_kept_with_d_eq_1`, `median_t_kept`"; §20.0: the
  v1.0 block must be printed in full "in the evidence summary"; §20.7 RULE 1: "the evidence summary lists
  them all"; §22.5: the v1.0 block is required "in every artifact and in the evidence summary". §22.2's
  `results_v1_1/` tree contains no evidence summary; §26 has no item producing one; §22.4 confines
  EXEC-002 without naming it. It is not a v1.0 artifact either — `results/` contains no such file — and the
  term enters this benchmark from qc_001.md QC-03's routing line.
Why blocking:
  QC-03's routing names the evidence summary as the thing to be constrained, and this draft's answer is to
  attach obligations to it five times without creating it. As written, an executor can complete every §26
  item and produce no artifact carrying the complete applicable-label set, the §16.7 (b) one-call
  diagnostic, or the v1.0 block in the human-readable place a downstream reporter reads. §16.7 (b)'s two
  derived quantities — the share of kept ALT reads whose entire evidence is ONE discordant modification
  call, the mechanism claim's substance — have no defined home at all.
Required change:
  Name the artifact and give it a normative layout: add `results_v1_1/evidence_summary.md` to §22.2's
  tree, specify its required blocks (the §22.5 fenced v1.0 registered-outcome and named-outcome blocks,
  the §16.4 table and cell sentence, the complete `branch_labels_applicable` set with RULE 5 suffixes, the
  §16.3 verdict tally, the §16.6 S3 near-miss block, the §16.7 (a) figure and (b) derived quantities, the
  §18.1 library-of-origin paragraph, and the corrected `WITHDRAWAL_BASIS`), add it to §22.4's
  single-location rule, and add a §26 item. Alternatively delete every reference to "the evidence summary"
  and re-anchor each obligation on `registered_outcome_v1_1.txt` — but §16.7 (b)'s derived columns then
  need a named home regardless.

### Lens 5 minor issues

1. §1's `preregistered_scope_sections` is advertised as machine-readable but is not computable ("§10 (v1.0
   text)", "§24 items 1-10"), and two unqualified entries — §20.1 and §20.2 — contain post hoc normative
   rules (the `_200`/`_2000` split, `leg_a_interval_reading` non-verdict-bearing, `band_admissible_2000`).
   §1.1's catch-all backstops the harm; mark the field non-computable or enumerate the post hoc clauses.
2. §17's carried-over summary reads "decision by pre-specified consistency rule" with no register
   qualifier, although §15.5.8's own correction exists two sections earlier and should be cited at §17.
3. §20.0's machine-readable discharge puts the bare literal `H1 SUPPORTED` on every `retention_sweep.tsv`
   row stating a `zlo_min`, with only `detection_table_ref` beside it — a pointer misnamed for what it
   points at. Rename it, or add `v1_1_mechanism_verdict` as a required column.
4. §20.7 RULE 5 annotates v1.0's preregistered label strings while v1.0's preserved block says "Named
   outcomes, which may not be relabelled"; one sentence in RULE 5 should say the suffix is an annotation
   of register, not a relabelling.
5. §16.4 binds "every human-readable artifact and every summary that states a `zlo_min` result" while
   §20.0 binds "every HUMAN-READABLE artifact that states a v1.1 verdict"; the asymmetry is probably
   intended but unstated, and it is the gap a slide deck falls through.
6. L-G carries a mandatory power-figure annotation and is then declared unreachable under clause 0b; say
   once, in the label block, which labels clause 0b closes (L-A by F11, L-G and L-I by clause 0b) so the
   emitted set is readable.

### Lens 5 supporting record

Recorded as passing, verbatim from the lens: §16.4 reprints the four-cell table verbatim, forbids "any
unqualified sentence of the form 'methylation enables 0.1% detection'" with no escape clause, binds the
evidence summary explicitly, and requires EXEC-002 to compute its own table with differences routed to
F11; §20.7's WITHDRAWAL clause names in advance exactly what withdraws the mechanism half; §20.10 shows
the outcome is not merely reachable but is the protocol's own stated expectation; §20.6 clause 0, §22.5's
fencing and §20.9's declared recalibration are "genuinely strong work". On AGENTS.md rule 3 the draft
complies — every constant enumerated in §1.1, frozen by §20.8 clause 3, and the two permissive
recalibrations declared with their measured operating characteristics; nothing is silent. On rule 8 the
draft repaired its own two iteration-7 violations (§20.5's pre-emptive weighting moved to §24 item 18;
§10.2's inference moved to a labelled interpretation note with the assumption named). No named non-success
outcome is relabelled into partial success anywhere in §20.7 or §21.

---

## Consolidated major-issue index (round 3 — the surviving set)

```text
Lens 1  GR3-MAJ-01  leg (iv)/F12/L-E: max over 7 comparator variants, firing in any of 32 cells, with
                    no selection correction and no measured size outside one cell type
        GR3-MAJ-02  REFUTATION-ELIGIBLE has no construction for the permutation legs, so L-D and L-F
                    are unreachable — SV-01 surviving for legs (ii) and (iii)
        GR3-MAJ-03  no null isolates methylation PATTERN; §10.1 asserts the opposite of §10.2; the
                    reference-side permutation (C5) is computable and not installed

Lens 2  R3-L2-01    BLANK_TRIPLE fires by construction in AXIS-L x V1 and AXIS-B x V2; the consequence
                    clause has no scope, so S6 is either unsatisfiable on all data or carried by rows
                    the protocol calls a re-expression of the QC-01 tie; the deciding figure is absent
                    from the frozen script
        R3-L2-02    §15.5.6 clause (g) mechanically forecloses the F12 firing that F12, §16.7 (c) and
                    §20.4 all promise; §15.5.6 and §15.5.11 disagree on which clauses exclude
        R3-L2-03    enlarging P declared harder in one direction only; the refutation side has no
                    family-wise control across members and no measured size

Lens 3  SV3-01      null_sd named but never operationally defined; the frozen simulation computes it by
                    the forbidden reading
        SV3-02      the 11.7x inflation is UNGATED and from a record FIND-0018 marks superseded; gated
                    figures are 2.65 (uncorrected) and < 1 (EV-0038-corrected)
        SV3-03      S5's refutation direction has no multiplicity control, no operating characteristics
                    and no blank-spread sensitivity, yet L-B1 headlines and propagates
        SV3-04      the size mandated beside L-E and F12 is measured for a one-comparator rule the
                    protocol runs over five

Lens 4  L4-MAJ-01   retention_sweep.tsv is keyed on `ladder_index`, which §15.5.4 names as forbidden
        L4-MAJ-02   the artifact's size and compute are unstated and its two bounding clauses
                    contradict each other with an undefined stride left to the executor
        L4-MAJ-03   §26 reinstates the per-worker leakage expectation §14 deleted as unsatisfiable

Lens 5  PH8-01      WITHDRAWAL_BASIS attributes a post hoc withdrawal to "EXEC-001 plus qc_001.md" and
                    cites qc_001.md for the opposite of what it says — propagated to four project records
        PH8-02      §21's post hoc F9 and F12 emit v1.0's preregistered label string unsuffixed
        PH8-03      the "§16.4 cell sentence" required verbatim by §20.7 and §26 does not exist and does
                    not name the cell
        PH8-04      five binding obligations routed to "the evidence summary", an artifact that is never
                    created, listed or checked
```

---

## The single objection most likely to be raised

> "Your deciding criterion may be unsatisfiable on every possible dataset, and you have not noticed.
> AXIS-L x V1 and AXIS-B x V2 are BLANK_TRIPLE at every evaluable target by your own algebra and your own
> SAMPLE_SD_TOL, and the figure you say settles it is not in the script you froze."

Recorded by lens 2 as R3-L2-01. It is not a request to loosen anything: the panel's required change is to
state the consequence in advance — if S6 cannot HOLD on any data, the protocol must say so before the run
rather than discover it afterwards.

---

## Round-budget outcome

```text
design_iteration   6 -> 7 -> 8   (max_design_iterations 8, reached)
review_iteration   6 -> 7 -> 8   (max_review_iterations 8, reached)
major issues      34 -> 25 -> 17
verdicts       5x REVISE, 5x REVISE, 5x REVISE   (0 REJECT at any round)
```

The ACCEPT rule (zero REVISE, zero REJECT, zero major issues) was not met at any round, and the loop
budget is exhausted. v1.1 remains a DRAFT. `protocols/v1.0_locked.md`, its checksum, its registered
outcome and the whole of EXEC-001 are unchanged, as constraint (d) requires.

Routing: the loop cannot auto-lock and cannot auto-continue. Per AGENTS.md rules 2 and 10 the decision to
extend the budget, to accept v1.1 with the 17 findings recorded as open, or to stop BM-0001 at the v1.0
result plus qc_001.md is a human gate. Returned to `human` with `orchestrator` holding the audit trail.
