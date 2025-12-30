#!/bin/bash
# Run unit tests based on project config
# Exit: 0 = all pass, 1 = failures
# Config: .claude/config/project.json → test_command

EVIDENCE_DIR="/tmp/test-evidence"
mkdir -p "$EVIDENCE_DIR"

# ─────────────────────────────────────────────────────────────────
# Config helper (self-contained)
# ─────────────────────────────────────────────────────────────────
CONFIG="$PWD/.claude/config/project.json"
get_config() { jq -r ".$1 // empty" "$CONFIG" 2>/dev/null || echo "$2"; }

# ─────────────────────────────────────────────────────────────────
# Get test command (config → auto-detect → fallback)
# ─────────────────────────────────────────────────────────────────
TEST_CMD=$(get_config "test_command" "")

if [ -z "$TEST_CMD" ]; then
    # Auto-detect based on project files
    if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
        TEST_CMD="pytest -q --tb=short"
    elif [ -f "Cargo.toml" ]; then
        TEST_CMD="cargo test"
    elif [ -f "go.mod" ]; then
        TEST_CMD="go test ./..."
    elif [ -f "package.json" ]; then
        TEST_CMD="npm test"
    else
        TEST_CMD="echo 'No test command configured in .claude/config/project.json'"
    fi
fi

# ─────────────────────────────────────────────────────────────────
# Run tests
# ─────────────────────────────────────────────────────────────────
echo "=== Running Unit Tests ==="
echo "Command: $TEST_CMD"

RESULT=0
eval "$TEST_CMD" 2>&1 | tee "$EVIDENCE_DIR/test-output.log" || RESULT=$?

# Save evidence
cat > "$EVIDENCE_DIR/unit-tests.json" << EOF
{
  "unit_tests": {
    "passed": $([ $RESULT -eq 0 ] && echo true || echo false),
    "exit_code": $RESULT,
    "command": "$TEST_CMD"
  }
}
EOF

exit $RESULT
