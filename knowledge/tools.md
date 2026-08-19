# Tools and compute available

Last surveyed: 2026-08-19, all entries `[verified 2026-08-19]` unless marked otherwise.

---

## 1. On `PATH`

| Tool | Version | Path | Note |
|---|---|---|---|
| `samtools` | 1.13 | `/usr/local/bin/samtools` | Older than htslib below; fine for read/subsample work |
| `bcftools` | 1.13 | `/usr/bin/bcftools` | |
| `tabix` / `bgzip` | htslib 1.19 | `/usr/local/bin/` | Newer htslib than samtools 1.13 |
| `minimap2` | 2.24-r1122 | `/usr/bin/minimap2` | **The BAMs were aligned with 2.26** — re-alignment would not reproduce them byte-for-byte |
| `whatshap` | 2.8 | `~/.local/bin/whatshap` | Phasing alternative / cross-check to LongPhase |
| `python3` | 3.10.12 | `/usr/bin/python3` | |
| `pip3` | 26.0.1 | `~/.local/bin/pip3` | User-site installs |
| `java` | OpenJDK 21.0.11 | `/usr/bin/java` | |
| `docker` | 29.0.2 | `/usr/bin/docker` | Available if a tool is easier to run containerised |
| `parallel` | GNU 20210822 | `/usr/bin/parallel` | |

## 2. Present but **not** on `PATH`

| Tool | Version | Path |
|---|---|---|
| **LongPhase** | **2.0.2** | `week1/experiment/external/longphase_develop/longphase` |
| **ClairS-TO** | latest checkout | `week1/experiment/external/ClairS_TO_latest/run_clairs_to` |
| **ClairS** | latest checkout | `week1/experiment/external/ClairS_latest/run_clairs` |
| Clair3 | latest checkout | `week1/experiment/external/Clair3_latest/` |
| hap.py | two builds | `week1/experiment/external/hap.py*`, `hap.py*-build` |

> **Gotcha — the ClairS-TO wrapper does not start.**
> `run_clairs_to --version` fails with `/usr/bin/env: 'python': No such file or directory`.
> There is no `python` on `PATH`, only `python3`. Any invocation needs a conda environment, a
> `python` shim, or the container image. The v0.5.0 run that produced the current candidate set
> was made under conditions not reproducible from a bare shell today.

## 3. Not installed

| Missing | Consequence |
|---|---|
| `modkit` | No off-the-shelf per-CpG methylation table extraction. **Not blocking**: `pysam` 0.24.0 parses `MM`/`ML` directly (`read.modified_bases`) |
| `dorado` | No re-basecalling; the existing modification calls must be taken as given, and the model version stays unconfirmed |
| `nanopolish` | Not needed for this design |
| `nextflow`, `singularity`/`apptainer` | Workflow orchestration is plain shell + Python; Docker is available if needed |

## 4. Python environment

`[verified 2026-08-19]` System Python 3.10.12 with user-site packages:

| Package | Version |
|---|---|
| `pysam` | 0.24.0 |
| `numpy` | 2.2.6 |
| `scipy` | 1.15.3 |
| `matplotlib` | 3.10.8 |
| `PyYAML` | 5.4.1 |

Absent: `pandas`, `scikit-learn`, `statsmodels`, `cyvcf2`, `pyranges`, `torch`, `tensorflow`.
`mrd-longphase/requirements.txt` lists only `pysam`, `numpy`, `matplotlib`, `PyYAML` — so the
analysis code as written runs, but **any modelling step beyond hand-rolled linear algebra needs
an install first**.

## 5. Compute

| Resource | Amount |
|---|---|
| CPU | **112 cores** |
| RAM | **503 GB total**, ~480 GB available at survey time |
| GPU | **None** — `nvidia-smi` is not present |

The absence of a GPU is a design constraint, not an inconvenience: it rules out the deep-model
route taken by MRD-EDGE-style methods on this machine, and reinforces the interpretable-model
choice already recorded in `docs/research/00_scope.md`. `[repo]`

Disk: the data volumes are large network/local mounts; a plain `df -h` hangs on this host, so
capacity was **not** measured. `[unverified]` Check free space before writing anything large.

## 6. Site / reporting toolchain

| Tool | Version | Where |
|---|---|---|
| Node | v22.22.2 | system |
| Astro | 5.18.2 | `mrd/site` |
| vitest | 3.2.7 | `mrd/site` |
| wrangler | 4.123.0 | `mrd/site` (Cloudflare deploys) |
| python-pptx | 1.0.2 | system — used by `tools/build_research_deck.py` |
| LibreOffice | present | `/usr/bin/soffice`, used to render decks for checking |
| cairosvg | present | used to rasterise the site's SVG figures for review |
