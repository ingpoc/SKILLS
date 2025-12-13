# Session Workflow

## Overview

The session workflow defines the standardized procedures for managing development sessions within the Two-Agent Framework. It ensures consistency, enables recovery from interruptions, and maintains clean state between sessions. This workflow is designed for 2-4 hour focused development sessions that incrementally build features while preserving context.

## Session Types

### 1. Initializer Sessions
- **Purpose**: Project planning and feature breakdown
- **Duration**: 4-8 hours
- **Agent**: initializer-agent
- **Output**: Complete feature-list.json with 200+ features

### 2. Coding Sessions
- **Purpose**: Implement single features incrementally
- **Duration**: 2-4 hours
- **Agent**: coding-agent
- **Output**: Completed feature with tests and documentation

### 3. Recovery Sessions
- **Purpose**: Resume from abnormal termination
- **Duration**: 30-60 minutes
- **Agent**: Depends on last activity
- **Output**: Clean state ready for normal session

### 4. Review Sessions
- **Purpose**: Assess progress and plan next steps
- **Duration**: 1-2 hours
- **Agent**: Any (Opus orchestrates)
- **Output**: Updated roadmap and priority adjustments

## Standard Session Workflow

### Phase 1: Session Initialization

#### Step 1: Environment Check
```bash
# Always start with location verification
pwd

# Check git status
git status
git log --oneline -5

# Verify working directory is clean
if [[ -n $(git status --porcelain) ]]; then
  echo "⚠️  Working directory not clean - commit or stash changes"
  exit 1
fi
```

#### Step 2: Context Recovery
```bash
# Check for abnormal exit
if [ -f ".claude/progress/session-state.json" ]; then
  cat .claude/progress/session-state.json | jq '.status'

  # If status is "active" with old heartbeat, recovery needed
  LAST_HB=$(cat .claude/progress/session-state.json | jq -r '.heartbeat.last_heartbeat')
  if [ "$STATUS" = "active" ] && [ "$LAST_HB" != "$(date -Iseconds)" ]; then
    echo "⚠️  Previous session ended abnormally - initiating recovery"
    # Run recovery procedures
  fi
fi
```

#### Step 3: Progress Assessment
```bash
# Read current state
echo "=== Current Progress ==="
cat .claude/progress/claude-progress.txt | tail -20

echo -e "\n=== Feature Statistics ==="
cat .claude/progress/feature-list.json | jq '{total: .total_features, completed: .completed, pending: .pending}'

echo -e "\n=== Last Session ==="
cat .claude/progress/session-state.json | jq '{session: .session_number, last_feature: .last_feature_id, status: .status}'
```

### Phase 2: Feature Selection

#### For Coding Agent Sessions
```bash
# Find next unblocked feature
SELECTED_FEATURE=$(cat .claude/progress/feature-list.json | jq -r '
  .categories as $cats |
  [
    $cats[] | .features[] | select(.passes == false)
  ] | sort_by(.dependencies | length) | .[0]
')

echo "Selected feature: $(echo $SELECTED_FEATURE | jq -r '.id') - $(echo $SELECTED_FEATURE | jq -r '.name')"

# Check dependencies
DEPS=$(echo $SELECTED_FEATURE | jq -r '.dependencies[]')
if [ -n "$DEPS" ]; then
  echo "Dependencies: $DEPS"
  # Verify all dependencies are marked as passes: true
fi
```

#### For Initializer Agent Sessions
```bash
# Determine if this is a new project or expansion
if [ ! -f ".claude/progress/feature-list.json" ]; then
  echo "New project - creating initial feature breakdown"
else
  echo "Project expansion - analyzing gaps and additions needed"
  # Analyze existing features for missing components
fi
```

### Phase 3: Session Execution

#### Coding Agent Workflow

