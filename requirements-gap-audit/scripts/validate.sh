#!/usr/bin/env bash
set -eu

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ -f "$HOME/.codex/skills/create-skill/scripts/audit.py" ]; then
  python3 "$HOME/.codex/skills/create-skill/scripts/audit.py" "$SKILL_DIR" "$@"
else
  python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$SKILL_DIR"
fi

