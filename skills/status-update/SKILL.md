---
name: status-update
description: Writes an honest status update for an initiative (or for all initiatives) from what is actually in pm/ - stage, stories done and in progress (including tracker statuses), what changed since the last update, risks, open questions, decisions made and needed, and asks - saved to pm/initiatives/<slug>/status/<yyyy-mm-dd>.md and tailored for executives, the team, or stakeholders. Use when a PM needs a weekly update, status report, stakeholder update, steering-committee summary, or a quick read on where things stand.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Status Update

Write the update from the artifacts and the tracker, not from memory, so it is quick to
produce and hard to spin. The PM adds what files cannot show (morale, politics, context) and
owns the status color.

## Non-negotiables

- **Every progress claim traces to an artifact or a tracker status.** If something is
  "almost done" but the story says `in-progress` and acceptance says "Not ready", the update
  says that.
- **The status color has a reason.** Use the definitions below. The agent proposes and the
  PM decides.
- **Lead with what the reader must know or do.** Asks and decisions needed go at the top.
- **Only write inside `pm/`.**

## Workflow

```
Status update progress:
- [ ] 1. Audience and scope
- [ ] 2. Collect the facts
- [ ] 3. Propose the status
- [ ] 4. Draft
- [ ] 5. Checkpoint and save
```

### 1. Audience and scope

Ask, if not given: one initiative or all of them, and who will read it:
- **Executive**: five lines or fewer. Status, the one thing that matters, asks.
- **Team**: full detail on stories, blockers, and next steps.
- **Stakeholders** (support, sales, partner teams): what is coming, when, and what it
  means for them.

### 2. Collect the facts

For one initiative:

```bash
python3 <this-skill-dir>/scripts/initiative_facts.py pm/initiatives/<slug>
```

It lists artifacts changed since the previous update, stories by status with tracker
keys and statuses, unanswered open questions, acceptance-check recommendations, and README
decisions. If a tracker is connected, refresh statuses first with `work-sync` (pull only),
because tracker statuses are only as fresh as the last sync.

For all initiatives (a portfolio update):

```bash
python3 <this-skill-dir>/scripts/pm_status.py pm --repo . --json
```

Then ask the PM what the files cannot know: dates promised to anyone, staffing changes,
dependencies on other teams, and anything said in meetings.

### 3. Propose the status

| Status | Meaning |
|--------|---------|
| **On track** | The next milestone will be met with the current plan. No help needed. |
| **At risk** | A known problem could miss the next milestone. There is a plan; it may need help. |
| **Off track** | The milestone will be missed without a change in scope, date, or people. A decision is needed. |

Propose one with a one-sentence reason grounded in the facts (for example: "At risk:
acceptance check found the tests cannot run, and Q4 on case sensitivity blocks story 002").
The PM confirms or changes it.

### 4. Draft

Use [templates/status-update.md](templates/status-update.md). Keep progress in terms
people outside the team understand: "Shoppers will see why a code failed (2 of 3 steps
built)" rather than a list of story IDs. Put IDs in links for those who want detail.
Compare with the previous update: say what moved, and call out anything that has been
"next" twice.

### 5. Checkpoint and save

Show the draft. After the PM confirms, save it to
`pm/initiatives/<slug>/status/<yyyy-mm-dd>.md` with
`id: SU-<slug>-<yyyy-mm-dd>`, `type: status-update`, and `derived_from` (the artifact IDs
the facts came from). Portfolio updates go in an initiative named `portfolio`. Then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

The PM sends it through their usual channel. Do not post to Slack, email, or the tracker
unless asked and connected.
