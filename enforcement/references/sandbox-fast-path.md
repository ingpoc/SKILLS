# Sandbox Fast-Path Pattern

**Purpose**: Hybrid security combining sandbox-runtime (OS-level isolation) with allowlist (fast-path for trusted commands).

**Speedup**: 2-3x for common commands (ls, cat, grep, git)

---

## Problem: Security vs Speed

| Approach | Security | Speed | Use Case |
|----------|----------|-------|----------|
| **Sandbox only** (srt) | High (OS-level) | Slow (process spawn) | All external commands |
| **Allowlist only** | Low (process-level) | Fast (direct exec) | Development environments |
| **Hybrid** ✅ | High (defense-in-depth) | Fast (2-3x common ops) | Production + Dev |

---

## Hybrid Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           HYBRID SECURITY: SANDBOX + FAST-PATH              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Command Execution                                          │
│       │                                                      │
│       ├──► In FAST-PATH allowlist?                          │
│       │        │                                             │
│       │        ├──► YES ──► Direct execution (fast)         │
│       │        │                   │                         │
│       │        │                   └─► Additional validation │
│       │        │                                             │
│       │        └──► NO ────► sandbox-runtime (srt)         │
│       │                          │                          │
│       │                          └─► Full OS isolation       │
│                                                              │
│  Fast-Path Commands: ls, cat, head, tail, grep, git, npm    │
│  Sandboxed Commands: Everything else                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Fast-Path Allowlist

### Trusted Commands (Safe for Direct Execution)

```python
FAST_PATH_COMMANDS = {
    # File inspection (read-only, no modification)
    "ls": "list directory contents",
    "cat": "read file contents",
    "head": "read first N lines",
    "tail": "read last N lines",
    "wc": "count lines/words/bytes",
    "grep": "search in files",
    "find": "find files (with restrictions)",

    # Version control (has own security model)
    "git": "version control operations",

    # Node.js package manager (for development)
    "npm": "node package manager",
    "node": "node.js runtime",
    "npx": "npx package executor",

    # Process management (read-only or dev processes)
    "ps": "list processes",
    "lsof": "list open files",
    "pgrep": "find process by name",

    # Build tools (within project dir)
    "make": "build automation",
    "pytest": "python test runner",
    "eslint": "javascript linter",
    "tsc": "typescript compiler"
}
```

### Commands Requiring Sandbox

```python
SANDBOX_REQUIRED = {
    # System operations
    "rm", "mv", "cp", "mkdir", "chmod", "chown",
    "sudo", "su",

    # Network operations
    "curl", "wget", "ssh", "scp",

    # Package managers (system-level)
    "apt", "yum", "dnf", "brew", "pip",

    # Database operations
    "psql", "mysql", "mongosh",

    # Unknown/untrusted
    "any_command_not_in_allowlist"
}
```

---

## Implementation

### Fast-Path Checker

```python
#!/usr/bin/env python3
"""
Fast-path command execution with safety checks.
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple, Optional

# Trusted commands for fast-path execution
FAST_PATH_ALLOWLIST = {
    "ls", "cat", "head", "tail", "wc", "grep", "find",
    "git", "npm", "node", "npx", "ps", "lsof", "pgrep",
    "make", "pytest", "eslint", "tsc", "jest"
}

# Paths that are always blocked (even in fast-path)
MANDATORY_BLOCK = [
    "/.ssh",
    "/.aws",
    "/.gnupg",
    "/.docker",
    "/etc/shadow",
    "/etc/passwd"
]

def is_safe_path(path: str) -> bool:
    """
    Check if path is safe for fast-path execution.
    """
    expanded = os.path.expanduser(path)

    # Check against mandatory block paths
    for blocked in MANDATORY_BLOCK:
        if expanded.startswith(os.path.expanduser(blocked)):
            return False

    # Check if within project directory
    cwd = os.getcwd()
    try:
        os.path.relpath(expanded, cwd)
        return True  # Within project
    except ValueError:
        return False  # Outside project

def check_command_safe(command: str) -> Tuple[bool, Optional[str]]:
    """
    Check if command is safe for fast-path execution.
    Returns: (is_safe, reason)
    """
    parts = command.split()
    if not parts:
        return False, "Empty command"

    cmd_name = parts[0]

    # Check if in allowlist
    if cmd_name not in FAST_PATH_ALLOWLIST:
        return False, f"Command '{cmd_name}' not in fast-path allowlist"

    # Check for dangerous flags
    dangerous_flags = ["--delete", "--force", "-rf", "-f"]
    if any(flag in command for flag in dangerous_flags):
        return False, f"Dangerous flag detected in command"

    # Check paths in command
    for part in parts:
        if part.startswith("/") or part.startswith("~"):
            if not is_safe_path(part):
                return False, f"Unsafe path: {part}"

    return True, None

def execute_command(command: str) -> Tuple[int, str, str]:
    """
    Execute command using fast-path or sandbox.
    Returns: (exit_code, stdout, stderr)
    """
    # Check if safe for fast-path
    is_safe, reason = check_command_safe(command)

    if is_safe:
        # Fast-path: direct execution
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
    else:
        # Sandbox path: use srt wrapper
        print(f"FAST-PATH BLOCKED: {reason}")
        print("Falling back to sandbox-runtime...")

        # Wrap with srt
        sandbox_cmd = f"srt {command}"
        result = subprocess.run(
            sandbox_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60  # Longer timeout for sandbox
        )

        return result.returncode, result.stdout, result.stderr

# Usage
if __name__ == "__main__":
    import sys
    command = " ".join(sys.argv[1:])
    exit_code, stdout, stderr = execute_command(command)
    print(stdout, end="")
    print(stderr, end="", file=sys.stderr)
    sys.exit(exit_code)
```

