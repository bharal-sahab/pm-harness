# Evals

These evals answer one question: **can a PM trust the knowledge base that `product-map`
writes?** Each pilot product has a set of golden questions that a new PM would really ask.
An agent answers them using only `pm/product/` (no source code), and the answers are
graded against what the code actually does.

| File | What it is |
|------|------------|
| `<product>/golden-questions.yaml` | 20 questions, each with the key points a good answer must contain and the source files that prove them |
| `rubric.md` | How answers are judged, and the pass bar |
| `run_golden.py` | Prints the answering prompt, grades answers automatically, and writes LLM-as-judge prompts |
| `run-cross-agent.sh` | Runs the whole loop headless with Claude Code, Codex, or the Cursor CLI |
| `results/` | One folder per run, with answers, report, and judge prompts |

## Run it by hand (any agent)

```bash
# 1. Give the prompt to your agent, with the knowledge base in pm/
python3 evals/run_golden.py prompt evals/medusa/golden-questions.yaml > prompt.md

# 2. Grade the answers.yaml it writes (cited files are checked against the real repo)
python3 evals/run_golden.py grade evals/medusa/golden-questions.yaml answers.yaml \
  --repo path/to/medusa --out report.md

# 3. Optional second pass: one judge prompt per question for any strong model
python3 evals/run_golden.py judge evals/medusa/golden-questions.yaml answers.yaml \
  --out-dir judge-prompts
```

## Run it with a real agent, headless

```bash
# Does our knowledge base work with this agent?
evals/run-cross-agent.sh --agent claude --repo path/to/medusa

# Does the product-map skill itself work with this agent, from scratch?
evals/run-cross-agent.sh --agent codex --repo path/to/medusa --mode map
```

Agents: `claude` (Claude Code), `codex` (Codex CLI), `cursor` (`cursor-agent`). The script
works on a temporary copy of the repo, so the original is never touched.

## How grading works

The automatic grade is a cheap first filter. A key point counts as covered when the
answer contains one of its phrases. An answer marked `unknown` scores zero, because an
honest "the knowledge base doesn't say" is still a gap in the knowledge base. Phrase matching
misses answers that say the right thing in other words. When a miss looks wrong, read the
answer, then either widen the phrase list or use the judge prompts. Never change a key
point just to make a run pass.

A run passes when average coverage is at least 0.85, no question scores below 0.5, at
least 90% of answers cite an expected source, and no citation points to a missing file.

## Adding a pilot

1. Map the product with `product-map` and save the result to `examples/<product>/pm/`.
2. Write `evals/<product>/golden-questions.yaml`. Write questions a PM would ask in their
   first month: what happens when something fails, who can do what, how two features
   interact. Prove every key point by reading the code yourself, and list those files
   under `sources`.
3. Run the eval. When a question fails, fix the **skill** first so the gap cannot happen
   on other products, then regenerate the map. Record what you changed in `results/README.md`.
