# Benchmark Review

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v0.1_draft.md` (v0.1, DRAFT)
Reviewer role: grill-me, adversarial methodological review
Review iteration: 1
Date: 2026-08-31

The reviewer did not edit the protocol and did not execute any part of the benchmark.
Sources inspected: the protocol; `research/decisions/2026-08-25-metric-and-baseline.md`;
`research/findings/FIND-0018.md`, `FIND-0019.md`, `FIND-0021.md`;
`research/surveys/long-read-tumor-only-mrd/exp-s1-022/scripts/05_mrd_detection.py`
and its results; `exp-s1-002/results/counts_TF0.tsv`; `exp-s1-007/results/counts_TF0.tsv`;
directory listings of the dilution BAMs.

---

## Verdict

REVISION_REQUIRED

Six blocking issues. One of them (B001) makes the protocol's central control
**arithmetically incapable of ever discriminating**, which would have produced a
benchmark that could not fail. That is the failure this review exists to catch.

---

## Blocking issues

### B001
Category: invalid control — degenerate by construction
Protocol section: §10 (arm C1), §20 (S1)
Problem:
  C1 is defined as "draw `k` of those `n` uniformly at random", where `k` is the number of
  ALT reads B1 kept. The primary statistic `G` is a **count of kept ALT reads**, gated on the
  original ALT count. Therefore `G_C1 = k = G_B1` exactly, in every sample, by construction.
  C1's z equals B1's z identically. The criterion `zlo_min(B1) > zlo_min(C1)` can never be
  satisfied and can never be violated; it is `x > x`.
Why it matters:
  The retention-rate confounder is the single most plausible alternative explanation for the
  prior HCC1395 result — the blank fell 39 -> 10 and z rose, and shrinking the blank raises z
  under *any* filter. The protocol names that confounder correctly and then installs a control
  that cannot test it. Executed as written, the benchmark would report a tie against its own
  control and the orchestrator would have to interpret a tautology.
Required revision:
  Redefine the control so it is matched on **filter aggressiveness**, not on the outcome.
  The natural matching is the cutoff rule itself: replace the methylation-disagreement score
  `d` with a null score drawn from the same score distribution, and apply the identical
  95th-percentile cutoff. Retention then follows from the rule rather than being copied from
  B1's answer, and B1's level-dependent retention (26% in blank, 67% at 1%, 37-50% at 0.1%
  in the prior HCC1395 run) becomes a testable claim rather than an assumption.

### B002
Category: undefined operational detail the executor would have to invent
Protocol section: §9, §10
Problem:
  The protocol never says whether the gate `1 <= alt <= 2` is applied to the ALT count
  **before** filtering or to the filtered count. The two give different candidate universes:
  applied after filtering, B1 would gate on a quantity B0 does not have, and the arms would
  no longer share a candidate universe — which §8 and §12 both promise they do.
Why it matters:
  This is exactly the "same candidate universe" requirement. Getting it wrong converts an
  evidence ablation into a comparison of two different candidate sets, and the protocol's
  own attribution argument collapses.
Required revision:
  State explicitly that the gate is evaluated on the **unfiltered** ALT count in every arm,
  so the set of gate-passing candidates is identical across B0, B1 and all controls, and only
  the number of reads counted at those candidates differs.

### B003
Category: unjustified statistical procedure / metric may be dominated by estimation noise
Protocol section: §15
Problem:
  The primary metric divides by `sd_blank_arm`, the standard deviation of three blank
  replicates. In B1 the blank statistic is roughly an order of magnitude smaller than in B0
  (39 -> 10 in the prior HCC1395 run, blanks 10 / 8 / 8). A standard deviation estimated from
  three small counts has 2 degrees of freedom and is extremely noisy; the interval propagates
  the uncertainty of the blank **mean** but treats that noisy sd as if it were known. B1 can
  therefore beat B0 on the primary metric purely because its sd estimate happened to come out
  small. The protocol offers no defence against this.
Why it matters:
  The whole benchmark turns on one scalar. If that scalar is dominated by a 2-df variance
  estimate, a positive result is uninterpretable and a negative one is not credited either.
Required revision:
  Require the primary criterion to hold under **both** blank-variance constructions,
  preregistered together: (a) the empirical sd over the three blank replicates, and
  (b) the frozen metric's original Poisson sd, `sqrt(mean_blank)`. Report both. If S1 holds
  under one and not the other, the registered outcome is `SD-MODEL DEPENDENT`, which is a
  named non-success, not a partial success.

### B004
Category: undefined behaviour / possible division by zero
Protocol section: §15
Problem:
  With three blank replicates and small counts, `sd_blank_arm = 0` is a live possibility
  (blanks of 8 / 8 / 8 are entirely plausible under B1). The protocol does not say what z is
  in that case. An executor would have to invent a rule, and every available invention
  (infinity, a floor, a fallback) changes the answer.
Why it matters:
  It would be invented at execution time, after the data exist — the precise thing the
  workflow forbids.
Required revision:
  Define it a priori: if `sd_blank_arm = 0`, the empirical-sd z for that arm is `UNDEFINED`,
  reported as such, and counts as a failure to demonstrate for S1 under construction (a);
  the Poisson construction (b) required by B003 remains defined whenever `mean_blank > 0`.
  Also define the case `mean_blank = 0`: both constructions are `UNDEFINED` and S1 fails.

### B005
Category: aggregation rule undefined for the control arms
Protocol section: §10 (C1, C2), §15
Problem:
  The controls are repeated (200 and 20 draws) and the protocol says the statistic is "the
  mean over draws". The mean of *what* is not specified — of `G`, of `z`, or of `zlo_min`.
  These are not interchangeable: `z` is a nonlinear function of the blank statistics, which
  are themselves redrawn in each replicate of the control.
Why it matters:
  Different choices can reverse the comparison. The executor cannot pick one without making a
  methodological decision.
Required revision:
  Specify that each draw is a **complete re-run of the arm**, blank samples included, using the
  same draw index and seed across all samples of an individual, producing one `zlo_min` per
  draw; the control's reported statistic is the **median** of those per-draw `zlo_min` values,
  with the 5th and 95th percentiles reported. Use the median so a single degenerate draw
  (e.g. a zero blank sd) cannot move the control's summary.

### B006
Category: insufficient control data for a preregistered criterion
Protocol section: §20 (S3)
Problem:
  S3 scores each TF0 replicate against the mean of the other two. With three blanks that
  leaves two reference points — a mean on 2 observations and a standard deviation on 1 degree
  of freedom. The resulting z is not a quantity a criterion can be built on, and S3 would be
  decided by noise. Two further blank replicates (`TF0_25x.rep4.bam`, `rep5.bam`) exist for
  **both** individuals and are simply not used.
Why it matters:
  S3 is one of the three gates that decide whether H1 is supported. A gate decided by noise
  is not a gate. Leaving available blank replicates unread is also a silent narrowing of the
  evidence, which the workflow forbids.
Required revision:
  Execute all five TF0 replicates per individual. Keep rep1-3 as the primary blank reference
  so the construction stays identical to the frozen `§4c` procedure, and run S3 as
  leave-one-out over all five (each blank scored against the mean and sd of the other four).
  Record the extra passes as part of the plan, not as a deviation.

### B007
Category: undefined label mapping for a required artifact
Protocol section: §22 (`error_analysis.tsv`)
Problem:
  The artifact requires `TP / TN / FP / FN` per sample, but the arms emit a **three-way**
  verdict (`detected` / `UNRELIABLE` / `not detected`). The protocol never says how
  `UNRELIABLE` maps onto the two-way confusion table.
Why it matters:
  Mapping `UNRELIABLE` to positive versus negative changes the reported sensitivity of every
  arm. It would be chosen at execution time with the results visible.
Required revision:
  Fix a priori: only `detected` counts as a positive prediction; `UNRELIABLE` and
  `not detected` both count as negative predictions for the confusion table, and the
  three-way verdict is carried in its own column so nothing is lost. State that this makes
  the confusion table conservative for every arm equally.

---

## Non-blocking issues

### N001
The name "methylation-shuffled control" (C2) does not describe what §10 specifies. Permuting
per-read call vectors also changes the consensus, so C2 as written perturbs the reference and
the reads together and its null is not clean. A sharper null preserves the consensus and the
score distribution exactly and destroys only the read-to-score correspondence. Recommend
renaming and respecifying; not blocking because the arm is a control rather than the baseline.

### N002
A second, genuinely different control is available at no extra I/O and would answer an
objection the protocol does not currently address: FIND-0021 measured that per-read AUC rises
with modification-call count per read (0.586 / 0.621 / 0.675 by CpG-count bucket). If B1 is
in effect selecting reads that carry many CpGs, the channel doing the work is read composition
rather than methylation pattern. Recommend a CpG-density control scored on confident-position
count under the identical cutoff rule.

### N003
HCC1395's frame is chr1-only (3,925 candidates) and COLO829's is genome-wide (4,000
candidates, of which 241 are on chr1). The protocol correctly refuses to compare magnitudes
across individuals. Recommend additionally reporting a chr1-restricted COLO829 arm as
`EXPLORATORY — NOT PRIMARY BENCHMARK`, so the scope difference is visible rather than argued.

### N004
§24 item 6 asserts that the oracle-free premise holds at 1% because the sample is still >= 99%
normal. That is an argument, not a measurement, and U1 already concedes it. Recommend labelling
the 1% row explicitly in the results tables rather than only in the limitations section.

### N005
`statistical_tests.tsv` will contain no test. Recommend it record the *reason* in a column
rather than being an empty file, so QC can verify the absence was deliberate.

---

## Gate evaluation

```text
- Research question explicit:                      PASS
- Unit of analysis explicit:                       PASS
- Truth defined:                                   PASS
- Candidate universe defined:                      PASS
- Baseline frozen:                                 PASS
- Treatment arms frozen:                           FAIL  (B001, B002, B005)
- Primary metric frozen:                           FAIL  (B003, B004)
- Statistical plan defined:                        FAIL  (B003, B005)
- Leakage guards defined:                          PASS
- Missingness handling defined:                    PASS
- Success criteria defined:                        FAIL  (B001 makes S1 partly tautological; B006)
- Failure criteria defined:                        FAIL  (F2 is untestable while B001 stands)
- Low-signal evaluation defined when applicable:   PASS
- No unresolved execution-blocking decisions:      FAIL  (B002, B004, B005, B007)
```

---

## The single objection most likely to be raised

> "The blank got smaller, so of course z went up. What did you compare that against?"

Under v0.1 the answer is a control that is arithmetically identical to the treatment. Until
B001 is fixed, the benchmark has no answer to the one question its result will be attacked on.

Routing: return to `benchmark-designer`.

---

## Addendum — reviewer correction, same iteration

Recorded rather than edited away, because the workflow keeps its own errors.

After writing B003 and B004 the reviewer read the frozen implementation
(`mrd/tools/mrdz/mrdz/score.py`, `blank_spread` / `z_interval` / `interval_verdict`) and the
script that produced the prior D4 result (`exp-s1-022/scripts/08_d4_intervals.py`). **The
z denominator in the frozen procedure is not the blank standard deviation.** It is the
plug-in binomial standard deviation computed on the sample under test:

```text
z    = ( G_sample - mean(blank replicates) ) / sample_sd
half = t_{n} * ( sd(blank replicates) / sqrt(n) ) / sample_sd
sample_sd = sqrt( sum over gate-passing candidates of  depth * p * (1-p) ),  p = a/depth
```

Verified arithmetically against the recorded D4 output: blanks [39, 35, 31] give mean 35.0 and
sd 4.00; the reported 0.1% rep1 interval half-width of 1.345 implies `sample_sd = 7.388`, and
`35.0 + 3.25 * 7.388 = 59.0`, which is exactly the gated total step 5 recorded for that sample.

Consequences for this review:

- **B003 stands, with its reasoning replaced.** The blank sd does not enter the denominator,
  so the "2-df sd in the denominator" argument is withdrawn. What remains is a real and
  separate ambiguity: `research/decisions/2026-08-25-metric-and-baseline.md` §1 defines
  `z = (G - G_blank)/sqrt(G_blank)` (Poisson), while the frozen `mrdz` implementation and the
  §4c reporting use the plug-in binomial `sample_sd`. FIND-0017 changed one to the other and
  FIND-0018 then showed the baseline's detection is **model-dependent** across exactly these
  variance models. A benchmark that picks one silently is picking the one that suits it. The
  required revision is unchanged in substance: preregister both, require S1 under both, and
  name `SD-MODEL DEPENDENT` as a non-success outcome.
- **B004 stands, with its trigger corrected.** The division-by-zero risk is `sample_sd = 0`,
  not `sd_blank = 0`, and it is reachable — an arm whose kept ALT count is zero at every
  gate-passing candidate has `p = 0` everywhere and `sample_sd = 0`. This is a live case for
  B1 at 0.01%. The frozen implementation already returns `nan` and the verdict
  `no estimate`; the protocol must adopt that behaviour explicitly rather than leave it to
  the executor.
- **B006 is strengthened, not weakened.** Because the blank replicates set the interval
  width through `sd(blanks)/sqrt(n)`, adding rep4 and rep5 narrows every interval in the
  benchmark and makes the three-way verdict less often `UNRELIABLE`. That is a change in
  power, so it must be preregistered rather than discovered — reinforcing the requirement
  that rep1-3 remain the primary reference and the five-blank use be declared in advance.

Additional required revision arising from the correction:

### B008
Category: implementation ambiguity in a frozen procedure
Protocol section: §15, §22
Problem: the protocol describes the interval in prose. Prose has already produced one
  misreading inside this review.
Required revision: the protocol must name the frozen implementation
  (`mrdz.score.blank_spread`, `z_interval`, `interval_verdict`, call threshold 3.0) as the
  normative definition, require the executor to import and call it rather than reimplement
  it, and record the module's SHA-256 in the execution manifest.

Verdict unchanged: REVISION_REQUIRED. Blocking issues now B001-B008.
