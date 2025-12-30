#!/usr/bin/env python3
"""
PreToolUse hook: Validate state transitions
Exit 2 = block invalid transition
"""

import json
import sys
import os

VALID_TRANSITIONS = {
    "START": ["INIT", "IMPLEMENT"],
    "INIT": ["IMPLEMENT"],
    "IMPLEMENT": ["TEST"],
    "TEST": ["IMPLEMENT", "COMPLETE"],
    "COMPLETE": []
}

input_data = json.load(sys.stdin)
tool_input = input_data.get("tool_input", {})
content = tool_input.get("content", "")

# Check if this is a state change
if '"state":' not in content:
    sys.exit(0)

# Get current state
state_file = ".claude/progress/state.json"
current_state = "START"
if os.path.exists(state_file):
    try:
        with open(state_file) as f:
            current_state = json.load(f).get("state", "START")
    except:
        pass

# Extract new state from content
import re
match = re.search(r'"state":\s*"(\w+)"', content)
if not match:
    sys.exit(0)

new_state = match.group(1)

# Validate transition
valid = VALID_TRANSITIONS.get(current_state, [])
if new_state not in valid:
    print(f"BLOCKED: Invalid transition {current_state} -> {new_state}", file=sys.stderr)
    print(f"Valid transitions from {current_state}: {valid}", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
