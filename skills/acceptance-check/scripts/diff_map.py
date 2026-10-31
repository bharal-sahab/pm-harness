#!/usr/bin/env python3
"""Summarize a code diff against an initiative's stories, for an acceptance check.

Usage:
  diff_map.py <initiative-dir> --base <ref> [--head HEAD] [--repo .] [--json]
  diff_map.py <initiative-dir> --diff-file pr.diff [--json]

Get a PR's diff without git history with, for example, `gh pr diff 123 > pr.diff`.

Reports, for each changed file: its kind (test, migration, API, UI, types, config, docs,
code), lines added and removed, the added line ranges (to cite as path:line), and which
stories list it in `code_refs` (exact file or same folder). Also lists:
  - changed files no story mentions (possible scope creep, or missing code_refs)
  - stories none of whose code_refs were touched (possibly not implemented in this diff)
  - lines changed or removed in API and type files (check whether consumers rely on them)
  - test files added or changed
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
from check_pm import as_list, load_yaml, split_frontmatter  # noqa: E402

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
KINDS = [
    ("test", re.compile(r"(^|/)(__tests__|tests?|spec|integration-tests)/|\.(spec|test)\.\w+$|_test\.\w+$")),
    ("migration", re.compile(r"(^|/)migrations?/|\.sql$")),
    ("docs", re.compile(r"\.(md|mdx)$")),
    ("config", re.compile(r"(^|/)(feature-flags|config)/|\.(ya?ml|json|toml|env)$")),
    ("types", re.compile(r"(^|/)types?/|\.d\.ts$")),
    ("api", re.compile(r"(^|/)(api|routes?|controllers?|handlers?|endpoints?)/")),
    ("ui", re.compile(r"\.(tsx|jsx|vue|svelte|swift|kt|dart)$|(^|/)(components|screens|pages|views)/")),
]


def kind_of(path: str) -> str:
    for name, rx in KINDS:
        if rx.search(path):
            return name
    return "code"


def parse_diff(text: str) -> dict[str, dict]:
    files: dict[str, dict] = {}
    cur = None
    new_line = 0
    for line in text.splitlines():
        if line.startswith("diff --git "):
            cur = None
            continue
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path == "/dev/null":
                cur = files.setdefault(prev_path, {"added": 0, "removed": 0, "ranges": [],
                                                   "status": "deleted", "removed_lines": []})
                continue
            path = path[2:] if path.startswith("b/") else path
            status = "added" if prev_path == "/dev/null" else "modified"
            cur = files.setdefault(path, {"added": 0, "removed": 0, "ranges": [],
                                          "status": status, "removed_lines": []})
            continue
        if line.startswith("--- "):
            p = line[4:].strip()
            prev_path = p[2:] if p.startswith("a/") else p
            continue
        if cur is None:
            continue
        m = HUNK.match(line)
        if m:
            new_line = int(m.group(1))
            run_start = None
            continue
        if line.startswith("+"):
            cur["added"] += 1
            if cur["ranges"] and cur["ranges"][-1][1] == new_line - 1:
                cur["ranges"][-1][1] = new_line
            else:
                cur["ranges"].append([new_line, new_line])
            new_line += 1
        elif line.startswith("-"):
            cur["removed"] += 1
            cur["removed_lines"].append(line[1:].strip())
        else:
            new_line += 1
    return files


def load_stories(folder: Path) -> dict[str, list[str]]:
    stories = {}
    for f in sorted((folder / "stories").glob("*.md")):
        raw, _ = split_frontmatter(f.read_text(encoding="utf-8"))
        meta = (load_yaml(raw) if raw else None) or {}
        if meta.get("status") == "superseded":
            continue
        stories[str(meta.get("id", f.stem))] = [str(r).split(":")[0] for r in as_list(meta.get("code_refs"))]
    return stories


def analyze(folder: Path, files: dict[str, dict]) -> dict:
    stories = load_stories(folder)
    touched_by_story = {sid: [] for sid in stories}
    rows = []
    for path, info in sorted(files.items()):
        matches = []
        for sid, refs in stories.items():
            for ref in refs:
                if path == ref:
                    matches.append((sid, "file"))
                    touched_by_story[sid].append(path)
                    break
                if "/" in ref and path.rsplit("/", 1)[0] == ref.rsplit("/", 1)[0]:
                    matches.append((sid, "folder"))
                    break
        kind = kind_of(path)
        removed_api = [l for l in info["removed_lines"] if l and not l.startswith(("//", "*", "/*"))]
        rows.append({
            "path": path, "kind": kind, "status": info["status"],
            "added": info["added"], "removed": info["removed"],
            "added_ranges": [f"{a}-{b}" if a != b else str(a) for a, b in info["ranges"]],
            "stories": [f"{s} ({how})" for s, how in matches],
            "possible_breaking": kind in ("api", "types") and bool(removed_api),
            "removed_lines": removed_api[:8] if kind in ("api", "types") else [],
        })
    return {
        "files": rows,
        "unmatched_files": [r["path"] for r in rows if not r["stories"] and r["kind"] not in ("test", "docs")],
        "stories_not_touched": [s for s, paths in touched_by_story.items() if not paths],
        "tests_changed": [r["path"] for r in rows if r["kind"] == "test"],
        "possible_breaking": [r["path"] for r in rows if r["possible_breaking"]],
    }


def render(r: dict) -> str:
    out = ["# Diff map", "", "| File | Kind | Status | +/- | Added lines | Stories |",
           "|------|------|--------|-----|-------------|---------|"]
    for f in r["files"]:
        rng = ", ".join(f["added_ranges"][:6]) + (" ..." if len(f["added_ranges"]) > 6 else "")
        out.append(f"| `{f['path']}` | {f['kind']} | {f['status']} | +{f['added']}/-{f['removed']} "
                   f"| {rng or '-'} | {', '.join(f['stories']) or '-'} |")
    def section(title, items, fmt=lambda x: f"- `{x}`"):
        out.extend(["", f"## {title}", ""] + ([fmt(i) for i in items] or ["None."]))
    section("Changed files no story mentions", r["unmatched_files"])
    section("Stories whose code_refs were not touched", r["stories_not_touched"], lambda s: f"- {s}")
    section("Tests added or changed", r["tests_changed"])
    out.extend(["", "## API and type lines changed or removed (check consumers)", ""])
    flagged = [f for f in r["files"] if f["removed_lines"]]
    out.extend([f"- `{f['path']}`: " + "; ".join(f"`{l}`" for l in f["removed_lines"]) for f in flagged]
               or ["None."])
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("initiative_dir")
    ap.add_argument("--base")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--diff-file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.diff_file:
        text = Path(args.diff_file).read_text(encoding="utf-8", errors="replace")
    elif args.base:
        try:
            text = subprocess.run(["git", "-C", args.repo, "diff", f"{args.base}...{args.head}"],
                                  capture_output=True, text=True, check=True).stdout
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            sys.exit(f"git diff failed ({exc}). Save the diff to a file and use --diff-file.")
    else:
        sys.exit("Pass --base <ref> or --diff-file <file>.")
    result = analyze(Path(args.initiative_dir), parse_diff(text))
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
