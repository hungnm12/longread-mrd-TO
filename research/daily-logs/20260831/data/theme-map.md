# Theme map — 2026-08-31

**Through-line.** Two threads ran in parallel and converged on the same sentence: the only ONT
signal this thesis can honestly add to its SNV baseline is methylation, and it has to be tested
as its own preregistered experiment — and by the end of the day that experiment existed, was
locked against its own results, ran to completion, returned a preregistered `H1 SUPPORTED` —
and was sent back by its own QC because the criterion carrying the mechanism claim turned out to
be passed by the control it was written to exclude.

| Theme | Theme summary | Tasks | Why they are one theme | Representative evidence | Open items |
|---|---|---|---|---|---|
| **Signal inventory** | Settled which ONT signals the lab's tumour/normal dilution data can carry, in what role, with the low-TF arithmetic that justifies it and the citation rule for the paper it came from | T1, T2, T3, T4 | All four advance one end goal — what this thesis may claim about each signal. T3 is the quantitative backing for T1's methylation verdict; T2 fixes how the source paper may be cited in the same argument; T4 supplies vocabulary the other three use | Four-signal role table; 0.27 molecules vs 5,000,000 fragments from the same 9 ng; 65/792 = 8.2% ecDNA | Neither the role table nor the citation rule is written into `claim-boundaries.md` or the thesis draft yet |
| **Protocol governance** | An autonomous design ↔ adversarial-review loop turned a research question into a protocol frozen at v1.0, closing 14 blocking findings including two that would have made the benchmark unable to answer its own question | T5, T6 | T6 is the content of T5's loop; together they form one deliverable (`protocols/v1.0_locked.md`) and one decision (what counts as success) | 8 → 3 → 2 → 1 → 0 blocking issues over five reviews; B001 degenerate control; B014 aggressiveness confound; S4 added; reviewer's self-correcting addendum | Nothing committed to git; BM-0001 is not registered in `research/experiments/registry/` |
| **Execution & QC** | The locked protocol ran clean (42 passes, 0 failures, leakage verified by evidence, EXP-S1-022 reproduced to four figures) and returned `H1 SUPPORTED` — which QC preserved verbatim while ruling `REDESIGN_REQUIRED`, because S4 is satisfied identically by the CpG-density control | T7, T8, T9 | One lifecycle stage feeding the next: T7 produces the numbers T8 scores against the frozen criteria, and T9 is the verification of that same scoring. Together they answer one question — is the registered result usable? | S1–S4 all HELD; B1 vs C2 retention 1.6741 vs 1.6839 and 2.9127 vs 2.9041; gated totals B1 22–28 vs C1/C2 1–3; detection changed in 1 of 4 cells | Protocol v1.1 not drafted; the retention sweep not run; MM/ML missingness rule still undefined; nothing committed |

## Coverage checklist

| Task | Theme |
|---|---|
| T1 four-signal roles | Signal inventory |
| T2 SIMMA citation rule | Signal inventory |
| T3 9 ng two denominators | Signal inventory |
| T4 DNA vs genome | Signal inventory (supporting; no page of its own) |
| T5 lifecycle to LOCK | Protocol governance |
| T6 control-design corrections | Protocol governance |
| T7 execution of the locked protocol | Execution & QC |
| T8 registered outcome H1 SUPPORTED | Execution & QC |
| T9 QC review, REDESIGN_REQUIRED | Execution & QC |

Every task is in a theme. No task was excluded.
