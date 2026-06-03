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

# MCP servers - verify .mcp.json exists with required servers
MCP_CHECK="false"
if [ -f ".mcp.json" ]; then
  # Check for token-efficient MCP
  if jq -e '.mcpServers["token-efficient"]' .mcp.json >/dev/null 2>&1; then
    # Check for context-graph MCP
    if jq -e '.mcpServers["context-graph"]' .mcp.json >/dev/null 2>&1; then
      MCP_CHECK="true"
    fi
  fi
fi

if [ "$MCP_CHECK" = "true" ]; then
  echo "✅ MCP servers configured (.mcp.json exists with token-efficient + context-graph)"
  ((PASS++))
else
  echo "❌ MCP servers not configured"
  echo "   Run: ~/.claude/skills/mcp-setup/scripts/setup-all.sh"
  ((FAIL++))
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
  echo ""
  echo "✅ All INIT criteria met!"
  echo ""
  echo "=== Initialization Complete ==="
  echo ""
  echo "Next step: Orchestrator skill will now take over session management."
  echo "The orchestrator will:"
  echo "  1. Verify dev environment health"
  echo "  2. Check current state (INIT)"
  echo "  3. Load implementation skill to start feature development"
  echo ""
  echo "Ready to proceed → Use /orchestrator skill to continue"

  exit 0
else
  echo ""
  echo "❌ Some checks failed"
  exit 1
fi
