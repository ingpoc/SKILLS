#!/bin/bash
# Phase 3: Learning Loop - Store Findings
# Stores browser testing findings in context graph
# This script outputs the MCP command to store the trace

set -e

ISSUE_TYPE="${1:-frontend}"
DESCRIPTION="${2:-Issue found during browser testing}"
OUTCOME="${3:-pending}"

echo "=== Phase 3: Learning Loop ==="
echo "Category: $ISSUE_TYPE"
echo "Outcome: $OUTCOME"
echo "Description: $DESCRIPTION"
echo ""

# Validate category
case "$ISSUE_TYPE" in
  "frontend"|"hydration"|"css"|"framework"|"testing"|"deployment")
    # Valid category
    ;;
  *)
    echo "Warning: Category '$ISSUE_TYPE' not in standard list"
    echo "Valid: frontend, hydration, css, framework, testing, deployment"
    ;;
esac

# Validate outcome
case "$OUTCOME" in
  "pending"|"success"|"failure")
    # Valid outcome
    ;;
  *)
    echo "Warning: Outcome '$OUTCOME' not valid"
    echo "Valid: pending, success, failure"
    OUTCOME="pending"
    ;;
esac

echo "--- MCP Command ---"
echo "mcp__context-graph__context_store_trace("
echo "  decision=\"$DESCRIPTION\","
echo "  category=\"$ISSUE_TYPE\","
echo "  outcome=\"$OUTCOME\""
echo ")"
echo ""
echo "--- After Fix, Update Outcome ---"
echo "# Replace trace_id with actual ID from store_trace result"
echo "mcp__context-graph__context_update_outcome("
echo "  trace_id=\"trace_abc123...\","
echo "  outcome=\"success\""
echo ")"
