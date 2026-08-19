# data/

Pointers and manifests only. **No bulk data lives in this repository** — no BAM, FASTQ, VCF or
FASTA. `.gitignore` enforces it.

| Path | What |
|---|---|
| `manifests/` | Small derived summaries the site and reports read, plus their JSON schemas |
| `metadata/` | Input tables and server-resource notes |
| `truth/` | Placeholder for truth-set pointers; contents stay outside the repo |
| `GOVERNANCE.md` | The rules for touching any of it |

## Where the real data is

The full inventory — paths, sizes, roles, replicate structure and mixing provenance — is
[`../research/knowledge/datasets.md`](../research/knowledge/datasets.md), which was written by
inspecting the server and marks each fact with its verification status.

Summary of what that document records:

| Dataset | Location | Role |
|---|---|---|
| HCC1395 tumor, ONT native mods | `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam` | Candidate discovery |
| HCC1395BL normal | same directory | **Evaluation only** |
| Dilution series (14 BAMs) | `/bip7_disk/pingting114/mixed_bam/HCC1395/` | Low-tumor-fraction material |
| GRCh38 reference | `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta` | Alignment reference |
| SEQC2 high-confidence somatic | `/big8_disk/data/HCC1395/SEQC2/` | Evaluation only |
| ClairS-TO PoN databases | `/big8_disk/data/PON/clairs-to_databases/` | Background suppression resources |

All are **read-only**.
