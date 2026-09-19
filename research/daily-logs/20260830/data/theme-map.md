# Theme map — 2026-08-30

**Through-line:** a first serious read of the SIMMA preprint was converted into a defensible thesis
position — what the paper claims, where it stops, and which of the user's own sentences would not
survive a reviewer — and then the material on disk was inventoried so the remaining gap can be tested.

| Theme | Theme summary | Tasks | Why one theme | Representative evidence | Open items |
|---|---|---|---|---|---|
| **A. What SIMMA claims, and the hole it leaves** | The seven problems were ordered into a dependency chain with P5 as the load-bearing hinge, and P5(b) — no computational method for multimodal integration — was identified as where the thesis sits | T1, T2 | Both advance the same end goal (a correct statement of the paper's problem space) and T2 is a correction inside T1's structure | P1–P5 chain; SIMMA fills P5(b) at sample level, leaving molecule level open | Whether "same-molecule co-occurrence" novelty still holds needs a re-search dated at submission |
| **B. What SIMMA actually does** | One library prep split into a WGS branch and an optional 76-gene targeted branch yields four signals from a single nanopore run, analysed by COPYBARA / SAVANA+hifiasm / RF+conformal prediction | T3, T4 | T4 states the constraint (N assays need N aliquots) that T3's protocol is the answer to; together they form one mechanism description | 5 ng input, R=0.97 yield vs load, 2,282x consensus depth, ~5e-4 error, COPYBARA at 0.5x mean coverage | Two caveats must be carried into thesis text and are not yet written down |
| **C. Claims that must survive the defence** | Two of the user's own framings were overturned — "short-read cannot dig into plasma biology" and "ecDNA is a free 24th chromosome" — and replaced with claims that hold under questioning | T5, T6 | Both are corrections of the user's framing rather than of the paper, both feed the same deliverable (a set of defensible thesis sentences), and both were prompted by the user's own questions | Short-read discovered ~167 bp nucleosome periodicity, tumour-shortening, end motifs; bisulfite costs 80–95% of material; ecDNA is acentric | EM-seq / Duet / TAPS must be named in the thesis; ecDNA scope question to put to the professor |
| **D. Note correction loop on 30.md** | Four issues in the user's own note were named against the paper's wording, a copy-over rewrite was supplied, and the user applied part of it the same day | T7 | Single deliverable (a citable note) with a measurable follow-through state | 4 flagged → 2 fixed, 1 partly fixed, 1 unfixed on disk at 20:56 | Specificity clause still conflated; "cannot be sampled serially" and the "not peer reviewed" caveat still absent |
| **E. Material on disk and the operating point it forces** | The disk holds two full 14-BAM dilution series (~2.1 TB) rather than the one the docs record, and the "which signal is better" question was immediately gated behind a paper-arithmetic check at 25x, TF=1e-4 | T8, T9 | T9's Question 1 is posed directly on the material T8 inventoried; together they answer "what can I actually test, and at what operating point" | 14 BAM × 2 cell lines, `.meta.json` provenance, depth ~25.0x, `MM/ML=present`; COLO829_PAO created 2026-08-23/24, absent from `datasets.md` (2026-08-19) | Config registry drift unfixed; Question 1 unanswered |

## Coverage checklist

| Task | Theme |
|---|---|
| T1 | A |
| T2 | A |
| T3 | B |
| T4 | B |
| T5 | C |
| T6 | C |
| T7 | D |
| T8 | E |
| T9 | E |

No task excluded.
