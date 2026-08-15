# Data Governance

## Read-only source assets

The following assets are treated as read-only sources and must never be modified in place:

- `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam`
- `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`
- upstream VCF and related execution outputs referenced from `mrd-longphase/`

## Repository policy

- Do not copy BAM, FASTQ, or large VCF payloads into this repository.
- Keep only manifests, summaries, plots, or other small derived artifacts needed for weekly reasoning.
- Site pages must redact absolute server paths in public-facing content.
- Full paths may appear in private repo docs or research manifests when required for provenance.

## Evidence hygiene

- Mark local descriptive findings as `preliminary` unless there is explicit local verification.
- Distinguish observed metrics from interpretation and from biological claims.
- Every result should point back to the dataset, run, or summary artifact it came from.