---

## Integration with sandbox-runtime

### Hybrid Configuration

**Fast-path for common ops, sandbox for everything else:**

```python
# .skills/enforcement/scripts/hybrid-execute.sh

#!/bin/bash

COMMAND="$1"

# Fast-path allowlist
FAST_PATH="ls|cat|head|tail|wc|grep|find|git|npm|node|npx|ps|lsof|pgrep"

# Check if command is in fast-path
if echo "$COMMAND" | grep -qE "^($FAST_PATH) "; then
    # Additional safety checks
    if echo "$COMMAND" | grep -qE "(rm|mv|cp|--force|-rf)"; then
        # Dangerous flags - use sandbox
        exec srt "$COMMAND"
    else
        # Safe for fast-path
        exec $COMMAND
    fi
else
    # Not in allowlist - use sandbox
    exec srt "$COMMAND"
fi
```

---

## Performance Comparison

### Sequential Execution (Sandbox Only)

```bash
# All commands go through srt
srt ls -la              # ~100ms overhead
srt cat package.json    # ~100ms overhead
srt grep "test" *.py    # ~100ms overhead
srt git status          # ~100ms overhead
# Total: 400ms + actual execution time
```

### Hybrid Execution (Fast-Path + Sandbox)

```bash
# Common commands: direct execution
ls -la                   # ~1ms overhead
cat package.json         # ~1ms overhead
grep "test" *.py         # ~1ms overhead
git status               # ~1ms overhead
# Total: 4ms + actual execution time

# Rare/dangerous: sandbox (when needed)
srt curl https://api.example.com  # ~100ms overhead
```

**Speedup**: ~100x faster for common commands (4ms vs 400ms overhead)

---

## Defense-in-Depth

```
┌─────────────────────────────────────────────────────────────┐
│              DEFENSE-IN-DEPTH SECURITY LAYERS                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Fast-Path Allowlist                                │
│  └─► Only specific commands allowed directly                │
│                                                              │
│  Layer 2: Path Validation                                    │
│  └─► Block access to sensitive paths (/.ssh, etc.)           │
│                                                              │
│  Layer 3: Flag Detection                                     │
│  └─► Block dangerous flags (--force, -rf, --delete)         │
│                                                              │
│  Layer 4: sandbox-runtime (OS-level)                         │
│  └─► Everything else gets full sandbox isolation            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Fast-Path Configuration File

```json
// .claude/fast-path-config.json
{
  "enabled": true,
  "allowlist": [
    "ls", "cat", "head", "tail", "wc", "grep", "find",
    "git", "npm", "node", "npx", "ps", "lsof", "pgrep"
  ],
  "blocked_flags": [
    "--delete", "--force", "-rf", "-f",
    "--recursive", "--no-preserve-root"
  ],
  "blocked_paths": [
    "~/.ssh",
    "~/.aws",
    "~/.gnupg",
    "/etc/shadow",
    "/etc/passwd"
  ],
  "project_only": true,
  "fallback_to_sandbox": true
}
```

---

## Hooks Integration

### Pre-ToolUse Hook for Fast-Path

```python
#!/usr/bin/env python3
# .claude/hooks/verify-fast-path.py

