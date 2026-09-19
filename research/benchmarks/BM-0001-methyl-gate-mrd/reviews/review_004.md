# Benchmark Review

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v0.4_draft.md` (v0.4, DRAFT)
Reviewer role: grill-me, adversarial methodological review
Review iteration: 4
Date: 2026-08-31

The reviewer did not edit the protocol and did not execute any part of the benchmark.

---

## Verdict

REVISION_REQUIRED

One blocking issue. It is a design issue, not a detail: B001's confounder has returned in a
weaker form, and the reviewer would rather say so at iteration 4 than have it said about a
locked protocol.

---

## Carried-forward check on review_003

```text
B012 pass-count arithmetic   RESOLVED — 14 exploratory, 42 total, runtime asymmetry stated.
B013 empty scorable set      RESOLVED — cut = 1.0, k = 0, propagates to `no estimate`.
N010, N011                   Adopted.
```

---

## Blocking issues

### B014
Category: residual confounding between the treatment and its control
Protocol section: §10 (C1), §20 (S1)
Problem:
  C1 matches B1 on the **rule** — the same 95th percentile over the same scorable set — and the
  protocol treats that as matching aggressiveness. It does not, in effect. Under C1 the scores
  are permuted, so an ALT read is kept with probability equal to the overall retention rate,
  about 5%, in every sample. Under B1 the measured ALT retention on HCC1395 was **26% in the
  blank, 67% at 1% and 37-50% at 0.1%** — five to ten times C1's. ALT reads systematically
  carry higher methylation-disagreement scores than typical reads, in blanks as well as in
  dilutions.

  So B1 and C1 do not count comparable numbers of reads. B1's `G` at 0.1% is of order 22-28 and
  C1's of order 3. Because `z` improves with counting statistics, B1 can beat C1 largely
  because it retains more ALT reads, not because it retains the *right* ones. That is B001's
  confounder — "the filter that keeps more wins" — re-entering through the back door.
Why it matters:
  `zlo_min(B1) > zlo_min(C1)` is one of the three legs of S1 and is the leg that is supposed to
  carry the mechanism claim. If it can be satisfied by aggressiveness, the benchmark's central
  claim is not testable by its central criterion.

  The arithmetic that makes this visible also points at the fix. A filter that kept ALT reads at
  the *same* rate in the blank and in the sample would shrink numerator and denominator together
  and leave `z` roughly unchanged: at HCC1395's numbers, a uniform 30% filter gives
  `(0.3*59 - 0.3*39)/sqrt(0.3*...) ~ 2.5` against the frozen `(59-39)/7.39 = 2.71`. **Only a
  filter whose ALT retention is differential — higher where tumour is present than in the
  blank — can improve `z`.** Differential retention is therefore the mechanism, and it is
  directly measurable, arm by arm, at no extra compute.
Required revision:
  Add a fourth preregistered success condition that tests the mechanism directly rather than
  through `z` alone, and state that it is a necessary condition:

```text
S4 (DIFFERENTIAL RETENTION — the mechanism)
    For B1, on both individuals:
        ALT retention at 0.1%  >  ALT retention at TF0 (blank)
    and the same must NOT hold for C1 beyond sampling noise, where C1's retention is
    level-independent by construction.
    Report the retention ratio  r = retention(0.1%) / retention(TF0)  for all four arms,
    with C1's 5th/95th percentiles across its 200 draws as the noise band.
```

  Additionally, §20 must state that `zlo_min(B1) > zlo_min(C1)` alone does not establish the
  mechanism, and that if S1 holds while S4 fails the registered outcome is
  `MECHANISM UNSUPPORTED` — a named non-success, not a partial success.

  The reviewer notes this costs no extra BAM pass: retention is already required as a secondary
  metric by §16 and as a column by §22. What changes is that it becomes decision-relevant
  instead of descriptive.

---

## Non-blocking issues

### N012
§22 fixes the column schema for `per_sample_metrics.tsv` and names the other result files
without schemas. Every one of them is a deterministic aggregation of `per_sample_metrics.tsv`
under rules that §15, §16 and §20 already fix, so the executor is not being asked to invent
methodology. Recommend nonetheless that `ablation_results.tsv` carry an explicit column set,
since it is the artifact holding the primary comparison and QC will read it first. Not blocking.

### N013
The mechanism argument in B014 above — that a proportional filter cannot improve `z` and only a
differential one can — is worth stating in §15 as the reason the primary metric is capable of
detecting the effect at all. It converts the choice of metric from a convention into an argument.

---

## Gate evaluation

```text
- Research question explicit:                      PASS
- Unit of analysis explicit:                       PASS
- Truth defined:                                   PASS
- Candidate universe defined:                      PASS
- Baseline frozen:                                 PASS
- Treatment arms frozen:                           PASS
- Primary metric frozen:                           PASS
- Statistical plan defined:                        PASS
- Leakage guards defined:                          PASS
- Missingness handling defined:                    PASS
- Success criteria defined:                        FAIL  (B014)
- Failure criteria defined:                        FAIL  (B014 — no named outcome for a
                                                    z-win without a mechanism)
- Low-signal evaluation defined when applicable:   PASS
- No unresolved execution-blocking decisions:      PASS
```

---

## The single objection most likely to be raised

> "Your control kept 5% of the ALT reads and your method kept 40%. Of course yours had the
> better counting statistics."

v0.4 has no answer. S4 is the answer, and it is measurable from artifacts the protocol already
requires.

Routing: return to `benchmark-designer`.
