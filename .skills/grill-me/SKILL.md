---
name: grill-me
description: Stress-test a plan, claim or interpretation by attacking its weakest point until it holds or breaks. Use when the user says "grill me", "poke holes", "is this right", or before presenting a result to the professor.
---

# Grill me

Adversarial review of the user's own reasoning. The goal is to find the failure here, at zero
cost, rather than in the meeting.

## Method

Ask one question at a time and wait for the answer. Follow the weakest answer, not the list.

1. **What would this look like if it were false?** If the answer is "the same", the design is
   not discriminating and nothing else matters.
2. **What is the denominator?** Of what total is this a fraction, and is that the total the
   claim implies?
3. **What is the control?** Against what blank or ablation is this measured?
4. **Which step is doing the work?** If several were added at once, the attribution is unknown.
5. **What would the professor ask?** Usually: sample size, generalisation, and what was
   compared to what.
6. **Which guardrail is closest to being crossed?** PASS ≠ somatic, filtered ≠ false positive,
   VAF ≠ tumor fraction, coverage ≠ sensitivity, cell line ≠ plasma.

## Rules

- Do not accept an answer that restates the claim more confidently.
- Do not soften because the work is the project's own.
- End with the single objection most likely to be raised, and whether it currently has an
  answer.
