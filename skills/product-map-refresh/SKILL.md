---
name: product-map-refresh
description: Brings the pm/product knowledge base up to date with the code by reading the git diff since the last map, updating only the affected pages, fixing broken citations, flagging FAQ answers and initiative artifacts that may be outdated, and writing a plain-language changelog of what changed for users. Use when pm/product exists but the code has moved on, after a release, when pm-start reports the map is stale, or when a PM asks "what changed in the product since...".
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Product Map Refresh

Keep `pm/product/` true without rebuilding it. A full `product-map` run is slow; most
weeks only a few behaviors change. This skill finds them, updates only those parts, and
tells the PM in plain language what changed for users.

## Non-negotiables

- **Read-only on product code.** Only write inside `pm/`.
- **Capability IDs never change.** Other artifacts link to them. A removed capability is
  marked as removed, never deleted or renamed.
- **Behavior, not code churn.** Refactors, renames, types, and performance work change
  nothing for users. Do not write about them except to fix citations.
- **Cite every new or changed claim**, and recheck line numbers in files that changed.
- **Respect `exclude_paths`** in `pm/config.yaml`.

## Workflow

Copy this checklist into your reply and keep it updated:

```
Refresh progress:
- [ ] 1. Preflight
- [ ] 2. Find what changed
- [ ] 3. Read the diffs and sort them
- [ ] 4. Checkpoint: confirm the update plan
- [ ] 5. Update pages and citations
- [ ] 6. Write the changelog and update _meta
- [ ] 7. Audit and hand off
```

### 1. Preflight

- If `pm/product/_meta.yaml` does not exist, stop and suggest `product-map`.
- Read `source_commit` from `_meta.yaml` and run `git rev-parse HEAD`. If they match, say
  the map is current and stop.
- If git is unavailable or the old commit is missing (shallow clone), ask the PM for a
  list of changed files or a compare link, save it to a file, and use `--changed-files`.
- If the diff is huge (more than about 2,000 relevant files, or a major version upgrade),
  recommend a full `product-map` rebuild instead, and let the PM decide.

### 2. Find what changed

```bash
python3 <this-skill-dir>/scripts/changed_pages.py pm --repo . > /tmp/pm-refresh.md
```

The report lists:

- **Product pages to update**: changed files mapped to pages through `page_sources`.
- **Citations that broke**: cited files that were deleted or renamed. These must be fixed.
- **Artifacts that cite changed files**: any page, FAQ answer, or initiative artifact
  whose claims may now be false.
- **Line-numbered citations in modified files**: the lines may have moved.
- **Changed areas no page covers**: possible new capabilities.

Tests, tooling, docs, dependency manifests, and excluded paths are already filtered out.

### 3. Read the diffs and sort them

For each changed file the report maps to a page, read the diff:

```bash
git diff <source_commit> HEAD -- <file>
```

Sort each change into one bucket:

| Bucket | Examples | What to do |
|--------|----------|------------|
| **User-visible** | New field, screen, status, rule, limit, error message, permission, email, integration | Update the page |
| **Moved** | File renamed or code moved, same behavior | Fix the citation only |
| **Internal** | Refactor, types, performance, logging | Nothing |

Use commit messages to find the intent (`git log --oneline <source_commit>..HEAD -- <path>`),
but trust the diff over the message.

For **changed areas no page covers**, open the folder. New routes, screens, modules, or
workflows usually mean a new capability or a new part of an existing one. Shared UI,
plumbing, and build tools do not. Add them to `not_covered` in `_meta.yaml` if they matter.

### 4. Checkpoint: confirm the update plan

Show the PM the plan and wait for confirmation:

```
Commits: <old short sha>..<new short sha> (<n> commits, <date range>)
User-visible changes: <n>
  - <capability>: <one line in plain language>
Pages to edit: <list>
New capabilities: <list or none>
Removed capabilities: <list or none>
Citations to fix: <n broken, n line numbers to recheck>
May be outdated: <FAQ answers and initiative artifacts>
```

### 5. Update pages and citations

- Edit only the affected sections. Keep each page's voice and structure.
- **New capability**: add a `### CAP-<new-slug>: <Title>` section using the `product-map`
  capability format (what it does, who uses it, rules and limits, errors users can hit,
  switches, confidence, where in the code). Add its folders to `page_sources`.
- **Removed capability**: keep the heading and replace its body with
  `**Removed** in \`<short sha>\`: <what replaced it, if anything>`.
- **Broken citations**: for a rename, point to the new path. For a deletion, find where the
  behavior went (search for the function or message). If it is gone, update or remove the
  claim. If you cannot tell, mark the claim *unknown* and add an open question.
- **Line numbers**: open each listed citation and fix the range so it still shows the claim.
- **FAQ answers** that cite changed files: re-verify. Update the answer, or add
  `**Possibly outdated** since \`<short sha>\`` under it if you cannot check it now.
- **Initiative artifacts** (`pm/initiatives/...`): do not edit them. List them in the
  hand-off. The owning skill or the PM decides what to change.
- **Open questions**: if a change answers one, mark it answered with the citation.
- Update `updated:` in the frontmatter of every page you edit.

### 6. Write the changelog and update `_meta`

Add an entry at the top of `pm/product/changelog.md` (create it from
[templates/changelog.md](templates/changelog.md) if missing). Write for a PM. Lead with
what users can now do differently, grouped by capability. Every bullet has a citation.

Then update `pm/product/_meta.yaml`:

```yaml
source_commit: <new HEAD sha>
refreshed_at: <YYYY-MM-DD>          # keep generated_at as the original build date
refresh_history:
  - {from: <old sha>, to: <new sha>, date: <YYYY-MM-DD>, pages: [<pages edited>]}
```

### 7. Audit and hand off

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo . --strict
```

Fix every error. Then tell the PM in a few sentences:
- the three to five changes that matter most for users,
- any FAQ answers or initiative artifacts that may now be wrong, and who should look,
- any new area that might deserve its own capability.

## Running after a release

The `release-notes` skill calls this one after a release. In that case, compare against the
release tag or merge commit instead of `HEAD`: `--to <tag>`.
