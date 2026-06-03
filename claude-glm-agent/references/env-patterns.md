# GLM Environment Variable Patterns

## Environment Variable Naming

### Prefix Convention

| Framework | Prefix | Example |
|-----------|--------|---------|
| Next.js (client) | `NEXT_PUBLIC_` | `NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN` |
| Vite (client) | `VITE_` | `VITE_ANTHROPIC_AUTH_TOKEN` |
| Backend (Python/Node) | None | `ANTHROPIC_AUTH_TOKEN` |
| Netlify | Site-level | `ANTHROPIC_AUTH_TOKEN` |
| Vercel | Site-level | `ANTHROPIC_AUTH_TOKEN` |

### Variable Patterns

```bash
# Standard Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxx

# z.ai Proxy (Required)
ANTHROPIC_AUTH_TOKEN=your-zai-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic

# z.ai Proxy (Optional - Model Overrides)
ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.7
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.7
```

## Framework-Specific Patterns

### Next.js

**.env.local** (development):

```bash
NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN=your-token
NEXT_PUBLIC_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
NEXT_PUBLIC_ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
```

**.env.production** (production preview):

```bash
NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN=your-token
NEXT_PUBLIC_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**Access in code**:

```typescript
const baseURL = process.env.NEXT_PUBLIC_ANTHROPIC_BASE_URL
const token = process.env.NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN
```

### Vite

**.env**:

```bash
VITE_ANTHROPIC_AUTH_TOKEN=your-token
VITE_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
VITE_ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
```

**Access in code**:

```typescript
const baseURL = import.meta.env.VITE_ANTHROPIC_BASE_URL
const token = import.meta.env.VITE_ANTHROPIC_AUTH_TOKEN
```

### Python (FastAPI/Flask)

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
```

**Access in code**:

```python
import os
from anthropic import Anthropic

anthropic = Anthropic(
    base_url=os.getenv('ANTHROPIC_BASE_URL'),
    api_key=os.getenv('ANTHROPIC_AUTH_TOKEN')
)
```

### Node.js (Express)

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**Access in code**:

```typescript
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  baseURL: process.env.ANTHROPIC_BASE_URL,
  apiKey: process.env.ANTHROPIC_AUTH_TOKEN
})
```

### Go

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**Access in code**:

```go
import "os"

baseURL := os.Getenv("ANTHROPIC_BASE_URL")
token := os.Getenv("ANTHROPIC_AUTH_TOKEN")
```

### Rust

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**Access in code** (using dotenv):

```rust
dotenv().ok();
let token = std::env::var("ANTHROPIC_AUTH_TOKEN")?;
```

## Deployment Platform Patterns

### Netlify

Set via dashboard or CLI:

```bash
netlify env:set ANTHROPIC_AUTH_TOKEN "your-token"
netlify env:set ANTHROPIC_BASE_URL "https://api.z.ai/api/anthropic"
netlify env:set ANTHROPIC_DEFAULT_SONNET_MODEL "glm-4.7"
```

Or in **netlify.toml** (not recommended for secrets):

```toml
[context.production.environment]
ANTHROPIC_BASE_URL = "https://api.z.ai/api/anthropic"
ANTHROPIC_DEFAULT_SONNET_MODEL = "glm-4.7"
```

### Vercel

Set via dashboard or CLI:

```bash
vercel env add ANTHROPIC_AUTH_TOKEN
vercel env add ANTHROPIC_BASE_URL
```

Or in **.env.production**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

### Render

Set via dashboard > Environment tab:

| Key | Value |
|-----|-------|
| `ANTHROPIC_AUTH_TOKEN` | `your-token` |
| `ANTHROPIC_BASE_URL` | `https://api.z.ai/api/anthropic` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `glm-4.7` |

## Migration Patterns

### From API_KEY to AUTH_TOKEN

**Before**:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx
```

**After**:

```bash
ANTHROPIC_AUTH_TOKEN=your-zai-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
```

### Fallback Pattern (Best Practice)

Support both during migration:

```typescript
const apiKey = process.env.ANTHROPIC_AUTH_TOKEN || process.env.ANTHROPIC_API_KEY
const baseURL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com'

const anthropic = new Anthropic({
  baseURL,
  apiKey
})
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Variables undefined | Missing prefix | Use `NEXT_PUBLIC_` for Next.js browser code |
| CORS error | Exposing secrets in browser | Move API calls to backend or API route |
| 401 Unauthorized | Invalid token | Verify z.ai token is correct |
| Model not found | Missing model override | Add `ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7` |
| Variables not loading | File not loaded | Restart dev server after changing .env |

## Security Best Practices

1. **Never commit .env files** - Add to `.gitignore`
2. **Use platform env vars** for deployment (Netlify, Vercel, Render)
3. **Rotate tokens regularly** - Set expiration dates
4. **Use fallback pattern** - Support both API_KEY and AUTH_TOKEN during migration
5. **Test in staging first** - Verify proxy works before production deployment

## .gitignore Patterns

```
# Environment files
.env
.env.local
.env.production
.env.*.local

# Backup files
*.backup.*
*.bak
```

## Environment-Specific Files

| File | When to Use | Loaded By |
|------|-------------|-----------|
| `.env` | Shared variables | All frameworks |
| `.env.local` | Local overrides | Next.js, Vite |
| `.env.development` | Development only | Next.js |
| `.env.production` | Production only | Next.js |
| `.env.test` | Testing only | Next.js |
