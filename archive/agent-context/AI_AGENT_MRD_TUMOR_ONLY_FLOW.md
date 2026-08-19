# AI Agent Execution Plan — Tumor-Only Long-Read MRD Research Flow

## 0. Mission

Build the research workflow from the **current HCC1395 tumor-only SNV candidate analysis** toward a **tumor-only MRD baseline for long-read sequencing**, **without requiring a matched-normal sample in the core pipeline**.

The AI agent must:

1. inspect the existing repository before changing anything;
2. reuse the repository's predefined folders and naming conventions;
3. implement analysis code incrementally;
4. update documentation and weekly-report artifacts after each completed phase;
5. preserve reproducibility and traceability;
6. never modify the source BAM/reference in place;
7. avoid adding matched-normal data as a required dependency;
8. separate **observation**, **interpretation**, **hypothesis**, and **validation** in all outputs.

The research question driving the whole workflow is:

> **Can reliable tumor-specific MRD markers be constructed from long-read tumor-only sequencing, and how well can those markers detect progressively lower tumor fractions before long-read-specific evidence such as phasing and methylation is added?**

---

# 1. Current starting point

Current analysis context:

- Sample: HCC1395 tumor-only
- Sequencing: ONT R10, 5 kHz simplex
- Caller: ClairS-TO v0.5.0
- Current report population:
  - total ClairS-TO VCF records: `3,169,996`
  - PASS SNVs: `48,819`
  - PASS proportion: approximately `1.54%`
  - median VAF: `0.461`
  - VAF IQR: `0.29–0.78`
  - median candidate-locus depth: `80x`
  - depth IQR: `59–106x`

Important interpretation:

- `PASS` means the call passed the current ClairS-TO workflow and filters.
- `PASS` does **not** mean confirmed somatic.
- The `48,819` PASS SNVs define the current candidate population to characterize.
- Do not treat the remaining ~98.46% of VCF records as automatically false variants or rescue targets.

Known read-only input locations currently used in the project:

- Tumor BAM: `/big8_disk/data/HCC1395/ONT_5khz_simplex_5mCG_5hmCG/HCC1395.bam`
- Reference: `/big8_disk/ref/GRCh38_no_alt_analysis_set.fasta`

These source files must never be modified.

---

# 2. Core research flow

```text
Tumor-only HCC1395
        │
        ▼
PHASE 1 — Candidate landscape characterization
        │
        ▼
PHASE 2 — Candidate reliability analysis
        │
        ▼
PHASE 3 — Tumor-only marker qualification
        │
        ▼
PHASE 4 — Tumor-only MRD SNV baseline
        │
        ▼
PHASE 5 — Low tumor-fraction detection
        │
        ▼
PHASE 6 — Error-aware evidence aggregation
        │
        ▼
PHASE 7 — Phased long-read evidence
        │
        ▼
PHASE 8 — Native methylation evidence
        │
        ▼
PHASE 9 — Multimodal MRD model
        │
        ▼
PHASE 10 — LoB / LoD / specificity / ablation
        │
        ▼
Master's thesis results
```

Matched-normal data are **not part of this core execution path**.

If a matched-normal or truth set is introduced later, it must be treated as an **external benchmark/evaluation source**, never as an input required to construct the tumor-only marker set.

---

# 3. Repository handling rules

Before writing code:

1. inspect the repository root;
2. list existing folders;
3. identify where the repository already stores:
   - source code;
   - scripts;
   - configs;
   - notebooks;
   - docs;
   - results;
   - reports;
   - tests;
4. map each requested output to the closest existing folder;
5. do **not** create a parallel folder tree if an equivalent predefined folder already exists.

If a required category does not exist:

- first search for an equivalent directory;
- only create a new directory if there is no reasonable existing location;
- document why the directory was created.

Never rename or delete existing directories unless explicitly instructed.

---

# 4. Automatic update policy

For every completed phase, the agent must update all applicable repository artifacts.

## 4.1 Code

Update or add:

- analysis scripts;
- reusable modules;
- configuration files;
- workflow entry points;
- tests where practical.

Code requirements:

- deterministic where possible;
- CLI arguments instead of hard-coded analysis thresholds;
- input/output paths configurable;
- clear logging;
- fail early on missing files;
- preserve raw inputs;
- write derived artifacts to repository-defined output/results locations.

## 4.2 Documentation

Update the repository's existing documentation location with:

- current research question;
- method;
- inputs;
- outputs;
- parameter definitions;
- assumptions;
- interpretation limits;
- completed findings;
- unresolved questions;
- next phase.

If the repo has a main `README`, update only the section relevant to this workflow. Do not turn the README into a full lab notebook.

## 4.3 Weekly research report notes

After every phase, create/update the existing weekly-report location using this structure:

