#!/bin/bash
# SessionStart hook: Check for existing progress files and detect abnormal exits
#
# This hook only activates when .claude/progress/ exists in the project

PROGRESS_DIR=".claude/progress"
FEATURE_FILE="$PROGRESS_DIR/feature-list.json"
SESSION_FILE="$PROGRESS_DIR/session-state.json"

# Check if progress infrastructure exists
if [ -d "$PROGRESS_DIR" ] && [ -f "$FEATURE_FILE" ] && [ -f "$SESSION_FILE" ]; then
    # Read session state
    STATUS=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('status', 'unknown'))" 2>/dev/null)
    LAST_HEARTBEAT=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('heartbeat', {}).get('last_heartbeat', 'unknown'))" 2>/dev/null)
    CURRENT_FEATURE=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('last_feature_id', 'None'))" 2>/dev/null)

    # Count features
    STATS=$(python3 -c "
import json
try:
    with open('$FEATURE_FILE') as f:
        data = json.load(f)
    total = 0
    completed = 0
    pending = 0
    for cat in data.get('categories', {}).values():
        for f in cat.get('features', []):
            total += 1
            if f.get('status') == 'completed':
                completed += 1
            elif f.get('status') == 'pending':
                pending += 1
    print(f'{total},{completed},{pending}')
except:
    print('0,0,0')
" 2>/dev/null)

    TOTAL=$(echo "$STATS" | cut -d',' -f1)
    COMPLETED=$(echo "$STATS" | cut -d',' -f2)
    PENDING=$(echo "$STATS" | cut -d',' -f3)

    if [ "$STATUS" = "active" ]; then
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  ⚠️  ABNORMAL EXIT DETECTED - RECOVERY REQUIRED              ║"
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║  Last heartbeat: $LAST_HEARTBEAT"
        echo "║  Feature in progress: $CURRENT_FEATURE"
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║  🤖 MANDATORY: Invoke coding-agent to recover                ║"
        echo "║                                                              ║"
        echo "║  Task tool → subagent_type='coding-agent'                    ║"
        echo "║  DO NOT implement directly as Opus                           ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
    elif [ "$PENDING" -gt 0 ]; then
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  📋 PENDING FEATURES DETECTED                                ║"
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║  Progress: $COMPLETED/$TOTAL completed, $PENDING pending"
        echo "╠══════════════════════════════════════════════════════════════╣"
        echo "║  🤖 MANDATORY: Invoke coding-agent to continue               ║"
        echo "║                                                              ║"
        echo "║  Task tool → subagent_type='coding-agent'                    ║"
        echo "║  DO NOT implement directly as Opus                           ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
    fi
fi

exit 0
