# Benchmark Review

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v0.5_draft.md` (v0.5, DRAFT)
Reviewer role: grill-me, adversarial methodological review
Review iteration: 5
Date: 2026-08-31

The reviewer did not edit the protocol and did not execute any part of the benchmark.

---

## Verdict

REVIEW_PASS

Zero blocking issues.

---

## Carried-forward check

```text
review_001  B001 degenerate control          RESOLVED (v0.2)
            B002 gate ordering               RESOLVED (v0.2)
            B003 variance model chosen silently  RESOLVED (v0.2)
            B004 undefined sample_sd = 0     RESOLVED (v0.2)
            B005 control aggregation         RESOLVED (v0.2)
            B006 S3 on two reference blanks  RESOLVED (v0.2)
            B007 UNRELIABLE unmapped         RESOLVED (v0.2)
            B008 prose vs implementation     RESOLVED (v0.2)
review_002  B009 S3 construction             RESOLVED (v0.3)
            B010 C2 tie-dependent retention  RESOLVED (v0.3)
            B011 exploratory arm derivation  RESOLVED (v0.3)
review_003  B012 pass-count arithmetic       RESOLVED (v0.4)
            B013 empty scorable set          RESOLVED (v0.4)
review_004  B014 aggressiveness confound     RESOLVED (v0.5)

Non-blocking N001-N013                       ALL ADOPTED
Unresolved review findings deleted           NONE
```

The reviewer's own error in review_001 (attributing the z denominator to the blank standard
deviation) is preserved in that file's addendum with the correction beside it, not edited away.

---

## Verification performed at this iteration

Checked directly against `protocols/v0.5_draft.md`:

- `unit_of_analysis: sample` present and argued (§5).
- Truth source and matching rule present, and the truth is sample-level provenance only (§7).
- Candidate universe frozen per individual with source file, count, scope and draw seed (§8);
  executor required to checksum both frames.
- Baseline defined operationally, not by name (§9).
- Four arms, one BAM pass, gate on the unfiltered ALT count, gate-passing set identical across
  arms by construction (§10).
- Primary metric single, with both variance constructions preregistered, undefined cases fixed
  a priori, and the normative implementation named and to be checksummed (§15).
- Statistical plan defines no test and says why, so no test can be selected later (§17).
- Leakage guards give a prevention rule and a verification route per path (§14).
- Missingness handled and, more importantly, made non-confounding — B1, C1 and C2 share one
  scorable set (§12).
- All three dilution levels required separately; 0.01% explicitly may not be dropped, and a
  detection there is named in advance as a suspicion of defect rather than a success (§19).
- Success criteria S1-S4 and failure criteria F1-F8, with every partial outcome given a name
  that is not "partial success" (§20, §21).
- Unresolved decisions U1-U3, none marked `Must resolve before execution: YES` (§25).

Arithmetic re-checked: 28 primary passes (2 individuals x [5 blanks + 3 x 3 dilutions]) and 14
exploratory passes (COLO829's 5 blanks + 9 dilutions) give 42. Consistent in §19 and §23.

---

## Falsifiability check

The reviewer's standing first question is "what would this look like if it were false?", and
v0.5 answers it in four distinct ways rather than one:

```text
methylation adds nothing                     -> F1, zlo_min(B1) <= zlo_min(B0)
the gain is filter aggressiveness            -> F2 / F7, C1 leg and S4
the gain is CpG density, not methylation     -> F3, C2 leg
the gain is HCC1395-specific                 -> F4, and FIND-0021 makes this a live outcome
the gain depends on the variance model       -> F6
B1 manufactures detections in blanks         -> F5
```

Prior evidence makes at least two of these genuinely possible: FIND-0021's COLO829 replication
failed both of its registered thresholds at the read-classification task, and FIND-0018 showed
the baseline's detection is variance-model dependent. This benchmark can lose.

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
- Success criteria defined:                        PASS
- Failure criteria defined:                        PASS
- Low-signal evaluation defined when applicable:   PASS
- No unresolved execution-blocking decisions:      PASS
```

---

## The single objection most likely to be raised, and whether it has an answer

> "Two cell lines. That is not a replication study, it is an anecdote and its repeat."

**It has no answer within this benchmark, and the protocol does not pretend otherwise.** §24
items 1, 2, 4 and 5 state it, §20 names `NOT REPLICATED` as the outcome if the second
individual disagrees, and `research/THESIS-PLAN.md` §5 already identifies more independent
individuals as the deciding experiment for a related question. This benchmark measures what two
individuals can measure and says so. That is a scope limit correctly declared, not a defect
this review can require to be fixed.

Routing: the protocol satisfies every lock gate. Return to `orchestrator` for AUTO LOCK.
