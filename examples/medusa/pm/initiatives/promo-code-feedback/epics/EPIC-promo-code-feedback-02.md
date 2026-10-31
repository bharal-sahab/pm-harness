---
id: EPIC-promo-code-feedback-02
type: epic
title: Shoppers learn when a code stops applying
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, TI-promo-code-feedback]
requirements: [R3, R5]
priority: p2
capabilities: [CAP-cart, CAP-promotions]
tracker:
  system: null
  key: null
---

# Shoppers learn when a code stops applying

**Outcome:** When a cart change removes a code that was applied, the shopper can be told
right away instead of discovering it at payment.

**Requirements:** R3, R5 from [the PRD](../prd.md)

## Stories

| Story | Title | Priority | Requirements |
|-------|-------|----------|--------------|
| [STORY-promo-code-feedback-004](../stories/STORY-promo-code-feedback-004.md) | Spike: one way to report dropped codes on every cart route | p2 | R3 |
| [STORY-promo-code-feedback-005](../stories/STORY-promo-code-feedback-005.md) | Report codes removed by a cart change | p2 | R3, R5 |

## Done when

- Both stories are accepted, and the feature flag is on by default in the next minor version.
