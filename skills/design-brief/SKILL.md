---
name: design-brief
description: Writes a design brief in pm/initiatives/<slug>/design.md that gives designers the full picture before they open Figma - the current flow from the product's journeys, the proposed flow, every affected screen with the UI code that renders it today, every state each screen needs (empty, loading, error, success, permission, offline), the copy needed for each error, reusable components, and accessibility needs. Use when a PM is handing work to design, asks for a design brief, user flow, screen list, or states list, or wants to know which screens a change touches.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Design Brief

Designers usually get the happy path and a deadline. They then discover the error states,
the second entry point, and the existing component library halfway through. A brief built
from the code gives them those on day one.

## Non-negotiables

- **The current flow comes from the product as built**: the journeys in
  `pm/product/journeys/` and the UI code, cited. Not from memory.
- **List states, not just screens.** Every screen gets its empty, loading, error, and
  success states considered. Error states come from the capability's
  "Errors users can hit" table.
- **Describe the problem and constraints, not the pixels.** The brief says what the design
  must achieve and what it must handle. The designer decides how.
- **Only write inside `pm/`.**

## Inputs

Read, if they exist: the initiative's `brief.md`, `prd.md`, and `research.md`; the related
capabilities and journeys in `pm/product/`; and `pm/product/how-it-is-built.md` for where the UI code
lives (web app, mobile app, admin dashboard, shared component library).

## Workflow

```
Design brief progress:
- [ ] 1. The change in one paragraph
- [ ] 2. Current flow
- [ ] 3. Proposed flow
- [ ] 4. Screens affected
- [ ] 5. States per screen
- [ ] 6. Copy, components, accessibility
- [ ] 7. Checkpoint and write
```

### 1. The change in one paragraph

Who it is for, what they are trying to do, what goes wrong today, and what success looks
like (the metric from the brief or PRD).

### 2. Current flow

Take the steps from the relevant journey and draw them as a Mermaid flowchart. For each
step, cite where the UI lives: the route, page, or screen file. If the repository has
no UI (an API product, or the storefront lives in another repo), say so, and describe what
API responses the client UI has to work with.

### 3. Proposed flow

Draw the new flow and mark what changed. Cover every entry point: a feature reached from
a deep link, email, notification, or second screen needs the same handling.

### 4. Screens affected

For each screen or surface (including email, push notifications, admin views, and
customer-support tools): what exists today (cited), what changes, and whether it is a new
screen, a changed screen, or unchanged but affected (for example, it shows data the change touches).

### 5. States per screen

Use the checklist in [templates/design.md](templates/design.md): default, empty, loading,
partial data, every error from the capability's error table plus network failure,
success and confirmation, permission denied, disabled feature (flag off), long and unusual
content (long names, large numbers, other currencies and languages, right-to-left
scripts), and, for mobile, offline and interrupted sessions. Mark the ones that do not apply
as "n/a" so the designer knows they were considered.

### 6. Copy, components, accessibility

- **Copy needed**: one row per message, with what triggers it and what the user should do
  next. Note where the message comes from today (server or client) and its current wording, cited.
- **Components to reuse**: search the UI code for a design system or component folder
  (for example `components/`, `ui/`, `design-system/`, or a package such as
  `@<org>/ui`). List the components that already do part of the job, so the design does
  not invent new ones.
- **Accessibility**: keyboard path, screen reader labels and announcements (especially for
  errors that appear without a page change), contrast, touch target size, and focus after
  an error.

### 7. Checkpoint and write

Show the PM the flows, the screen list, and the state count, and confirm. Write
`pm/initiatives/<slug>/design.md` with `id: DES-<slug>`, `type: design`, `derived_from`
(the brief, PRD, or both), `capabilities`, and `code_refs` (the UI files). End with open
design questions and the list of frames the PM expects back. Update the initiative README, then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

When designs exist, suggest `design-review`.
