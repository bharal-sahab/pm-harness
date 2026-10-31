# Jira

## Connect

The official server is Atlassian's **Rovo MCP server**, at `https://mcp.atlassian.com/v2/mcp`.
It uses OAuth 2.1 (or an API token if your admin allows it). The agent's MCP settings
usually look like this:

```json
{ "mcpServers": { "atlassian": { "type": "http", "url": "https://mcp.atlassian.com/v2/mcp" } } }
```

Writing needs the `write:jira:agent-interface` scope, granted through your organization's
permission groups. If tools are missing, ask your Jira admin which permission groups are on.

## Tools (Rovo MCP v2, checked October 2026)

Primary tools appear directly in the tool list. Other tools are found with `discover` and
called through `executeRead` or `executeWrite`. Names change between versions, so if a name
below is missing, call `discover` with a plain description ("create a Jira work item").

| Need | Tool |
|------|------|
| Find the cloud site and projects | `listJiraProjects` (deferred) |
| Issue types available in the project | `listJiraProjectIssueTypesMetadata` (deferred) |
| Create an epic or story | `createJiraIssue` (primary): `project`, `issueType`, `summary`, description, parent |
| Update content | `editJiraIssue` (primary) |
| Read status | `getJiraIssue` (primary), or `searchJiraIssuesUsingJql` for many at once |
| Comment (for superseded stories) | `addOrEditJiraIssueComment` (primary) |
| Link two items (dependencies) | `createJiraIssueLink` (deferred) |

Older v1 servers used other names (`getVisibleJiraProjects`, `addCommentToJiraIssue`,
`issueTypeName`). Prefer v2.

## Field mapping

| pm/ field | Jira field | Notes |
|-----------|------------|-------|
| `title` | Summary | |
| body | Description | Send markdown if the tool accepts it; the payload already rewrites relative links |
| `type: epic` | Issue type "Epic" | Some projects rename it; check the issue types first |
| `type: story` | `default_issue_type` from config, usually "Story" | |
| `epic` | Parent | Use the epic's key from its `tracker.key` |
| `priority` | Priority | p0 Highest, p1 High, p2 Medium, p3 Low (the script maps it) |
| `initiative` | Label | Plus the label `pm-harness` |
| `estimate` | Not pushed | The team owns estimates in Jira |

Bulk status read: `searchJiraIssuesUsingJql` with
`project = <KEY> AND labels = <initiative-slug>`.

## CSV import (no MCP server)

1. Create the file with `sync.py csv`. It contains only items to create.
2. In Jira: **Settings > System > External System Import > CSV** (admins), or the
   project's **Import work items** option.
3. Map the columns: Summary, Issue Type, Description, Priority, Labels. Map "Issue ID" and
   "Parent ID" so Jira links stories to their epics.
4. After the import, collect the keys and record each one with `sync.py record`.
