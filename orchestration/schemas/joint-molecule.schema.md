# Joint-molecule evidence contract

Status: active — the data contract for Phases 3–5
Date: 2026-08-16
Implemented by `src/joint_evidence/`, produced by `workflow/joint_molecule/extract_joint_molecules.py`

---

## 1. What one record is

**One record = one read × one candidate locus.**

A read overlapping three candidate loci produces three records. This denormalization is
deliberate: the unit of analysis in
[`../../research/knowledge/scope.md`](../../research/knowledge/scope.md) is the *informative
molecule at a locus*, and every downstream metric (`joint_yield`, per-candidate counts,
per-phase-set strata) is computed over exactly this unit.

A record is written **whether or not it is usable**. Unusable records carry `usable=0` and a
populated `exclusion_reason`. This is what makes the feasibility funnel countable: the funnel
is a `GROUP BY exclusion_reason` over the same table, not a separate pipeline.

## 2. Fields

| Field | Type | Source | Notes |
|---|---|---|---|
| `sample_id` | str | config | e.g. `HCC1395_TF1e-2_25x_rep1` |
| `dilution` | str | config | `1e-2`, `1e-3`, `1e-4`, `0`, `pure` — **nominal mixing ratio** |
| `source_label_for_evaluation_only` | str | read-name membership | `tumor` / `normal` / `unassigned` / `` — **never an inference input** |
| `chrom` | str | candidate | |
| `region_id` | str | region partition | `{chrom}_{start}_{end}`, the resumability key |
| `candidate_id` | str | candidate | `{chrom}:{pos}:{ref}>{alt}` |
| `candidate_position` | int | candidate | 1-based, VCF convention |
| `read_id` | str | BAM | `query_name` |
| `observed_allele` | str | pileup | the read's base at `candidate_position`; `-` for deletion, `` if not aligned |
| `allele_quality` | int | BAM | base quality at that position |
| `mapping_quality` | int | BAM | `MAPQ` |
| `read_length` | int | BAM | `query_length` |
| `phase_set` | int | `PS` tag | empty if unphased |
| `haplotype_tag` | int | `HP` tag | 1 / 2, empty if unhaplotagged |
| `haplotype_confidence_if_available` | float | — | empty; LongPhase/WhatsHap emit no per-read confidence. **Kept as a named empty column rather than dropped**, so its absence is explicit rather than forgotten |
| `cpg_positions` | list[int] | MM/ML | reference positions of CpG sites on this read, `;`-joined |
| `methylation_probabilities` | list[float] | MM/ML | **P(5mC)** per position, `;`-joined, 3 dp |
| `methylation_probabilities_5hmc` | list[float] | MM/ML | **P(5hmC)** per position, `;`-joined, 3 dp |
| `methylated_cpg_count` | int | derived | count where `P(5mC) ≥ meth_call_threshold` |
| `unmethylated_cpg_count` | int | derived | count where `P(5mC) ≤ 1 − meth_call_threshold` |
| `distance_of_cpgs_to_read_ends` | list[int] | derived | min(query_pos, query_len − query_pos) per CpG, `;`-joined |
| `usable` | int | derived | 1 / 0 |
| `exclusion_reason` | str | derived | see §4; empty when `usable=1` |
| `tool_versions` | str | provenance | `samtools=1.13;pysam=0.24.0;…` |
| `input_manifest_id` | str | provenance | sha1 of the resolved input set; joins to the run manifest |

### Deviations from the brief's suggested field list

Two additions, one justified split:

- **`methylation_probabilities_5hmc`** — the brief lists a single
  `methylation_probabilities`. The data carries both `C+m` and `C+h` codes at every CpG
  (verified: 2,535 positions each on the first read of `chr1:1,000,000+`), and
  [`../../research/knowledge/claim-boundaries.md`](../../research/knowledge/claim-boundaries.md)
  requires 5mC and 5hmC be handled separately. Summing them would destroy that.
- `methylated_cpg_count` / `unmethylated_cpg_count` do **not** sum to `len(cpg_positions)`.
  CpGs in the ambiguous middle band belong to neither. The difference is the per-read
  ambiguity mass, and it is recoverable rather than hidden.

## 3. Storage format — trade-off

The brief requires the trade-off be documented rather than chosen for convenience.

