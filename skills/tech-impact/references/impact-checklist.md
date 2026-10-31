# Impact checklist

What to look for on each surface, and quick ways to find it. Adapt the search commands to
the repo's languages (see `pm/product/how-it-is-built.md`).

## Surfaces

| Surface | Look for | Quick search |
|---------|----------|--------------|
| User interface | Pages, screens, components that show or collect the data; empty, loading, and error states | `rg -l "<field or label text>" --type tsx`; route folders; i18n files for the copy |
| API | Route handlers, request validators, response types, SDK methods, OpenAPI specs | `rg -n "<path segment>" <api folder>`; `rg -n "<ResponseType>"` |
| Business logic | Services, workflows, use cases, jobs; the line where the decision is made | `rg -n "throw new\|raise\|Error(" <module>`; the capability's citations |
| Data | Models, schema files, migrations, enums, indexes | `rg -n "enum\|model\|Entity\|Table" <module>/models` |
| Events and integrations | Emitted events, subscribers, webhooks, provider calls | `rg -n "emit\|publish\|subscribe\|webhook"` |
| Configuration | Feature flags, settings, environment variables, permissions | `rg -n "feature_flag\|featureFlag\|isEnabled\|permission"` |

## Consumers of a changed API or event

- Web storefront or app, mobile apps (old versions stay installed for months), admin UI.
- Generated or hand-written SDKs and their response types.
- Partner integrations, webhooks subscribers, plugins, extension hooks.
- Analytics events and dashboards that read the fields.

Adding a field to a response is usually safe. Renaming, removing, or changing the meaning
of one is a **breaking change**.

## Risk categories

| Category | Ask |
|----------|-----|
| Breaking change | Does any consumer rely on the current shape or behavior? |
| Data migration | Do existing records need new values or a backfill? Can it run without downtime? |
| Money | Does it change prices, discounts, taxes, payments, or refunds? Rounding and currency? |
| Security and privacy | Does it reveal data to someone new (for example, why a code failed might reveal a customer's group)? |
| Performance | Does it add work to a hot path (cart, checkout, search, login)? |
| Permissions | Who can see or do the new thing? Is that enforced on the server? |
| Third parties | Does it depend on a provider's behavior, limits, or contract? |
| Extensibility | Do plugins, hooks, or customer extensions run in this path and assume today's behavior? |
| Localization | New user-facing text that needs translation? Formats for dates, money? |
| Concurrency | Can two requests race (double click, two tabs, retries)? Is there a lock? |

## Sizing guide

| Size | Usually means |
|------|---------------|
| S | Config or copy change, or exposing data the code already has; one surface |
| M | New behavior in one area across two or three surfaces; no data migration |
| L | New data, a migration, a breaking change, or work across many surfaces or teams |

Always give the reason next to the size. Engineering will refine it.
