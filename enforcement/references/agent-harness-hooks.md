# Agent-Harness Specific Hooks

Enforcement patterns for the agent-harness state machine system.

## Hook 1: Block Implementing Non-Existent Feature

**File**: `.claude/hooks/block-invalid-feature.py`
**Event**: PreToolUse (Write/Edit)
**Purpose**: Prevent implementing features not in feature-list.json

```python
#!/usr/bin/env python3
"""
Block coding-agent from implementing features not in feature-list.json
"""

import json
import sys
import os

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only check src/ files
    if not file_path.startswith("src/") and "/src/" not in file_path:
        sys.exit(0)

    # Load feature list
    feature_file = ".claude/progress/feature-list.json"
    if not os.path.exists(feature_file):
        print("BLOCKED: No feature-list.json. Run initialization skill first.", file=sys.stderr)
        sys.exit(2)

    with open(feature_file) as f:
        features = json.load(f)

    # Get pending feature IDs
    pending_ids = [f["id"] for f in features if f["status"] == "pending"]

    if not pending_ids:
        print("BLOCKED: No pending features to implement", file=sys.stderr)
        print("Available features:", [f["id"] for f in features], file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook 2: Block COMPLETE Without All Tested

**File**: `.claude/hooks/block-incomplete.py`
**Event**: PreToolUse (Write state.json)
**Purpose**: Prevent COMPLETE state if any feature is untested

```python
#!/usr/bin/env python3
"""
Block transition to COMPLETE if any feature isn't tested
"""

