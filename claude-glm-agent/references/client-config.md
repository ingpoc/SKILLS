# Anthropic Client Configuration Patterns

## Client Factory Pattern

Best practice for creating Anthropic clients with environment-based configuration.

### TypeScript/JavaScript

#### Basic Factory

```typescript
// lib/anthropic-client.ts
import Anthropic from '@anthropic-ai/sdk'

const baseURL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com'
const authToken = process.env.ANTHROPIC_AUTH_TOKEN || process.env.ANTHROPIC_API_KEY

if (!authToken) {
  throw new Error('ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY is required')
}

export const anthropic = new Anthropic({
  baseURL,
  apiKey: authToken,
  defaultHeaders: {
    'anthropic-version': '2023-06-01'
  }
})

// Export config for debugging
export const config = { baseURL, hasToken: !!authToken }
```

#### Next.js App Router

```typescript
// lib/anthropic-client.ts
import Anthropic from '@anthropic-ai/sdk'

const getAnthropicClient = () => {
  const baseURL = process.env.NEXT_PUBLIC_ANTHROPIC_BASE_URL || 'https://api.anthropic.com'
  const authToken = process.env.NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN

  if (!authToken) {
    throw new Error('NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN is required')
  }

  return new Anthropic({
    baseURL,
    apiKey: authToken,
    defaultHeaders: {
      'anthropic-version': '2023-06-01'
    }
  })
}

export const anthropic = getAnthropicClient()
```

#### Next.js API Route (Server-Side)

```typescript
// app/api/chat/route.ts
import Anthropic from '@anthropic-ai/sdk'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  // Use server-side env vars (no NEXT_PUBLIC_ prefix)
  const baseURL = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com'
  const authToken = process.env.ANTHROPIC_AUTH_TOKEN

  if (!authToken) {
    return NextResponse.json({ error: 'Missing credentials' }, { status: 401 })
  }

  const anthropic = new Anthropic({
    baseURL,
    apiKey: authToken
  })

  // ... rest of handler
}
```

#### Vite (React/Vue/Svelte)

```typescript
// lib/anthropic-client.ts
import Anthropic from '@anthropic-ai/sdk'

const baseURL = import.meta.env.VITE_ANTHROPIC_BASE_URL || 'https://api.anthropic.com'
const authToken = import.meta.env.VITE_ANTHROPIC_AUTH_TOKEN

if (!authToken) {
  throw new Error('VITE_ANTHROPIC_AUTH_TOKEN is required')
}

export const anthropic = new Anthropic({
  baseURL,
  apiKey: authToken
})
```

### Python

#### FastAPI Factory

```python
# lib/anthropic_client.py
import os
from anthropic import Anthropic

def get_anthropic_client():
    base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')
    auth_token = os.getenv('ANTHROPIC_AUTH_TOKEN') or os.getenv('ANTHROPIC_API_KEY')

    if not auth_token:
        raise ValueError('ANTHROPIC_AUTH_TOKEN is required')

    return Anthropic(
        base_url=base_url,
        api_key=auth_token,
    )

# Singleton instance
anthropic = get_anthropic_client()
```

#### Flask Factory

```python
# extensions.py
from anthropic import Anthropic
from flask import current_app

def get_anthropic():
    base_url = current_app.config.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')
    auth_token = current_app.config.get('ANTHROPIC_AUTH_TOKEN')

    return Anthropic(
        base_url=base_url,
        api_key=auth_token,
    )

# app.py
from flask import Flask
from extensions import get_anthropic

app = Flask(__name__)
app.config.update({
    'ANTHROPIC_BASE_URL': os.getenv('ANTHROPIC_BASE_URL'),
    'ANTHROPIC_AUTH_TOKEN': os.getenv('ANTHROPIC_AUTH_TOKEN')
})
```

#### Django Settings

```python
# settings.py
import os
from anthropic import Anthropic

ANTHROPIC_CONFIG = {
    'base_url': os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com'),
    'api_key': os.getenv('ANTHROPIC_AUTH_TOKEN'),
}

# utils/anthropic.py
from django.conf import settings
from anthropic import Anthropic

def get_anthropic_client():
    return Anthropic(**settings.ANTHROPIC_CONFIG)
```

### Go

