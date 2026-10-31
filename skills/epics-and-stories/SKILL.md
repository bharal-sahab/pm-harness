---
name: epics-and-stories
description: Breaks a PRD into epics and small, testable user stories in pm/initiatives/<slug>/, each with Given/When/Then acceptance criteria, error cases from the product knowledge base, code pointers from the tech impact, and a trace back to PRD requirements, then checks that every requirement is covered. Use when a PM wants to write epics, user stories, tickets, or a backlog, split work for sprint planning, or prepare work to push to Jira or Linear.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Epics and Stories

Turn a PRD into a backlog the team can pick up without a meeting to decode it. Stories
are markdown files in `pm/`, which stays the source of truth. `work-sync` pushes them to
a tracker later.

## Non-negotiables

- **Only write inside `pm/`.** Follow `pm/CONVENTIONS.md` for IDs and frontmatter.
- **Every story traces to a requirement** (`requirements: [R1]`) and **every must-have
  requirement has a story.** The trace script checks both.
- **Every story is testable**: numbered acceptance criteria (`AC1`, `AC2`, ...) in
  Given/When/Then form, including at least one unhappy path when the area has errors.
- **Vertical slices.** A story delivers something a user, operator, or API consumer can
  observe. "Build the database table" is a task, not a story.
- **Stop before writing many files.** Show the outline first (rule 8 of the conventions).

## Workflow

```
Backlog progress:
- [ ] 1. Read the inputs
- [ ] 2. Outline epics and stories
- [ ] 3. Checkpoint: confirm the outline
- [ ] 4. Write the files
- [ ] 5. Trace and check
- [ ] 6. Hand off
```

### 1. Read the inputs

- `prd.md`: the requirement IDs, priorities, edge cases, non-goals, and rollout.
- `tech-impact.md` if it exists: surfaces, files, sequence, risks, existing tests. This is
  where `code_refs` and the "Notes for engineering" come from.
- `design.md` if it exists: screens and states. Each state often becomes a criterion.
- The capability's "Errors users can hit" in `pm/product/capabilities.md`: these become
  unhappy-path criteria.

Without a PRD, ask the PM for the requirements in a few bullets and number them yourself.
Recommend writing the PRD first for anything larger than a few stories.

### 2. Outline epics and stories

- **Epics** group stories by user outcome, not by technical layer. Most initiatives need
  one to four. An epic that maps to one requirement is fine.
- **Stories** follow INVEST: independent, negotiable, valuable, estimable, small (a few
  days of work at most), testable. Use the splitting patterns in
  [references/splitting.md](references/splitting.md) when a story is too big.
- Order stories by the tech-impact sequence, so the first ones unblock the rest.
- Respect non-goals. Do not create stories for them.
- Add a **spike** (a time-boxed investigation) only for a real unknown from tech-impact's
  questions for engineering, and say what decision it unblocks.

### 3. Checkpoint: confirm the outline

Show a compact outline and wait for confirmation:

```
EPIC-<slug>-01 <title> (R1, R2)
  STORY-<slug>-001 <title> [p1] R1
  STORY-<slug>-002 <title> [p2] R2
EPIC-<slug>-02 ...
Not covered: <requirements left out on purpose, with reason>
```

### 4. Write the files

- Epics: `pm/initiatives/<slug>/epics/EPIC-<slug>-<nn>.md` from [templates/epic.md](templates/epic.md).
- Stories: `pm/initiatives/<slug>/stories/STORY-<slug>-<nnn>.md` from [templates/story.md](templates/story.md).

Writing good acceptance criteria:
- One behavior per criterion. Name it: `**AC2: Expired code**`.
- Concrete values beat adjectives: "a code that expired yesterday", not "an invalid code".
- Write what the user observes, not how the code does it.
- Cover the happy path, each relevant error from the knowledge base, and permissions
  (who must *not* be able to do it).
- If a criterion depends on copy or design not decided yet, link the open question.

`derived_from` for a story is `[PRD-<slug>, EPIC-<slug>-<nn>]` (add `TI-<slug>` if used).
Set `tracker: {system: null, key: null}`; `work-sync` fills it in. Leave `estimate: null`
for the team.

Keep IDs stable. When updating an existing backlog, add new numbers instead of
renumbering, and mark dropped stories `status: superseded` instead of deleting them.

### 5. Trace and check

```bash
python3 <this-skill-dir>/scripts/trace.py pm/initiatives/<slug>
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Fix every error. Warnings about should- or could-have requirements without stories are
fine if the PM agreed to defer them; note that in the PRD's open questions or the README.

Add the epics and a stories summary row to the initiative README.

### 6. Hand off

Tell the PM: the number of epics and stories, the trace result, the first story to start
with and why, and the next steps: `work-sync` to push to the tracker, and `test-plan`.
