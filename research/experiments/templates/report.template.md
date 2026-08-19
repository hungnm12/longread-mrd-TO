# <EXP-ID> — <title>

| | |
|---|---|
| **Hypothesis** | H_ |
| **Status** | planned / running / observed / verified / rejected / blocked |
| **Decision** | ACCEPT / REJECT / PARTIAL / BLOCKED / INCONCLUSIVE — *leave blank until the run finishes* |
| **Manifest** | `experiments/registry/<EXP-ID>.yaml` |
| **Date** | |

## Research question

<!-- One sentence. The question this run answers, not the task it performs. -->

## Prediction (written before the run)

<!-- What you expect and why. Recorded so it can turn out wrong. If this section is
     written after the results, say so explicitly — a retrofitted prediction is not one. -->

## Method

<!-- Enough to re-run: inputs, config file, thresholds, split, commands. -->

```bash
# exact commands
```

## Observed result

<!-- Numbers only. Every rate with its denominator. Every estimate with an interval and an n.
     No interpretation in this section. -->

| Metric | Value | n | Interval |
|---|---|---|---|
| | | | |

## Inferred interpretation

<!-- What the observation suggests, and under which stated assumptions. Labelled as
     inference, not as observation. -->

## Hypothesis

<!-- What might be true if a further assumption held. Must name a test that would falsify it. -->

## Unresolved questions

<!-- Known gaps this run did not close. -->

## Confounders considered

| Confounder | Handled how | Residual risk |
|---|---|---|
| | | |

## Claim boundaries

<!-- Copy the applicable standing caveats from research/knowledge/claim-boundaries.md §6.
     At minimum, for anything touching the dilution series: -->

- Dilution levels are **nominal mixing ratios**; the realized tumor fraction was not measured.
- **n = 1 replicate** per dilution level; within-level variance is not estimable.
- HCC1395 genomic dilution is controlled low-TF method development, **not** plasma cfDNA and
  **not** evidence of clinical MRD performance.

## Decision

<!-- ACCEPT / REJECT / PARTIAL / BLOCKED / INCONCLUSIVE, with the acceptance condition
     restated and the observed value compared against it. -->

## Next experiment

<!-- The next smallest falsifiable step. If the decision was REJECT, name which pivot from
     research/hypotheses/hypotheses.md is being taken. -->

## Artifacts

<!-- Paths to funnel tables, summaries, figures, logs. -->
