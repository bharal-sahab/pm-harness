---
id: EVAL-<slug>-taxonomy
type: eval
title: <Feature> - Failure taxonomy
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [PRD-<slug>]
---

# <Feature>: how it fails

**Data:** <n> traces from <source, dates>. Labeled by <PM name>. Pass rate: <x%>.

| Failure mode | Definition | Traces | % of traces | Risk | How we catch it |
|--------------|------------|--------|-------------|------|-----------------|
| <name> | <one line, observable> | <n> | <x%> | high/med/low | fix / code check / judge |

## <Failure mode name>

**Definition:** <precise, observable>
**Fail example:** <trace ID>: <short excerpt and why it fails>
**Pass example:** <trace ID>: <short excerpt and why it passes>
**Likely cause:** <prompt, retrieval, data, model, product logic, or unknown>
**Decision:** <fix now (story link) | code check (what it checks) | judge ([judge](judges/<mode>.md))>
