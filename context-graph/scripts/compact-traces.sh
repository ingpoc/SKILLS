#!/bin/bash
# Compact old traces to save storage
# Usage: compact-traces.sh [DAYS_OLD]
# Output: Compaction summary

DAYS_OLD="${1:-7}"
TRACES_DIR=".claude/traces"
ARCHIVE_DIR=".claude/traces/archive"

mkdir -p "$ARCHIVE_DIR"

echo "=== Compacting traces older than $DAYS_OLD days ==="

# Find old traces
OLD_TRACES=$(find "$TRACES_DIR" -maxdepth 1 -name "*.json" -mtime +"$DAYS_OLD" 2>/dev/null)

if [ -z "$OLD_TRACES" ]; then
    echo "No traces older than $DAYS_OLD days"
    exit 0
fi

COUNT=0
for trace in $OLD_TRACES; do
    ((COUNT++))
    FILENAME=$(basename "$trace")

    # Extract just metadata (compact version)
    jq '{id, timestamp, category, decision, outcome}' "$trace" > "$ARCHIVE_DIR/$FILENAME"

    # Remove full trace
    rm "$trace"
done

echo "Compacted $COUNT traces to $ARCHIVE_DIR"
echo "Full traces removed, metadata preserved"

# Show archive size
du -sh "$ARCHIVE_DIR" 2>/dev/null
