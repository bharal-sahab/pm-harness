---
id: PROD-faq
type: product-page
title: Medusa - Questions and answers
status: approved
updated: 2026-10-30
---

# Questions and answers

Questions PMs asked about the product, answered from the code. Newest first. Each answer
was true at the commit shown; `product-map-refresh` flags answers whose cited files changed.

## Can a shopper use more than one promo code on the same cart?

**Short answer:** Yes. Codes stack: each new code is added to the codes already on the
cart, and automatic promotions apply alongside them. There is no setting to make a
promotion "exclusive" or "not combinable" with others.

- Adding a code keeps the codes already applied; the default action is "add", not "replace" `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts:123-129`
- The promotion engine evaluates the new codes, the codes already on the cart, and every automatic promotion together `packages/modules/promotion/src/services/promotion-module.ts:851-891`
- Order of application: buy X get Y promotions first, then higher-value promotions before lower ones `packages/modules/promotion/src/utils/compute-actions/buy-get.ts:663-677`
- Searched the promotion module for `exclusive`, `stackable`, and `combin` and found no such setting `packages/modules/promotion/src/models/promotion.ts`
- Codes that do not qualify are skipped without an error to the shopper (already noted in [open questions](open-questions.md)) `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts:195`

**Confidence:** High for stacking; Medium that no exclusivity setting exists (absence found by search, not by reading every file).
**Capabilities:** CAP-promotions, CAP-cart (see [capabilities](capabilities.md))
**Asked:** 2026-10-30 at commit `2cfefbd`

## Does an abandoned cart hold stock?

**Short answer:** No. Adding to the cart only *checks* that enough stock is available.
Stock is *reserved* only when the order is placed, so abandoned carts never block other
shoppers. The flip side: two shoppers can have the last unit in their carts, and the
second to pay gets an "out of stock" error at checkout.

- Add to cart runs an availability check that throws if stock is short; it creates no reservation `packages/core/core-flows/src/cart/workflows/add-to-cart.ts:319` `packages/core/core-flows/src/cart/steps/confirm-inventory.ts:45-49`
- Reservations are created in the same step that places the order `packages/core/core-flows/src/cart/workflows/complete-cart.ts:648-653`
- What the second shopper sees at checkout is described in the [checkout journey](journeys/checkout.md)

**Confidence:** High - read both paths.
**Capabilities:** CAP-cart, CAP-inventory, CAP-checkout (see [capabilities](capabilities.md))
**Asked:** 2026-10-30 at commit `2cfefbd`
