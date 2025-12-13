#!/bin/bash
# Session End Hook: Mark session as completed for proper recovery detection
#
# Updates session-state.json to status: "completed"
# This enables the session-progress-check hook to detect abnormal exits

if [ -f ".claude/progress/session-state.json" ]; then
    CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    python3 -c "
import json
try:
    with open('.claude/progress/session-state.json', 'r') as f:
        data = json.load(f)
    data['status'] = 'completed'
    data['ended_at'] = '$CURRENT_TIME'
    if 'heartbeat' not in data:
        data['heartbeat'] = {}
    data['heartbeat']['last_heartbeat'] = '$CURRENT_TIME'
    with open('.claude/progress/session-state.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('✓ Session marked as completed')
except Exception as e:
    print(f'Warning: Could not update session state: {e}')
" 2>/dev/null
fi

exit 0
