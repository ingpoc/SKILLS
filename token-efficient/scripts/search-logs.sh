#!/bin/bash
# Search logs with pattern (wrapper for MCP tool)
# Usage: search-logs.sh FILE PATTERN [LIMIT]
# Note: Actual processing uses MCP tool for token efficiency

FILE=$1
PATTERN=${2:-"ERROR"}
LIMIT=${3:-100}

if [ -z "$FILE" ]; then
    echo "Usage: search-logs.sh FILE PATTERN [LIMIT]"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

# Show file stats
LINES=$(wc -l < "$FILE")
SIZE=$(du -h "$FILE" | cut -f1)

echo "=== Log Search ==="
echo "File: $FILE"
echo "Size: $SIZE ($LINES lines)"
echo "Pattern: $PATTERN"
echo "Limit: $LIMIT"
echo ""

# Quick preview with grep
MATCHES=$(grep -c "$PATTERN" "$FILE" 2>/dev/null || echo 0)
echo "Quick count: ~$MATCHES matches"
echo ""

cat << EOF
For token-efficient processing, use MCP tool:

mcp__token_efficient__process_logs(
    file_path="$FILE",
    pattern="$PATTERN",
    limit=$LIMIT,
    context_lines=2,
    response_format="summary"
)

Token savings: ~95% (returns matches, not full log)
EOF
