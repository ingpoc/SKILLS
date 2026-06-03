# Framework-Specific GLM Setup

## Next.js

### App Router (Recommended)

**Directory structure**:

```
app/
├── api/
│   └── chat/
│       └── route.ts       # API route for server-side calls
├── page.tsx               # Your page
└── layout.tsx
lib/
└── anthropic-client.ts    # Client factory
```

**.env.local**:

```bash
NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN=your-token
NEXT_PUBLIC_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
NEXT_PUBLIC_ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.7
```

**lib/anthropic-client.ts**:

```typescript
import Anthropic from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  baseURL: process.env.NEXT_PUBLIC_ANTHROPIC_BASE_URL,
  apiKey: process.env.NEXT_PUBLIC_ANTHROPIC_AUTH_TOKEN
})
```

**app/api/chat/route.ts**:

```typescript
import { anthropic } from '@/lib/anthropic-client'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const { message } = await request.json()

  const response = await anthropic.messages.create({
    model: 'glm-4.7',
    max_tokens: 1024,
    messages: [{ role: 'user', content: message }]
  })

  return NextResponse.json(response)
}
```

### Pages Router

**pages/api/chat.ts**:

```typescript
import type { NextApiRequest, NextApiResponse } from 'next'
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  baseURL: process.env.ANTHROPIC_BASE_URL,
  apiKey: process.env.ANTHROPIC_AUTH_TOKEN
})

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { message } = req.body

  const response = await anthropic.messages.create({
    model: 'glm-4.7',
    max_tokens: 1024,
    messages: [{ role: 'user', content: message }]
  })

  res.status(200).json(response)
}
```

## Vite (React/Vue/Svelte)

### React + Vite

**.env**:

```bash
VITE_ANTHROPIC_AUTH_TOKEN=your-token
VITE_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**src/lib/anthropic-client.ts**:

```typescript
import Anthropic from '@anthropic-ai/sdk'

const baseURL = import.meta.env.VITE_ANTHROPIC_BASE_URL || 'https://api.anthropic.com'
const authToken = import.meta.env.VITE_ANTHROPIC_AUTH_TOKEN

export const anthropic = new Anthropic({
  baseURL,
  apiKey: authToken
})
```

**src/App.tsx**:

```typescript
import { anthropic } from './lib/anthropic-client'

function App() {
  const [response, setResponse] = useState('')

  const sendMessage = async () => {
    const result = await anthropic.messages.create({
      model: 'glm-4.7',
      max_tokens: 1024,
      messages: [{ role: 'user', content: 'Hello!' }]
    })
    setResponse(result.content[0].text)
  }

  return <button onClick={sendMessage}>Send</button>
}
```

### Vue + Vite

**.env**:

```bash
VITE_ANTHROPIC_AUTH_TOKEN=your-token
VITE_ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**src/lib/anthropic.ts**:

```typescript
import Anthropic from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  baseURL: import.meta.env.VITE_ANTHROPIC_BASE_URL,
  apiKey: import.meta.env.VITE_ANTHROPIC_AUTH_TOKEN
})
```

**src/components/Chat.vue**:

```vue
<script setup lang="ts">
import { anthropic } from '@/lib/anthropic'

const sendMessage = async () => {
  const response = await anthropic.messages.create({
    model: 'glm-4.7',
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello!' }]
  })
  console.log(response)
}
</script>
```

### SvelteKit

**.env**:

```bash
VITE_ANTHROPIC_AUTH_TOKEN=your-token
```

**src/lib/client.ts**:

```typescript
import Anthropic from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  baseURL: import.meta.env.VITE_ANTHROPIC_BASE_URL,
  apiKey: import.meta.env.VITE_ANTHROPIC_AUTH_TOKEN
})
```

## Python

### FastAPI

**requirements.txt**:

```
fastapi
uvicorn
anthropic
python-dotenv
```

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**main.py**:

