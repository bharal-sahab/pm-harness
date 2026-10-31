---
id: STORY-<slug>-<nnn>
type: story
title: <Short, user-facing title>
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [PRD-<slug>, EPIC-<slug>-<nn>]
epic: EPIC-<slug>-<nn>
requirements: [R1]
priority: p1
estimate: null
capabilities: [CAP-<slug>]
code_refs: [<path/to/file.ts>]
tracker:
  system: null
  key: null
---

# <Title>

**As a** <user type> **I want** <capability> **so that** <outcome>.

## Acceptance criteria

**AC1: <Happy path name>**
- Given <starting state with concrete values>
- When <the user does something>
- Then <what they observe>

**AC2: <Error or edge case name>**
- Given <state>
- When <action>
- Then <observable result>

## Notes for engineering

- <Where this lands in the code, from tech-impact> `<path:line>`
- <Existing behavior or partial support to reuse>

## Out of scope

- <What this story does not do; link the story that does, if any>

## Dependencies

- <Story IDs or decisions this needs first, or "none">
