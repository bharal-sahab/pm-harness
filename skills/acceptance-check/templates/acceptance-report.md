---
id: AC-<slug>-<label>
type: acceptance-report
title: <Initiative title> - Acceptance check for <PR or branch>
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [STORY-<slug>-<nnn>]
code_refs: [<changed files>]
---

# Acceptance check: <PR title or branch>

**Recommendation:** <Ready to accept | Accept with follow-ups | Not ready>. <One or two reasons.>
**Diff:** <PR link or base...head>, <n> files, +<a>/-<r> lines.
**Stories checked:** <STORY IDs>

## Acceptance criteria

| Criterion | Verdict | Evidence | Note |
|-----------|---------|----------|------|
| STORY-<slug>-001/AC1 | Done and tested | `<path:line>`, `<test path:line>` | |
| STORY-<slug>-001/AC2 | Done, not tested | `<path:line>` | <what test is missing> |

## Unplanned changes

- `<path>`: <why it changed, and whether it is fine>

## Risks

- <API, data, or flag concerns, or "None found">

## Check by hand

1. <Manual check, with data and the expected result>

## Follow-ups

- <Missing tests or criteria to track, with the story they belong to>
