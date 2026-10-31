#!/usr/bin/env bash
# Run the golden-question eval with a real coding agent, headless.
#
# Usage:
#   evals/run-cross-agent.sh --agent claude|codex|cursor --repo PATH \
#       [--mode answer|map] [--questions FILE] [--kb DIR] [--out DIR]
#
# Modes:
#   answer  (default) Copies an existing knowledge base (--kb, default examples/<name>/pm)
#           into a scratch copy of the repo and asks the agent to answer the golden
#           questions from pm/product only. Tests whether the knowledge base works with
#           that agent.
#   map     Installs the harness skills into a scratch copy of the repo, asks the agent
#           to run product-map from scratch (accepting defaults at checkpoints), then
#           answers. Tests the skill itself end to end on that agent. Slow and costly.
#
# The scratch copy lives in a temp folder; the original repo is never modified.
# Results land in --out (default evals/results/<repo-name>-<agent>-<mode>-<date>).

set -euo pipefail

HARNESS="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="" REPO="" MODE="answer" QUESTIONS="" KB="" OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --repo) REPO="$(cd "$2" && pwd)"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --questions) QUESTIONS="$2"; shift 2 ;;
    --kb) KB="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) sed -n 2,19p "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$AGENT" && -n "$REPO" ]] || { echo "Need --agent and --repo (see --help)" >&2; exit 2; }
NAME="$(basename "$REPO")"
QUESTIONS="${QUESTIONS:-$HARNESS/evals/$NAME/golden-questions.yaml}"
KB="${KB:-$HARNESS/examples/$NAME/pm}"
OUT="${OUT:-$HARNESS/evals/results/$NAME-$AGENT-$MODE-$(date +%Y%m%d)}"
[[ -f "$QUESTIONS" ]] || { echo "No questions file: $QUESTIONS" >&2; exit 2; }

case "$AGENT" in
  claude) BIN="$(command -v claude || true)" ;;
  codex) BIN="$(command -v codex || true)" ;;
  cursor) BIN="$(command -v cursor-agent || command -v agent || true)" ;;
  *) echo "Unknown agent: $AGENT (use claude, codex or cursor)" >&2; exit 2 ;;
esac
[[ -n "$BIN" ]] || { echo "The $AGENT CLI is not installed or not on PATH" >&2; exit 3; }

run_agent() {
  local prompt="$1"
  case "$AGENT" in
    claude) "$BIN" -p "$prompt" --allowedTools "Read,Write,Edit,Glob,Grep,Bash" ;;
    codex) "$BIN" exec --full-auto "$prompt" ;;
    cursor) "$BIN" -p --force --output-format text "$prompt" ;;
  esac
}

WORK="$(mktemp -d)/$NAME"
echo "Scratch copy: $WORK"
rsync -a --exclude node_modules --exclude .pm-eval "$REPO/" "$WORK/"
mkdir -p "$OUT"
cd "$WORK"

if [[ "$MODE" == "map" ]]; then
  rm -rf pm
  "$HARNESS/scripts/install.sh" --target "$WORK" --agents universal,claude --copy >/dev/null
  run_agent "Use the product-map skill to map this repository for product managers. \
This is an unattended run: at every checkpoint accept your own recommendation, use depth \
standard, and continue without waiting for me." | tee "$OUT/map-transcript.txt"
  python3 "$HARNESS/scripts/check_pm.py" pm --repo "$WORK" --strict | tee "$OUT/check.txt" || true
  cp -R pm "$OUT/pm"
elif [[ "$MODE" == "answer" ]]; then
  [[ -d "$KB" ]] || { echo "No knowledge base at $KB" >&2; exit 2; }
  rm -rf pm && cp -R "$KB" pm
else
  echo "Unknown mode: $MODE" >&2; exit 2
fi

python3 "$HARNESS/evals/run_golden.py" prompt "$QUESTIONS" > "$OUT/prompt.md"
run_agent "$(cat "$OUT/prompt.md")" | tee "$OUT/answer-transcript.txt"
[[ -f answers.yaml ]] || { echo "Agent did not write answers.yaml" >&2; exit 4; }
cp answers.yaml "$OUT/answers.yaml"

python3 "$HARNESS/evals/run_golden.py" grade "$QUESTIONS" "$OUT/answers.yaml" \
  --repo "$WORK" --out "$OUT/report.md"
python3 "$HARNESS/evals/run_golden.py" judge "$QUESTIONS" "$OUT/answers.yaml" \
  --out-dir "$OUT/judge-prompts" >/dev/null
echo "Results: $OUT"
