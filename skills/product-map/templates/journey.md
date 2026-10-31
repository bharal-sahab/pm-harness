---
id: JRN-<slug>
type: journey
title: <Journey name>
status: draft
updated: <YYYY-MM-DD>
source_commit: <sha>
capabilities: [CAP-<slug>]
---

# Journey: <name>

**Actor:** <who>  **Trigger:** <what starts it>  **Outcome:** <what success looks like>

## The flow

```mermaid
sequenceDiagram
  actor User
  participant Surface as <Storefront / App / Admin>
  participant System as <Backend>
  User->>Surface: <action>
  Surface->>System: <request>
  System-->>Surface: <result>
```

## Step by step

| # | What the user does or sees | What the system does | Code |
|---|----------------------------|----------------------|------|
| 1 | <...> | <...> | `<path>` |

## Business rules

- <Rule> `<path>`

## What can go wrong

| Situation | What the user experiences | What the system does | Code |
|-----------|---------------------------|----------------------|------|
| <Payment declined> | <...> | <...> | `<path>` |

## Events and notifications

- `<event.name>`: <when it fires, who listens> `<path>`

## Open questions

- <Question the code could not answer>
