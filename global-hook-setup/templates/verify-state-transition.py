#!/usr/bin/env python3
"""
Global Hook: verify-state-transition.py

Blocks invalid state machine transitions.

Valid transitions:
  START → INIT, IMPLEMENT
  INIT → IMPLEMENT
  IMPLEMENT → TEST
  TEST → IMPLEMENT, COMPLETE
  COMPLETE → (none)

Invalid transitions that are blocked:
  START → IMPLEMENT (skip init)
  FIX_BROKEN → IMPLEMENT (skip fixing)
  INIT → COMPLETE (skip implementation)
  IMPLEMENT → COMPLETE (skip testing)
  TEST → COMPLETE (without passing tests)
"""

import json
import sys

# Valid state transitions
VALID_TRANSITIONS = {
    "START": ["INIT", "IMPLEMENT"],
    "FIX_BROKEN": ["INIT"],
    "INIT": ["IMPLEMENT"],
    "IMPLEMENT": ["TEST"],
    "TEST": ["IMPLEMENT", "COMPLETE"],
    "COMPLETE": []
}

def main():
    # Read stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Not JSON, not for us

    # Only process state.json writes
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if "state.json" not in file_path:
        sys.exit(0)

    # Get content from Write (content) or Edit (new_string)
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    # Parse states
    try:
        new_state_data = json.loads(content) if content else {}
        new_state = new_state_data.get("state", "")

        # Read current state
        try:
            with open(file_path, "r") as f:
                current_data = json.load(f)
                current_state = current_data.get("state", "START")
        except (FileNotFoundError, json.JSONDecodeError):
            current_state = "START"

        # Validate transition
        if current_state == new_state:
            sys.exit(0)  # No change, valid

        valid_next = VALID_TRANSITIONS.get(current_state, [])

        if new_state not in valid_next:
            print(f"BLOCKED: Invalid state transition {current_state} → {new_state}", file=sys.stderr)
            print(f"Valid transitions from {current_state}: {valid_next}", file=sys.stderr)
            sys.exit(2)

    except (json.JSONDecodeError, KeyError):
        pass  # Can't parse, allow

    sys.exit(0)

if __name__ == "__main__":
    main()
