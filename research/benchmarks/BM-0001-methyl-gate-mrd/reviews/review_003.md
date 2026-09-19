# Benchmark Review

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v0.3_draft.md` (v0.3, DRAFT)
Reviewer role: grill-me, adversarial methodological review
Review iteration: 3
Date: 2026-08-31

The reviewer did not edit the protocol and did not execute any part of the benchmark.

---

## Verdict

REVISION_REQUIRED

Two blocking issues. Both are executable-detail defects rather than design defects: one is an
arithmetic inconsistency in the execution plan, the other is an undefined edge case in the
cutoff rule. The design is otherwise accepted — no methodological objection survives from
review_001 or review_002.

---

## Carried-forward check on review_002

```text
B009 S3 construction      RESOLVED — both constructions, held-out blank's own sample_sd,
                          fails if any of ten detects under either.
B010 C2 tie handling      RESOLVED — top-k with k fixed by n_scorable alone; seeded tie-break;
                          realised retention recorded for all four arms.
B011 exploratory arm      RESOLVED — declared an independent re-run with its own consensus.

N006-N009 all adopted.
```

---

## Blocking issues

### B012
Category: internally inconsistent execution plan
Protocol section: §19, §23
Problem:
  §19 says the exploratory COLO829 chr1 re-run "costs 12 further BAM passes (COLO829's 5 blanks
  and 9 dilutions, minus none)". Five blanks plus nine dilutions is **fourteen**, not twelve.
  §23 then states a total of "40 BAM passes" built on the same wrong 12. The correct totals are
  14 exploratory passes and 42 in all.
Why it matters:
  The executor's precheck compares the planned pass count against what it actually runs, and a
  mismatch is exactly what `protocol_deviations.md` is for. A protocol that is arithmetically
  wrong forces either a spurious deviation record or a silent correction, and silent correction
  of a locked protocol is the failure mode this workflow exists to prevent.
Required revision:
  Correct both figures: 14 exploratory passes, 42 total. While correcting, state the expected
  runtime asymmetry — the exploratory passes cover 241 candidates against the primary passes'
  ~4,000, so they are roughly an order of magnitude cheaper and the wall-clock estimate should
  not be scaled linearly from 42.

### B013
Category: undefined edge case in a frozen rule
Protocol section: §10 (B1 step 6, and by inheritance C1 and C2)
Problem:
  `cut` is defined as `sorted_scores[int(PCT/100 * (len-1))]`. The protocol does not say what
  happens when **no read in a sample is scorable** (`n_scorable = 0`), which makes the index
  expression undefined, nor what `k` means in C2's top-k rule when `n_scorable = 0` (it
  evaluates to `-1`). The frozen reference implementation has a defined behaviour here —
  `cut = 1.0` when the scorable set is empty, which keeps nothing, since the score is bounded
  in [0, 1] and the rule is strict `>`. That behaviour is in the code and not in the protocol.
Why it matters:
  This is reachable. The exploratory arm scores reads overlapping only 241 candidates, and a
  blank replicate there could plausibly yield very few scorable reads. An executor meeting an
  empty scorable set at run time would have to invent a rule with the data in front of it.
Required revision:
  Write the frozen behaviour into the protocol: if `n_scorable = 0` then `cut = 1.0`, `k = 0`,
  no ALT read is kept, `G_arm = 0` and `sample_sd = 0`, which propagates to the already-defined
  `no estimate` verdict of §15. State that this is the reference implementation's behaviour
  being adopted, not a new choice.

---

## Non-blocking issues

### N010
The exploratory chr1 COLO829 arm builds its consensus from reads overlapping 241 candidates
rather than 4,000 — roughly a sixteen-fold smaller read set, and therefore a much smaller set
of positions reaching `MIN_COV = 10`. The arm may be consensus-limited rather than
signal-limited, which is a different thing from what the primary benchmark measures. Recommend
reporting the consensus and confident-position counts for that arm beside its result, and
saying in one line that a small consensus is a candidate explanation for whatever it shows.
Non-blocking: the arm decides nothing in §20.

### N011
§15's justification for choosing 0.1% as the primary level rests on 1% detecting everywhere
and 0.01% being unreachable. That is well sourced. It is worth stating explicitly in §20 that
if 1% or 0.01% behaves unexpectedly in this benchmark, that is a **finding to report**, not a
reason to move the primary level — otherwise the pre-registration is only as strong as the
next person's memory of why it was made.

---

## Gate evaluation

```text
- Research question explicit:                      PASS
- Unit of analysis explicit:                       PASS
- Truth defined:                                   PASS
- Candidate universe defined:                      PASS
- Baseline frozen:                                 PASS
- Treatment arms frozen:                           FAIL  (B013)
- Primary metric frozen:                           PASS
- Statistical plan defined:                        PASS
- Leakage guards defined:                          PASS
- Missingness handling defined:                    PASS
- Success criteria defined:                        PASS
- Failure criteria defined:                        PASS
- Low-signal evaluation defined when applicable:   PASS
- No unresolved execution-blocking decisions:      FAIL  (B012, B013)
```

---

## The single objection most likely to be raised

At this iteration the reviewer could not find a surviving objection to the *design*. The
objection that remains is procedural: a locked protocol containing an arithmetic error and an
undefined edge case will be corrected during execution, and corrections during execution are
indistinguishable, after the fact, from adjustments during execution.

Routing: return to `benchmark-designer`.
