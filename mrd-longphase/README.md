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
│   ├── candidates/         #   candidate variant parsing / QC
│   ├── markers/            #   marker/compendium construction & tagging
│   ├── evidence/           #   per-locus read evidence (exact-ALT pileup, VAF)
│   ├── models/             #   detection / noise models (e.g. MRDetect-style scoring)
│   └── evaluation/         #   metrics: precision/recall/F1, LoD, titration
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
└── reports/                # write-ups
    └── weekly/             #   weekly research reports
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
