# Git Integration

## Overview

Git integration is fundamental to the Two-Agent Framework's success. It provides version control, collaboration, rollback capabilities, and a complete audit trail of all development activities. The framework enforces specific Git workflows to ensure clean state, traceable changes, and seamless collaboration between agents and human developers.

## Git Workflow Philosophy

### 1. Clean State Principle
Every commit must represent a working, mergeable state to the main branch. No half-finished features, no broken tests, no TODOs left in production code.

### 2. Atomic Commits
One feature = one commit. Each commit implements a complete, tested feature with clear documentation of what was changed.

### 3. Traceability
Every commit links directly to a feature ID from the feature-list.json, enabling complete traceability from requirements to implementation.

### 4. Recovery
Git provides the ultimate recovery mechanism—any mistake can be rolled back to a previous working state.

## Branch Strategy

### Main Branch Protection

```json
// .github/branch-protection.json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/tests",
      "ci/lint",
      "ci/type-check"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": {
    "users": [],
    "teams": ["core-developers"]
  }
}
```

### Branch Types

| Branch Type | Purpose | Lifecycle |
|-------------|---------|-----------|
| **main** | Production-ready code | Permanent |
| **develop** | Integration branch | Permanent |
| **feature/ID** | Individual feature development | Temporary |
| **hotfix/ID** | Production fixes | Temporary |
| **release/v** | Release preparation | Temporary |

### Branch Naming Conventions

```
feature/AUTH-001        # User registration feature
feature/UI-045          # Navigation component
bugfix/DB-023           # Database connection issue
hotfix/PROD-001         # Production hotfix
release/v2.1.0          # Release branch
```

## Commit Message Format

### Conventional Commits Standard

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Purpose | Example |
|------|---------|---------|
| **feat** | New feature | `feat(AUTH-001): Add user registration` |
| **fix** | Bug fix | `fix(API-023): Fix authentication timeout` |
| **docs** | Documentation | `docs(README): Update installation guide` |
| **style** | Code style | `style(UI): Fix button alignment` |
| **refactor** | Refactoring | `refactor(DB): Consolidate query methods` |
| **test** | Tests | `test(AUTH-001): Add registration tests` |
| **chore** | Maintenance | `chore(deps): Update dependencies` |

### Feature-Specific Format

```
feat(FEATURE-ID): Brief feature description

Detailed explanation of implementation:
- What was changed
- Why it was changed
- How it was implemented
- Any trade-offs made

Testing performed:
- Unit tests: passing
- Integration tests: passing
- Manual verification: complete

Closes #ISSUE_NUMBER
```

### Complete Example

```
feat(AUTH-001): Implement user registration system

- Added registration form with email validation
- Integrated SendGrid for email verification
- Implemented password strength requirements
- Added rate limiting to prevent abuse

Backend changes:
- Created /api/auth/register endpoint
- Added User model with email verification
- Implemented JWT token generation

Frontend changes:
- Created RegistrationPage component
- Added form validation with React Hook Form
- Integrated with backend API

Testing:
- Unit tests: 100% coverage
- Integration tests: All passing
- Manual verification: Steps 1-11 completed

The feature now allows users to register with email verification
and automatically logs them in after successful registration.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Commit Automation

### Pre-Commit Hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run tests
npm run test:unit
if [ $? -ne 0 ]; then
  echo "❌ Unit tests failed. Commit aborted."
  exit 1
fi

# Run linting
npm run lint
if [ $? -ne 0 ]; then
  echo "❌ Linting errors found. Commit aborted."
  exit 1
fi

# Check for TODOs
TODO_COUNT=$(git diff --cached --name-only | xargs grep -l "TODO\|FIXME" 2>/dev/null | wc -l)
if [ $TODO_COUNT -gt 0 ]; then
  echo "⚠️  Found $TODO_COUNT files with TODO/FIXME:"
  git diff --cached --name-only | xargs grep -n "TODO\|FIXME" 2>/dev/null
  read -p "Continue anyway? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Check feature status
if [ -f ".claude/progress/feature-list.json" ]; then
  # Get staged feature IDs from commit message
  FEATURE_ID=$(git log -1 --pretty=format:'%s' | grep -oE '\([A-Z]{3}-[0-9]{3}\)' | tr -d '()')

  if [ -n "$FEATURE_ID" ]; then
    FEATURE_PASSES=$(jq -r --arg id "$FEATURE_ID" \
      '.categories[].features[] | select(.id == $id) | .passes' \
      .claude/progress/feature-list.json)

    if [ "$FEATURE_PASSES" != "true" ]; then
      echo "⚠️  Feature $FEATURE_ID is not marked as passing in feature-list.json"
      read -p "Continue anyway? (y/N): " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
      fi
    fi
  fi
fi

echo "✅ All checks passed. Committing..."
exit 0
```

