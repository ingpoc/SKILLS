#!/bin/bash
# Pre-Tool Guard: Consolidated hook for two-agent system enforcement
# Blocks: Direct implementation by Opus (when progress files exist)
# Updates: Session heartbeat
#
# Exit codes: 0 = allow, 2 = block with message
#
# This hook only activates when .claude/progress/ exists in the project

# Read hook input from stdin (JSON with tool_name, tool_input, etc.)
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty')

# Get file path for Edit/Write tools
FILE_PATH=""
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty')
fi

# Check if we're in a Task tool context (agent delegation)
IS_AGENT_CONTEXT=$(echo "$INPUT" | jq -r '.agent_context // .is_agent // empty')
TASK_IN_PROGRESS=$(echo "$INPUT" | jq -r '.task_id // empty')

# If we're in an agent context or a task is running, allow implementation files
if [ -n "$IS_AGENT_CONTEXT" ] || [ -n "$TASK_IN_PROGRESS" ]; then
    # Allow all edits in agent context
    exit 0
fi

# ============================================================
# GUARD: Block Opus from editing implementation files directly
# Only active when .claude/progress/feature-list.json exists
# ============================================================
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
    # Check if editing source files (common patterns)
    if echo "$FILE_PATH" | grep -qE '^.*(src/|lib/|app/|components/|pages/).*\.(ts|tsx|js|jsx|py|rb|go|rs)$'; then

        # Check for bypass keywords in temp file (stored by UserPromptSubmit hook)
        BYPASS_FILE="/tmp/claude-hook-bypass-$$"
        if [ -f "$BYPASS_FILE" ]; then
            BYPASS=$(cat "$BYPASS_FILE")
            if echo "$BYPASS" | grep -qiE '(quick fix|direct edit|no progress|bypass hook)'; then
                # Bypass allowed
                rm -f "$BYPASS_FILE"
                exit 0
            fi
        fi

        # Only enforce if progress files exist (project is using two-agent system)
        if [ -f ".claude/progress/feature-list.json" ]; then
            PENDING=$(python3 -c "
import json
try:
    with open('.claude/progress/feature-list.json') as f:
        data = json.load(f)
    # Count pending across all categories
    count = 0
    for cat in data.get('categories', {}).values():
        for f in cat.get('features', []):
            if f.get('status') == 'pending':
                count += 1
    print(count)
except:
    print(0)
" 2>/dev/null)

            if [ "$PENDING" -gt 0 ]; then
                echo '{"decision": "block", "reason": "⛔ BLOCKED: Opus editing implementation files directly.\n\n**Two-Agent System Enforced:**\n- Use `coding-agent` for implementation\n- Opus role: orchestrate, explore, verify\n\n**To bypass:** Include \"quick fix\", \"direct edit\", or \"no progress\" in your prompt.\n\n**Pending features:** '"$PENDING"'"}'
                exit 0
            fi
        fi
    fi
fi

# ============================================================
# HEARTBEAT: Update session state (keeps session-state.json fresh)
# ============================================================
if [ -f ".claude/progress/session-state.json" ]; then
    CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    python3 -c "
import json
try:
    with open('.claude/progress/session-state.json', 'r') as f:
        data = json.load(f)
    if 'heartbeat' not in data:
        data['heartbeat'] = {}
    data['heartbeat']['last_heartbeat'] = '$CURRENT_TIME'
    data['status'] = 'active'
    with open('.claude/progress/session-state.json', 'w') as f:
        json.dump(data, f, indent=2)
except:
    pass
" 2>/dev/null
fi

# Allow tool to proceed
exit 0
