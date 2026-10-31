---
name: test-plan
description: Writes a test plan for an initiative in pm/initiatives/<slug>/test-plan.md, turning every story acceptance criterion into test cases and adding the edge cases, error states, permission checks, and regression areas the code reveals, then checks that every criterion is covered. Use when a PM or QA wants a test plan, test cases, QA scenarios, a regression checklist, or UAT script for a feature before or during development.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Test Plan

Give QA, engineers, and the PM one shared list of what must be true before the work
ships. Acceptance criteria say what the PM asked for; the code says what else can break.
This skill uses both.

## Non-negotiables

- **Only write inside `pm/`.** Do not write test code; engineers own automated tests.
- **Every acceptance criterion has at least one test case**, referenced as
  `STORY-<slug>-<nnn>/AC<n>`. The coverage script checks this.
- **Cite where extra cases come from**: a code path, an error in the knowledge base, or a
  risk in the tech impact.
- **Concrete data.** "A code that expired yesterday", not "an invalid code".

## Workflow

```
Test plan progress:
- [ ] 1. Read the inputs
- [ ] 2. Cases from acceptance criteria
- [ ] 3. Cases the code reveals
- [ ] 4. Regression and non-functional checks
- [ ] 5. Write and check coverage
```

### 1. Read the inputs

- `stories/*.md`: every acceptance criterion (skip superseded stories).
- `prd.md`: edge cases, non-goals (to mark out of scope), rollout and feature flags.
- `tech-impact.md`: risks, consumers, and existing tests near the change.
- `pm/product/`: the capability's "Errors users can hit" and the journeys' "What can go
  wrong" for the affected capabilities.
- `design.md`: screens and states (empty, loading, error, success).

### 2. Cases from acceptance criteria

Write at least one case per criterion. A criterion with several "Then" lines may need
more than one case. Each case: ID (`TC-01`), the criteria it covers, the level, the
preconditions and data, the steps, and the expected result.

Pick the cheapest level that proves the behavior:

| Level | Use for |
|-------|---------|
| Unit | One rule or calculation |
| Integration / API | Behavior through an API, with a real database |
| End to end | A full user journey across screens |
| Manual | Visual checks, copy, exploratory testing, anything not worth automating |

### 3. Cases the code reveals

Add the cases a PM would not think of. Look for:

- **Errors** in the affected capabilities that the stories do not mention.
- **Boundaries**: limits, minimums, maximums, empty lists, exactly at a threshold.
- **Permissions**: who must *not* be able to do this (logged out, another customer,
  a role without access). Check the auth code for the touched routes.
- **State**: what happens when the same action runs twice, out of order, or in two tabs.
- **Data variety**: currencies, languages, time zones, very long text, special characters.
- **Feature flag**: behavior with the flag on, and that nothing changes with it off.
- **Old clients**: if an API changes, a client that ignores the new fields still works.

Tag these cases `derived` and cite their source.

### 4. Regression and non-functional checks

- **Regression areas**: the journeys in `pm/product/journeys/` that pass through the
  touched capabilities, and the consumers listed in the tech impact. List what to re-check,
  and point to existing test files from the tech impact.
- **Non-functional**: only the ones that matter here, from the PRD's guardrail metrics
  and the tech impact's risks (performance on a hot path, security, accessibility, and so on).
- **Exploratory charters**: two or three time-boxed missions for a human tester, for
  example "Explore applying and removing codes while editing the cart, looking for
  totals that do not match".

### 5. Write and check coverage

Write `pm/initiatives/<slug>/test-plan.md` from [templates/test-plan.md](templates/test-plan.md).
Frontmatter: `id: TP-<slug>`, `type: test-plan`, `derived_from` with the PRD, the tech
impact, and the epics.

```bash
python3 <this-skill-dir>/scripts/ac_coverage.py pm/initiatives/<slug>
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Fix every error. Update the initiative README row. Tell the PM the number of cases, how
many come from the code rather than the stories, and the top regression risk. Suggest
`acceptance-check` once there is a pull request.
