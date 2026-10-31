---
id: PRD-promo-code-feedback
type: prd
title: Tell shoppers why a promo code did not apply
status: in-review
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PROD-open-questions, JRN-promotions-at-checkout, PROD-faq]
capabilities: [CAP-promotions, CAP-cart]
code_refs:
  - packages/medusa/src/api/store/carts/[id]/promotions/route.ts
  - packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts
  - packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts
  - packages/modules/promotion/src/services/promotion-module.ts
  - packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts
owner: Example PM
---

# Tell shoppers why a promo code did not apply

**Summary:** When a shopper enters a promo code that does not apply, Medusa's Store API
returns the cart without the code and without a reason, so no storefront can tell the
shopper what went wrong. This change makes the Store API say which code failed and why,
including when a code stops applying because the cart changed, so storefronts can show a
helpful message.

## Problem

Shoppers who enter a code and see no discount do not know whether they mistyped it, it
expired, or their cart does not qualify. They retry, abandon, or contact support.
Storefront developers cannot fix this today, because the API does not give them the
reason.

**Evidence:** Hypothesis, not yet validated. It comes from open question 3 in the
[product map](../../product/open-questions.md). Q1 below asks for support-ticket data to
size it.

## Current behavior

- Codes stack, and every code is re-checked together with automatic promotions (see
  [FAQ](../../product/faq.md)) `packages/modules/promotion/src/services/promotion-module.ts:851-891`
- The Store API route that adds codes runs the promotion workflow and then returns only
  the cart. It ignores the workflow's result `packages/medusa/src/api/store/carts/[id]/promotions/route.ts:14-32`
- The workflow already returns `skipped_promo_codes` with a reason, but only for two cases:
  the code's usage limit is reached, or its campaign budget is used up
  `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts:195`
  `packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts:88-99`
- Codes that do not exist, are draft or inactive, or whose campaign has not started or has
  ended are filtered out before evaluation. Nothing records why
  `packages/modules/promotion/src/services/promotion-module.ts:166-200`
- Codes whose conditions the cart does not meet (for example, customer group or items),
  or whose currency differs from the cart's, are skipped silently
  `packages/modules/promotion/src/services/promotion-module.ts:1040-1052`
- Every change to cart items re-checks the codes and can drop one silently, for example
  when removing an item takes the cart below a condition
  `packages/core/core-flows/src/cart/workflows/refresh-cart-items.ts:242-249`

## Goals and metrics

| Metric | Type | Baseline | Target | Measured in |
|--------|------|----------|--------|-------------|
| Code entries that end with the code applied or a reason shown | Primary | Unknown: reasons are not returned today (Q2) | 100% of failed entries return a reason | Store API logs or storefront analytics |
| Support contacts about discount codes | Secondary | Unknown (Q1) | -30% within one quarter of storefront adoption | Support tool tags |
| p95 latency of adding a code | Guardrail | Unknown (Q3) | No more than +10% | APM |

## Users and scenarios

- **Storefront developer** wants to know why a code failed, so that they can show the
  shopper a specific message.
- **Shopper** wants to know why their code did not work, so that they can fix it (retype,
  add items) or stop trying.
- **Merchant** wants fewer support contacts and abandoned carts caused by confusing codes.

## Requirements

| ID | Requirement | Priority | Capability |
|----|-------------|----------|------------|
| R1 | When a shopper adds one or more codes and some cannot be applied, the Store API response lists each code that was not applied, with a machine-readable reason. | must | CAP-promotions |
| R2 | Reasons distinguish at least: not valid (does not exist or not active), expired or not started, usage limit reached, campaign budget used up, cart does not meet the conditions, and currency not supported. | must | CAP-promotions |
| R3 | When a code that was applied stops applying because the cart changed, the next cart response from that change says which code was removed and why. | must | CAP-cart |
| R4 | A reason never reveals private or internal details, such as customer group names, rule values, or budget amounts. | must | CAP-promotions |
| R5 | Clients that ignore the new information keep working unchanged. | must | CAP-cart |
| R6 | Merchants can see how often each code fails and why. | could | CAP-promotions |

## Edge cases and errors

| Case | Today | Required behavior |
|------|-------|-------------------|
| Several codes added at once, some fail | Applied codes kept, failed ones dropped silently `packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts:192-203` | Applied codes kept; each failed code listed with its reason (R1) |
| Code already on the cart is added again | Treated as one code `packages/modules/promotion/src/services/promotion-module.ts:851-853` | No failure reported |
| Automatic promotion does not apply | Silently not applied | Not reported: the shopper did not enter it |
| Shopper removes a code | Code removed | Not a failure; nothing reported |
| Campaign budget per customer needs an attribute the cart lacks | Request fails with an error `packages/modules/promotion/src/services/promotion-module.ts:990-999` | Unchanged (out of scope) |
| Same code entered by mistake with different capitalization | Unknown (Q4) | Decide in Q4 |

## User experience

The Store API change is the product here; storefront copy is up to each storefront. A
suggested message per reason will be included in the API docs for the Next.js starter
team (see Non-goals). The flow is the
[promotions journey](../../product/journeys/promotions-at-checkout.md), with a reason
returned at the "skip" step.

## Rollout

The new information is additive, so R1 and R2 can ship without a flag. R3 changes the
responses of every cart-changing route, so ship it behind a feature flag using Medusa's
feature-flag system `packages/medusa/src/feature-flags/translation.ts`, on by default in
the next minor version.

## Non-goals

- Updating the Next.js starter storefront (separate repository). Follow-up initiative.
- Suggesting alternative codes or showing "add 10 more to qualify". Valuable, but needs
  rule-specific messages; revisit after R1-R3.
- Changing how promotions are evaluated or stacked.

## Assumptions

- Storefront developers will adopt the new field within a release or two.
- Saying "expired" separately from "not valid" is acceptable to merchants (Q5).

## Open questions

| # | Question | Owner | Needed by |
|---|----------|-------|-----------|
| Q1 | How many support contacts per month mention discount codes? | Support lead | Before approval |
| Q2 | Can we log failed code entries today to get a baseline? | Engineering | Before build |
| Q3 | What is the current p95 latency of adding a code? | Engineering | Before build |
| Q4 | Are codes matched case-insensitively? | Engineering | Before stories are final |
| Q5 | Does separating "expired" from "not valid" let people discover old codes? Is that a problem for merchants? | Product owner, security | Before build |
