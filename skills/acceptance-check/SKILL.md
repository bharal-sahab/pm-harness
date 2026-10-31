---
name: acceptance-check
description: Reads a pull request or branch diff and reports, for each acceptance criterion of the related stories, whether the change appears to implement it, whether a test covers it, what is missing, and what changed outside the planned scope, with every verdict cited to diff lines. Writes the report to pm/initiatives/<slug>/acceptance/. Use when a PM wants to check a PR against acceptance criteria, verify a story is done before accepting it, review what a branch delivers, or prepare UAT. It is not a code review.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Acceptance Check

Answer the PM's question before they accept a story: **does this change do what we asked,
and how do we know?** This is not a code review. Do not comment on style, structure, or
naming. Engineers review the code; the PM checks the behavior.

## Non-negotiables

- **Read-only.** Never push, approve, merge, or comment on the PR unless the PM asks for a
  comment, and show the comment first.
- **Every verdict cites evidence**: a diff line (`path:line` in the new version) or a test.
- **"Can't tell" is a valid verdict.** Code that looks right is not proof; say what to
  check by hand.
- **Only write inside `pm/`.**

## Workflow

```
Acceptance check progress:
- [ ] 1. Get the diff and the stories
- [ ] 2. Map the diff
- [ ] 3. Judge each criterion
- [ ] 4. Scope, risks, and tests
- [ ] 5. Write the report
```

### 1. Get the diff and the stories

- The diff: with git, compare against the base branch (`--base main`). For a pull request
  without the branch locally, save its diff first (for example `gh pr diff <n> > pr.diff`,
  or the `.diff` URL of the PR) and use `--diff-file`.
- The stories: ask which initiative and stories the PR is for, or read the PR description
  for `STORY-` IDs. Read their acceptance criteria, and the test plan if it exists.

### 2. Map the diff

```bash
python3 <this-skill-dir>/scripts/diff_map.py pm/initiatives/<slug> --diff-file pr.diff
```

It lists every changed file with its kind (test, migration, API, UI, types, config, code),
its added line numbers, and the stories whose `code_refs` point to it. It also lists files
no story mentions, stories with no touched files, tests changed, and API or type lines that
were changed or removed.

### 3. Judge each criterion

For each acceptance criterion of the stories in scope, read the relevant diff hunks and
decide:

| Verdict | Meaning |
|---------|---------|
| **Done and tested** | The diff implements the behavior, and a test in the diff (or an existing test) checks it |
| **Done, not tested** | The diff implements it, but nothing checks it automatically |
| **Partly done** | Some "Then" lines are implemented, others are not |
| **Missing** | Nothing in the diff implements it |
| **Can't tell** | Depends on data, configuration, or code outside the diff; say what to check by hand |
| **Out of scope** | The criterion belongs to a story this PR does not claim |

Cite the diff lines for every verdict. If a test exists, check that it would actually run:
imported helpers and fixtures must exist in the repo or the diff. A test that cannot run
does not count.

### 4. Scope, risks, and tests

- **Unplanned changes**: files no story mentions. Often fine (a type, a helper), sometimes
  scope creep, sometimes a missing `code_refs`. Say which, briefly.
- **API and data changes**: for changed or removed API or type lines, say whether
  existing consumers could break (from the tech impact's consumer list). Flag any migration.
- **Test plan**: map tests in the diff to test-plan cases (`TC-`) where you can.
- **Feature flags**: if the PRD or story needs a flag, check that the change sits behind it.

### 5. Write the report

Write `pm/initiatives/<slug>/acceptance/AC-<slug>-<label>.md` from
[templates/acceptance-report.md](templates/acceptance-report.md), where `<label>` is the
PR number (`pr-1234`) or a short branch name. Frontmatter: `id: AC-<slug>-<label>`,
`type: acceptance-report`, `derived_from` with the story IDs, and `code_refs` with the
changed files.

Lead with the recommendation: **ready to accept**, **accept with follow-ups**, or **not
ready**, and the one or two reasons. Then the criteria table, unplanned changes, risks,
and what to check by hand.

Update the initiative README row, then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

If the PM wants to post a summary on the PR, draft a short comment (the recommendation,
the missing criteria, the manual checks) and show it before posting.
