---
id: GLOSSARY-003
term: Haplotag (HP/PS)
short_definition: The HP tag assigns a read to a haplotype; the PS tag names the phase block that assignment is relative to.
---

Phasing tools such as LongPhase and WhatsHap write two tags onto each read they can place:

- `HP:i:1` or `HP:i:2` — which of the two haplotypes the read was assigned to
- `PS:i:<int>` — the **phase set**, the block of the genome within which that assignment holds

`HP` is meaningful only **within** its `PS`. Phase blocks are independently oriented, so haplotype 1
in one phase set has no relationship to haplotype 1 in another. Grouping on `HP` alone silently
pools unrelated haplotypes; the sound grouping key is the pair `phase_set:haplotype`.

Haplotype consistency is evidence compatible with somatic origin. It does not demonstrate it.