| Format | For | Against | Verdict |
|---|---|---|---|
| **Parquet** | columnar, compressed, typed, fast partitioned reads; native list columns | **`pyarrow` is not installed** (`repo_audit.md` §11); adds a heavyweight dependency; not inspectable with the shell tools already in use | rejected **for now** |
| **JSONL** | native nesting for the four list-valued fields; no dependency | 3–5× larger; not columnar; awkward with `awk`/`cut`; no schema enforcement | rejected |
| **TSV (+ gzip)** | matches every existing output in this repo (`candidate_pass_snvs.tsv`, `qc_stats.txt`, `change_log.tsv`); readable by `awk`/`cut`/`sort`; zero new dependencies; diff-able fixtures | list fields need delimiter encoding (`;`); no types; larger than Parquet; full scan to read one column | **chosen** |

**Chosen: gzip-compressed TSV, one file per region partition, with a sidecar JSON manifest.**

Reasoning: consistency with the repository's existing conventions and zero new dependencies
outweigh columnar performance at this stage, where the binding constraint is *whether enough
molecules exist at all* (H1), not query throughput. The list-encoding cost is one `;`-join.

**Revisit trigger:** if a single dilution level exceeds ~10 GB of records, or if Phase 5
model fitting becomes I/O-bound, install `pyarrow` and add a Parquet writer behind the same
`writer.py` interface. The record definition is format-agnostic precisely so this swap costs
one module. Recorded in
[`../../research/decisions/decision-log.md`](../../research/decisions/decision-log.md).

### Layout on disk

```
results/joint_evidence/<sample_id>/
├── manifest.json                       # config, tool versions, input_manifest_id, region list
├── regions/
│   ├── chr1_1000000_2000000.tsv.gz     # one partition per region
│   ├── chr1_2000000_3000000.tsv.gz
│   └── …
└── _complete/
    ├── chr1_1000000_2000000            # empty marker, written after the partition closes
    └── …
```

## 4. Exclusion reasons

Evaluated in this fixed order; the **first** failure is recorded, so counts partition cleanly.

| `exclusion_reason` | Meaning |
|---|---|
| `secondary_or_supplementary` | not a primary alignment |
| `unmapped` | read unmapped |
| `duplicate_or_qcfail` | flagged |
| `low_mapping_quality` | `MAPQ < min_mapping_quality` |
| `allele_not_aligned` | candidate position falls in a deletion or skipped region |
| `low_allele_quality` | base quality `< min_allele_quality` |
| `no_haplotype_tag` | `HP` absent |
| `no_methylation_tag` | `MM`/`ML` absent |
| `insufficient_cpgs` | usable CpGs `< min_cpg_per_read` after read-end exclusion |
| *(empty)* | usable |

Ordering matters: it makes the funnel in
[`../../research/experiments/evaluation-plan.md`](../../research/experiments/evaluation-plan.md)
a strict partition, so stage survival rates are interpretable and sum correctly.

## 5. Processing guarantees

| Guarantee | How |
|---|---|
| **Region-based** | Input is a region list; each region is processed independently. The BAM is never loaded whole — only `fetch(chrom, start, end)`. |
| **Resumable** | A region with a marker in `_complete/` is skipped. Interrupted partitions are rewritten from scratch, never appended to. |
| **Deterministic** | Records sorted by `(candidate_position, read_id)`; floats fixed to 3 dp; no dict-iteration order dependence; no randomness. Re-running a region byte-reproduces its partition. |
| **Explicit configuration** | Every filter and threshold from `config/experiments/*.yaml`. No defaults inside `src/`. A missing required threshold raises rather than defaulting. |
| **Logging** | Per-region: counts by exclusion reason, wall time, records written. |
| **Provenance** | `tool_versions` and `input_manifest_id` on every row; full resolved config in `manifest.json`. |
| **Testable on fixtures** | Synthetic BAMs with known MM/ML, HP/PS, and alleles under `tests/fixtures/`. No real BAM in any test. |

## 6. Evaluation-only firewall

`source_label_for_evaluation_only` is populated by a **separate** code path
(`src/joint_evidence/labels.py`) that reads the source BAMs. It is:

- written to the record table, because evaluation needs it;
- **excluded by name** from every feature matrix built in `src/models/`;
- asserted absent by `tests/unit/test_leakage.py`.

The field name is long and awkward on purpose. Any code review that sees it inside a feature
path should stop.

## 7. What this contract does not do

- It does **not** define the model, the score, or any threshold's value.
- It does **not** decide which reads are tumor-derived. `source_label_for_evaluation_only` is
  measurement, not inference.
- It does **not** aggregate. Aggregation to locus or sample level is H4's problem.
