#!/usr/bin/env bash
# smart_setup.sh - Analyze codebase and create appropriate worktrees
# Usage: smart_setup.sh [base-branch] [target-dir]

set -eo pipefail

BASE_BRANCH="${1:-$(git branch --show-current)}"
TARGET_DIR="${2:-$(git rev-parse --show-toplevel)/.claude/worktrees}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPT_DIR="$(dirname "$0")"

echo "=== Smart Worktree Setup ==="
echo "Repository: $(basename "$REPO_ROOT")"
echo "Base branch: $BASE_BRANCH"
echo ""

# Run analysis
echo "Step 1: Analyzing codebase..."
ANALYSIS=$("$SCRIPT_DIR/analyze_codebase.sh" "$REPO_ROOT")
echo ""

# Parse analysis
TOTAL_FILES=$(echo "$ANALYSIS" | jq -r '.total_files')
FEATURES=$(echo "$ANALYSIS" | jq -r '.features | join(", ")')
RECOMMENDED_AGENTS=$(echo "$ANALYSIS" | jq -r '.recommended_agents')

echo "Step 2: Analysis Results"
echo "  Total source files: $TOTAL_FILES"
echo "  Detected features: $FEATURES"
echo ""

# Filter agents by confidence (only high and medium)
echo "Step 3: Selecting agents..."
SELECTED_AGENTS=()

while IFS= read -r agent; do
    [[ -z "$agent" ]] && continue
    name=$(echo "$agent" | cut -d: -f1)
    agent_type=$(echo "$agent" | cut -d: -f2)
    focus=$(echo "$agent" | cut -d: -f3)
    confidence=$(echo "$agent" | cut -d: -f4)

    if [[ "$confidence" == "high" ]] || [[ "$confidence" == "medium" ]]; then
        SELECTED_AGENTS+=("$name:$agent_type:$focus:$confidence")
        echo "  ✅ $name ($agent_type, focus: $focus, confidence: $confidence)"
    else
        echo "  ⏭️  $name (skipped - low confidence)"
    fi
done <<< "$(echo "$RECOMMENDED_AGENTS" | jq -r '.[]')"

echo ""
echo "Step 4: Creating worktrees..."
echo "Target directory: $TARGET_DIR"
mkdir -p "$TARGET_DIR"

# Create worktrees for selected agents
CREATED_COUNT=0
for agent_config in "${SELECTED_AGENTS[@]}"; do
    name=$(echo "$agent_config" | cut -d: -f1)
    agent_type=$(echo "$agent_config" | cut -d: -f2)
    focus=$(echo "$agent_config" | cut -d: -f3)
    confidence=$(echo "$agent_config" | cut -d: -f4)

    worktree_path="$TARGET_DIR/$name"
    branch_name="worktree/$name-$(date +%Y%m%d%H%M%S)"

    echo ""
    echo "Creating: $name"
    echo "  Path: $worktree_path"
    echo "  Branch: $branch_name"

    if [[ -d "$worktree_path" ]]; then
        echo "  ⚠️  Already exists, skipping..."
        continue
    fi

    # Create worktree with new branch
    if git worktree add -b "$branch_name" "$worktree_path" "$BASE_BRANCH" 2>/dev/null; then
        :
    else
        echo "  ⚠️  Branch may exist, trying without -b..."
        git worktree add "$worktree_path" "$BASE_BRANCH"
    fi

    # Create isolated .claude directory
    mkdir -p "$worktree_path/.claude/sessions"
    mkdir -p "$worktree_path/.claude/tasks"

    # Create worktree metadata with analysis info
    cat > "$worktree_path/.claude/worktree-metadata.json" <<EOF
{
    "name": "$name",
    "agent_type": "$agent_type",
    "focus": "$focus",
    "confidence": "$confidence",
    "base_branch": "$BASE_BRANCH",
    "created_at": "$(date -Iseconds)",
    "repo_root": "$REPO_ROOT",
    "detected_features": $(echo "$ANALYSIS" | jq '.features'),
    "total_files": $TOTAL_FILES
}
EOF

    echo "  ✅ Created"
    ((CREATED_COUNT++))
done

echo ""
echo "=== Setup Complete ==="
echo "Created $CREATED_COUNT worktrees"
echo ""
git worktree list

# Save analysis for later use
echo "$ANALYSIS" > "$TARGET_DIR/analysis.json"
echo ""
echo "Analysis saved to: $TARGET_DIR/analysis.json"
echo ""
echo "Next: Spawn agents using Task tool with prompts from references/agent_prompts.md"