1. **Feature Preparation**
   ```bash
   # Create feature branch (optional but recommended)
   git checkout -b "feature/$(echo $SELECTED_FEATURE | jq -r '.id | tolower')"

   # Update session state
   cat .claude/progress/session-state.json | \
     jq ".current_feature = $(echo $SELECTED_FEATURE | jq '{id, name, started_at: now}')" > \
     .claude/progress/session-state.json.tmp && \
     mv .claude/progress/session-state.json.tmp .claude/progress/session-state.json
   ```

2. **Development Process**
   - Read related files to understand patterns
   - Implement feature following established conventions
   - Write/update tests for the feature
   - Document any new APIs or components

3. **Progress Updates**
   ```bash
   # Update heartbeat every 5 minutes during long tasks
   while [ $LONG_RUNNING_TASK = true ]; do
     cat .claude/progress/session-state.json | \
       jq ".heartbeat.last_heartbeat = \"$(date -Iseconds)\"" > \
       .claude/progress/session-state.json.tmp && \
       mv .claude/progress/session-state.json.tmp .claude/progress/session-state.json
     sleep 300
   done
   ```

#### Initializer Agent Workflow

1. **Project Analysis**
   - Read any existing documentation
   - Understand business requirements
   - Identify all major system components

2. **Feature Breakdown**
   - Create high-level epics (10-20 categories)
   - Detail specific features (100-200 items)
   - Add granular sub-tasks (200-500 total tasks)
   - Ensure each task is 2-4 hours of work

3. **Environment Setup**
   ```bash
   # Create project structure
   mkdir -p {src,tests,docs,scripts,.claude/progress}

   # Initialize progress tracking
   echo "Project initialized on $(date)" > .claude/progress/claude-progress.txt

   # Create initial session state
   cat > .claude/progress/session-state.json << EOF
   {
     "session_number": 0,
     "started_at": "$(date -Iseconds)",
     "agent_type": "initializer",
     "status": "completed",
     "metadata": {
       "total_features_created": 247,
       "categories_created": 12
     }
   }
   EOF
   ```

### Phase 4: Testing and Verification

#### Manual Testing Protocol

1. **Environment Preparation**
   ```bash
   # Ensure development server is running
   npm run dev
   # or
   python -m src.server

   # Wait for server to be ready
   until curl -s http://localhost:3000 > /dev/null; do
     echo "Waiting for server..."
     sleep 2
   done
   ```

2. **Step-by-Step Verification**
   ```bash
   # Get the steps for current feature
   STEPS=$(cat .claude/progress/feature-list.json | \
     jq -r --arg id "$FEATURE_ID" \
     '.categories[].features[] | select(.id == $id) | .steps[]')

   # Execute each step manually
   echo "Testing feature: $FEATURE_ID"
   echo "=============================="

   for step in $STEPS; do
     echo -e "\nStep: $step"
     read -p "Press Enter after completing this step..."

     # Verify step success (automated checks where possible)
     # This is where you'd add specific verification code
   done
   ```

3. **Automated Testing**
   ```bash
   # Run unit tests
   npm test
   # or
   pytest

   # Run integration tests
   npm run test:integration
   # or
   pytest tests/integration/

   # Run E2E tests (if available)
   npm run test:e2e
   ```

#### Browser Automation with Puppeteer MCP

```javascript
// Example test execution using Puppeteer MCP
await browser.navigate('http://localhost:3000');
await browser.click('a[href="/register"]');
await browser.fillForm({
  email: 'test@example.com',
  password: 'SecurePass123!',
  confirmPassword: 'SecurePass123!'
});
await browser.click('button[type="submit"]');
await browser.waitForText('Welcome! Your account has been created.');
```

### Phase 5: Session Completion

#### Update Feature Status
```bash
# Mark feature as complete
cat .claude/progress/feature-list.json | \
  jq --arg id "$FEATURE_ID" \
  '(.categories[].features[] | select(.id == $id)) |= {
    .,
    "passes": true,
    "completed_at": "$(date -Iseconds)",
    "notes": "Successfully implemented and tested"
  }' > .claude/progress/feature-list.json.tmp && \
  mv .claude/progress/feature-list.json.tmp .claude/progress/feature-list.json
```

