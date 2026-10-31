---
name: design-review
description: Reviews designs - from Figma through the Figma MCP server, or from screenshots and exported images - against the design brief, the PRD, the stories, and how the product is built, and writes findings to pm/initiatives/<slug>/design-review.md - missing states and flows, missing error copy, components that duplicate existing ones, data the design shows that the API does not provide, and visible accessibility problems. Use when a PM asks to review, critique, or check designs, mockups, Figma files, or screenshots before handoff to engineering.
license: Apache-2.0
compatibility: Reads Figma through a Figma MCP server when one is connected; otherwise works from images the PM provides.
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Design Review

Check that the design is complete and buildable before engineering starts. This is a
product completeness review, not a taste review: visual style belongs to the designer.

## Non-negotiables

- **Every finding points at something**: a frame or screenshot name, and the requirement,
  state, or code it conflicts with.
- **Feasibility claims are cited.** "The API doesn't return this" needs the file that
  shows what the API returns.
- **Separate must-fix from suggestions.** Use the severity levels below.
- **Only report what is visible.** Images cannot prove contrast ratios or screen reader
  behavior. Flag those as "check in build".
- **Only write inside `pm/`.**

## Getting the designs

- **Figma MCP server** (if connected, for example Figma's remote server at
  `https://mcp.figma.com/mcp` or the desktop app's local server): ask the PM for the file
  or frame link. Use the server's tools to get screenshots, the frame and layer structure, and
  variables or tokens. Tool names vary by version, so use the ones the server lists.
  Read only. Do not edit the file.
- **Images**: screenshots, exported frames, or a PDF the PM provides. Ask for one image
  per screen or state, named so findings can refer to them.

If neither is available, stop and ask. Do not review a design from a description.

## Workflow

```
Design review progress:
- [ ] 1. Gather the yardsticks
- [ ] 2. Inventory the designs
- [ ] 3. Coverage
- [ ] 4. Feasibility against the code
- [ ] 5. Consistency and accessibility
- [ ] 6. Write the review
```

### 1. Gather the yardsticks

Read the initiative's `design.md` (flows, screens, states table, copy needed), `prd.md`
(requirements), and the stories' acceptance criteria. If there is no design brief, build a
quick states checklist from the capability's "Errors users can hit" table in `pm/product/`.

### 2. Inventory the designs

List every frame or image: name, which screen and state it shows, and which flow step.

### 3. Coverage

Map designs to the yardsticks. Report:
- Flow steps and entry points with no design.
- States from the brief's table with no design (the most common gap: errors, empty, and loading).
- Requirements and acceptance criteria the design does not show how to satisfy.
- Error messages with no copy, or copy that does not tell the user what to do next.

### 4. Feasibility against the code

For each piece of data, action, or behavior the design shows, check that the product can
provide it. Look at the API responses, models, and UI code (follow `ask-the-product`).
Typical findings: the design shows a reason the API does not return, a field that does
not exist, a real-time update the backend cannot push, or a limit or rule that differs
from the code. Cite the code for each.

### 5. Consistency and accessibility

- **Consistency**: compare against the components listed in the design brief, or the
  component folder in the code. Flag new components that look like existing ones, and
  patterns that behave differently from the same pattern elsewhere in the product.
- **Accessibility (visible only)**: text that looks too small or low contrast, touch
  targets that look too small, color alone carrying meaning, missing visible labels, and
  error messages that are far from the field. Add a "check in build" list for what images cannot show.

### 6. Write the review

Severity:
- **Blocker**: engineering cannot build it as designed, or a required flow or state is missing.
- **Major**: users will hit a gap or confusing moment; fix before build.
- **Minor**: polish or consistency; fix if cheap.
- **Question**: needs a decision from the PM or designer.

Write `pm/initiatives/<slug>/design-review.md` from
[templates/design-review.md](templates/design-review.md), with `id: DR-<slug>`,
`type: design-review`, and `derived_from: [DES-<slug>]` (or the PRD). If designs are reviewed
again, add a new round section instead of a new file. Update the initiative README, then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```
