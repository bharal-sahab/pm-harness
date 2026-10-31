# Eval run log

## Medusa

Pilot: [medusajs/medusa](https://github.com/medusajs/medusa) at commit
`2cfefbd370fd133e629b8d545a28460af5ffd01b`. Enterprise-licensed paths are excluded from the
map and may not be cited.

| Run | Agent | Knowledge base | Result | Coverage (avg / lowest) | Grounded | Invalid citations |
|-----|-------|----------------|--------|-------------------------|----------|-------------------|
| [run1](medusa-run1/report.md) | Cursor agent (Claude) | First product-map output | FAIL | 0.95 / 0.00 | 1.00 | 0 |
| [run2](medusa-run2/report.md) | Cursor agent (Claude) | After the skill fix below | PASS | 1.00 / 1.00 | 1.00 | 0 |

### What run 1 taught us

- **Q18 (a variant with no price) was a real gap.** The map recorded "only published
  products can be added" but not the "no price" error thrown next to it in the same function.
  The agent answered honestly with `unknown`. The root cause was in the skill, not the
  product: nothing in `product-map` asked for errors. The fix added an **Errors** step to
  the investigation and an "Errors users can hit" table to every capability. Regenerating
  the capabilities page with the new step closed the gap.
- **Q01 lost a point to wording.** The answer said "the order that was just created is
  deleted", but the phrase list only matched "order is deleted". The phrase list was widened,
  and so was Q18's ("do not have a price"). The key points themselves did not change.
- **Grader fix.** At first, `unknown` answers could get partial credit from a stray keyword
  match. They now score zero, which matches the rubric.

### Cross-agent runs

Not run yet. The Claude Code, Codex, and Cursor CLIs were not installed on the machine
that produced run1 and run2. To fill in this table, run:

```bash
for a in claude codex cursor; do evals/run-cross-agent.sh --agent $a --repo path/to/medusa; done
```

Add a row for each run above. Use `--mode map` to test the skill itself on each agent.