### Commit Message Validation

```javascript
// scripts/validate-commit-msg.js
const conventionalCommits = require('conventional-commits-validator');

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'test',
        'chore'
      ]
    ],
    'scope-case': [2, 'always', 'pascal-case'],
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 100],
    'footer-max-line-length': [2, 'always', 100],
    'scope-empty': [2, 'never'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'header-max-length': [2, 'always', 100]
  }
};
```

### Automatic Commit Generation

```bash
#!/bin/bash
# scripts/commit-feature.sh

FEATURE_ID=$1

if [ -z "$FEATURE_ID" ]; then
  echo "Usage: ./commit-feature.sh <FEATURE-ID>"
  exit 1
fi

# Get feature information
FEATURE_INFO=$(jq -r --arg id "$FEATURE_ID" \
  '.categories[].features[] | select(.id == $id)' \
  .claude/progress/feature-list.json)

FEATURE_NAME=$(echo "$FEATURE_INFO" | jq -r '.name')
FEATURE_DESC=$(echo "$FEATURE_INFO" | jq -r '.description')

# Generate commit message
cat > .git/COMMIT_EDITMSG << EOF
feat($FEATURE_ID): $FEATURE_NAME

$FEATURE_DESC

Implementation details extracted from git diff:
$(git diff --cached --stat)

Testing:
- Manual verification: All steps completed
- Unit tests: Passing
- Integration tests: Passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF

# Execute commit
git commit -F .git/COMMIT_EDITMSG

# Update feature status
jq --arg id "$FEATURE_ID" \
  '(.categories[].features[] | select(.id == $id)) |= {
    .,
    "passes": true,
    "completed_at": "'$(date -Iseconds)'"
  }' \
  .claude/progress/feature-list.json > .tmp && \
  mv .tmp .claude/progress/feature-list.json

echo "✅ Feature $FEATURE_ID committed successfully!"
```

## Collaboration Workflow

### Feature Branch Workflow

```bash
# 1. Create feature branch
git checkout -b feature/AUTH-001

# 2. Implement feature
# ... (coding, testing, etc.)

# 3. Commit changes
git add .
./scripts/commit-feature.sh AUTH-001

# 4. Push to remote
git push -u origin feature/AUTH-001

# 5. Create pull request
# (done through GitHub UI)

# 6. After review and merge:
git checkout main
git pull origin main
git branch -d feature/AUTH-001
```

### Pull Request Template

```markdown
<!-- .github/pull_request_template.md -->
## Description
Brief description of changes made in this PR.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Feature ID
<!-- Link to feature-list.json -->
Feature: [AUTH-001](https://github.com/user/repo/blob/main/.claude/progress/feature-list.json#L42)

## Testing Performed
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual steps verified
- [ ] E2E tests pass
- [ ] Performance tests pass

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->

## Additional Notes
<!-- Any additional information about the PR -->
```

### Code Review Process

```yaml
# .github/workflows/pr-check.yml
name: PR Check

on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  pr-validation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Validate PR format
      uses: actions/github-script@v6
      with:
        script: |
          // Check PR description for required sections
          const body = context.payload.pull_request.body;
          const required = ['Description', 'Feature ID', 'Testing Performed'];

          for (const section of required) {
            if (!body.includes(section)) {
              core.setFailed(`PR missing required section: ${section}`);
              return;
            }
          }

          // Extract feature ID from PR
          const featureMatch = body.match(/Feature:\s*\[([A-Z]{3}-[0-9]{3})\]/);
          if (featureMatch) {
            const featureId = featureMatch[1];
            console.log(`Feature ID found: ${featureId}`);

            // Check if feature exists in feature-list.json
            const fs = require('fs');
            const featureList = JSON.parse(fs.readFileSync('.claude/progress/feature-list.json', 'utf8'));

            let featureExists = false;
            for (const category of Object.values(featureList.categories)) {
              if (category.features.some(f => f.id === featureId)) {
                featureExists = true;
                break;
              }
            }

            if (!featureExists) {
              core.setFailed(`Feature ${featureId} not found in feature-list.json`);
            }
          }
```

