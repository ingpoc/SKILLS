#!/usr/bin/env bash
set -eu

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"

find_audit_py() {
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
    exit 2
fi

set +e
python3 "$AUDIT" "$SKILL_DIR" "$@"
EXIT=$?
set -e

if [ "$EXIT" -ne 0 ]; then
    cat >&2 <<EOF

Hard findings detected in skill: $SKILL_NAME
Run create-skill Optimize lane against this skill.
EOF
fi

exit "$EXIT"
