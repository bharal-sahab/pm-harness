---
name: product-map
description: Scans a product codebase (web, mobile, API, or platform) and writes a plain-language product knowledge base under pm/product - overview, capability map, user journeys, glossary, data model, integrations, and architecture - with every claim cited to code. Use when a PM is new to a product or repo, asks "how does this product work", wants to onboard onto or map a codebase, or when pm/product does not exist yet.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Product Map

Turn a codebase into a product knowledge base that a product manager can read without
engineering help, and that every other harness skill reuses as context.

The output is a set of markdown pages in `pm/product/`. They describe **what the product
does today, for whom, and where in the code that lives**. They do not describe how to
write code.

## Non-negotiables

- **Read-only on product code.** Only write inside `pm/`.
- **Cite everything.** Every statement about behavior ends with a backticked, repo-relative
  path, e.g. `packages/core/core-flows/src/cart/workflows/complete-cart.ts`. Add `:line` when
  a specific line proves the point.
- **Unknown beats wrong.** If the code does not answer it, write it in `open-questions.md`.
- **Respect `exclude_paths`** in `pm/config.yaml`. Never open, quote, or describe them.
- **Plain language.** Follow [references/writing-for-pms.md](references/writing-for-pms.md).

## Workflow

Copy this checklist into your reply and keep it updated:

```
Product map progress:
- [ ] 1. Set up pm/ and config
- [ ] 2. Survey the repository
- [ ] 3. Checkpoint: confirm profile and scope with the PM
- [ ] 4. Investigate each capability area
- [ ] 5. Checkpoint: confirm page plan
- [ ] 6. Write pages
- [ ] 7. Audit and fix
- [ ] 8. Hand off
```

### 1. Set up `pm/` and config

- If `pm/CONVENTIONS.md` is missing, copy [templates/CONVENTIONS.md](templates/CONVENTIONS.md) there.
- If `pm/config.yaml` is missing, create it from [templates/config.yaml](templates/config.yaml).
- If `pm/product/_meta.yaml` already exists, stop and suggest the `product-map-refresh`
  skill instead, unless the PM explicitly wants a full rebuild.

### 2. Survey the repository

Run the survey script from this skill's folder against the repo root:

```bash
python3 <this-skill-dir>/scripts/survey.py . > /tmp/pm-survey.md
```

If the repo has no git metadata, pass `--commit <sha>` when the PM knows it.
Then read the repo's own `README`, `AGENTS.md`/`CLAUDE.md`, and top-level docs it lists.

Use the survey plus [references/platform-signals.md](references/platform-signals.md) to decide:

- **Product type and platforms**: web app, mobile app, API, platform/SDK, or a mix.
- **Audiences**: who uses each surface (e.g. shoppers, merchants, developers, admins).
- **Capability areas**: 6 to 20 business areas (e.g. Catalog, Checkout, Payments).
  Derive them from domain folders, modules, routes, and screens, not from tech layers.
- **License-restricted or sensitive paths**: anything the survey flags under
  "License-restricted areas", plus secrets or customer data. Propose them as `exclude_paths`.
- **Noise to skip**: docs sites, generated code, fixtures, and example apps unless they are the product.

### 3. Checkpoint: confirm profile and scope

Show the PM a short profile and wait for confirmation before investigating:

```
Product: <name> - <one sentence>
Platforms: <web / mobile / api / platform>
Audiences: <list>
Capability areas (proposed): <list with one line each>
Excluded paths: <list and reason>
Depth: quick (overview, capabilities, glossary) | standard (all pages, 3-5 journeys) | deep (all pages, 6-10 journeys)
```

Default depth is **standard**. Write the confirmed values into `pm/config.yaml`.

### 4. Investigate each capability area

For each area, trace from the outside in:

1. **Entry points**: the routes, screens, API endpoints, CLI commands, or jobs that expose it.
2. **Business logic**: the services/workflows they call. Note rules, limits, validations,
   and what happens on failure.
3. **Data**: the entities and statuses involved (enums are gold: they list real states).
4. **Errors**: every error a user can hit along the path. Search the entry point and the
   logic it calls for thrown errors and validation messages, and record each one with its
   trigger. PMs ask "what happens if..." more than anything else; these answer it.
5. **Side effects**: events, notifications, emails, webhooks, third-party calls.
6. **Switches**: feature flags, config options, permissions that change behavior.

Breadth before depth: skim every area before going deep on any one. If your agent supports
parallel subagents, give each one a single capability area and ask it to return notes with
file citations; then write the pages yourself so the voice stays consistent.

Rate each finding: **High** (you read the code path end to end), **Medium** (read part of it
or inferred from names and types), **Low** (guess from structure; also add an open question).

### 5. Checkpoint: confirm page plan

List the pages you will write, the journeys you picked (the 3-10 flows that matter most to
users or revenue), and anything you will leave out. Wait for confirmation.

### 6. Write pages

Write in this order, using the templates:

| Page | Template |
|------|----------|
| `pm/product/capabilities.md` | [templates/capabilities.md](templates/capabilities.md) |
| `pm/product/journeys/<slug>.md` | [templates/journey.md](templates/journey.md) |
| `pm/product/data-model.md` | [templates/data-model.md](templates/data-model.md) |
| `pm/product/integrations.md` | [templates/integrations.md](templates/integrations.md) |
| `pm/product/how-it-is-built.md` | [templates/how-it-is-built.md](templates/how-it-is-built.md) |
| `pm/product/domain-glossary.md` | [templates/domain-glossary.md](templates/domain-glossary.md) |
| `pm/product/OVERVIEW.md` (write last; it is the hub) | [templates/OVERVIEW.md](templates/OVERVIEW.md) |
| `pm/product/open-questions.md` | [templates/open-questions.md](templates/open-questions.md) |
| `pm/product/_meta.yaml` | [templates/_meta.yaml](templates/_meta.yaml) |

Rules while writing:

- Capability IDs are `CAP-<slug>` and never change once published; other skills link to them.
- Every journey includes at least one mermaid diagram and a "What can go wrong" section.
- Every capability has an "Errors users can hit" table built from step 4. If the area has
  no user-facing errors, say so explicitly.
- Link pages to each other with relative links so the knowledge base is navigable.
- In `_meta.yaml`, record `page_sources`: for each page, the folders it was built from.
  The `product-map-refresh` skill uses this to update only the pages affected by a change.

### 7. Audit and fix

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo . --strict
```

Fix every error. Then pick five random citations, open each file, and confirm it really
supports the sentence that cites it. Fix or downgrade confidence for any that do not.

### 8. Hand off

Tell the PM, in a few sentences: what was written, the suggested reading order
(OVERVIEW, capabilities, the top journey, glossary), the three most important open
questions to take to engineering, and the next skills to try (`ask-the-product` for
questions, `prd` or `research-plan` to start an initiative).

## Large repositories

- Map the product, not the repo. A monorepo with 100 packages may have 12 capability areas.
- Skip framework internals unless they change what users experience; summarize them in
  `how-it-is-built.md` in one paragraph each.
- Prefer enums, route files, API specs, and workflow definitions over implementation files.
  They describe behavior densely.
- Time-box each area. Record what you skipped in `_meta.yaml` under `not_covered`.
