#!/usr/bin/env python3
"""Check a PM harness `pm/` folder against the harness conventions.

Usage:
    python3 check_pm.py <pm-dir> [--repo <repo-root>] [--strict] [--quiet]

Reports missing frontmatter, invalid types/statuses, duplicate IDs, broken
artifact references, broken relative links, missing code references, and
citations of excluded paths. Exits 1 when errors are found.

No third-party dependencies. Uses PyYAML when installed, otherwise a small
built-in parser that covers the YAML subset the harness writes.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

TYPE_PREFIX = {
    "product-page": "PROD",
    "journey": "JRN",
    "initiative": "INIT",
    "research-plan": "RP",
    "research": "RES",
    "competitive-scan": "CS",
    "brief": "BRIEF",
    "design": "DES",
    "design-review": "DR",
    "prd": "PRD",
    "tech-impact": "TI",
    "epic": "EPIC",
    "story": "STORY",
    "test-plan": "TP",
    "acceptance-report": "AC",
    "eval": "EVAL",
    "release": "REL",
    "status-update": "SU",
    "decision": "DEC",
}
STATUSES = {"draft", "in-review", "approved", "in-progress", "done", "superseded"}
REQUIRED = ("id", "type", "title", "status", "updated")
ID_RE = re.compile(r"^[A-Z]+-[a-z0-9]+(?:-[a-z0-9]+)*$")
CAP_RE = re.compile(r"^#{2,4}\s+(CAP-[a-z0-9-]+)", re.M)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CITE_RE = re.compile(r"`([A-Za-z0-9_.@\-\[\]]+(?:/[A-Za-z0-9_.@\-\[\]]+)+\.[A-Za-z0-9]+)(?::\d+(?:-\d+)?)?`")
SKIP_FILES = {"CONVENTIONS.md"}


# --------------------------------------------------------------------------- YAML

def _scalar(text: str):
    t = text.strip()
    if t == "" or t in ("null", "~", "Null", "NULL"):
        return None
    if t in ("true", "True"):
        return True
    if t in ("false", "False"):
        return False
    if (t[0] == t[-1]) and t[0] in ("'", '"') and len(t) >= 2:
        return t[1:-1]
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        return [] if not inner else [_scalar(p) for p in _split_top(inner)]
    if t.startswith("{") and t.endswith("}"):
        inner = t[1:-1].strip()
        out = {}
        for part in _split_top(inner) if inner else []:
            k, _, v = part.partition(":")
            out[k.strip()] = _scalar(v)
        return out
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    return t


def _split_top(text: str):
    parts, depth, buf, quote = [], 0, "", None
    for ch in text:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
            continue
        buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


def _strip_comment(line: str) -> str:
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def mini_yaml(text: str):
    lines = [_strip_comment(l) for l in text.splitlines()]
    lines = [l for l in lines if l.strip()]

    def parse(i: int, indent: int):
        if i < len(lines) and lines[i].lstrip().startswith("- "):
            items = []
            while i < len(lines):
                cur = len(lines[i]) - len(lines[i].lstrip())
                if cur < indent or not lines[i].lstrip().startswith("- "):
                    break
                items.append(_scalar(lines[i].lstrip()[2:]))
                i += 1
            return items, i
        out = {}
        while i < len(lines):
            line = lines[i]
            cur = len(line) - len(line.lstrip())
            if cur < indent:
                break
            key, _, val = line.strip().partition(":")
            i += 1
            if val.strip():
                out[key.strip()] = _scalar(val)
            elif i < len(lines) and (len(lines[i]) - len(lines[i].lstrip())) > cur:
                child_indent = len(lines[i]) - len(lines[i].lstrip())
                out[key.strip()], i = parse(i, child_indent)
            elif i < len(lines) and lines[i].lstrip().startswith("- ") and (len(lines[i]) - len(lines[i].lstrip())) == cur:
                out[key.strip()], i = parse(i, cur)
            else:
                out[key.strip()] = None
        return out, i

    result, _ = parse(0, 0)
    return result


def load_yaml(text: str):
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ImportError:
        data = mini_yaml(text)
    return _normalize(data)


def _normalize(value):
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, (_dt.date, _dt.datetime)):
        return value.isoformat()[:10]
    return value


def split_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end].strip("\n"), text[end + 4:]


# --------------------------------------------------------------------------- checks

class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path, msg):
        self.errors.append(f"ERROR   {path}: {msg}")

    def warn(self, path, msg):
        self.warnings.append(f"WARN    {path}: {msg}")


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def check(pm_dir: Path, repo: Path | None, strict: bool) -> Report:
    rep = Report()
    if not pm_dir.is_dir():
        rep.error(pm_dir, "pm folder not found")
        return rep

    config = {}
    cfg_path = pm_dir / "config.yaml"
    if cfg_path.exists():
        config = load_yaml(cfg_path.read_text()) or {}
    else:
        rep.warn(cfg_path, "missing pm/config.yaml")
    excludes = [p.rstrip("/") for p in as_list(config.get("exclude_paths"))]

    capabilities: set[str] = set()
    caps_file = pm_dir / "product" / "capabilities.md"
    if caps_file.exists():
        capabilities = set(CAP_RE.findall(caps_file.read_text()))

    meta = pm_dir / "product" / "_meta.yaml"
    if (pm_dir / "product").is_dir():
        if not meta.exists():
            rep.error(meta, "missing; product-map must record source_commit")
        else:
            m = load_yaml(meta.read_text()) or {}
            for key in ("source_commit", "generated_at"):
                if not m.get(key):
                    rep.error(meta, f"missing `{key}`")

    docs: dict[str, tuple[Path, dict]] = {}
    files = sorted(p for p in pm_dir.rglob("*.md") if p.name not in SKIP_FILES)
    for path in files:
        rel = path.relative_to(pm_dir)
        raw, body = split_frontmatter(path.read_text())
        if raw is None:
            rep.error(rel, "no YAML frontmatter")
            continue
        try:
            fm = load_yaml(raw) or {}
        except Exception as exc:  # noqa: BLE001
            rep.error(rel, f"frontmatter is not valid YAML ({exc})")
            continue
        for key in REQUIRED:
            if not fm.get(key):
                rep.error(rel, f"missing required field `{key}`")
        art_id, art_type = fm.get("id"), fm.get("type")
        if art_id and not ID_RE.match(str(art_id)):
            rep.error(rel, f"id `{art_id}` must look like PREFIX-lowercase-slug")
        if art_type and art_type not in TYPE_PREFIX:
            rep.error(rel, f"unknown type `{art_type}`")
        elif art_type and art_id and not str(art_id).startswith(TYPE_PREFIX[art_type] + "-"):
            rep.error(rel, f"id `{art_id}` should start with `{TYPE_PREFIX[art_type]}-` for type `{art_type}`")
        if fm.get("status") and fm["status"] not in STATUSES:
            rep.error(rel, f"status `{fm['status']}` not in {sorted(STATUSES)}")
        if fm.get("updated") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(fm["updated"])):
            rep.error(rel, "`updated` must be YYYY-MM-DD")

        parts = rel.parts
        if parts[0] == "initiatives" and len(parts) > 2:
            slug = parts[1]
            if fm.get("initiative") != slug:
                rep.error(rel, f"`initiative` should be `{slug}` (folder name)")
            if "derived_from" not in fm:
                rep.error(rel, "initiative artifacts need `derived_from` (use [] if none)")

        if art_id:
            if art_id in docs:
                rep.error(rel, f"duplicate id `{art_id}` (also in {docs[art_id][0]})")
            else:
                docs[art_id] = (rel, fm)

        for cap in as_list(fm.get("capabilities")):
            if capabilities and cap not in capabilities:
                rep.error(rel, f"capability `{cap}` not found in product/capabilities.md")

        for ref in as_list(fm.get("code_refs")):
            _check_code_path(rep, rel, str(ref), repo, excludes, strict_missing=True)

        for target in LINK_RE.findall(body):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            target_path = (path.parent / target.split("#")[0]).resolve()
            if not target_path.exists():
                rep.error(rel, f"broken link `{target}`")

        cites = CITE_RE.findall(body)
        for cite in cites:
            _check_code_path(rep, rel, cite, repo, excludes, strict_missing=False)
        if art_type in ("product-page", "journey") and not cites and rel.name != "open-questions.md":
            (rep.error if strict else rep.warn)(rel, "no code citations; product pages must be grounded")

    for art_id, (rel, fm) in docs.items():
        for ref in as_list(fm.get("derived_from")) + as_list(fm.get("epic")):
            if ref and ref not in docs:
                rep.error(rel, f"references unknown artifact `{ref}`")
    return rep


def _check_code_path(rep: Report, rel, ref: str, repo, excludes, strict_missing: bool):
    clean = ref.split(":")[0]
    for ex in excludes:
        if clean == ex or clean.startswith(ex + "/"):
            rep.error(rel, f"cites excluded path `{clean}`")
            return
    if repo is None:
        return
    if not (repo / clean).exists():
        if strict_missing:
            rep.error(rel, f"code_ref `{clean}` does not exist in repo")
        else:
            rep.warn(rel, f"cited path `{clean}` not found in repo")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pm_dir", type=Path)
    ap.add_argument("--repo", type=Path, default=None, help="repository root used to verify code paths")
    ap.add_argument("--strict", action="store_true", help="treat ungrounded product pages as errors")
    ap.add_argument("--quiet", action="store_true", help="only print errors")
    args = ap.parse_args(argv)

    rep = check(args.pm_dir, args.repo, args.strict)
    for line in rep.errors:
        print(line)
    if not args.quiet:
        for line in rep.warnings:
            print(line)
    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
