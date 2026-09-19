# Benchmark Review

Benchmark: BM-0001-methyl-gate-mrd
Protocol under review: `protocols/v0.2_draft.md` (v0.2, DRAFT)
Reviewer role: grill-me, adversarial methodological review
Review iteration: 2
Date: 2026-08-31

The reviewer did not edit the protocol and did not execute any part of the benchmark.

---

## Verdict

REVISION_REQUIRED

Three blocking issues remain. All three are of the same kind: an operational choice the
executor would otherwise have to invent at run time, with the data in front of it. None
of them reopens the design; v0.2's substantive answers to B001-B008 are accepted.

---

## Carried-forward check on review_001

```text
B001 degenerate control       RESOLVED — verified. C1 and C2 are matched on the cutoff rule,
                              not on B1's output. Under C1 the retention among ALT reads is
                              ~5% by construction and level-independent, whereas B1's was
                              measured level-dependent (26% blank / 67% at 1% / 37-50% at
                              0.1%). The arms can therefore differ, and B1 > C1 is a real test.
B002 gate ordering            RESOLVED — §10 states it normatively and §26 makes the executor
                              verify the gate-passing set is identical across arms.
B003 variance model           RESOLVED — V1 and V2 both preregistered; SD-MODEL DEPENDENT is
                              a named non-success.
B004 undefined cases          RESOLVED — nan -> "no estimate" -> failure to demonstrate.
B005 control aggregation      RESOLVED — draw = complete re-run including blanks; median of
                              200 per-draw zlo_min, with 5th/95th percentiles.
B006 blank replicates         RESOLVED — five blanks executed, rep1-3 primary, S3 leave-one-out.
B007 UNRELIABLE mapping       RESOLVED — only `detected` is a positive prediction.
B008 prose vs implementation  RESOLVED — mrdz.score named normative and checksummed.
```

Non-blocking N001-N005 all adopted.

---

## Blocking issues

### B009
Category: undefined evaluation detail
Protocol section: §20 (S3)
Problem:
  S3 says B1 must return `detected` on none of the ten leave-one-out blanks. It does not say
  under which variance construction, and V1 and V2 give different `sample_sd` and therefore
  different verdicts. It also does not say what `sample_sd` means for a blank being scored —
  the blank's own plug-in binomial sd, presumably, but "presumably" is what this workflow
  forbids.
Why it matters:
  S3 is one of three gates deciding whether H1 is supported. FIND-0018 established that these
  two constructions can disagree about a detection. An executor choosing one at run time would
  be choosing a gate outcome with the data visible.
Required revision:
  State that S3 is evaluated under **both** constructions, that the held-out blank's own
  `sample_sd` is used exactly as for any evaluated sample, and that S3 fails if **any** of the
  ten blanks returns `detected` under **either** construction.

### B010
Category: undefined behaviour that changes the control's aggressiveness
Protocol section: §10 (C2)
Problem:
  `score_C2` is the count of confident positions on a read — an **integer** with heavy ties.
  The frozen rule `keep iff score > cut`, where `cut` is the indexed percentile, was written
  for the continuous `score_B1`, where ties are negligible. On an integer score with a large
  tie mass at the percentile value, `> cut` can retain far more or far less than the nominal
  5%. C2's whole purpose is to be an **equally aggressive** filter; a tie-dependent retention
  rate destroys that.
Why it matters:
  If C2 accidentally retains 15% of reads, it is a weaker filter than B1 and losing to B1
  proves nothing. If it retains 1%, it is a stronger filter and beating B1 proves nothing.
  Either way the control stops controlling, which is the same class of defect as B001.
Required revision:
  Define C2 by an explicit top-k rule whose k depends only on the number of scorable reads:
  `k = n_scorable - 1 - floor(PCT/100 * (n_scorable - 1))`, i.e. exactly the number of reads
  the percentile index leaves strictly above the cut position. Keep the k highest `score_C2`
  reads, ties broken by a seeded random permutation of the tied block, seed recorded. State
  that B1 and C1 keep the frozen `> cut` rule unchanged, and record all three arms' realised
  retention so the matching is auditable rather than assumed.

### B011
Category: ambiguous derivation of a reported arm
Protocol section: §19 (exploratory COLO829 chr1 arm)
Problem:
  The protocol does not say whether the chr1-restricted COLO829 arm is a **subset of the same
  BAM pass** (restricting the candidate set at scoring time, so the consensus, the confident
  positions and the cutoff are still built from all 4,000 candidates' reads) or an
  **independent re-run** on 241 candidates (so the consensus is built from a 16x smaller read
  set). These are different methods and would give different numbers.
Why it matters:
  It is labelled EXPLORATORY and decides nothing in §20, but it will be reported next to the
  primary numbers, and an unlabelled methodological difference between adjacent numbers is how
  a reader is misled.
Required revision:
  State which. The reviewer notes without prescribing that a re-run is the more honest analogue
  of HCC1395's chr1-only frame, and that a subset is the cheaper one; either is defensible if
  declared.

---

## Non-blocking issues

### N006
The dilution material's provenance says the mixtures are "samtools subsampling of
deduplicated tumor and normal". EV-0038 measured that one HCC1395 library, `ONT_5khz`, carries
**duplicated primary reads at a ratio of 2.000**, and that duplication moves sites across the
gate's 1-to-2 ceiling — the exact quantity this benchmark scores. The word "deduplicated"
in the provenance is a claim in a YAML file, not a verified property of these 28 BAMs.
Recommend the executor capture each BAM's `@PG` chain into the manifest and report the
duplicate-flag rate it observes, so the claim is checkable. Non-blocking because any
duplication affects B0 and B1 identically within an individual and cannot explain a
between-arm difference.

### N007
A read spanning two candidates contributes to both, in every arm. This is inherited from the
frozen metric and is not a defect of this benchmark, but it means the gated total is a count
of read-observations rather than of molecules. Recommend saying so once in §24 so the
statistic is not read as a molecule count.

### N008
§16 requires retention to be reported. Recommend making it explicit that retention is reported
for **all four arms**, since the credibility of B1 > C1 and B1 > C2 rests on the reader being
able to see how aggressive each filter actually was.

### N009
The 200-draw C1 arm multiplies the reported numbers by 200 internally but collapses to three
percentiles. Recommend also persisting the full per-draw `zlo_min` vector to
`results/` so QC can check the median is not an artefact of a bimodal draw distribution.

---

## Gate evaluation

```text
- Research question explicit:                      PASS
- Unit of analysis explicit:                       PASS
- Truth defined:                                   PASS
- Candidate universe defined:                      PASS
- Baseline frozen:                                 PASS
- Treatment arms frozen:                           FAIL  (B010)
- Primary metric frozen:                           PASS
- Statistical plan defined:                        PASS
- Leakage guards defined:                          PASS
- Missingness handling defined:                    PASS
- Success criteria defined:                        FAIL  (B009)
- Failure criteria defined:                        PASS
- Low-signal evaluation defined when applicable:   FAIL  (B011)
- No unresolved execution-blocking decisions:      FAIL  (B009, B010, B011)
```

---

## The single objection most likely to be raised

> "Your control filter and your treatment filter did not keep the same number of reads, so
> which one is stricter is doing the work."

v0.2 answers this for C1 by construction and fails to answer it for C2, because an integer
score with ties does not obey the cutoff rule the protocol assumes. B010 is that objection.

Routing: return to `benchmark-designer`.
