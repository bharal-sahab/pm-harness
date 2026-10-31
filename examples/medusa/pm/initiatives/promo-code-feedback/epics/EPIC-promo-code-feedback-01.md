---
id: EPIC-promo-code-feedback-01
type: epic
title: Shoppers learn why a code they entered did not apply
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, TI-promo-code-feedback]
requirements: [R1, R2, R4, R5]
priority: p1
capabilities: [CAP-promotions]
tracker:
  system: null
  key: null
---

# Shoppers learn why a code they entered did not apply

**Outcome:** Every code a shopper enters either applies or comes back with a reason a
storefront can show.

**Requirements:** R1, R2, R4, R5 from [the PRD](../prd.md)

## Stories

| Story | Title | Priority | Requirements |
|-------|-------|----------|--------------|
| [STORY-promo-code-feedback-001](../stories/STORY-promo-code-feedback-001.md) | Return the reasons Medusa already knows | p1 | R1, R5 |
| [STORY-promo-code-feedback-002](../stories/STORY-promo-code-feedback-002.md) | Explain codes that are not valid, expired, or not started | p1 | R2, R4 |
| [STORY-promo-code-feedback-003](../stories/STORY-promo-code-feedback-003.md) | Explain codes the cart does not qualify for | p1 | R2, R4 |

## Done when

- All three stories are accepted and documented in the Store API reference.
- Failed code entries are logged, so the PRD's primary metric can be measured.
