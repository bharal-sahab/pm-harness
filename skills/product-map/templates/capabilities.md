---
id: PROD-capabilities
type: product-page
title: <Product> capabilities
status: draft
updated: <YYYY-MM-DD>
source_commit: <sha>
---

# Capabilities

Each capability is something a user can accomplish. IDs are stable: other artifacts
(PRDs, stories, test plans) reference them.

## Summary

| ID | Capability | Audience | Surface | Confidence |
|----|------------|----------|---------|------------|
| CAP-<slug> | <Name> | <Who> | <Where> | High |

## <Area name>

### CAP-<slug>: <Capability name>

**What it does:** <One or two sentences in user terms.>

**Who uses it:** <Audience>, through <surface>.

**Rules and limits:**
- <Business rule found in code> `<path/to/file.ts>`
- <Validation, limit, or edge case> `<path/to/file.ts:42>`

**Errors users can hit:**

| When | Message or outcome | Code |
|------|--------------------|------|
| <Adding an item with no price> | <"... do not have a price"> | `<path/to/file.ts:42>` |

**Switches:** <Feature flags, config, permissions that change behavior, or "none found".>

**Related:** [<journey>](journeys/<slug>.md), data: <Entity> in [data-model.md](data-model.md)

**Where in the code:** `<entry point>`, `<logic>`, `<data model>`

**Confidence:** High | Medium | Low - <why>
