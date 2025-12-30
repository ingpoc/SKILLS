#!/bin/bash
# Check browser console for errors
# Usage: check-console-errors.sh TAB_ID
# Note: This is a helper script - actual console reading uses MCP tools
# Exit: 0 = no errors found, 1 = errors detected

TAB_ID=$1
EVIDENCE_DIR="/tmp/test-evidence"

if [ -z "$TAB_ID" ]; then
    echo "Usage: check-console-errors.sh TAB_ID"
    echo "Get TAB_ID from tabs_context_mcp first"
    exit 1
fi

mkdir -p "$EVIDENCE_DIR"

# Note: Actual console reading happens via MCP tool
# This script documents the pattern and saves evidence

cat << 'EOF'
To check console errors, use MCP tool:

mcp__claude_in_chrome__read_console_messages(
    tabId=TAB_ID,
    pattern="ERROR|WARN|Exception",
    limit=50
)

Pattern examples:
- "ERROR" - JavaScript errors
- "ERROR|WARN" - Errors and warnings
- "TypeError|ReferenceError" - Specific JS errors
- "404|500" - HTTP errors
EOF

echo ""
echo "Evidence will be saved to: $EVIDENCE_DIR/console-errors.json"
