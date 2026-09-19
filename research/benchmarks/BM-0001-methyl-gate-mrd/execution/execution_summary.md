# Execution Summary

## Benchmark

```yaml
benchmark_id: BM-0001-methyl-gate-mrd
protocol_version: "1.0"
protocol_checksum: "sha256:9c615da4af068a5330bb512942810c9f2229aa2348554cddcfc130021e200b8c"
execution_id: EXEC-001
status: READY_FOR_QC
```

## Data executed

28 primary BAM passes: HCC1395 and COLO829, five TF0 blanks and three replicates each at 1%,
0.1% and 0.01%. All three dilution levels executed and reported; none dropped. 14 exploratory
COLO829 chr1 passes also executed.

All inputs GRCh38_no_alt_analysis_set, all indexed, all read-only. Candidate frames frozen and
checksummed: HCC1395 3,925 chr1 candidates, COLO829 4,000 genome-wide candidates.

## Arms executed

B0, B1, C1 (200 draws), C2 — all four from a single BAM pass per sample, both variance
constructions V1 and V2. The gate-passing candidate set is identical across arms by
construction, as protocol §10 requires.

## Implementation validation

`run_sample.py` reproduces `EXP-S1-022` step 5 on HCC1395 TF0 rep1 exactly: consensus 1,153,835,
confident 353,719, cut 0.0769, gated 39, kept 10, unscorable 2,217. The primary metric also
reproduces the prior `EXP-S1-022` step 8 D4 interval exactly — B0 `zlo_min` at 0.1% is +0.7396
against the recorded +0.74, and B1's is +2.2995 against the recorded +2.30.

## Primary metric produced

`zlo_min` at 0.1%, both constructions, both individuals, all four arms. See
`results/ablation_results.tsv`.

## Preregistered criteria, applied mechanically

```text
S1 HELD   S2 HELD   S3 HELD   S4 HELD
REGISTERED_OUTCOME: H1 SUPPORTED
```

The executor makes no interpretation of this. Two observations are recorded for QC because they
are properties of the output rather than readings of it:

1. B1 retains 36% (HCC1395) and 9.2% (COLO829) of blank scorable ALT reads against C1's 4.6%
   and 4.1% and C2's 3.8% and 2.1%. B1's `G` at 0.1% is 22-28 and 9-19 reads; C1's is 1-3 and
   2-3; C2's is 2-3 and 2-7.
2. C2's retention ratio is 1.6839 and 2.9041 against B1's 1.6741 and 2.9127.

## Required artifacts

27 of 27 present and non-empty (`results/artifact_manifest.tsv`).

## Failed steps

None. All 41 dispatched jobs exited 0.

## Protocol deviations

Five recorded in `execution/protocol_deviations.md`. All carry `Methodology changed: NO`.

## Reproducibility information

`execution/execution_manifest.yaml`, `execution/environment.txt`,
`execution/random_seeds.yaml`, `execution/execution_log.md`, `execution/inputs_manifest.tsv`,
`execution/files_opened.txt`. Determinism: DETERMINISTIC; both stochastic components are seeded
from fixed strings.

## Blocking issues for QC

None blocking. Three items flagged for QC attention:

- the count-scale asymmetry between B1 and its controls (observation 1 above)
- the near-identity of B1's and C2's retention ratios (observation 2 above)
- the exploratory arm is degenerate — every blank yields zero kept ALT reads, so `sample_sd = 0`
  and the verdict is `no estimate`, the case protocol §15 defines a priori and review_003 N010
  predicted. It decides nothing in §20.

---

```text
HANDOFF_STATUS: READY_FOR_QC

Next role:
QC / Statistical Reviewer
```