```go
// pkg/anthropic/client.go
package anthropic

import (
    "os"
    "github.com/anthropics/anthropic-go/v2"
)

var Client *anthropic.Client

func init() {
    baseURL := os.Getenv("ANTHROPIC_BASE_URL")
    if baseURL == "" {
        baseURL = "https://api.anthropic.com"
    }

    token := os.Getenv("ANTHROPIC_AUTH_TOKEN")
    if token == "" {
        token = os.Getenv("ANTHROPIC_API_KEY")
    }

    Client = anthropic.NewClient(
        anthropic.WithBaseURL(baseURL),
        anthropic.WithAPIKey(token),
    )
}
```

### Rust

```rust
// src/anthropic/client.rs
use anthropic::client::Client;
use std::env;

pub fn get_client() -> Result<Client, Box<dyn std::error::Error>> {
    let base_url = env::var("ANTHROPIC_BASE_URL")
        .unwrap_or_else(|_| "https://api.anthropic.com".to_string());

    let auth_token = env::var("ANTHROPIC_AUTH_TOKEN")
        .or_else(|_| env::var("ANTHROPIC_API_KEY"))?;

    Ok(Client::new(base_url, auth_token)?)
}

// Lazy static singleton
use once_cell::sync::Lazy;

pub static ANTHROPIC: Lazy<Client> = Lazy::new(|| {
    get_client().expect("Failed to create Anthropic client")
});
```

## Testing Patterns

### Mock Client for Tests

```typescript
// __tests__/mocks/anthropic.ts
import { vi } from 'vitest'

export const mockAnthropic = {
  messages: {
    create: vi.fn(),
    stream: vi.fn()
  }
}

vi.mock('@anthropic-ai/sdk', () => ({
  default: vi.fn(() => mockAnthropic)
}))
```

### Conditional Client

```typescript
// lib/anthropic-client.ts
import Anthropic from '@anthropic-ai/sdk'

const isTest = process.env.NODE_ENV === 'test'

export const anthropic = isTest
  ? null as any
  : new Anthropic({
      baseURL: process.env.ANTHROPIC_BASE_URL,
      apiKey: process.env.ANTHROPIC_AUTH_TOKEN
    })
```

## Debugging

### Enable Logging

```typescript
export const anthropic = new Anthropic({
  baseURL,
  apiKey: authToken,
  dangerouslyAllowBrowser: true, // Only for debugging!
  fetch: async (input, init) => {
    console.log('[Anthropic Request]', input, init)
    const response = await fetch(input, init)
    console.log('[Anthropic Response]', response.status)
    return response
  }
})
```

### Configuration Validator

```typescript
// lib/config-validator.ts
export function validateConfig() {
  const required = [
    'ANTHROPIC_AUTH_TOKEN'
  ]

  const optional = [
    'ANTHROPIC_BASE_URL',
    'ANTHROPIC_DEFAULT_SONNET_MODEL'
  ]

  const missing = required.filter(key => !process.env[key])

  if (missing.length > 0) {
    throw new Error(`Missing required env vars: ${missing.join(', ')}`)
  }

  console.log('✓ Anthropic config validated')
  console.log('  BASE_URL:', process.env.ANTHROPIC_BASE_URL || 'default')
  console.log('  Has token:', !!process.env.ANTHROPIC_AUTH_TOKEN)
}
```

## Error Handling

```typescript
// lib/anthropic-client.ts
import Anthropic, { APIError } from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  baseURL,
  apiKey: authToken,
  httpAgent: {
    maxRetries: 3,
    // Retry on 429 (rate limit) and 5xx
    statusCodesToRetry: [429, 500, 502, 503, 504]
  }
})

// Usage with error handling
try {
  const response = await anthropic.messages.create({...})
} catch (error) {
  if (error instanceof APIError) {
    console.error('Anthropic API error:', error.message)
    if (error.status === 401) {
      console.error('Check your ANTHROPIC_AUTH_TOKEN')
    }
  }
}
```

## Streaming Patterns

```typescript
// Streaming with proper cleanup
async function streamMessage(message: string) {
  const stream = await anthropic.messages.stream({
    model: 'glm-4.7',
    max_tokens: 1024,
    messages: [{ role: 'user', content: message }]
  })

  for await (const event of stream) {
    switch (event.type) {
      case 'text_delta':
        process.stdout.write(event.delta.text)
        break
      case 'error':
        console.error('Stream error:', event.error)
        break
    }
  }
}
```
