#!/bin/bash
# Validate prompt hash matches declared hash
# Usage: validate-prompt.sh PROMPT_FILE
# Exit: 0 = valid, 1 = invalid/no hash

PROMPT_FILE=${1:-"PROMPT.md"}

if [ ! -f "$PROMPT_FILE" ]; then
    echo "ERROR: File not found: $PROMPT_FILE"
    exit 1
fi

# Extract declared hash from header
DECLARED=$(grep -o 'SHA256: [a-f0-9]\+' "$PROMPT_FILE" | head -1 | cut -d' ' -f2)

if [ -z "$DECLARED" ]; then
    echo "WARN: No hash declared in $PROMPT_FILE"
    exit 0  # No hash = no validation (allow)
fi

# Calculate actual hash (strip comment lines)
CONTENT=$(grep -v '^<!--' "$PROMPT_FILE" | grep -v '^$')
ACTUAL=$(echo "$CONTENT" | shasum -a 256 | cut -d' ' -f1)

# Compare (declared may be truncated)
if [[ "$ACTUAL" == "$DECLARED"* ]]; then
    echo "PASS: Hash valid for $PROMPT_FILE"
    exit 0
else
    echo "FAIL: Hash mismatch in $PROMPT_FILE"
    echo "  Declared: $DECLARED"
    echo "  Actual:   ${ACTUAL:0:32}..."
    exit 1
fi
