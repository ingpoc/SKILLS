#!/bin/bash
# Create feature-list.json from requirements
# Usage: ./create-feature-list.sh [features.md|features.json]
# Responsibility: Feature breakdown (INIT state)

set -e

FEATURES_INPUT="${1:-}"
OUTPUT_FILE=".claude/progress/feature-list.json"
mkdir -p .claude/progress

# ─────────────────────────────────────────────────────────────────
# Parse from file if provided
# ─────────────────────────────────────────────────────────────────

if [ -n "$FEATURES_INPUT" ] && [ -f "$FEATURES_INPUT" ]; then
    echo "Parsing features from: $FEATURES_INPUT"
    
    if [[ "$FEATURES_INPUT" == *.json ]]; then
        cp "$FEATURES_INPUT" "$OUTPUT_FILE"
        echo "Copied JSON features to $OUTPUT_FILE"
        jq '.features | length' "$OUTPUT_FILE" | xargs -I{} echo "Features: {}"
        exit 0
    fi
    
    # Parse markdown list items
    echo '{"features": [' > "$OUTPUT_FILE"
    FIRST=true
    ID=1
    
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        
        FEAT_ID=$(printf "feat-%03d" $ID)
        DESC=$(echo "$line" | sed 's/^[[:space:]]*[-*+0-9.]\+[[:space:]]*//' | sed 's/"/\\"/g')
        
        [ "$FIRST" = true ] && FIRST=false || echo "," >> "$OUTPUT_FILE"
        
        echo "  {\"id\": \"$FEAT_ID\", \"description\": \"$DESC\", \"priority\": $ID, \"status\": \"pending\", \"tier\": \"mvp\"}" >> "$OUTPUT_FILE"
        ((ID++))
    done < <(grep -E '^\s*[-*+]|\d+\.' "$FEATURES_INPUT")
    
    echo '], "metadata": {"created": "'$(date -Iseconds)'", "version": "1.0"}}' >> "$OUTPUT_FILE"
    jq '.' "$OUTPUT_FILE" > /tmp/fl.tmp && mv /tmp/fl.tmp "$OUTPUT_FILE"
    
    echo "Created $((ID-1)) features in $OUTPUT_FILE"
    exit 0
fi

# ─────────────────────────────────────────────────────────────────
# Create template if no input
# ─────────────────────────────────────────────────────────────────

if [ -f "$OUTPUT_FILE" ]; then
    echo "Feature list exists: $OUTPUT_FILE"
    jq '.features | length' "$OUTPUT_FILE" | xargs -I{} echo "Features: {}"
    exit 0
fi

cat > "$OUTPUT_FILE" << EOF
{
  "features": [],
  "metadata": {
    "created": "$(date -Iseconds)",
    "version": "1.0"
  }
}
EOF
echo "Created empty feature list: $OUTPUT_FILE"
echo "Add features with: jq '.features += [{...}]' $OUTPUT_FILE"
