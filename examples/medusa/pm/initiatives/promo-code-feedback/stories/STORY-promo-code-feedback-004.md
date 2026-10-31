---
id: STORY-promo-code-feedback-004
type: story
title: "Spike: one way to report dropped codes on every cart route"
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, EPIC-promo-code-feedback-02, TI-promo-code-feedback]
epic: EPIC-promo-code-feedback-02
requirements: [R3]
priority: p2
estimate: null
capabilities: [CAP-cart]
code_refs:
  - packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts
tracker:
  system: null
  key: null
---

# Spike: one way to report dropped codes on every cart route

**As a** tech lead **I want** a time-boxed investigation of how to report dropped codes
**so that** STORY-promo-code-feedback-005 can be estimated and built once, not per route.

Time box: two days.

## Acceptance criteria

**AC1: Routes listed**
- Given the store cart routes
- When the spike is done
- Then there is a list of every route that runs the cart refresh, which can drop codes

**AC2: Approach decided**
- Given the options in tech impact Questions 4 and 5
- When the spike is done
- Then one approach is chosen, written up as a decision in `pm/decisions/`, and linked here

## Notes for engineering

- Codes are re-checked with "replace" on every item change `packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts:242-249`

## Out of scope

- Building it (STORY-promo-code-feedback-005).

## Dependencies

- None.
