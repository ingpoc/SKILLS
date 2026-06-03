# Tool Search & Lazy Loading Patterns

**When to use:** Servers with 20+ tools where tool definitions exceed 10K tokens

## Problem: Context Pollution

### Without Tool Search

| Setup | Token Cost | % of 200K Context |
|-------|------------|-------------------|
| 7 MCP servers (67 tools) | 67,300 tokens | 33.7% |
| 12 MCP servers | 82,000 tokens | 41% |

**Impact:**

- 40%+ context consumed before conversation starts
- Tool definitions crowd out actual work
- Large servers force users to disable tools
- No way to scale beyond 50-100 tools

### With Tool Search (defer_loading)

| Setup | Token Cost | Savings |
|-------|------------|---------|
| Same 7 servers | 10,095 tokens | 85% reduction |
| Same 12 servers | ~15,000 tokens | ~82% reduction |

**Benefits:**

- Tools load on-demand via semantic search
- 3-5 most relevant tools per search
- Automatic when definitions exceed 10K tokens
- No server-side changes required

---

## When to Use Tool Search

### Triggers (any of these)

- [ ] Server has 20+ tools
- [ ] Tool definitions exceed 10K tokens
- [ ] Multiple tool categories/domains
- [ ] Infrequent tool usage patterns
- [ ] Growing tool library (expecting expansion)
- [ ] Users need to disable tools due to context limits

### Indicators

| Scenario | Tool Search? |
|----------|--------------|
| 5 tools, single domain | No |
| 15 tools, tightly related | Maybe (plan for growth) |
| 25 tools, multiple domains | Yes |
| 50+ tools | Absolutely |
| Tool definitions >10K tokens | Automatic in Claude Code 2.1.7+ |

---

## How Tool Search Works

### Architecture

```
User Query
    ↓
Claude analyzes intent
    ↓
Tool Search (if defer_loading: true)
    ↓
Search covers: tool names, descriptions, arg names, arg descriptions
    ↓
Returns 3-5 most relevant tools
    ↓
Claude uses tools to accomplish task
```

### Search Mechanisms

**1. Regex Pattern Search** (`tool_search_tool_regex_20251119`)

- Direct pattern matching against tool metadata
- Fast, deterministic results
- Good for: known tool names, specific patterns

**2. BM25 Search** (`tool_search_tool_bm25_20251119`)

- Natural language semantic search
- Ranks by relevance score
- Good for: exploratory queries, intent-based discovery

### What Gets Searched

| Field | Searchable | Impact |
|-------|------------|--------|
| Tool name | ✓ | High (exact matches prioritized) |
| Tool description | ✓ | High (semantic keywords) |
| Argument names | ✓ | Medium (parameter discovery) |
| Argument descriptions | ✓ | Medium (usage context) |
| Annotations | ✗ | Not searched |
| Return types | ✗ | Not searched |

---

## Implementation: Server Side

### No Changes Required

**Key insight:** Tool search is a **client-side feature**. Servers remain unchanged.

```python
# Your existing server code works as-is
@mcp.tool()
async def slack_send_message(channel: str, text: str) -> str:
    """Send a message to a Slack channel"""
    # Implementation unchanged
```

**What happens:**

- Server exposes tools normally via `tools/list`
- Client decides which tools to defer
- Search happens client-side when tools are needed
- Tools load on-demand, not upfront

### But: Optimize for Discoverability

While tool search works automatically, make tools easy to discover:

**Pattern:**

```python
@mcp.tool(
    name="service_domain_action_resource",
    description="Clear purpose with semantic keywords for search"
)
async def tool_function(
    descriptive_param_name: str = Field(
        description="Searchable param description with context"
    )
) -> str:
    pass
```

---

## Implementation: Client Side

### Claude Code 2.1.7+ (Automatic)

Tool search activates automatically when:

- Tool definitions exceed 10K tokens (5% of 200K context)
- OR: User explicitly configures `defer_loading`

**No configuration required** for automatic activation.

### Manual Configuration (Advanced)

**For Claude API or custom clients:**

```python
{
  "type": "mcp_toolset",
  "mcp_server_name": "your-server",
  "default_config": {
    "defer_loading": True  # Defer all tools by default
  },
  "configs": {
    # Override for frequently used tools
    "service_health_check": {"defer_loading": False},
    "service_list_resources": {"defer_loading": False}
  }
}
```

**Keep 3-5 frequently used tools as non-deferred** (health checks, list operations, etc.)

### API Requirements

```python
# Required beta header for tool search
headers = {
    "anthropic-beta": "advanced-tool-use-2025-11-20"
}
```

