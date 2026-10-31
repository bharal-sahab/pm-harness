---
id: PROD-capabilities
type: product-page
title: Medusa capabilities
status: draft
updated: 2026-10-30
source_commit: 2cfefbd370fd133e629b8d545a28460af5ffd01b
---

# Capabilities

Each capability is something a user can accomplish. IDs are stable: PRDs, stories and test
plans reference them. Medusa has three audiences: **shoppers** (through a storefront that
calls the Store API), **merchants** (through the Admin dashboard and Admin API), and
**developers** (who extend and host Medusa).

## Summary

| ID | Capability | Audience | Surface | Confidence |
|----|------------|----------|---------|------------|
| CAP-catalog-browsing | Browse and search products | Shopper | Store API | High |
| CAP-cart | Build a cart | Shopper | Store API | High |
| CAP-checkout | Check out and place an order | Shopper | Store API | High |
| CAP-customer-accounts | Accounts, login, order history | Shopper | Store API, Auth API | High |
| CAP-self-service-returns | Request a return without staff | Shopper | Store API | High |
| CAP-product-management | Manage the catalog | Merchant | Admin | High |
| CAP-pricing | Prices, price lists, tiered prices | Merchant | Admin | High |
| CAP-promotions | Discounts, campaigns, budgets | Merchant | Admin | High |
| CAP-inventory | Stock per location, reservations | Merchant | Admin | High |
| CAP-order-management | Fulfill, ship, deliver, cancel | Merchant | Admin | High |
| CAP-post-purchase-changes | Returns, claims, exchanges, edits | Merchant | Admin | High |
| CAP-refunds | Refunds and store credit | Merchant | Admin | High |
| CAP-draft-orders | Create orders for customers | Merchant | Admin (plugin) | High |
| CAP-customer-management | Customers and customer groups | Merchant | Admin | High |
| CAP-shipping-setup | Locations, zones, shipping options | Merchant | Admin | Medium |
| CAP-markets-and-taxes | Regions, currencies, tax rates | Merchant | Admin | Medium |
| CAP-sales-channels | Sales channels and storefront keys | Merchant | Admin | High |
| CAP-team-and-access | Staff users, invites, secret keys | Merchant | Admin | High |
| CAP-translations | Multi-language content (off by default) | Merchant, Shopper | Admin, Store API | Medium |
| CAP-extensibility | Customize and extend the platform | Developer | Code, Admin SDK | High |

## Shopper capabilities

### CAP-catalog-browsing: Browse and search products

**What it does:** Shoppers list products, variants, categories, collections, tags and types,
see prices for their region and currency, and search. Only products linked to the
storefront's sales channel are visible.

**Who uses it:** Shoppers, through any storefront calling the Store API.

**Rules and limits:**
- Every Store API call must send a publishable API key; the key's sales channels decide which products are visible `packages/core/framework/src/http/middlewares/ensure-publishable-api-key.ts:19-27`, `packages/medusa/src/api/utils/middlewares/common/maybe-attach-pub-key-scopes.ts`
- Only `published` products can be added to a cart `packages/core/core-flows/src/cart/workflows/get-variants-and-items-with-prices.ts:163-176`
- Search only covers indexes the developer has opted in `packages/medusa/src/api/store/search/route.ts`

**Switches:** `index_engine` flag changes how product lists are filtered `packages/medusa/src/feature-flags/index-engine.ts`; `translation` flag enables localized content `packages/medusa/src/feature-flags/translation.ts`.

**Where in the code:** `packages/medusa/src/api/store/products/route.ts`, `packages/medusa/src/api/store/product-categories/route.ts`, `packages/modules/product/src/models/product.ts`

**Errors users can hit:** Missing or revoked storefront key: "Publishable API key required in the request header: x-publishable-api-key" `packages/core/framework/src/http/middlewares/ensure-publishable-api-key.ts:19-27`.

**Confidence:** High for visibility rules; Medium for search behavior.

### CAP-cart: Build a cart

**What it does:** A shopper creates a cart for a region, adds and changes items, and sets
email and addresses. Prices, taxes, discounts and shipping are recalculated after each change.

