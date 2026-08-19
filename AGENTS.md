# Agent Operating Rules

1. Never modify the research hypothesis unless explicitly authorized.
2. Never bypass a human gate.
3. Never silently change thresholds after observing results.
4. Never use truth labels during feature construction unless the experiment explicitly permits it.
5. Never modify raw source data.
6. Every result must record:
   - input
   - configuration
   - software version
   - command
   - output
   - experiment ID
7. Failed experiments are scientific evidence and must not be deleted.
8. Observation, interpretation, and conclusion must be separated.
9. Agents may only write to directories permitted for their role.
10. Orchestrator coordinates work but cannot make scientific decisions reserved for the human.