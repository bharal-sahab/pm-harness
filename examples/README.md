# Examples

Real output from the harness skills, run on open-source products. Each folder holds the
`pm/` folder the skills wrote, as it would sit in that product's repository.

## Medusa

[Medusa](https://github.com/medusajs/medusa) is an open-source commerce platform: the
backend, APIs, and admin dashboard behind online stores. The knowledge base was built from
commit `2cfefbd370fd133e629b8d545a28460af5ffd01b`. Every code path cited in the example
resolves at that commit, and CI checks this.

### Read in this order

1. [pm/product/OVERVIEW.md](medusa/pm/product/OVERVIEW.md): what Medusa is, who uses it,
   and the capability map.
2. [pm/product/journeys/checkout.md](medusa/pm/product/journeys/checkout.md): one journey
   end to end, including what can go wrong.
3. [pm/product/open-questions.md](medusa/pm/product/open-questions.md): what the code could
   not answer, and surprising behavior worth raising.
4. [pm/initiatives/promo-code-feedback/](medusa/pm/initiatives/promo-code-feedback/): one
   initiative from PRD to status update.

### What each skill produced

| Skill | Output |
|-------|--------|
| `product-map` | Everything in [pm/product/](medusa/pm/product/) except the FAQ |
| `ask-the-product` | [pm/product/faq.md](medusa/pm/product/faq.md) |
| `prd` | [prd.md](medusa/pm/initiatives/promo-code-feedback/prd.md) |
| `tech-impact` | [tech-impact.md](medusa/pm/initiatives/promo-code-feedback/tech-impact.md) |
| `epics-and-stories` | [epics/](medusa/pm/initiatives/promo-code-feedback/epics/) and [stories/](medusa/pm/initiatives/promo-code-feedback/stories/) |
| `test-plan` | [test-plan.md](medusa/pm/initiatives/promo-code-feedback/test-plan.md) |
| `acceptance-check` | [acceptance/](medusa/pm/initiatives/promo-code-feedback/acceptance/), run against [sample-pr/promo-reasons.diff](medusa/sample-pr/promo-reasons.diff) |
| `status-update` | [status/2026-10-30.md](medusa/pm/initiatives/promo-code-feedback/status/2026-10-30.md) |

### What is real and what is made up

- **Real:** everything about how Medusa behaves, with citations to its code. The problem in
  the initiative comes from the map's open questions: Medusa works out why a promo code was
  skipped, but the store API does not return the reason.
- **Made up:** the people, metrics, dates, and decisions in the initiative, and the sample
  pull request. The diff was written for the example against real Medusa files; it is not
  a Medusa pull request.
- **Not covered:** Medusa's Enterprise-licensed code (role-based access and single sign-on)
  was excluded on purpose, and the documentation sites under `www/`. See
  [pm/config.yaml](medusa/pm/config.yaml).

The research, design, release, and tracker skills have no Medusa output yet, because
they need inputs a code scan cannot provide: interview notes, designs, a real release, or a
Jira or Linear workspace.

### Check it yourself

```bash
python3 scripts/check_pm.py examples/medusa/pm --strict                  # structure and links
python3 scripts/pm_status.py examples/medusa/pm                          # where things stand
python3 skills/epics-and-stories/scripts/trace.py examples/medusa/pm/initiatives/promo-code-feedback
```

To verify citations too, download Medusa at the commit above and pass `--repo <path>` to
`check_pm.py`.

## Adding a pilot

Pick an open-source product with a permissive license and a different shape from the
existing pilots (for example, a mobile app or a developer tool). Run `product-map` on it, put
the output in `examples/<name>/pm/`, and add golden questions under `evals/<name>/` (see
[evals/README.md](../evals/README.md)). Record the commit in `pm/product/_meta.yaml`.
