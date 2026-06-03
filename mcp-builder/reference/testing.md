# Testing MCP Servers

## Critical Warning

**MCP servers are long-running processes** that wait for requests over stdio/stdin or sse/http. Running them directly (e.g., `python server.py` or `node dist/index.js`) will cause your process to hang indefinitely.

## Safe Testing Methods

### 1. Use Evaluation Harness (Recommended)
The evaluation harness manages the server lifecycle for you. See [evaluation.md](./evaluation.md) for complete guide.

### 2. Run in tmux
```bash
# Start server in tmux
tmux new -s mcp-server
python server.py  # or node dist/index.js

# Detach: Ctrl+b then d
# Test with evaluation harness in main process
# Kill tmux session: tmux kill-session -t mcp-server
```

### 3. Use Timeout for Quick Checks
```bash
# Verify server starts without crashing
timeout 5s python server.py
# Exit code 124 = timeout (expected, server is running)
# Other exit codes = error in server startup
```

## Pre-Flight Checks

### Python
```bash
# Syntax validation
python -m py_compile your_server.py

# Check imports (review file for import errors)
grep -n "^import\|^from" your_server.py

# Run with timeout to verify startup
timeout 5s python your_server.py
```

### TypeScript
```bash
# Build and verify
npm run build

# Check dist output exists
ls -la dist/index.js

# Run with timeout to verify startup
timeout 5s node dist/index.js
```

## Manual Testing Workflow

1. **Syntax Check**: Verify code compiles/transpiles
2. **Start Server**: Run in tmux or background
3. **Test Tools**: Use evaluation harness or MCP inspector
4. **Monitor Logs**: Check stderr for errors
5. **Cleanup**: Kill server process when done

## Common Testing Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Process hangs | Server waiting for stdio | Use tmux or evaluation harness |
| Import errors | Missing dependencies | Check requirements.txt/package.json |
| Build fails | TypeScript errors | Fix type errors, run `npm run build` |
| Server crashes | Runtime errors | Check logs, add error handling |
| Tools not found | Registration issue | Verify `@mcp.tool()` or `registerTool()` |

## Integration Testing

Use the evaluation harness to test complete workflows:

```bash
# See evaluation.md for complete guide
python scripts/run_evaluation.py \
  --server-path ./your_server.py \
  --questions ./evaluations/questions.xml \
  --output ./results/
```

## Debugging Tips

1. **Add logging**: Use stderr for debug output (stdout is for MCP protocol)
2. **Test tools individually**: Create small test scripts for each tool
3. **Check schemas**: Validate Pydantic/Zod schemas separately
4. **Monitor resources**: Check CPU/memory usage during testing
5. **Test error paths**: Verify error messages are actionable

## Next Steps

After testing locally:
1. Create comprehensive evaluations ([evaluation.md](./evaluation.md))
2. Test with real LLM interactions
3. Iterate based on agent feedback
4. Deploy to production environment
