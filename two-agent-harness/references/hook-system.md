# Hook System

## Overview

The Hook System is a critical enforcement mechanism in the Two-Agent Framework that ensures agents follow proper workflows, maintain progress tracking, and leave clean state between sessions. Hooks are automated scripts that trigger at specific events during Claude Code execution, providing defense-in-depth protection against common pitfalls and ensuring framework compliance.

## Hook Architecture

### Hook Event Types

The Two-Agent Framework uses these hook events:

| Event | Timing | Purpose | Typical Use |
|-------|--------|---------|-------------|
| **PreToolUse** | Before any tool execution | Validate and guard tool usage | Block Opus from direct code editing |
| **PostToolUse** | After any tool execution | Remind about progress updates | Prompt for feature status updates |
| **SessionStart** | When Claude Code starts | Detect abnormal exits | Check for incomplete sessions |
| **SubagentStop** | When an agent finishes | Verify agent compliance | Ensure progress was updated |
| **SessionEnd** | When Claude Code exits | Clean session termination | Mark session as completed |
| **UserPromptSubmit** | When user sends message | Context injection | Add progress context to prompts |

### Hook Implementation Types

1. **Command Hooks**: Execute shell scripts
2. **Filter Hooks**: Modify inputs/outputs
3. **Validation Hooks**: Check conditions before proceeding
4. **Notification Hooks**: Send alerts or messages

## Core Hook Implementations

### 1. Pre-Tool Guard (pre-tool-guard.sh)

**Purpose**: Prevent Opus from directly editing source code, enforcing the two-agent separation.

```bash
#!/bin/bash
# .claude/hooks/pre-tool-guard.sh

# Extract tool name and arguments from stdin
read -r INPUT

# Parse tool name (simplified parsing)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool' 2>/dev/null || echo "unknown")

# Skip checks for allowed tools
ALLOWED_TOOLS=("Read" "Bash" "Grep" "Glob" "WebFetch" "WebSearch" "TodoWrite")

for allowed in "${ALLOWED_TOOLS[@]}"; do
    if [[ "$TOOL_NAME" == "$allowed" ]]; then
        echo "Tool $TOOL_NAME is allowed" >&2
        exit 0
    fi
done

# Check if trying to edit source files directly
if [[ "$TOOL_NAME" == "Edit" ]] || [[ "$TOOL_NAME" == "Write" ]]; then
    # Extract file path from arguments
    FILE_PATH=$(echo "$INPUT" | jq -r '.file_path // .input.file_path' 2>/dev/null)

    # Block editing src/ directory unless coding-agent is active
    AGENT_TYPE=$(cat .claude/progress/session-state.json 2>/dev/null | jq -r '.agent_type // "unknown"')

    if [[ "$FILE_PATH" == src/* ]] && [[ "$AGENT_TYPE" != "coding" ]]; then
        echo "❌ ERROR: Cannot edit src/ files directly. Use the coding-agent for implementation." >&2
        echo "   This ensures proper progress tracking and clean state maintenance." >&2
        exit 1
    fi
fi

# Update heartbeat if session is active
if [ -f ".claude/progress/session-state.json" ]; then
    cat .claude/progress/session-state.json | \
        jq ".heartbeat.last_heartbeat = \"$(date -Iseconds)\"" > \
        .claude/progress/session-state.json.tmp && \
        mv .claude/progress/session-state.json.tmp .claude/progress/session-state.json
fi

exit 0
```

**Configuration**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/pre-tool-guard.sh",
            "statusMessage": "Validating tool usage..."
          }
        ]
      }
    ]
  }
}
```

### 2. Post-Tool Reminder (post-tool-guard.sh)

**Purpose**: Remind developers to update progress after making changes.

```bash
#!/bin/bash
# .claude/hooks/post-tool-guard.sh

# Extract tool information
read -r INPUT
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool' 2>/dev/null || echo "unknown")

