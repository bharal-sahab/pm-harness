---
id: TI-promo-code-feedback
type: tech-impact
title: Tell shoppers why a promo code did not apply - Technical impact
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback]
capabilities: [CAP-promotions, CAP-cart]
code_refs:
  - packages/medusa/src/api/store/carts/[id]/promotions/route.ts
  - packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts
  - packages/modules/promotion/src/services/promotion-module.ts
  - packages/core/utils/src/promotion/index.ts
  - packages/core/types/src/http/cart/store/responses.ts
  - packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts
source_commit: 2cfefbd370fd133e629b8d545a28460af5ffd01b
---

# Tell shoppers why a promo code did not apply: technical impact

> Prepared from the code by the PM harness to support a conversation with engineering.
> Sizes are relative (S, M, L), not estimates. Engineering owns the estimate.

**Overall size:** L. R1 is small because the data already exists. R2 needs new outcomes from
the promotion engine. R3 touches every route that changes a cart.
**Biggest risk:** R3 changes the responses of many cart routes. Stories should ship R1 and R2
first, and put R3 behind a flag.
**Key finding:** Half of R1 is already built. The workflow computes skipped codes with a
reason, and the Store API route throws that away.

## Where each requirement lands

| Req | Where today's behavior is decided | What already exists |
|-----|-----------------------------------|---------------------|
| R1 | The store route runs the workflow, then returns only a re-fetched cart `packages/medusa/src/api/store/carts/[id]/promotions/route.ts:14-32` | Workflow output `skipped_promo_codes` `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts:195` |
| R2 | Not-found, inactive and out-of-date codes are filtered out in the query `packages/modules/promotion/src/services/promotion-module.ts:166-200`. Unmet conditions and currency mismatch are skipped with `continue` `packages/modules/promotion/src/services/promotion-module.ts:1040-1052` | Two reasons exist: `promotionLimitExceeded` and `campaignBudgetExceeded` `packages/core/utils/src/promotion/index.ts:46-53` |
| R3 | Changing items re-runs promotions with "replace" and no result is kept `packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts:242-249` | Nothing |
| R4 | The engine knows which rule failed only inside `areRulesValidForContext` `packages/modules/promotion/src/services/promotion-module.ts:1044-1048` | Nothing. The reason must stay generic ("conditions not met") |
| R5 | The response type has only `cart` `packages/core/types/src/http/cart/store/responses.ts:5-10` | Additive fields are safe for typed clients |
| R6 | No reporting of failed entries | Nothing (deferred: could-have) |

## Impact by surface

| Surface | What changes | Files | Type | Size |
|---------|--------------|-------|------|------|
| API | Add-promotions response includes a list of codes not applied, with reasons | `packages/medusa/src/api/store/carts/[id]/promotions/route.ts` | modify | S: the data exists |
| API types and SDK | Optional field on the cart response; the SDK's `addPromotions` gets the type for free | `packages/core/types/src/http/cart/store/responses.ts`, `packages/core/js-sdk/src/store/index.ts:886` | modify | S |
| Business logic | The promotion engine reports new outcomes: not valid, expired or not started, conditions not met, currency not supported | `packages/modules/promotion/src/services/promotion-module.ts`, `packages/core/utils/src/promotion/index.ts`, `packages/core/types/src/promotion/common/compute-actions.ts` | modify | M: the engine needs an extra lookup to tell "expired" from "does not exist" |
| Business logic | The step that turns engine output into adjustments maps the new outcomes to reasons | `packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts:161-204` | modify | S |
| Business logic | Cart-changing workflows compare codes before and after the refresh and report dropped codes | `packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts` | modify | M |
| API | Every route that changes a cart can include dropped codes | Store cart routes under `packages/medusa/src/api/store/carts` | modify | L: many routes, one pattern |
| Configuration | Feature flag for R3 | `packages/medusa/src/feature-flags` | new | S |
| Data | None: reasons are returned, not stored | none | none | none |

## Who else depends on this

| Changed thing | Consumers | Breaking? |
|---------------|-----------|-----------|
| Add-promotions response | Storefronts, the JS SDK, mobile apps | No: additive |
| Engine outcomes (`ComputedActions`) | Cart promotions, draft-order adjustments, order-edit previews `packages/core/core-flows/src/draft-order/workflows/compute-draft-order-adjustments.ts` `packages/core/core-flows/src/order/workflows/compute-adjustments-for-preview.ts` | Possibly: these must ignore the new outcomes (Question 2) |
| `updateCartPromotionsWorkflow` output | Plugins and custom workflows that run it | No: additive |
| Cart responses from item routes (R3) | All storefronts | No if additive, but behind a flag to be safe |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Saying "expired" vs "not valid" lets people probe for old codes | medium | low | Product decision (PRD Q5); the reason could be merged into "not valid" |
| A reason leaks private conditions (customer group) | low | medium | Generic "conditions not met" reason only (R4) |
| Extra lookup slows the cart, which runs promotions on every item change | medium | medium | Only look up codes that were not found; measure p95 (PRD Q3) |
| Draft orders or order edits mis-handle new outcomes | medium | medium | Engine change plus tests in both flows (Question 2) |
| Many cart routes changed for R3 | high | medium | One helper, feature flag, ship after R1 and R2 |

## Suggested sequence

1. Return the existing two reasons from the add-promotions route (R1, R5). Ships alone and
   gives storefronts something to use right away.
2. New outcomes in the promotion engine, mapped to reasons (R2, R4).
3. Report codes dropped by cart changes, behind a flag (R3).

Steps 1 and 2 can ship in the same minor release. Step 3 can follow.

## Rollout switches

Medusa has a feature-flag system with one file per flag `packages/medusa/src/feature-flags/translation.ts`.

## Existing tests near the change

- `packages/modules/promotion/integration-tests/__tests__/services/promotion-module/compute-actions.spec.ts`: engine outcomes
- `integration-tests/http/__tests__/cart/store/cart.spec.ts`: store cart routes, including promotions
- `integration-tests/http/__tests__/cart/store/concurrent-promotions.spec.ts`: promotions under concurrent requests

## Questions for engineering

1. The workflow already returns `skipped_promo_codes`, but the route discards it
   (`packages/medusa/src/api/store/carts/[id]/promotions/route.ts:14-32`). Can we return it
   next to `cart` in the same release, and does anything rely on the response having only `cart`?
2. Draft-order and order-edit flows also consume engine outcomes. Do their handlers
   ignore unknown actions, like the cart step's `switch` does
   (`packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts:161-204`)?
3. To tell "expired" from "does not exist", should the engine run a second query without
   the active filter (`packages/modules/promotion/src/services/promotion-module.ts:166-200`),
   or should the workflow do it?
4. For R3, do we compare codes before and after `refresh-cart-items`
   (`packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts:242-249`), or have
   the promotion workflow return removed codes directly?
5. How many store routes run `refresh-cart-items`? Is there one place to attach dropped codes
   to all of their responses?
6. Are codes matched case-insensitively today (PRD Q4)?

## Terms used

- **Workflow**: a series of steps Medusa runs in order, which can undo themselves if a step fails.
- **Route**: the code behind one API address, such as `POST /store/carts/{id}/promotions`.
- **Promotion engine (`computeActions`)**: the part of the promotion module that decides
  which discounts apply to a cart.
- **Additive change**: adding new information without changing or removing what exists, so old clients keep working.
- **Feature flag**: a switch that turns a behavior on or off without a new release.
- **SDK**: a code library storefront developers use to call the API.
