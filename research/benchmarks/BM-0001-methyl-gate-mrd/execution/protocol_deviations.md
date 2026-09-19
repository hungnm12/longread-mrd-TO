# EXEC-001 — protocol deviations

Locked protocol v1.0, sha256 `9c615da4af068a5330bb512942810c9f2229aa2348554cddcfc130021e200b8c`.

No methodological deviation occurred. Five items are recorded; all have
`Methodology changed: NO`.

---

```text
Deviation ID: D1
Protocol section: §22 / executor phase 2 (input checksums)
Expected: a checksum per input.
Observed: SHA-256 computed for the two candidate frames and for mrdz/score.py. NOT computed
          for the 28 BAMs.
Reason:   the BAMs total roughly 2.3 TB and sit on another user's read-only volume; hashing
          them would cost more wall-clock than the benchmark itself and would not change any
          result. Recorded instead, per BAM: absolute path, byte size, mtime, index presence,
          reference build derived from the @SQ header, and the full @PG chain including the
          `samtools view -s <seed>.<fraction>` subsample record.
Impact:   input identity is established by path + size + header + provenance chain rather than
          by content hash. A silent content change to a source BAM would not be detected.
Methodology changed: NO
Human approval obtained: NOT REQUIRED (no methodological choice involved)

Deviation ID: D2
Protocol section: none — executor implementation
Expected: aggregation to run.
Observed: the first aggregation run raised TypeError in `levels_detected` because the C1 arm
          was routed through the deterministic blank accessor. Fixed by using C1's per-draw
          median blanks in that function, matching what the same script already did elsewhere.
Reason:   implementation defect in code written by the executor.
Impact:   none. The fault raised an exception rather than producing a wrong number, and no
          result artifact existed before the fix.
Methodology changed: NO
Human approval obtained: NOT REQUIRED

Deviation ID: D3
Protocol section: §16, §22 (`retention`)
Expected: "ALT-read retention rate (kept / scorable ALT)" reported for all four arms.
Observed: computed literally, B0's ratio exceeds 1 (1.19 to 1.67), because B0's numerator is
          every ALT read while the denominator excludes the unscorable ones. B0 applies no
          filter, so a retention above 1 is an artifact of the formula, not a measurement.
Reason:   the locked formula was written for the filtered arms.
Impact:   none on any criterion — S4 reads B1's retention, and B0 has no filter to characterise.
          The literal §16 value is reported UNCHANGED, and a second column
          `retention_scorable_only` is added, which restricts B0's numerator to the scorable ALT
          reads and is therefore 1.0 for B0 and identical to the literal value for B1, C1 and C2.
          S4 and the ablation table use `retention_scorable_only`, which for B1 is the same
          number the locked formula gives.
Methodology changed: NO
Human approval obtained: NOT REQUIRED

Deviation ID: D4
Protocol section: §21 F8 vs §22 schema
Expected: §21 F8 requires checking whether C1's retention ratio departs from 1 beyond its own
          5-95 band. §22's column schema did not include that band.
Observed: the executor added `retention_ratio_p05` and `retention_ratio_p95` to
          `ablation_results.tsv` so the check §21 requires can actually be evaluated.
Reason:   internal inconsistency between §21 and §22 of the locked protocol.
Impact:   enables a required check that would otherwise have been unevaluable. Adds no freedom.
Methodology changed: NO
Human approval obtained: NOT REQUIRED

Deviation ID: D5
Protocol section: §19, §23 (exploratory arm)
Expected: 14 exploratory COLO829 chr1 passes; the arm may be consensus-limited (N010).
Observed: all 14 ran and completed. The arm is degenerate: with 241 candidates the consensus
          holds 97,789 positions against the primary run's 1,153,835, and every blank replicate
          yields zero kept ALT reads under B1, C1 and C2, so `sample_sd = 0` and the verdict is
          `no estimate` — the case §15 defines a priori.
Reason:   predicted in advance by review_003 N010 and written into §19.
Impact:   none. The arm decides nothing in §20 and is reported as uninformative rather than as
          a result.
Methodology changed: NO
Human approval obtained: NOT REQUIRED
```
