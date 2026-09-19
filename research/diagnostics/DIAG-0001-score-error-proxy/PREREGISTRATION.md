# DIAG-0001 — Is `score_b1` substantially a per-read error-rate proxy?

**Registered BEFORE execution. Written 2026-09-19. No number from this diagnostic existed when
this file was hashed.**

This is a **diagnostic**, not a benchmark arm and not a registered protocol experiment. It does
not change BM-0001's hypothesis, metric, gate or criteria, and it cannot on its own support or
refute H1. It exists to tell the human gate whether the confound three design rounds failed to
design around is real, before a fourth round is attempted.

## Why

BM-0001's treatment arm scores a read by

```python
score_b1[name] = d / t          # run_sample.py:91
```

where `t` counts the read's calls at confident consensus CpG positions and `d` counts those that
DISAGREE with the consensus. That is a **discordance rate**. The protocol reads it as "this read's
methylation pattern departs from the sample's", which is what a tumour-derived read should do. But
a read with a high basecall / modification-call error rate also departs from the consensus, and
nothing in the design separates the two.

Two facts already on record make this live rather than theoretical:

1. In HCC1395's TF0 blanks — **no tumour present** — ALT reads at gate-passing candidates are kept
   at 27-40% against a global keep rate of 4.9%, an enrichment of 5.5-8.2x (recomputed from
   `execution/raw/`, recorded in the 2026-09-19 commit message). Whatever the score selects there,
   it is not tumour.
2. Gated ALT reads in a pure-normal sample are basecall or alignment errors by construction.

## Question

Among scorable reads, how much of `score_b1` is explained by per-read sequencing error, measured
independently of methylation?

## Data

- `/bip7_disk/pingting114/mixed_bam/HCC1395/TF0_25x/TF0_25x.rep1.cram` — the blank. Chosen because
  it contains no tumour, so any structure found there cannot be tumour signal.
- `/bip7_disk/pingting114/mixed_bam/HCC1395/TF1e-3_25x/TF1e-3_25x.rep1.cram` — the primary level,
  for contrast.
- Reference `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`, md5
  `a6da8681616c05eb542f1d91606a7b2f` (EV-0052).
- Candidates: `research/surveys/long-read-tumor-only-mrd/exp-s1-002/results/counts_TF0.tsv`,
  3,925 chr1 candidates — the identical frame EXEC-001 used.

No matched normal, no SEQC2, no panel of normals, no population database is opened. This
diagnostic needs no truth labels and uses none.

## Method

`score_b1`, the confident-position set and the cut are recomputed by the **frozen EXEC-001
constants** (ML=128, MIN_COV=10, CONF_LO=0.1, CONF_HI=0.9, MIN_CPG=5, PCT=95, gate 1<=alt<=2,
MIN_BQ=20, MIN_MQ=20) so the reproduction is checkable against the recorded values.

For each scorable read, alongside `score_b1`, record error proxies that know nothing about
methylation:

| proxy | definition |
|---|---|
| `nm_rate` | `NM` tag / aligned length — mismatches+indels per aligned base |
| `mapq` | mapping quality |
| `aln_len` | aligned reference length |
| `n_conf` | confident CpG positions on the read (this is `score_c2`, the density control) |
| `mean_ml` | mean modification-call probability, a confidence proxy |

## Reproduction check, which must pass before anything below is read

On TF0 rep1 the recomputation must return **exactly** the recorded values:
`n_consensus_positions` 1,153,835 · `n_confident_positions` 353,719 · `n_scorable_reads` 58,990 ·
`K_B1` 2,895 · `cut` 0.0769. If it does not, the diagnostic is void and returns
IMPLEMENTATION_FAULT rather than a result.

## Predictions — fixed now, before the data exist

```text
P1  Spearman rho(score_b1, nm_rate) over all scorable reads in the BLANK.
      rho >= 0.30  -> ERROR-DOMINATED. score_b1 is substantially an error-rate proxy.
      rho <= 0.10  -> NOT ERROR-DOMINATED. The confound is not the explanation.
      0.10 < rho < 0.30 -> PARTIAL, reported as such and as neither outcome.

P2  In the BLANK, gate-passing ALT reads that B1 KEEPS versus those it does not.
      Registered prediction: kept reads have higher median nm_rate than unkept.
      Reported as a ratio of medians with a Mann-Whitney U two-sided p and the two counts.
      Counts here are small (~25 scorable ALT reads per blank). If either group has fewer
      than 5 reads the leg returns UNDERPOWERED, not a result.

P3  Does nm_rate alone reproduce B1's blank enrichment? Rank scorable reads by nm_rate,
      keep the top 5% (matching PCT=95), and compute the same ALT-read retention.
      Registered prediction: an nm_rate-only filter reaches at least HALF of B1's measured
      blank ALT retention of 40.0% (i.e. >= 20%). This is the operational form of the
      confound: a filter that knows only error rate, and nothing about methylation.

P4  Contrast with the 0.1% sample. If score_b1 were purely an error proxy, rho and the P3
      retention should be about the SAME at TF0 and at 0.1%, because error rate does not
      know the tumour fraction. A materially higher B1 retention at 0.1% than an
      nm_rate-only filter achieves there is evidence that something beyond error rate is
      contributing.
```

## What this diagnostic cannot do

- It cannot support or refute H1. It measures a property of the score, not a detection outcome.
- `NM` conflates sequencing error with true divergence from the reference, including real somatic
  and germline variation. A read carrying genuine variants has a higher `nm_rate` for reasons that
  are not error. This biases P1 and P3 **towards** finding a correlation, so a NULL result is the
  stronger one and a positive result is an upper bound on the error contribution.
- It is one individual and one chromosome. COLO829 is not run here.
- It says nothing about whether the reads it flags are tumour-derived.

## Outcomes, named in advance

```text
ERROR-DOMINATED        P1 >= 0.30 and P3 >= 20%  -> the v1.1 elaboration is aimed at the wrong
                                                    confound; the cheaper fix is to control the
                                                    score for error rate, not to add arms
NOT ERROR-DOMINATED    P1 <= 0.10 and P3 < 20%   -> the confound is not the explanation and the
                                                    panel's MAJ-01 is answered by measurement
MIXED                  anything else             -> reported as measured, no verdict
IMPLEMENTATION_FAULT   reproduction check fails  -> void, no numbers reported
```
