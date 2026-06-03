#!/usr/bin/env bash
# clean_worktrees.sh - Remove all worktrees created by orchestrator
# Usage: clean_worktrees.sh <target-dir>

set -euo pipefail

TARGET_DIR="${1:-$(git rev-parse --show-toplevel)/.claude/worktrees}"

echo "=== Cleaning Worktrees ==="

for worktree in "$TARGET_DIR"/*/; do
    [[ -d "$worktree" ]] || continue
    name=$(basename "$worktree")
    [[ "$name" == "aggregated" ]] && continue

    echo "Removing: $name"

    # Get branch name from worktree
    cd "$worktree"
    branch=$(git branch --show-current 2>/dev/null || echo "")

    cd - > /dev/null

    # Remove worktree
    git worktree remove "$worktree" --force 2>/dev/null || {
        echo "  ⚠️  Could not remove worktree, deleting manually..."
        rm -rf "$worktree"
    }

    # Optionally delete branch
    if [[ -n "$branch" ]]; then
        git branch -D "$branch" 2>/dev/null || echo "  ⚠️  Branch already deleted or in use"
    fi

    echo "  ✅ Removed"
done

# Remove aggregated directory
rm -rf "$TARGET_DIR/aggregated"

echo ""
echo "=== Cleanup Complete ==="
git worktree list
