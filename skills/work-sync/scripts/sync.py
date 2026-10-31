#!/usr/bin/env python3
"""Plan and record syncs between pm/ epics and stories and a tracker (Jira or Linear).

Markdown in pm/ owns the content (title, description, acceptance criteria). The tracker
owns workflow status. This script never calls a tracker; the agent does that through
the connected MCP server, then records the result here.

Usage:
  sync.py plan   <initiative-dir> [--system jira|linear] [--json]
  sync.py record <artifact.md> --system S --key K [--url U] [--status S] [--content-synced]
  sync.py csv    <initiative-dir> > import.csv     # Jira CSV import, when no MCP server

plan    Lists each epic and story with the action needed: create (no key yet), update
        (content changed since the last sync), or none. Includes the ready-to-send title,
        description, type, priority, labels, and parent.
record  Writes the tracker block into the artifact's frontmatter. Use --content-synced
        after pushing content, so the next plan knows it is up to date. Use --status
        when pulling a status back; the harness status is updated from the mapping.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import load_yaml, split_frontmatter  # noqa: E402

PRIORITY = {
    "jira": {"p0": "Highest", "p1": "High", "p2": "Medium", "p3": "Low"},
    "linear": {"p0": "1 (Urgent)", "p1": "2 (High)", "p2": "3 (Medium)", "p3": "4 (Low)"},
}
# Tracker status category -> harness status. Matching is by lowercase substring.
STATUS_MAP = [
    (("cancel", "won't", "wont", "duplicate", "obsolete"), "superseded"),
    (("done", "closed", "resolved", "released", "complete"), "done"),
    (("progress", "review", "qa", "testing", "started", "doing"), "in-progress"),
    (("backlog", "to do", "todo", "open", "triage", "selected", "ready", "unstarted"), "approved"),
]
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def read(path: Path) -> tuple[dict, str, str]:
    text = path.read_text(encoding="utf-8")
    raw, body = split_frontmatter(text)
    return ((load_yaml(raw) if raw else None) or {}), body, text


def content_hash(meta: dict, body: str) -> str:
    basis = "\n".join([str(meta.get("title", "")), str(meta.get("priority", "")), body.strip()])
    return hashlib.sha256(basis.encode()).hexdigest()[:12]


def to_tracker_markdown(body: str, path: Path, pm_root: Path) -> str:
    """Rewrite relative links as repo paths so they make sense outside the repo."""
    def repl(m):
        target = m.group(2)
        if re.match(r"^[a-z]+://|^#", target):
            return m.group(0)
        resolved = (path.parent / target.split("#")[0]).resolve()
        try:
            rel = resolved.relative_to(pm_root.parent)
        except ValueError:
            rel = Path(target)
        return f"{m.group(1)} (`{rel}`)"
    body = re.sub(r"^#\s+.*\n+", "", body.strip(), count=1)
    return LINK_RE.sub(repl, body)


def find_pm_root(path: Path) -> Path:
    for parent in [path, *path.parents]:
        if parent.name == "pm":
            return parent
    return path


def items(folder: Path, system: str | None):
    pm_root = find_pm_root(folder.resolve())
    files = sorted((folder / "epics").glob("*.md")) + sorted((folder / "stories").glob("*.md"))
    epic_keys = {}
    for f in files:
        meta, body, _ = read(f)
        if meta.get("type") == "epic":
            epic_keys[meta.get("id")] = (meta.get("tracker") or {}).get("key")
    out = []
    for f in files:
        meta, body, _ = read(f)
        if meta.get("status") == "superseded" and not (meta.get("tracker") or {}).get("key"):
            continue
        tracker = meta.get("tracker") or {}
        h = content_hash(meta, body)
        if not tracker.get("key"):
            action = "create"
        elif tracker.get("synced_hash") != h:
            action = "update"
        else:
            action = "none"
        kind = "Epic" if meta.get("type") == "epic" else "Story"
        rel = f.resolve().relative_to(pm_root.parent)
        desc = to_tracker_markdown(body, f.resolve(), pm_root)
        desc += (f"\n\n---\nSource: `{rel}` ({meta.get('id')}). Edit the source file; "
                 f"this item is synced by the PM harness.")
        epic = meta.get("epic")
        out.append({
            "file": str(f), "id": meta.get("id"), "action": action, "type": kind,
            "key": tracker.get("key"), "title": meta.get("title"),
            "priority": PRIORITY.get(system or "", {}).get(str(meta.get("priority")), meta.get("priority")),
            "labels": [str(meta.get("initiative")), "pm-harness"],
            "parent_id": epic, "parent_key": epic_keys.get(epic) if epic else None,
            "status": meta.get("status"), "hash": h, "description": desc,
        })
    return out


def cmd_plan(args) -> int:
    plan = items(Path(args.initiative_dir), args.system)
    if args.json:
        print(json.dumps(plan, indent=2, default=str))
        return 0
    counts = {a: sum(1 for p in plan if p["action"] == a) for a in ("create", "update", "none")}
    print(f"# Sync plan: {Path(args.initiative_dir).name}\n")
    print(f"{counts['create']} to create, {counts['update']} to update, {counts['none']} unchanged.\n")
    print("| Action | ID | Type | Key | Parent | Title |")
    print("|--------|----|------|-----|--------|-------|")
    for p in plan:
        parent = p["parent_key"] or (f"{p['parent_id']} (create first)" if p["parent_id"] else "-")
        print(f"| {p['action']} | {p['id']} | {p['type']} | {p['key'] or '-'} | {parent} | {p['title']} |")
    print("\nRun with --json for the full payloads (description, priority, labels).")
    return 0


def harness_status(tracker_status: str) -> str | None:
    s = tracker_status.lower()
    for words, status in STATUS_MAP:
        if any(w in s for w in words):
            return status
    return None


def cmd_record(args) -> int:
    path = Path(args.artifact)
    meta, body, text = read(path)
    tracker = dict(meta.get("tracker") or {})
    tracker.update({"system": args.system, "key": args.key})
    if args.url:
        tracker["url"] = args.url
    if args.status:
        tracker["status"] = args.status
    if args.content_synced:
        tracker["synced_hash"] = content_hash(meta, body)
    tracker["synced_at"] = dt.date.today().isoformat()

    end = text.find("\n---", 3)
    fm = text[3:end].strip("\n").splitlines()
    kept, skip = [], False
    for line in fm:
        if re.match(r"^tracker:", line):
            skip = True
            continue
        if skip and (line.startswith(" ") or line.startswith("\t")):
            continue
        skip = False
        kept.append(line)
    order = ["system", "key", "url", "status", "synced_at", "synced_hash"]
    kept.append("tracker:")
    for k in order + [k for k in tracker if k not in order]:
        if k in tracker and tracker[k] is not None:
            kept.append(f"  {k}: {tracker[k]}")

    new_status = harness_status(args.status) if args.status else None
    if new_status:
        kept = [f"status: {new_status}" if re.match(r"^status:", ln) else ln for ln in kept]
    path.write_text("---\n" + "\n".join(kept) + text[end:], encoding="utf-8")
    note = f"; status -> {new_status}" if new_status else ""
    print(f"Recorded {args.system} {args.key} on {meta.get('id')}{note}")
    return 0


def cmd_csv(args) -> int:
    plan = items(Path(args.initiative_dir), "jira")
    w = csv.writer(sys.stdout)
    w.writerow(["Issue ID", "Parent ID", "Issue Type", "Summary", "Description", "Priority", "Labels"])
    for p in plan:
        if p["action"] != "create":
            continue
        w.writerow([p["id"], p["parent_id"] or "", p["type"], p["title"], p["description"],
                    p["priority"], " ".join(l.replace(" ", "-") for l in p["labels"])])
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("initiative_dir")
    p.add_argument("--system", choices=["jira", "linear"])
    p.add_argument("--json", action="store_true")
    r = sub.add_parser("record")
    r.add_argument("artifact")
    r.add_argument("--system", required=True, choices=["jira", "linear"])
    r.add_argument("--key", required=True)
    r.add_argument("--url")
    r.add_argument("--status")
    r.add_argument("--content-synced", action="store_true")
    c = sub.add_parser("csv")
    c.add_argument("initiative_dir")
    args = ap.parse_args(argv)
    return {"plan": cmd_plan, "record": cmd_record, "csv": cmd_csv}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
