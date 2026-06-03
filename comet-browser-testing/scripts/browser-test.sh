#!/bin/bash
# Phase 2: Comet Browser Testing
# Executes Comet-based browser testing with validated prompts
# This script outputs the Comet prompt to be used with MCP tools

set -e

TEST_TYPE="${1:-visual}"
URL="${2:-http://localhost:3000}"
EXTRA="${3:-}"

echo "=== Phase 2: Comet Browser Testing ==="
echo "URL: $URL"
echo "Test Type: $TEST_TYPE"
echo ""

# Select prompt template based on test type
case "$TEST_TYPE" in
  "load"|"initial")
    PROMPT="Navigate to $URL and report:
1. Does the page fully load? (yes/no)
2. Any console errors? (list them)
3. What specific elements are visible? (describe 3-5 elements)
4. Is there a loading state that doesn't resolve? (describe)
5. What is the page title? (exact text)"
    ;;

  "style"|"styling")
    PROMPT="Navigate to $URL and check styling:
1. Are there any obvious layout breaks? (describe specifically)
2. Do colors/theme appear consistent? (yes/no - describe which elements)
3. Are there any unstyled elements? (describe - raw HTML visible?)
4. Is text readable against backgrounds? (yes/no - which text/background)
5. Any obvious visual bugs? (broken images, misaligned elements)"
    ;;

  "func"|"functionality")
    PROMPT="Navigate to $URL and test $EXTRA:
1. Can you see $EXTRA? (yes/no - describe appearance)
2. Click the $EXTRA - what happens? (describe exact behavior)
3. Any console errors on click? (list them)
4. Does the action complete? (describe result - URL change, modal, etc.)
5. Is there a loading state? (describe)"
    ;;

  "nav"|"navigation")
    PROMPT="Navigate to $URL and test navigation:
1. Click on $EXTRA
2. Does the URL change? (yes/no - what is the new URL?)
3. Does the new page load? (yes/no - describe what you see)
4. Any console errors during navigation? (list them)
5. Is there a page transition animation? (describe)
6. Can you click browser back button? (what happens?)"
    ;;

  "complete"|"visual")
    PROMPT="Navigate to $URL and verify:
1. Are all expected sections visible? (describe which sections)
2. Any broken images or icons? (describe - alt text, placeholder boxes)
3. Is content truncated or hidden? (describe - text cut off, overflow)
4. Any obvious visual bugs? (misaligned, overlapping, missing spacing)
5. Does scrolling work? (describe behavior)
6. Any console errors? (list them)"
    ;;

  "feature")
    PROMPT="Navigate to $URL and test $EXTRA:
1. What specific action did you take? (describe step by step)
2. What was the expected behavior? (describe what should happen)
3. What actually happened? (describe exactly what you observed)
4. Any console errors during test? (list full error messages)
5. Is there visual feedback? (describe - toast, modal, redirect, etc.)"
    ;;

  *)
    echo "Unknown test type: $TEST_TYPE"
    echo "Valid types: load, style, func, nav, complete, feature"
    echo "Usage: $0 <type> <url> [extra]"
    exit 1
    ;;
esac

echo "--- Comet Prompt ---"
echo "$PROMPT"
echo ""
echo "--- MCP Commands ---"
echo "# Connect to Comet"
echo "mcp__comet-bridge__comet_connect()"
echo ""
echo "# Send test task"
echo "mcp__comet-bridge__comet_ask(prompt=\"$(echo "$PROMPT" | tr '\n' ' ' | sed 's/"/\\"/g')\", newChat=true, timeout=30000)"
echo ""
echo "# Capture screenshot"
echo "mcp__comet-bridge__comet_screenshot()"
