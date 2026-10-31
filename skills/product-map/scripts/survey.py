#!/usr/bin/env python3
"""Inventory a repository so an agent can plan a product map.

Usage:
    python3 survey.py [repo-dir] [--exclude PATH ...] [--commit SHA] [--json]

Reads only file names, manifests, license files, and env examples. Never reads
files under excluded paths (from --exclude and pm/config.yaml `exclude_paths`).
Prints a markdown report (or JSON with --json) covering: size and languages,
frameworks, likely platforms, monorepo packages, feature-bearing folders, API
specs, docs, feature flags, integration hints, and license-restricted paths.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", ".nuxt", "vendor", "Pods", "__pycache__",
    ".venv", "venv", "target", "coverage", ".turbo", ".cache", ".yarn", ".gradle", "DerivedData",
    ".idea", ".vscode", "out", ".expo", ".svelte-kit", "tmp", ".pilots",
}
LANG_BY_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript (React)", ".js": "JavaScript", ".jsx": "JavaScript (React)",
    ".mjs": "JavaScript", ".cjs": "JavaScript", ".py": "Python", ".rb": "Ruby", ".go": "Go",
    ".java": "Java", ".kt": "Kotlin", ".swift": "Swift", ".m": "Objective-C", ".dart": "Dart",
    ".cs": "C#", ".php": "PHP", ".rs": "Rust", ".scala": "Scala", ".ex": "Elixir", ".exs": "Elixir",
    ".vue": "Vue", ".svelte": "Svelte", ".sql": "SQL", ".graphql": "GraphQL", ".proto": "Protobuf",
    ".html": "HTML", ".erb": "Ruby templates", ".css": "CSS", ".scss": "SCSS",
}
JS_FRAMEWORKS = {
    "next": ("Next.js", "web"), "react": ("React", "web"), "vue": ("Vue", "web"), "nuxt": ("Nuxt", "web"),
    "@angular/core": ("Angular", "web"), "svelte": ("Svelte", "web"), "@remix-run/react": ("Remix", "web"),
    "vite": ("Vite", "web"), "react-native": ("React Native", "mobile"), "expo": ("Expo", "mobile"),
    "@capacitor/core": ("Capacitor", "mobile"), "electron": ("Electron", "desktop"), "@tauri-apps/api": ("Tauri", "desktop"),
    "express": ("Express", "api"), "@nestjs/core": ("NestJS", "api"), "fastify": ("Fastify", "api"), "koa": ("Koa", "api"),
    "hono": ("Hono", "api"), "graphql": ("GraphQL", "api"), "@apollo/server": ("Apollo Server", "api"),
    "@trpc/server": ("tRPC", "api"), "@mikro-orm/core": ("MikroORM", None), "typeorm": ("TypeORM", None),
    "prisma": ("Prisma", None), "@prisma/client": ("Prisma", None), "drizzle-orm": ("Drizzle", None),
    "sequelize": ("Sequelize", None), "mongoose": ("Mongoose (MongoDB)", None), "redis": ("Redis client", None),
    "ioredis": ("Redis client", None), "bullmq": ("BullMQ queues", None), "stripe": ("Stripe SDK", None),
    "commander": ("CLI (commander)", "cli"), "yargs": ("CLI (yargs)", "cli"),
}
PY_FRAMEWORKS = {
    "django": ("Django", "web"), "flask": ("Flask", "api"), "fastapi": ("FastAPI", "api"),
    "sqlalchemy": ("SQLAlchemy", None), "celery": ("Celery queues", None), "pydantic": ("Pydantic", None),
}
SIGNAL_DIRS = {
    "routes", "pages", "app", "screens", "views", "controllers", "api", "models", "entities", "migrations",
    "schemas", "workflows", "jobs", "subscribers", "handlers", "services", "features", "modules",
    "resolvers", "components", "domain", "usecases", "use-cases", "commands", "events", "webhooks",
}
INTEGRATION_HINTS = {
    "STRIPE": "Stripe (payments)", "PAYPAL": "PayPal (payments)", "ADYEN": "Adyen (payments)",
    "SENDGRID": "SendGrid (email)", "MAILGUN": "Mailgun (email)", "RESEND": "Resend (email)", "SES": "AWS SES (email)",
    "TWILIO": "Twilio (SMS)", "S3": "AWS S3 (files)", "AWS": "AWS", "GCS": "Google Cloud Storage",
    "REDIS": "Redis", "DATABASE_URL": "SQL database", "POSTGRES": "Postgres", "MONGO": "MongoDB",
    "ALGOLIA": "Algolia (search)", "MEILI": "Meilisearch (search)", "ELASTIC": "Elasticsearch",
    "SENTRY": "Sentry (errors)", "SEGMENT": "Segment (analytics)", "POSTHOG": "PostHog (analytics)",
    "AMPLITUDE": "Amplitude (analytics)", "GOOGLE": "Google", "GITHUB": "GitHub", "AUTH0": "Auth0",
    "CLERK": "Clerk (auth)", "OPENAI": "OpenAI", "ANTHROPIC": "Anthropic", "SLACK": "Slack",
}
RESTRICTIVE = re.compile(r"enterprise|commercial|proprietary|business source|BUSL|elastic license|SSPL", re.I)


def load_config_excludes(repo: Path) -> list[str]:
    cfg = repo / "pm" / "config.yaml"
    if not cfg.exists():
        return []
    excludes, in_block = [], False
    for line in cfg.read_text().splitlines():
        if line.startswith("exclude_paths:"):
            rest = line.split(":", 1)[1].strip()
            if rest.startswith("["):
                return [p.strip().strip("'\"") for p in rest.strip("[]").split(",") if p.strip()]
            in_block = True
            continue
        if in_block:
            if line.strip().startswith("- "):
                excludes.append(line.strip()[2:].split("#")[0].strip().strip("'\""))
            elif line.strip() and not line.startswith(" "):
                break
    return excludes


def walk(repo: Path, excludes: list[str]):
    ex = [e.rstrip("/") for e in excludes]
    stack = [repo]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir())
        except (PermissionError, FileNotFoundError):
            continue
        for p in entries:
            rel = p.relative_to(repo).as_posix()
            if any(rel == e or rel.startswith(e + "/") for e in ex):
                continue
            if p.is_dir():
                if p.name in IGNORE_DIRS or p.is_symlink():
                    continue
                stack.append(p)
                yield p, rel, True
            else:
                yield p, rel, False


def git_commit(repo: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:  # noqa: BLE001
        return None


def survey(repo: Path, excludes: list[str], commit: str | None) -> dict:
    langs, files, dirs = Counter(), 0, 0
    manifests, signal_dirs, api_specs, docs, flags, env_examples, licenses = [], Counter(), [], [], [], [], []
    frameworks, platforms = {}, set()
    packages = []
    mobile_markers = []

    for path, rel, is_dir in walk(repo, excludes):
        if is_dir:
            dirs += 1
            if path.name.lower() in SIGNAL_DIRS:
                signal_dirs[rel] += 1
            if path.name.endswith(".xcodeproj"):
                mobile_markers.append(rel)
                platforms.add("mobile")
            if "feature-flag" in path.name.lower() or "featureflag" in path.name.lower():
                flags.append(rel)
            continue
        files += 1
        name, low = path.name, path.name.lower()
        lang = LANG_BY_EXT.get(path.suffix.lower())
        if lang:
            langs[lang] += 1
        if name in ("package.json", "pyproject.toml", "requirements.txt", "Gemfile", "go.mod", "pom.xml",
                    "build.gradle", "build.gradle.kts", "pubspec.yaml", "Podfile", "Package.swift", "Cargo.toml",
                    "composer.json", "mix.exs", "pnpm-workspace.yaml", "turbo.json", "nx.json", "lerna.json"):
            manifests.append(rel)
        if re.search(r"(openapi|swagger).*\.(ya?ml|json)$", low) or low.endswith((".graphql", ".gql", ".proto")):
            api_specs.append(rel)
        if low in ("readme.md", "agents.md", "claude.md", "contributing.md", "architecture.md") or "/adr/" in rel.lower():
            docs.append(rel)
        if ("feature-flag" in low or "featureflag" in low or "feature_flag" in low) and len(flags) < 200:
            flags.append(rel)
        if low.startswith(".env") and ("example" in low or "template" in low or "sample" in low):
            env_examples.append(path)
        if "license" in low and path.suffix.lower() in ("", ".md", ".txt"):
            licenses.append(path)
        if name == "AndroidManifest.xml":
            mobile_markers.append(rel)
            platforms.add("mobile")

    for rel in manifests:
        path = repo / rel
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if path.name == "package.json":
            try:
                pkg = json.loads(text)
            except json.JSONDecodeError:
                continue
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {}), **pkg.get("peerDependencies", {})}
            for dep, (label, plat) in JS_FRAMEWORKS.items():
                if dep in deps:
                    frameworks.setdefault(label, []).append(rel)
                    if plat:
                        platforms.add(plat)
            if pkg.get("bin"):
                platforms.add("cli")
            if rel != "package.json" and pkg.get("name"):
                packages.append({"path": str(Path(rel).parent), "name": pkg.get("name"),
                                 "description": (pkg.get("description") or "")[:140]})
        elif path.name in ("pyproject.toml", "requirements.txt"):
            for dep, (label, plat) in PY_FRAMEWORKS.items():
                if re.search(rf"(?im)^\s*[\"']?{dep}\b", text):
                    frameworks.setdefault(label, []).append(rel)
                    if plat:
                        platforms.add(plat)
        elif path.name == "Gemfile" and re.search(r"gem ['\"]rails['\"]", text):
            frameworks.setdefault("Ruby on Rails", []).append(rel)
            platforms.add("web")
        elif path.name == "go.mod":
            frameworks.setdefault("Go module", []).append(rel)
            platforms.add("api")
        elif path.name in ("pom.xml", "build.gradle", "build.gradle.kts"):
            if "spring-boot" in text:
                frameworks.setdefault("Spring Boot", []).append(rel)
                platforms.add("api")
            if "com.android.application" in text:
                frameworks.setdefault("Android app", []).append(rel)
                platforms.add("mobile")
        elif path.name == "pubspec.yaml" and "flutter" in text:
            frameworks.setdefault("Flutter", []).append(rel)
            platforms.add("mobile")
        elif path.name in ("Podfile", "Package.swift"):
            frameworks.setdefault("iOS / Swift", []).append(rel)
            platforms.add("mobile")

    if len(packages) >= 8:
        platforms.add("platform")

    integrations = Counter()
    env_keys = []
    for env in env_examples[:20]:
        for line in env.read_text(errors="ignore").splitlines():
            key = line.split("=", 1)[0].strip()
            if re.fullmatch(r"[A-Z][A-Z0-9_]+", key):
                env_keys.append(key)
                for hint, label in INTEGRATION_HINTS.items():
                    if hint in key:
                        integrations[label] += 1

    restricted = []
    for lic in licenses:
        try:
            text = lic.read_text(errors="ignore")
        except OSError:
            continue
        if RESTRICTIVE.search(text[:5000]):
            paths = sorted(set(re.findall(r"`([\w@.\-\[\]/]+/?)`", text)))
            restricted.append({"file": lic.relative_to(repo).as_posix(),
                               "listed_paths": [p for p in paths if "/" in p][:200]})

    return {
        "repo": str(repo),
        "commit": commit or git_commit(repo) or "unknown",
        "files": files,
        "dirs": dirs,
        "languages": langs.most_common(12),
        "frameworks": {k: sorted(set(v))[:5] for k, v in sorted(frameworks.items())},
        "platform_guess": sorted(platforms) or ["unknown"],
        "manifests": sorted(manifests)[:60],
        "workspace_packages": sorted(packages, key=lambda p: p["path"])[:150],
        "feature_dirs": sorted(signal_dirs)[:120],
        "api_specs": sorted(api_specs)[:40],
        "docs": sorted(docs)[:60],
        "feature_flags": sorted(set(flags))[:60],
        "mobile_markers": sorted(mobile_markers)[:20],
        "env_keys": sorted(set(env_keys))[:80],
        "integration_hints": integrations.most_common(30),
        "restricted_licenses": restricted,
        "excluded": excludes,
    }


def to_markdown(s: dict) -> str:
    out = [f"# Repository survey\n", f"- Repo: `{s['repo']}`", f"- Commit: `{s['commit']}`",
           f"- Size: {s['files']} files in {s['dirs']} folders (dependencies and build output skipped)",
           f"- Platform guess: {', '.join(s['platform_guess'])}",
           f"- Excluded paths: {', '.join(s['excluded']) or 'none'}\n"]

    def section(title, rows):
        out.append(f"## {title}\n")
        out.extend(rows or ["- none found"])
        out.append("")

    section("Languages (file count)", [f"- {l}: {n}" for l, n in s["languages"]])
    section("Frameworks and libraries", [f"- {k} (in {', '.join(v)})" for k, v in s["frameworks"].items()])
    section("Workspace packages", [f"- `{p['path']}` {p['name']}: {p['description']}" for p in s["workspace_packages"]])
    section("Feature-bearing folders", [f"- `{d}`" for d in s["feature_dirs"]])
    section("API specs", [f"- `{p}`" for p in s["api_specs"]])
    section("Existing docs", [f"- `{p}`" for p in s["docs"]])
    section("Feature flags", [f"- `{p}`" for p in s["feature_flags"]])
    section("Integration hints (from env examples)", [f"- {l}" for l, _ in s["integration_hints"]])
    rows = []
    for r in s["restricted_licenses"]:
        rows.append(f"- `{r['file']}` uses restrictive wording. Paths it lists (propose as exclude_paths):")
        rows.extend(f"  - `{p}`" for p in r["listed_paths"]) if r["listed_paths"] else rows.append("  - (no paths listed; read the file)")
    section("License-restricted areas", rows)
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", default=".", type=Path)
    ap.add_argument("--exclude", action="append", default=[], help="repo-relative path to skip (repeatable)")
    ap.add_argument("--commit", default=None, help="commit SHA when the repo has no git metadata")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not repo.is_dir():
        print(f"Not a directory: {repo}", file=sys.stderr)
        return 2
    excludes = sorted(set(args.exclude + load_config_excludes(repo)))
    result = survey(repo, excludes, args.commit)
    print(json.dumps(result, indent=2) if args.json else to_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
