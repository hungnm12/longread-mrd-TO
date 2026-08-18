// Related-work comparison rows for section 4 of the narrative.
//
// One row per supplied study. The columns are fixed by the comparison the thesis needs to
// make — problem, evidence modality, strategy, contribution, and the limitation that is
// relevant *here* — so that the table reads as an argument rather than as seven summaries.
//
// Deliberately absent: any performance number. The studies use different assays, sample
// types, and cohorts; placing their reported sensitivities side by side would imply a
// comparison the data does not support.

export interface RelatedWorkEntry {
  /** Citation key from src/data/references.ts. */
  ref: string;
  name: string;
  problem: string;
  modality: string;
  strategy: string;
  contribution: string;
  limitation: string;
}

/**
 * Maps a `papers` collection id to its citation key, so the notes area can show the number
 * a reader saw on the narrative page instead of an internal PDF filename.
 */
export const paperIdToRefKey: Record<string, string> = {
  "PAPER-001": "mrdetect",
  "PAPER-002": "nanorcs",
  "PAPER-003": "ont-cfdna-methyl",
  "PAPER-004": "ont-realtime",
  "PAPER-005": "methyl-fragmentation",
  "PAPER-006": "phased-seq",
  "PAPER-007": "mrd-edge"
};

export const relatedWork: RelatedWorkEntry[] = [
  {
    ref: "mrdetect",
    name: "MRDetect",
    problem:
      "A single mutated locus carries too little evidence to monitor disease when tumor content is very low.",
    modality: "Genome-wide SNVs from cell-free DNA",
    strategy:
      "Integrate weak evidence across a very large number of patient-specific sites instead of sequencing few sites deeply.",
    contribution:
      "Established breadth-over-depth: many individually unconvincing observations can be aggregated into one monitoring readout.",
    limitation:
      "Aggregation operates over loci, not within a molecule; each read contributes one allele observation and nothing else."
  },
  {
    ref: "mrd-edge",
    name: "MRD-EDGE",
    problem:
      "Genome-wide cell-free DNA sequencing produces far more background artefacts than true tumor observations.",
    modality: "SNVs and copy-number variation, with learned classification",
    strategy:
      "Use machine-learning-guided signal enrichment to rank candidate observations by how tumor-like their local features are.",
    contribution:
      "Showed that learned suppression of background can be applied before aggregation, rather than relying on filters alone.",
    limitation:
      "The learned feature space is built from short-read sequence context; native base modifications are not part of it."
  },
  {
    ref: "phased-seq",
    name: "PhasED-Seq",
    problem:
      "Independent sequencing errors are hard to separate from single true mutations at very low tumor content.",
    modality: "Multiple somatic variants observed in phase on the same molecule",
    strategy:
      "Require co-occurrence of linked variants, so that background must fail twice on the same fragment to imitate signal.",
    contribution:
      "Demonstrated molecular linkage as a background-suppression principle, and reported it inside an analytical validation framework.",
    limitation:
      "Requires two or more variants on one fragment — availability that falls exactly where tumor content is lowest."
  },
  {
    ref: "ont-realtime",
    name: "Real-time nanopore cfDNA genome and fragmentome analysis",
    problem:
      "Genomic and fragment-level readouts from liquid biopsy are usually separate, slow assays.",
    modality: "Copy-number and cell-free DNA fragmentation from nanopore reads",
    strategy:
      "Analyse the genome and the fragmentome directly from native nanopore sequencing, as data arrives.",
    contribution:
      "Showed that long-read platforms give access to molecule-level properties without a dedicated additional assay.",
    limitation:
      "Focuses on copy-number and fragmentation; it does not address single-nucleotide evidence at low tumor fraction."
  },
  {
    ref: "nanorcs",
    name: "NanoRCS",
    problem:
      "Per-read nanopore error rates limit how confidently a single molecule can be called tumor-derived.",
    modality: "Consensus-corrected long reads carrying SNV, copy-number, and fragmentomic signal",
    strategy:
      "Raise per-molecule accuracy through rolling-circle consensus, then estimate tumor fraction from several signal classes at once.",
    contribution:
      "Combined higher read accuracy with multimodal estimation on one long-read platform.",
    limitation:
      "The combined modalities are sequence-level and fragment-level; haplotype context and native methylation are not the axes being combined."
  },
  {
    ref: "methyl-fragmentation",
    name: "Methylation and cell-free DNA fragmentation",
    problem:
      "It is unclear what actually determines where cell-free DNA fragments break.",
    modality: "DNA methylation and gene expression against genome-wide fragmentation",
    strategy:
      "Relate fragmentation patterns to the underlying epigenetic and transcriptional state.",
    contribution:
      "Provided evidence that methylation and fragmentation are biologically coupled rather than independent readouts.",
    limitation:
      "A caution for any design that stacks modalities: coupled evidence added twice inflates apparent confidence."
  },
  {
    ref: "ont-cfdna-methyl",
    name: "Oxford Nanopore cfDNA methylation requirements",
    problem:
      "Methylation measured on cell-free DNA is sensitive to how the library was prepared.",
    modality: "Native methylation calling on nanopore cell-free DNA",
    strategy:
      "Specify the pre-analytical and library-preparation requirements under which cfDNA methylation profiling is supported.",
    contribution:
      "Makes protocol dependence explicit, so methylation evidence can be treated as conditional on preparation rather than absolute.",
    limitation:
      "A technical requirements document, not a detection study: it constrains interpretation without supplying comparative evidence."
  }
];
