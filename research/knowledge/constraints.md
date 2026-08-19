# Constraints

What bounds any plan made in this project. Violating one of these is not a trade-off; it
invalidates the result.

---

## 1. Data governance

| Rule | Why |
|---|---|
| **Source data is read-only.** Never modify, re-index, move or re-sort anything under `/big8_disk/data/`, `/big8_disk/ref/`, `/bip7_disk/pingting114/` | Shared server; other users' work depends on these exact files `[repo]` |
| **No bulk data in the repository.** No BAM/FASTQ/VCF/FASTA — only manifests, summaries and small derived artifacts | `.gitignore` enforces it `[repo]` |
| **Absolute server paths stay out of the public site.** Full paths belong in `docs/`, `knowledge/` and manifests | `AGENTS.md`; the site validator rejects absolute paths in evidence records `[repo]` |
| **Normal BAM is evaluation-only.** `HCC1395BL.bam` and read-name labels may never enter a discovery or inference path | The setting is *tumor-only*; using the normal as input answers a different, easier question `[repo]` |

## 2. Compute

| Limit | Detail |
|---|---|
| **No GPU** | `nvidia-smi` absent `[verified 2026-08-19]`. Deep-learning designs are off the table on this host |
| 112 cores / 503 GB RAM | Generous for parallel region-scoped work `[verified 2026-08-19]` |
| Disk capacity unknown | `df` hangs on this host `[verified 2026-08-19]`; ~0.7 TB of derived output already exists in `week1/`, `week3/`, `week4/` |
| Each dilution BAM is ~76 GB; 14 of them ≈ 1.06 TB | Whole-genome passes are expensive. Region-scoped, resumable processing is the only sane default `[verified 2026-08-19]` |

## 3. Environment gotchas

| Gotcha | Workaround |
|---|---|
| `run_clairs_to` fails: `/usr/bin/env: 'python': No such file or directory` `[verified 2026-08-19]` | Use a conda env, a `python` shim, or the container |
| `longphase` and `modkit`/`dorado`: not on `PATH` / not installed `[verified 2026-08-19]` | LongPhase 2.0.2 is at `week1/experiment/external/longphase_develop/longphase`; parse `MM`/`ML` with `pysam` instead of `modkit` |
| `minimap2` on `PATH` is 2.24; the BAMs were built with 2.26 `[verified 2026-08-19]` | Do not re-align and expect identical output |
| No `pandas`/`scikit-learn` installed `[verified 2026-08-19]` | Install deliberately, and record it, before any modelling step |
| Basecaller/model not in the BAM header `[verified 2026-08-19]` | Treat the "5 kHz simplex 5mCG/5hmCG" description as a naming claim until confirmed |

## 4. Scientific guardrails

These are claim boundaries, enforced in the site validator and repeated here because they are
easiest to break while moving fast `[repo]`:

- `PASS` is a caller retention label — **not** confirmed somatic truth.
- Filtered ≠ false positive. The 98.46% not retained is a selection funnel.
- VAF ≠ tumor fraction.
- High coverage in the source sample ≠ low-tumor-fraction sensitivity.
- No claim that phase or methylation improves tumor recognition before a baseline, a defined
  metric and an ablation exist.
- HCC1395 genomic dilution ≠ plasma cfDNA. Nothing here supports a clinical MRD claim.

## 5. Method-level constraints inherited from the literature

- Methylation and fragmentation are **coupled**; treating them as independent evidence inflates
  confidence [6] `[unverified]`.
- Methylation is protocol-sensitive, and read-end calls are the least reliable [7]
  `[unverified]`.
- Any detection score needs a blank distribution to be interpretable [3] `[unverified]`.

## 6. Process constraints

- Work is not "done" without evidence or a written reason — enforced by
  `site/scripts/validate-research-os.mjs` `[repo]`.
- Evidence is never `verified` because an AI summarised it; that status needs a named person
  and a date `[repo]`.
- Thresholds are set **before** seeing results; `config/experiments/h1_feasibility.yaml` ships
  with every threshold `null` and the runner refuses to guess `[repo]`.
