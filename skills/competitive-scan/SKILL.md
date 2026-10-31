---
name: competitive-scan
description: Compares competitors against your product's capabilities in pm/product/capabilities.md - feature by feature, with every competitor claim linked to a public source and every claim about your product cited to code - and writes the gaps, parity, differentiators, and patterns worth borrowing to pm/initiatives/<slug>/competitive-scan.md. Use when a PM asks how competitors handle something, wants a feature comparison or competitive matrix, needs to justify a gap in a PRD, or prepares positioning.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Competitive Scan

Compare like with like. Most competitive matrices compare a competitor's marketing page to
the team's memory of its own product. This one compares public evidence about competitors
to what your code actually does.

## Non-negotiables

- **Every competitor claim has a source**: a URL and the date you read it. Docs, help
  centers, changelogs, API references, and pricing pages beat marketing pages.
- **"Not found" is not "does not have".** Write "not found in public docs" unless a
  source says it is missing.
- **Every claim about your product is cited to code** or comes from `pm/product/`.
- **Public information only.** No logging into competitor accounts the PM does not own, no
  scraping that breaks terms of service, no confidential material.
- **Only write inside `pm/`.**

## Workflow

```
Competitive scan progress:
- [ ] 1. Scope
- [ ] 2. Our side
- [ ] 3. Their side
- [ ] 4. Compare and interpret
- [ ] 5. Write
```

### 1. Scope

Agree with the PM on:
- **Competitors**: 3 to 6. Include the obvious leaders, one fast-moving newcomer, and the
  alternative users actually use instead (often a spreadsheet, an agency, or doing nothing).
- **Scope**: the capabilities to compare (`CAP-` IDs) or the initiative's problem.
- **Lens**: features, user experience, pricing and packaging, or developer experience.

### 2. Our side

For each capability in scope, write what the product does today from
`pm/product/capabilities.md` and the journeys: supported, partly supported (and what is
missing), or not supported, each with a citation. Use `ask-the-product` for details the
knowledge base lacks. This is often where the PM finds the product does more than they thought.

### 3. Their side

If the agent can search and read the web, research each competitor from primary sources:
product docs, help center articles, API references, changelogs (what they shipped
recently tells you where they are going), and pricing pages. Otherwise, ask the PM for links
or material, and work from that. Record for each finding: the claim, the URL, and the date read.

### 4. Compare and interpret

Fill the matrix with one row per capability or sub-feature and one column per product.
Use plain values: **Yes**, **Partial** (with what is missing), **No** (with a source),
**Not found**, and a footnote link for every cell.

Then interpret. A matrix is not a conclusion:
- **Gaps that matter**: where competitors are ahead *and* the gap affects your users or
  deals (link research or sales evidence if any).
- **Parity**: table stakes you have or must have.
- **Differentiators**: where you are ahead. Say how durable the lead is.
- **Patterns worth borrowing**: UX or product approaches, described and linked, not copied.
- **Ignore list**: things competitors do that you should deliberately not do.

### 5. Write

Write `pm/initiatives/<slug>/competitive-scan.md` from
[templates/competitive-scan.md](templates/competitive-scan.md), with `id: CS-<slug>`,
`type: competitive-scan`, `derived_from: []` (or the brief), and `capabilities`. For a
product-wide scan not tied to one initiative, use an initiative named
`competitive-landscape`. Update the initiative README, then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Note the date in the title. Competitive information goes stale in months.
