#!/usr/bin/env python3
"""Report the state of a pm/ folder and suggest the next harness skill.

Usage:
  python3 pm_status.py [pm-dir] [--repo DIR] [--json]

Reports whether pm/ is set up, how fresh the product knowledge base is, and where each
initiative stands in the lifecycle (research -> design -> definition -> build -> QA ->
release), with the skill to run next.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import load_yaml, split_frontmatter  # noqa: E402

STALE_DAYS = 30

# (artifact present, stage reached, skill(s) to run next). Order is the lifecycle.
STAGES = [
    ("research-plan.md", "Research planned", "research-synthesis (after the interviews)"),
    ("research.md", "Research synthesized", "design-brief, or prd for small changes"),
    ("brief.md", "Problem framed", "design-brief, or prd for small changes"),
    ("design.md", "Designed", "design-review, then prd"),
    ("design-review.md", "Design reviewed", "prd"),
    ("prd.md", "Defined", "tech-impact"),
    ("tech-impact.md", "Impact assessed", "epics-and-stories"),
    ("stories", "Stories written", "work-sync to push to the tracker, and test-plan"),
    ("test-plan.md", "Test planned", "acceptance-check when the code is ready"),
    ("acceptance", "Verifying", "release-notes once acceptance passes"),
    ("release.md", "Released", "status-update, then product-map-refresh"),
]


def frontmatter(path: Path) -> dict:
    try:
        raw, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return {}
    return (load_yaml(raw) if raw else None) or {}


def git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                             text=True, timeout=20)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def parse_date(value) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def knowledge_base(pm_dir: Path, repo: Path) -> dict:
    product = pm_dir / "product"
    meta_path = product / "_meta.yaml"
    if not meta_path.exists():
        return {"exists": False}
    meta = load_yaml(meta_path.read_text()) or {}
    sha = str(meta.get("source_commit") or "")
    built = parse_date(meta.get("refreshed_at") or meta.get("generated_at"))
    age = (dt.date.today() - built).days if built else None

    head = git(repo, "rev-parse", "HEAD")
    behind = changed = None
    if head and sha and not sha.startswith("<"):
        count = git(repo, "rev-list", "--count", f"{sha}..HEAD")
        behind = int(count) if count and count.isdigit() else None
        files = git(repo, "diff", "--name-only", sha, "HEAD")
        changed = len(files.splitlines()) if files else (0 if files == "" else None)

    if behind is not None:
        stale = behind > 0
    else:
        stale = age is not None and age > STALE_DAYS

    oq = product / "open-questions.md"
    open_questions = 0
    if oq.exists():
        rows = [ln for ln in oq.read_text().splitlines() if re.match(r"^\|\s*\d+\s*\|", ln)]
        open_questions = sum(1 for r in rows if "answered" not in r.lower())
    faq = product / "faq.md"
    faq_count = len(re.findall(r"(?m)^## ", faq.read_text())) if faq.exists() else 0
    caps = product / "capabilities.md"
    cap_count = len(re.findall(r"(?m)^### CAP-", caps.read_text())) if caps.exists() else 0

    return {
        "exists": True,
        "pages": len(list(product.rglob("*.md"))),
        "capabilities": cap_count,
        "source_commit": sha[:12],
        "head": head[:12] if head else None,
        "last_built": str(built) if built else None,
        "age_days": age,
        "commits_behind": behind,
        "files_changed": changed,
        "stale": stale,
        "open_questions": open_questions,
        "faq_entries": faq_count,
    }


def initiative(folder: Path) -> dict:
    readme = frontmatter(folder / "README.md")
    present = [name for name, _, _ in STAGES if (folder / name).exists()]
    stage, next_skill = "Started", "research-plan, or prd if the problem is already clear"
    for name, label, nxt in STAGES:
        if name in present:
            stage, next_skill = label, nxt

    stories = sorted((folder / "stories").glob("*.md")) if (folder / "stories").is_dir() else []
    by_status: dict[str, int] = {}
    unsynced = 0
    for s in stories:
        fm = frontmatter(s)
        by_status[str(fm.get("status", "unknown"))] = by_status.get(str(fm.get("status", "unknown")), 0) + 1
        tracker = fm.get("tracker") or {}
        if not (isinstance(tracker, dict) and tracker.get("key")):
            unsynced += 1

    return {
        "slug": folder.name,
        "title": readme.get("title", folder.name),
        "status": readme.get("status", "unknown"),
        "owner": readme.get("owner"),
        "updated": str(readme.get("updated", "")),
        "artifacts": present,
        "stage": stage,
        "next": next_skill,
        "stories": len(stories),
        "stories_by_status": by_status,
        "stories_not_in_tracker": unsynced,
    }


def status(pm_dir: Path, repo: Path) -> dict:
    if not pm_dir.is_dir():
        return {"pm_exists": False, "recommendations": [
            "Set up pm/ (pm-start does this), then run product-map to build the knowledge base."]}
    config = load_yaml((pm_dir / "config.yaml").read_text()) if (pm_dir / "config.yaml").exists() else None
    tracker = ((config or {}).get("tracker") or {}).get("system")
    kb = knowledge_base(pm_dir, repo)
    inits_dir = pm_dir / "initiatives"
    inits = [initiative(f) for f in sorted(inits_dir.iterdir()) if f.is_dir()] if inits_dir.is_dir() else []

    recs = []
    if not (pm_dir / "CONVENTIONS.md").exists() or config is None:
        recs.append("Finish setup: pm/CONVENTIONS.md or pm/config.yaml is missing.")
    if not kb["exists"]:
        recs.append("Run product-map: there is no product knowledge base yet.")
    elif kb["stale"]:
        why = (f"{kb['commits_behind']} commits behind" if kb["commits_behind"]
               else f"{kb['age_days']} days old")
        recs.append(f"Run product-map-refresh: the knowledge base is {why}.")
    for i in inits:
        if i["status"] in ("done", "superseded"):
            continue
        recs.append(f"{i['slug']}: at '{i['stage']}'. Next: {i['next']}.")
        if tracker and i["stories_not_in_tracker"]:
            recs.append(f"{i['slug']}: {i['stories_not_in_tracker']} stories are not in "
                        f"{tracker} yet. Run work-sync.")
    if kb.get("exists") and not inits:
        recs.append("Start an initiative: research-plan to explore a problem, or prd if it is already clear.")

    return {
        "pm_exists": True,
        "product_name": (config or {}).get("product_name"),
        "tracker": tracker,
        "knowledge_base": kb,
        "initiatives": inits,
        "recommendations": recs,
    }


def render(s: dict) -> str:
    if not s["pm_exists"]:
        return "# PM status\n\nNo `pm/` folder yet.\n\n## Next\n\n- " + s["recommendations"][0] + "\n"
    out = [f"# PM status: {s.get('product_name') or 'unnamed product'}", ""]
    kb = s["knowledge_base"]
    out.append("## Product knowledge base")
    out.append("")
    if not kb["exists"]:
        out.append("Not built yet.")
    else:
        fresh = "**stale**" if kb["stale"] else "current"
        behind = (f", {kb['commits_behind']} commits and {kb['files_changed']} files behind HEAD"
                  if kb["commits_behind"] is not None else "")
        out.append(f"- {kb['pages']} pages, {kb['capabilities']} capabilities; {fresh}"
                   f" (built from `{kb['source_commit']}` on {kb['last_built']}{behind})")
        out.append(f"- {kb['open_questions']} open questions, {kb['faq_entries']} answered FAQ entries")
    out += ["", "## Initiatives", ""]
    if not s["initiatives"]:
        out.append("None yet.")
    else:
        out.append("| Initiative | Status | Stage | Stories | Next skill |")
        out.append("|------------|--------|-------|---------|------------|")
        for i in s["initiatives"]:
            st = ", ".join(f"{n} {k}" for k, n in sorted(i["stories_by_status"].items())) or "-"
            out.append(f"| {i['slug']} | {i['status']} | {i['stage']} | {st} | {i['next']} |")
    out += ["", f"Tracker: {s['tracker'] or 'none (markdown only)'}", "", "## Next", ""]
    out += [f"- {r}" for r in s["recommendations"]] or ["- Nothing pending."]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pm_dir", nargs="?", default="pm")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    result = status(Path(args.pm_dir), Path(args.repo))
    print(json.dumps(result, indent=2, default=str) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
