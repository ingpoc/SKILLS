#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WRAPPER="$HOME/.local/bin/resume-session"
INSPECTOR="$SKILL_DIR/scripts/inspect_checkpoint.py"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

if ! cmp -s "$SKILL_DIR/scripts/resume-session" "$WRAPPER"; then
  printf 'installed resume-session wrapper differs from the skill source\n' >&2
  exit 1
fi

PROJECT="$TMP_DIR/project"
NESTED="$PROJECT/nested/work"
mkdir -p "$PROJECT/.claude/session-data" "$NESTED"
cat >"$PROJECT/.claude/session-data/CURRENT.md" <<'EOF'
ancestor checkpoint

## codex_goal
objective: Complete the exact saved objective without shrinking its exit gate.
resume_policy: ensure-active
EOF

OUTPUT="$(cd "$NESTED" && RESUME_SESSION_INSPECTOR="$INSPECTOR" "$WRAPPER")"
case "$OUTPUT" in
  *"$PROJECT/.claude/session-data/CURRENT.md"*"ancestor checkpoint"*"## codex_goal"*"Complete the exact saved objective"*) ;;
  *)
    printf 'ancestor checkpoint resolution failed:\n%s\n' "$OUTPUT" >&2
    exit 1
    ;;
esac

OVERRIDE="$TMP_DIR/override"
mkdir -p "$OVERRIDE/.claude/session-data"
printf 'override checkpoint\n' >"$OVERRIDE/.claude/session-data/CURRENT.md"
OUTPUT="$(cd "$NESTED" && RESUME_SESSION_ROOT="$OVERRIDE" RESUME_SESSION_INSPECTOR="$INSPECTOR" "$WRAPPER")"
case "$OUTPUT" in
  *"$OVERRIDE/.claude/session-data/CURRENT.md"*"override checkpoint"*) ;;
  *)
    printf 'explicit root resolution failed:\n%s\n' "$OUTPUT" >&2
    exit 1
    ;;
esac

INSPECTION="$(cd "$NESTED" && RESUME_SESSION_INSPECTOR="$INSPECTOR" "$WRAPPER" --inspect-json)"
case "$INSPECTION" in
  *'"mode": "review-checkpoint"'*'"objective_missing"'*) ;;
  *)
    printf 'inspection did not reject the noncanonical checkpoint fixture:\n%s\n' "$INSPECTION" >&2
    exit 1
    ;;
esac

printf 'resume-session root resolution: ok\n'
