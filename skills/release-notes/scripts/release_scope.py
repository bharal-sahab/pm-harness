#!/usr/bin/env python3
"""Work out what an initiative actually shipped in a release, before writing notes.

Usage:
  python3 release_scope.py pm/initiatives/<slug> [--repo DIR --from REF --to REF] [--json]
  python3 release_scope.py pm/initiatives/<slug> --changed-files FILE [--json]

A story counts as shipped when its status is `done` or its tracker status (as recorded
by work-sync) is a done-like status. With a git range (or a file listing changed paths,
one per line), the script also checks each story's `code_refs` against the files changed
in the release and flags:
  - stories marked done whose code did not change in this release (shipped earlier, or
    the code_refs are wrong);
  - stories not marked done whose code did change (maybe shipped, maybe partial).
It also lists the PRD requirements covered by shipped stories and the latest
acceptance-check recommendations.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import load_yaml, split_frontmatter  # noqa: E402

DONE_LIKE = {"done", "closed", "resolved", "released", "shipped", "complete", "completed"}


def read(path: Path) -> tuple[dict, str]:
    raw, body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    return ((load_yaml(raw) if raw else None) or {}), body


def changed_files(args) -> list[str] | None:
    if args.changed_files:
        lines = Path(args.changed_files).read_text().splitlines()
        return [ln.split("\t")[-1].strip() for ln in lines if ln.strip()]
    if args.from_ref:
        cmd = ["git", "-C", str(args.repo), "diff", "--name-only", args.from_ref, args.to_ref]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            sys.exit(f"git failed: {exc}")
        if out.returncode != 0:
            sys.exit(f"git failed: {out.stderr.strip()}")
        return [ln for ln in out.stdout.splitlines() if ln]
    return None


def touches(ref: str, files: list[str]) -> list[str]:
    ref = ref.rstrip("/")
    return [f for f in files if f == ref or f.startswith(ref + "/")]


def scope(folder: Path, files: list[str] | None) -> dict:
    stories = []
    for path in sorted((folder / "stories").glob("*.md")) if (folder / "stories").is_dir() else []:
        fm, _ = read(path)
        tracker = fm.get("tracker") if isinstance(fm.get("tracker"), dict) else {}
        tracker_status = str(tracker.get("status") or "")
        shipped = str(fm.get("status")) == "done" or tracker_status.lower() in DONE_LIKE
        refs = [str(r) for r in (fm.get("code_refs") or [])]
        hits = sorted({f for r in refs for f in touches(r, files)}) if files is not None else None
        stories.append({
            "id": fm.get("id"), "title": fm.get("title"), "status": fm.get("status"),
            "tracker_key": tracker.get("key"), "tracker_status": tracker_status or None,
            "requirements": [str(r) for r in (fm.get("requirements") or [])],
            "shipped": shipped, "code_refs": refs, "changed_in_release": hits,
        })

    flags = []
    if files is not None:
        for s in stories:
            if s["shipped"] and s["code_refs"] and not s["changed_in_release"]:
                flags.append(f"{s['id']} is marked done but none of its code_refs changed in this release.")
            if not s["shipped"] and s["changed_in_release"]:
                flags.append(f"{s['id']} is not marked done but its code changed in this release.")
            if s["shipped"] and not s["code_refs"]:
                flags.append(f"{s['id']} is marked done but has no code_refs to check.")

    acceptance = []
    for path in sorted((folder / "acceptance").glob("*.md")) if (folder / "acceptance").is_dir() else []:
        fm, body = read(path)
        m = re.search(r"\*\*Recommendation:\*\*\s*(.+?)(?=\n\s*\n|\s\*\*[A-Z][^*\n]*:\*\*|\Z)", body, re.S)
        acceptance.append({"path": path.relative_to(folder).as_posix(), "updated": str(fm.get("updated")),
                           "recommendation": " ".join(m.group(1).split()) if m else None})

    shipped = [s for s in stories if s["shipped"]]
    return {
        "initiative": folder.name,
        "files_in_release": len(files) if files is not None else None,
        "shipped": [s["id"] for s in shipped],
        "not_shipped": [s["id"] for s in stories if not s["shipped"]],
        "requirements_shipped": sorted({r for s in shipped for r in s["requirements"]},
                                       key=lambda r: int(r[1:]) if r[1:].isdigit() else 999),
        "stories": stories,
        "flags": flags,
        "acceptance": acceptance,
    }


def render(r: dict) -> str:
    out = [f"# Release scope: {r['initiative']}", ""]
    if r["files_in_release"] is not None:
        out.append(f"Files changed in the release: {r['files_in_release']}")
    out.append(f"Shipped stories: {len(r['shipped'])} of {len(r['stories'])}")
    out.append(f"Requirements covered by shipped stories: {', '.join(r['requirements_shipped']) or 'none'}")
    out += ["", "## Stories", ""]
    for s in r["stories"]:
        mark = "shipped" if s["shipped"] else "not shipped"
        tracker = f", tracker {s['tracker_key']}: {s['tracker_status']}" if s["tracker_key"] else ""
        code = ""
        if s["changed_in_release"] is not None:
            code = f", {len(s['changed_in_release'])} of its files changed in release"
        out.append(f"- {s['id']} [{s['status']}{tracker}] {mark}{code}: {s['title']}")
    out += ["", "## Check before announcing", ""]
    out += [f"- {f}" for f in r["flags"]] or ["Nothing flagged."]
    out += ["", "## Acceptance checks", ""]
    out += [f"- {a['path']} ({a['updated']}): {a['recommendation'] or 'no recommendation line'}"
            for a in r["acceptance"]] or ["None found. Consider running acceptance-check first."]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("initiative_dir", type=Path)
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--from", dest="from_ref", help="previous release tag or commit")
    ap.add_argument("--to", dest="to_ref", default="HEAD", help="this release tag or commit")
    ap.add_argument("--changed-files", help="file listing changed paths, one per line")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not args.initiative_dir.is_dir():
        print(f"Not a folder: {args.initiative_dir}", file=sys.stderr)
        return 2
    result = scope(args.initiative_dir, changed_files(args))
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