---

## Tool Naming for Discoverability

### Pattern: `{service}_{domain}_{action}_{resource}`

**Examples:**

| Good | Why |
|------|-----|
| `slack_messages_send` | Clear hierarchy, searchable parts |
| `slack_channels_list` | Consistent prefix enables category search |
| `slack_users_search` | Action verb clear, resource explicit |
| `github_issues_create` | Service+domain grouped |
| `github_pulls_review_submit` | Multi-level hierarchy |

| Bad | Why |
|-----|-----|
| `send_message` | No service context |
| `slackMsg` | Abbreviation, not searchable |
| `do_slack_thing` | Vague action |
| `tool_42` | No semantic meaning |

### Naming Strategy

**For small servers (5-10 tools):**

- Simple descriptive names fine
- Example: `create_event`, `list_users`

**For medium servers (10-20 tools):**

- Add domain prefix
- Example: `calendar_create_event`, `user_list_all`

**For large servers (20+ tools):**

- Full hierarchy with service prefix
- Example: `google_calendar_events_create`, `google_contacts_users_list`
- **Critical:** Consistent prefixes enable category discovery

### Domain Grouping

```python
# Slack server with multiple domains
slack_messages_send      # Messages domain
slack_messages_list
slack_messages_delete
slack_channels_create    # Channels domain
slack_channels_list
slack_channels_archive
slack_users_search       # Users domain
slack_users_info
slack_users_presence
```

**Search query:** "slack messages" → finds all message tools
**Search query:** "slack users" → finds all user tools

---

## Description Writing for Search

### Formula: Purpose + Keywords + Use Cases

**Structure:**

1. **First sentence:** Clear purpose statement
2. **Keywords:** Common synonyms and related terms
3. **Use cases:** When/why to use this tool

**Pattern:**

```python
description = (
    "Send a message to a Slack channel or direct message (DM). "
    "Supports posting, replying, threading, and broadcasting. "
    "Use for notifications, alerts, team communication, or chatbot responses."
)
```

### Examples

**Good:**

```python
@mcp.tool(
    description=(
        "Search GitHub repositories by name, description, or topic. "
        "Supports filtering by language, stars, forks, and date. "
        "Use for finding projects, discovering libraries, or researching codebases."
    )
)
async def github_repos_search(query: str): pass
```

**Why it works:**

- ✓ Clear purpose: "Search GitHub repositories"
- ✓ Keywords: "name, description, topic, language, stars, forks"
- ✓ Use cases: "finding projects, discovering libraries, researching"
- ✓ Searchable synonyms: search/find/discover

**Bad:**

```python
@mcp.tool(description="Searches stuff")
async def search(q: str): pass
```

**Why it fails:**

- ✗ Vague: "stuff" is not searchable
- ✗ No context: what gets searched?
- ✗ No keywords: missing semantic terms
- ✗ No use cases: when would you use this?

### Keyword Strategy

**Include common synonyms:**

| Canonical | Synonyms to Include |
|-----------|---------------------|
| send | post, publish, broadcast, transmit |
| list | get, fetch, retrieve, query, find |
| delete | remove, archive, destroy |
| create | add, new, make, generate |
| update | edit, modify, change, revise |
| search | find, query, lookup, discover |

**Example:**

```python
description = (
    "Create a new GitHub issue (bug report, feature request, or task). "
    "Supports labels, assignees, milestones, and markdown formatting."
)
# Includes: create, new, add, make (implied)
# Keywords: bug, feature, task, labels, assignees
```

---

## Argument Naming for Search

### Pattern: Descriptive, Not Abbreviated

**Good:**

```python
async def send_message(
    channel_name_or_id: str,      # Clear what formats accepted
    message_text: str,              # "message_text" > "text"
    thread_timestamp: Optional[str], # Explains what the timestamp is for
    recipient_email: Optional[str]  # "recipient" > "to"
): pass
```

**Bad:**

```python
async def send_message(
    ch: str,       # Abbreviation
    txt: str,      # Abbreviation
    ts: str,       # Unclear meaning
    to: str        # Too generic
): pass
```

### Argument Descriptions (Searchable!)

```python
async def github_issues_create(
    repository: str = Field(
        description="Repository name in 'owner/repo' format (e.g., 'microsoft/vscode')"
    ),
    title: str = Field(
        description="Issue title (summary of bug, feature, or task)"
    ),
    body: str = Field(
        description="Issue description with details, steps to reproduce, or acceptance criteria. Supports markdown."
    ),
    labels: Optional[List[str]] = Field(
        description="Issue labels for categorization (e.g., 'bug', 'enhancement', 'documentation')"
    )
): pass
```

