#!/bin/bash
# Mark current feature as implemented
# Usage: mark-feature-complete.sh [FEATURE_ID]

FEATURE_ID=${1:-$(jq -r '.feature_id' .claude/progress/state.json)}
FEATURE_FILE=".claude/progress/feature-list.json"

if [ -z "$FEATURE_ID" ] || [ "$FEATURE_ID" = "null" ]; then
    echo "ERROR: No feature ID specified"
    exit 1
fi

if [ ! -f "$FEATURE_FILE" ]; then
    echo "ERROR: feature-list.json not found"
    exit 1
fi

# Update feature status
jq '(.features[] | select(.id == "'$FEATURE_ID'")).status = "implemented"' "$FEATURE_FILE" > /tmp/features.tmp && \
mv /tmp/features.tmp "$FEATURE_FILE"

# Update metadata
TOTAL=$(jq '.features | length' "$FEATURE_FILE")
COMPLETED=$(jq '[.features[] | select(.status == "implemented" or .status == "tested")] | length' "$FEATURE_FILE")

jq '.metadata.total = '$TOTAL' | .metadata.completed = '$COMPLETED'' "$FEATURE_FILE" > /tmp/features.tmp && \
mv /tmp/features.tmp "$FEATURE_FILE"

echo "Feature $FEATURE_ID marked as implemented"
jq '.features[] | select(.id == "'$FEATURE_ID'")' "$FEATURE_FILE"