#### Update Progress Log
```bash
# Update claude-progress.txt
cat >> .claude/progress/claude-progress.txt << EOF

## Session $SESSION_NUMBER - $(date +%Y-%m-%d) ($DURATION minutes)
### Completed:
- [x] $FEATURE_ID: $FEATURE_NAME ($ESTIMATED_HOURS h)
  $IMPLEMENTATION_NOTES

### Statistics:
- Total: $TOTAL_FEATURES
- Completed: $COMPLETED_FEATURES ($(echo "scale=1; $COMPLETED_FEATURES * 100 / $TOTAL_FEATURES" | bc)%)
- Session velocity: $(echo "scale=1; $FEATURES_THIS_SESSION / ($DURATION / 60)" | bc) features/hour

EOF
```

#### Clean Git State
```bash
# Add all changes
git add .

# Commit with conventional format
git commit -m "feat($FEATURE_ID): Implement $FEATURE_NAME

$COMMIT_BODY

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Optionally merge to main
git checkout main
git merge feature/$FEATURE_ID
git branch -d feature/$FEATURE_ID
```

#### Update Session State
```bash
cat .claude/progress/session-state.json | \
  jq '{
    .,
    "status": "completed",
    "ended_at": "$(date -Iseconds)",
    "session_summary": {
      "features_completed": 1,
      "features_blocked": 0,
      "total_time_minutes": $SESSION_MINUTES,
      "notes": "Successfully completed $FEATURE_ID"
    }
  }' > .claude/progress/session-state.json.tmp && \
  mv .claude/progress/session-state.json.tmp .claude/progress/session-state.json
```

## Recovery Procedures

### Detecting Abnormal Termination

The session-start hook automatically detects abnormal exits:

```bash
#!/bin/sh
# .claude/hooks/session-progress-check.sh

SESSION_STATE=".claude/progress/session-state.json"

if [ -f "$SESSION_STATE" ]; then
  STATUS=$(cat "$SESSION_STATE" | jq -r '.status')
  LAST_HB=$(cat "$SESSION_STATE" | jq -r '.heartbeat.last_heartbeat')

  if [ "$STATUS" = "active" ]; then
    # Calculate time since last heartbeat
    AGE=$(($(date +%s) - $(date -d "$LAST_HB" +%s)))

    if [ $AGE -gt 1800 ]; then  # 30 minutes
      echo "⚠️  Previous session ended abnormally (last heartbeat: $LAST_HB)"
      echo "Running recovery procedures..."

      # Check git status
      if [[ -n $(git status --porcelain) ]]; then
        echo "Found uncommitted changes - creating recovery branch"
        git checkout -b "recovery-$(date +%Y%m%d-%H%M%S)"
        git add .
        git commit -m "Recovery: Save incomplete changes from crashed session"
      fi

      # Mark session as interrupted
      jq '.status = "interrupted"' "$SESSION_STATE" > "$SESSION_STATE.tmp" && \
        mv "$SESSION_STATE.tmp" "$SESSION_STATE"
    fi
  fi
fi
```

### Recovery Workflow

1. **Assess Damage**
   ```bash
   # What was being worked on?
   CURRENT_FEATURE=$(cat .claude/progress/session-state.json | jq -r '.current_feature.id')
   echo "Was working on: $CURRENT_FEATURE"

   # Check git state
   git log --oneline -5
   git status

   # Check for broken code
   if [ -f "package.json" ]; then
     npm run build 2>&1 | grep -i error || echo "Build OK"
   fi
   ```

2. **Decision Point**
   - **Option A**: Complete partial work if mostly done
   - **Option B**: Rollback to last good state
   - **Option C**: Create new feature from remaining work

