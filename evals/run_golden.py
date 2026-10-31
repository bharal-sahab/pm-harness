#!/usr/bin/env python3
"""Golden-question evals for the product knowledge base.

Usage:
  python3 evals/run_golden.py prompt <questions.yaml>               > prompt.md
  python3 evals/run_golden.py grade  <questions.yaml> <answers.yaml> [--repo DIR] [--out report.md]
  python3 evals/run_golden.py judge  <questions.yaml> <answers.yaml> --out-dir DIR

prompt  Prints the instructions an agent follows to answer every question using ONLY
        pm/product/ (the generated knowledge base), in the answers.yaml format.
grade   Automatic grading: key-point coverage, grounding (cites an expected source),
        and citation validity (cited files exist in --repo). Writes a markdown report.
judge   Writes one LLM-as-judge prompt per question applying evals/rubric.md, for a
        stronger second pass. Feed each prompt to any model and record its verdicts.

Pass bar (see evals/rubric.md): average key-point coverage >= 0.85, no question below
0.5, grounding >= 0.9, and zero invalid citations.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
from check_pm import load_yaml  # noqa: E402

PASS_COVERAGE = 0.85
MIN_QUESTION = 0.5
PASS_GROUNDING = 0.9

ANSWER_FORMAT = """\
answers:
  - id: Q01
    answer: >
      Two to five plain-language sentences a PM could repeat in a meeting.
    citations: [path/to/file.ts, path/to/other.ts:120]
    pages_used: [journeys/checkout.md]
    confidence: high   # high | medium | low | unknown
"""


def load(path: Path):
    try:
        import yaml  # noqa: F401
    except ImportError:
        sys.exit("The golden-question files need PyYAML: pip install pyyaml")
    return load_yaml(path.read_text()) or {}


def cmd_prompt(questions_file: Path) -> int:
    q = load(questions_file)
    print(f"# Golden questions: {q.get('product')}\n")
    print("Answer every question below using ONLY the files in `pm/product/`.")
    print("Do not open product source code. If the knowledge base does not answer a")
    print("question, say so and set confidence to `unknown`; do not guess.")
    print("Copy the code citations the knowledge base gives for each fact you use.\n")
    print("Write your answers to `answers.yaml` in exactly this format:\n")
    print("```yaml\n" + ANSWER_FORMAT + "```\n")
    print("## Questions\n")
    for item in q["questions"]:
        print(f"- **{item['id']}**: {item['question']}")
    return 0


def _matches_source(citation: str, sources: list[str]) -> bool:
    path = citation.split(":")[0].strip()
    return any(path.startswith(s) or s.startswith(path) or s in path for s in sources)


def grade(questions: dict, answers: dict, repo: Path | None):
    by_id = {a["id"]: a for a in answers.get("answers", [])}
    rows = []
    for item in questions["questions"]:
        ans = by_id.get(item["id"], {})
        text = (ans.get("answer") or "").lower()
        cites = [str(c) for c in (ans.get("citations") or [])]
        unknown = str(ans.get("confidence", "")).lower() == "unknown"
        hits = [] if unknown else [
            kp["point"] for kp in item["key_points"] if any(p.lower() in text for p in kp["any"])
        ]
        misses = [kp["point"] for kp in item["key_points"] if kp["point"] not in hits]
        if unknown:
            misses = ["knowledge-base gap (answer was 'unknown')"]
        coverage = len(hits) / len(item["key_points"])
        grounded = any(_matches_source(c, item["sources"]) for c in cites)
        invalid = []
        if repo is not None:
            invalid = [c for c in cites if not (repo / c.split(":")[0]).exists()]
        rows.append({
            "id": item["id"], "question": item["question"], "coverage": coverage,
            "grounded": grounded, "invalid": invalid, "misses": misses,
            "confidence": ans.get("confidence", "missing"), "answered": bool(text),
        })
    n = len(rows)
    summary = {
        "coverage": sum(r["coverage"] for r in rows) / n,
        "grounding": sum(r["grounded"] for r in rows) / n,
        "invalid": sum(len(r["invalid"]) for r in rows),
        "worst": min(r["coverage"] for r in rows),
    }
    summary["passed"] = (
        summary["coverage"] >= PASS_COVERAGE and summary["worst"] >= MIN_QUESTION
        and summary["grounding"] >= PASS_GROUNDING and summary["invalid"] == 0
    )
    return rows, summary


def render(rows, summary, title: str) -> str:
    out = [f"# {title}\n",
           f"**Result: {'PASS' if summary['passed'] else 'FAIL'}**\n",
           "| Metric | Value | Bar |", "|--------|-------|-----|",
           f"| Average key-point coverage | {summary['coverage']:.2f} | >= {PASS_COVERAGE} |",
           f"| Lowest single question | {summary['worst']:.2f} | >= {MIN_QUESTION} |",
           f"| Grounded answers | {summary['grounding']:.2f} | >= {PASS_GROUNDING} |",
           f"| Invalid citations | {summary['invalid']} | 0 |", "",
           "| ID | Coverage | Grounded | Confidence | Missed key points |",
           "|----|----------|----------|------------|-------------------|"]
    for r in rows:
        missed = "; ".join(r["misses"]) or "-"
        if r["invalid"]:
            missed += f" (invalid citations: {', '.join(r['invalid'])})"
        out.append(f"| {r['id']} | {r['coverage']:.2f} | {'yes' if r['grounded'] else 'no'} | {r['confidence']} | {missed} |")
    return "\n".join(out) + "\n"


def cmd_grade(args) -> int:
    rows, summary = grade(load(args.questions), load(args.answers), args.repo)
    report = render(rows, summary, f"Golden eval: {args.answers.parent.name}")
    if args.out:
        args.out.write_text(report)
    print(report)
    return 0 if summary["passed"] else 1


def cmd_judge(args) -> int:
    questions, answers = load(args.questions), load(args.answers)
    rubric = (ROOT / "evals" / "rubric.md").read_text()
    by_id = {a["id"]: a for a in answers.get("answers", [])}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for item in questions["questions"]:
        ans = by_id.get(item["id"], {})
        expected = "\n".join(f"- {kp['point']}" for kp in item["key_points"])
        prompt = (
            f"You are grading one answer written for a product manager.\n\n{rubric}\n\n"
            f"## Question\n{item['question']}\n\n## Expected key points\n{expected}\n\n"
            f"## Expected sources (any)\n" + "\n".join(f"- {s}" for s in item["sources"]) +
            f"\n\n## Answer to grade\n{ans.get('answer', '(missing)')}\n\n"
            f"Citations: {ans.get('citations', [])}\nStated confidence: {ans.get('confidence')}\n\n"
            "Return YAML: `correctness: 0|1|2`, `grounded: 0|1`, `plain_language: 0|1`, "
            "`honest: 0|1`, `confidently_wrong: true|false`, `notes: <one sentence>`.\n"
        )
        (args.out_dir / f"{item['id']}.md").write_text(prompt)
    print(f"Wrote {len(questions['questions'])} judge prompts to {args.out_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("questions", type=Path)
    g = sub.add_parser("grade")
    g.add_argument("questions", type=Path)
    g.add_argument("answers", type=Path)
    g.add_argument("--repo", type=Path, default=None)
    g.add_argument("--out", type=Path, default=None)
    j = sub.add_parser("judge")
    j.add_argument("questions", type=Path)
    j.add_argument("answers", type=Path)
    j.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    if args.cmd == "prompt":
        return cmd_prompt(args.questions)
    return cmd_grade(args) if args.cmd == "grade" else cmd_judge(args)


if __name__ == "__main__":
    sys.exit(main())
