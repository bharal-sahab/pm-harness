---
id: STORY-promo-code-feedback-002
type: story
title: Explain codes that are not valid, expired, or not started
status: draft
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: [PRD-promo-code-feedback, EPIC-promo-code-feedback-01, TI-promo-code-feedback]
epic: EPIC-promo-code-feedback-01
requirements: [R2, R4]
priority: p1
estimate: null
capabilities: [CAP-promotions]
code_refs:
  - packages/modules/promotion/src/services/promotion-module.ts
  - packages/core/utils/src/promotion/index.ts
  - packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts
tracker:
  system: null
  key: null
---

# Explain codes that are not valid, expired, or not started

**As a** shopper **I want** to know if my code does not exist, has expired, or is not
active yet **so that** I stop retrying a code that will not work.

## Acceptance criteria

**AC1: Code does not exist**
- Given no promotion has the code `NOPE123`
- When a shopper adds `NOPE123`
- Then `NOPE123` is listed as not applied with the reason "not valid"

**AC2: Code is not active**
- Given the code `DRAFT15` belongs to a promotion with status draft or inactive
- When a shopper adds `DRAFT15`
- Then `DRAFT15` is listed with the reason "not valid", the same as a code that does not exist

**AC3: Campaign ended**
- Given the code `BLACKFRIDAY` belongs to a campaign that ended yesterday
- When a shopper adds `BLACKFRIDAY`
- Then it is listed with the reason "expired" (or "not valid" if PRD Q5 decides to merge them)

**AC4: Campaign not started**
- Given the code `XMAS` belongs to a campaign that starts next week
- When a shopper adds `XMAS`
- Then it is listed with the reason "not started" (or "not valid" if PRD Q5 decides to merge them)

**AC5: No internal details**
- Given any code that is not applied for the reasons above
- When it is listed
- Then the entry contains only the code and the reason, with no promotion ID, campaign name, or dates

## Notes for engineering

- Inactive and out-of-date codes are filtered out by the active-promotions query, so
  nothing records them today `packages/modules/promotion/src/services/promotion-module.ts:166-200`
- New engine outcomes go next to the existing two `packages/core/utils/src/promotion/index.ts:46-53`
- Map them to reasons where the existing two are mapped `packages/core/core-flows/src/cart/steps/prepare-adjustments-from-promotion-actions.ts:192-203`
- Draft orders and order-edit previews also read engine outcomes (tech impact, Question 2)

## Out of scope

- Conditions and currency (STORY-promo-code-feedback-003).

## Dependencies

- STORY-promo-code-feedback-001 (the response field).
- PRD Q5 decides whether "expired" and "not started" are shown separately.
