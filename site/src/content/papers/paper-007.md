---
id: PAPER-007
title: Ultrasensitive plasma-based monitoring of tumor burden using machine learning-guided signal enrichment
local_filename: nihms-2005923.pdf
pdf_available: false
status: observed
evidence_level: external_report
sequencing_modality: Plasma monitoring with ML-guided enrichment
strategy: Tumor-only or tumor-naive comparison point
signal_modalities: [SNV, CNA, ML enrichment]
reusable_module: A comparison point for tumor-only or plasma-only monitoring strategies and selective signal enrichment.
non_transferable_module: The exact machine-learning design and plasma workflow are not yet aligned to the local long-read baseline.
limitations:
  - Indexed from the brief summary only.
  - Specific model behavior and reported performance are still unverified locally.
role_in_map: Counterpoint for future tumor-only and tumor-naive strategy decisions.
---

## Problem

How to enrich weak plasma-based tumor signals without depending entirely on a classic tumor-informed
panel workflow.

## Transfer map

- **Reusable now:** a future comparison point when deciding how far tumor-only signal enrichment should go.
- **Not transferable yet:** any direct ML method reuse without local data alignment and explicit evaluation.
