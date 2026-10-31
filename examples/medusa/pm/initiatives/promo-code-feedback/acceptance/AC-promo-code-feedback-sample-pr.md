---
id: AC-promo-code-feedback-sample-pr
type: acceptance-report
title: Tell shoppers why a promo code did not apply - Acceptance check for the sample PR
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [STORY-promo-code-feedback-001, TP-promo-code-feedback]
code_refs:
  - packages/medusa/src/api/store/carts/[id]/promotions/route.ts
  - packages/core/types/src/http/cart/store/responses.ts
  - packages/core/js-sdk/src/store/index.ts
---

# Acceptance check: sample PR "Return skipped promo codes from the Store API"

> Example run of `acceptance-check` against a sample diff written for this demo:
> [the sample diff](../../../../sample-pr/promo-reasons.diff).
> Line numbers refer to the files after the change.

**Recommendation:** Not ready. The behavior for STORY-promo-code-feedback-001 looks
complete, but the new tests import a helper that does not exist, so they cannot run and
nothing proves the behavior yet.
**Diff:** 4 files, +75/-4 lines.
**Stories checked:** STORY-promo-code-feedback-001 (the PR claims only this story).

## Acceptance criteria

| Criterion | Verdict | Evidence | Note |
|-----------|---------|----------|------|
| STORY-promo-code-feedback-001/AC1 | Done, not tested | Route keeps the workflow result and returns `skipped_promo_codes` `packages/medusa/src/api/store/carts/[id]/promotions/route.ts:14` `packages/medusa/src/api/store/carts/[id]/promotions/route.ts:32-35` | Test in `promotion-feedback.spec.ts` lines 17-33 would cover it, but cannot run (see Follow-ups) |
| STORY-promo-code-feedback-001/AC2 | Done, not tested | Same route; the type allows `campaign_budget_exceeded` (`responses.ts` line 18 after the change) | No test for the budget case (TC-02) |
| STORY-promo-code-feedback-001/AC3 | Done, not tested | The workflow already keeps valid codes and lists only skipped ones `packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts:192-210` | Test in `promotion-feedback.spec.ts` lines 35-56 cannot run |
| STORY-promo-code-feedback-001/AC4 | Done, not tested | Returns an empty list when nothing is skipped (`?? []`) `packages/medusa/src/api/store/carts/[id]/promotions/route.ts:34` | Add an assertion for the empty list (TC-04) |
| STORY-promo-code-feedback-001/AC5 | Done, not tested | `cart` is unchanged and the new type extends the old one (`responses.ts` line 12); the field is additive | Run the existing cart tests to confirm (TC-05) |

## Unplanned changes

- `packages/core/js-sdk/src/store/index.ts:892`: the SDK's `addPromotions` now returns the
  new response type. Fine and expected from the tech impact; add this file to the story's
  `code_refs`.

## Risks

- The route now relies on the workflow returning its result directly. If the workflow
  engine ever runs this workflow in the background, `result` would be empty, and `?? []`
  would hide it (the response would say nothing was skipped). Can't tell from the diff; ask
  engineering.
- Reasons are the internal names (`promotion_limit_exceeded`). Confirm with the storefront
  team that these are the names they should depend on (PRD R1 asks for machine-readable reasons).

## Check by hand

1. Create `SUMMER10` with a usage limit of 1, use it once, then add it to a new cart. Expect
   `skipped_promo_codes: [{ code: "SUMMER10", reason: "promotion_limit_exceeded" }]`.
2. Add a valid code. Expect `skipped_promo_codes: []` and the code on the cart.

## Follow-ups

- **Blocking:** `promotion-feedback.spec.ts` imports `setupCartWithPromotions` from
  `helpers/promotions`, which is not in the repository or the diff. Add the helper or use
  existing fixtures.
- Add tests for the budget case (AC2) and the empty list (AC4).
