# Datasets on this server

Last surveyed: 2026-08-19. All paths are **read-only inputs**; nothing in this project writes
to them (see [`constraints.md`](./constraints.md)).

---

## 1. Source sequencing — HCC1395 ONT, native modifications

`/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/` `[verified 2026-08-19]`

| File | Size | Role |
|---|---|---|
| `HCC1395.bam` (+ `.bai`) | 272 GB | Pure tumor cell line. Candidate discovery; positive-control methylation reference |
| `HCC1395BL.bam` (+ `.bai`) | 139 GB | Matched B-lymphoblastoid normal. **Evaluation only** — source of per-read labels, never a discovery input |

Both carry 5mC + 5hmC on every sampled read and no phasing — see
[`ont-capabilities.md`](./ont-capabilities.md).

### Other HCC1395 ONT copies on the server

`[verified 2026-08-19]` Three further trees exist and must not be confused with the above:

| Path | What it is |
|---|---|
| `/big8_disk/data/HCC1395/ONT/` | A different ONT BAM pair (223 GB / 134 GB) **plus** existing caller outputs: `ClairS_TO_v0_3_0`, `ClairS_TO_ss_v0_3_0`, `ClairS_v0_4_0`, `ClairS_v0_4_1` (symlink), `DeepSomatic_TO_v1_8_0`, `depth/` |
| `/big8_disk/data/HCC1395/ONT_Dorado/` | Symlinks to `/big8_disk/Google_somatic_data/bams/HCC1395/…`, with its own ClairS / ClairS-TO / DeepSomatic output trees |
| `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/` | **The one this project uses** — the only tree whose name asserts modified-base calling |

`[unverified]` Whether the `ONT/` and `ONT_Dorado/` BAMs carry `MM`/`ML` has not been checked.
If they do not, they are unusable for this project's methylation axis regardless of their other
merits.

## 2. Dilution series — the low-tumor-fraction material

`/bip7_disk/pingting114/mixed_bam/HCC1395/` `[verified 2026-08-19]`

| Level | Replicates | Per-file size | Files |
|---|---|---|---|
| `TF0_25x` (blank) | **5** | 76.0–76.1 GB | `TF0_25x.rep1…rep5.bam` |
| `TF1e-2_25x` (1%) | **3** | 75.7 GB | `TF1e-2_25x.rep1…rep3.bam` |
| `TF1e-3_25x` (0.1%) | **3** | 75.7 GB | `TF1e-3_25x.rep1…rep3.bam` |
| `TF1e-4_25x` (0.01%) | **3** | 75.7 GB | `TF1e-4_25x.rep1…rep3.bam` |

**14 BAMs, ~1.06 TB total, each with a `.bai`.**

> **This corrects the research contract.** `docs/research/00_scope.md` records "~25×, **1
> replicate**" per level, and `docs/research/01_paper_patterns.md` argues that "one replicate
> per dilution level cannot support a statistically meaningful LoD". Both statements are
> factually wrong about the data on disk: there are 3 replicates per tumor-bearing level and
> **5 blanks**. Five blank replicates is the usual minimum for a rudimentary limit-of-blank
> estimate, so a validation-shaped claim is less out of reach than the contract assumes. The
> contract has not been edited — this note flags the disagreement for a deliberate decision.

### Mixing provenance

`[verified 2026-08-19]` Recorded in each BAM's `@PG` chain: reads were deduplicated, then
subsampled with `samtools view -s SEED.FRACTION` from tumor and normal separately and merged.
Seeds and fractions are therefore reproducible from the headers themselves:

| Level | Tumor `-s` | Normal `-s` |
|---|---|---|
| `TF0` | — (normal only) | `101.94768764` |
| `TF1e-2` | `201.0030826141` | `111.9382107657` |
| `TF1e-3` | `301.0003082614` | `121.9467399545` |
| `TF1e-4` | `401.0000308261` | `131.9475928734` |

Read names are the original ONT UUIDs `[verified 2026-08-19]`, which is what makes per-read
tumor/normal labelling by name-matching against the source BAMs possible — for **evaluation
only**.

## 3. Truth and benchmark resources

| Resource | Path | Contents |
|---|---|---|
| **SEQC2 high-confidence somatic** | `/big8_disk/data/HCC1395/SEQC2/` `[verified 2026-08-19]` | `high-confidence_sSNV_in_HC_regions_v1.2.1.vcf(.gz/.tbi)`, sINDEL equivalents, merged sSNV+sINDEL, `High-Confidence_Regions_v1.2.bed` (16.9 MB), plus a `CNV/` subdirectory |
| **Orthogonal-tools benchmark** | `/big8_disk/data/HCC1395/orthogonal-tools-benchmark/` `[verified 2026-08-19]` | `HCC1395_orthogonal-tools-benchmark_somatic-only.vcf(.gz/.tbi)` (88.8 MB raw) and its `.bed` (11.9 MB) |
| **Reference genome** | `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` (+ `.fai`) `[verified 2026-08-19]` | 3.14 GB, the alignment reference — matches the BAM headers |

These are **evaluation resources**, not discovery inputs: using them to select candidates would
leak truth into the method.

## 4. Population and panel-of-normals resources

`/big8_disk/data/PON/clairs-to_databases/` `[verified 2026-08-19]` — the databases ClairS-TO
uses for tumor-only background suppression:

- `gnomad.r2.1.af-ge-0.001.sites.vcf(.gz/.tbi)`
- `dbsnp.b138.non-somatic.sites.vcf(.gz/.tbi)` (1.87 GB raw)
- `1000g-pon.sites.vcf(.gz/.tbi)`
- `CoLoRSdb.GRCh38.v1.1.0.deepvariant.glnexus.af-ge-0.001.vcf(.gz/.tbi)` (5.26 GB raw) — a
  **long-read** population database, relevant when reasoning about ONT-specific artifacts
- `GRCh38Chr1-22XY_excludedGIABStratifV3.3AllDifficultRegions_includedCMRGv1.0.bed`
- `clairs-to_databases.tar.gz` (1.52 GB) and `source.txt`

`/big8_disk/data/PON/deepsomatic-to_databases/` also exists `[verified 2026-08-19]`.

## 5. Other cell lines available

`[verified 2026-08-19]` `/big8_disk/data/` also holds `COLO829`, `colo829_nygc`, `H1437`,
`H2009`, `HCC1937`, `HCC1954`. Out of scope now, but they are the obvious external-validity
material if a method ever needs a second cell line.

## 6. This project's own outputs

| Path | Size | What |
|---|---|---|
| `week4/expA_full/HCC1395_pure/snv.vcf.gz` | 90.8 MB `[verified 2026-08-19]` | The ClairS-TO tumor-only SNV call set behind the 3,169,996 / 48,819 figures |
| `week1/experiment/clairs_to_wgs_server1/` | — `[verified 2026-08-19]` | Earlier WGS tumor-only run (`snv_…`, `indel_…`, timing logs) |
| `week3/` | 158 GB `[verified 2026-08-19]` | Tagging, compendium, dilution inputs, `run_clairs_to.sh`, `pipeline.md` |
| `week4/expB/` | — `[verified 2026-08-19]` | `score_calls_compendium.tsv`, `score_truth_compendium.tsv`, `mrd_calls.tsv`, `mrd_truth.tsv` |
| `mrd/research/manifests/week-001-candidate-landscape.json` | small `[repo]` | The summary the site and the deck read |

Workspace footprint `[verified 2026-08-19]`: `week1` 276 GB, `week3` 158 GB, `week4` 268 GB,
`mrd` 482 MB. Roughly **0.7 TB of derived output already exists** outside the repository.
