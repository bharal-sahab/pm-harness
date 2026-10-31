---
id: PRD-<slug>
type: prd
title: <Initiative title>
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [<BRIEF-slug>, <DES-slug>]
capabilities: [CAP-<slug>]
code_refs: [<path/to/file.ts>]
owner: <PM name>
---

# <Initiative title>

**Summary:** <Two or three sentences: the problem, who has it, and what will change.>

## Problem

<Who has the problem, when, and how often. What it costs them and the business.>

**Evidence:** <Links to research, data, tickets: [RES-slug](research.md). If there is none,
write "Hypothesis: not yet validated" and suggest research-plan.>

## Current behavior

<How the product works today in this area, from pm/product and the code. Each fact cited.>

- <fact> `<path/to/file.ts:42>`

## Goals and metrics

| Metric | Type | Baseline | Target | Measured in |
|--------|------|----------|--------|-------------|
| <metric> | Primary | <value or "unknown - see Q1"> | <value> | <analytics tool, table, or report> |
| <metric> | Guardrail | <value> | Must not get worse | <source> |

## Users and scenarios

- **<User type>** wants to <job>, so that <outcome>.

## Requirements

| ID | Requirement | Priority | Capability |
|----|-------------|----------|------------|
| R1 | <Observable behavior: "When ..., the user ..."> | must | CAP-<slug> |
| R2 | <...> | should | CAP-<slug> |

## Edge cases and errors

| Case | Today | Required behavior |
|------|-------|-------------------|
| <case from "Errors users can hit"> | <what happens now> `<path>` | <what should happen, or "out of scope"> |

## User experience

<Link to [design](design.md) or the journey this changes. A short flow or mermaid diagram
if there is no design yet.>

## Rollout

<Feature flag or setting to use, who gets it first, how to turn it off.>

## Non-goals

- <Tempting adjacent work we are not doing, and why>

## Assumptions

- <Defaults the PM accepted without evidence>

## Open questions

| # | Question | Owner | Needed by |
|---|----------|-------|-----------|
| Q1 | <question> | <person or team> | <stage or date> |
