#!/usr/bin/env bash
# Install PM harness skills into a product repository (or globally).
#
# Usage:
#   scripts/install.sh [--target <repo-dir>] [--global] [--copy] [--agents universal,claude] [skill ...]
#
#   --target   product repository to install into (default: current directory)
#   --global   install into your home directory instead of a repository
#   --copy     copy skill folders instead of symlinking them (use for teammates/CI)
#   --agents   comma-separated: universal (.agents/skills: Codex, Cursor, Copilot,
#              Antigravity, Amp...), claude (.claude/skills: Claude Code).
#              Default: universal. Cursor reads both folders, so only add claude
#              if someone on the team uses Claude Code.
#   skill ...  install only these skills (default: all)
#
# Alternative without cloning: npx skills add bharal-sahab/pm-harness

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(pwd)"
GLOBAL=0
MODE="link"
AGENTS="universal"
SKILLS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --global) GLOBAL=1; shift ;;
    --copy) MODE="copy"; shift ;;
    --agents) AGENTS="$2"; shift 2 ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 2 ;;
    *) SKILLS+=("$1"); shift ;;
  esac
done

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  for d in "$HARNESS_DIR"/skills/*/; do SKILLS+=("$(basename "$d")"); done
fi

dest_dirs=()
IFS=',' read -ra agent_list <<< "$AGENTS"
for agent in "${agent_list[@]}"; do
  case "$agent" in
    universal) [[ $GLOBAL -eq 1 ]] && dest_dirs+=("$HOME/.agents/skills") || dest_dirs+=("$TARGET/.agents/skills") ;;
    claude)    [[ $GLOBAL -eq 1 ]] && dest_dirs+=("$HOME/.claude/skills") || dest_dirs+=("$TARGET/.claude/skills") ;;
    *) echo "Unknown agent '$agent' (use universal or claude)" >&2; exit 2 ;;
  esac
done

for dest in "${dest_dirs[@]}"; do
  mkdir -p "$dest"
  for skill in "${SKILLS[@]}"; do
    src="$HARNESS_DIR/skills/$skill"
    [[ -f "$src/SKILL.md" ]] || { echo "No such skill: $skill" >&2; exit 1; }
    rm -rf "${dest:?}/$skill"
    if [[ "$MODE" == "copy" ]]; then
      cp -R "$src" "$dest/$skill"
    else
      ln -s "$src" "$dest/$skill"
    fi
  done
  echo "Installed ${#SKILLS[@]} skill(s) into $dest ($MODE)"
done

if [[ $GLOBAL -eq 0 ]]; then
  echo
  echo "Next: open $TARGET in your agent and say \"run pm-start\"."
fi
