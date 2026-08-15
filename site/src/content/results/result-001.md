---
id: RESULT-001
title: Week 1 tumor-only candidate landscape baseline
status: observed
evidence_level: preliminary
experiment_id: EXP-001
run_id: RUN-001
weekly_reports: [WEEK-001]
observation: 48,819 PASS SNVs were retained from 3,169,996 total ClairS-TO records, with median depth 80, median VAF 0.461, and median ALT support 35.
interpretation: The retained set has substantial read support for descriptive characterization, but those distributions do not by themselves establish somatic truth or low-tumor-fraction sensitivity.
caveats:
  - PASS is a caller retention label, not a truth label.
  - The reported numbers are preliminary until tied back to the upstream execution manifest and logs where needed.
  - The selection funnel is not a false-positive-rate estimate for filtered calls.
denominator: All 3,169,996 ClairS-TO records from the referenced tumor-only run.
metric_definition: PASS SNV proportion is PASS SNVs divided by total ClairS-TO records; distribution summaries are medians and interquartile ranges over retained PASS SNVs.
takeaway: Week 1 has a defensible descriptive baseline and should now move into reliability characterization instead of deeper biological interpretation.
last_verified: null
datasets: []
tools: []
papers: [PAPER-001]
risks: [RISK-001, RISK-002]
---

The result is intentionally modest: it documents the candidate landscape and keeps the caveats
attached to the numbers. That makes it useful for a weekly report while preventing accidental
promotion of descriptive statistics into a stronger biological claim.
