---
name: tech-impact
description: Analyzes what a proposed change touches in the codebase (screens, APIs, data, workflows, events, integrations, and feature flags), with every finding cited to code, then lists the risks, what to build first, where existing tests live, and the sharp questions to ask engineering. Written in plain language so the PM learns how the product is built. Use when a PM has a PRD or idea and asks "what does this touch", "how big is this", "what are the risks", or wants to prepare for a refinement or sizing session with engineering.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Tech Impact

Read the code the way a tech lead would before a refinement session, and explain what
you find to the PM. The output does not replace engineering's estimate. It makes the
conversation with engineering faster and sharper, and teaches the PM how the product is
built along the way.

## Non-negotiables

- **Read-only on product code.** Only write inside `pm/`.
- **Cite every finding** with a backticked, repo-relative path, adding `:line` when one
  line proves it.
- **No time estimates.** Use relative sizes (S, M, L) with the reason. Engineering owns
  the estimate. Say so in the document.
- **Separate fact from inference.** "The API returns only the cart" is a fact with a
  citation. "This probably needs a new field" is an inference; label it.
- **Respect `exclude_paths`** in `pm/config.yaml`.

## Workflow

```
Tech impact progress:
- [ ] 1. Read the requirements
- [ ] 2. Locate each requirement in the code
- [ ] 3. Map the impact by surface
- [ ] 4. Risks, sequencing, and tests
- [ ] 5. Questions for engineering
- [ ] 6. Write, check, and hand off
```

### 1. Read the requirements

Read `pm/initiatives/<slug>/prd.md` and list its requirement IDs. Without a PRD, ask the
PM for the change in a few sentences, and number the parts yourself (`R1`, `R2`, ...).
Also read `design.md` if it exists: screens and states often reveal work the PRD hides.

### 2. Locate each requirement in the code

For each requirement, start from the knowledge base, then go to the code:

1. The capability's "Where in the code" and the journey citations in `pm/product/`.
2. Trace outside in: **entry point** (route, screen, endpoint, job), then **logic**
   (service, workflow), then **data** (models, enums, migrations), then **output** (API
   response, UI, events, emails).
3. Note where today's behavior is decided. That is usually where the change lands.
4. Look for code that already does part of the job. Partial support that is not exposed
   is the most common and most valuable finding.

See [references/impact-checklist.md](references/impact-checklist.md) for what to look for
on each surface and how to find it quickly.

### 3. Map the impact by surface

Fill the impact table in [templates/tech-impact.md](templates/tech-impact.md). One row
per surface touched:

| Surface | Examples |
|---------|----------|
| User interface | Web pages, mobile screens, admin screens, emails |
| API | Endpoints, request and response shapes, SDKs, webhooks |
| Business logic | Services, workflows, validation rules, jobs |
| Data | Tables, fields, statuses, migrations, backfills |
| Events and integrations | Events emitted or consumed, third-party calls |
| Configuration | Feature flags, settings, permissions |

For each row: what changes (plain language), the files (cited), the change type (new,
modify, or config only), and the size (S, M, L) with a one-line reason.

**Who else depends on it?** For every API or event you change, find its consumers:
storefronts, mobile apps, SDKs, partner integrations, plugins, and extension points. A
response shape change that is fine for the web app can break an old mobile app version.

### 4. Risks, sequencing, and tests

- **Risks**: go through the categories in the checklist reference (breaking changes, data
  migration, money, security, performance, permissions, third parties, extensibility,
  localization). Keep only the ones that apply. Each gets likelihood, impact, and a
  mitigation.
- **Sequencing**: what must exist before what. Typical order: data, then logic, then
  API, then UI. Point out pieces that could ship on their own.
- **Rollout switches**: existing feature-flag systems or settings that allow a gradual or
  reversible launch.
- **Existing tests**: find test files that cover the touched code (search for the file
  or function names under test folders). List them. `test-plan` builds on this.

### 5. Questions for engineering

This is the most valuable section. Write five to ten questions that only someone who
read the code could ask. Each one cites what prompted it:

- Weak: "How hard is this?"
- Strong: "The workflow already computes `skippedPromoCodes` with a reason, but the store
  route discards the result (`packages/medusa/src/api/store/carts/[id]/promotions/route.ts:14-31`).
  Can we return it without breaking the SDK's response type?"

### 6. Write, check, and hand off

Write `pm/initiatives/<slug>/tech-impact.md` from the template. Frontmatter:
`id: TI-<slug>`, `type: tech-impact`, `derived_from: [PRD-<slug>]`, `capabilities`, and
`code_refs` with the main files. End with **"Terms used"**, a short glossary of the
technical words in the document, in plain language, so the PM can reuse them.

If you learned durable facts about current behavior that `pm/product/` lacks, offer to add
them to the right page (following `ask-the-product`'s write-back rules).

Update the initiative README row, then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Hand off in a few sentences: the overall size and why, the top risk, the most important
question for engineering, and the next step (`epics-and-stories`).
