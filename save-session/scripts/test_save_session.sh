#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WRAPPER="$SKILL_DIR/scripts/save-session"
INSTALLED="$HOME/.local/bin/save-session"
export SESSION_WORKSPACE_HELPER="$SKILL_DIR/../session-orchestrate/scripts/session_workspace.py"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

if ! cmp -s "$WRAPPER" "$INSTALLED"; then
  printf 'installed save-session wrapper differs from the skill source\n' >&2
  exit 1
fi

PROJECT="$TMP_DIR/project"
mkdir -p "$PROJECT"
GOAL_OBJECTIVE=$'Complete the exact saved objective.\nPreserve every accepted exit condition.'

SAVE_SESSION_ROOT="$PROJECT" \
SAVE_SESSION_GOAL_OBJECTIVE="$GOAL_OBJECTIVE" \
SAVE_SESSION_GOAL_RESUME_POLICY="ensure-active" \
SAVE_SESSION_WORKING_ON="Goal persistence test" \
SAVE_SESSION_NEXT_ACTION="Resume the exact goal." \
"$WRAPPER" >/dev/null

CHECKPOINT="$PROJECT/.session/CURRENT.md"
grep -Fq '## codex_goal' "$CHECKPOINT"
grep -Fq 'resume_policy: ensure-active' "$CHECKPOINT"
grep -Fq 'Complete the exact saved objective.' "$CHECKPOINT"
grep -Fq 'Preserve every accepted exit condition.' "$CHECKPOINT"
grep -Fq '**resume_window_hours:** 24' "$CHECKPOINT"

CUSTOM="$TMP_DIR/custom-window"
mkdir -p "$CUSTOM"
SAVE_SESSION_ROOT="$CUSTOM" \
SAVE_SESSION_RESUME_WINDOW_HOURS="72" \
"$WRAPPER" >/dev/null 2>&1
grep -Fq '**resume_window_hours:** 72' "$CUSTOM/.session/CURRENT.md"

NESTED_ROOT="$TMP_DIR/nested-root"
NESTED_WORK="$NESTED_ROOT/path/to/work"
mkdir -p "$NESTED_WORK"
python3 "$SESSION_WORKSPACE_HELPER" ensure --root "$NESTED_ROOT" >/dev/null
(cd "$NESTED_WORK" && "$WRAPPER" >/dev/null 2>&1)
test -f "$NESTED_ROOT/.session/CURRENT.md"
test ! -e "$NESTED_WORK/.session/CURRENT.md"

NO_GOAL="$TMP_DIR/no-goal"
mkdir -p "$NO_GOAL"
SAVE_SESSION_ROOT="$NO_GOAL" "$WRAPPER" >/dev/null 2>&1
grep -Fq '*(none supplied; do not infer a goal from working_on or next_action)*' \
  "$NO_GOAL/.session/CURRENT.md"

INVALID="$TMP_DIR/invalid"
mkdir -p "$INVALID"
if SAVE_SESSION_ROOT="$INVALID" \
  SAVE_SESSION_GOAL_OBJECTIVE="Invalid policy fixture" \
  SAVE_SESSION_GOAL_RESUME_POLICY="replace-existing" \
  "$WRAPPER" >/dev/null 2>&1; then
  printf 'invalid goal resume policy was accepted\n' >&2
  exit 1
fi

for invalid_window in 0 169 nope; do
  if SAVE_SESSION_ROOT="$INVALID" \
    SAVE_SESSION_RESUME_WINDOW_HOURS="$invalid_window" \
    "$WRAPPER" >/dev/null 2>&1; then
    printf 'invalid resume window was accepted: %s\n' "$invalid_window" >&2
    exit 1
  fi
done

printf 'save-session goal checkpoint: ok\n'
