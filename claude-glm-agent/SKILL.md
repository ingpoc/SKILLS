---
name: claude-glm-agent
description: "Use when configuring apps to use z.ai GLM 4.7 proxy instead of standard Anthropic API. Works with any frontend (Next.js, Vite) or backend (Python, Node.js) framework."
context: fork
agent: general-purpose
---

# Claude GLM Agent Configuration

Configure any app to use z.ai GLM 4.7 proxy instead of standard Anthropic API.

## Quick Start

```bash
# Initialize project for GLM configuration
~/.claude/skills/claude-glm-agent/scripts/init-glm.sh

# Configure .env files
./.claude/scripts/configure-glm.sh

# Test proxy connection
~/.claude/skills/claude-glm-agent/scripts/test-proxy.sh

# Migrate existing project from API_KEY to AUTH_TOKEN
./.claude/scripts/configure-glm.sh --migrate
```

## Configuration Workflows

### 1. New Frontend Project (Next.js)

| Step | Action |
|------|--------|
| 1 | Detect `package.json` with Next.js or Vite |
| 2 | Prompt for z.ai token |
| 3 | Create `.env.local` with `NEXT_PUBLIC_` prefix |
| 4 | Add ANTHROPIC_BASE_URL pointing to z.ai proxy |
| 5 | Add model overrides for GLM 4.7 |
| 6 | Test proxy connection |

### 2. New Backend Project (Python/Node)

| Step | Action |
|------|--------|
| 1 | Detect `requirements.txt` or `package.json` |
| 2 | Prompt for z.ai token |
| 3 | Create `.env` without public prefix |
| 4 | Add ANTHROPIC_BASE_URL and model overrides |
| 5 | Test proxy connection |

### 3. Existing Project Migration

| Step | Action |
|------|--------|
| 1 | Scan for existing ANTHROPIC_API_KEY |
| 2 | Backup current .env files |
| 3 | Replace with ANTHROPIC_AUTH_TOKEN |
| 4 | Add BASE_URL and model overrides |
| 5 | Update code if needed (client factory pattern) |
| 6 | Test and rollback on failure |

### 4. Netlify Deployment

| Step | Action |
|------|--------|
| 1 | Deploy via netlify-deploy skill |
| 2 | Set environment variables via Netlify dashboard |
| 3 | Configure ANTHROPIC_* variables for GLM 4.7 |
| 4 | Redeploy to apply changes |

## Environment Variables

### Required Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `ANTHROPIC_AUTH_TOKEN` | Your z.ai token | Authentication with z.ai proxy |
| `ANTHROPIC_BASE_URL` | `https://api.z.ai/api/anthropic` | Proxy endpoint |

### Optional Model Overrides

| Variable | Value | Purpose |
|----------|-------|---------|
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `glm-4.7` | Route Haiku requests to GLM 4.7 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `glm-4.7` | Route Sonnet requests to GLM 4.7 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `glm-4.7` | Route Opus requests to GLM 4.7 |

### Frontend vs Backend

| Environment | Variable Prefix | Example |
|-------------|-----------------|---------|
| Next.js (browser) | `NEXT_PUBLIC_` | `NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN` |
| Vite (browser) | `VITE_` | `VITE_ANTHROPIC_AUTH_TOKEN` |
| Backend (server) | None | `ANTHROPIC_AUTH_TOKEN` |

## Configuration Examples

### Next.js (.env.local)

```bash
# z.ai GLM 4.7 Proxy Configuration
NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN=your-zai-token-here
NEXT_PUBLIC_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
NEXT_PUBLIC_ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7
NEXT_PUBLIC_ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
NEXT_PUBLIC_ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7
```

### Vite (.env)

```bash
# z.ai GLM 4.7 Proxy Configuration
VITE_ANTHROPIC_AUTH_TOKEN=your-zai-token-here
VITE_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
VITE_ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7
VITE_ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
VITE_ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7
```

### Backend Python (.env)

```bash
# z.ai GLM 4.7 Proxy Configuration
ANTHROPIC_AUTH_TOKEN=your-zai-token-here
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7
```

### Backend Node.js (.env)

```bash
# z.ai GLM 4.7 Proxy Configuration
ANTHROPIC_AUTH_TOKEN=your-zai-token-here
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7
```

### Netlify Environment Variables

Set via dashboard or CLI:

```bash
netlify env:set ANTHROPIC_AUTH_TOKEN "your-zai-token"
netlify env:set ANTHROPIC_BASE_URL "https://api.z.ai/api/anthropic"
netlify env:set ANTHROPIC_DEFAULT_HAIKU_MODEL "glm-4.7"
netlify env:set ANTHROPIC_DEFAULT_SONNET_MODEL "glm-4.7"
netlify env:set ANTHROPIC_DEFAULT_OPUS_MODEL "glm-4.7"
```

## Code Patterns

### Client Factory Pattern

Best practice for environments requiring both standard and proxy API access:

```typescript
// lib/anthropic-client.ts
import Anthropic from '@anthropic-ai/sdk'

const baseURL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com'
const authToken = process.env.ANTHROPIC_AUTH_TOKEN || process.env.ANTHROPIC_API_KEY

export const anthropic = new Anthropic({
  baseURL,
  apiKey: authToken,
  defaultHeaders: {
    'anthropic-version': '2023-06-01'
  }
})
```

### Python Client

```python
# lib/anthropic_client.py
import os
from anthropic import Anthropic

base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')
auth_token = os.getenv('ANTHROPIC_AUTH_TOKEN') or os.getenv('ANTHROPIC_API_KEY')

anthropic = Anthropic(
    base_url=base_url,
    api_key=auth_token,
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check ANTHROPIC_AUTH_TOKEN is valid z.ai token |
| Connection timeout | Verify ANTHROPIC_BASE_URL is correct |
| Model not found | Check model overrides, ensure GLM 4.7 is available |
| CORS error (browser) | Ensure NEXT_PUBLIC_ or VITE_ prefix is used |
| Proxy not working | Run test-proxy.sh to verify connection |

## Migration Guide

### From ANTHROPIC_API_KEY to AUTH_TOKEN

| Step | Action |
|------|--------|
| 1 | Replace `ANTHROPIC_API_KEY` with `ANTHROPIC_AUTH_TOKEN` |
| 2 | Add `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic` |
| 3 | Add model override variables |
| 4 | Update code to use AUTH_TOKEN (or use fallback pattern) |
| 5 | Test with test-proxy.sh |

### Fallback Pattern (Best Practice)

Support both API_KEY and AUTH_TOKEN:

```typescript
const apiKey = process.env.ANTHROPIC_AUTH_TOKEN || process.env.ANTHROPIC_API_KEY
```

## Scripts

| Script | Purpose |
|--------|---------|
| `init-glm.sh` | Initialize project: copy configure-glm.sh to `.claude/scripts/` |
| `configure-glm.sh` | Configure .env files (copied to project) |
| `test-proxy.sh` | Test z.ai proxy connection |
| `migrate-env.sh` | Migrate from API_KEY to AUTH_TOKEN |

## Resources

| Resource | Load When |
|----------|-----------|
| `env-patterns.md` | Need environment variable patterns for specific frameworks |
| `client-config.md` | Need client factory pattern examples |
| `frameworks.md` | Need framework-specific setup instructions |
