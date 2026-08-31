# Theme map — 2026-08-31

**Through-line.** Two threads ran in parallel and converged on the same sentence: the only ONT
signal this thesis can honestly add to its SNV baseline is methylation, and it has to be tested
as its own preregistered experiment — and by the end of the day that experiment existed, was
locked against its own results, and was running.

| Theme | Theme summary | Tasks | Why they are one theme | Representative evidence | Open items |
|---|---|---|---|---|---|
| **Signal inventory** | Settled which ONT signals the lab's tumour/normal dilution data can carry, in what role, with the low-TF arithmetic that justifies it and the citation rule for the paper it came from | T1, T2, T3, T4 | All four advance one end goal — what this thesis may claim about each signal. T3 is the quantitative backing for T1's methylation verdict; T2 fixes how the source paper may be cited in the same argument; T4 supplies vocabulary the other three use | Four-signal role table; 0.27 molecules vs 5,000,000 fragments from the same 9 ng; 65/792 = 8.2% ecDNA | Neither the role table nor the citation rule is written into `claim-boundaries.md` or the thesis draft yet |
| **Protocol governance** | An autonomous design ↔ adversarial-review loop turned a research question into a protocol frozen at v1.0, closing 14 blocking findings including two that would have made the benchmark unable to answer its own question | T5, T6 | T6 is the content of T5's loop; together they form one deliverable (`protocols/v1.0_locked.md`) and one decision (what counts as success) | 8 → 3 → 2 → 1 → 0 blocking issues over five reviews; B001 degenerate control; B014 aggressiveness confound; S4 added; reviewer's self-correcting addendum | Nothing committed to git; BM-0001 is not registered in `research/experiments/registry/` |
| **Execution state** | The locked protocol went to execution: 28 BAM passes launched with full provenance capture; half complete and still running, with an unexplained base-modification parse error in every log | T7 | Single operational capability, distinct reader decision from the design theme: this one is about whether the run is healthy, not about whether the design is sound | 1,935 `[E::bam_parse_basemod2] MM/MN data length is incompatible with SEQ length` in one 25× pass; 14 of 28 passes complete at 16:39 (all exit 0, ~580 s each); `workflow_state.yaml` still `EXECUTION`, `execution_iteration: 0` | Smoke test never validated against the prior EXP-S1-022 result; exploratory COLO829 chr1 arm declared but not launched; QC stage not entered |

## Coverage checklist

| Task | Theme |
|---|---|
| T1 four-signal roles | Signal inventory |
| T2 SIMMA citation rule | Signal inventory |
| T3 9 ng two denominators | Signal inventory |
| T4 DNA vs genome | Signal inventory (supporting; no page of its own) |
| T5 lifecycle to LOCK | Protocol governance |
| T6 control-design corrections | Protocol governance |
| T7 execution launch | Execution state |

Every task is in a theme. No task was excluded.
