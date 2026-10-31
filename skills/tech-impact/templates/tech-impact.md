---
id: TI-<slug>
type: tech-impact
title: <Initiative title> - Technical impact
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [PRD-<slug>]
capabilities: [CAP-<slug>]
code_refs: [<path/to/main/file.ts>]
source_commit: <sha checked against>
---

# <Initiative title>: technical impact

> Prepared from the code by the PM harness to support a conversation with engineering.
> Sizes are relative (S, M, L), not estimates. Engineering owns the estimate.

**Overall size:** <S | M | L> - <one-line reason>
**Biggest risk:** <one line>
**Key finding:** <the one thing about the code that most changes the plan>

## Where each requirement lands

| Req | Where today's behavior is decided | What already exists |
|-----|-----------------------------------|---------------------|
| R1 | <plain description> `<path:line>` | <partial support, or "nothing"> |

## Impact by surface

| Surface | What changes | Files | Type | Size |
|---------|--------------|-------|------|------|
| API | <plain language> | `<path>` | modify | S - <reason> |

## Who else depends on this

| Changed thing | Consumers | Breaking? |
|---------------|-----------|-----------|
| <endpoint, event, or field> | <web app, mobile, SDK, plugins> | <no: additive / yes: why> |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| <risk> | low/med/high | low/med/high | <mitigation> |

## Suggested sequence

1. <first piece and why>
2. <next piece>

<Pieces that could ship on their own.>

## Rollout switches

<Feature flags or settings available, with citations, or "none found".>

## Existing tests near the change

- `<path/to/test.spec.ts>` - <what it covers>

## Questions for engineering

1. <Question that only someone who read the code could ask> (`<path:line>`)

## Terms used

- **<term>**: <plain-language meaning>
