---
id: EVAL-<slug>
type: eval
title: <Feature> - Eval plan
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [PRD-<slug>, EVAL-<slug>-taxonomy]
owner: <PM name>
---

# <Feature>: eval plan

**Goal of the feature:** <one sentence>
**What good means:** <the user's bar, in plain language>

## Evaluators

| Failure mode | Evaluator | Type | Validated | Runs |
|--------------|-----------|------|-----------|------|
| <mode> | <check name or [judge](judges/<mode>.md)> | code / judge | TPR <x>, TNR <y> | CI / nightly / on release |

## Launch thresholds

| Failure mode | Risk | Today | Threshold to launch |
|--------------|------|-------|---------------------|
| <mode> | high | <x%> | 0% |
| <mode> | low | <x%> | <= <y%> |

## Monitoring after launch

- Read <n> production traces every <week>; reader: <name>.
- Re-run error analysis after any change to the model, prompt, retrieval, or data.
- Alert when <metric> passes <threshold>.

## Data

- Traces: <where they are stored; retention; personal data handling>
- Labels: `labels.csv` (<n> traces), splits in `splits/`
