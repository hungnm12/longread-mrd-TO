# queue/

Handoff requests between agents. One YAML file per request:

```yaml
id: Q-0001
from: implementer
to: data-qc
stage: qc
item: EXP-H1-001
request: Confirm MM/ML parse rate on the 1e-3 dilution before the funnel run
blocking: true
created: 2026-08-19
```

An agent that needs something outside its permission grant writes here instead of taking it.
The orchestrator drains the queue; nothing else deletes from it.

Empty is the normal state.
