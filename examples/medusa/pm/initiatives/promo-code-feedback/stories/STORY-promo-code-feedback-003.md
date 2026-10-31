---
id: STORY-promo-code-feedback-003
type: story
title: Explain codes the cart does not qualify for
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
tracker:
  system: null
  key: null
---

# Explain codes the cart does not qualify for

**As a** shopper **I want** to know when my cart does not qualify for a code **so that** I
can change my cart or stop trying.

## Acceptance criteria

**AC1: Conditions not met**
- Given the code `BULK10` only applies to customers in the "Wholesale" group
- And the shopper is not in that group
- When the shopper adds `BULK10`
- Then `BULK10` is listed as not applied with the reason "conditions not met"
- And the entry does not mention the group or any rule value

**AC2: Currency not supported**
- Given the code `EUR5OFF` gives 5 off in EUR only
- And the cart's currency is USD
- When the shopper adds `EUR5OFF`
- Then it is listed with the reason "currency not supported"

**AC3: No qualifying items**
- Given a buy-X-get-Y code `SOCKS3` whose items are not in the cart
- When the shopper adds `SOCKS3`
- Then it is listed with the reason "conditions not met"

## Notes for engineering

- Unmet conditions and currency mismatch are skipped with `continue` today `packages/modules/promotion/src/services/promotion-module.ts:1040-1052`
- Which rule failed is only known inside the rule check, and must not leak (PRD R4) `packages/modules/promotion/src/services/promotion-module.ts:1044-1048`
- AC3 needs an engineering check: does a buy-get code with no matching items produce
  no adjustments, and so no outcome at all?

## Out of scope

- Telling the shopper how to qualify ("add 10 more"): a PRD non-goal.

## Dependencies

- STORY-promo-code-feedback-001.
