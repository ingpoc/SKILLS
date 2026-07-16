#!/usr/bin/env bash
# Self-validate this skill against agentskills.io spec + project local style.
# Uses create-skill/scripts/audit.py. Supports Codex user-level skills,
# Claude user-level skills, and repo-local .codex/.claude skill installs.
#
# Usage:
#   ./scripts/validate.sh              # default audit
#   ./scripts/validate.sh --strict     # cross-runtime portability gate
#   ./scripts/validate.sh --json       # machine-readable
#
# Exit codes match audit.py: 0 clean (or soft-only), 1 hard findings, 2 IO error.

set -eu

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"

find_audit_py() {
    # 1. If this is create-skill itself, prefer the local audit.py.
    CANDIDATE="$SKILL_DIR/scripts/audit.py"
    if [ -f "$CANDIDATE" ]; then
        printf '%s\n' "$CANDIDATE"
        return 0
    fi

    # 2. Walk up looking for repo-local skill installs.
    REPO_ROOT="$SKILL_DIR"
    while [ "$REPO_ROOT" != "/" ]; do
        for CANDIDATE in \
            "$REPO_ROOT/.codex/skills/create-skill/scripts/audit.py" \
            "$REPO_ROOT/.claude/skills/create-skill/scripts/audit.py"; do
            if [ -f "$CANDIDATE" ]; then
                printf '%s\n' "$CANDIDATE"
                return 0
            fi
        done
        REPO_ROOT="$(dirname "$REPO_ROOT")"
    done

    # 3. User-level skill installs.
    for CANDIDATE in \
        "$HOME/.codex/skills/create-skill/scripts/audit.py" \
        "$HOME/.claude/skills/create-skill/scripts/audit.py"; do
        if [ -f "$CANDIDATE" ]; then
            printf '%s\n' "$CANDIDATE"
            return 0
        fi
    done

    return 1
}

if ! AUDIT="$(find_audit_py)"; then
    echo "validate.sh: could not locate create-skill audit.py from $SKILL_DIR" >&2
    echo "  Checked local create-skill, repo-local .codex/.claude, and user-level ~/.codex/skills / ~/.claude/skills" >&2
    exit 2
fi

set +e
python3 "$AUDIT" "$SKILL_DIR" "$@"
EXIT=$?
set -e

if [ "$EXIT" -ne 0 ]; then
    CREATE_SKILL_DIR="$(dirname "$(dirname "$AUDIT")")"
    cat >&2 <<EOF

────────────────────────────────────────────────────────────────────
Hard findings detected in skill: $SKILL_NAME

Most skill findings need editorial judgment — they are not safely
auto-fixable. To resolve them, hand this skill to the create-skill
Optimize lane:

  1. Run /create-skill and pick "Optimize" (or type "optimize $SKILL_NAME")
  2. The Optimize lane reads this audit output as input and walks you
     through the per-finding fix using:
       $CREATE_SKILL_DIR/references/optimize.md

For per-check rationale and fix recipes:
  cat $CREATE_SKILL_DIR/references/checklist.md
────────────────────────────────────────────────────────────────────
EOF
    exit "$EXIT"
fi

python3 "$SKILL_DIR/scripts/test_session_orchestrate.py"
