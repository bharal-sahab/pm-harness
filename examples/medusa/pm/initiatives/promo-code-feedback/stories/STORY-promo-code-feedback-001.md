---
id: STORY-promo-code-feedback-001
type: story
title: Return the reasons Medusa already knows when a code is not applied
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, EPIC-promo-code-feedback-01, TI-promo-code-feedback]
epic: EPIC-promo-code-feedback-01
requirements: [R1, R5]
priority: p1
estimate: null
capabilities: [CAP-promotions]
code_refs:
  - packages/medusa/src/api/store/carts/[id]/promotions/route.ts
  - packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts
  - packages/core/types/src/http/cart/store/responses.ts
tracker:
  system: null
  key: null
---

# Return the reasons Medusa already knows when a code is not applied

**As a** storefront developer **I want** the add-promotions response to list codes that
were not applied and why **so that** I can tell the shopper.

## Acceptance criteria

**AC1: Usage limit reached**
- Given a code `SUMMER10` with a usage limit of 100 that has been used 100 times
- When a shopper adds `SUMMER10` to their cart
- Then the response contains the cart without `SUMMER10`
- And the response lists `SUMMER10` as not applied with the reason "usage limit reached"

**AC2: Campaign budget used up**
- Given a code `VIP20` whose campaign budget is fully spent
- When a shopper adds `VIP20`
- Then the response lists `VIP20` as not applied with the reason "campaign budget used up"

**AC3: Mixed result**
- Given `SUMMER10` has reached its limit and `WELCOME5` is valid for this cart
- When a shopper adds both codes in one request
- Then `WELCOME5` is applied to the cart
- And only `SUMMER10` is listed as not applied

**AC4: Nothing to report**
- Given `WELCOME5` is valid for this cart
- When a shopper adds `WELCOME5`
- Then the list of codes not applied is empty

**AC5: Old clients keep working**
- Given a client that reads only `cart` from the response
- When it adds any code
- Then it receives the same `cart` as before this change

## Notes for engineering

- The workflow already returns `skipped_promo_codes`; the route ignores it
  `packages/medusa/src/api/store/carts/[id]/promotions/route.ts:14-32`
  `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts:195`
- Add the field as optional on the response type `packages/core/types/src/http/cart/store/responses.ts:5-10`

## Out of scope

- New reasons (STORY-promo-code-feedback-002 and STORY-promo-code-feedback-003).

## Dependencies

- None. This story can ship first.