3. **Execute Recovery**
   ```bash
   case $RECOVERY_OPTION in
     A)
       echo "Completing partial work..."
       # Continue implementation
       ;;
     B)
       echo "Rolling back to last commit..."
       git reset --hard HEAD
       # Mark feature as not started
       ;;
     C)
       echo "Creating new feature for remaining work..."
       # Split feature into smaller parts
       ;;
   esac
   ```

## Session Automation Scripts

### Session Start Script
```bash
#!/bin/bash
# .claude/scripts/start-session.sh

SESSION_TYPE=${1:-"coding"}
SESSION_NUMBER=$(($(cat .claude/progress/session-state.json | jq -r '.session_number') + 1))

echo "Starting Session #$SESSION_NUMBER ($SESSION_TYPE)"

# Initialize session state
cat > .claude/progress/session-state.json << EOF
{
  "session_number": $SESSION_NUMBER,
  "started_at": "$(date -Iseconds)",
  "agent_type": "$SESSION_TYPE",
  "status": "active",
  "heartbeat": {
    "last_heartbeat": "$(date -Iseconds)",
    "interval_seconds": 300,
    "missed_heartbeats": 0
  }
}
EOF

# Start heartbeat monitor
nohup bash .claude/scripts/heartbeat-monitor.sh &>/dev/null &

echo "Session initialized successfully"
```

### Heartbeat Monitor
```bash
#!/bin/bash
# .claude/scripts/heartbeat-monitor.sh

while true; do
  sleep 300  # 5 minutes

  if [ -f ".claude/progress/session-state.json" ]; then
    # Update heartbeat
    jq '.heartbeat.last_heartbeat = "'$(date -Iseconds)'"' \
      .claude/progress/session-state.json > .tmp && \
      mv .tmp .claude/progress/session-state.json

    # Check if we should still be running
    STATUS=$(cat .claude/progress/session-state.json | jq -r '.status')
    if [ "$STATUS" != "active" ]; then
      echo "Session no longer active, stopping heartbeat monitor"
      exit 0
    fi
  else
    echo "No session state file found, exiting"
    exit 1
  fi
done
```

### Session End Script
```bash
#!/bin/bash
# .claude/scripts/end-session.sh

# Stop heartbeat monitor
pkill -f heartbeat-monitor.sh

# Update session state
END_TIME=$(date -Iseconds)
DURATION=$(($(date +%s) - $(date -d "$(cat .claude/progress/session-state.json | jq -r '.started_at')" +%s)))

cat .claude/progress/session-state.json | \
  jq "{
    .,
    \"status\": \"completed\",
    \"ended_at\": \"$END_TIME\",
    \"duration_minutes\": $((DURATION / 60))
  }" > .tmp && mv .tmp .claude/progress/session-state.json

echo "Session closed successfully"
```

## Best Practices

### 1. Session Planning
- **Clear Objective**: Know exactly which feature you'll implement
- **Timeboxing**: Keep sessions to 2-4 hours maximum
- **Dependencies Ready**: Verify prerequisites before starting
- **Environment Prepared**: Have all tools and services running

### 2. During Session
- **Single Focus**: Work on only one feature
- **Regular Updates**: Update progress every 30 minutes
- **Test Continuously**: Don't wait until the end to test
- **Document Decisions**: Note important choices and tradeoffs

### 3. Session Completion
- **Clean State**: Always leave code deployable
- **Complete Tests**: Ensure all new features are tested
- **Update Everything**: Feature list, progress log, session state
- **Proper Commit**: Use conventional commit format

### 4. Between Sessions
- **Review Progress**: Read claude-progress.txt before starting
- **Check Blockers**: Verify no features are blocked
- **Plan Next**: Know what you'll work on next
- **Sync Team**: Communicate progress to team members

## Session Templates

