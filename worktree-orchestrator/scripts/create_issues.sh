#!/usr/bin/env bash
# create_issues.sh - Create GitHub issues from worktree findings
# Usage: create_issues.sh [target-dir]

set -eo pipefail

TARGET_DIR="${1:-$(git rev-parse --show-toplevel)/.claude/worktrees}"
REPO=$(git remote get-url origin | sed 's/.*github.com[/:]//' | sed 's/.git$//')

echo "=== Creating GitHub Issues ==="
echo "Repository: $REPO"
echo "Source: $TARGET_DIR"
echo ""

# Check gh is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) not installed"
    echo "Install with: brew install gh"
    exit 1
fi

# Check auth
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

# Create labels if they don't exist
echo "Creating labels..."
gh label create "security" --repo "$REPO" --color "d73a4a" --description "Security issues" 2>/dev/null || true
gh label create "critical" --repo "$REPO" --color "b60205" --description "Critical priority" 2>/dev/null || true
gh label create "P0" --repo "$REPO" --color "e11d21" --description "Immediate action" 2>/dev/null || true
gh label create "P1" --repo "$REPO" --color "ff7f00" --description "High priority" 2>/dev/null || true
gh label create "performance" --repo "$REPO" --color "fbca04" --description "Performance issues" 2>/dev/null || true
gh label create "testing" --repo "$REPO" --color "1d76db" --description "Test coverage" 2>/dev/null || true
gh label create "architecture" --repo "$REPO" --color "5319e7" --description "Architecture concerns" 2>/dev/null || true

CREATED_ISSUES=()

# Function to create issue from finding
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"

    url=$(gh issue create --repo "$REPO" --title "$title" --label "$labels" --body "$body")
    echo "  Created: $url"
    CREATED_ISSUES+=("$url")
}

# Parse security findings
SECURITY_FILE="$TARGET_DIR/review-security/findings.md"
if [[ -f "$SECURITY_FILE" ]]; then
    echo ""
    echo "Processing security findings..."

    # Extract critical items
    while IFS= read -r line; do
        if [[ "$line" =~ \[([A-Z_]+\.PY):([0-9-]+)\]\ \*\*(.+)\*\*:\ (.+) ]]; then
            file="${BASH_REMATCH[1]}"
            lines="${BASH_REMATCH[2]}"
            severity="${BASH_REMATCH[3]}"
            desc="${BASH_REMATCH[4]}"

            title="[Security/Critical] ${severity} - ${file}:${lines}"
            body="## Severity: CRITICAL 🔴

## Summary
${desc}

## Location
- **File:** \`src/jarvis/${file}\`
- **Lines:** ${lines}

## @claude
Please analyze and fix this security issue in \`src/jarvis/${file}\`."

            create_issue "$title" "$body" "security,critical,P0"
        fi
    done < <(grep -E "^\- \[" "$SECURITY_FILE" | head -10)
fi

# Parse performance findings
PERF_FILE="$TARGET_DIR/review-performance/findings.md"
if [[ -f "$PERF_FILE" ]]; then
    echo ""
    echo "Processing performance findings..."

    while IFS= read -r line; do
        if [[ "$line" =~ \[src/jarvis/([a-z_/]+\.py):([0-9-]+)\]\ (.+) ]]; then
            file="${BASH_REMATCH[1]}"
            lines="${BASH_REMATCH[2]}"
            desc="${BASH_REMATCH[3]:0:100}"

            title="[Performance] ${file}:${lines}"
            body="## Severity: HIGH 🟠

## Summary
${desc}...

## Location
- **File:** \`src/jarvis/${file}\`
- **Lines:** ${lines}

## @claude
Please analyze and fix this performance issue in \`src/jarvis/${file}\`."

            create_issue "$title" "$body" "performance,P0"
            break  # Just first one for now
        fi
    done < <(grep -E "^\- \[src" "$PERF_FILE" | head -5)
fi

# Parse test findings
TEST_FILE="$TARGET_DIR/testing/test_report.md"
if [[ -f "$TEST_FILE" ]]; then
    echo ""
    echo "Processing testing findings..."

    # Create one summary issue for testing
    title="[Testing] Critical modules missing tests"
    body="## Severity: HIGH 🟡

## Summary
Critical modules identified with zero or minimal tests.

## Missing Tests
See \`$TEST_FILE\` for detailed breakdown.

## @claude
Please create comprehensive tests for the critical modules identified in the test report."

    create_issue "$title" "$body" "testing,P0"
fi

echo ""
echo "=== Issues Created ==="
echo "Total: ${#CREATED_ISSUES[@]}"
for url in "${CREATED_ISSUES[@]}"; do
    echo "  $url"
done

echo ""
echo "Next: Comment '@claude please fix this' on any issue to have Claude analyze and fix it."
