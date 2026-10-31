---
name: prd
description: Writes a lean, testable PRD for an initiative in pm/initiatives/<slug>/prd.md, pulling the problem and evidence from the research brief and design, and the current product behavior (with code citations) from the pm/product knowledge base, so requirements start from how the product really works today. Use when a PM wants to write a PRD, spec, one-pager, or requirements doc, turn a brief or idea into requirements, or define a change before engineering sizes it.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# PRD

Write a short PRD that engineering and design can build from and QA can test against.
What makes it different from a blank template: the **current behavior** section comes
from the code, so the team argues about the change, not about how things work today.

## Non-negotiables

- **Only write inside `pm/`.** Follow `pm/CONVENTIONS.md` (frontmatter, IDs, links).
- **Cite current behavior.** Every statement about how the product works today carries a
  code citation, copied from `pm/product/` or verified in the code.
- **Requirements say what, not how.** Describe the behavior users get. Leave the
  implementation to `tech-impact` and engineering.
- **Every requirement is testable**, and has an ID (`R1`, `R2`, ...) that stories and
  tests trace back to. IDs never get reused.
- **Unknown beats invented.** Missing numbers, baselines, or decisions go in "Open
  questions" with an owner, never as made-up values.

## Workflow

```
PRD progress:
- [ ] 1. Find or start the initiative
- [ ] 2. Gather context
- [ ] 3. Fill gaps with the PM
- [ ] 4. Draft
- [ ] 5. Self-review
- [ ] 6. Checkpoint and save
```

### 1. Find or start the initiative

Work in `pm/initiatives/<slug>/`. If it does not exist, agree on a short slug with the
PM and create the folder with a `README.md` as described in the "Initiative README"
section of `pm/CONVENTIONS.md`. If `prd.md` already exists, update it instead of writing
a new one, and keep existing requirement IDs.

### 2. Gather context

Read, in this order, whatever exists:

1. Upstream artifacts in the initiative: `brief.md`, `research.md`, `competitive-scan.md`,
   `design.md`, `design-review.md`. Link to them; do not copy them.
2. The product knowledge base: the related capabilities in `pm/product/capabilities.md`
   (including "Errors users can hit"), the journeys they appear in, `faq.md`, and
   `open-questions.md`.
3. If `pm/product/` does not exist, say so. Offer `product-map`, or verify the few facts
   you need directly in the code, following the rules of `ask-the-product`.

From this, write down the **current behavior**: what users can do today, the rules, and
what goes wrong, each with a citation. This is often where the PM learns the most.

### 3. Fill gaps with the PM

Ask only what the artifacts do not answer, in one round of at most five questions. Usual
gaps: who exactly the user is, the outcome metric and its target, what is out of scope,
deadlines or constraints, and who decides. Offer a sensible default for each question.
If the PM wants to move fast, proceed with the defaults and list them as assumptions.

### 4. Draft

Write `pm/initiatives/<slug>/prd.md` from [templates/prd.md](templates/prd.md).

- **Problem**: who has it, how often, and the evidence (link `RES-`/`BRIEF-` IDs, data,
  tickets). Without evidence, say so and mark the problem as a hypothesis.
- **Goals and metrics**: one primary metric with a baseline, a target, and where it is
  measured. Add guardrail metrics for what must not get worse.
- **Requirements**: numbered `R1`, `R2`, ... with priority (must, should, could). Write
  each one as observable behavior: "When a code cannot be applied, the shopper sees why",
  not "Add a reason field to the API". Link each to the capability it changes.
- **Edge cases and errors**: start from the capability's "Errors users can hit" table
  and the journey's "What can go wrong". Say what should happen in each case.
- **Rollout**: check the capability's "Switches" and `integrations.md` for feature flags
  or settings you can use for a gradual or reversible launch.
- **Non-goals**: as important as goals. Name the tempting adjacent work you are not doing.

Frontmatter: `id: PRD-<slug>`, `type: prd`, `initiative: <slug>`, `derived_from` with the
IDs of the artifacts you used, `capabilities`, and `code_refs` for the files cited in
"Current behavior".

### 5. Self-review

Check the draft against this list, and fix what fails:

- [ ] A new engineer could explain the problem after reading only the first section.
- [ ] Current behavior is cited, and matches the knowledge base or the code.
- [ ] Every requirement is testable and traces to the problem or a goal.
- [ ] No requirement prescribes an implementation unless it is a real constraint.
- [ ] Every error case from the capability is covered or explicitly out of scope.
- [ ] The metric has a baseline (or an open question to get one) and a target.
- [ ] Non-goals exist.
- [ ] Technical terms are explained in plain language the first time.

### 6. Checkpoint and save

Show the PM: the one-paragraph summary, the requirement list, the assumptions you made,
and the open questions. Set `status: draft`, or `in-review` once the PM says it is ready
for the team. Update the initiative README row.

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Suggest the next step: `tech-impact` to see what it touches in the code, or
`design-brief` if the flows are not designed yet.