## History Tracking

### Git Log Analysis

```bash
#!/bin/bash
# scripts/git-stats.sh

echo "=== Git Statistics ==="

# Total commits
TOTAL_COMMITS=$(git rev-list --count HEAD)
echo "Total commits: $TOTAL_COMMITS"

# Commits by type
echo -e "\n=== Commits by Type ==="
git log --pretty=format:'%s' | grep -oE '^[a-z]+' | sort | uniq -c | sort -nr

# Commits by feature
echo -e "\n=== Commits by Feature ==="
git log --pretty=format:'%s' | grep -oE '\([A-Z]{3}-[0-9]{3}\)' | sort | uniq -c | sort -nr

# Contributors
echo -e "\n=== Contributors ==="
git log --pretty=format:'%an' | sort | uniq -c | sort -nr

# Recent activity
echo -e "\n=== Recent Activity (Last 7 Days) ==="
git log --since="7 days ago" --pretty=format:'%h %s' | wc -l | xargs echo "Commits:"
git log --since="7 days ago" --pretty=format:'%s'
```

### Feature History

```bash
#!/bin/bash
# scripts/feature-history.sh

FEATURE_ID=$1

if [ -z "$FEATURE_ID" ]; then
  echo "Usage: ./feature-history.sh <FEATURE-ID>"
  exit 1
fi

echo "=== History for $FEATURE_ID ==="

# Find all commits for this feature
COMMITS=$(git log --grep="($FEATURE_ID)" --oneline)

echo -e "\nCommits:"
echo "$COMMITS"

# Show file changes
echo -e "\nFile changes:"
git log --grep="($FEATURE_ID)" --name-only --pretty=format: | sort | uniq

# Show feature status
echo -e "\nCurrent status:"
jq -r --arg id "$FEATURE_ID" \
  '.categories[].features[] | select(.id == $id)' \
  .claude/progress/feature-list.json

# Show time tracking
echo -e "\nTimeline:"
git log --grep="($FEATURE_ID)" --pretty=format:'%h %ad %s' --date=short
```

## Recovery and Rollback

### Quick Recovery Commands

```bash
#!/bin/bash
# scripts/quick-recovery.sh

echo "=== Quick Recovery Options ==="

# 1. Undo last commit (keep changes)
echo "1. Undo last commit (keep changes):"
echo "   git reset --soft HEAD~1"

# 2. Undo last commit (discard changes)
echo -e "\n2. Undo last commit (discard changes):"
echo "   git reset --hard HEAD~1"

# 3. Recover specific file
echo -e "\n3. Recover file from last commit:"
echo "   git checkout HEAD -- path/to/file"

# 4. Recover to specific commit
echo -e "\n4. Recover to specific commit:"
echo "   git reset --hard <commit-hash>"

# 5. Stash current changes
echo -e "\n5. Stash current changes:"
echo "   git stash"

# 6. Recover from stash
echo -e "\n6. Recover from stash:"
echo "   git stash pop"

# Show recent commits for reference
echo -e "\n=== Recent Commits ==="
git log --oneline -10
```

### Disaster Recovery

```bash
#!/bin/bash
# scripts/disaster-recovery.sh

echo "=== Disaster Recovery ==="

# Create backup branch
BACKUP_BRANCH="recovery-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup branch: $BACKUP_BRANCH"
git checkout -b $BACKUP_BRANCH

# Save current state
git add .
git commit -m "RECOVERY: Save state before recovery"
git checkout main

# Options
echo -e "\nRecovery Options:"
echo "1. Reset to last known good state (HEAD~5)"
echo "2. Reset to specific commit"
echo "3. Reset to tag"
echo "4. Interactive rebase"
echo "5. Abort and return to backup"

read -p "Choose option (1-5): " -n 1 -r
echo

case $REPLY in
  1)
    git reset --hard HEAD~5
    echo "Reset to HEAD~5"
    ;;
  2)
    read -p "Enter commit hash: " COMMIT
    git reset --hard $COMMIT
    echo "Reset to $COMMIT"
    ;;
  3)
    git tag -l | sort -V
    read -p "Enter tag name: " TAG
    git reset --hard $TAG
    echo "Reset to tag $TAG"
    ;;
  4)
    git log --oneline -20
    read -p "Enter base commit (HEAD~n): " BASE
    git rebase -i $BASE
    ;;
  5)
    git checkout $BACKUP_BRANCH
    echo "Returned to backup branch: $BACKUP_BRANCH"
    ;;
esac

echo -e "\nRecovery complete. Verify state with:"
echo "  git log --oneline -5"
echo "  git status"
```