# Check if this was a code-changing operation
if [[ "$TOOL_NAME" == "Edit" ]] || [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "Bash" ]]; then
    # Only remind if coding-agent is active
    if [ -f ".claude/progress/session-state.json" ]; then
        AGENT_TYPE=$(cat .claude/progress/session-state.json | jq -r '.agent_type // "unknown"')

        if [[ "$AGENT_TYPE" == "coding" ]]; then
            echo "" >&2
            echo "💡 Reminder: Don't forget to update progress tracking!" >&2
            echo "   - Mark completed features as 'passes': true in feature-list.json" >&2
            echo "   - Update claude-progress.txt with session summary" >&2
            echo "   - Commit changes with descriptive message" >&2
            echo "" >&2

            # Show current feature if available
            CURRENT_FEATURE=$(cat .claude/progress/session-state.json | jq -r '.current_feature.id // "None"')
            if [[ "$CURRENT_FEATURE" != "None" ]]; then
                echo "   Current feature: $CURRENT_FEATURE" >&2
            fi
        fi
    fi
fi

exit 0
```

### 3. Session Progress Check (session-progress-check.sh)

**Purpose**: Detect abnormal session termination and prompt for recovery.

```bash
#!/bin/bash
# .claude/hooks/session-progress-check.sh

SESSION_STATE=".claude/progress/session-state.json"

# Check if session state exists
if [ ! -f "$SESSION_STATE" ]; then
    echo "No previous session found. Starting fresh." >&2
    exit 0
fi

# Read session status
STATUS=$(cat "$SESSION_STATE" | jq -r '.status // "unknown"')
LAST_HB=$(cat "$SESSION_STATE" | jq -r '.heartbeat.last_heartbeat // "never"')
AGENT_TYPE=$(cat "$SESSION_STATE" | jq -r '.agent_type // "unknown"')
SESSION_NUM=$(cat "$SESSION_STATE" | jq -r '.session_number // "?"')

if [[ "$STATUS" == "active" ]]; then
    # Calculate time since last heartbeat
    if [[ "$LAST_HB" != "never" ]]; then
        LAST_EPOCH=$(date -d "$LAST_HB" +%s 2>/dev/null || echo 0)
        NOW_EPOCH=$(date +%s)
        AGE=$((NOW_EPOCH - LAST_EPOCH))

        # If more than 30 minutes, likely abnormal termination
        if [ $AGE -gt 1800 ]; then
            echo "⚠️  Previous session ended abnormally!" >&2
            echo "   Session #$SESSION_NUM ($AGENT_TYPE agent)" >&2
            echo "   Last heartbeat: $(date -d "$LAST_HB" '+%Y-%m-%d %H:%M:%S')" >&2
            echo "   Time since: $((AGE / 60)) minutes" >&2
            echo "" >&2
            echo "Recommended actions:" >&2
            echo "1. Check git status for uncommitted changes" >&2
            echo "2. Review what was being worked on" >&2
            echo "3. Complete partial work or rollback" >&2
            echo "4. Mark session as 'interrupted' in session-state.json" >&2
            echo "" >&2

            # Check git status
            if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
                echo "⚠️  You have uncommitted changes!" >&2
                git status --short >&2
            fi

            # Mark session as interrupted
            jq '.status = "interrupted"' "$SESSION_STATE" > "$SESSION_STATE.tmp" && \
                mv "$SESSION_STATE.tmp" "$SESSION_STATE"
        else
            echo "Resuming active session #$SESSION_NUM ($AGENT_TYPE agent)" >&2
        fi
    else
        echo "⚠️  Session active but no heartbeat recorded" >&2
    fi
else
    echo "Previous session #$SESSION_NUM completed successfully" >&2
fi

# Show progress summary
if [ -f ".claude/progress/feature-list.json" ]; then
    TOTAL=$(cat .claude/progress/feature-list.json | jq -r '.total_features // 0')
    COMPLETED=$(cat .claude/progress/feature-list.json | jq -r '.completed // 0')
    PENDING=$((TOTAL - COMPLETED))

    echo "" >&2
    echo "📊 Progress Summary:" >&2
    echo "   Total features: $TOTAL" >&2
    echo "   Completed: $COMPLETED ($(( COMPLETED * 100 / TOTAL ))%)" >&2
    echo "   Pending: $PENDING" >&2
fi

