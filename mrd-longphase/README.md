# mrd-longphase

Code repository for the master's thesis on **tumor-only minimal residual disease (MRD)
detection from long-read (ONT) sequencing**, with haplotype phasing and methylation as
auxiliary signals.

The layout separates *pipeline orchestration* (`workflow/`) from *reusable library code*
(`src/`), and keeps *inputs* (`data/`), *outputs* (`results/`, `figures/`), and
*write-ups* (`reports/`, `notebooks/`) apart so the analysis stays reproducible.

## Directory structure

```
mrd-longphase/
├── config/                 # run configuration (YAML/params, sample sheets, paths)
├── workflow/               # pipeline steps (scripts / Snakemake / Nextflow rules)
│   ├── tumor_only/         #   tumor-only somatic calling (e.g. ClairS-TO)
│   ├── matched_normal/     #   matched tumor-normal calling (comparison / validation)
│   ├── truth_validation/   #   benchmark calls vs truth sets (SEQC2, som.py/isec)
│   ├── marker_selection/   #   build & tag the tumor-informed marker compendium
│   ├── dilution/           #   dilution-series (1% / 0.1% / 0.01%) preparation & scoring
│   ├── phasing/            #   LongPhase haplotype phasing / haplotagging
│   ├── methylation/        #   methylation (5mCG/5hmCG) extraction & analysis
│   └── mrd_detection/      #   MRD detection / limit-of-detection estimation
│
├── src/                    # importable Python package (reusable logic, no I/O side effects)
│   ├── candidates/         #   candidate variant parsing / QC          [upstream baseline]
│   ├── io/                 #   regions: parsing, partitioning, merging
│   ├── phasing/            #   HP/PS haplotype context
│   ├── methylation/        #   MM/ML -> per-CpG 5mC & 5hmC evidence
│   ├── joint_evidence/     #   the joint-molecule record and its writer
│   ├── provenance/         #   tool versions, seeds, run manifests
│   ├── markers/            #   marker/compendium construction & tagging
│   ├── evidence/           #   per-locus read evidence (exact-ALT pileup, VAF)
│   ├── models/             #   the A-F ablation grid + interpretable classifiers
│   └── evaluation/         #   feasibility funnel, leakage-safe splits, metrics
│
├── data/                   # inputs (large raw data lives outside; keep pointers here)
│   ├── metadata/           #   sample sheets, BAM paths, coverage, run metadata
│   └── truth/              #   truth VCFs / high-confidence BEDs (or symlinks)
│
├── results/                # generated outputs (tables, VCFs, scoring TSVs)
│   ├── tumor_only/
│   ├── marker_validation/
│   ├── dilution/
│   ├── phasing/
│   └── multimodal/
│
├── notebooks/              # exploratory analysis (Jupyter)
├── figures/                # publication / thesis figures
├── tests/                  # unit/, integration/, fixtures/ — synthetic BAMs only
├── experiments/            # registry/ (pre-registered manifests) + templates/
├── docs/                   # joint_molecule_schema.md — the data contract
└── reports/                # write-ups
    └── weekly/             #   weekly research reports
```

Additional `workflow/` stages for the current research direction:

```
workflow/
├── joint_molecule/         # extract_joint_molecules.py — per-region evidence extraction
├── feasibility_funnel/     # report_funnel.py — the H1 decision
└── tools/                  # report_environment.py — versions + data reachability
```

## Conventions
- `src/` is a Python package — import as `from src.evidence import ...` (or install with
  `pip install -e .`). Keep it side-effect free; put runnable steps in `workflow/`.
- Large raw data (BAMs, references) are **not** committed. Store real paths in
  `data/metadata/` and symlink into `data/` as needed.
- `results/` and `figures/` are reproducible outputs — regenerate from `workflow/` + `config/`.
- One config file per experiment in `config/`; never hard-code paths in `src/`.

## Getting started
1. Put sample/BAM paths and truth-set locations in `config/` and `data/metadata/`.
2. Add pipeline steps under `workflow/<stage>/`.
3. Keep shared logic in `src/`; import it from workflow scripts and notebooks.

## Current tumor-only baseline
The repository now includes a Phase 1 tumor-only HCC1395 characterization flow under
`workflow/tumor_only/`. Its current scope is deliberately descriptive:

- extract PASS SNV candidates from a ClairS-TO VCF;
- summarize depth, VAF, and ALT-support landscapes;
- write candidate-level analysis tables, figures, and weekly research notes;
- preserve tumor-only execution without requiring a matched-normal sample.

The current configured HCC1395 run is documented in `config/tumor_only_hcc1395.yaml`
with read-only source paths recorded in `data/metadata/hcc1395_tumor_only_inputs.tsv`.

## Current research direction

The primary storyline is now **tumor-only long-read MRD through haplotype-conditioned native
methylation evidence**; the tumor-only candidate characterization above is its *upstream
baseline*, supplying the candidate loci the new pipeline iterates over.

The data contract for the new work is [`docs/joint_molecule_schema.md`](./docs/joint_molecule_schema.md):
one record per (read, candidate), carrying the allele, the HP/PS haplotype context, and the
MM/ML methylation evidence read off the same alignment record.

```
candidate regions
  -> extract overlapping reads      workflow/joint_molecule/
  -> read allele, HP/PS, MM/ML      src/{joint_evidence,phasing,methylation}/
  -> apply quality checks in order  src/joint_evidence/extract.py
  -> emit sparse records            src/joint_evidence/writer.py
  -> count the funnel               workflow/feasibility_funnel/  <- the H1 decision
```

Research documents live one level up in [`../docs/research/`](../docs/research). Read
`00_scope.md` first, and treat `05_claim_boundaries.md` as binding on every output.

## Conventions added for this direction

- **No threshold defaults inside `src/`.** A missing required threshold raises; the funnel
  reports `BLOCKED`. A defaulted threshold is an unrecorded research decision.
- **Every examined read is recorded**, usable or not, tagged with the first check it failed.
  The feasibility funnel is a grouping over that one table, not a second pipeline.
- **5mC and 5hmC are never summed.** Separate columns, separate features.
- **`source_label_for_evaluation_only` never reaches a model.** The name is deliberately
  awkward; `tests/unit/test_leakage.py` asserts the firewall holds.
- **Partitions are byte-reproducible.** Sorted records, fixed float precision, `gzip mtime=0`.
- **Tests use synthetic BAMs only** (`tests/fixtures/synthetic_bam.py`). No test touches a
  real BAM.

Run everything with `../run-tests.sh python`.
