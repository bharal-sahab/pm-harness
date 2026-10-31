# AGENTS.md: working on the PM harness

This repository contains the PM harness: a set of portable Agent Skills that help product
managers understand a codebase and run the product lifecycle on top of that understanding.
These instructions are for agents and humans editing the harness itself. The rules the
skills follow inside a product repo live in `schemas/artifact-frontmatter.md`.

## Layout

- `skills/<name>/SKILL.md` holds one skill, plus optional `templates/`, `references/`, `scripts/`.
- `schemas/artifact-frontmatter.md` is the canonical copy of the `pm/` folder conventions.
- `scripts/check_pm.py` is the canonical `pm/` folder checker, and `scripts/pm_status.py`
 the canonical status report (vendored into pm-start and status-update).
- `scripts/validate.py` validates every skill. Run `--sync` to copy shared files into skills.
- `scripts/install.sh` installs skills into a product repo or globally.
- `evals/` holds golden questions, rubrics, and graded results used to test the skills.
- `examples/<pilot>/pm/` holds real output produced by the skills on pilot repositories.

## Rules for skills

1. Use only frontmatter fields from the Agent Skills spec: `name`, `description`, `license`,
   `compatibility`, `metadata`, `allowed-tools`. No agent-specific fields, so every skill
   works in Claude Code, Codex, Cursor, Copilot, and Antigravity.
2. `name` matches the folder name. `description` is third person, says what the skill does
   and includes "Use when ..." with trigger phrases a PM would actually say.
3. Keep `SKILL.md` under 500 lines. Put templates in `templates/`, long guidance in
   `references/`, and deterministic work in `scripts/`. Link them one level deep.
4. Each skill is self-contained: it may be installed alone. Never link to another skill's
   files. Name the other skill instead ("run the `product-map` skill first").
5. Shared files are vendored, not linked. Edit the canonical file under `schemas/` or
   `scripts/`, then run `python3 scripts/validate.py --sync`.
6. Skills never modify product code. They only write inside `pm/` in the product repo.
7. Skills that call external tools (Jira, Linear, Figma) must work without them: they
   produce markdown first and treat the external push as an optional step behind a checkpoint.
8. Write for a PM who is new to the product and not deeply technical: plain language,
   terms explained on first use, code cited by path instead of pasted.

## Before you finish a change

```bash
python3 scripts/validate.py --sync
```

The command must report `0 problem(s)`. If you changed what a skill writes, also run
`python3 scripts/check_pm.py examples/medusa/pm --strict`. If you changed product-map or
ask-the-product, re-run the golden questions in `evals/medusa/` and update `evals/results/`.
CI (`.github/workflows/ci.yml`) runs these checks and verifies the example's citations
against Medusa's code.
