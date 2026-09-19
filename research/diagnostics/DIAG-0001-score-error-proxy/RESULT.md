# DIAG-0001 — result

Registered `PREREGISTRATION.md` sha256 `e204a937d023c5760f234bc0603427f6d8532eda194e1553b1e16116a55f23d8`
at 2026-09-19T22:47:06+08:00. Script `diag_pass.py` sha256 `82d0bb56…`. Both frozen before any
number below existed.

## Reproduction check — PASS

The registration made this gating: miss any of five recorded EXEC-001 values and the diagnostic is
void. An independent reimplementation reading **CRAM** (EXEC-001 read BAM) returned:

| quantity | EXEC-001 | DIAG-0001 |
|---|---|---|
| `n_consensus_positions` | 1,153,835 | 1,153,835 |
| `n_confident_positions` | 353,719 | 353,719 |
| `n_scorable_reads` | 58,990 | 58,990 |
| `K_B1` | 2,895 | 2,895 |
| `cut` | 0.07692307692307693 | 0.07692307692307693 |

Exact on all five. This also settles the open question EV-0052 left: the CRAM conversion reproduces
the BAM results bit-for-bit through the full scoring path.

## The registered predictions

```text
P1  rho(score_b1, nm_rate)   TF0 +0.1133   0.1%  +0.1137
      registered: >=0.30 ERROR-DOMINATED | <=0.10 NOT | between = PARTIAL
      -> PARTIAL, at both levels, and near-identical across tumour fraction

P2  blank, median nm_rate kept vs unkept gated-ALT reads
      0.0821 / 0.0153 = 5.35x, Mann-Whitney p=0.009, n=9 vs 15   -> HELD
      at 0.1%: 0.0232 / 0.0118 = 1.96x, p=0.076                  -> weaker, not significant

P3  nm_rate-only top-5% filter, ALT retention among gated-ALT reads
      TF0 :  37.5%  against B1's 37.5%   -> registered threshold (>=20%) CLEARED, at 100% of B1
      0.1%:  16.7%  against B1's 47.6%   -> NOT cleared

P4  contrast: rho is the same at both levels (+0.1133 / +0.1137), as a pure error proxy would be.
      P3 retention is NOT: error-only falls 37.5% -> 16.7% while B1 rises 37.5% -> 47.6%.
```

**Registered outcome: MIXED.** `ERROR-DOMINATED` needs P1>=0.30 *and* P3>=20%; P1 is 0.113.
`NOT ERROR-DOMINATED` needs P1<=0.10 *and* P3<20%; P1 is 0.113. Neither fires, so per the
registration this is "reported as measured, no verdict".

Independently, the review panel judged both of those labels unsupportable before any number was
read, because `NM` is blind to modification-call error — which, given EV-0054, is exactly the
channel `d` counts. The numbers above are therefore reported as **descriptive measurements of a
basecall-error channel**, not as a verdict on the mechanism.

## The set-overlap check the panel asked for, which P3 did not specify

P3 compares retention *rates*. Equal rates can come from different reads. Measured:

| | B1 keeps | error-only keeps | same reads | Jaccard |
|---|---|---|---|---|
| TF0 (blank) | 9 | 9 | **5** | 0.385 |
| TF 0.1% | 20 | 7 | 4 | 0.174 |

So in the blank the error-only filter matches B1's retention **exactly in magnitude** (9 of 24,
37.5% both) while agreeing on only **5 of 9** reads. Rate equality was not set equality, and P3
alone would have overstated the case.

## What the numbers support

1. **The blank confound is real at the operating point.** In a sample with no tumour, a filter that
   knows only per-read alignment error reproduces B1's gated-ALT retention exactly — 37.5% against
   37.5%, a 7.6x enrichment over the 4.91% global keep rate. Whatever B1 selects in the blank,
   error rate alone reaches the same amount of it.
2. **B1 is not simply that filter.** Only 56% of its kept blank reads are the error filter's, and
   at 0.1% B1 retains 47.6% where error-only reaches 16.7%.
3. **The strongest single correlate of `score_b1` is not error rate.** It is `n_conf`, the number of
   confident positions the read spans — rho +0.266 against nm_rate's +0.113. `n_conf` is precisely
   `score_c2`, the CpG-density control. That is QC-01's finding arriving by a second route: the
   score is more coupled to CpG density than to error.
4. Read with EV-0054, `score_b1` is a one-sided hypermethylation-call rate whose largest measured
   correlate is how many confident CpGs a read spans.

## What these numbers do not support

- Any statement about H1. This measures a property of the score, never a detection outcome.
- Any claim that the blank confound explains the 0.1% result. It does not: B1 clearly exceeds the
  error-only filter there.
- Any claim that error is *not* involved. P2 in the blank is a 5.35-fold median difference at
  p=0.009, and P1 sits above the registered null band at both levels.
- Precision. The gated-ALT populations are 24 and 42 reads; the kept subsets are 9 and 20. Every
  percentage above is a small-count statistic and none should be quoted beyond two figures.
- Generality. One individual, one replicate per level, chr1 only. COLO829 was not run.

## Correction carried from the review

The registration quotes B1's blank ALT retention as 40.0%. That figure counts ALT *occurrences*
(25), as EXEC-001 does; this diagnostic builds a read **set** (24 unique, one read being ALT at two
gate-passing candidates). Under set semantics the reference is 37.5%, which is what is used above.
The registration is left unedited with this noted here.
