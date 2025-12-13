# Full-Stack Debugger Skill

A comprehensive debugging skill for systematically resolving full-stack application issues that span UI, backend, and database layers.

## Quick Start

### When to Use This Skill

Use this skill when you observe:

- **UI Errors**: Dashboard buttons failing, error messages in UI, status showing errors
- **Backend Failures**: Task execution failures, import errors, service initialization failures
- **Database Issues**: Data showing wrong status, missing records, failed transactions
- **API Problems**: Endpoints returning errors, unexpected responses, validation failures
- **Cascading Failures**: Multiple components failing simultaneously

### How to Invoke This Skill

```
@full-stack-debugger Debug [issue description]
```

Example:
```
@full-stack-debugger Debug AI Analysis Scheduler shows "0 done" but "4 failed"
```

## What This Skill Does

The Full-Stack Debugger implements a proven 6-phase debugging workflow:

1. **Detection** - Identify errors from UI, backend logs, and database state
2. **Analysis** - Read code, logs, and payloads to find root causes
3. **Fix** - Apply code fixes one issue at a time
4. **Restart** - Clean server restart with cache clearing
5. **Verification** - Validate fix through health checks, browser tests, and logs
6. **Iteration** - Repeat until all issues are resolved

## Debugging Workflow Overview

### Phase 1: Detection (Find What's Broken)

The skill checks three layers simultaneously:

**Browser UI**:
- Navigate to affected page
- Check for error messages and disabled functionality
- Read console errors (F12 → Console)
- Note specific UI state

**Backend Logs**:
- Query error logs: `tail -200 /path/to/logs/errors.log`
- Search error patterns: `grep "error_pattern"`
- Track error timestamps and stack traces
- Identify repeated failures (systemic issue)

**Database State**:
- Query tables directly: `sqlite3 state/robo_trader.db`
- Check task status, failed records, error states
- Note affected records and their states

### Phase 2: Analysis (Find Why It's Broken)

The skill reads code systematically:

**Code Analysis**:
- Read error file/module from error message
- Check imports: Is `Optional` imported? Is class name correct?
- Look for syntax errors: Unmatched quotes, unclosed parentheses
- Check function signatures: Match payload to expected parameters
- Reference common patterns from `references/common_errors.md`

**Payload Analysis**:
- Find what API sends to task handler
- Read task handler code for expected fields
- Compare actual vs expected payload structure
- Identify missing required fields

### Phase 3: Fix (Make One Change at a Time)

The skill applies fixes methodically:

**One Issue Per Iteration**:
- Fix only ONE problem at a time
- Don't cascade fixes or change multiple things
- Use fix templates from `references/fix_templates.md`
- Verify each fix is syntactically correct

**Common Fix Patterns**:
- Missing imports: Add to import statement
- Wrong class names: Update import and instantiation
- Missing docstring quotes: Add opening `"""`
- Wrong payload fields: Add missing required fields
- Syntax errors: Fix quotes, parentheses, brackets

### Phase 4: Restart (Clean Server Restart)

The skill restarts the backend with proper cleanup:

```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Clear Python bytecode cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Restart backend
sleep 3 && python -m src.main --command web

# Wait for startup
sleep 10

# Verify health
curl -m 5 http://localhost:8000/api/health
```

### Phase 5: Verification (Confirm It Works)

The skill verifies the fix through multiple checks:

**Health Check**:
- Call `/api/health` endpoint
- Verify `"status": "healthy"`
- If still failing, check logs for new errors

**Browser Verification**:
- Navigate to affected page in browser
- Trigger the action that previously failed
- Verify error is gone
- Check console for new errors

**Database Verification**:
- Query affected records/tasks
- Verify status changed from failed to success
- Check metrics updated (e.g., "1 done" instead of "0 done")

**Log Verification**:
- Check recent logs for same error
- Verify no new errors appeared
- Look for success messages

### Phase 6: Iteration (Repeat Until Fixed)

The skill continues the cycle:

1. **Check logs for remaining errors**
2. **If more errors exist**:
   - Return to Phase 2 (Analysis)
   - Fix next issue (Phase 3)
   - Restart (Phase 4)
   - Verify (Phase 5)
3. **Stop when all issues fixed**:
   - All schedulers show completed execution counts
   - UI shows no error states
   - Logs show no error patterns
   - Tasks show success status

## Reference Files

### common_errors.md

Quick reference for recognizing common Python and application errors:

- **Syntax Errors**: Unterminated strings, missing quotes
- **Import Errors**: Missing imports, wrong class names
- **Attribute/Key Errors**: Dictionary key not found, missing attributes
- **Type Errors**: Wrong argument types, function signature mismatches
- **Payload Errors**: Missing required fields, wrong structure

**Use this** when you see an error message and need to quickly identify the root cause.

### fix_templates.md

Ready-to-use fix patterns for common problems:

**Templates include**:
1. Missing Import - Add to import statement
2. Wrong Class Name - Update import and instantiation
3. Missing Docstring Quotes - Add opening `"""`
4. Unterminated String - Add closing quote
5. Missing Payload Field - Add to dictionary
6. Wrong Function Arguments - Provide all required args
7. Database Lock - Use ConfigurationState locked methods
8. Missing Module - Restore from .backup file
9. Health Check - Verify backend recovery
10. Browser Verification - Test from UI

**Use this** to quickly apply proven fixes for common errors. Copy, paste, and adapt to your situation.

## Key Principles

1. **One Issue at a Time** - Fix one problem per iteration to prevent cascading failures
2. **Verify Immediately** - Always restart and verify after each fix
3. **Multi-Layer Detection** - Check UI, logs, and database for clues
4. **Iterative Refinement** - Continue until all issues resolved
5. **Clean Restart** - Always kill + cache clear + restart for fresh state
6. **Browser Verification** - Test in actual UI, not just logs

## Example Debugging Session

### Scenario: AI Analysis Scheduler shows "0 done" but "4 failed"

**Phase 1: Detection**
1. Browser: Navigate to System Health dashboard
2. Observe: "AI Analysis Scheduler" showing "0 done, 4 failed"
3. Logs: `tail -50 logs/errors.log` shows `portfolio_intelligence_analyzer.py` missing
4. Database: Query `execution_history` table - all tasks have `status="failed"`

**Phase 2: Analysis**
1. Error message indicates missing file: `portfolio_intelligence_analyzer.py`
2. Check directory: File is missing, but `portfolio_intelligence_analyzer.py.backup` exists
3. Likely cause: File was deleted or not restored properly

**Phase 3: Fix**
1. Use Template 8: Missing Module/File Initialization
2. Copy backup: `cp portfolio_intelligence_analyzer.py.backup portfolio_intelligence_analyzer.py`
3. Verify syntax: Check file is valid Python (can parse)

**Phase 4: Restart**
1. Kill backend: `lsof -ti:8000 | xargs kill -9`
2. Clear cache: `find . -type d -name "__pycache__" -exec rm -rf {} +`
3. Restart: `python -m src.main --command web`
4. Wait 10 seconds for startup

**Phase 5: Verification**
1. Health check: `curl -m 5 http://localhost:8000/api/health` → `"status":"healthy"`
2. Browser: Reload System Health dashboard
3. Trigger: Click "Execute" on AI Analysis Scheduler
4. Check: "0 done" → "1 done" (metrics updated)
5. Logs: `tail` shows no errors related to analyzer

**Phase 6: Iteration**
1. Trigger again: Click "Execute" on Portfolio Analysis Scheduler
2. Observe: Shows "1 done" successfully
3. All schedulers: Check all are now functional
4. Complete: All issues resolved ✅

## Troubleshooting

### "I followed all phases but issue persists"

1. **Check you killed the process correctly**:
   - `ps aux | grep python` to see if process still running
   - `lsof -i :8000` to check port 8000

2. **Check logs for new errors**:
   - `tail -100 logs/errors.log` after each restart
   - Look for different error than before (indicates progress)

3. **Verify changes actually saved**:
   - Read back the file you edited
   - Check syntax matches expected pattern
   - Compare to fix templates

4. **Check for cascading failures**:
   - Is this a new error or same issue manifesting differently?
   - Read error message carefully for actual root cause
   - May need multiple iterations to resolve

### "Restart seems to work but error returns"

This typically indicates:
- The fix was partial (only fixed symptom, not cause)
- Multiple issues (fixed one but another causes same symptom)
- Stale Python bytecode cache

**Solution**:
1. Kill backend again
2. Clear cache: `find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null`
3. Restart fresh
4. Check logs immediately after start for any new errors

## Tips for Effective Debugging

1. **Read error messages completely** - Stack traces tell you exactly what's wrong
2. **Check timestamps** - Multiple errors at same time indicate batch failure
3. **Search code before guessing** - Find the actual code, don't assume
4. **Verify assumptions** - Read what the code actually does, not what you think
5. **Test immediately** - Don't batch fixes, verify each one works
6. **Keep logs open** - Watch logs while testing to catch new errors

## Files Included

```
full-stack-debugger/
├── SKILL.md                 # Complete skill workflow and instructions
├── references/
│   ├── common_errors.md     # Common error patterns reference
│   └── fix_templates.md     # Ready-to-use fix templates
└── README.md                # This file
```

## When to Consult Architecture Experts

If after following all 6 phases you still have issues, consult architecture patterns:

- **Architecture Questions**: Use `@feature-dev:code-architect` for pattern understanding
- **Design Decisions**: Seek validation before major refactors
- **Service Structure**: Clarify if service organization is correct

But always try the systematic debugging workflow first - it solves 95% of issues!

## Version

- **Created**: 2025-11-09
- **Status**: Production Ready
- **Tested Scenarios**: Scheduler failures, import errors, missing services, payload issues, database locks

## Support

For issues with this skill:
1. Verify you have latest version
2. Check that all 6 phases were completed
3. Review reference files for your specific error type
4. Consult project CLAUDE.md for architecture patterns
