#!/usr/bin/env bash
# Verify INIT state exit criteria
# This script checks all requirements for INIT state completion

echo "=== INIT State Verification ==="
echo ""

PASS=0
FAIL=0

check() {
  if eval "$1"; then
    echo "✅ $2"
    ((PASS++))
  else
    echo "❌ $2"
    ((FAIL++))
  fi
}

# Project structure
check "[ -f '.claude/CLAUDE.md' ]" ".claude/CLAUDE.md exists"
check "[ -f '.claude/config/project.json' ]" ".claude/config/project.json exists"
check "[ -d '.claude/progress/' ]" ".claude/progress/ directory exists"

# Feature list
check "[ -f '.claude/progress/feature-list.json' ]" "feature-list.json exists"
check "jq -e '.features | length > 0' .claude/progress/feature-list.json >/dev/null 2>&1" "feature-list has features"
check "jq -e '.features[0] | has(\"id\", \"description\", \"priority\", \"status\")' .claude/progress/feature-list.json >/dev/null 2>&1" "features have required fields"

# State
check "[ -f '.claude/progress/state.json' ]" "state.json exists"
check "jq -e '.state == \"INIT\"' .claude/progress/state.json >/dev/null 2>&1" "state is INIT"

# Global hooks (expanded path)
GLOBAL_HOOKS="$HOME/.claude/hooks"
check "[ -d '$GLOBAL_HOOKS' ]" "global hooks directory exists"
check "[ -f '$GLOBAL_HOOKS/verify-state-transition.py' ]" "verify-state-transition.py installed"
check "[ -f '$GLOBAL_HOOKS/require-commit-before-tested.py' ]" "require-commit-before-tested.py installed"

# Project hooks
check "[ -d '.claude/hooks/' ]" "project hooks directory exists"
check "[ -f '.claude/hooks/verify-tests.py' ]" "verify-tests.py installed"
check "[ -f '.claude/hooks/session-entry.sh' ]" "session-entry.sh installed"

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
  echo ""
  echo "✅ All INIT criteria met!"
  exit 0
else
  echo ""
  echo "❌ Some checks failed"
  exit 1
fi
