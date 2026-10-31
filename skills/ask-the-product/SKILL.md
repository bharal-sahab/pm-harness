---
name: ask-the-product
description: Answers product questions such as "how does X work", "what happens if Y", "who can do Z", or "why does this happen" in plain language, grounded in the pm/product knowledge base and verified against the code, then saves what it learned back to the knowledge base. Use when a PM asks how the product behaves, needs a fact for a PRD, ticket, or stakeholder, or wants to check an assumption before a meeting.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Ask the Product

Answer a PM's question about how the product behaves today. Answer the way a senior
engineer would explain it to a smart non-engineer: short, concrete, and with proof.
Every answer makes the knowledge base a little better for the next person.

## Non-negotiables

- **Read-only on product code.** Only write inside `pm/`.
- **Cite every fact** with a backticked, repo-relative path, adding `:line` when one line
  proves it. Copy citations from the knowledge base when they are there.
- **Unknown beats wrong.** If neither the knowledge base nor the code settles it, say so
  and record an open question.
- **Respect `exclude_paths`** in `pm/config.yaml`. Never open, quote, or describe them.
- **Answer only the question.** Do not propose features or solutions unless asked.

## Before you start

If `pm/product/` does not exist, explain that it is needed and offer to run `product-map`
first. For a quick one-off answer, you may skip it and go straight to the code (step 3),
but tell the PM that the answer will not be saved.

## Workflow

### 1. Understand the question

Restate the question in one line. If it is ambiguous, pick the most likely meaning and
say which one you picked. Classify it to know where to look first:

| Question shape | Look first in | Then in the code |
|----------------|---------------|------------------|
| "What happens if..." (failure, edge case) | Capability "Errors users can hit", journey "What can go wrong" | Thrown errors and validators along the path |
| "How does X work?" | The journey for X, then its capability | Entry point, then the workflow or service it calls |
| "Who can...?" / "Can a [role]...?" | Capability "Who uses it", `how-it-is-built.md` | Auth middleware, permission checks, route guards |
| "Is it possible to...?" / "Can we configure...?" | Capability "Switches", `integrations.md` | Config files, feature flags, settings models |
| "When does X happen?" / "What triggers X?" | Journey diagrams, `integrations.md` | Events, subscribers, jobs, webhooks |
| "How many / how long / what limit?" | Capability "Rules and limits" | Validators, constants, schema constraints |
| "What is a [term]?" | `domain-glossary.md` | Data model or enum that defines it |

### 2. Check the knowledge base

1. Search `pm/product/faq.md` first. If the question was already answered and its
   citations still exist, reuse the answer (still do the freshness check below).
2. Search the other `pm/product/` pages for the key terms and their glossary synonyms.
3. **Freshness check.** Compare `source_commit` in `pm/product/_meta.yaml` with the current
   commit (`git rev-parse HEAD`). If they differ, run
   `git diff --name-only <source_commit> HEAD -- <files you plan to cite>`. If any of them
   changed, verify that part in the code (step 3) instead of trusting the page.

If the knowledge base fully answers the question and is fresh, go to step 4.

### 3. Verify or fill gaps in the code

Use the citations in the knowledge base as entry points. Trace from the outside in:
entry point, then the logic it calls, then the errors and side effects. Stop as soon as
the question is settled. Breadth matters less than proof.

Rate the answer:
- **High**: you read the code path that decides the behavior.
- **Medium**: you read part of the path, or inferred from names, types, or docs.
- **Low**: an educated guess from structure. Say so plainly and add an open question.

Absence is hard to prove. "There is no setting for X" needs a search, and you must say what
you searched (for example, "no `exclusive` or `stackable` field in the promotion module").

### 4. Answer

Use this shape. Keep it under about 200 words unless the PM asks for more.

```markdown
**Short answer:** <one to three sentences a PM could repeat in a meeting>

**Details**
- <fact> `<path/to/file.ts:42>`
- <fact> `<path/to/other.ts>`

**Confidence:** High | Medium | Low - <why, in one clause>
**Worth asking engineering:** <only if something is uncertain or surprising>
```

Explain any technical term in passing (e.g. "a *workflow*, a series of steps that undo
themselves if one fails"). If the PM asks "show me", add the code path as a numbered list
of files in the order they run.

### 5. Save what you learned

The knowledge base should never have to rediscover the same fact.

- **Always**: add the question and answer to `pm/product/faq.md` (create it from
  [templates/faq.md](templates/faq.md) if missing). Use the FAQ entry format there. Skip
  this only if the answer came straight from an existing page with no new facts; in that
  case, link the page in your reply instead.
- **If you found a durable fact that belongs on a page** (a rule, an error, a state, a
  permission), show the PM the exact line you would add and where, then add it once they
  confirm. Keep capability IDs unchanged.
- **If a page was wrong or stale**, fix the sentence and its citation after confirming
  with the PM, and mention it in the FAQ entry.
- **If the answer resolves an item in `open-questions.md`**, mark it answered there and
  link the FAQ entry.
- **If you could not answer**, add the question to `open-questions.md` with what you
  checked and who might know.

Update `updated:` in the frontmatter of every page you change. Then check your work:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

## Follow-ups

When the answer shows a gap or a problem the PM may want to act on, mention the next
skill in one line: `prd` to define a change, `research-plan` to check if users care, or
`tech-impact` to size it.