**Why searchable:**

- ✓ Context provided: "owner/repo format"
- ✓ Examples included: "microsoft/vscode"
- ✓ Keywords: "bug, feature, task, markdown, categorization"
- ✓ Explains purpose: "steps to reproduce, acceptance criteria"

---

## Tool Categorization

### Logical Grouping Strategy

**For servers with multiple domains:**

| Domain | Tool Prefix | Example |
|--------|-------------|---------|
| Messages | `slack_messages_*` | `slack_messages_send` |
| Channels | `slack_channels_*` | `slack_channels_create` |
| Users | `slack_users_*` | `slack_users_search` |
| Files | `slack_files_*` | `slack_files_upload` |

**Search behavior:**

- "slack messages" → Returns message tools
- "slack channels" → Returns channel tools
- "slack users" → Returns user tools

---

## Testing Tool Discoverability

### Verification Patterns

**1. Manual Search Simulation**

```python
# Ask yourself: what would users search for?
test_queries = [
    "send slack message",           # Natural language
    "slack notification",           # Use case
    "post to channel",              # Synonym
    "slack DM",                     # Abbreviation
    "slack messages",               # Domain
]

# For each query, check if your tool name/description matches
```

**2. Coverage Check**

```python
# Ensure each tool has:
checklist = [
    "Clear action verb in name",
    "Service/domain prefix",
    "Rich description with keywords",
    "Common synonyms included",
    "Use cases explained",
    "Descriptive argument names",
    "Argument descriptions with context"
]
```

**3. Search Query Examples**

| User Intent | Search Query | Should Find |
|-------------|--------------|-------------|
| Send notification | "send message slack" | `slack_messages_send` |
| List channels | "slack channels" | `slack_channels_list` |
| Find user | "search user slack" | `slack_users_search` |
| Upload file | "slack file upload" | `slack_files_upload` |
| Archive channel | "slack channel archive" | `slack_channels_archive` |

---

## Best Practices Summary

### Tool Naming

- [ ] Use `service_domain_action_resource` pattern for 20+ tools
- [ ] Consistent prefixes for tool grouping
- [ ] Clear action verbs (send, list, create, delete, update)
- [ ] No abbreviations (channel > ch, message > msg)

### Descriptions

- [ ] First sentence states clear purpose
- [ ] Include semantic keywords matching user intent
- [ ] Add common synonyms for actions
- [ ] Explain use cases (when/why to use)
- [ ] Keep under 200 characters for readability

### Arguments

- [ ] Descriptive parameter names (recipient_email > to)
- [ ] Detailed descriptions with context
- [ ] Include examples in descriptions
- [ ] Explain formats/constraints

### Organization

- [ ] Group related tools with consistent prefixes
- [ ] Keep 3-5 frequently used tools as non-deferred
- [ ] Document tool categories in server description

### Client Configuration

- [ ] Set `defer_loading: true` for large servers
- [ ] Override for frequently used tools
- [ ] Test with `anthropic-beta: advanced-tool-use-2025-11-20` header

---

## Examples

See implementation examples:

- [searchable-tools.py](../examples/searchable-tools.py) - Python with FastMCP
- [searchable-tools.ts](../examples/searchable-tools.ts) - TypeScript with MCP SDK

---

## Token Savings Calculator

| Server Size | Without Tool Search | With Tool Search | Savings |
|-------------|---------------------|------------------|---------|
| 10 tools | ~2,500 tokens | ~1,500 tokens | 40% |
| 25 tools | ~6,500 tokens | ~2,000 tokens | 69% |
| 50 tools | ~13,000 tokens | ~2,500 tokens | 81% |
| 100 tools | ~26,000 tokens | ~3,000 tokens | 88% |

**Formula:** Savings increase with server size. 50+ tools = 80%+ savings.

---

## Common Pitfalls

### 1. Vague Tool Names

```python
# Bad
@mcp.tool(name="process")
@mcp.tool(name="handle_request")
@mcp.tool(name="do_thing")

# Good
@mcp.tool(name="slack_messages_send")
@mcp.tool(name="github_issues_create")
@mcp.tool(name="calendar_events_update")
```

### 2. Missing Keywords in Descriptions

```python
# Bad
@mcp.tool(description="Does message stuff")

# Good
@mcp.tool(
    description=(
        "Send a message to a Slack channel or direct message (DM). "
        "Supports posting, replying, threading, and broadcasting."
    )
)
```

### 3. Abbreviated Argument Names

