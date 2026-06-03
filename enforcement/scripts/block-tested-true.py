#!/usr/bin/env python3
"""
PreToolUse hook: Block marking tested:true without evidence
Exit 2 = block action
"""

import json
import sys
import os

input_data = json.load(sys.stdin)
tool_input = input_data.get("tool_input", {})
content = tool_input.get("content", "")

# Check if marking tested:true
if '"tested": true' in content or '"tested":true' in content:
    evidence_dir = "/tmp/test-evidence"
    results_file = os.path.join(evidence_dir, "results.json")

    if not os.path.exists(results_file):
        print("BLOCKED: Cannot mark tested:true without evidence", file=sys.stderr)
        print("Run tests and collect evidence to /tmp/test-evidence/results.json", file=sys.stderr)
        sys.exit(2)

    # Check if tests actually passed
    try:
        with open(results_file) as f:
            results = json.load(f)
        if not results.get("all_passed", False):
            print("BLOCKED: Cannot mark tested:true - tests did not pass", file=sys.stderr)
            print(f"Results: {json.dumps(results, indent=2)}", file=sys.stderr)
            sys.exit(2)
    except json.JSONDecodeError:
        print("BLOCKED: Invalid results.json format", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
