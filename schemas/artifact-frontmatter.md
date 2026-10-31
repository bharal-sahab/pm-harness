# PM Harness Conventions

This file defines how the PM harness stores product knowledge and work artifacts.
Every harness skill reads and writes files under one folder, `pm/`, at the root of
the product repository. Following these rules is what lets one skill pick up
where another left off.

## Folder layout

```
pm/
  CONVENTIONS.md        # this file
  config.yaml           # product name, tracker settings, excluded paths
  product/              # how the product works today (written by product-map)
    OVERVIEW.md
    capabilities.md
    journeys/<journey-slug>.md
    domain-glossary.md
    data-model.md
    integrations.md
    how-it-is-built.md
    open-questions.md
    faq.md              # answered questions (written by ask-the-product)
    changelog.md        # how the product changed between refreshes (product-map-refresh)
    _meta.yaml
  initiatives/<initiative-slug>/   # one folder per piece of work
    README.md           # initiative index and current stage
    research-plan.md
    research.md
    competitive-scan.md
    brief.md
    design.md
    design-review.md
    prd.md
    tech-impact.md
    epics/EPIC-<initiative-slug>-<nn>.md
    stories/STORY-<initiative-slug>-<nnn>.md
    test-plan.md
    acceptance/AC-<initiative-slug>-<label>.md
    evals/
    release.md
    status/<yyyy-mm-dd>.md
  decisions/DEC-<nnnn>-<slug>.md
```

Create files lazily. Only write a file when there is something real to put in it.

## Frontmatter

Every markdown file under `pm/` (except `CONVENTIONS.md`) starts with YAML frontmatter.

### Required on every artifact

| Field | Meaning |
|-------|---------|
| `id` | Unique ID. Uppercase prefix, a hyphen, then lowercase slug and optional number. Example: `STORY-guest-checkout-003`. |
| `type` | One of the types in the table below. |
| `title` | Human-readable title. |
| `status` | One of `draft`, `in-review`, `approved`, `in-progress`, `done`, `superseded`. |
| `updated` | Date of last meaningful change, `YYYY-MM-DD`. |

### Required on initiative artifacts

| Field | Meaning |
|-------|---------|
| `initiative` | The initiative slug (the folder name under `pm/initiatives/`). |
| `derived_from` | List of artifact IDs this one was built from. Use `[]` for the first artifact. |

### Optional on any artifact

