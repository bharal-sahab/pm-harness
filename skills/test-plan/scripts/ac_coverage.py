#!/usr/bin/env python3
"""Check that a test plan covers every acceptance criterion of an initiative's stories.

Usage:
  python3 ac_coverage.py pm/initiatives/<slug> [--plan test-plan.md] [--json]

Finds every criterion (`**AC1: ...**` or `### AC1`) in stories/, and every reference of
the form `STORY-<slug>-<nnn>/AC<n>` in the test plan. Reports criteria with no test
(error) and references to criteria that do not exist (error). Superseded stories are
skipped. Exit code 1 when there are errors.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import load_yaml, split_frontmatter  # noqa: E402

AC_HEAD = re.compile(r"^\*\*(AC\d+)\b|^#{2,4}\s+(AC\d+)\b", re.M)
AC_REF = re.compile(r"\b(STORY-[a-z0-9-]+?-\d{3})/(AC\d+)\b")


def criteria(folder: Path) -> dict[str, str]:
    found = {}
    for f in sorted((folder / "stories").glob("*.md")):
        raw, body = split_frontmatter(f.read_text(encoding="utf-8"))
        meta = (load_yaml(raw) if raw else None) or {}
        if meta.get("status") == "superseded":
            continue
        sid = str(meta.get("id", f.stem))
        for m in AC_HEAD.finditer(body):
            ac = m.group(1) or m.group(2)
            line = body[m.start():body.find("\n", m.start())]
            found[f"{sid}/{ac}"] = line.strip("*# ").strip()
    return found


def coverage(folder: Path, plan_name: str) -> dict:
    acs = criteria(folder)
    plan = folder / plan_name
    text = plan.read_text(encoding="utf-8") if plan.exists() else ""
    refs: dict[str, int] = {}
    for m in AC_REF.finditer(text):
        key = f"{m.group(1)}/{m.group(2)}"
        refs[key] = refs.get(key, 0) + 1
    missing = [k for k in acs if k not in refs]
    unknown = [k for k in refs if k not in acs]
    errors = [f"{k} has no test: {acs[k]}" for k in missing]
    errors += [f"{k} is referenced in {plan_name} but does not exist" for k in unknown]
    if not plan.exists():
        errors.insert(0, f"{plan_name} not found")
    return {"criteria": len(acs), "covered": len(acs) - len(missing),
            "missing": missing, "unknown": unknown, "errors": errors}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("initiative_dir")
    ap.add_argument("--plan", default="test-plan.md")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    r = coverage(Path(args.initiative_dir), args.plan)
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['covered']} of {r['criteria']} acceptance criteria have at least one test.")
        for e in r["errors"]:
            print(f"ERROR   {e}")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
