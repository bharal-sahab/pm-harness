---
id: INIT-promo-code-feedback
type: initiative
title: Tell shoppers why a promo code did not apply
status: in-progress
updated: 2026-10-30
initiative: promo-code-feedback
derived_from: []
capabilities: [CAP-promotions, CAP-cart]
owner: Example PM
---

# Tell shoppers why a promo code did not apply

> Example initiative, run end to end with the harness skills on Medusa to show how the
> artifacts chain. The problem is real (from the product map's open questions); the
> people, metrics, and decisions are made up.

**Goal:** Every promo code a shopper enters either applies or comes back with a reason a
storefront can show.
**Stage:** Definition

| Artifact | ID | Status | Updated |
|----------|----|--------|---------|
| [PRD](prd.md) | PRD-promo-code-feedback | in-review | 2026-10-30 |
| [Tech impact](tech-impact.md) | TI-promo-code-feedback | draft | 2026-10-30 |
| [Epic 01: why a code did not apply](epics/EPIC-promo-code-feedback-01.md) | EPIC-promo-code-feedback-01 | draft | 2026-10-30 |
| [Epic 02: when a code stops applying](epics/EPIC-promo-code-feedback-02.md) | EPIC-promo-code-feedback-02 | draft | 2026-10-30 |
| Stories (5) | STORY-promo-code-feedback-001 to 005 | draft | 2026-10-30 |
| [Test plan](test-plan.md) | TP-promo-code-feedback | draft | 2026-10-30 |
| [Acceptance check: sample PR](acceptance/AC-promo-code-feedback-sample-pr.md) | AC-promo-code-feedback-sample-pr | draft | 2026-10-30 |
| [Status update](status/2026-10-30.md) | SU-promo-code-feedback-2026-10-30 | done | 2026-10-30 |

## Decisions

- 2026-10-30: R6 (merchant report on failed codes) is deferred. It is a could-have and
  needs logging that does not exist yet. It has no story on purpose.
- 2026-10-30: Ship in three steps: existing reasons first, then new reasons, then dropped
  codes behind a feature flag (from the [tech impact](tech-impact.md)).