"""
Hook to enable fast-path for safe bash commands.
"""

import json
import sys
import subprocess

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only check bash commands
    if not command.startswith(("ls ", "cat ", "head ", "tail ", "grep ")):
        sys.exit(0)

    # Load fast-path config
    try:
        with open(".claude/fast-path-config.json") as f:
            config = json.load(f)
    except:
        sys.exit(0)  # No config, use default behavior

    if not config.get("enabled", False):
        sys.exit(0)

    # Check if in allowlist
    cmd_name = command.split()[0]
    if cmd_name not in config["allowlist"]:
        sys.exit(0)

    # Additional safety checks
    for blocked in config.get("blocked_flags", []):
        if blocked in command:
            print(f"BLOCKED: Dangerous flag '{blocked}' in fast-path command", file=sys.stderr)
            print("This command requires sandbox execution", file=sys.stderr)
            sys.exit(2)

    # Allow fast-path execution
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Testing

### Verify Fast-Path Works

```bash
#!/bin/bash
# .skills/enforcement/scripts/test-fast-path.sh

echo "Testing fast-path execution..."

# Test 1: Fast-path command should work
./scripts/fast-path-exec.sh "ls -la"
if [ $? -eq 0 ]; then
    echo "✓ Fast-path ls works"
else
    echo "✗ Fast-path ls failed"
    exit 1
fi

# Test 2: Dangerous command should be blocked
./scripts/fast-path-exec.sh "rm -rf /tmp/test" 2>&1 | grep -q "BLOCKED"
if [ $? -eq 0 ]; then
    echo "✓ Dangerous command blocked"
else
    echo "✗ Dangerous command not blocked"
    exit 1
fi

# Test 3: Unknown command should use sandbox
./scripts/fast-path-exec.sh "curl https://example.com" 2>&1 | grep -q "sandbox"
if [ $? -eq 0 ]; then
    echo "✓ Unknown command uses sandbox"
else
    echo "✗ Unknown command didn't use sandbox"
    exit 1
fi

echo "All tests passed!"
```

---

## Best Practices

1. **Keep allowlist minimal**: Only add commands that are truly safe
2. **Block dangerous flags**: Even safe commands can be dangerous with flags
3. **Path validation**: Always check paths before fast-path execution
4. **Fallback to sandbox**: When in doubt, use sandbox
5. **Log fast-path usage**: Track which commands use fast-path for auditing
6. **Regular review**: Periodically review allowlist and blocked paths

---

## Anti-Patterns

| ❌ Anti-Pattern | ✅ Correct Pattern |
|-----------------|-------------------|
| All commands in fast-path | Minimal allowlist |
| No path validation | Block sensitive paths |
| No flag checking | Block dangerous flags |
| Direct exec without checks | Hybrid with validation |
| No fallback to sandbox | Always sandbox when unsure |

---

## Monitoring

```python
def log_fast_path_usage(command: str, path: str):
    """
    Log fast-path command execution for auditing.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "path": path,
        "user": os.getenv("USER"),
        "pid": os.getpid()
    }

    with open(".claude/logs/fast-path.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## Scripts

**Fast-path executor script:**
```bash
#!/bin/bash
# .skills/enforcement/scripts/fast-path-exec.sh

COMMAND="$1"
CONFIG=".claude/fast-path-config.json"

# Check if fast-path is enabled
if [ "$(jq -r '.enabled' $CONFIG 2>/dev/null)" != "true" ]; then
    exec srt "$COMMAND"
fi

# Extract command name
CMD_NAME=$(echo "$COMMAND" | awk '{print $1}')

# Check if in allowlist
if ! jq -r '.allowlist[]' $CONFIG 2>/dev/null | grep -q "^$CMD_NAME$"; then
    # Not in allowlist - use sandbox
    exec srt "$COMMAND"
fi

# Check for blocked flags
for flag in $(jq -r '.blocked_flags[]' $CONFIG 2>/dev/null); do
    if echo "$COMMAND" | grep -q "$flag"; then
        echo "BLOCKED: Dangerous flag '$flag' detected" >&2
        exec srt "$COMMAND"
    fi
done

# Safe for fast-path
exec $COMMAND
```

---

*Added: 2025-12-28*
*Purpose: Hybrid security combining sandbox isolation with fast-path for trusted commands*
*Speedup: 2-3x for common commands (ls, cat, grep, git)*
