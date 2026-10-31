# Linear

## Connect

The official server is hosted by Linear at `https://mcp.linear.app/mcp` (read-only:
`https://mcp.linear.app/mcp/readonly`). It uses OAuth 2.1, or a Linear API key as a
bearer token.

```json
{ "mcpServers": { "linear": { "type": "http", "url": "https://mcp.linear.app/mcp" } } }
```

## Tools (checked October 2026)

Recent versions merged create and update into `save_*` tools. Older versions and
third-party servers still use `create_issue` and `update_issue`. Use whichever the
connected server lists.

| Need | Current tool | Older name |
|------|--------------|------------|
| Find the team | `list_teams` | same |
| Workflow states of the team | `list_issue_statuses` | same |
| Labels | `list_issue_labels`, `create_issue_label` | same |
| Create or update an issue | `save_issue` (no ID: create; with ID: update) | `create_issue`, `update_issue` |
| Read an issue and its state | `get_issue`, or `list_issues` filtered by label | same |
| Comment | `save_comment` | `create_comment` |
| Projects (optional, for epics) | `list_projects`, `save_project` | `create_project` |

## Modeling epics

Linear has no "Epic" issue type. Pick one approach with the PM and save it in
`pm/config.yaml` as `tracker.default_issue_type`:

- **Parent issues (default)**: the epic is an issue, and stories are its sub-issues
  (set the story's parent to the epic's ID). Works in any team.
- **Projects**: the epic is a Linear project, and stories belong to it. Better for large
  epics with milestones. Record the project's ID as the epic's `tracker.key`.

## Field mapping

| pm/ field | Linear field | Notes |
|-----------|--------------|-------|
| `title` | Title | |
| body | Description | Markdown is native in Linear |
| `epic` | Parent issue, or project | See "Modeling epics" |
| `priority` | Priority | p0 Urgent (1), p1 High (2), p2 Medium (3), p3 Low (4) |
| `initiative` | Label | Plus the label `pm-harness`; create the labels first if missing |
| `estimate` | Not pushed | The team owns estimates |

The key to record is the issue identifier, like `SHOP-123`. Its URL is in the tool's
response.

## Import without MCP

Linear's importer (**Settings > Import / Export**) can import CSV files from other tools,
including Jira's format. The simplest path is `sync.py csv` (Jira format), then Linear's
Jira CSV option. After the import, record the identifiers with `sync.py record`.
