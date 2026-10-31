#!/usr/bin/env python3
"""Numbers for AI evals: failure rates, data splits, and judge validation. No dependencies.

Usage:
  eval_stats.py failures labels.csv
  eval_stats.py split    labels.csv --out-dir DIR [--seed 7]
  eval_stats.py judge    labels.csv --judge-col judge [--human-col pass]
                         [--unlabeled judged.csv] [--seed 7]

labels.csv columns (header row required):
  id            trace ID
  pass          the human verdict: pass/fail, true/false, 1/0, yes/no
  failure_mode  for failures: one mode, or several separated by ";"
  note          optional free text
  judge         (judge command) the LLM judge's verdict for the same trace

failures  Pass rate, and how often each failure mode occurs, most common first.
split     Stratified train (15%) / dev (45%) / test (40%) files. Use train for judge
          examples, dev to improve the judge, test once for the final numbers.
judge     True positive rate (judge says pass when the human says pass) and true
          negative rate (judge says fail when the human says fail), with 95% bootstrap
          intervals. With --unlabeled (a CSV with the judge column over new traces),
          estimates the real pass rate corrected for the judge's errors.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import Counter
from pathlib import Path

TRUE = {"pass", "true", "1", "yes", "y", "p"}
FALSE = {"fail", "false", "0", "no", "n", "f"}


def verdict(value: str) -> bool | None:
    v = (value or "").strip().lower()
    return True if v in TRUE else False if v in FALSE else None


def read(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cmd_failures(args) -> int:
    rows = read(args.labels)
    labeled = [r for r in rows if verdict(r.get("pass", "")) is not None]
    fails = [r for r in labeled if verdict(r["pass"]) is False]
    modes = Counter()
    unmoded = 0
    for r in fails:
        parts = [m.strip() for m in (r.get("failure_mode") or "").split(";") if m.strip()]
        if not parts:
            unmoded += 1
        modes.update(parts)
    n = len(labeled)
    print(f"{n} labeled traces ({len(rows) - n} unlabeled). Pass rate: {pct(n - len(fails), n)}.\n")
    print("| Failure mode | Traces | % of all traces | % of failures |")
    print("|--------------|--------|-----------------|---------------|")
    for mode, c in modes.most_common():
        print(f"| {mode} | {c} | {pct(c, n)} | {pct(c, len(fails))} |")
    if unmoded:
        print(f"| (no mode yet) | {unmoded} | {pct(unmoded, n)} | {pct(unmoded, len(fails))} |")
    return 0


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "n/a"


def cmd_split(args) -> int:
    rows = read(args.labels)
    rng = random.Random(args.seed)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    groups = {True: [], False: []}
    for r in rows:
        v = verdict(r.get("pass", ""))
        if v is not None:
            groups[v].append(r)
    splits = {"train": [], "dev": [], "test": []}
    for group in groups.values():
        rng.shuffle(group)
        a, b = round(len(group) * 0.15), round(len(group) * 0.60)
        splits["train"] += group[:a]
        splits["dev"] += group[a:b]
        splits["test"] += group[b:]
    fields = list(rows[0].keys()) if rows else ["id", "pass"]
    for name, items in splits.items():
        with open(out / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(items)
        print(f"{name}: {len(items)} traces ({sum(verdict(r['pass']) for r in items)} pass)")
    return 0


def rates(pairs: list[tuple[bool, bool]]) -> tuple[float | None, float | None]:
    hp = [j for h, j in pairs if h]
    hf = [j for h, j in pairs if not h]
    tpr = sum(hp) / len(hp) if hp else None
    tnr = sum(1 for j in hf if not j) / len(hf) if hf else None
    return tpr, tnr


def corrected(observed: float, tpr: float, tnr: float) -> float | None:
    denom = tpr + tnr - 1
    if denom <= 0:
        return None
    return min(1.0, max(0.0, (observed + tnr - 1) / denom))


def interval(values: list[float]) -> str:
    values = sorted(v for v in values if v is not None)
    if not values:
        return "n/a"
    lo, hi = values[int(0.025 * len(values))], values[int(0.975 * len(values)) - 1]
    return f"{lo:.2f}-{hi:.2f}"


def cmd_judge(args) -> int:
    rows = read(args.labels)
    pairs = []
    for r in rows:
        h, j = verdict(r.get(args.human_col, "")), verdict(r.get(args.judge_col, ""))
        if h is not None and j is not None:
            pairs.append((h, j))
    if not pairs:
        sys.exit(f"No rows with both `{args.human_col}` and `{args.judge_col}` verdicts.")
    tpr, tnr = rates(pairs)
    rng = random.Random(args.seed)
    boot = [rates([rng.choice(pairs) for _ in pairs]) for _ in range(1000)]
    n_hp = sum(1 for h, _ in pairs if h)
    print(f"{len(pairs)} traces with both verdicts ({n_hp} human pass, {len(pairs) - n_hp} human fail).\n")
    print("| Metric | Value | 95% interval |")
    print("|--------|-------|--------------|")
    print(f"| True positive rate (TPR) | {fmt(tpr)} | {interval([b[0] for b in boot])} |")
    print(f"| True negative rate (TNR) | {fmt(tnr)} | {interval([b[1] for b in boot])} |")
    agree = sum(1 for h, j in pairs if h == j) / len(pairs)
    print(f"| Raw agreement | {agree:.2f} | |")
    if min(n_hp, len(pairs) - n_hp) < 20:
        print("\nFewer than 20 human passes or fails: treat these numbers as rough.")

    if args.unlabeled:
        judged = [verdict(r.get(args.judge_col, "")) for r in read(args.unlabeled)]
        judged = [j for j in judged if j is not None]
        if judged and tpr is not None and tnr is not None:
            observed = sum(judged) / len(judged)
            est = corrected(observed, tpr, tnr)
            boot_est = []
            for b_tpr, b_tnr in boot:
                if b_tpr is not None and b_tnr is not None:
                    sample = [rng.choice(judged) for _ in judged]
                    boot_est.append(corrected(sum(sample) / len(sample), b_tpr, b_tnr))
            print(f"\nOn {len(judged)} new traces the judge passed {observed:.0%}.")
            if est is None:
                print("The judge is no better than chance (TPR + TNR <= 1); fix it before using it.")
            else:
                print(f"Corrected pass rate: {est:.0%} (95% interval {interval(boot_est)}).")
    return 0


def fmt(x: float | None) -> str:
    return f"{x:.2f}" if x is not None else "n/a"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("failures")
    f.add_argument("labels")
    s = sub.add_parser("split")
    s.add_argument("labels")
    s.add_argument("--out-dir", required=True)
    s.add_argument("--seed", type=int, default=7)
    j = sub.add_parser("judge")
    j.add_argument("labels")
    j.add_argument("--judge-col", default="judge")
    j.add_argument("--human-col", default="pass")
    j.add_argument("--unlabeled")
    j.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)
    return {"failures": cmd_failures, "split": cmd_split, "judge": cmd_judge}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
