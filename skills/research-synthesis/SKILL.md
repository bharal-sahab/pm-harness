---
name: research-synthesis
description: Turns raw research - interview notes and transcripts, support tickets, survey answers, app reviews, sales notes - into evidence-backed themes and insights in pm/initiatives/<slug>/research.md, checks what users report against how the product actually works, and frames the opportunity in a problem brief (brief.md) for design and the PRD. Use when a PM has interview notes, transcripts, tickets, or feedback to make sense of, wants themes, insights, or an affinity map, or needs a problem statement or opportunity brief backed by evidence.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Research Synthesis

Go from a pile of notes to a few insights the team believes, because every one of them
traces back to what real people said or did. Then check those insights against the
product as built: users often describe a bug, a design gap, or a misunderstanding, and the
fix is different for each.

## Non-negotiables

- **Never invent or improve quotes.** Quote exactly, or paraphrase and say so.
- **Every theme and insight cites its sources** (`[P3]`, `[T-4812]`, `[R-12]`), and says
  how many independent sources support it.
- **Anonymize people.** Use participant IDs. No names, emails, or company names unless the
  PM confirms that is allowed.
- **Raw data stays where it is** unless the PM asks to store it in `pm/`. Reference its
  location instead.
- **Only write inside `pm/`.**

## Workflow

```
Synthesis progress:
- [ ] 1. Inventory the sources
- [ ] 2. Extract observations
- [ ] 3. Cluster into themes
- [ ] 4. Write insights
- [ ] 5. Check against the product
- [ ] 6. Checkpoint, then write research.md and brief.md
```

### 1. Inventory the sources

List every source: type, count, dates, segments, and where it lives. Give each item an ID
(`P1` to `Pn` for participants, ticket numbers for tickets, `R1` to `Rn` for reviews).
Read `research-plan.md` if it exists: the hypotheses tell you what to look for, but record
everything, including what contradicts them.

### 2. Extract observations

Go through every source and pull out atomic observations: one fact, behavior, need, or
pain per row, with the source ID and a short exact quote where possible. Prefer what people
**did** over what they **said they would do**. For large sets (more than about 30 sources),
process them in batches and keep a running table.

### 3. Cluster into themes

Group observations that share an underlying need or behavior (affinity mapping). Name each
theme as a user statement ("I can't tell if my code worked"), not a feature ("Code
feedback"). For each theme, record:

- **Frequency**: how many independent sources, out of how many.
- **Intensity**: workarounds, money or time lost, strong emotion, churn.
- **Segments**: who it applies to, and who it does not.

Keep a "Doesn't fit" list. Surprises and contradictions are often the most valuable findings.

### 4. Write insights

An insight explains a theme and says why it matters:

> **We learned that** <who> <behavior or need> **because** <underlying reason>,
> **which means** <implication for the product>.

Rate the evidence: **strong** (3 or more independent sources across more than one
segment, including observed behavior), **moderate** (several sources, one segment or
self-reported only), **weak** (one or two sources). Three to six insights is typical.

### 5. Check against the product

For every insight that involves product behavior, check `pm/product/` (and the code,
following `ask-the-product`) and classify it:

| What is going on | Example | Leads to |
|------------------|---------|----------|
| **Works as built, but users do not understand it** | Codes stack, but users think only one is allowed | Design or copy change |
| **Gap: the product does not do it** | No reason is given when a code fails | New requirement |
| **Bug: the product should do it but does not** | A valid code is rejected | Bug ticket |
| **Unknown** | Code and knowledge base do not settle it | Open question |

Cite the code for each classification. This step is what keeps the team from building
features for problems that are really bugs, or copy problems.

### 6. Checkpoint, then write `research.md` and `brief.md`

Show the PM the themes and insights with their evidence ratings, and wait for confirmation.
Then write:

- `pm/initiatives/<slug>/research.md` from [templates/research.md](templates/research.md):
  `id: RES-<slug>`, `type: research`, `derived_from: [RP-<slug>]` (or `[]`).
- `pm/initiatives/<slug>/brief.md` from [templates/brief.md](templates/brief.md):
  `id: BRIEF-<slug>`, `type: brief`, `derived_from: [RES-<slug>]`. The brief frames the
  problem and opportunity. It does not prescribe the solution.

Update the initiative README, then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Suggest the next step: `design-brief` for changes to flows and screens, or `prd` for small
or non-visual changes.
