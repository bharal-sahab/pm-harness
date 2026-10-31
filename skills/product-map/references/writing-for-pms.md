# Writing for PMs

The reader is a smart product manager on their first week with this product. They are
comfortable with ambiguity and business trade-offs, less so with code. Every page should
let them answer "what does the product do, for whom, and what happens when X" without
asking an engineer.

## Voice

- Lead with the user-visible behavior, then the mechanism, then the citation.
  Good: "A shopper can check out without an account; the order stores their email instead
  of a customer record `packages/.../complete-cart.ts`."
  Bad: "`completeCartWorkflow` invokes `createOrdersStep` with `customer_id` nullable."
- Use the product's business words, and give the code name in backticks once so the PM can
  recognize it in tickets and conversations.
- Prefer tables for rules, states, and failure cases; prose for explanations.
- No filler: no "In this document we will", no "Let's dive in", no closing summaries.

## Translate engineering concepts

| Engineers say | Write |
|---------------|-------|
| endpoint / route | "the API call the app makes to ..." (then the path in backticks) |
| workflow / saga / orchestration | "the step-by-step process that ..., which undoes earlier steps if a later one fails" |
| compensation / rollback | "undo step" |
| enum / status field | "the states a <thing> can be in" |
| event / subscriber / webhook | "a signal the system sends when ... so other parts can react" |
| feature flag | "an on/off switch that ..." |
| module / service | "the part of the system responsible for ..." |
| migration | "a change to how data is stored" |
| idempotency / locking | "protection against the same action running twice at once" |
| provider / adapter | "a plug-in that connects to <third party>" |
| middleware | "a check that runs before every request, e.g. ..." |
| cache | "a fast copy of data that can be briefly out of date" |

## Citations

- Format: backticked repo-relative path, optional line: `path/to/file.ts` or `path/to/file.ts:120`.
- Put the citation at the end of the sentence or in the table's Code column.
- Cite the file that proves the claim (the rule, the enum, the validation), not just the folder.
- Never paste more than one line of code. Paraphrase, then cite.

## Confidence

| Level | Meaning | What to do |
|-------|---------|------------|
| High | You read the code path end to end | State it plainly |
| Medium | You read part of it or inferred from names and types | State it, mark "(likely)" |
| Low | Inferred from structure only | Avoid stating it; add an open question instead |

## Diagrams

- Overview: `mindmap` of capability areas.
- Journeys: `sequenceDiagram` for multi-party flows, `flowchart` for branching rules.
- Data: `erDiagram` with the 8 to 15 entities that matter; skip join tables.
- Status lifecycles: `stateDiagram-v2`.
- No styling or colors; node IDs without spaces.
