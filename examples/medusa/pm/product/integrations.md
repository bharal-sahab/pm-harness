---
id: PROD-integrations
type: product-page
title: Medusa integrations and switches
status: draft
updated: 2026-10-30
source_commit: 2cfefbd370fd133e629b8d545a28460af5ffd01b
---

# Integrations and switches

Medusa connects to outside services through **providers**: plug-ins that each implement
one job (take payments, send email, store files). Swapping a provider is configuration, not
a rewrite. Providers in this repository live in `packages/modules/providers/`.

## Third-party services

| Service | Used for | Required? | Code |
|---------|----------|-----------|------|
| PostgreSQL | All business data | Yes | `packages/core/utils/src/common/define-config.ts` |
| Redis | Production queues, locks, caching, multi-server setups | Optional (recommended for production) | `packages/modules/event-bus-redis/package.json` |
| Stripe | Card payments plus Bancontact, BLIK, giropay, iDEAL, Przelewy24, PromptPay, OXXO | Optional | `packages/modules/providers/payment-stripe/src/index.ts` |
| SendGrid | Transactional email | Optional | `packages/modules/providers/notification-sendgrid/src/services/sendgrid.ts` |
| AWS S3 (or S3-compatible) | Image and file storage | Optional (local disk by default) | `packages/modules/providers/file-s3/src/services/s3-file.ts` |
| Google, GitHub | Social login | Optional | `packages/modules/providers/auth-google/src/services/google.ts`, `packages/modules/providers/auth-github/src/services/github.ts` |
| PostHog | Product analytics events | Optional | `packages/modules/providers/analytics-posthog/src/services/posthog-analytics.ts` |
| Algolia InstantSearch | Storefront search UI adapter | Optional | `packages/core/instantsearch-adapter/package.json` |

**Not included:** tax calculation services (only a built-in "system" calculator) and
shipping carriers (only "manual" fulfillment) `packages/modules/tax/src/providers/system.ts`,
`packages/modules/providers/fulfillment-manual/src/services/manual-fulfillment.ts`.
**Enterprise-only (not mapped):** SSO through OIDC and role-based permissions.

### Payment details that affect product decisions

- The main Stripe provider authorizes at checkout and captures later unless configured to capture immediately; local payment methods capture automatically `packages/modules/providers/payment-stripe/src/core/stripe-base.ts`.
- Stripe webhooks arrive at `/hooks/payment/<provider>`; without a webhook secret, 3-D Secure and redirect payments can leave orders pending `packages/medusa/src/api/hooks/payment/[provider]/route.ts`, `packages/medusa/src/subscribers/payment-webhook.ts`.

## Public interfaces

| Interface | Who uses it | Code |
|-----------|-------------|------|
| Store API (`/store/...`) | Storefronts and mobile apps; needs a publishable key | `packages/medusa/src/api/store/` |
| Admin API (`/admin/...`) | Admin dashboard and back-office integrations; needs a staff login or secret key | `packages/medusa/src/api/admin/` |
| Auth API (`/auth/...`) | Login for customers and staff | `packages/medusa/src/api/auth/` |
| JavaScript SDK | Typed client for all three APIs | `packages/core/js-sdk/src/index.ts` |
| Payment webhooks (`/hooks/payment/...`) | Payment providers | `packages/medusa/src/api/hooks/payment/[provider]/route.ts` |
| Admin extensions | Widgets and pages added by developers | `packages/admin/admin-sdk/src/config/index.ts` |

## Feature flags and configuration

All flags default to **off** and are switched with environment variables `MEDUSA_FF_<KEY>`.

| Flag | Default | What it changes | Code |
|------|---------|-----------------|------|
| `translation` | off | Multi-language catalog content and the Translations settings page | `packages/medusa/src/feature-flags/translation.ts` |
| `index_engine` | off | Faster product filtering through a search index | `packages/medusa/src/feature-flags/index-engine.ts` |
| `view_configurations` | off | Saved, configurable admin table views and property labels (work in progress) | `packages/medusa/src/feature-flags/view-configurations.ts` |
| `caching` | off | Built-in caching (work in progress) | `packages/medusa/src/feature-flags/caching.ts` |
| `backend_hmr` | off | Developer hot reload; no product impact | `packages/medusa/src/feature-flags/backend-hmr.ts` |

Key configuration with product impact `packages/core/utils/src/common/define-config.ts`:
default login method (email and password), default fulfillment (manual), default
notifications (log only), default file storage (local disk), the draft orders plugin (on).

## Events other systems can react to

Signals are sent only after the process that triggers them succeeds
`packages/core/core-flows/src/common/steps/emit-event.ts`. Full list: `packages/core/utils/src/core-flows/events.ts`.

| Event | When |
|-------|------|
| `order.placed` | Checkout or draft-order conversion succeeds |
| `order.return_requested`, `order.return_received` | Return lifecycle |
| `order.transfer_requested` | A customer asks to claim an order |
| `cart.created`, `cart.updated`, `cart.customer_transferred` | Cart lifecycle |
| `auth.password_reset` | Password reset requested |

There is no built-in order confirmation email. A notification provider plus a listener on
`order.placed` is needed; a configurable notification listener exists for this
`packages/medusa/src/subscribers/configurable-notifications.ts`.

## Telemetry

Medusa sends anonymous usage data (versions, OS, enabled modules and flags) to Medusa;
disable with `MEDUSA_DISABLE_TELEMETRY=true` `packages/medusa-telemetry/src/store.js`.
