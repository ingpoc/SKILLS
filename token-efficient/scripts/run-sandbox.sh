#!/bin/bash
# Execute code in sandbox (wrapper for MCP tool)
# Usage: run-sandbox.sh FILE [LANGUAGE]
# Note: Actual execution uses MCP tool for token efficiency

FILE=$1
LANG=${2:-"python"}

if [ -z "$FILE" ]; then
    echo "Usage: run-sandbox.sh FILE [LANGUAGE]"
    echo "Languages: python, bash, node"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

# Detect language from extension
case "${FILE##*.}" in
    py) LANG="python" ;;
    sh) LANG="bash" ;;
    js) LANG="node" ;;
esac

LINES=$(wc -l < "$FILE")
SIZE=$(du -h "$FILE" | cut -f1)

echo "=== Sandbox Execution ==="
echo "File: $FILE"
echo "Language: $LANG"
echo "Size: $SIZE ($LINES lines)"
echo ""

cat << EOF
For token-efficient execution, use MCP tool:

mcp__token_efficient__execute_code(
    code=open("$FILE").read(),
    language="$LANG",
    response_format="summary",
    timeout=30
)

Token savings: ~98% (executes without loading to context)

Heredoc support for bash:
\`\`\`bash
<<EOF
your multi-line
script here
EOF
\`\`\`
EOF
