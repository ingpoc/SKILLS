#!/bin/bash
# Query traces by keyword/pattern
# Usage: query-traces.sh "SEARCH_TERM" [LIMIT]
# Output: Matching traces (summaries)

SEARCH="$1"
LIMIT="${2:-5}"
TRACES_DIR=".claude/traces"

if [ ! -d "$TRACES_DIR" ]; then
    echo "No traces found"
    exit 0
fi

echo "=== Searching traces for: $SEARCH ==="

# Simple grep-based search (could be replaced with vector search)
MATCHES=$(grep -l -i "$SEARCH" "$TRACES_DIR"/*.json 2>/dev/null | head -n "$LIMIT")

if [ -z "$MATCHES" ]; then
    echo "No matching traces found"
    exit 0
fi

COUNT=0
for trace in $MATCHES; do
    ((COUNT++))
    echo ""
    echo "--- Match $COUNT ---"
    jq '{id, timestamp, category, decision, outcome}' "$trace"
done

echo ""
echo "Found $COUNT matching traces"
