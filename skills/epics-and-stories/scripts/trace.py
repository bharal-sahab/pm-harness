#!/usr/bin/env python3
"""Check that an initiative's stories cover its PRD, and that every story is testable.

Usage:
  python3 trace.py pm/initiatives/<slug> [--json]

Reads the requirement table in prd.md (rows starting with `| R<n> |`), the epics in
epics/, and the stories in stories/. Reports:
  - a matrix of requirement -> stories
  - must-have requirements with no story (error); should/could ones (warning)
  - stories that cite unknown requirements or epics (error)
  - stories with no requirements (warning) or no Given/When/Then criteria (error)
Exit code 1 when there are errors.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import as_list, load_yaml, split_frontmatter  # noqa: E402

REQ_ROW = re.compile(r"^\|\s*(R\d+)\s*\|\s*(.+?)\s*\|\s*(must|should|could|won't|wont)\s*\|", re.I | re.M)
AC_HEAD = re.compile(r"^\*\*(AC\d+)\b|^#{2,4}\s+(AC\d+)\b", re.M)


def read(path: Path) -> tuple[dict, str]:
    raw, body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    return ((load_yaml(raw) if raw else None) or {}), body


def trace(folder: Path) -> dict:
    prd = folder / "prd.md"
    reqs = {}
    if prd.exists():
        _, body = read(prd)
        for m in REQ_ROW.finditer(body):
            reqs[m.group(1)] = {"text": m.group(2), "priority": m.group(3).lower(), "stories": []}

    epics = {}
    for f in sorted((folder / "epics").glob("*.md")):
        meta, _ = read(f)
        epics[str(meta.get("id"))] = {"title": meta.get("title"), "stories": 0}

    errors, warnings, stories = [], [], []
    for f in sorted((folder / "stories").glob("*.md")):
        meta, body = read(f)
        sid = str(meta.get("id", f.stem))
        story_reqs = [str(r) for r in as_list(meta.get("requirements"))]
        acs = [a or b for a, b in AC_HEAD.findall(body)]
        has_gwt = all(w in body for w in ("Given", "When", "Then"))
        stories.append({"id": sid, "title": meta.get("title"), "epic": meta.get("epic"),
                        "requirements": story_reqs, "acceptance_criteria": len(acs),
                        "status": meta.get("status")})
        epic = str(meta.get("epic")) if meta.get("epic") else None
        if epic and epic not in epics:
            errors.append(f"{sid}: epic {epic} not found in epics/")
        elif epic:
            epics[epic]["stories"] += 1
        if not story_reqs:
            warnings.append(f"{sid}: no `requirements` listed")
        for r in story_reqs:
            if r in reqs:
                reqs[r]["stories"].append(sid)
            elif reqs:
                errors.append(f"{sid}: requirement {r} is not in prd.md")
        if not acs or not has_gwt:
            errors.append(f"{sid}: needs numbered acceptance criteria (AC1, ...) in Given/When/Then form")

    if not prd.exists():
        warnings.append("No prd.md: cannot check requirement coverage")
    for rid, r in reqs.items():
        if not r["stories"] and r["priority"] not in ("won't", "wont"):
            (errors if r["priority"] == "must" else warnings).append(
                f"{rid} ({r['priority']}) has no story: {r['text'][:80]}")
    for eid, e in epics.items():
        if e["stories"] == 0:
            warnings.append(f"{eid}: epic has no stories")

    return {"requirements": reqs, "epics": epics, "stories": stories,
            "errors": errors, "warnings": warnings}


def render(t: dict) -> str:
    out = ["# Traceability", "", "| Req | Priority | Stories |", "|-----|----------|---------|"]
    for rid, r in t["requirements"].items():
        out.append(f"| {rid} | {r['priority']} | {', '.join(r['stories']) or '**none**'} |")
    out += ["", f"{len(t['stories'])} stories in {len(t['epics'])} epics, "
            f"{sum(s['acceptance_criteria'] for s in t['stories'])} acceptance criteria.", ""]
    out += [f"ERROR   {e}" for e in t["errors"]] + [f"WARN    {w}" for w in t["warnings"]]
    out.append(f"\n{len(t['errors'])} error(s), {len(t['warnings'])} warning(s)")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("initiative_dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    result = trace(Path(args.initiative_dir))
    print(json.dumps(result, indent=2, default=str) if args.json else render(result))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
