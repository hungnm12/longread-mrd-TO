---
id: GLOSSARY-004
term: MM/ML tags
short_definition: SAM tags carrying per-base modification calls read natively off the molecule — no bisulfite conversion.
---

`MM:Z:` lists which bases carry a modification and which modification code, as deltas counting the
skipped bases of that type. `ML:B:C,` carries the matching probabilities as bytes.

Dorado 5mCG/5hmCG basecalling emits two codes at every called CpG: `C+m` for 5-methylcytosine and
`C+h` for 5-hydroxymethylcytosine. They are complementary rather than independent — their sum plus
P(unmodified) is one — and this project keeps them separate throughout rather than summing them.

The byte `q` represents the probability interval `[q/256, (q+1)/256)`, so it is decoded to the
interval midpoint `(q + 0.5) / 256`.
