---
name: mcp-setup
description: "Use when setting up MCP servers for the first time or verifying MCP configuration. Ensures token-efficient and context-graph MCP servers are properly installed and configured with API keys."
keywords: mcp, setup, installation, configuration, voyager-ai, token-efficient
---

# MCP Setup

Configure required MCP servers for agent-harness token efficiency and learning loops.

## Required MCP Servers

| Server | Purpose | API Key |
|--------|---------|---------|
| `token-efficient` | CSV/log processing, sandbox execution (98% token savings) | None |
| `context-graph` | Semantic decision trace search | Voyage AI |

## Setup Instructions

### 1. Install token-efficient MCP

```bash
# Clone and build
git clone https://github.com/gurusharan/token-efficient-mcp.git ~/token-efficient-mcp
cd ~/token-efficient-mcp
npm install
npm run build
```

### 2. Install context-graph MCP

```bash
# Already in agent-harness, just install dependencies
cd /path/to/agent-harness/context-graph-mcp
pip install -r requirements.txt
```

### 3. Get Voyage AI API Key

1. Sign up at https://voyageai.com
2. Get API key from dashboard
3. Export: `export VOYAGE_API_KEY="your_key_here"`

### 4. Configure MCP

**Project-level** `.mcp.json` at agent-harness root:

```json
{
  "mcpServers": {
    "token-efficient": {
      "command": "srt",
      "args": ["node", "/absolute/path/to/token-efficient-mcp/dist/index.js"]
    },
    "context-graph": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/agent-harness/context-graph-mcp",
        "run",
        "python",
        "server.py"
      ],
      "env": {
        "VOYAGE_API_KEY": "your_key_here"
      }
    }
  }
}
```

Paths are auto-detected by the setup script.

### 5. Verify

```bash
# Restart Claude Code, then check tools are available
# You should see: context_store_trace, context_query_traces, etc.
```

## Quick Setup Script

Run `scripts/setup-all.sh` to automate:

1. Clone/build token-efficient MCP
2. Install context-graph dependencies
3. Prompt for Voyage AI key
4. Generate project-level `.mcp.json` at agent-harness root

## Verification

After setup, test:

```python
# Via context-graph MCP
context_store_trace(decision="Test setup", category="general")
context_list_categories()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `module 'chromadb' not found` | `pip install chromadb` |
| `VOYAGE_API_KEY not found` | Set env var or add to mcp.json env |
| Tools not available | Restart Claude Code |
| `srt: command not found` | Install token-efficient MCP |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup-all.sh` | **Use this** - Auto-detects paths, sets up both MCP servers |
| `scripts/verify-setup.sh` | Check if MCP servers are working |
| `scripts/install-token-efficient.sh` | Standalone token-efficient MCP installer |
