---
name: data-qc
description: Verify that experiment inputs exist and have the properties the design assumes, before compute is spent. Use before any run, or when the user asks "is this data usable / does it have methylation / is it phased".
---

# Data QC

Answer one question: are the inputs what the design assumes?

## Steps

1. Read the experiment spec's `inputs` block.
2. For each input, check and record `expected` / `observed` / `result` / `command`:
   - path exists, is readable, has an index;
   - reference matches the BAM header;
   - the properties the design needs. For this project usually:
     ```bash
     samtools view -H <bam> | grep -E '^@(HD|RG|PG)'
     samtools view <bam> chr1:5000000-5020000 | head -400   # count MM/ML/HP/PS
     ```
3. Write the report to `outputs/temporary/qc/QC-NNNN.yaml`
   (`orchestration/schemas/qc.schema.yaml`).
4. Verdict `pass` or `fail`. On fail, return the item to `design` with the blocking reason.

## Rules

- **Never write to a source path.** Read-only inspection only; this skill touches shared data
  more than any other.
- `unknown` is a valid result. A check that could not be performed is not a pass.
- Sample a region rather than streaming a 76 GB BAM; say which region was sampled.
- Known baseline for this data (`research/knowledge/ont-capabilities.md`): `MM`/`ML` present on
  every sampled read with separate `C+m` and `C+h`; `HP`/`PS` absent; median read ~11 kb.
