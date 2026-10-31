---
id: STORY-promo-code-feedback-005
type: story
title: Report codes removed by a cart change
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, EPIC-promo-code-feedback-02, TI-promo-code-feedback]
epic: EPIC-promo-code-feedback-02
requirements: [R3, R5]
priority: p2
estimate: null
capabilities: [CAP-cart, CAP-promotions]
code_refs:
  - packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts
  - packages/medusa/src/feature-flags/translation.ts
tracker:
  system: null
  key: null
---

# Report codes removed by a cart change

**As a** shopper **I want** to be told when a change to my cart removes a discount **so
that** I am not surprised by the price at payment.

## Acceptance criteria

**AC1: Removing an item drops a code**
- Given a cart with `SPEND50` applied, which needs a subtotal of at least 50
- And the cart subtotal is 60
- When the shopper removes an item worth 20
- Then the response says `SPEND50` was removed with the reason "conditions not met"

**AC2: A code that still applies is not reported**
- Given a cart with `WELCOME5` applied and no conditions
- When the shopper changes an item quantity
- Then no removed codes are reported

**AC3: Flag off means no change**
- Given the feature flag for this behavior is off
- When the shopper removes an item that drops `SPEND50`
- Then the response is exactly as it is today

**AC4: Old clients keep working**
- Given the flag is on and a client that reads only `cart`
- When any cart change drops a code
- Then the client receives the same `cart` as before this change

## Notes for engineering

- Approach comes from STORY-promo-code-feedback-004.
- Feature flags follow the one-file-per-flag pattern `packages/medusa/src/feature-flags/translation.ts`

## Out of scope

- Automatic promotions that stop applying (the shopper did not enter them).

## Dependencies

- STORY-promo-code-feedback-004 and STORY-promo-code-feedback-001.