exit 0
```

### 4. Coding Agent Verification (verify-coding-agent.sh)

**Purpose**: Ensure coding-agent updated progress before stopping.

```bash
#!/bin/bash
# .claude/hooks/verify-coding-agent.sh

# Only run for coding-agent
AGENT_NAME=${1:-"unknown"}

if [[ "$AGENT_NAME" != "coding-agent" ]]; then
    exit 0
fi

# Check if progress was updated
SESSION_STATE=".claude/progress/session-state.json"
FEATURE_LIST=".claude/progress/feature-list.json"

if [ ! -f "$SESSION_STATE" ] || [ ! -f "$FEATURE_LIST" ]; then
    echo "⚠️  Progress files not found. Please ensure they are created." >&2
    exit 1
fi

# Get last update times
FEATURE_UPDATE=$(date -r "$FEATURE_LIST" +%s 2>/dev/null || echo 0)
SESSION_UPDATE=$(date -r "$SESSION_STATE" +%s 2>/dev/null || echo 0)
NOW=$(date +%s)

# Check if updates are recent (within 10 minutes)
FEATURE_AGE=$((NOW - FEATURE_UPDATE))
SESSION_AGE=$((NOW - SESSION_UPDATE))

if [ $FEATURE_AGE -gt 600 ] && [ $SESSION_AGE -gt 600 ]; then
    echo "⚠️  WARNING: Progress tracking may not be up to date!" >&2
    echo "" >&2
    echo "Before stopping, please ensure you have:" >&2
    echo "1. Updated feature status in feature-list.json" >&2
    echo "2. Added session summary to claude-progress.txt" >&2
    echo "3. Committed all changes" >&2
    echo "" >&2
    echo "Last updates:" >&2
    echo "   Feature list: $((FEATURE_AGE / 60)) minutes ago" >&2
    echo "   Session state: $((SESSION_AGE / 60)) minutes ago" >&2
    echo "" >&2

    # Ask for confirmation
    read -p "Continue without updating progress? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please update progress before stopping the agent." >&2
        exit 1
    fi
fi

# Check for uncommitted changes
if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
    echo "⚠️  You have uncommitted changes!" >&2
    echo "   Please commit your work before stopping the agent." >&2
    git status --short >&2
    echo ""
    read -p "Continue without committing? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Progress verification complete" >&2
exit 0
```

### 5. Session End Handler (session-end.sh)

**Purpose**: Cleanly close sessions and prepare for recovery.

```bash
#!/bin/bash
# .claude/hooks/session-end.sh

SESSION_STATE=".claude/progress/session-state.json"

if [ -f "$SESSION_STATE" ]; then
    # Update session end time
    END_TIME=$(date -Iseconds)

    # Calculate duration
    START_TIME=$(cat "$SESSION_STATE" | jq -r '.started_at // "unknown"')
    if [[ "$START_TIME" != "unknown" ]]; then
        START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null || echo 0)
        END_EPOCH=$(date +%s)
        DURATION_MINUTES=$(((END_EPOCH - START_EPOCH) / 60))
    else
        DURATION_MINUTES=0
    fi

    # Update session state
    cat "$SESSION_STATE" | \
        jq "{
            .,
            \"status\": \"completed\",
            \"ended_at\": \"$END_TIME\",
            \"duration_minutes\": $DURATION_MINUTES
        }" > "$SESSION_STATE.tmp" && \
        mv "$SESSION_STATE.tmp" "$SESSION_STATE"

    # Log session completion
    SESSION_NUM=$(cat "$SESSION_STATE" | jq -r '.session_number // "?"')
    echo "Session #$SESSION_NUM completed successfully" >&2
    echo "Duration: $DURATION_MINUTES minutes" >&2
fi

