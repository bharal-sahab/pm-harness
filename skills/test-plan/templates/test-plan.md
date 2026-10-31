---
id: TP-<slug>
type: test-plan
title: <Initiative title> - Test plan
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [PRD-<slug>, TI-<slug>, EPIC-<slug>-01]
capabilities: [CAP-<slug>]
---

# <Initiative title>: test plan

**Scope:** <stories covered>. **Out of scope:** <PRD non-goals>.
**Environments and flags:** <where to test; feature flag states to test>

## Test cases

| ID | Covers | Level | Source | Preconditions and data | Steps | Expected |
|----|--------|-------|--------|------------------------|-------|----------|
| TC-01 | STORY-<slug>-001/AC1 | API | story | <state with concrete values> | <steps> | <observable result> |
| TC-02 | - | API | derived: `<path:line>` | <state> | <steps> | <result> |

## Regression

| Area | Why | How |
|------|-----|-----|
| <journey or consumer> | <shares the touched code> `<path>` | <existing test file, or manual check> |

## Non-functional checks

- <Only those that matter, with the threshold from the PRD guardrails>

## Exploratory charters

1. <Explore X, using Y, looking for Z> (time box: 30 minutes)

## Test data

- <Records to create first: products, promotions, users, with their settings>

## Exit criteria

- Every test case passes, or has a ticket and an accepted risk.
- <Guardrail metrics within threshold>
