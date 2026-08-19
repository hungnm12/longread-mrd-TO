# ONT capabilities — what this data physically gives us

Last surveyed: 2026-08-19. Everything marked `[verified 2026-08-19]` was checked by reading
the BAMs on this server; the commands are given so any claim can be re-run.

---

## 1. What is on every read

| Property | Status | Detail |
|---|---|---|
| **Aligned sequence** | `[verified 2026-08-19]` | minimap2 2.26-r1175, preset `map-ont`, against `GRCh38_no_alt_analysis_set.fasta`, 195 reference sequences |
| **Native 5mC** (`MM:Z:C+m?` + `ML:B:C`) | `[verified 2026-08-19]` | present on **224/224** sampled reads (pure tumor BAM, chr1:5,000,000–5,020,000) |
| **Native 5hmC** (`MM:Z:C+h?` + `ML`) | `[verified 2026-08-19]` | present on the same 224/224 reads — 5mC and 5hmC are **separate channels**, never summed |
| **Haplotype tag** `HP:i:` | `[verified 2026-08-19]` | **absent — 0/224 reads.** Nothing is phased yet |
| **Phase set** `PS:i:` | `[verified 2026-08-19]` | **absent — 0/224 reads** |
| **Read length** | `[verified 2026-08-19]` | median ≈ 11.3 kb, max 70.2 kb in the sampled window |
| **Mapping quality** | `[verified 2026-08-19]` | median MAPQ 60 |

```bash
samtools view /big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam \
    chr1:5000000-5020000 | head -400        # then count MM/ML/HP/PS tags
```

**The consequence that matters.** A single read spans ~11 kb of sequence carrying, at once,
the allele at any candidate inside it, the alleles at every heterozygous site inside it, and a
per-CpG methylation call. That co-observation is the platform capability the project's
hypothesis rests on. Phase, however, is **not given** — it is work this project must do.

## 2. Modification-call encoding

- `MM:Z:C+m?,...` and `C+h?,...` — the `?` flag means *implicit unknown*: positions not listed
  are of **unknown** modification status, not "unmodified". `[verified 2026-08-19]`
- `ML:B:C,...` — one probability byte (0–255) per listed position, in the order given by `MM`.
- Parsing needs no external tool: `pysam` 0.24.0 exposes `modified_bases` /
  `modified_bases_forward` directly. `modkit` is **not installed** (see
  [`tools.md`](./tools.md)).
- Both channels are CpG-context calls from the `5mCG_5hmCG` model family, by the dataset's
  name — see the provenance gap below.

## 3. Provenance gap — the basecaller is not recorded

`[verified 2026-08-19]` The BAM header contains **no `@RG` line and no basecaller `@PG`
line**. The only `@PG` entries are `minimap2` and four `samtools` steps. The chemistry,
sampling rate, basecall model and Dorado version are therefore asserted **only by directory and
FASTQ file names**:

```
/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/
    → minimap2 ... HCC1395_5khz_simplex_5mCG_5hmCG.fastq
```

So "R10.4.1, 5 kHz, simplex, Dorado sup, 5mCG/5hmCG" is a **naming claim, not a header fact**.
`[unverified]` Anything downstream that depends on the exact model version — methylation
calibration in particular — needs this confirmed with whoever produced the run.

The alignment used `minimap2 -y`, which is what carries the `MM`/`ML` tags through from the
unaligned reads. `[verified 2026-08-19]`

## 4. What survives subsampling

`[verified 2026-08-19]` The dilution BAMs keep the modification tags: 300/300 sampled reads in
`TF1e-4_25x.rep1.bam` carry both `MM` and `ML`, and none carry `HP`/`PS`. Dilutions are
`samtools view -s` subsamples of the same aligned reads, so per-read properties are inherited
unchanged — see [`datasets.md`](./datasets.md) for the exact fractions and seeds.

## 5. What ONT does *not* give here

| Not available | Why it matters |
|---|---|
| Phase / haplotype tags | Must be produced by this project (LongPhase 2.0.2 is present but unrun) |
| Duplex reads | Data is **simplex**; per-read accuracy is what it is, with no duplex consensus to fall back on |
| Consensus correction | No rolling-circle or UMI-style consensus in this dataset — the NanoRCS trade is not available and not compatible with keeping modifications native |
| Recorded basecall model | See §3 — provenance gap |
| Per-read truth labels | Only recoverable by read-name matching against the source tumor/normal BAMs, and only for the dilutions `[repo]` |

## 6. Capability summary in one line

Kilobase-scale native reads that carry allele, heterozygous context and CpG methylation on the
same molecule, at ~25× in the dilution series, with phasing still to be computed and the
basecalling provenance still to be confirmed.