# Clean up temporary files
rm -f .claude/temp/*.tmp 2>/dev/null

# Backup progress files
BACKUP_DIR=".claude/progress/backups"
mkdir -p "$BACKUP_DIR"
cp .claude/progress/*.json "$BACKUP_DIR/" 2>/dev/null || true

echo "Session cleanup complete" >&2
exit 0
```

## Advanced Hook Patterns

### 1. Context Injection Hook

Inject relevant context into user prompts automatically:

```bash
#!/bin/bash
# .claude/hooks/context-injection.sh

USER_PROMPT="$1"

# Add progress context if working on features
if [ -f ".claude/progress/session-state.json" ]; then
    CURRENT_FEATURE=$(cat .claude/progress/session-state.json | jq -r '.current_feature.id // "None"')

    if [[ "$CURRENT_FEATURE" != "None" ]]; then
        FEATURE_INFO=$(cat .claude/progress/feature-list.json | \
            jq --arg id "$CURRENT_FEATURE" \
            '.categories[].features[] | select(.id == $id)')

        echo "Current context: Working on $CURRENT_FEATURE"
        echo "Feature details: $FEATURE_INFO"
    fi
fi

# Pass through original prompt
echo "$USER_PROMPT"
```

### 2. Quality Gate Hook

Enforce quality standards before commits:

```bash
#!/bin/bash
# .claude/hooks/quality-gate.sh

# Run only before commit operations
if [[ "$1" != "pre-commit" ]]; then
    exit 0
fi

# Check if tests pass
if command -v npm >/dev/null 2>&1; then
    if ! npm test --silent 2>/dev/null; then
        echo "❌ Tests are failing. Please fix before committing." >&2
        exit 1
    fi
fi

# Check code coverage (if configured)
if [ -f "coverage/coverage-summary.json" ]; then
    COVERAGE=$(cat coverage/coverage-summary.json | jq -r '.total.lines.pct')
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
        echo "⚠️  Code coverage is ${COVERAGE}%. Consider adding tests." >&2
    fi
fi

# Check for TODOs in committed files
TODO_COUNT=$(git diff --cached --name-only | xargs grep -l "TODO\|FIXME" 2>/dev/null | wc -l)
if [ $TODO_COUNT -gt 0 ]; then
    echo "⚠️  Found TODOs/FIXMEs in files being committed:" >&2
    git diff --cached --name-only | xargs grep -n "TODO\|FIXME" 2>/dev/null >&2
    echo "" >&2
    echo "Consider addressing these before committing." >&2
fi

exit 0
```

### 3. Resource Monitor Hook

Monitor system resources during long-running sessions:

```bash
#!/bin/bash
# .claude/hooks/resource-monitor.sh

# Check system resources every 10 minutes
INTERVAL=600

while true; do
    # Check disk space
    DISK_USAGE=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 90 ]; then
        echo "⚠️  Disk usage is ${DISK_USAGE}%. Consider cleaning up." >&2
    fi

    # Check memory usage
    if command -v free >/dev/null 2>&1; then
        MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ $MEM_USAGE -gt 90 ]; then
            echo "⚠️  Memory usage is ${MEM_USAGE}%." >&2
        fi
    fi

    # Check for large temp files
    TEMP_SIZE=$(du -sh .claude/temp 2>/dev/null | awk '{print $1}' | sed 's/[A-Z]//')
    if [[ "$TEMP_SIZE" -gt 100 ]]; then  # More than 100MB
        echo "⚠️  Temp directory is large (${TEMP_SIZE}MB). Consider cleanup." >&2
    fi

    sleep $INTERVAL
done &
```

## Hook Configuration Patterns

### 1. Conditional Hooks

Run hooks only for specific conditions:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "agent": "opus",
          "tool": ["Edit", "Write"]
        },
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/block-opus-edits.sh"
          }
        ]
      }
    ]
  }
}
```

### 2. Hook Chains

Run multiple hooks in sequence:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/update-progress-reminder.sh"
          },
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/quality-check.sh"
          },
          {
            "type": "notification",
            "message": "Remember to commit your changes!"
          }
        ]
      }
    ]
  }
}
```

### 3. Hook Parameters

Pass parameters to hooks:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash .claude/hooks/session-check.sh",
            "args": {
              "heartbeat_timeout": 1800,
              "require_clean_git": true
            }
          }
        ]
      }
    ]
  }
}
```

## Testing Hooks

### Unit Testing Hooks

```bash
#!/bin/bash
# test-hooks.sh

# Test pre-tool-guard hook
echo "Testing pre-tool-guard..."
echo '{"tool": "Edit", "file_path": "src/test.js"}' | .claude/hooks/pre-tool-guard.sh
[ $? -eq 1 ] && echo "✅ Correctly blocked Edit on src/" || echo "❌ Failed to block"

echo '{"tool": "Read", "file_path": "src/test.js"}' | .claude/hooks/pre-tool-guard.sh
[ $? -eq 0 ] && echo "✅ Correctly allowed Read on src/" || echo "❌ Failed to allow"

# Test session-progress-check
echo "Testing session-progress-check..."
# Create test session state
cat > test-session.json << EOF
{
  "session_number": 1,
  "status": "active",
  "heartbeat": {
    "last_heartbeat": "2025-01-01T10:00:00Z"
  }
}
EOF

.claude/hooks/session-progress-check.sh < test-session.json
echo "✅ Session check completed"
```

### Integration Testing

```bash
#!/bin/bash
# integration-test.sh

# Set up test environment
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"
mkdir -p .claude/{hooks,progress}

# Copy hooks to test
cp ~/.claude/skills/progress-harness/assets/hooks/* .claude/hooks/

# Test full session flow
echo "Starting integration test..."

# 1. Session start
.claude/hooks/session-progress-check.sh

# 2. Simulate tool usage
echo '{"tool": "Write", "file_path": "test.js"}' | .claude/hooks/pre-tool-guard.sh
echo '{"tool": "Write", "file_path": "test.js"}' | .claude/hooks/post-tool-guard.sh

# 3. Session end
.claude/hooks/session-end.sh

echo "✅ Integration test passed"
cd ..
rm -rf "$TEST_DIR"
```

## Troubleshooting Hooks

### Common Issues

1. **Hook Not Executing**
   - Check file permissions: `chmod +x .claude/hooks/*.sh`
   - Verify .claude/settings.json format
   - Check Claude Code logs for errors

2. **Hook Failing Silently**
   - Add debug output: `echo "Hook running..." >&2`
   - Check exit codes: `echo $?` after hook execution
   - Run hook manually to test

3. **Performance Issues**
   - Profile hook execution time
   - Optimize heavy operations
   - Consider running expensive checks asynchronously

### Debug Mode Hook

```bash
#!/bin/bash
# .claude/hooks/debug-wrapper.sh

# Enable debug mode
if [ "$DEBUG_HOOKS" = "1" ]; then
    echo "=== DEBUG: Hook $0 ===" >&2
    echo "Input: $1" >&2
    echo "Environment:" >&2
    env | grep HOOK >&2
    echo "========================" >&2
fi

# Run actual hook
"$@"
EXIT_CODE=$?

if [ "$DEBUG_HOOKS" = "1" ]; then
    echo "=== Hook exit code: $EXIT_CODE ===" >&2
fi

exit $EXIT_CODE
```

## Best Practices

### 1. Hook Design
- Keep hooks focused and simple
- Use descriptive error messages
- Log important events for debugging
- Handle edge cases gracefully

### 2. Performance
- Minimize blocking operations
- Cache expensive computations
- Use background processes for monitoring
- Implement timeouts for long operations

### 3. Maintainability
- Document hook purpose and behavior
- Use version control for hook changes
- Test hooks thoroughly before deployment
- Monitor hook execution in production

### 4. Security
- Validate all inputs
- Use absolute paths for commands
- Avoid executing user input directly
- Review hooks for security vulnerabilities

### 5. User Experience
- Provide clear feedback messages
- Offer recovery options when possible
- Allow bypass for emergency situations
- Keep messages concise and actionable

## Hook Evolution

### Phase 1: Basic Enforcement
- Block unauthorized edits
- Remind about progress updates
- Detect session interruptions

### Phase 2: Quality Assurance
- Automated testing gates
- Code quality checks
- Performance monitoring

### Phase 3: Intelligence
- Predictive block detection
- Smart context injection
- Adaptive enforcement

The hook system is essential for maintaining the integrity and effectiveness of the Two-Agent Framework, ensuring that agents follow proper workflows and that development progresses smoothly and predictably.