#!/usr/bin/env bash
# aggregate_results.sh - Collect results from all worktrees
# Usage: aggregate_results.sh <target-dir>

set -euo pipefail

TARGET_DIR="${1:-$(git rev-parse --show-toplevel)/.claude/worktrees}"
OUTPUT_DIR="$TARGET_DIR/aggregated"

echo "=== Aggregating Worktree Results ==="

mkdir -p "$OUTPUT_DIR"

# Collect findings from each worktree
SUMMARY_FILE="$OUTPUT_DIR/summary.md"
PRIORITIZED_FILE="$OUTPUT_DIR/prioritized_actions.md"

echo "# Worktree Orchestrator Summary" > "$SUMMARY_FILE"
echo "Generated: $(date -Iseconds)" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Process each worktree
for worktree in "$TARGET_DIR"/*/; do
    [[ -d "$worktree" ]] || continue
    name=$(basename "$worktree")
    [[ "$name" == "aggregated" ]] && continue

    echo "Processing: $name"

    # Read metadata
    metadata_file="$worktree/.claude/worktree-metadata.json"
    if [[ -f "$metadata_file" ]]; then
        focus=$(jq -r '.focus' "$metadata_file" 2>/dev/null || echo "unknown")
        agent_type=$(jq -r '.agent_type' "$metadata_file" 2>/dev/null || echo "unknown")
    else
        focus="unknown"
        agent_type="unknown"
    fi

    # Append to summary
    echo "" >> "$SUMMARY_FILE"
    echo "## $name ($agent_type: $focus)" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    # Check for output files
    for output in "findings.md" "architecture_review.md" "sdk_compliance.md" "test_report.md"; do
        if [[ -f "$worktree/$output" ]]; then
            echo "### $output" >> "$SUMMARY_FILE"
            cat "$worktree/$output" >> "$SUMMARY_FILE"
            echo "" >> "$SUMMARY_FILE"
        fi
    done

    # Check for patches
    if [[ -d "$worktree/patches" ]]; then
        patch_count=$(find "$worktree/patches" -name "*.patch" 2>/dev/null | wc -l)
        echo "**Patches:** $patch_count" >> "$SUMMARY_FILE"
    fi
done

# Generate prioritized actions
echo "# Prioritized Actions" > "$PRIORITIZED_FILE"
echo "Generated: $(date -Iseconds)" >> "$PRIORITIZED_FILE"
echo "" >> "$PRIORITIZED_FILE"

# Extract high-priority items (simplified - real version would parse severity)
echo "## Security (review-security)" >> "$PRIORITIZED_FILE"
grep -i "critical\|high\|severity" "$TARGET_DIR/review-security/findings.md" 2>/dev/null >> "$PRIORITIZED_FILE" || echo "No critical findings" >> "$PRIORITIZED_FILE"

echo "" >> "$PRIORITIZED_FILE"
echo "## Performance (review-performance)" >> "$PRIORITIZED_FILE"
grep -i "critical\|high\|impact" "$TARGET_DIR/review-performance/findings.md" 2>/dev/null >> "$PRIORITIZED_FILE" || echo "No critical findings" >> "$PRIORITIZED_FILE"

echo "" >> "$PRIORITIZED_FILE"
echo "## Architecture Recommendations" >> "$PRIORITIZED_FILE"
head -50 "$TARGET_DIR/architecture/architecture_review.md" 2>/dev/null >> "$PRIORITIZED_FILE" || echo "No architecture review" >> "$PRIORITIZED_FILE"

echo ""
echo "=== Aggregation Complete ==="
echo "Summary: $SUMMARY_FILE"
echo "Prioritized: $PRIORITIZED_FILE"