| Field | Meaning |
|-------|---------|
| `capabilities` | List of capability IDs from `pm/product/capabilities.md`, e.g. `[CAP-checkout]`. |
| `code_refs` | List of repo-relative file paths the artifact relies on. |
| `source_commit` | Git commit the content was checked against. |
| `owner` | Person accountable for the artifact. |
| `tracker` | Map: `system` (`jira`, `linear`, or `null`), `key`, `url`, `status` (the tracker's own status name), `synced_at`, and `synced_hash` (set by work-sync to detect local edits). |

### Story and epic extras

| Field | Applies to | Meaning |
|-------|------------|---------|
| `epic` | story | ID of the parent epic. |
| `requirements` | epic, story | PRD requirement IDs it delivers, e.g. `[R1, R3]`. |
| `priority` | epic, story | `p0`, `p1`, `p2`, or `p3`. |
| `estimate` | story | Team's estimate unit, or `null`. |

Acceptance criteria in a story are numbered `AC1`, `AC2`, ... so tests and acceptance
reports can point at one criterion: `STORY-guest-checkout-003/AC2`.

## Artifact types and ID prefixes

| `type` | ID prefix | Written by | Location |
|--------|-----------|------------|----------|
| `product-page` | `PROD` | product-map, product-map-refresh, ask-the-product | `pm/product/*.md` |
| `journey` | `JRN` | product-map | `pm/product/journeys/` |
| `initiative` | `INIT` | any skill that starts an initiative | `initiatives/<slug>/README.md` |
| `research-plan` | `RP` | research-plan | `research-plan.md` |
| `research` | `RES` | research-synthesis | `research.md` |
| `competitive-scan` | `CS` | competitive-scan | `competitive-scan.md` |
| `brief` | `BRIEF` | research-synthesis | `brief.md` |
| `design` | `DES` | design-brief | `design.md` |
| `design-review` | `DR` | design-review | `design-review.md` |
| `prd` | `PRD` | prd | `prd.md` |
| `tech-impact` | `TI` | tech-impact | `tech-impact.md` |
| `epic` | `EPIC` | epics-and-stories | `epics/` |
| `story` | `STORY` | epics-and-stories | `stories/` |
| `test-plan` | `TP` | test-plan | `test-plan.md` |
| `acceptance-report` | `AC` | acceptance-check | `acceptance/` |
| `eval` | `EVAL` | ai-evals | `evals/` |
| `release` | `REL` | release-notes | `release.md` |
| `status-update` | `SU` | status-update | `status/` |
| `decision` | `DEC` | any skill | `pm/decisions/` |

Capabilities are not separate files. They are `###` headings inside
`pm/product/capabilities.md`, each starting with its ID, e.g. `### CAP-checkout: Checkout`.

## Example

```yaml
---
id: STORY-guest-checkout-003
type: story
title: Shopper can check out without creating an account
status: draft
updated: 2026-10-30
initiative: guest-checkout
derived_from: [PRD-guest-checkout, EPIC-guest-checkout-01]
epic: EPIC-guest-checkout-01
priority: p1
capabilities: [CAP-checkout]
code_refs: [packages/core/core-flows/src/cart/workflows/complete-cart.ts]
tracker: { system: null, key: null }
---
```

## Initiative README

Every initiative folder has a `README.md`. It is the index for the work: what it is, where
it stands, and every artifact in it. The skill that starts the initiative creates it, and
every skill that writes an artifact in the folder updates its row.

```markdown
---
id: INIT-guest-checkout
type: initiative
title: Guest checkout
status: in-progress
updated: 2026-10-30
initiative: guest-checkout
derived_from: []
capabilities: [CAP-checkout]
owner: <PM name>
---

# Guest checkout

**Goal:** <one sentence: the outcome for users or the business>
**Stage:** <Research | Design | Definition | Build | QA | Released>

| Artifact | ID | Status | Updated |
|----------|----|--------|---------|
| [PRD](prd.md) | PRD-guest-checkout | approved | 2026-10-30 |

## Decisions

- <YYYY-MM-DD>: <decision> (<link to DEC- file if any>)
```

## Writing rules

1. **Ground every claim about the product.** When you say the product does something,
   cite the file that shows it, e.g. `(packages/medusa/src/api/store/carts/route.ts)`.
   Paths are relative to the repository root.
2. **Say "unknown" instead of guessing.** Add the question to `pm/product/open-questions.md`
   or to the artifact's "Open questions" section.
3. **Plain language first.** Explain a technical term the first time it appears in a file,
   and link it to `pm/product/domain-glossary.md` when it is defined there.
4. **Never change product code.** Harness skills only write inside `pm/`.
5. **Respect `exclude_paths`** from `pm/config.yaml`. Do not read, quote, or describe files
   under those paths (licensing, secrets, or confidentiality).
6. **Link artifacts, don't copy them.** Reference upstream artifacts by ID and relative link
   instead of pasting their content.
7. **Keep the initiative README current.** When a skill writes an artifact in an initiative,
   it adds or updates that artifact's row in the initiative README.
8. **Stop at checkpoints.** Before creating more than five files, or pushing anything to an
   external tool, show the plan and wait for the PM to confirm.

## `pm/config.yaml`

```yaml
product_name: Acme Commerce
platforms: [web, api]          # any of: web, mobile, api, platform, desktop, cli
audiences: [shoppers, merchants]
depth: standard                # quick | standard | deep (product-map coverage)
tracker:
  system: null                 # jira | linear | null (markdown only)
  project_key: null            # e.g. SHOP for Jira, team key for Linear
  default_issue_type: Story
exclude_paths: []              # repo-relative paths the harness must not read
glossary_overrides: {}         # term -> preferred plain-language definition
```

## Checking your work

Run the bundled checker (it ships inside several harness skills under `scripts/check_pm.py`):

```bash
python3 <skill-dir>/scripts/check_pm.py pm --repo .
```

It reports missing frontmatter fields, duplicate IDs, broken artifact references,
broken relative links, and `code_refs` that do not exist in the repository.