## Integration with Development Tools

### IDE Integration (VS Code)

```json
// .vscode/settings.json
{
  "git.enableSmartCommit": true,
  "git.smartCommitChanges": "all",
  "git.autofetch": true,
  "git.confirmSync": false,
  "git.postCommitCommand": "none",
  "git.showInlineOpenFileAction": false,
  "git.suggestSmartCommit": false,
  "git.supportCancellation": false
}
```

### Git Aliases

```bash
# .gitconfig
[alias]
  # Feature workflow
  feature = "!f() { git checkout -b feature/$1; }; f"
  commit-feature = "!sh ./scripts/commit-feature.sh"
  feature-status = "!sh ./scripts/feature-history.sh"

  # Quick operations
  save = "!git add -A && git commit -m 'WIP: Save progress'"
  wipe = "!git add -A && git commit -m 'WIPE: Reset to clean state' && git reset --hard HEAD~1"
  undo = "reset --soft HEAD~1"

  # History
  graph = "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
  find = "!f() { git log --all --grep=\"$1\" --pretty=format:'%h %s' }; f"

  # Statistics
  stats = "!sh ./scripts/git-stats.sh"
  churn = "!f() { git log -M -C --name-only --format='format:' $@ | sort | uniq -c | sort -nr }; f"
```

### GitHub CLI Integration

```bash
#!/bin/bash
# scripts/gh-integration.sh

# Create PR from feature branch
create_pr() {
  FEATURE_ID=$(git branch --show-current | grep -oE '[A-Z]{3}-[0-9]{3}')

  if [ -z "$FEATURE_ID" ]; then
    echo "No feature ID found in branch name"
    exit 1
  fi

  # Get feature info
  FEATURE_INFO=$(jq -r --arg id "$FEATURE_ID" \
    '.categories[].features[] | select(.id == $id) | {
      name: .name,
      description: .description,
      steps: .steps
    }' \
    .claude/progress/feature-list.json)

  # Create PR
  gh pr create \
    --title "feat($FEATURE_ID): $(echo "$FEATURE_INFO" | jq -r '.name')" \
    --body "$(cat << EOF
## Description
$(echo "$FEATURE_INFO" | jq -r '.description')

## Feature ID
$FEATURE_ID

## Testing Performed
$(echo "$FEATURE_INFO" | jq -r '.steps[]' | sed 's/^/- [ ] /')

## Checklist
- [x] Code follows project guidelines
- [x] Self-review completed
- [x] Tests added and passing
- [x] Documentation updated

EOF
)"
}

# List features in progress
list_features() {
  jq -r '.categories[].features[] | select(.passes == false) | "\(.id) - \(.name)"' \
    .claude/progress/feature-list.json
}

# Main menu
case "$1" in
  pr)
    create_pr
    ;;
  list)
    list_features
    ;;
  *)
    echo "Usage: $0 {pr|list}"
    ;;
esac
```

## Best Practices

### 1. Commit Hygiene
- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Include feature IDs in all related commits
- Never commit broken code

### 2. Branch Management
- Delete feature branches after merging
- Keep main branch clean and deployable
- Use descriptive branch names
- Protect critical branches

### 3. Collaboration
- Review all code before merging
- Use pull requests for all changes
- Document decisions in commit messages
- Resolve conflicts carefully

### 4. Security
- Never commit secrets or API keys
- Use .gitignore effectively
- Review access permissions regularly
- Sign commits when possible

### 5. Performance
- Use shallow clones for CI/CD
- Keep repository size manageable
- Use Git LFS for large files
- Archive old branches

This comprehensive Git integration ensures that all development activities are tracked, versioned, and recoverable, providing a solid foundation for the Two-Agent Framework's incremental development approach.