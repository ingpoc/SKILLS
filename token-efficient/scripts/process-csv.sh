#!/bin/bash
# Process CSV with filter (wrapper for MCP tool)
# Usage: process-csv.sh FILE [FILTER_EXPR] [LIMIT]
# Note: Actual processing uses MCP tool for token efficiency

FILE=$1
FILTER=${2:-""}
LIMIT=${3:-100}

if [ -z "$FILE" ]; then
    echo "Usage: process-csv.sh FILE [FILTER_EXPR] [LIMIT]"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

# Show file stats
LINES=$(wc -l < "$FILE")
SIZE=$(du -h "$FILE" | cut -f1)

echo "=== CSV Processing ==="
echo "File: $FILE"
echo "Size: $SIZE ($LINES lines)"
echo "Filter: ${FILTER:-none}"
echo "Limit: $LIMIT"
echo ""

cat << EOF
For token-efficient processing, use MCP tool:

mcp__token_efficient__process_csv(
    file_path="$FILE",
    filter_expr="$FILTER",
    limit=$LIMIT,
    response_format="summary"
)

Token savings: ~99% (returns summary, not raw data)
EOF
