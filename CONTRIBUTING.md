# Contributing

Thanks for helping. Contributions from product managers matter as much as those from
engineers. Most improvements to this project are better instructions, templates, and
questions, not code.

## Good first contributions

- **Run a skill on your product and report what went wrong.** Open an issue with the skill,
  the agent and model, what you asked, and what was wrong or confusing. Leave out anything
  confidential.
- **Add a pilot.** Run `product-map` on an open-source product with a different shape (a
  mobile app, a developer tool, a data platform) and contribute the output and golden
  questions. See [examples/README.md](examples/README.md).
- **Improve a template.** If your team's PRD or story format has something the templates
  lack, propose it with a reason.
- **Add a tracker or design tool.** Follow the pattern in `skills/work-sync/references/`.

## How the repository works

Read [AGENTS.md](AGENTS.md) first. In short:

- Each skill is a folder under `skills/` with a `SKILL.md`, and optional `templates/`,
  `references/`, and `scripts/`. A skill must work when installed alone.
- Shared files have one canonical copy: the `pm/` conventions in `schemas/`, and
  `check_pm.py` and `pm_status.py` in `scripts/`. Copies inside skills are generated. Edit
  the canonical file, then run the sync.
- Skills only write inside `pm/` and never change product code.
- Scripts use the Python standard library only (Python 3.10 or later). The eval grader
  under `evals/` is the one exception: it needs PyYAML.

## Making a change

1. Edit the skill, template, or canonical file.
2. Sync and validate:

   ```bash
   python3 scripts/validate.py --sync
   ```

   It must report `0 problem(s)`.
3. If you changed what a skill writes, check the example still passes:

   ```bash
   python3 scripts/check_pm.py examples/medusa/pm --strict
   ```

4. If you changed `product-map` or `ask-the-product`, re-run the golden questions
   ([evals/README.md](evals/README.md)) and add the results under `evals/results/`.
5. Open a pull request that says what changed, why, and how you tested it. CI runs the
   same checks, and verifies the example's citations against Medusa's code.

## Writing style for skills

Skills are read by agents, and their output is read by PMs who may be new to the product
and are not engineers.

- Use plain language. Explain a technical term the first time it appears.
- Cite code by path. Do not paste it.
- Say what to do, in order. Keep `SKILL.md` under 500 lines and move long material to
  `references/`.
- Write the `description` in the third person, and include "Use when ..." with phrases a
  PM would actually say.
- Use only Agent Skills frontmatter fields, so every agent can load the skill.

## License

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