import json
import sys
import os

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    content = tool_input.get("content", "")

    # Check if setting state to COMPLETE
    if '"state": "COMPLETE"' not in content and '"state":"COMPLETE"' not in content:
        sys.exit(0)

    # Load feature list
    feature_file = ".claude/progress/feature-list.json"
    if not os.path.exists(feature_file):
        sys.exit(0)

    with open(feature_file) as f:
        features = json.load(f)

    # Check for untested features
    untested = [f["id"] for f in features if f.get("status") != "tested"]

    if untested:
        print(f"BLOCKED: Cannot enter COMPLETE - {len(untested)} features untested", file=sys.stderr)
        print(f"Untested: {untested}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook 3: Token Efficiency Warning

**File**: `.claude/hooks/warn-token-usage.py`
**Event**: PostToolUse
**Purpose**: Warn when operations use excessive tokens (non-blocking)

```python
#!/usr/bin/env python3
"""
PostToolUse hook: Warn when operations use >10K tokens
Non-blocking - just logs the warning
"""

import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_result = input_data.get("tool_result", {})
    tool_name = input_data.get("tool_name", "")

    # Check token usage in result
    result_str = json.dumps(tool_result)
    if "input_tokens" in result_str or "output_tokens" in result_str:
        try:
            input_tokens = tool_result.get("input_tokens", 0)
            output_tokens = tool_result.get("output_tokens", 0)
            total = input_tokens + output_tokens

            if total > 10000:
                print(f"⚠️  HIGH TOKEN USAGE: {tool_name} used {total:,} tokens", file=sys.stderr)
                print(f"   Input: {input_tokens:,}, Output: {output_tokens:,}", file=sys.stderr)
                print(f"   Consider: defer_loading, progressive disclosure, or MCP tools", file=sys.stderr)
        except:
            pass

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook 4: Require Code Review for Core Files

**File**: `.claude/hooks/require-code-review.py`
**Event**: PreToolUse (Write/Edit)
**Purpose**: Block edits to core files without explicit review flag

```python
#!/usr/bin/env python3
"""
Block edits to core files without 'reviewed' flag in system prompt
"""

import json
import sys

CORE_FILES = [
    "src/state-machine.ts",
    "src/orchestrator.ts",
    "src/enforcement.ts",
]

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Check if editing core file
    if file_path not in CORE_FILES:
        sys.exit(0)

    # Check for reviewed flag (would be in a metadata file)
    review_file = ".claude/pending-review.json"
    import os
    if not os.path.exists(review_file):
        print(f"BLOCKED: Editing core file {file_path} requires review", file=sys.stderr)
        print("1. Create .claude/pending-review.json with:", file=sys.stderr)
        print(f'   {{"file": "{file_path}", "reason": "..."}}', file=sys.stderr)
        print("2. Get explicit user approval", file=sys.stderr)
        sys.exit(2)

    with open(review_file) as f:
        review = json.load(f)
    if review.get("file") != file_path or not review.get("approved"):
        print(f"BLOCKED: Core file edit not approved: {file_path}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook 5: Enforce Determinism Checks

**File**: `.claude/hooks/require-determinism.py`
**Event**: PreToolUse (any)
**Purpose**: Ensure temperature=0 for critical state changes

```python
#!/usr/bin/env python3
"""
Block critical operations without temperature=0
"""

import json
import sys

CRITICAL_OPERATIONS = ["Write", "Edit", "state.json", "feature-list.json"]

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check critical tools
    if tool_name not in CRITICAL_OPERATIONS[:2]:  # Write, Edit
        sys.exit(0)

    file_path = tool_input.get("file_path", "")

    # Only check critical files
    if not any(f in file_path for f in CRITICAL_OPERATIONS[2:]):
        sys.exit(0)

    # Check for determinism flag (would be set by orchestrator)
    import os
    if os.path.exists(".claude/deterministic-mode"):
        sys.exit(0)

    print("BLOCKED: Critical operation requires temperature=0", file=sys.stderr)
    print(f"File: {file_path}", file=sys.stderr)
    print("Set deterministic mode first", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    main()
```

---

## Hook 6: MCP Server Sandboxing Verification

**File**: `.claude/hooks/verify-mcp-sandboxed.py`
**Event**: PreToolUse (Write .mcp.json)
**Purpose**: Ensure MCP servers are wrapped with `srt` for security isolation

```python
#!/usr/bin/env python3
"""
Verify MCP servers are wrapped with sandbox-runtime (srt)
Implements Layer 2 enforcement: OS-level isolation for external tools
"""

import json
import sys

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # Only check .mcp.json writes
    if ".mcp.json" not in file_path:
        sys.exit(0)

    try:
        config = json.loads(content)
        mcp_servers = config.get("mcpServers", {})

        # Check each MCP server
        unsandboxed = []
        for name, server in mcp_servers.items():
            command = server.get("command", "")
            # Allow local scripts (they run in current shell context)
            if command.startswith("./") or command.startswith("python") or command.startswith("node"):
                continue
            # npx commands should be wrapped with srt
            if "npx" in command and "srt" not in command:
                unsandboxed.append(name)

        if unsandboxed:
            print("BLOCKED: MCP servers must be wrapped with 'srt' for security isolation", file=sys.stderr)
            print(f"Unsandboxed servers: {unsandboxed}", file=sys.stderr)
            print("", file=sys.stderr)
            print("Fix pattern:", file=sys.stderr)
            print('  "command": "srt",', file=sys.stderr)
            print('  "args": ["npx", "-y", "@package/name"]', file=sys.stderr)
            print("", file=sys.stderr)
            print("See: .skills/enforcement/references/sandbox-runtime.md", file=sys.stderr)
            sys.exit(2)

    except json.JSONDecodeError:
        # Not JSON yet, allow write
        sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## Hook 7: Verify srt Configuration

**File**: `.claude/hooks/verify-srt-config.py`
**Event**: PermissionRequest (for file operations)
**Purpose**: Block access to sensitive paths even if sandboxed

```python
#!/usr/bin/env python3
"""
Additional enforcement: Block access to sensitive paths
Works alongside srt for defense-in-depth
"""

import json
import sys
import os

# Mandatory deny paths (beyond srt defaults)
MANDATORY_DENY = [
    "~/.ssh",
    "~/.aws",
    "~/.gnupg",
    "~/.docker",
]

def main():
    input_data = json.load(sys.stdin)
    permission_request = input_data.get("permissionRequest", {})
    file_path = permission_request.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Expand user path
    expanded = os.path.expanduser(file_path)
    home = os.path.expanduser("~")

    # Check against mandatory deny
    for deny in MANDATORY_DENY:
        deny_expanded = os.path.expanduser(deny)
        if expanded.startswith(deny_expanded):
            print(f"BLOCKED: Access to sensitive path denied: {deny}", file=sys.stderr)
            print(f"Attempted: {file_path}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## MCP Server Sandboxing Pattern

**Pattern**: Wrap all external MCP servers with `srt`

**Before** (unsafe):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    }
  }
}
```

**After** (sandboxed):
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "srt",
      "args": ["npx", "-y", "@modelcontextprotocol/server-filesystem"]
    }
  }
}
```

**See**: `.skills/enforcement/references/sandbox-runtime.md` for full configuration

---