### Coding Session Template
```
## Session N - YYYY-MM-DD

### Objective
- Feature: [ID] [Feature Name]
- Estimated: [X hours]
- Dependencies: [List if any]

### Progress
- [ ] Read related files (15 min)
- [ ] Implement core functionality (X hours)
- [ ] Add/update tests (30 min)
- [ ] Manual verification (30 min)
- [ ] Documentation updates (15 min)

### Blockers/Issues
- [ ] None

### Notes
-
```

### Review Session Template
```
## Review Session - YYYY-MM-DD

### Completed Since Last Review
1. [Feature ID] - [Brief description]
2. [Feature ID] - [Brief description]
3. ...

### Current Status
- Total Features: [N]
- Completed: [X] ([Y]%)
- In Progress: [A]
- Blocked: [B]

### Next Priorities
1. [Feature ID] - [Reason for priority]
2. [Feature ID] - [Reason for priority]
3. ...

### Risks and Mitigations
- Risk: [Description]
- Mitigation: [Plan]

### Stakeholder Updates
- [Any important communications]
```

## Integration with IDE

### VS Code Tasks
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Coding Session",
      "type": "shell",
      "command": ".claude/scripts/start-session.sh coding",
      "group": "build"
    },
    {
      "label": "End Session",
      "type": "shell",
      "command": ".claude/scripts/end-session.sh",
      "group": "build"
    },
    {
      "label": "Update Progress",
      "type": "shell",
      "command": ".claude/scripts/update-progress.sh",
      "group": "build"
    }
  ]
}
```

### IDE Extensions
- **GitLens**: Visualize feature progress through git history
- **TODO Highlight**: Spot incomplete features
- **Session Manager**: Track active coding sessions
- **Progress Bar**: Customizable project progress indicator

## Monitoring and Analytics

### Session Metrics
Track these metrics for continuous improvement:

```javascript
const sessionMetrics = {
  averageSessionLength: 185, // minutes
  featuresPerSession: 2.3,
  sessionSuccessRate: 0.95, // % of sessions completing features
  recoveryFrequency: 0.08, // % of sessions needing recovery
  averageRecoveryTime: 45, // minutes

  // Trends
  velocityTrend: "increasing",
  bugRateTrend: "decreasing",
  featureComplexityTrend: "stable"
};
```

### Automated Alerts
```bash
# Set up alerts for:
if [ $SESSION_LENGTH -gt 240 ]; then
  echo "⚠️  Long session detected - consider taking a break"
fi

if [ $FEATURES_COMPLETED -eq 0 ]; then
  echo "⚠️  No features completed - check for blockers"
fi

if [ git merge-conflicts ]; then
  echo "⚠️  Merge conflicts detected - resolve before continuing"
fi
```

## Troubleshooting Guide

### Common Session Issues

1. **Can't Find Current Feature**
   - Check session-state.json for last_feature_id
   - Look at git log for recent commits
   - Read claude-progress.txt for latest updates

2. **Tests Keep Failing**
   - Verify development server is running
   - Check test database is populated
   - Review recent code changes for side effects

3. **Git State is Dirty**
   - Commit or stash changes before selecting new feature
   - Use `git stash` if you want to save work temporarily
   - Consider if this should be part of current feature

4. **Dependencies Not Met**
   - Find blocking features and implement them first
   - Update feature dependencies if incorrectly linked
   - Document the blocker in feature notes

### Emergency Procedures

```bash
# If everything is broken:
git checkout main
git reset --hard $(git log --oneline -10 | head -1 | awk '{print $1}')
# Revert to last known good state

# If progress files are corrupted:
cp .claude/progress/backups/*.json .claude/progress/
# Restore from recent backup

# If you don't know what to do next:
cat .claude/progress/feature-list.json | jq '.categories[].features[] | select(.passes == false) | .id, .name'
# List all pending features
```

This comprehensive session workflow ensures that development progresses smoothly, interruptions are recoverable, and project context is preserved across sessions and team members.