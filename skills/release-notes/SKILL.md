---
name: release-notes
description: Writes release notes for an initiative in pm/initiatives/<slug>/release.md - user-facing notes in plain language, internal notes for support, sales, and success teams (what changed, how to explain it, known limits, rollout and flags), and a changelog entry - only for stories that are verified as shipped, then hands off to product-map-refresh so the product knowledge base matches the release. Use when a PM is preparing a release, launch, or announcement, asks for release notes, a changelog, or enablement notes, or wants to know what actually shipped.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Release Notes

Announce exactly what shipped, to each audience in its own words, then make sure the
product knowledge base catches up.

## Non-negotiables

- **Only announce what shipped.** A story is shipped when it is done (in `pm/` or in the
  tracker) and its code is in the release. Run the script below and resolve every flag first.
- **Users read benefits, not tickets.** User-facing notes say what people can now do or
  what got better, without story IDs or internal names.
- **Internal notes say what could go wrong.** Known limits, rollout state, and how to
  answer customer questions.
- **Describe behavior as built.** If the shipped code differs from the PRD, the notes
  follow the code (cite it), and the difference goes to the PM.
- **Only write inside `pm/`.**

## Workflow

```
Release notes progress:
- [ ] 1. Find what shipped
- [ ] 2. Resolve the flags
- [ ] 3. Gather the story behind it
- [ ] 4. Draft for each audience
- [ ] 5. Checkpoint and write
- [ ] 6. Hand off to product-map-refresh
```

### 1. Find what shipped

Ask the PM for the release range (previous tag or commit, and this one). If the tracker is
connected, refresh story statuses first with `work-sync` (pull only). Then:

```bash
python3 <this-skill-dir>/scripts/release_scope.py pm/initiatives/<slug> \
  --repo . --from <previous-tag> --to <this-tag>
```

Without git access, pass `--changed-files <file>` with one changed path per line (for
example, from the pull requests in the release).

### 2. Resolve the flags

For every line under "Check before announcing":
- **Done but code not in this release**: it shipped earlier, or its `code_refs` are wrong. Ask.
- **Not done but code changed**: it may have shipped partly. Check the acceptance report,
  or run `acceptance-check`. Do not announce partial work as complete.
- **Acceptance says "Not ready"**: tell the PM before writing anything.

Also check feature flags (from the PRD rollout section and the code): a shipped feature
behind a flag that is off is not released to users. Say so in the internal notes.

### 3. Gather the story behind it

For the shipped stories, read the PRD (problem, who it helps, success metric), the
requirements they cover, the research or brief for user language, and the capability's
error table for limits. Check the actual behavior in the changed code when wording matters
(messages, limits, defaults) and cite it.

### 4. Draft for each audience

Use [templates/release.md](templates/release.md):
- **User-facing**: a headline and two or three sentences per change. Lead with the benefit
  ("You now see why a discount code didn't apply"). Match the product's existing changelog
  tone if there is one (search the repo for `CHANGELOG.md` or release notes).
- **Internal (support, sales, success)**: what changed, who sees it and when (rollout,
  flags, platforms), how to explain it, known limits and edge cases, what to do if a
  customer reports a problem, and the metric the team is watching.
- **Changelog entry**: one line per change in the format the repo already uses (for
  example, Keep a Changelog sections: Added, Changed, Fixed, Removed).
- **API or developer notes** (platform products): new or changed fields, endpoints, and
  types, and whether anything breaks, from `tech-impact.md` and the diff.

### 5. Checkpoint and write

Show the PM the shipped list, anything excluded and why, and the drafts. After confirmation,
write `pm/initiatives/<slug>/release.md` with `id: REL-<slug>`, `type: release`, and
`derived_from` (the PRD and acceptance report IDs). For staged rollouts, add a new
dated section per release in the same file. Mark the shipped stories `status: done` if they
are not already, and set the initiative README stage to "Released". Then:

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

### 6. Hand off to product-map-refresh

The product changed, so the knowledge base is now behind. Tell the PM to run
`product-map-refresh` for the same range (`--since <previous-tag> --to <this-tag>`) so
capabilities, journeys, and the error tables describe the new behavior. Suggest
`status-update` to tell stakeholders.
