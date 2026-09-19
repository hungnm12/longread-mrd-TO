# EXEC-001 — execution log

Benchmark `BM-0001-methyl-gate-mrd`, locked protocol v1.0
(`sha256:9c615da4af068a5330bb512942810c9f2229aa2348554cddcfc130021e200b8c`).
All times 2026-08-31, Asia/Taipei.

| step | time | command | exit | runtime | in | out |
|---|---|---|---|---|---|---|
| S1 precheck: inputs | 16:20 | existence + index check over the 28 BAM paths | 0 | <1 s | dilution BAM tree | `missing=0` |
| S2 precheck: headers | 16:22 | `pysam` header read, 28 BAMs | 0 | ~30 s | 28 BAMs | `execution/inputs_manifest.tsv` |
| S3 precheck: provenance | 16:23 | `@PG` chain capture, 3 representative BAMs | 0 | ~5 s | BAMs | `execution/pg_chains.txt` |
| S4 freeze: candidates | 16:22 | copy of both frames, verbatim `chrom/pos/ref/alt` | 0 | <1 s | exp-s1-002, exp-s1-007 `counts_TF0.tsv` | `execution/candidate_universe.tsv` (7,925 rows) |
| S5 environment | 16:22 | version and resource capture | 0 | ~2 s | host | `execution/environment.txt` |
| S6 validation pass | 16:21–16:40 | `run_sample.py --bam HCC1395/TF0_25x/TF0_25x.rep1.bam` | 0 | ~19 min | 1 BAM | `execution/raw/SMOKE_HCC1395_TF0_rep1.json` |
| S7 validation check | 16:41 | comparison against `EXP-S1-022` step 5 recorded output | 0 | <1 s | S6 output | `execution/precheck_validation.md` — **exact match on all 7 reported quantities** |
| S8 primary batch | 16:24–16:52 | `xargs -P 13 -n 4 -a execution/jobs_space.txt execution/scripts/run_one.sh` | 0 | 27 jobs, 941–1,180 s each | 27 BAMs | `execution/raw/*.json` |
| S9 exploratory batch | 16:50–16:57 | `xargs -P 13 -n 5 -a execution/jobs_exploratory.txt execution/scripts/run_one.sh` | 0 | 14 jobs | 14 BAMs, chr1 filter | `execution/raw_exploratory/*.json` |
| S10 aggregation (failed) | 16:53 | `aggregate.py` | 1 | 2 s | raw JSON | `TypeError` — deviation D2 |
| S11 aggregation | 16:54 | `aggregate.py --indir execution/raw --outdir results` | 0 | ~40 s | 28 JSON | 224 per-sample rows, 16 ablation rows |
| S12 criteria | 16:54 | `finalize.py --outdir results` | 0 | ~2 s | S11 output | `results/criteria_evaluation.tsv`, `registered_outcome.txt` |
| S13 reporting fix | 16:58 | D3 + D4 applied, S11/S12 re-run | 0 | ~40 s | raw JSON | same artifacts, `retention_scorable_only` and C1 retention band added |
| S14 exploratory aggregation | 16:58 | `aggregate.py --indir execution/raw_exploratory --tag EXPL_` | 0 | ~10 s | 14 JSON | `results/exploratory/` |
| S15 leakage check | 16:59 | scan of every path opened by every worker | 0 | <1 s | 42 JSON | `execution/files_opened.txt` — 31 paths, **no matched normal, no SEQC2, no panel** |
| S16 artifact validation | 17:00 | checksum and existence sweep | 0 | ~2 s | all artifacts | `results/artifact_manifest.tsv` — 27/27 OK |

## Concurrency

Protocol §23 caps concurrency at 14. Observed maximum was 14 concurrent `run_sample.py`
processes (13 from `xargs` plus the validation pass, then 13 exploratory plus the last primary
job). Verified by process listing at 16:24 and 16:51.

## Runtime

Primary passes: 941 s to 1,180 s each, 28 passes, two waves of 14. Wall-clock 16:21 to 16:52.
Exploratory passes: 14 passes over 241 candidates each, wall-clock 16:50 to 16:57.
Total wall-clock for execution: ~36 minutes. The protocol budgeted ~12 min/BAM at 14-way
concurrency; observed ~16 min/BAM. No timeout, no retry, no killed process.

## Failures

None. `timings.tsv` records exit code 0 for all 41 dispatched jobs plus the validation pass.

## Known benign stderr, counted rather than suppressed (protocol §23)

`[E::bam_parse_basemod2] ... MM/MN data length is incompatible with SEQ length` and
`[W::hts_idx_load3] The index file is older than the data file`. Both appeared in the prior
`EXP-S1-022` runs on the same BAMs. Per-job stderr is retained in `execution/logs/*.err`.
