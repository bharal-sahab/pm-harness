#!/usr/bin/env python3
"""Work out which parts of pm/ a code change affects.

Usage:
  python3 changed_pages.py [pm-dir] [--repo DIR] [--since SHA] [--to REF]
                           [--changed-files FILE] [--json]

By default compares `source_commit` in pm/product/_meta.yaml with HEAD using git.
Without git, pass --changed-files with one change per line, either `git diff
--name-status` output (`M<TAB>path`, `D<TAB>path`, `R100<TAB>old<TAB>new`) or bare paths.

Reports:
  - product pages to update (via `page_sources` in _meta.yaml)
  - citations that broke because the cited file was deleted or renamed
  - artifacts (any pm/ file, including initiatives and faq.md) that cite changed files
  - changed areas that no page covers (candidates for new capabilities)
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_pm import CITE_RE, as_list, load_yaml, split_frontmatter  # noqa: E402

NOISE = ("/__tests__/", "/__mocks__/", "/test/", "/tests/", "/fixtures/", "/integration-tests/")
NOISE_SUFFIX = (".spec.ts", ".test.ts", ".spec.tsx", ".test.tsx", ".spec.js", ".test.js",
                "_test.go", "_test.py", ".snap", "CHANGELOG.md", "yarn.lock",
                "package-lock.json", "pnpm-lock.yaml")
NOISE_PREFIX = (".changeset/", ".github/", "integration-tests/")


def is_noise(path: str) -> bool:
    """Tests, tooling, docs, and dependency manifests: changes that rarely alter behavior."""
    p = "/" + path
    parts = path.split("/")
    return (any(n in p for n in NOISE) or path.endswith(NOISE_SUFFIX)
            or path.startswith(NOISE_PREFIX)
            or any(seg.startswith(".") for seg in parts)
            or path.endswith((".md", ".mdx"))
            or (len(parts) == 1 and path != "package.json")
            or (len(parts) > 1 and parts[-1] == "package.json"))


def is_catch_all(pattern: str) -> bool:
    """A one-folder pattern like `packages` or `src` matches everything; never decisive."""
    return "/" not in pattern.strip("/") and "." not in pattern


def matches(path: str, pattern: str) -> bool:
    pattern = pattern.rstrip("/")
    return (path == pattern or path.startswith(pattern + "/")
            or fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern + "/*"))


def parse_changes(lines) -> dict[str, str]:
    """Return {path: status} where status is A, M, D, or R:<new path>."""
    changes: dict[str, str] = {}
    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) == 1:
            changes[parts[0].strip()] = "M"
            continue
        code = parts[0][:1]
        if code == "R" and len(parts) >= 3:
            changes[parts[1]] = f"R:{parts[2]}"
            changes[parts[2]] = "A"
        elif code in "ACMTD":
            changes[parts[1]] = "D" if code == "D" else ("A" if code == "A" else "M")
    return changes


def git_changes(repo: Path, since: str, to: str) -> dict[str, str]:
    cmd = ["git", "-C", str(repo), "diff", "--name-status", "-M", f"{since}", f"{to}"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("git is not available. Pass --changed-files instead.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"git diff failed: {exc.stderr.strip()}\n"
                 f"If {since[:12]} is missing, the clone may be shallow: try `git fetch --unshallow`.")
    return parse_changes(out.splitlines())


def doc_citations(pm_dir: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """For each pm/ markdown file (relative to pm/): cited paths, and citations with lines."""
    paths: dict[str, set[str]] = {}
    with_lines: dict[str, set[str]] = {}
    for md in sorted(pm_dir.rglob("*.md")):
        if md.name == "CONVENTIONS.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        raw_meta, body = split_frontmatter(text)
        meta = (load_yaml(raw_meta) if raw_meta else None) or {}
        doc = str(md.relative_to(pm_dir))
        cited = set()
        for m in CITE_RE.finditer(body):
            cited.add(m.group(1))
            if ":" in m.group(0):
                with_lines.setdefault(doc, set()).add(m.group(0).strip("`"))
        cited.update(str(r).split(":")[0] for r in as_list(meta.get("code_refs")))
        if cited:
            paths[doc] = cited
    return paths, with_lines


def analyze(pm_dir: Path, changes: dict[str, str]) -> dict:
    meta = load_yaml((pm_dir / "product" / "_meta.yaml").read_text()) or {}
    config_path = pm_dir / "config.yaml"
    config = load_yaml(config_path.read_text()) if config_path.exists() else {}
    excludes = [str(p) for p in as_list((config or {}).get("exclude_paths"))]
    page_sources = meta.get("page_sources") or {}

    excluded = [p for p in changes if any(matches(p, e) for e in excludes)]
    noise = [p for p in changes if p not in excluded and (is_noise(p) or p.startswith("pm/"))]
    relevant = {p: s for p, s in changes.items() if p not in excluded and p not in noise}

    pages: dict[str, list[str]] = defaultdict(list)
    for path in relevant:
        for page, sources in page_sources.items():
            if any(matches(path, str(s)) for s in as_list(sources) if not is_catch_all(str(s))):
                pages[page].append(path)

    broken, review = [], defaultdict(list)
    cited_anywhere = set()
    cited_paths, line_cites = doc_citations(pm_dir)
    recheck_lines = {
        doc: sorted(c for c in cites if changes.get(c.split(":")[0]) == "M")
        for doc, cites in line_cites.items()
    }
    for doc, cited in cited_paths.items():
        for path in sorted(cited):
            status = changes.get(path)
            if status is None:
                continue
            cited_anywhere.add(path)
            if status == "D" or status.startswith("R:"):
                broken.append({"doc": doc, "path": path,
                               "now": status[2:] if status.startswith("R:") else None})
            else:
                review[doc].append(path)

    covered = {p for files in pages.values() for p in files} | cited_anywhere
    uncovered = Counter("/".join(p.split("/")[:-1][:5]) or p for p in relevant if p not in covered)

    return {
        "since": meta.get("source_commit"),
        "changed": len(changes),
        "relevant": len(relevant),
        "ignored_noise": len(noise),
        "ignored_excluded": len(excluded),
        "pages": {k: sorted(v) for k, v in sorted(pages.items())},
        "broken_citations": broken,
        "artifacts_to_review": {k: v for k, v in sorted(review.items())},
        "line_citations_to_recheck": {k: v for k, v in sorted(recheck_lines.items()) if v},
        "uncovered_areas": dict(uncovered.most_common()),
    }


def render(r: dict, label: str) -> str:
    out = [f"# Changes {label}", ""]
    out.append(f"{r['changed']} files changed: {r['relevant']} relevant, "
               f"{r['ignored_noise']} tests or tooling, {r['ignored_excluded']} in excluded paths.")
    out += ["", "## Product pages to update", ""]
    if not r["pages"]:
        out.append("None.")
    for page, files in r["pages"].items():
        shown = ", ".join(f"`{f}`" for f in files[:5])
        more = f" and {len(files) - 5} more" if len(files) > 5 else ""
        out.append(f"- **{page}** ({len(files)} files): {shown}{more}")
    out += ["", "## Citations that broke (file deleted or renamed)", ""]
    if not r["broken_citations"]:
        out.append("None.")
    for b in r["broken_citations"]:
        now = f" -> now `{b['now']}`" if b["now"] else " (deleted)"
        out.append(f"- `{b['doc']}` cites `{b['path']}`{now}")
    out += ["", "## Artifacts that cite changed files (check they are still true)", ""]
    if not r["artifacts_to_review"]:
        out.append("None.")
    for doc, files in r["artifacts_to_review"].items():
        out.append(f"- `{doc}`: " + ", ".join(f"`{f}`" for f in files))
    out += ["", "## Line-numbered citations in modified files (lines may have moved)", ""]
    if not r["line_citations_to_recheck"]:
        out.append("None.")
    for doc, cites in r["line_citations_to_recheck"].items():
        out.append(f"- `{doc}`: " + ", ".join(f"`{c}`" for c in cites))
    out += ["", "## Changed areas no page covers (possible new capabilities)", ""]
    if not r["uncovered_areas"]:
        out.append("None.")
    for area, n in list(r["uncovered_areas"].items())[:20]:
        out.append(f"- `{area}`: {n} files")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pm_dir", nargs="?", default="pm")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--since", help="defaults to source_commit in pm/product/_meta.yaml")
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--changed-files", help="file with changed paths (no git needed)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    pm_dir = Path(args.pm_dir)
    meta_path = pm_dir / "product" / "_meta.yaml"
    if not meta_path.exists():
        sys.exit(f"{meta_path} not found. Run the product-map skill first.")

    if args.changed_files:
        changes = parse_changes(Path(args.changed_files).read_text().splitlines())
        label = f"listed in `{args.changed_files}`"
    else:
        since = args.since or (load_yaml(meta_path.read_text()) or {}).get("source_commit")
        if not since or str(since).startswith("<"):
            sys.exit("No source_commit in _meta.yaml. Pass --since <sha>.")
        changes = git_changes(Path(args.repo), str(since), args.to)
        label = f"from `{str(since)[:12]}` to `{args.to}`"

    result = analyze(pm_dir, changes)
    print(json.dumps(result, indent=2) if args.json else render(result, label))
    return 0


if __name__ == "__main__":
    sys.exit(main())