```python
# Bad
async def send(ch: str, txt: str, ts: str): pass

# Good
async def send_message(
    channel_name: str,
    message_text: str,
    thread_timestamp: Optional[str]
): pass
```

### 4. Not Grouping Related Tools

```python
# Bad (inconsistent naming)
send_slack_message
create_channel_slack
slack_user_search

# Good (consistent prefixes)
slack_messages_send
slack_channels_create
slack_users_search
```

### 5. Deferring Frequently Used Tools

```python
# Bad: defer health checks
"service_health_check": {"defer_loading": True}

# Good: keep essential tools non-deferred
"service_health_check": {"defer_loading": False}
"service_list_resources": {"defer_loading": False}
```

---

## Migration Guide

### Existing Server → Tool Search Ready

**Step 1: Audit Current Naming**

```bash
# List all tool names
grep -r "@mcp.tool" . | grep "name=" | sort
```

**Step 2: Identify Inconsistencies**

- Mixed naming patterns?
- Abbreviations?
- No domain prefixes?

**Step 3: Refactor Incrementally**

```python
# Before
@mcp.tool(name="send")
async def send(ch: str, txt: str): pass

# After (backward compatible via alias)
@mcp.tool(
    name="slack_messages_send",
    description="Send message to Slack channel or user (DM, post, reply, broadcast)"
)
async def slack_messages_send(
    channel_name: str = Field(description="Channel name or ID"),
    message_text: str = Field(description="Message content (supports markdown)")
): pass
```

**Step 4: Update Descriptions**

Add keywords, synonyms, use cases to all tool descriptions.

**Step 5: Test Discoverability**

Run through test queries (see "Testing Tool Discoverability" above).

**Step 6: Client Configuration**

```python
# .mcp.json or client config
{
  "mcp_server_name": "your-server",
  "default_config": {"defer_loading": true}
}
```

---

## Advanced: Search Optimization

### Keyword Density

**Target:** 5-10 semantic keywords per tool description

```python
# Low keyword density (2 keywords)
"Send a message"

# Optimal keyword density (8 keywords)
"Send a message to a Slack channel or direct message (DM). "
"Supports posting, replying, threading, and broadcasting."
# Keywords: send, message, slack, channel, DM, post, reply, broadcast
```

### Synonym Mapping

**Build a synonym map for your domain:**

```python
# E-commerce example
SYNONYMS = {
    "product": ["item", "goods", "merchandise", "sku"],
    "order": ["purchase", "transaction", "sale"],
    "customer": ["user", "buyer", "shopper", "client"],
    "search": ["find", "lookup", "query", "discover", "browse"]
}
```

**Incorporate into descriptions:**

```python
@mcp.tool(
    description=(
        "Search products by name, SKU, or description. "
        "Find items by category, price range, or availability. "
        "Use for browsing merchandise or discovering goods."
    )
)
```

### Natural Language Patterns

**Users search with natural language:**

| Pattern | Example Query | Tool Name Match |
|---------|---------------|-----------------|
| Action + Object | "send slack message" | `slack_messages_send` |
| Service + Action | "github create issue" | `github_issues_create` |
| Domain + Action | "email send" | `email_messages_send` |
| Use Case | "notify team" | `slack_messages_send` |

**Design names and descriptions to match these patterns.**

---

## References

- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [Tool Search GitHub Issue](https://github.com/anthropics/claude-agent-sdk-typescript/issues/124)
- [Claude Code Tool Search Article](https://jpcaparas.medium.com/claude-code-finally-gets-lazy-loading-for-mcp-tools-explained-39b613d1d5cc)
- [Tool Search API Documentation](/.skills/tools-search-tool.md)

---

## Quick Reference

### Checklist for New Tools

- [ ] Name: `service_domain_action_resource` pattern
- [ ] Description: Purpose + keywords + use cases (<200 chars)
- [ ] Arguments: Descriptive names + detailed descriptions
- [ ] Keywords: 5-10 semantic terms included
- [ ] Synonyms: Common action synonyms added
- [ ] Prefix: Consistent with related tools
- [ ] Testable: Works with natural language queries

### Token Impact

| Action | Token Cost | Savings |
|--------|------------|---------|
| Load all 50 tools upfront | 13,000 | 0% |
| Load 5 tools on-demand | 1,300 | 90% |
| Search for tools (3-5 results) | 2,500 | 81% |

### Configuration Template

```python
{
  "type": "mcp_toolset",
  "mcp_server_name": "your-server",
  "default_config": {"defer_loading": true},
  "configs": {
    "frequently_used_tool_1": {"defer_loading": false},
    "frequently_used_tool_2": {"defer_loading": false}
  }
}
```
