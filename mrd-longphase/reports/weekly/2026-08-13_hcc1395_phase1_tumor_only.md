# HCC1395 Phase 1 Tumor-Only Candidate Landscape (2026-08-13)

## Research question

What does the tumor-only PASS SNV candidate landscape look like before any somatic interpretation?

## Why it matters

This phase defines the retained analysis population for later reliability scoring and tumor-only marker qualification without requiring a matched normal.

## Experiment / analysis

- Input VCF: `/big8_disk/hung114/ONT_MRD/week4/expA_full/HCC1395_pure/snv.vcf.gz`
- Extraction target: PASS single-nucleotide variants only
- Quantified dimensions: candidate count, depth, VAF, ALT support, and depth relationships

## Observation

- The retained population contains 48,819 PASS SNVs from 3,169,996 total ClairS-TO records (1.54% of all records).
- Candidate depth is centered at median 80x with IQR 59-106x.
- Candidate VAF is centered at median 0.461 with IQR 0.292-0.779.
- ALT-support is centered at median 35 reads with IQR 24-53 reads.
- The VAF-depth correlation is -0.419, while ALT-support vs depth correlation is 0.328.

## Interpretation

- The candidate count defines the retained analysis population, not a confirmed somatic set.
- Depth and allele balance do not collapse into a single simple coverage effect because VAF-depth correlation is moderately negative while ALT-support follows depth more directly.
- Broad VAF and ALT-support distributions show heterogeneity in retained calls, but they do not establish biological origin.

## Limitations

- This phase is descriptive only and does not classify calls as somatic, germline, or artifact.
- Metrics rely on ClairS-TO VCF fields and inherit their caller-specific assumptions.
- No matched-normal evidence is used here by design.

## Decision

- Phase 1 is ready once downstream work uses these documented distributions as the baseline candidate landscape.
- Phase 2 should focus on feature extraction for reliability analysis rather than additional biological interpretation.

## Next research question

Which tumor-only candidate features are associated with potentially reliable or unreliable SNV calls?
