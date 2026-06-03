#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: audit-next.sh [worktree] [--launch|--no-launch]

Print or launch a Codex prompt that executes exactly the next unchecked item
from PROGRESS.md and then stops.

Options:
  --launch       Launch Codex in the worktree.
  --no-launch    Print the launch command only. Default.
  -h, --help     Show this help.
USAGE
}

worktree=""
launch=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --launch)
      launch=1
      shift
      ;;
    --no-launch)
      launch=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$worktree" ]]; then
        echo "Unexpected extra argument: $1" >&2
        usage >&2
        exit 2
      fi
      worktree="$1"
      shift
      ;;
  esac
done

if [[ -z "$worktree" ]]; then
  worktree="."
fi

worktree="$(CDPATH= cd -- "$worktree" && pwd)"

if [[ ! -f "$worktree/GOAL.md" || ! -f "$worktree/PROGRESS.md" ]]; then
  echo "Expected GOAL.md and PROGRESS.md in: $worktree" >&2
  exit 1
fi

prompt="Read GOAL.md and PROGRESS.md. Execute exactly the next unchecked item per the Execution Rules. Stop after one item. Update PROGRESS.md by moving the item to Completed with commit hash/date/verification, or to Rejected with reason. If the item is requires-approval or migration-needed, stop and ask the human before editing."

cat <<EOF
Continue command:
codex -C "$worktree" "$prompt"
EOF

if [[ "$launch" -eq 1 ]]; then
  exec codex -C "$worktree" "$prompt"
fi
