---
name: research-plan
description: Plans user research for an initiative in pm/initiatives/<slug>/research-plan.md - the decision it informs, what is already known from the product knowledge base and data, the riskiest assumptions, the method, who to recruit, and an interview guide that asks about past behavior instead of opinions (Mom Test style). Use when a PM wants to plan interviews, a usability test, a survey, or discovery research, validate a problem or idea, or write an interview guide or screener.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Research Plan

Plan research that changes a decision. Most research fails because it asks users to
predict their own behavior ("Would you use...?"), or because it studies things the team
could have learned from its own product and data.

## Non-negotiables

- **Start from the decision.** If no answer would change what the team does, do not run
  the research.
- **Do not research what the product can tell you.** Check `pm/product/` and the code
  (via `ask-the-product`) for how things work today, and analytics for what users do.
- **Ask about the past, not the future.** No "would you", "do you like", or pitching the
  idea during discovery interviews. See [references/interview-questions.md](references/interview-questions.md).
- **Only write inside `pm/`.**

## Workflow

```
Research plan progress:
- [ ] 1. Frame the decision
- [ ] 2. Collect what is already known
- [ ] 3. Rank the assumptions
- [ ] 4. Choose the method
- [ ] 5. Participants and recruiting
- [ ] 6. Write the guide
- [ ] 7. Checkpoint and save
```

### 1. Frame the decision

In the initiative folder (create it and its README per `pm/CONVENTIONS.md` if needed),
write down with the PM: the decision this research informs, who decides, and by when.
Example: "Decide whether to build promo-code feedback this quarter, or fix
checkout errors first."

### 2. Collect what is already known

- **The product today**: the related capabilities, journeys, FAQ, and open questions in
  `pm/product/`. Note behaviors users may be reacting to (for example, a code that
  silently does not apply), with citations.
- **Data the team already has**: analytics, support tickets, reviews, sales notes. List
  what to pull, and ask the PM for access. These often answer "how many" faster than
  interviews.
- **Earlier research**: other initiatives' `research.md` files on the same capabilities.

### 3. Rank the assumptions

List the assumptions behind the initiative in four groups: the problem exists
(desirability), people will use the solution (usability), it works for the business
(viability), it can be built (feasibility; often answered by `tech-impact`). Score each one
for **risk if wrong** and **current evidence**. Research the high-risk, low-evidence ones
first. Write each as a testable hypothesis with what would prove it wrong.

### 4. Choose the method

| Question type | Method | Typical size |
|---------------|--------|--------------|
| Does the problem exist? How do people deal with it today? | Discovery interviews | 5-8 per segment |
| Can people use this design? | Usability test (moderated) | 5 per round |
| How many people have it? | Data analysis, or a survey | Depends on population |
| What do people say in their own words? | Support ticket or review analysis | 50-200 items |
| How does behavior unfold over time? | Diary study | 8-15 people, 1-2 weeks |

Combine a qualitative method (why) with a quantitative one (how many) when the decision is big.

### 5. Participants and recruiting

Define who qualifies (behavior, not demographics: "applied a promo code in the last
month"), who to exclude (employees, friends of the team), segments and how many of each,
and how to find them. Write screener questions that do not reveal the right answer.

### 6. Write the guide

For interviews, follow the structure in [templates/research-plan.md](templates/research-plan.md):
warm-up, the story of the last time it happened, probes, the current workaround, and
wrap-up. Use the good and bad question pairs in the reference. For usability tests, write
tasks as goals ("You want 10% off with the code from your email"), not instructions
("Click the promo field").

### 7. Checkpoint and save

Show the PM the decision, the top three hypotheses, the method, and the guide, and wait
for confirmation. Write `pm/initiatives/<slug>/research-plan.md` from the template, with
`id: RP-<slug>`, `type: research-plan`, `derived_from` (the PRD or brief if any, otherwise
`[]`), and `capabilities`. Update the initiative README.

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

After the sessions, suggest `research-synthesis` to turn the notes into insights.
