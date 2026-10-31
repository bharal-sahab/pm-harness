#!/usr/bin/env python3
"""Collect the facts a status update is written from, for one initiative folder.

Usage:
  python3 initiative_facts.py pm/initiatives/<slug> [--since YYYY-MM-DD] [--json]

Reports: artifacts and which changed since the last status update (or --since), stories
by status with tracker keys and tracker statuses, open questions still unanswered, the
latest acceptance-check recommendations, decisions listed in the README, and the path of
the previous status update. It only reads files; tracker statuses are as last recorded by
work-sync.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import load_yaml, split_frontmatter  # noqa: E402

QUESTION_ROW = re.compile(r"^\|\s*(Q\d+)\s*\|\s*(.+?)\s*\|(.*)$")
CLOSED = re.compile(r"\b(answered|resolved|closed|done)\b", re.I)


def read(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    raw, body = split_frontmatter(text)
    return ((load_yaml(raw) if raw else None) or {}), body


def as_date(value) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def section(body: str, heading: str) -> str:
    m = re.search(rf"(?ms)^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", body)
    return m.group(1) if m else ""


def facts(folder: Path, since: dt.date | None) -> dict:
    status_dir = folder / "status"
    previous = sorted(status_dir.glob("*.md")) if status_dir.is_dir() else []
    last_update = previous[-1] if previous else None
    if since is None and last_update is not None:
        since = as_date(last_update.stem)

    artifacts, stories, questions, acceptance = [], [], [], []
    for path in sorted(folder.rglob("*.md")):
        rel = path.relative_to(folder).as_posix()
        if rel.startswith("status/"):
            continue
        fm, body = read(path)
        updated = as_date(fm.get("updated"))
        entry = {
            "path": rel, "id": fm.get("id"), "type": fm.get("type"),
            "title": fm.get("title"), "status": fm.get("status"),
            "updated": str(updated) if updated else None,
            "changed_since_last_update": bool(since and updated and updated > since),
        }
        artifacts.append(entry)

        if fm.get("type") == "story":
            tracker = fm.get("tracker") if isinstance(fm.get("tracker"), dict) else {}
            stories.append({
                "id": fm.get("id"), "title": fm.get("title"), "status": fm.get("status"),
                "epic": fm.get("epic"), "priority": fm.get("priority"),
                "tracker_key": tracker.get("key"), "tracker_status": tracker.get("status"),
                "synced_at": str(tracker.get("synced_at")) if tracker.get("synced_at") else None,
            })

        if fm.get("type") == "acceptance-report":
            m = re.search(r"\*\*Recommendation:\*\*\s*(.+?)(?=\n\s*\n|\s\*\*[A-Z][^*\n]*:\*\*|\Z)", body, re.S)
            acceptance.append({
                "path": rel, "updated": entry["updated"],
                "recommendation": " ".join(m.group(1).split()) if m else None,
            })

        for line in body.splitlines():
            q = QUESTION_ROW.match(line)
            if q and not CLOSED.search(q.group(3)):
                questions.append({"artifact": fm.get("id") or rel, "id": q.group(1),
                                  "question": q.group(2), "rest": q.group(3).strip(" |")})

    readme_fm, readme_body = read(folder / "README.md") if (folder / "README.md").exists() else ({}, "")
    decisions: list[str] = []
    for ln in section(readme_body, "Decisions").splitlines():
        if ln.lstrip().startswith(("- ", "* ")):
            decisions.append(ln.strip()[2:].strip())
        elif ln.strip() and decisions and ln.startswith((" ", "\t")):
            decisions[-1] += " " + ln.strip()

    by_status: dict[str, int] = {}
    for s in stories:
        by_status[str(s["status"])] = by_status.get(str(s["status"]), 0) + 1

    return {
        "initiative": folder.name,
        "title": readme_fm.get("title", folder.name),
        "owner": readme_fm.get("owner"),
        "since": str(since) if since else None,
        "previous_update": last_update.relative_to(folder).as_posix() if last_update else None,
        "artifacts": artifacts,
        "changed": [a["path"] for a in artifacts if a["changed_since_last_update"]],
        "stories": stories,
        "stories_by_status": by_status,
        "stories_not_in_tracker": [s["id"] for s in stories if not s["tracker_key"]],
        "open_questions": questions,
        "acceptance": acceptance,
        "decisions": decisions,
    }


def render(f: dict) -> str:
    out = [f"# Facts for {f['title']} ({f['initiative']})", ""]
    out.append(f"Previous update: {f['previous_update'] or 'none'}"
               + (f" (changes counted since {f['since']})" if f["since"] else ""))
    out += ["", "## Artifacts", ""]
    for a in f["artifacts"]:
        mark = " (changed)" if a["changed_since_last_update"] else ""
        out.append(f"- {a['path']}: {a['id']} [{a['status']}], updated {a['updated']}{mark}")
    out += ["", "## Stories", ""]
    if f["stories"]:
        counts = ", ".join(f"{k}: {v}" for k, v in sorted(f["stories_by_status"].items()))
        out.append(f"{len(f['stories'])} stories ({counts})")
        for s in f["stories"]:
            tracker = f"{s['tracker_key']} ({s['tracker_status'] or 'status not recorded'})" if s["tracker_key"] else "not in tracker"
            out.append(f"- {s['id']} [{s['status']}] {s['title']} - {tracker}")
    else:
        out.append("No stories yet.")
    out += ["", "## Open questions", ""]
    out += [f"- {q['artifact']} {q['id']}: {q['question']}" for q in f["open_questions"]] or ["None found."]
    out += ["", "## Acceptance checks", ""]
    out += [f"- {a['path']} ({a['updated']}): {a['recommendation'] or 'no recommendation line'}"
            for a in f["acceptance"]] or ["None yet."]
    out += ["", "## Decisions (from README)", ""]
    out += [f"- {d}" for d in f["decisions"]] or ["None listed."]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("initiative_dir", type=Path)
    ap.add_argument("--since", help="count artifacts changed after this date (YYYY-MM-DD)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not args.initiative_dir.is_dir():
        print(f"Not a folder: {args.initiative_dir}", file=sys.stderr)
        return 2
    since = as_date(args.since) if args.since else None
    result = facts(args.initiative_dir, since)
    print(json.dumps(result, indent=2, default=str) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