**Rules and limits:**
- The cart's currency must match its region's currency `packages/core/core-flows/src/cart/workflows/create-carts.ts:92-106`
- Shoppers cannot set prices; only variant, quantity and metadata `packages/medusa/src/api/store/carts/validators.ts:74-78`
- Adding the same variant again re-prices the combined quantity, so quantity tiers apply `packages/core/core-flows/src/cart/workflows/add-to-cart.ts:176-194`
- Stock is checked at add-to-cart unless the variant allows backorders or does not track inventory `packages/core/core-flows/src/cart/steps/confirm-inventory.ts:76-97`
- Changing the shipping country to one outside the region is rejected; changing region clears addresses and custom-priced items `packages/core/core-flows/src/cart/workflows/update-cart.ts:72-100`
- Setting quantity to 0 removes the item `packages/core/core-flows/src/cart/workflows/update-line-item-in-cart.ts`

**Errors users can hit:**

| When | Message or outcome | Code |
|------|--------------------|------|
| Adding a variant that has no price for the cart's currency, region or customer | Rejected: "Variants with IDs ... do not have a price" | `packages/core/core-flows/src/cart/workflows/get-variants-and-items-with-prices.ts:170-175` |
| Adding a variant whose product is not published (or does not exist) | Rejected: "... do not exist or belong to a product that is not published" | `packages/core/core-flows/src/cart/workflows/get-variants-and-items-with-prices.ts:163-169` |
| Not enough stock (tracked inventory, no backorders) | Rejected: "Some variant does not have the required inventory" | `packages/core/core-flows/src/cart/steps/confirm-inventory.ts:80-97` |
| Variant not stocked at any location serving this sales channel | Rejected | `packages/core/core-flows/src/cart/utils/prepare-confirm-inventory-input.ts:209-222` |
| Changing a cart that is already completed | Rejected: "Cart ... is already completed." | `packages/core/core-flows/src/cart/steps/validate-cart.ts:38-43` |
| Currency different from the region's | Rejected at cart creation | `packages/core/core-flows/src/cart/workflows/create-carts.ts:92-106` |
| Shipping country outside the region | Rejected: "Country with code ... is not within region ..." | `packages/core/core-flows/src/cart/workflows/update-cart.ts:72-88` |

**Related:** [Checkout journey](journeys/checkout.md), Cart in [data-model.md](data-model.md)

**Where in the code:** `packages/medusa/src/api/store/carts/route.ts`, `packages/core/core-flows/src/cart/workflows/`

**Confidence:** High

### CAP-checkout: Check out and place an order

**What it does:** The shopper picks a shipping method, applies promo codes, starts a payment
with a provider, and completes the cart. Completion turns the cart into an order, reserves
stock, records promotion usage and authorizes payment, or undoes all of it if anything fails.

**Rules and limits:**
- Guest checkout is the default; no account is needed `packages/core/core-flows/src/cart/steps/find-or-create-customer.ts`
- Only one payment session per cart; starting a new one deletes the others (no split payments) `packages/core/core-flows/src/payment-collection/workflows/create-payment-session.ts:218-224`
- If the cart total changes after payment starts, all payment sessions are deleted and the shopper must start payment again `packages/core/core-flows/src/cart/workflows/refresh-payment-collection.ts:124-172`
- A shipping method is required when any item needs shipping, and each product's shipping profile must be covered `packages/core/core-flows/src/cart/steps/validate-shipping.ts`
- Payment is authorized last, after the order is created, to minimize rollbacks `packages/core/core-flows/src/cart/workflows/complete-cart.ts:684-691`
- Completing the same cart twice returns the same order, never a duplicate `packages/core/core-flows/src/cart/workflows/complete-cart.ts:388-411`
- The amount charged is the payment session's amount; completion does not re-compare it to the cart total `packages/core/core-flows/src/cart/workflows/complete-cart.ts:82-96`

**Errors users can hit:**

| When | Message or outcome | Code |
|------|--------------------|------|
| Placing an order with an empty cart | "Cannot complete a cart with no items" | `packages/core/core-flows/src/cart/steps/validate-cart-items.ts:40-45` |
| No payment started | "Payment collection has not been initiated for cart" / "Payment sessions are required to complete cart" | `packages/core/core-flows/src/cart/steps/validate-cart-payments.ts:60-86` |
| Shippable items but no shipping method | "No shipping method selected but the cart contains items that require shipping." | `packages/core/core-flows/src/cart/steps/validate-shipping.ts:86-111` |
| Card declined, or 3-D Secure needed | Friendly response: cart plus error (see [checkout](journeys/checkout.md)) | `packages/core/core-flows/src/payment/steps/authorize-payment-session.ts:85-99` |
| Item sold out at the last moment | HTTP error; no payment attempted | `packages/modules/inventory/src/services/inventory-module.ts` |

