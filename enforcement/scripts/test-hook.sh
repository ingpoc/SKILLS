#!/bin/bash
# Test enforcement hooks with sample input
# Usage: ./test-hook.sh <hook-script> [test-name]

HOOK_SCRIPT="$1"
TEST_NAME="${2:-default}"

if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "Error: Hook script not found: $HOOK_SCRIPT"
    echo "Usage: ./test-hook.sh <path-to-hook.py> [test-name]"
    exit 1
fi

# Test inputs for different scenarios
case $TEST_NAME in
    tested-true)
        # Test block-tested-true.py
        echo '{"tool_name":"Write","tool_input":{"file_path":".claude/progress/feature-list.json","content":"{\"tested\":true}"}}' | python3 "$HOOK_SCRIPT"
        ;;

    tested-with-evidence)
        # Setup evidence first
        mkdir -p /tmp/test-evidence
        echo '{"all_passed":true}' > /tmp/test-evidence/results.json
        echo '{"tool_name":"Write","tool_input":{"file_path":".claude/progress/feature-list.json","content":"{\"tested\":true}"}}' | python3 "$HOOK_SCRIPT"
        ;;

    invalid-transition)
        # Test validate-transition.py (assuming START state)
        echo '{"tool_name":"Write","tool_input":{"file_path":".claude/progress/state.json","content":"{\"state\":\"COMPLETE\"}"}}' | python3 "$HOOK_SCRIPT"
        ;;

    valid-transition)
        echo '{"tool_name":"Write","tool_input":{"file_path":".claude/progress/state.json","content":"{\"state\":\"IMPLEMENT\"}"}}' | python3 "$HOOK_SCRIPT"
        ;;

    *)
        echo "Available test cases:"
        echo "  tested-true       - Test blocking tested:true without evidence"
        echo "  tested-with-evidence - Test allowing tested:true with evidence"
        echo "  invalid-transition  - Test blocking invalid state transition"
        echo "  valid-transition    - Test allowing valid state transition"
        echo ""
        echo "Usage: ./test-hook.sh <hook.py> <test-name>"
        exit 1
        ;;
esac

EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 2 ]; then
    echo "✓ Hook BLOCKED as expected (exit code 2)"
elif [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Hook ALLOWED (exit code 0)"
else
    echo "⚠️  Unexpected exit code: $EXIT_CODE"
fi
