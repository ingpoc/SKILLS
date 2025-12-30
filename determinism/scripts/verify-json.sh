#!/bin/bash
# Verify file is valid JSON
# Usage: verify-json.sh FILE
# Exit: 0 = valid, 1 = invalid

FILE=$1

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE"
    exit 1
fi

if python3 -c "import json; json.load(open('$FILE'))" 2>/dev/null; then
    echo "PASS: Valid JSON"
    exit 0
else
    echo "FAIL: Invalid JSON"
    exit 1
fi