**Switches:** Region setting `automatic_taxes` decides whether taxes are calculated automatically `packages/modules/region/src/models/region.ts`.

**Related:** [Checkout journey](journeys/checkout.md), [Promotions journey](journeys/promotions-at-checkout.md)

**Where in the code:** `packages/medusa/src/api/store/carts/[id]/complete/route.ts`, `packages/core/core-flows/src/cart/workflows/complete-cart.ts`

**Confidence:** High (read end to end).

### CAP-customer-accounts: Accounts, login, order history

**What it does:** Shoppers register, log in (email and password by default; Google and
GitHub available), reset passwords, manage profile and addresses, see past orders, and claim
guest orders into their account through an order transfer.

**Rules and limits:**
- Registration is two calls: create login credentials, then create the customer profile `packages/medusa/src/api/auth/[actor_type]/[auth_provider]/register/route.ts`, `packages/medusa/src/api/store/customers/route.ts`
- One registered account per email; a guest record with the same email does not block registration `packages/core/core-flows/src/customer/steps/validate-customer-account-creation.ts`, `packages/modules/customer/src/models/customer.ts:30-34`
- Password reset always answers "success" so it does not reveal which emails have accounts; sending the email is left to a subscriber `packages/core/core-flows/src/auth/workflows/generate-reset-password-token.ts`
- Order history requires login, but a single order can be read by anyone who has its ID `packages/medusa/src/api/store/orders/middlewares.ts`, `packages/medusa/src/api/store/orders/[id]/route.ts`
- Orders can only be transferred to a registered account that does not already own them `packages/core/core-flows/src/order/workflows/transfer/request-order-transfer.ts:68-83`

**Related:** [Customer accounts journey](journeys/customer-accounts.md)

**Where in the code:** `packages/medusa/src/api/auth/`, `packages/medusa/src/api/store/customers/`, `packages/modules/providers/auth-emailpass/src/services/emailpass.ts`

**Errors users can hit:** "Customer with this email already has an account" on duplicate registration `packages/core/core-flows/src/customer/steps/validate-customer-account-creation.ts`; account, address and order-history pages reject anonymous requests `packages/medusa/src/api/store/customers/middlewares.ts`.

**Confidence:** High

### CAP-self-service-returns: Request a return without staff

**What it does:** A shopper who knows an order ID can request a return of items from that
order; Medusa creates the return and its return shipment.

**Rules and limits:**
- No login required; the order ID acts as the secret `packages/medusa/src/api/store/returns/route.ts`
- Order must not be canceled; items must belong to the order; return reasons must be valid `packages/core/core-flows/src/order/workflows/return/create-complete-return.ts`
- The request may include a return-shipping price and a "receive now" flag (see [open questions](open-questions.md)) `packages/medusa/src/api/store/returns/validators.ts`

**Related:** [Returns, claims and exchanges journey](journeys/returns-claims-exchanges.md)

**Errors users can hit:** Returning items from a canceled order, items not on the order, or with an invalid return reason is rejected `packages/core/core-flows/src/order/workflows/return/create-complete-return.ts`.

**Confidence:** High for the flow; Medium for intended restrictions.

## Merchant capabilities

### CAP-product-management: Manage the catalog

**What it does:** Merchants create and edit products, variants, options, categories (a
tree), collections, tags and types; manage media; import and export CSV.

**Rules and limits:**
- Product states: `draft`, `proposed`, `published`, `rejected` (default `draft`) `packages/core/utils/src/product/enums.ts`
- Each variant can track inventory (`manage_inventory`, default on) and allow backorders (default off) `packages/modules/product/src/models/product-variant.ts`
- A product belongs to at most one collection and one shipping profile `packages/modules/product/src/models/product.ts`, `packages/modules/link-modules/src/definitions/product-shipping-profile.ts`
- Options can be shared across products `packages/modules/product/src/models/product-product-option.ts`

**Where in the code:** `packages/admin/dashboard/src/routes/products/`, `packages/medusa/src/api/admin/products/route.ts`

**Errors users can hit:** Not inventoried at standard depth; duplicate handles and SKUs are rejected by unique constraints `packages/modules/product/src/models/product-variant.ts`.

**Confidence:** High

### CAP-pricing: Prices, price lists, tiered prices

**What it does:** Each variant has prices per currency, optionally per region and quantity
range. Price lists add sales or overrides, optionally for customer groups and date ranges.

