#!/usr/bin/env python3
"""
PostToolUse hook: Warn when operations use >10K tokens
Non-blocking - just logs warning
"""

import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_result = input_data.get("tool_result", {})
    tool_name = input_data.get("tool_name", "")

    result_str = json.dumps(tool_result)
    if "input_tokens" in result_str or "output_tokens" in result_str:
        try:
            input_tokens = tool_result.get("input_tokens", 0)
            output_tokens = tool_result.get("output_tokens", 0)
            total = input_tokens + output_tokens

            if total > 10000:
                print(f"HIGH TOKEN USAGE: {tool_name} used {total:,} tokens", file=sys.stderr)
        except:
            pass

    sys.exit(0)

if __name__ == "__main__":
    main()
