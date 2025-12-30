# Sandbox Runtime - Layer 2 Enforcement

**Repository**: [anthropic-experimental/sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime)

**Purpose**: OS-level sandboxing for MCP servers, enforcing filesystem and network restrictions at the process level.

---

## Alignment with DESIGN-v2.md

```
sandbox-runtime → Layer 2 (Enforcement)
├── Filesystem isolation     └→ denyRead, allowWrite, denyWrite
├── Network isolation         └→ allowedDomains, deniedDomains
├── Violation monitoring      └→ SandboxViolationStore (learning traces)
└── Proxy-based filtering     └→ HTTP + SOCKS5 proxies
```

---

## Installation

```bash
npm install -g @anthropic-ai/sandbox-runtime
```

### Platform Dependencies

| Platform | Required | Installation |
|----------|----------|--------------|
| **macOS** | `ripgrep` | `brew install ripgrep` |
| **Linux** | `bubblewrap`, `socat`, `ripgrep` | `apt install bubblewrap socat ripgrep` |
| **Windows** | Not supported | - |

---

## Configuration

### Settings File: `~/.srt-settings.json`

```json
{
  "network": {
    "allowedDomains": [
      "github.com",
      "*.github.com",
      "api.anthropic.com",
      "npmjs.org",
      "*.npmjs.org"
    ],
    "deniedDomains": [],
    "allowUnixSockets": [],
    "allowLocalBinding": false
  },
  "filesystem": {
    "denyRead": ["~/.ssh", "~/.aws", "~/.gnupg"],
    "allowWrite": [".", "src/", "test/", "/tmp"],
    "denyWrite": [".env", "*.key", ".claude/"]
  },
  "ignoreViolations": {
    "*": ["/usr/bin", "/System"],
    "npm": ["/private/tmp"]
  },
  "enableWeakerNestedSandbox": false
}
```

### Permission Patterns

| Type | Pattern | Default | Behavior |
|------|---------|---------|----------|
| **Read** | deny-only | Allow all | Block specific paths |
| **Write** | allow-only | Deny all | Allow specific paths |
| **Network** | allow-only | Deny all | Allow specific domains |

### Glob Pattern Support (macOS)

```
*     → matches any chars except /
**    → matches any chars including /
?     → matches single char except /
[abc] → character class
[0-9] → character range
```

**Note**: Linux does NOT support glob patterns. Use literal paths only.

---

## MCP Server Integration

### Pattern: Wrap MCP Commands with `srt`

**Before** (`.mcp.json`):
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
    },
    "github": {
      "command": "srt",
      "args": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    },
    "token-efficient": {
      "command": "srt",
      "args": ["npx", "-y", "@anthropic-ai/mcp-server-token-efficient"]
    }
  }
}
```

### Per-Project Config (`.srt-settings.json` in project root)

For agent-harness specific restrictions:

```json
{
  "network": {
    "allowedDomains": ["github.com", "*.github.com", "api.anthropic.com"],
    "deniedDomains": []
  },
  "filesystem": {
    "denyRead": ["~/.ssh", "~/.aws"],
    "allowWrite": [".", ".skills/", ".claude/progress/"],
    "denyWrite": [".env", ".claude/settings.json", "node_modules/"]
  }
}
```

Then use with `--settings` flag:
```bash
srt --settings .srt-settings.json <command>
```

---

## Library Usage (TypeScript)

### Initialize and Run Commands

```typescript
import {
  SandboxManager,
  type SandboxRuntimeConfig
} from '@anthropic-ai/sandbox-runtime'
import { spawn } from 'child_process'

const config: SandboxRuntimeConfig = {
  network: {
    allowedDomains: ['github.com', '*.npmjs.org'],
    deniedDomains: []
  },
  filesystem: {
    denyRead: ['~/.ssh'],
    allowWrite: ['.', '/tmp'],
    denyWrite: ['.env']
  }
}

await SandboxManager.initialize(config)

const sandboxedCommand = await SandboxManager.wrapWithSandbox(
  'curl https://api.github.com/repos/anthropics/claude-code'
)

const child = spawn(sandboxedCommand, { shell: true, stdio: 'inherit' })

child.on('exit', (code) => {
  console.log(`Exited with code ${code}`)
})
```

### Runtime Inspection

```typescript
// Get filesystem restrictions
const readConfig = SandboxManager.getFsReadConfig()
console.log('Denied reads:', readConfig.denyOnly)

const writeConfig = SandboxManager.getFsWriteConfig()
console.log('Allowed writes:', writeConfig.allowOnly)