**Rules and limits:**
- Price list types: `sale` (applies only if lower than the original price) and `override` (always wins) `packages/modules/pricing/src/services/pricing-module.ts:429-456`
- Price lists start as `draft` and can be scheduled with start and end dates `packages/modules/pricing/src/models/price-list.ts`
- Customer-group targeting uses a `customer.groups.id` rule `packages/admin/dashboard/src/routes/price-lists/price-list-create/components/price-list-create-form/price-list-create-form.tsx`
- Prices can be tax-inclusive per currency or region `packages/modules/pricing/src/models/price-preference.ts`

**Where in the code:** `packages/modules/pricing/src/`, `packages/admin/dashboard/src/routes/price-lists/`

**Errors users can hit:** Not inventoried at standard depth.

**Confidence:** High

### CAP-promotions: Discounts, campaigns, budgets

**What it does:** Merchants create discount codes or automatic discounts: amount or
percentage off items, orders or shipping, and "buy X get Y". Promotions can be grouped
into campaigns with dates and spend or usage budgets.

**Rules and limits:**
- Types `standard` and `buyget`; statuses `draft`, `active`, `inactive` `packages/core/utils/src/promotion/index.ts`
- Percentages must be 0 to 100; buy-get needs minimum buy quantity and apply quantity `packages/modules/promotion/src/utils/validations/application-method.ts:48-93`
- Targeting rules: customer group, region, shipping country, sales channel, product, category, collection, type, tag, shipping option type `packages/medusa/src/api/admin/promotions/utils/rule-attributes-map.ts`
- Campaign budgets: total spend, total uses, or per-customer spend or uses; a promotion that would exceed its budget is not applied `packages/modules/promotion/src/utils/compute-actions/usage.ts`
- Each promotion can also have its own usage limit `packages/modules/promotion/src/models/promotion.ts`

**Related:** [Promotions at checkout](journeys/promotions-at-checkout.md)

**Errors users can hit:** Percentage outside 0-100, buy-get without quantities, or fixed amount without currency is rejected at setup `packages/modules/promotion/src/utils/validations/application-method.ts:48-93`. At checkout, non-qualifying codes are skipped silently (see [promotions journey](journeys/promotions-at-checkout.md)).

**Confidence:** High

### CAP-inventory: Stock per location, reservations

**What it does:** Merchants track stock for each inventory item at each stock location,
edit levels in bulk, and see or adjust reservations that hold stock for orders.

**Rules and limits:**
- Available stock = stocked minus reserved, per location `packages/modules/inventory/src/models/inventory-level.ts`
- One variant can consume several inventory items (kits and bundles) through a required quantity `packages/modules/link-modules/src/definitions/product-variant-inventory-item.ts`
- Reservations are created at order placement at the first location with enough stock `packages/core/core-flows/src/cart/steps/reserve-inventory.ts`

**Where in the code:** `packages/admin/dashboard/src/routes/inventory/`, `packages/admin/dashboard/src/routes/reservations/`, `packages/modules/inventory/src/`

**Errors users can hit:** Reserving more than is available: "Not enough stock available for item ... at location ..." unless backorders are allowed `packages/modules/inventory/src/services/inventory-module.ts`.

**Confidence:** High

### CAP-order-management: Fulfill, ship, deliver, cancel

**What it does:** Merchants view and export orders, create fulfillments from a stock
location, mark them shipped and delivered, cancel fulfillments, archive and cancel orders.

**Rules and limits:**
- Shipped fulfillments cannot be canceled `packages/core/core-flows/src/order/workflows/cancel-order-fulfillment.ts`
- An order cannot be canceled if it is completed or has any fulfillment that is not canceled `packages/core/core-flows/src/order/workflows/cancel-order.ts:71-104`
- Canceling refunds captured payments, cancels uncaptured ones and releases reservations `packages/core/core-flows/src/order/workflows/cancel-order.ts`
- Items with tracked inventory need a reservation before they can be fulfilled `packages/core/core-flows/src/order/workflows/create-fulfillment.ts`
- Payment and fulfillment status shown on an order are calculated, not stored `packages/core/core-flows/src/order/utils/aggregate-status.ts`

**Related:** [Order fulfillment journey](journeys/order-fulfillment.md)

**Errors users can hit:** "Cannot cancel a completed order. Please use the return process to handle refunds or exchanges." and "All fulfillments must be canceled before canceling an order" `packages/core/core-flows/src/order/workflows/cancel-order.ts:81-96`.

**Confidence:** High

### CAP-post-purchase-changes: Returns, claims, exchanges, edits

