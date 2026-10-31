# Platform signals: where features live

Use this to find entry points quickly in common stacks. Features are usually exposed in
one place (routes, screens, commands) and implemented in another (services, workflows).

## Web apps

| Stack | Pages / screens | Server logic | Data |
|-------|-----------------|--------------|------|
| Next.js (app router) | `app/**/page.tsx`, `app/**/layout.tsx` | `app/**/route.ts`, server actions | Prisma `schema.prisma`, Drizzle schemas |
| Next.js (pages router) | `pages/**/*.tsx` | `pages/api/**` | as above |
| React SPA (Vite/CRA) | `src/routes`, `src/pages`, router config | calls to an API client | API types |
| Rails | `app/views`, `config/routes.rb` | `app/controllers`, `app/services` | `app/models`, `db/schema.rb` |
| Django | `templates/`, `urls.py` | `views.py`, `services.py` | `models.py`, `migrations/` |
| Angular / Vue / Svelte | `src/app/**/*.component.ts`, `src/views`, `src/routes` | API services | API types |

## Mobile apps

| Stack | Screens | Navigation | Data / API |
|-------|---------|------------|------------|
| React Native / Expo | `src/screens`, `app/` (expo-router) | `navigation/`, `app/_layout.tsx` | API client, `state/`, `store/` |
| iOS (Swift) | `*View.swift`, `*ViewController.swift` | `Coordinator`, `NavigationStack` | `Models/`, `Services/` |
| Android (Kotlin) | `*Fragment.kt`, `*Screen.kt` (Compose), `res/layout` | `nav_graph.xml`, `NavHost` | `data/`, `repository/` |
| Flutter | `lib/**/screens`, `*_page.dart` | `go_router`, `routes.dart` | `lib/**/models`, `services/` |

Mobile specifics to capture: app-store release process, offline behavior, push
notifications, deep links, platform differences (iOS vs Android), minimum OS versions.

## APIs and platforms

| Signal | What it tells you |
|--------|-------------------|
| `openapi.yaml`, `swagger.json` | Complete list of public operations; best capability inventory |
| `*.graphql`, `schema.graphql` | Types and operations exposed to clients |
| `*.proto` | Service contracts between internal services |
| `routes/`, `controllers/`, `api/` folders | Endpoints grouped by area; folder names often equal capability names |
| `modules/`, `domains/`, `bounded-contexts/` | Business areas; often 1:1 with capability areas |
| `workflows/`, `sagas/`, `jobs/`, `subscribers/` | Multi-step processes, background work, event reactions |
| `migrations/` | History of data changes; recent ones show active product work |
| `feature-flags/`, `flags.ts`, LaunchDarkly/Unleash/Statsig usage | Behavior switches and in-progress features |
| `providers/`, `adapters/`, `integrations/` | Third-party connections |
| `sdk/`, `client/`, `js-sdk/` | What external developers can do |
| `plugins/`, `extensions/`, `widgets/` | Extension points customers build on |
| `.env.example` | Required services and integrations |

## Monorepos

- Workspace config: `package.json` `workspaces`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`.
- Classify each package as **product** (user-facing behavior), **platform** (framework, SDKs,
  shared infra), **tooling** (CLI, lint, build), or **docs/examples**. Map product packages in
  depth, summarize platform packages, list tooling and docs in one table.

## Statuses and rules are the fastest path to behavior

Search for enums and constants to learn real states and limits:

```bash
rg -n "enum \w*Status|Status\s*=\s*\{|status: .*\|" --type ts
rg -n "throw new \w*Error\(|raise \w*Error|ValidationError" <area-folder>
```

Thrown errors with messages are a ready-made list of "what can go wrong".