// Get network restrictions
const networkConfig = SandboxManager.getNetworkRestrictionConfig()
console.log('Allowed hosts:', networkConfig.allowedHosts)
```

### Validation with Zod

```typescript
import {
  SandboxRuntimeConfigSchema,
  NetworkConfigSchema
} from '@anthropic-ai/sandbox-runtime'

const result = SandboxRuntimeConfigSchema.safeParse(config)

if (!result.success) {
  result.error.issues.forEach(issue => {
    console.error(`${issue.path.join('.')}: ${issue.message}`)
  })
}
```

---

## Enforcement Integration

### Violation Monitoring (Learning Loop)

```typescript
import { SandboxViolationStore } from '@anthropic-ai/sandbox-runtime'

// Enable violation monitoring (macOS)
await SandboxManager.initialize(config, undefined, true)

// Violations logged to store for learning traces
// Can be queried for pattern detection
```

### Verification Scripts

```bash
# Check if sandbox is working
srt "cat ~/.ssh/id_rsa"
# Expected: "Operation not permitted"

# Test network restrictions
srt "curl https://blocked-domain.com"
# Expected: "Connection blocked by network allowlist"

# Verify allowed writes
srt "echo test > /tmp/sandbox-test.txt"
# Expected: Success
```

---

## Mandatory Deny Paths (Auto-Protected)

These paths are **always blocked** from writes, even in allowed paths:

**Files**:
- Shell configs: `.bashrc`, `.bash_profile`, `.zshrc`, `.zprofile`, `.profile`
- Git configs: `.gitconfig`, `.gitmodules`
- Claude configs: `.ripgreprc`, `.mcp.json`

**Directories**:
- IDE: `.vscode/`, `.idea/`
- Claude: `.claude/commands/`, `.claude/agents/`
- Git: `.git/hooks/`, `.git/config`

**Note**: On Linux, only existing files are blocked. macOS blocks patterns for existing + new files.

---

## CLI Usage

```bash
# Basic usage
srt <command>

# With debug logging
srt --debug curl https://example.com

# Custom settings file
srt --settings /path/to/settings.json npm install

# Check sandbox violations (macOS)
log stream --predicate 'process == "sandbox-exec"' --style syslog

# Trace blocked operations (Linux)
strace -f srt <command> 2>&1 | grep EPERM
```

---

## Security Considerations

| Risk | Mitigation |
|------|------------|
| **Domain fronting** | Narrow allowed domains, inspect traffic |
| **Unix socket escalation** | Avoid `allowUnixSockets: ["/var/run/docker.sock"]` |
| **Filesystem escalation** | Don't allow writes to `$PATH` dirs or shell configs |
| **Nested sandbox weakness** | Only use `enableWeakerNestedSandbox: true` in Docker |

---

## Integration with agent-harness

### 1. Layer 2 Enforcement Tool

| Feature | Maps To |
|---------|---------|
| Filesystem restrictions | Skills isolation |
| Network allowlists | External API gating |
| Violation logs | Learning traces |

### 2. Verification Scripts

Location: `.skills/enforcement/scripts/`

- `verify-sandbox.sh` - Test sandbox restrictions
- `verify-mcp-sandboxed.sh` - Check MCP servers wrapped with srt

### 3. Learning Loop

```
Enforcement hook blocks action
         ↓
Log: { state, action, violation_type, path }
         ↓
Pattern detection (3+ similar violations)
         ↓
Update skill OR create guard hook
```

---

## Common Recipes

### Allow GitHub Access

```json
{
  "network": {
    "allowedDomains": [
      "github.com",
      "*.github.com",
      "lfs.github.com",
      "api.github.com"
    ]
  },
  "filesystem": {
    "denyRead": [],
    "allowWrite": ["."],
    "denyWrite": []
  }
}
```

### Restrict to Project Directory

```json
{
  "network": {
    "allowedDomains": []
  },
  "filesystem": {
    "denyRead": ["~/.ssh", "~/.aws"],
    "allowWrite": ["."],
    "denyWrite": [".env", "config/production.json"]
  }
}
```

### Jest with Sandbox (macOS)

```bash
srt "jest --no-watchman"
```

---

## Resources

- [GitHub Repository](https://github.com/anthropic-experimental/sandbox-runtime)
- [NPM Package](https://www.npmjs.com/package/@anthropic-ai/sandbox-runtime)
- [Claude Code Sandboxing Documentation](https://code.claude.com/sandboxing)
- [Blog: Beyond Permission Prompts](https://www.anthropic.com/blog/making-claude-code-more-secure)

---

*Added: 2025-12-28*
*Status: Layer 2 enforcement integration reference*