**What it does:** Merchants handle returns (request and receive), claims (merchant fault:
refund or replace), exchanges (swap items) and order edits (add or change items). All four
use one "begin, stage changes, confirm" engine called order changes.

**Rules and limits:**
- Cannot return more than was fulfilled; cannot receive more than was requested `packages/modules/order/src/utils/actions/return-item.ts`, `packages/modules/order/src/utils/actions/receive-return-item.ts`
- A return cannot be canceled after any item is received `packages/core/core-flows/src/order/workflows/return/cancel-return.ts`
- Exchanges need at least one item in and one item out `packages/core/core-flows/src/order/workflows/exchange/confirm-exchange-request.ts`
- Order edits cannot reduce a quantity below what is already fulfilled `packages/modules/order/src/utils/actions/item-update.ts`
- Any price difference is settled through a new payment collection or credit `packages/core/core-flows/src/order/workflows/claim/confirm-claim-request.ts`

**Related:** [Returns, claims and exchanges journey](journeys/returns-claims-exchanges.md)

**Errors users can hit:** Returning more than fulfilled, receiving more than requested, canceling a received return, or confirming an exchange without items in and out are all rejected (see [returns journey](journeys/returns-claims-exchanges.md)).

**Confidence:** High for rules; Medium for customer-facing confirmation of edits.

### CAP-refunds: Refunds and store credit

**What it does:** Merchants refund captured payments with a reason and note, and add
credit lines to settle balances.

**Rules and limits:**
- Cannot refund more than was captured `packages/core/core-flows/src/payment/workflows/refund-payment.ts`
- Credit lines are only allowed when there is an outstanding balance, and only up to that amount `packages/core/core-flows/src/order/workflows/create-order-credit-lines.ts`
- Refund reasons are configurable in Settings `packages/admin/dashboard/src/routes/refund-reasons/`

**Where in the code:** `packages/medusa/src/api/admin/payments/[id]/refund/route.ts`

**Errors users can hit:** Refunding more than captured is rejected `packages/core/core-flows/src/payment/workflows/refund-payment.ts`.

**Confidence:** High

### CAP-draft-orders: Create orders for customers

**What it does:** Staff build an order on a customer's behalf (phone or in-store sales),
edit items, shipping and promotions, then convert it to a real order.

**Rules and limits:**
- Draft orders are ordinary orders with status `draft` `packages/medusa/src/api/admin/draft-orders/route.ts`
- The screens come from the `@medusajs/draft-order` plugin, which is on by default `packages/core/utils/src/common/define-config.ts:228-237`, `packages/plugins/draft-order/README.md`
- Converting reserves stock, recalculates tax and emits the same "order placed" signal as checkout `packages/core/core-flows/src/draft-order/workflows/convert-draft-order.ts`

**Errors users can hit:** Converting something that is not a draft is rejected `packages/core/core-flows/src/draft-order/workflows/convert-draft-order.ts`.

**Confidence:** High

### CAP-customer-management: Customers and customer groups

**What it does:** Merchants list, create and export customers, manage addresses, and group
customers for targeted prices and promotions.

**Rules and limits:**
- Guest and registered records can exist for the same email `packages/modules/customer/src/models/customer.ts:30-34`
- Group names are unique `packages/modules/customer/src/models/customer-group.ts`

**Where in the code:** `packages/admin/dashboard/src/routes/customers/`, `packages/admin/dashboard/src/routes/customer-groups/`

**Errors users can hit:** Duplicate customer group names are rejected `packages/modules/customer/src/models/customer-group.ts`.

**Confidence:** High

### CAP-shipping-setup: Locations, zones, shipping options

**What it does:** Merchants define stock locations, the areas each location serves (service
zones by country, province, city or postcode), and the shipping options offered there with
flat or carrier-calculated prices.

**Rules and limits:**
- Shipping options shown at checkout come from locations linked to the cart's sales channel and must be enabled for the store `packages/core/core-flows/src/cart/workflows/list-shipping-options-for-cart.ts`
- Price types: `flat` or `calculated` `packages/modules/fulfillment/src/models/shipping-option.ts`
- Only a manual fulfillment provider ships in this repository; carrier integrations are add-ons `packages/modules/providers/fulfillment-manual/src/services/manual-fulfillment.ts`

**Where in the code:** `packages/admin/dashboard/src/routes/locations/`, `packages/modules/fulfillment/src/models/`

**Errors users can hit:** Not inventoried at standard depth; at checkout, an option without a price is rejected `packages/core/core-flows/src/cart/workflows/add-shipping-method-to-cart.ts`.