```text
Research question
↓
Why it matters
↓
Experiment / analysis
↓
Observation
↓
Interpretation
↓
Limitations
↓
Decision
↓
Next research question
```

Do not write weekly notes as a task log.

Bad:

- installed package;
- ran script;
- generated plot.

Good:

- candidate depth is concentrated while VAF is broad;
- this indicates depth and allele composition describe different properties;
- somatic identity is not established by these observations.

## 4.4 Change log

Maintain or update an existing change log / experiment log if present.

Each change should record:

- date;
- phase;
- files changed;
- command used;
- key parameters;
- output paths;
- result summary;
- known limitations.

---

# 5. PHASE 1 — Tumor-only candidate landscape characterization

## Research question

> **What does the tumor-only PASS SNV candidate landscape look like?**

## Goal

Describe the retained candidate population before attempting biological interpretation.

## Required analyses

### A. Candidate count

Report:

- total VCF records;
- PASS SNV count;
- PASS proportion.

Interpretation:

- candidate count describes the size of the retained analysis population;
- it does not indicate somatic truth.

### B. Read-depth landscape

Compute:

- median;
- Q1;
- Q3;
- IQR;
- 5th/95th percentile if useful;
- histogram.

Interpretation:

- depth describes how much sequencing evidence is available at each candidate locus.

Avoid claims such as "adequate" or "sufficient" unless a threshold is explicitly defined.

### C. VAF landscape

Compute:

- median;
- Q1;
- Q3;
- IQR;
- histogram.

Interpretation:

- VAF describes how allele support is divided between REF and ALT reads;
- broad VAF does not establish biological origin.

### D. ALT-support landscape

Compute absolute ALT-supporting read counts.

Required outputs:

- ALT count distribution;
- median ALT support;
- IQR;
- relation to VAF and depth.

### E. Relationships

Generate at minimum:

- VAF vs DP;
- ALT count vs DP;
- optionally QUAL vs VAF if QUAL is readily available.

Purpose:

- determine whether observed allele-fraction variation can be trivially explained by coverage variation;
- do not assign biological categories yet.

## Required Phase 1 artifacts

Use existing repo directories and create/update equivalents of:

- candidate summary table;
- candidate-level analysis table;
- VAF histogram;
- depth histogram;
- ALT-support histogram;
- VAF-vs-depth plot;
- short Week 1 interpretation document.

## Phase 1 completion criterion

The agent must be able to answer:

1. How large is the retained candidate population?
2. How much locus-level sequencing evidence supports candidates?
3. How broadly is ALT allele support distributed?
4. Is VAF variation obviously explained by read depth?
5. What is known vs still unresolved?

Do not proceed to Phase 2 until these answers are documented.

---

# 6. PHASE 2 — Candidate reliability analysis

## Research question

> **Which tumor-only candidate features are associated with potentially reliable or unreliable SNV calls?**

This phase still does not assume access to a matched normal.

## Candidate feature groups

### Sequence support

- DP;
- ALT count;
- VAF;
- QUAL;
- strand support if available;
- base-quality summaries if available;
- mapping-quality summaries if available.

### Sequence context

Where feasible:

- homopolymer context;
- repeat context;
- low-mappability region;
- local sequence complexity.

### Caller-derived information

Extract:

- FILTER;
- INFO annotations;
- FORMAT fields;
- ClairS-TO confidence-related fields available in the current VCF.

## Output

Build a candidate feature table suitable for downstream ranking.

Do **not** automatically label:

- high VAF = somatic;
- VAF ~0.5 = germline;
- VAF ~1 = LOH;
- low VAF = artifact.

These are hypotheses, not labels.

## Phase 2 completion criterion

Produce a documented set of measurable features that may help distinguish candidate reliability without matched-normal information.

---

# 7. PHASE 3 — Tumor-only marker qualification

## Research question

> **Can a high-confidence tumor marker set be constructed using tumor-only evidence?**

## Goal

Rank or filter the PASS candidates using only tumor-derived and external non-patient-specific information.

Possible evidence types:

- sequence support;
- caller confidence;
- locus-specific technical quality;
- population-frequency annotations if available;
- generic panel-of-normal information already built into ClairS-TO outputs if available;
- problematic-region annotations;
- repeat/homopolymer context;
- mappability;
- optional public/common germline databases.

## Important constraint

Do not use the patient's matched-normal sample to construct the marker set.

## Initial implementation

Start with an interpretable rule-based or weighted-ranking model.

Example conceptual score:

```text
marker_score =
    support_score
  + caller_confidence
  + locus_quality
  - technical_risk
  - common_germline_risk
```

Do not start with deep learning.

## Output

Create a tumor-only marker dictionary containing at minimum:

```text
marker_id
chrom
pos
ref
alt
DP
ALT_count
VAF
QUAL
FILTER
sequence_context
technical_flags
population_flags
marker_score
marker_tier
```

Recommended tiers:

- `TIER_1_HIGH_CONFIDENCE`
- `TIER_2_POSSIBLE`
- `TIER_3_HIGH_RISK`
- `UNRESOLVED`

These are marker-confidence tiers, not confirmed somatic-status labels.

---

# 8. PHASE 4 — Tumor-only SNV MRD baseline

## Research question

> **Using only tumor-only qualified SNV markers, how well can tumor signal be detected as tumor fraction decreases?**

## Goal

Establish the simplest comparator that all later long-read-specific methods must beat.

## Baseline method

Use only:

- selected SNV markers;
- ALT read evidence;
- no phasing;
- no methylation;
- no fragmentomics;
- no deep learning.

Possible sample-level score:

```text
MRD_score = Σ marker_weight_i × ALT_evidence_i
```

Start with a simple unweighted score as a reference, then compare with weighted scoring.

## Output

For every sample/dilution:

- number of informative markers covered;
- total tumor-allele observations;
- weighted/unweighted MRD score;
- estimated background;
- detection status under defined threshold.

---

# 9. PHASE 5 — Low tumor-fraction detection

## Research question

> **At what tumor fraction does SNV-only tumor signal become indistinguishable from background?**

## Dilution series

Use available tumor-only/mixture resources or construct synthetic analytical mixtures where scientifically valid.

Suggested levels:

```text
1%
0.5%
0.1%
0.05%
0.02%
0.01%
```

Add lower levels only if molecule sampling and coverage make them meaningful.

## Critical wording

Synthetic HCC1395 dilution is an **analytical low-tumor-fraction sequence-detection benchmark**, not full biological MRD validation.

Document this explicitly.

---

# 10. PHASE 6 — Error-aware evidence aggregation

## Research question

> **Can locus-specific error modeling reduce false tumor evidence at very low tumor fractions?**

Estimate, where possible:

```text
error_i = P(ALT_i | background)
```

Avoid relying on a single global ONT error rate.

Candidate weighting may then include:

```text
weight_i ∝ marker_confidence_i / expected_error_i
```

Compare:

- unweighted marker aggregation;
- confidence-weighted aggregation;
- error-aware aggregation.

---

# 11. PHASE 7 — Phased long-read evidence

## Research question

> **Does co-occurrence of multiple tumor-marker alleles on the same long-read molecule improve specificity over single-SNV evidence?**

Tasks:

1. phase compatible tumor-only variants;
2. identify marker pairs/sets that can occur on the same observed molecule;
3. extract same-molecule ALT evidence;
4. compare false-background and detection performance against SNV-only baseline.

Do not assume long genomic phase blocks are automatically observable in cfDNA.

Measure actual read-span compatibility.

---

# 12. PHASE 8 — Native methylation evidence

## Research question

> **Can native nanopore methylation provide orthogonal tumor evidence when SNV support is sparse?**

Use modified-base information already present or callable from the tumor dataset.

Potential feature types:

- CpG methylation state;
- regional methylation score;
- per-molecule methylation pattern;
- DMR-related evidence where defensible without matched normal.

Important:

Without a matched-normal sample, tumor-specific methylation claims must be conservative.

Possible alternatives:

- external normal references;
- public healthy methylation resources;
- tumor-vs-reference differential analysis;
- unsupervised/relative methylation features.

Document exactly which reference source is used.

---

# 13. PHASE 9 — Multimodal MRD model

## Research question

> **Does combining SNV, phase, and methylation evidence improve low-TF detection compared with the SNV-only baseline?**

Per-molecule feature vector may include:

```text
sequence_support
marker_confidence
phase_support
methylation_score
read_quality
mapping_quality
```

Start with an interpretable model:

- weighted likelihood;
- logistic regression;
- simple generalized linear model.

Only add more complex ML if the simple model establishes measurable signal.

---

# 14. PHASE 10 — Final evaluation

Required analyses:

- Limit of Blank (LoB);
- Limit of Detection (LoD);
- sensitivity;
- specificity;
- precision / FDR where meaningful;
- PR-AUC / ROC-AUC when appropriate;
- modality ablation.

## Required ablation

At minimum compare:

| Model | SNV | Error-aware | Phase | Methylation |
|---|---:|---:|---:|---:|
| A | ✓ |  |  |  |
| B | ✓ | ✓ |  |  |
| C | ✓ | ✓ | ✓ |  |
| D | ✓ | ✓ |  | ✓ |
| E | ✓ | ✓ | ✓ | ✓ |

Primary thesis comparison:

> Does adding long-read-specific evidence improve detection at fixed specificity over the tumor-only SNV baseline?

---

# 15. Optional external benchmark branch

