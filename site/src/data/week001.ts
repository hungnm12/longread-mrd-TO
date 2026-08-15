import summary from "../../../research/manifests/week-001-candidate-landscape.json";

const totalCalls = summary.summary.total_calls;
const passSnvs = summary.summary.pass_snvs;
const filteredCalls = totalCalls - passSnvs;

export const candidateLandscape = {
  ...summary,
  displaySources: [
    "mrd-longphase/results/tumor_only/HCC1395/variant_summary.tsv",
    "mrd-longphase/results/tumor_only/HCC1395/qc_stats.txt",
    "mrd-longphase/reports/weekly/2026-08-13_hcc1395_phase1_tumor_only.md"
  ],
  funnel: [
    { label: "Total ClairS-TO calls", count: totalCalls, pct: 100 },
    { label: "Filtered out of PASS SNV set", count: filteredCalls, pct: 98.46 },
    { label: "PASS SNVs retained for Week 1", count: passSnvs, pct: summary.summary.pass_snv_fraction_pct }
  ],
  distributions: [
    {
      label: "Depth",
      median: summary.summary.median_depth,
      q25: summary.summary.depth_q25,
      q75: summary.summary.depth_q75,
      unit: "reads"
    },
    {
      label: "VAF",
      median: summary.summary.median_vaf,
      q25: summary.summary.vaf_q25,
      q75: summary.summary.vaf_q75,
      unit: "fraction"
    },
    {
      label: "ALT support",
      median: summary.summary.median_alt_support,
      q25: summary.summary.alt_support_q25,
      q75: summary.summary.alt_support_q75,
      unit: "reads"
    }
  ],
  notes: [
    "PASS is a caller-level retention label, not a biological truth label.",
    "The 1.54% figure is a selection funnel, not a false-positive rate.",
    "High source-sample coverage does not establish low tumor-fraction detection capability."
  ]
};