**Confidence:** Medium (rule evaluation not fully traced).

### CAP-markets-and-taxes: Regions, currencies, tax rates

**What it does:** A region is a market: a set of countries with one currency, its payment
providers and tax behavior. Tax regions hold rates per country and province, with overrides.

**Rules and limits:**
- Each region has exactly one currency and an `automatic_taxes` setting (default on) `packages/modules/region/src/models/region.ts`
- Payment providers are enabled per region `packages/modules/link-modules/src/definitions/region-payment-provider.ts`
- Only the built-in "system" tax calculator ships here; Avalara-style providers are add-ons `packages/modules/tax/src/providers/system.ts`

**Where in the code:** `packages/admin/dashboard/src/routes/regions/`, `packages/admin/dashboard/src/routes/tax-regions/`

**Errors users can hit:** Forcing tax calculation on a cart without a shipping country is rejected `packages/core/core-flows/src/tax/steps/get-item-tax-lines.ts`.

**Confidence:** Medium

### CAP-sales-channels: Sales channels and storefront keys

**What it does:** A sales channel is a place you sell (web store, app, POS, B2B portal). It
decides which products are sold and which stock locations serve it. Each storefront uses a
publishable key linked to one or more channels.

**Rules and limits:**
- A cart's channel comes from the key; mismatches are rejected `packages/medusa/src/api/utils/middlewares/common/ensure-pub-key-sales-channel-match.ts`
- Disabled channels cannot be used for new carts `packages/core/core-flows/src/cart/steps/find-sales-channel.ts`

**Where in the code:** `packages/admin/dashboard/src/routes/sales-channels/`, `packages/modules/sales-channel/src/models/sales-channel.ts`

**Errors users can hit:** A cart for a sales channel outside the key's scope, or a disabled channel, is rejected `packages/medusa/src/api/utils/middlewares/common/ensure-pub-key-sales-channel-match.ts`.

**Confidence:** High

### CAP-team-and-access: Staff users, invites, secret keys

**What it does:** Merchants invite staff by email, manage users, and create secret API keys
for server-to-server access to the Admin API.

**Rules and limits:**
- Users are created by accepting an invite; there is no "create user" Admin API `packages/medusa/src/api/admin/users/route.ts`
- Invites expire after 24 hours by default `packages/modules/user/src/services/user-module.ts`
- Secret keys are sent with HTTP Basic auth and can be revoked `packages/core/framework/src/http/middlewares/authenticate-middleware.ts`
- Roles and permissions (RBAC) and SSO exist but are Enterprise-licensed and not mapped here.

**Where in the code:** `packages/admin/dashboard/src/routes/users/`, `packages/admin/dashboard/src/routes/api-key-management/`

**Errors users can hit:** Expired invites are rejected `packages/modules/user/src/services/user-module.ts`.

**Confidence:** High

### CAP-translations: Multi-language content

**What it does:** Merchants translate product and catalog fields per locale; storefronts
fetch localized content. Off unless the `translation` feature flag is enabled.

**Rules and limits:**
- Admin translation and locale APIs and the Settings menu entry are hidden without the flag `packages/medusa/src/feature-flags/translation.ts`, `packages/admin/dashboard/src/components/layout/settings-layout/settings-layout.tsx`

**Where in the code:** `packages/modules/translation/src/models/translation.ts`

**Errors users can hit:** Translation APIs are unavailable unless the flag is on `packages/medusa/src/feature-flags/translation.ts`.

**Confidence:** Medium

## Developer capabilities

### CAP-extensibility: Customize and extend the platform

**What it does:** Developers add their own data modules, link them to built-in ones, wrap or
hook into built-in workflows, react to events, run scheduled jobs, add API routes, and add
admin widgets and pages. Plugins package these for reuse.

**Rules and limits:**
- Built-in workflows expose hooks (for example `validate` on checkout) for custom logic `packages/core/core-flows/src/cart/workflows/complete-cart.ts:403-406`
- Admin widgets attach to named zones on almost every screen `packages/admin/admin-shared/src/extensions/widgets/constants.ts`
- Two official plugins ship in this repo: draft orders and loyalty (gift cards) `packages/plugins/draft-order/README.md`, `packages/plugins/loyalty/src/subscribers/create-gift-card.ts`

**Related:** [how-it-is-built.md](how-it-is-built.md)

**Errors users can hit:** Not applicable (developer capability).

**Confidence:** High