## Settings.json for Agent-Harness

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": { "tool_name": "Write|Edit" },
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/validate-transition.py" },
          { "type": "command", "command": "python3 .claude/hooks/block-invalid-feature.py" },
          { "type": "command", "command": "python3 .claude/hooks/block-incomplete.py" },
          { "type": "command", "command": "python3 .claude/hooks/require-determinism.py" },
          { "type": "command", "command": "python3 .claude/hooks/verify-mcp-sandboxed.py" }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/verify-srt-config.py" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/warn-token-usage.py" }
        ]
      }
    ]
  }
}
```

---

## Hook 8: Require Git Commit Before Tested

**File**: `.claude/hooks/require-commit-before-tested.py`
**Event**: PreToolUse (Write feature-list.json)
**Purpose**: Block marking feature as tested without committing changes first

From Anthropic Effective Harnesses: *"Git commit history with descriptive messages"*

```python
#!/usr/bin/env python3
"""
Block marking feature as tested without git commit.
"""

import json
import sys
import subprocess

def has_uncommitted_changes() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=5
    )
    return bool(result.stdout.strip())

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # Only check writes to feature-list.json
    if "feature-list.json" not in file_path:
        sys.exit(0)

    # Only check if setting status to "tested"
    if '"status": "tested"' not in content:
        sys.exit(0)

    # Block if uncommitted changes exist
    if has_uncommitted_changes():
        print("BLOCKED: Cannot mark feature as tested with uncommitted changes", file=sys.stderr)
        print("Run: .skills/implementation/scripts/feature-commit.sh <feature-id>", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Integration with feature-commit.sh**:
```bash
# 1. Implement feature
# 2. Run tests
# 3. Commit with feature ID
.skills/implementation/scripts/feature-commit.sh feat-001 "Implement user login"

# 4. Now marking tested will succeed
# (hook checks for clean git status)
```

---

## Hook 9: Require Dependencies Before Feature Work

**File**: `.claude/hooks/require-dependencies.py`
**Event**: PreToolUse (Write/Edit src/ files)
**Purpose**: Block feature implementation if required dependencies are missing

From Anthropic Effective Harnesses: *"init.sh script for development server startup"*

```python
#!/usr/bin/env python3
"""
Block feature work if required dependencies are missing.
"""

import json
import sys
import os

def load_project_config() -> dict:
    config_path = ".claude/config/project.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}

def check_required_env(config: dict) -> list:
    missing = []
    required = config.get("required_env", [])
    for var in required:
        if not os.environ.get(var):
            missing.append(var)
    return missing

def main():
    input_data = json.load(sys.stdin)
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only check writes to src/ files (feature implementation)
    if not file_path:
        sys.exit(0)

    # Allow writes to config and progress files
    if ".claude/" in file_path or "config" in file_path:
        sys.exit(0)

    # Only check src/ or app/ directories
    is_source_file = any(x in file_path for x in ["/src/", "/app/", "/lib/", "/components/"])
    if not is_source_file:
        sys.exit(0)

    # Load config and check dependencies
    config = load_project_config()
    if not config:
        sys.exit(0)

    missing_env = check_required_env(config)

    if missing_env:
        print("BLOCKED: Missing required environment variables", file=sys.stderr)
        for var in missing_env:
            print(f"  - {var}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Set these variables before implementing features:", file=sys.stderr)
        print(f"  export {missing_env[0]}=your_value", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Configuration** (`.claude/config/project.json`):
```json
{
  "required_env": ["DATABASE_URL", "API_KEY", "SECRET_KEY"]
}
```

---

## Quick Reference

| Hook | Blocks | Event | Use Case |
|------|--------|-------|----------|
| validate-transition.py | Invalid state changes | PreToolUse | State machine enforcement |
| block-tested-true.py | tested:true without evidence | PreToolUse | Quality gate |
| block-invalid-feature.py | Implementing non-existent feature | PreToolUse | Feature validation |
| block-incomplete.py | COMPLETE with untested features | PreToolUse | Completion gate |
| warn-token-usage.py | (Warning only) | PostToolUse | Token efficiency |
| require-code-review.py | Core file edits without approval | PreToolUse | Safety gate |
| require-determinism.py | Critical ops without temp=0 | PreToolUse | Determinism |
| verify-mcp-sandboxed.py | Unwrapped MCP servers | PreToolUse | Layer 2 security isolation |
| verify-srt-config.py | Sensitive path access | PermissionRequest | Defense-in-depth file protection |
| require-commit-before-tested.py | tested:true without commit | PreToolUse | Git integration |
| require-dependencies.py | src/ writes without deps | PreToolUse | External dependencies |
