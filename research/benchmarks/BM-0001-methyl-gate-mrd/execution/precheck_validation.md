# EXEC-001 — implementation validation against the prior recorded result

Protocol v1.0 §26 requires the executor to verify that it implements the locked methodology
rather than a variant of it. The check available here is strong: `EXP-S1-022` step 5 ran the
same B0 and B1 computation on HCC1395 TF0 rep1 with the same frozen constants, and its output
is on disk at
`research/surveys/long-read-tumor-only-mrd/exp-s1-022/results/EXP-S1-022-step5.txt`.

This benchmark's `run_sample.py` was run on that BAM before the batch was trusted.

| quantity | this execution | prior recorded | match |
|---|---|---|---|
| consensus positions | 1,153,835 | 1,153,835 | exact |
| confident positions | 353,719 | 353,719 | exact |
| cutoff | 0.0769 | 0.0769 | exact |
| gated ALT total (B0 `G`) | 39 | 39 | exact |
| kept ALT total (B1 `G`) | 10 | 10 | exact |
| retention | 26% | 26% | exact |
| unscorable ALT reads | 2,217 | 2,217 | exact |

Additional quantities this benchmark records that the prior run did not:

```text
gate-passing candidates      30
reads touched                73,124
scorable reads               58,990
K_B1 (reads above the cut)   2,895  = 4.91% of scorable
k_C2 (top-k, protocol §10)   2,950  = 5.00% of scorable
duplicate-flagged reads      0
```

Two things follow.

1. **The implementation is the locked one.** Every quantity the prior run reported is
   reproduced exactly, so the pileup, the quality filters, the consensus construction, the
   confident-position band, the scorability rule and the percentile cutoff are all the frozen
   ones.
2. **C2's aggressiveness matches B1's by construction, as protocol §10 requires.** `K_B1` is
   4.91% of the scorable reads and `k_C2` is 5.00%. Review_002's B010 — that an integer score
   with ties would make C2 an unmatched filter under the `> cut` rule — is confirmed as having
   been a real risk and confirmed as closed by the top-k rule that replaced it.

The duplicate-flag count of 0 is recorded per review_002 N006. It is consistent with the `@PG`
chain, which shows the mixtures built from `/bip8_disk/pingting114/dedup_source_v2/` sources;
it is not by itself proof of deduplication, because a name-based dedup does not set the flag.
What the chain does show is that a dedup step exists and that each replicate carries its own
`samtools view -s <seed>.<fraction>` subsample record.
