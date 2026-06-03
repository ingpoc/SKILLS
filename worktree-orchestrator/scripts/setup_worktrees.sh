#!/usr/bin/env bash
# setup_worktrees.sh - Create isolated git worktrees for parallel agent execution
# Usage: setup_worktrees.sh <base-branch> [target-dir]

set -eo pipefail

BASE_BRANCH="${1:-$(git branch --show-current)}"
TARGET_DIR="${2:-$(git rev-parse --show-toplevel)/.claude/worktrees}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"

echo "=== Worktree Orchestrator Setup ==="
echo "Repository: $REPO_NAME"
echo "Base branch: $BASE_BRANCH"
echo "Target directory: $TARGET_DIR"
echo ""

# Create target directory
mkdir -p "$TARGET_DIR"

# Worktree configurations: name:agent_type:focus
WORKTREES=(
    "review-security:code-review:security"
    "review-performance:code-review:performance"
    "architecture:plan:architecture"
    "sdk-verify:agent-sdk-verifier:sdk"
    "testing:testing:coverage"
)

# Create worktrees
for config in "${WORKTREES[@]}"; do
    name="${config%%:*}"
    rest="${config#*:}"
    agent_type="${rest%%:*}"
    focus="${rest##*:}"

    worktree_path="$TARGET_DIR/$name"
    branch_name="worktree/$name-$(date +%Y%m%d%H%M%S)"

    echo "Creating worktree: $name"
    echo "  Path: $worktree_path"
    echo "  Branch: $branch_name"
    echo "  Agent: $agent_type (focus: $focus)"

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

    # Create worktree metadata
    cat > "$worktree_path/.claude/worktree-metadata.json" <<EOF
{
    "name": "$name",
    "agent_type": "$agent_type",
    "focus": "$focus",
    "base_branch": "$BASE_BRANCH",
    "created_at": "$(date -Iseconds)",
    "repo_root": "$REPO_ROOT"
}
EOF

    echo "  ✅ Created"
done

echo ""
echo "=== Worktrees Ready ==="
git worktree list
echo ""
echo "Next: Spawn agents in each worktree using Task tool"
