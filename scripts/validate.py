#!/usr/bin/env python3
"""Validate harness skills against the Agent Skills spec and harness rules.

Usage:
    python3 scripts/validate.py            # validate skills, vendored files, examples
    python3 scripts/validate.py --sync     # copy canonical shared files into skills first

Checks per skill (https://agentskills.io/specification):
  - SKILL.md exists and starts with YAML frontmatter
  - only spec fields: name, description, license, compatibility, metadata, allowed-tools
  - name: 1-64 chars, lowercase a-z 0-9 and single hyphens, matches folder name
  - description: 1-1024 chars; compatibility <= 500 chars; metadata is str -> str
Harness rules:
  - SKILL.md body under 500 lines
  - relative links in SKILL.md resolve and stay one level deep
  - description says when to use the skill ("Use when")
  - vendored shared files are identical to their canonical source
  - every `<this-skill-dir>/...` path in SKILL.md, and every check_pm import, ships with the skill
"""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
from check_pm import check as check_pm_folder, load_yaml, split_frontmatter  # noqa: E402

ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MAX_LINES = 500
SKILL_DIR_REF = re.compile(r"<this-skill-dir>/([\w./-]+\.\w+)")

# canonical file -> skill-relative destinations
VENDORED = {
    "schemas/artifact-frontmatter.md": [
        "pm-start/templates/CONVENTIONS.md",
        "product-map/templates/CONVENTIONS.md",
    ],
    "schemas/config.yaml": [
        "pm-start/templates/config.yaml",
        "product-map/templates/config.yaml",
    ],
    "scripts/check_pm.py": [
        "pm-start/scripts/check_pm.py",
        "product-map/scripts/check_pm.py",
        "product-map-refresh/scripts/check_pm.py", "ask-the-product/scripts/check_pm.py",
        "prd/scripts/check_pm.py", "tech-impact/scripts/check_pm.py",
        "epics-and-stories/scripts/check_pm.py", "test-plan/scripts/check_pm.py",
        "acceptance-check/scripts/check_pm.py", "ai-evals/scripts/check_pm.py",
        "work-sync/scripts/check_pm.py", "status-update/scripts/check_pm.py",
        "release-notes/scripts/check_pm.py", "research-synthesis/scripts/check_pm.py",
        "design-brief/scripts/check_pm.py", "design-review/scripts/check_pm.py",
        "research-plan/scripts/check_pm.py", "competitive-scan/scripts/check_pm.py",
    ],
    "scripts/pm_status.py": [
        "pm-start/scripts/pm_status.py",
        "status-update/scripts/pm_status.py",
    ],
}


def sync() -> None:
    for src, dests in VENDORED.items():
        for dest in dests:
            target = ROOT / "skills" / dest
            if target.parent.parent.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / src, target)
                print(f"synced {src} -> skills/{dest}")


def validate_skill(skill_dir: Path) -> list[str]:
    errs: list[str] = []
    rel = skill_dir.relative_to(ROOT)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{rel}: missing SKILL.md"]
    text = skill_md.read_text()
    raw, body = split_frontmatter(text)
    if raw is None:
        return [f"{rel}/SKILL.md: missing YAML frontmatter"]
    fm = load_yaml(raw) or {}

    extra = set(fm) - ALLOWED
    if extra:
        errs.append(f"{rel}: non-spec frontmatter fields {sorted(extra)}")

    name = fm.get("name")
    if not name:
        errs.append(f"{rel}: missing `name`")
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            errs.append(f"{rel}: invalid name `{name}`")
        if name != skill_dir.name:
            errs.append(f"{rel}: name `{name}` must match folder `{skill_dir.name}`")

    desc = fm.get("description") or ""
    if not desc:
        errs.append(f"{rel}: missing `description`")
    elif len(desc) > 1024:
        errs.append(f"{rel}: description is {len(desc)} chars (max 1024)")
    elif "use when" not in desc.lower():
        errs.append(f"{rel}: description should say when to use it (include 'Use when')")

    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not 1 <= len(comp) <= 500):
        errs.append(f"{rel}: compatibility must be a 1-500 char string")

    meta = fm.get("metadata")
    if meta is not None and (
        not isinstance(meta, dict) or not all(isinstance(v, str) for v in meta.values())
    ):
        errs.append(f"{rel}: metadata must map strings to strings (quote numbers)")

    n_lines = len(text.splitlines())
    if n_lines > MAX_LINES:
        errs.append(f"{rel}/SKILL.md: {n_lines} lines (max {MAX_LINES})")

    in_code = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            clean = target.split("#")[0]
            if clean.startswith("pm/") or clean.startswith("../"):
                continue
            if not (skill_dir / clean).exists():
                errs.append(f"{rel}/SKILL.md: broken link `{target}`")
            elif clean.count("/") > 1:
                errs.append(f"{rel}/SKILL.md: link `{target}` is more than one level deep")

    for ref in sorted(set(SKILL_DIR_REF.findall(body))):
        if not (skill_dir / ref).exists():
            errs.append(f"{rel}/SKILL.md: references `<this-skill-dir>/{ref}`, which does not exist")
    for script in sorted(skill_dir.glob("scripts/*.py")):
        if "from check_pm import" in script.read_text() and not (skill_dir / "scripts/check_pm.py").exists():
            errs.append(f"{rel}/{script.relative_to(skill_dir)}: imports check_pm but the skill "
                        "does not ship scripts/check_pm.py (add it to VENDORED)")
    return errs


def validate_vendored() -> list[str]:
    errs = []
    for src, dests in VENDORED.items():
        for dest in dests:
            target = ROOT / "skills" / dest
            if not target.parent.parent.exists():
                continue
            if not target.exists():
                errs.append(f"skills/{dest}: missing vendored copy of {src} (run --sync)")
            elif not filecmp.cmp(ROOT / src, target, shallow=False):
                errs.append(f"skills/{dest}: out of sync with {src} (run --sync)")
    return errs


def validate_examples() -> list[str]:
    errs = []
    for pm_dir in sorted((ROOT / "examples").glob("*/pm")):
        rep = check_pm_folder(pm_dir, repo=None, strict=True)
        errs.extend(f"{pm_dir.relative_to(ROOT)}: {e}" for e in rep.errors)
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sync", action="store_true", help="copy canonical shared files into skills first")
    args = ap.parse_args()
    if args.sync:
        sync()

    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()) if (ROOT / "skills").exists() else []
    errors: list[str] = []
    for skill in skills:
        errors.extend(validate_skill(skill))
    errors.extend(validate_vendored())
    errors.extend(validate_examples())

    for e in errors:
        print(e)
    print(f"\nChecked {len(skills)} skill(s): {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
