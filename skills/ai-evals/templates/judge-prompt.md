---
id: EVAL-<slug>-judge-<mode>
type: eval
title: <Feature> - Judge for "<failure mode>"
status: draft
updated: <YYYY-MM-DD>
initiative: <slug>
derived_from: [EVAL-<slug>-taxonomy]
---

# Judge: <failure mode>

**Validation (dev):** TPR <x>, TNR <y> on <n> traces. **Final (test):** TPR <x>, TNR <y>.

## Prompt

```text
You are evaluating one thing only: whether <the failure mode, stated precisely>.

PASS: <exact definition from the taxonomy>
FAIL: <exact definition, with the typical ways it shows up>

Ignore every other quality of the output (style, length, other errors).

Examples:
<Input/output 1 - clear PASS - critique - verdict>
<Input/output 2 - clear FAIL - critique - verdict>
<Input/output 3 - borderline - critique - verdict>

Now evaluate:
Input: {input}
Output: {output}
<Context the judge needs, e.g. the source documents: {context}>

Respond in JSON: {"critique": "<specific evidence from the output>", "result": "Pass" | "Fail"}
```

## Notes

- Examples come from the train split only.
- <Known weak spots of this judge>
