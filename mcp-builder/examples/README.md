# MCP Server Examples

Code templates demonstrating core MCP server patterns.

## Files

| File | Purpose | Key Concepts |
|------|---------|--------------|
| `basic-server.py` | Python server structure | Server init, tool registration, input validation, error handling |
| `basic-server.ts` | TypeScript server structure | Server setup, Zod schemas, tool registration, type safety |
| `tool-with-context.py` | Workflow consolidation | Multi-step workflows, context optimization, response formats |
| `error-handling.py` | Actionable error patterns | Educational errors, guidance messages, recovery suggestions |

## Usage

These are templates, not runnable servers. To use:

1. Copy relevant template
2. Add your API integration logic
3. Implement helper functions (fetch_from_api, format_as_json, etc.)
4. Follow language-specific guides in `../reference/`

## Pattern Index

### Server Initialization
- **Python**: See `basic-server.py` lines 1-13
- **TypeScript**: See `basic-server.ts` lines 1-20

### Input Validation
- **Python**: Pydantic models in `basic-server.py` lines 15-19
- **TypeScript**: Zod schemas in `basic-server.ts` lines 21-26

### Tool Registration
- **Python**: `@mcp.tool()` decorator in `basic-server.py` line 21
- **TypeScript**: `server.registerTool()` in `basic-server.ts` line 29

### Error Handling
- Educational errors: `error-handling.py` lines 18-28, 43-51
- Recovery suggestions: `error-handling.py` lines 63-73

### Workflow Consolidation
- Multi-step workflow: `tool-with-context.py` lines 57-75
- Response formats: `tool-with-context.py` lines 77-82

### Tool Annotations
- Complete example: `tool-with-context.py` lines 25-30

## Next Steps

After reviewing examples:
1. Read full implementation guides in `../reference/`
2. Study API documentation for your target service
3. Create implementation plan
4. Build and test your server

See `../SKILL.md` for complete development workflow.
