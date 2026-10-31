---
id: TP-promo-code-feedback
type: test-plan
title: Tell shoppers why a promo code did not apply - Test plan
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, TI-promo-code-feedback, EPIC-promo-code-feedback-01, EPIC-promo-code-feedback-02]
capabilities: [CAP-promotions, CAP-cart]
---

# Tell shoppers why a promo code did not apply: test plan

**Scope:** STORY-promo-code-feedback-001 to 005. **Out of scope:** storefront messages
(Next.js starter), "how to qualify" hints, the merchant report (R6).
**Environments and flags:** API tests against a test database. Run the R3 cases with the
dropped-codes flag on and off.

## Test cases

| ID | Covers | Level | Source | Preconditions and data | Steps | Expected |
|----|--------|-------|--------|------------------------|-------|----------|
| TC-01 | STORY-promo-code-feedback-001/AC1 | API | story | `SUMMER10`, limit 100, used 100 | Add `SUMMER10` | Cart without it; listed with "usage limit reached" |
| TC-02 | STORY-promo-code-feedback-001/AC2 | API | story | `VIP20` in a campaign whose spend budget is used up | Add `VIP20` | Listed with "campaign budget used up" |
| TC-03 | STORY-promo-code-feedback-001/AC3 | API | story | `SUMMER10` at limit, `WELCOME5` valid | Add both in one request | `WELCOME5` applied; only `SUMMER10` listed |
| TC-04 | STORY-promo-code-feedback-001/AC4 | API | story | `WELCOME5` valid | Add `WELCOME5` | List of codes not applied is empty |
| TC-05 | STORY-promo-code-feedback-001/AC5, STORY-promo-code-feedback-005/AC4 | API | story | Client using the current JS SDK | Add a failing code; remove an item that drops a code | `cart` identical to today's response |
| TC-06 | STORY-promo-code-feedback-002/AC1 | API | story | No promotion `NOPE123` | Add `NOPE123` | Listed with "not valid" |
| TC-07 | STORY-promo-code-feedback-002/AC2 | API | story | `DRAFT15` with status draft; `OLD15` with status inactive | Add each | Both "not valid", same as TC-06 |
| TC-08 | STORY-promo-code-feedback-002/AC3 | API | story | Campaign of `BLACKFRIDAY` ended yesterday | Add `BLACKFRIDAY` | "expired" (or "not valid" per PRD Q5) |
| TC-09 | STORY-promo-code-feedback-002/AC4 | API | story | Campaign of `XMAS` starts next week | Add `XMAS` | "not started" (or "not valid" per PRD Q5) |
| TC-10 | STORY-promo-code-feedback-002/AC5 | API | story | Codes from TC-06 to TC-09 | Inspect each entry | Only code and reason; no IDs, names, or dates |
| TC-11 | STORY-promo-code-feedback-003/AC1 | API | story | `BULK10` for group "Wholesale"; shopper not in it | Add `BULK10` | "conditions not met"; no group name in the response |
| TC-12 | STORY-promo-code-feedback-003/AC2 | API | story | `EUR5OFF` in EUR; cart in USD | Add `EUR5OFF` | "currency not supported" |
| TC-13 | STORY-promo-code-feedback-003/AC3 | API | story | Buy-get `SOCKS3`; no socks in cart | Add `SOCKS3` | "conditions not met" |
| TC-14 | STORY-promo-code-feedback-004/AC1, STORY-promo-code-feedback-004/AC2 | Manual | story | Spike finished | Review the route list and the decision record | Every route that refreshes the cart is listed; decision linked |
| TC-15 | STORY-promo-code-feedback-005/AC1 | API | story | `SPEND50` (min subtotal 50) applied; subtotal 60 | Remove a 20 item | Response reports `SPEND50` removed, "conditions not met" |
| TC-16 | STORY-promo-code-feedback-005/AC2 | API | story | `WELCOME5` applied | Change a quantity | No removed codes reported |
| TC-17 | STORY-promo-code-feedback-005/AC3 | API | story | Flag off; `SPEND50` applied | Remove the item | Response identical to today |
| TC-18 | - | API | derived: `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts:123-129` | `WELCOME5` already applied | Add `WELCOME5` again | Not reported as failed; still applied once |
| TC-19 | - | API | derived: `packages/modules/promotion/src/services/promotion-module.ts:990-999` | Promotion with a per-customer budget; cart without that attribute | Add the code | Same error as today (out of scope) |
| TC-20 | - | API | derived: PRD edge cases | Automatic promotion whose rules do not match | Add any valid code | Automatic promotion not listed as failed |
| TC-21 | - | API | derived: `packages/medusa/src/api/store/carts/middlewares.ts:104-113` | No customer login (route needs only the cart ID and the publishable key) | Add 50 different made-up codes quickly | Each returns "not valid"; note whether any rate limit applies (input for PRD Q5) |
| TC-22 | - | API | derived: `packages/modules/promotion/src/services/promotion-module.ts:851-853` | Codes `summer10` vs `SUMMER10` | Add the lowercase version | Record the behavior (answers PRD Q4) |
| TC-23 | - | Integration | derived: TI Question 2 | Draft order with a code that is not valid | Refresh draft order adjustments | Draft order flow unaffected by the new outcomes |

## Regression

| Area | Why | How |
|------|-----|-----|
| [Promotions at checkout](../../product/journeys/promotions-at-checkout.md) | Same engine and workflow | `packages/modules/promotion/integration-tests/__tests__/services/promotion-module/compute-actions.spec.ts` |
| [Checkout](../../product/journeys/checkout.md) | Promotions re-checked on every cart change | `integration-tests/http/__tests__/cart/store/cart.spec.ts` |
| Concurrent promotion updates | The workflow holds a cart lock | `integration-tests/http/__tests__/cart/store/concurrent-promotions.spec.ts` |
| Draft orders and order edits | Consume the same engine outcomes | `packages/core/core-flows/src/draft-order/workflows/compute-draft-order-adjustments.ts` (no dedicated test found; manual) |

## Non-functional checks

- p95 latency of adding a code and of changing cart items: no more than 10% worse than
  the baseline (PRD guardrail; baseline is PRD Q3).

## Exploratory charters

1. Explore adding, removing, and re-adding codes while editing the cart, looking for
   totals that do not match the applied codes (30 minutes).
2. Explore codes at their exact limits (last use, last unit of budget, campaign ending
   this minute), looking for wrong reasons (30 minutes).

## Test data

- Promotions: `SUMMER10`, `VIP20`, `WELCOME5`, `NOPE123` (absent), `DRAFT15`, `OLD15`,
  `BLACKFRIDAY`, `XMAS`, `BULK10`, `EUR5OFF`, `SOCKS3`, `SPEND50`, with the settings above.
- Customer group "Wholesale" with one customer; one customer outside it.
- Regions in USD and EUR.

## Exit criteria

- TC-01 to TC-20 and TC-23 pass. TC-21 and TC-22 are recorded, and PRD Q4 and Q5 are answered.
- Latency guardrail met.
