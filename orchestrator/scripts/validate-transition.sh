#!/bin/bash
# Validate state transition
# Usage: ./validate-transition.sh FROM TO
# Responsibility: State machine enforcement (ORCHESTRATOR)
# Exit: 0 = valid, 1 = invalid

set -e

FROM="${1:-}"
TO="${2:-}"

if [ -z "$FROM" ] || [ -z "$TO" ]; then
    echo "Usage: $0 FROM TO"
    echo "States: START, FIX_BROKEN, INIT, IMPLEMENT, TEST, COMPLETE"
    exit 1
fi

# Valid transitions (from DESIGN-v2.md state machine)
case "$FROM" in
    START)
        [[ "$TO" =~ ^(INIT|IMPLEMENT|FIX_BROKEN)$ ]] && exit 0
        ;;
    FIX_BROKEN)
        [[ "$TO" =~ ^(INIT|IMPLEMENT)$ ]] && exit 0
        ;;
    INIT)
        [[ "$TO" = "IMPLEMENT" ]] && exit 0
        ;;
    IMPLEMENT)
        [[ "$TO" = "TEST" ]] && exit 0
        ;;
    TEST)
        [[ "$TO" =~ ^(IMPLEMENT|COMPLETE)$ ]] && exit 0
        ;;
    COMPLETE)
        # No transitions from COMPLETE
        ;;
esac

echo "Invalid transition: $FROM → $TO"
echo "Valid from $FROM: $(case $FROM in
    START) echo "INIT, IMPLEMENT, FIX_BROKEN";;
    FIX_BROKEN) echo "INIT, IMPLEMENT";;
    INIT) echo "IMPLEMENT";;
    IMPLEMENT) echo "TEST";;
    TEST) echo "IMPLEMENT, COMPLETE";;
    COMPLETE) echo "(none)";;
esac)"
exit 1
