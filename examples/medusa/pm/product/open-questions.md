---
id: PROD-open-questions
type: product-page
title: Open questions about Medusa
status: draft
updated: 2026-10-30
---

# Open questions

Things the code could not answer, or behavior that looks surprising. Take these to
engineering or the product owner, then record the answer in the relevant page.

| # | Question | Why it matters | Where we looked | Ask |
|---|----------|----------------|-----------------|-----|
| 1 | The storefront return endpoint needs no login and accepts a shopper-supplied return-shipping price and a "receive now" flag. "Receive now" builds its list from every item on the order, not only the returned ones. Does our deployment restrict these, as Medusa's docs recommend? | Shoppers could set their own return shipping cost or mark items received | `packages/medusa/src/api/store/returns/validators.ts`, `packages/core/core-flows/src/order/workflows/return/create-complete-return.ts:68-72`, `packages/core/core-flows/src/order/workflows/return/create-complete-return.ts:451-465` | Backend lead, security |
| 2 | "Sold out at checkout" returns an HTTP error instead of the friendly cart-plus-error response used for payment failures. Should it be friendly? | Shoppers may see a generic error at the last step | `packages/medusa/src/api/store/carts/[id]/complete/route.ts:40` | Storefront team |
| 3 | Invalid promo codes are skipped without a reason in the Store API response. Does the storefront explain why? | Support tickets about discounts | `packages/core/core-flows/src/cart/workflows/update-cart-promotions.ts` | Storefront team |
| 4 | Who sends order confirmation, password reset and order transfer emails in our setup? Medusa only emits signals. | Missing emails look like bugs to shoppers | `packages/medusa/src/subscribers/configurable-notifications.ts` | Platform team |
| 5 | Can a fulfillment be marked delivered without being shipped? Intended for pickup? | Delivery reporting accuracy | `packages/core/core-flows/src/order/workflows/mark-order-fulfillment-as-delivered.ts` | Backend lead |
| 6 | Do order edits need customer approval before confirmation? | Customer trust, payment changes | `packages/core/core-flows/src/order/workflows/order-edit/request-order-edit.ts` | Product owner |
| 7 | Should registering with an email automatically attach that email's guest orders? Today it needs an order transfer. | Account experience | `packages/core/core-flows/src/order/workflows/transfer/request-order-transfer.ts` | Product owner |
| 8 | Draft Orders and Gift Cards are commented out of the main admin menu ("enable when domain is introduced"); drafts come from a plugin. Is a native version planned? | Roadmap and training | `packages/admin/dashboard/src/components/layout/main-layout/main-layout.tsx` | Product owner |
| 9 | Are role-based permissions or SSO (Enterprise) part of our license? They were excluded from this map. | Admin access stories may depend on them | `ENTERPRISE-LICENSE.md` | Legal, product owner |