```python
import os
from fastapi import FastAPI
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
anthropic = Anthropic(
    base_url=os.getenv('ANTHROPIC_BASE_URL'),
    api_key=os.getenv('ANTHROPIC_AUTH_TOKEN')
)

class Message(BaseModel):
    content: str

@app.post("/chat")
async def chat(message: Message):
    response = anthropic.messages.create(
        model="glm-4.7",
        max_tokens=1024,
        messages=[{"role": "user", "content": message.content}]
    )
    return response
```

### Flask

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**app.py**:

```python
import os
from flask import Flask, request, jsonify
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
anthropic = Anthropic(
    base_url=os.getenv('ANTHROPIC_BASE_URL'),
    api_key=os.getenv('ANTHROPIC_AUTH_TOKEN')
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    response = anthropic.messages.create(
        model="glm-4.7",
        max_tokens=1024,
        messages=[{"role": "user", "content": data['message']}]
    )
    return jsonify(response)
```

### Django

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**settings.py**:

```python
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC = {
    'base_url': os.getenv('ANTHROPIC_BASE_URL'),
    'api_key': os.getenv('ANTHROPIC_AUTH_TOKEN')
}
```

**views.py**:

```python
from django.http import JsonResponse
from anthropic import Anthropic
from django.conf import settings

def chat(request):
    client = Anthropic(**settings.ANTHROPIC)
    response = client.messages.create(
        model="glm-4.7",
        max_tokens=1024,
        messages=[{"role": "user", "content": request.POST.get('message')}]
    )
    return JsonResponse(response)
```

## Node.js

### Express

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**server.js**:

```javascript
require('dotenv').config()
import express from 'express'
import Anthropic from '@anthropic-ai/sdk'

const app = express()
app.use(express.json())

const anthropic = new Anthropic({
  baseURL: process.env.ANTHROPIC_BASE_URL,
  apiKey: process.env.ANTHROPIC_AUTH_TOKEN
})

app.post('/chat', async (req, res) => {
  const response = await anthropic.messages.create({
    model: 'glm-4.7',
    max_tokens: 1024,
    messages: [{ role: 'user', content: req.body.message }]
  })
  res.json(response)
})

app.listen(3000)
```

## Go

**.env**:

```bash
ANTHROPIC_AUTH_TOKEN=your-token
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

**main.go**:

```go
package main

import (
    "os"
    "github.com/anthropics/anthropic-go/v2"
    "github.com/gin-gonic/gin"
)

func main() {
    baseURL := os.Getenv("ANTHROPIC_BASE_URL")
    if baseURL == "" {
        baseURL = "https://api.anthropic.com"
    }

    client := anthropic.NewClient(
        anthropic.WithBaseURL(baseURL),
        anthropic.WithAPIKey(os.Getenv("ANTHROPIC_AUTH_TOKEN")),
    )

    r := gin.Default()
    r.POST("/chat", func(c *gin.Context) {
        var req struct {
            Message string `json:"message"`
        }
        c.BindJSON(&req)

        resp, err := client.Messages.Create(c, anthropic.MessageCreateParams{
            Model:     anthropic.F(anthropic.ModelClaude3_5Sonnet20241022),
            MaxTokens: anthropic.F(1024),
            Messages: anthropic.F([]anthropic.MessageParam{
                anthropic.NewUserMessage(anthropic.NewTextBlock(req.Message)),
            }),
        })

        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, resp)
    })

    r.Run(":3000")
}
```

## Common Patterns Across Frameworks

### Server-Side API Route Pattern

For frontend frameworks (Next.js, SvelteKit, etc.), use API routes to hide credentials:

1. Frontend → Internal API Route → Anthropic API
2. Credentials stored server-side only
3. CORS handled by internal API

### Direct Client-Side Pattern

For public apps (disclosure acceptable):

1. Frontend → Anthropic API directly
2. Credentials in `NEXT_PUBLIC_` / `VITE_` prefixed variables
3. Rate limiting and abuse prevention required

### Hybrid Pattern

Best of both:

1. Use public API for non-sensitive operations
2. Use server-side route for sensitive operations
3. Separate clients for each use case
