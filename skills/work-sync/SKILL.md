---
name: work-sync
description: Pushes epics and stories from pm/initiatives to Jira or Linear through whichever tracker MCP server is connected, and pulls keys and statuses back into the markdown, keeping pm/ as the source of truth for content and the tracker as the source of truth for status. Falls back to a CSV import file when no MCP server is available. Use when a PM wants to create tickets, push stories to Jira or Linear, sync a backlog, update tickets after editing stories, or pull ticket status back.
license: Apache-2.0
metadata:
  harness: pm-harness
  version: "0.1.0"
---

# Work Sync

Keep stories in two places without them drifting apart. The rule that makes it work:

- **`pm/` owns the content**: title, description, acceptance criteria, priority.
- **The tracker owns the workflow**: status, assignee, sprint, estimate.

Push content out, pull status back. Never overwrite one side's fields from the other.

## Non-negotiables

- **Nothing is pushed without the PM's confirmation.** Show the plan first, every time.
- **Never delete or close tracker items.** Superseded stories get a comment, not a deletion.
- **Record every result** with the script, so `pm/` always knows the key of each item.
- **The tracker MCP server is optional.** Without one, export a CSV for import instead.

## Workflow

```
Sync progress:
- [ ] 1. Check setup
- [ ] 2. Build the plan
- [ ] 3. Checkpoint: confirm the plan
- [ ] 4. Push
- [ ] 5. Pull status back
- [ ] 6. Check and report
```

### 1. Check setup

- Read `tracker` in `pm/config.yaml`: `system` (`jira` or `linear`), `project_key`, and
  `default_issue_type`. If `system` is `null`, ask the PM which tracker and project to
  use and save the answer there.
- Check that a tracker MCP server is connected by looking for its tools. See
  [references/jira.md](references/jira.md) or [references/linear.md](references/linear.md)
  for the tool names, how to connect, and the field mapping.
- No server? Offer the CSV fallback (step 4b), or help the PM connect one.

### 2. Build the plan

```bash
python3 <this-skill-dir>/scripts/sync.py plan pm/initiatives/<slug> --system <jira|linear>
```

Each epic and story gets an action:

- **create**: it has no tracker key yet.
- **update**: its content changed since the last push (the script compares a hash).
- **none**: already in sync.

Use `--json` to get the full payloads: title, description (relative links rewritten as
repo paths, with a source footer), type, priority mapped to the tracker's names, labels,
and the parent epic.

### 3. Checkpoint: confirm the plan

Show the plan table and the target project, and wait for confirmation. Mention anything
unusual: stories whose epic is not in the tracker yet (epics go first), or updates that
would overwrite text someone edited in the tracker (check the item's last update time
against `synced_at` before pushing an update).

### 4. Push

**a. With an MCP server.** Process epics first, then stories, so each story can be linked
to its parent epic's key. For each item:

1. Create or update it with the payload, using the tool names in the reference.
2. Record the result right away:

```bash
python3 <this-skill-dir>/scripts/sync.py record <artifact.md> --system <jira|linear> \
  --key <KEY> --url <URL> --content-synced
```

If a call fails, stop, report what was created so far, and do not retry blindly. Re-running
the plan shows exactly what is left.

**b. Without an MCP server.** For Jira:

```bash
python3 <this-skill-dir>/scripts/sync.py csv pm/initiatives/<slug> > <slug>-import.csv
```

Tell the PM how to import it (in [references/jira.md](references/jira.md)). After the
import, ask for the created keys and record them with `sync.py record`. For Linear, use the
plan's `--json` output and the import steps in [references/linear.md](references/linear.md).

### 5. Pull status back

For each item with a key, read its current status through the MCP server, then record it:

```bash
python3 <this-skill-dir>/scripts/sync.py record <artifact.md> --system <s> --key <KEY> \
  --status "<tracker status name>"
```

The script stores the tracker's status name and maps it to the harness status
(`approved`, `in-progress`, `done`, `superseded`). Do not use `--content-synced` when only
pulling status.

If someone changed the title or description in the tracker, do not copy it back silently.
Show the PM the difference and ask which version should win, then edit the markdown and
push again.

### 6. Check and report

```bash
python3 <this-skill-dir>/scripts/check_pm.py pm --repo .
```

Report in a few lines: what was created or updated (with links), what failed, and the
status counts pulled back. Update the initiative README if stages changed. Suggest
`status-update` for a stakeholder summary.