This branch is optional and must not become a core dependency.

```text
Tumor-only marker set
        │
        ├── core downstream MRD analysis
        │
        └── optional external evaluation
                  │
                  ├── matched-normal evidence
                  └── truth set
```

Purpose:

- estimate how many tumor-only candidate/marker calls are truly somatic;
- estimate germline/technical contamination;
- compare tumor-only marker quality against a stronger reference;
- quantify the performance cost of not requiring matched normal.

If this branch is executed, report it as **evaluation**, not as a required marker-construction step.

---

# 16. Research claims the agent must NOT make prematurely

Do not claim:

- PASS = confirmed somatic;
- high VAF = clonal somatic;
- VAF ~0.5 = germline;
- VAF ~1 = LOH;
- 48,819 candidates are all MRD markers;
- ~98.46% non-PASS records are false;
- non-PASS records should be rescued without independent evidence;
- 80x candidate depth is sufficient for clinical MRD;
- synthetic dilution equals clinical MRD validation;
- multimodal integration improves detection before ablation proves it.

---

# 17. Weekly-report progression

The AI agent should automatically update the weekly-report documentation according to the following research sequence.

## Week 1

> **What does the tumor-only candidate landscape look like?**

Outputs:

- candidate count;
- VAF distribution;
- depth distribution;
- ALT-support distribution;
- VAF-vs-depth relationship;
- known vs unknown.

## Week 2

> **Which measurable tumor-only features are associated with candidate reliability?**

Outputs:

- candidate feature table;
- sequence-support/context analysis;
- proposed reliability features;
- no somatic-status overclaim.

## Week 3

> **Can tumor-only evidence be used to construct a high-confidence marker set?**

Outputs:

- marker scoring/tiering;
- marker dictionary;
- sensitivity analysis of thresholds.

## Week 4

> **How does an SNV-only tumor-informed MRD baseline behave as tumor fraction decreases?**

Outputs:

- baseline scoring;
- dilution curves;
- initial background analysis.

## Week 5

> **What limits low-TF detection?**

Outputs:

- background/error characterization;
- informative-marker counts;
- candidate LoB/LoD analysis.

## Week 6+

Proceed to:

- error-aware weighting;
- phasing;
- methylation;
- multimodal integration;
- ablation.

---

# 18. Required agent behavior after every run

After each execution cycle, the agent must print a concise structured summary:

```text
PHASE:
RESEARCH QUESTION:

FILES READ:
FILES CREATED:
FILES MODIFIED:

COMMANDS EXECUTED:

KEY RESULTS:

OBSERVATION:

INTERPRETATION:

LIMITATIONS:

NEXT RESEARCH QUESTION:

REPO DOCS UPDATED:
```

Do not end with only "task completed".

---

# 19. Implementation order for the next run

The next AI-agent run should focus only on **Phase 1**.

Execute in this order:

1. inspect repository structure;
2. identify the current ClairS-TO VCF and existing analysis scripts;
3. verify current reported counts rather than blindly trusting them;
4. construct a candidate-level PASS-SNV table;
5. compute summary statistics for:
   - candidate count;
   - DP;
   - VAF;
   - ALT count;
6. generate:
   - VAF histogram;
   - DP histogram;
   - ALT-count histogram;
   - VAF-vs-DP scatter;
7. compare calculated values with the current weekly report;
8. flag discrepancies instead of silently replacing numbers;
9. update code in the existing analysis/source directories;
10. update documentation in the predefined documentation/report directories;
11. write the Week 1 result summary;
12. stop before biological/somatic-status interpretation unless explicitly requested.

---

# 20. Phase 1 expected conclusion format

The agent should aim for a conclusion in this form, with values filled from verified analysis:

> The current ClairS-TO tumor-only workflow retains **N PASS SNV candidates** for characterization. Candidate loci show a median read depth of **X** with an IQR of **Q1–Q3**, while VAF has a median of **Y** with an IQR of **Q1–Q3**. Absolute ALT support and VAF-depth relationships further describe the sequencing evidence underlying these candidates. These results establish the tumor-only candidate landscape but do not yet determine somatic identity or MRD-marker suitability.

The next research question should be:

> **Which tumor-only measurable features are informative for candidate reliability?**

---

# 21. Definition of done for this AI-agent plan

The workflow is considered successfully implemented when:

- the repo contains reproducible code for all completed phases;
- each phase has a documented research question;
- outputs are stored in predefined repository locations;
- weekly documentation is automatically updated;
- raw input files remain untouched;
- configuration and thresholds are traceable;
- the tumor-only marker construction path does not require matched normal;
- optional matched-normal/truth evaluation is clearly isolated from the core pipeline;
- the final thesis can compare SNV-only baseline vs long-read-specific improvements using reproducible experiments.
