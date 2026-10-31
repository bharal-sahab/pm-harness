---
id: PROD-domain-glossary
type: product-page
title: Medusa glossary
status: draft
updated: 2026-10-30
source_commit: 2cfefbd370fd133e629b8d545a28460af5ffd01b
---

# Glossary

| Term | Meaning in this product | Also called | Code name | Defined in |
|------|-------------------------|-------------|-----------|------------|
| Region | A market: a set of countries sharing one currency, payment methods and tax behavior | Market | `Region` | `packages/modules/region/src/models/region.ts` |
| Sales channel | A place you sell (web store, app, POS, B2B portal); decides which products and stock apply | Storefront, channel | `SalesChannel` | `packages/modules/sales-channel/src/models/sales-channel.ts` |
| Publishable key | Public ID a storefront sends on every request; linked to sales channels | Storefront key | `ApiKey` type `publishable` | `packages/modules/api-key/src/models/api-key.ts` |
| Secret key | Private key for server-to-server Admin API access | Admin API key | `ApiKey` type `secret` | `packages/modules/api-key/src/models/api-key.ts` |
| Product | An item shoppers browse | | `Product` | `packages/modules/product/src/models/product.ts` |
| Variant | The specific purchasable version of a product (size, color) | SKU | `ProductVariant` | `packages/modules/product/src/models/product-variant.ts` |
| Inventory item | The physical thing counted in stock; a variant can use several (bundles) | Stock item | `InventoryItem` | `packages/modules/inventory/src/models/inventory-item.ts` |
| Stock location | A warehouse or store that holds stock and ships orders | Warehouse | `StockLocation` | `packages/modules/stock-location/src/models/stock-location.ts` |
| Reservation | Stock held for an order line until it ships | Allocation | `ReservationItem` | `packages/modules/inventory/src/models/reservation-item.ts` |
| Backorder | Selling a variant even when it is out of stock | | `allow_backorder` | `packages/modules/product/src/models/product-variant.ts` |
| Cart | The shopper's basket before checkout | Basket | `Cart` | `packages/modules/cart/src/models/cart.ts` |
| Guest customer | A customer record created from a checkout email without an account | | `has_account: false` | `packages/modules/customer/src/models/customer.ts` |
| Payment collection | The amount owed for a cart, order, claim or exchange | | `PaymentCollection` | `packages/modules/payment/src/models/payment-collection.ts` |
| Payment session | One payment attempt with one provider | Payment intent (Stripe) | `PaymentSession` | `packages/modules/payment/src/models/payment-session.ts` |
| Authorize / capture | Reserve the money on the card / actually take it | | | `packages/core/core-flows/src/payment/steps/authorize-payment-session.ts` |
| Credit line | Store credit applied to settle a balance | Store credit | `CreditLine` | `packages/modules/cart/src/models/credit-line.ts` |
| Order change | A staged change to an order (return, claim, exchange, edit) that must be confirmed | | `OrderChange` | `packages/modules/order/src/models/order-change.ts` |
| Claim | Merchant-fault fix: refund or replacement for missing, wrong or broken items | | `OrderClaim` | `packages/modules/order/src/models/claim.ts` |
| Exchange | Customer swaps items for others | Swap | `OrderExchange` | `packages/modules/order/src/models/exchange.ts` |
| Order edit | Changing items on an order after placement | | `order-edit` workflows | `packages/core/core-flows/src/order/workflows/order-edit/begin-order-edit.ts` |
| Draft order | An order staff build for a customer before it is placed | Manual order | status `draft` | `packages/medusa/src/api/admin/draft-orders/route.ts` |
| Fulfillment | One shipment of items from a location | Shipment | `Fulfillment` | `packages/modules/fulfillment/src/models/fulfillment.ts` |
| Shipping profile | Group of products that ship the same way (e.g. oversized) | | `ShippingProfile` | `packages/modules/fulfillment/src/models/shipping-profile.ts` |
| Service zone | Geographic area a location ships to | Delivery zone | `ServiceZone` | `packages/modules/fulfillment/src/models/service-zone.ts` |
| Shipping option | A delivery choice shown at checkout with a price | Shipping method (once chosen) | `ShippingOption` | `packages/modules/fulfillment/src/models/shipping-option.ts` |
| Promotion | A discount, by code or automatic | Coupon, discount | `Promotion` | `packages/modules/promotion/src/models/promotion.ts` |
| Campaign | A group of promotions with dates and a budget | | `Campaign` | `packages/modules/promotion/src/models/campaign.ts` |
| Price list | Sale prices or override prices for a period or customer group | | `PriceList` | `packages/modules/pricing/src/models/price-list.ts` |
| Customer group | Segment of customers for targeted prices and promotions | Segment | `CustomerGroup` | `packages/modules/customer/src/models/customer-group.ts` |

## Easily confused

- **Shipping option vs shipping method:** the option is what the merchant configures; the
  method is the option a shopper picked on their cart or order.
- **Variant vs inventory item:** a T-shirt bundle variant may consume three inventory items.
  Stock is counted on inventory items, not variants.
- **Order status vs payment status vs fulfillment status:** only order status is stored.
  The other two are calculated from payments and fulfillments.
- **Claim vs exchange:** claims are the merchant's fault (no charge to the customer);
  exchanges are the customer's choice and may require a payment difference.
- **Sale vs override price list:** sale only applies when cheaper than the regular price;
  override always applies.
