---
name: ai-evals
description: Guides a PM through evaluating an AI or LLM feature the way strong AI teams do - reading real outputs, labeling pass or fail, turning notes into a failure taxonomy, choosing code checks or LLM judges per failure, validating judges against human labels, and setting launch thresholds - and records it all in pm/initiatives/<slug>/evals/. Use when a PM is building, launching, or improving an AI feature (chatbot, agent, summarizer, RAG, recommendations), asks how to evaluate or test an LLM feature, wants quality metrics or launch criteria for AI, or sees AI quality complaints.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# AI Evals

Help the PM own the most important question about an AI feature: **is it good enough
for our users, and how will we know if it gets worse?** The method follows the error
analysis approach taught by Hamel Husain and Shreya Shankar: look at real outputs first,
write tests second.

The PM's job is judgment: deciding what "good" means and labeling outputs. The agent's
job is to make that fast, organize it, and do the math. For deep engineering work (review
apps, synthetic data pipelines, RAG metrics), install the
[evals plugin](https://github.com/ai-evals-course/evals-skills)
(`npx skills add https://github.com/ai-evals-course/evals-skills`) and hand off to it.

## Non-negotiables

- **The PM labels; the agent proposes.** Never mark an output pass or fail on the PM's
  behalf without their review. Agent suggestions are clearly marked as suggestions.
- **Binary verdicts.** Pass or fail, never 1-5 scores. Scores hide disagreement.
- **Look before you measure.** No metrics or judges before reading at least 50 real
  outputs (100 is better).
- **One judge, one failure mode.** A judge that checks "quality" checks nothing.
- **Only write inside `pm/`.** Traces may contain personal data: store only IDs and short
  excerpts unless the PM confirms the data may be kept in the repo.

## Workflow

```
AI evals progress:
- [ ] 1. Frame what good means
- [ ] 2. Gather outputs
- [ ] 3. Read and label (error analysis)
- [ ] 4. Build the failure taxonomy
- [ ] 5. Decide how to catch each failure
- [ ] 6. Write and validate judges
- [ ] 7. Set launch and monitoring thresholds
```

### 1. Frame what good means

Work in `pm/initiatives/<slug>/evals/`. From the PRD (or the PM), write down:

- What the feature does, for whom, and the user's goal in one sentence.
- What a great output looks like, and what would make a user stop trusting it.
- Risk level: what is the worst plausible output (wrong money amount, harmful advice,
  leaked data)? High-risk failures get zero tolerance.
- Where outputs come from: production logs, a staging log, or nothing yet.

### 2. Gather outputs

- **Existing feature**: ask engineering for 100 recent traces (input, output, and any tool
  calls or retrieved documents) as JSONL or CSV, sampled across days and user types.
- **Not launched yet**: build test inputs from dimensions. Pick 3 or 4 dimensions that
  change behavior (user type, intent, difficulty, language), list 3 to 5 values each,
  combine them into 50 to 100 realistic inputs, and have engineering run them through the
  feature. Hand off to the evals plugin's synthetic data skill for larger sets.

Save a `labels.csv` with columns `id, pass, failure_mode, note` (one row per trace). Keep
traces in their own file, referenced by ID.

### 3. Read and label (error analysis)

Show the PM traces in batches of 10. For each one, the PM decides **pass or fail** and, for
failures, writes a short note about **the first thing that went wrong** (errors cascade;
fix the first one). Notes describe what happened, not why: "Quoted a refund window of 60
days; policy is 30", not "model hallucinated".

You may suggest a verdict and a note for each trace to speed things up; the PM confirms or
changes it. Stop when new traces stop showing new kinds of failure (often 50 to 100).

### 4. Build the failure taxonomy

Group the notes into 4 to 8 failure modes. Each mode gets a name, a one-line definition,
a pass example, and a fail example. Then fill `failure_mode` for every failure in
`labels.csv` and count:

```bash
python3 <this-skill-dir>/scripts/eval_stats.py failures evals/labels.csv
```

Write `evals/failure-taxonomy.md` from [templates/failure-taxonomy.md](templates/failure-taxonomy.md).
Frontmatter: `id: EVAL-<slug>-taxonomy`, `type: eval`, `derived_from: [PRD-<slug>]`.

### 5. Decide how to catch each failure

For each mode, in this order of preference:

| Option | When | Example |
|--------|------|---------|
| **Fix it now** | The cause is obvious: a prompt gap, missing data, a product bug | Add the refund policy to the prompt; write a story with `epics-and-stories` |
| **Code check** | The failure is objective: format, length, a required field, a forbidden phrase, a wrong tool call | A regex that rejects amounts not found in the source |
| **LLM judge** | The failure needs interpretation: tone, faithfulness, relevance | "Does the answer claim something the source does not say?" |

Most teams over-use judges. Push for fixes and code checks first.

### 6. Write and validate judges

For each failure mode that needs a judge, write `evals/judges/<mode>.md` from
[templates/judge-prompt.md](templates/judge-prompt.md): the task, precise pass and fail
definitions from the taxonomy, two to four examples (including a borderline one), and an
output that gives the critique before the verdict.

Then validate it against the PM's labels:

```bash
python3 <this-skill-dir>/scripts/eval_stats.py split evals/labels.csv --out-dir evals/splits
# examples come from train; run the judge on dev, add its verdicts as a `judge` column
python3 <this-skill-dir>/scripts/eval_stats.py judge evals/splits/dev.csv
```

Improve the judge on dev until both the true positive rate and the true negative rate are
at least 0.9 (or the bar the PM sets). Then run it once on test and record those numbers.
Never use test traces as examples. When the judge later runs on new traces, use
`--unlabeled` to get the pass rate corrected for the judge's own errors.

### 7. Set launch and monitoring thresholds

Write `evals/README.md` (the eval plan) from [templates/eval-plan.md](templates/eval-plan.md),
with `id: EVAL-<slug>`, `type: eval`:

- The evaluators (code checks and validated judges) and where they run (CI, nightly).
- **Launch thresholds** per failure mode, agreed with the PM: zero tolerance for high-risk
  modes, a maximum rate for the others.
- **Monitoring**: how many production traces the team reads each week (start with 20 to
  50), who reads them, and when to repeat error analysis (after model, prompt, or data changes).

Update the initiative README, then check:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Hand off: the top failure modes and their rates, what is fixed versus measured, whether the
launch thresholds are met, and the next step (stories for the fixes, or `release-notes`).
