# Fix Templates

Ready-to-use fix patterns for common debugging scenarios. Copy, paste, and adapt to your specific situation.

## Import Error Fixes

### Template 1: Missing Import

**Problem**: `NameError: name 'Optional' is not defined`

**Pattern**: Type used but not imported from typing module

**Fix Template**:
```python
# BEFORE
from typing import Dict, List, Any

def function() -> Optional[Dict]:  # Optional not imported!
    pass

# AFTER
from typing import Dict, List, Any, Optional  # Add Optional

def function() -> Optional[Dict]:
    pass
```

**Steps**:
1. Find the line using undefined name
2. Look for import statement at top of file
3. Add missing name to import (alphabetically)
4. Save and restart server

**Checklist**:
- [ ] Undefined name added to import statement
- [ ] Other names in that import still work
- [ ] No syntax errors (proper comma placement)

---

### Template 2: Wrong Class Name Import

**Problem**: `ImportError: cannot import name 'DataGatherer' from 'src.services.portfolio_intelligence.data_gatherer'`

**Pattern**: Class name doesn't match what's actually defined in the module

**Fix Template**:
```python
# Find actual class name by reading the file:
# src/services/portfolio_intelligence/data_gatherer.py contains:
# class PortfolioDataGatherer:
#     def __init__(self, state_manager, config_state):

# BEFORE
from src.services.portfolio_intelligence.data_gatherer import DataGatherer
self.data_gatherer = DataGatherer(state_manager)

# AFTER
from src.services.portfolio_intelligence.data_gatherer import PortfolioDataGatherer
self.data_gatherer = PortfolioDataGatherer(state_manager, config_state)
```

**Steps**:
1. Read error: which module, which class?
2. Open the module file and search for `class ClassName:`
3. Copy exact class name from file
4. Update import statement
5. Update all instantiations to use correct class
6. Update constructor arguments to match `__init__` signature

**Checklist**:
- [ ] Read actual class definition in module file
- [ ] Copied exact class name (case-sensitive!)
- [ ] Updated import statement
- [ ] Updated all instantiations
- [ ] Constructor arguments match `__init__` parameters
- [ ] No syntax errors

---

## Syntax Error Fixes

### Template 3: Missing Triple Quotes on Docstring

**Problem**: `SyntaxError: unterminated triple-quoted string literal (detected at line 11) (__init__.py, line 7)`

**Pattern**: Docstring missing opening triple quotes

**Fix Template**:
```python
# BEFORE (Line 1 of file)
Module docstring without opening quotes

This is a multi-line docstring.
It explains the module purpose.
All components are modularized.
"""

# AFTER (Line 1 of file)
"""
Module docstring with opening quotes

This is a multi-line docstring.
It explains the module purpose.
All components are modularized.
"""
```

**Steps**:
1. Go to the line mentioned in error message
2. Look above and below for docstring text
3. Add opening `"""` before the docstring text
4. Ensure closing `"""` is present
5. Check indentation is correct

**Checklist**:
- [ ] Opening `"""` added on first line
- [ ] Content unchanged (between opening and closing quotes)
- [ ] Closing `"""` still present
- [ ] No extra blank lines before opening quotes
- [ ] Indentation matches rest of file

---

### Template 4: Unterminated String Literal

**Problem**: `SyntaxError: unterminated string literal (detected at line 15)`

**Pattern**: String missing closing quote

**Fix Template**:
```python
# BEFORE
text = "This string is missing the closing quote
another_line = "valid string"

# AFTER
text = "This string has the closing quote"
another_line = "valid string"
```

**Steps**:
1. Find the line with error
2. Look for opening quote: `"` or `'`
3. Find if closing quote exists: `"` or `'`
4. If missing, add closing quote
5. Watch for escaped quotes: `\"` inside string

**Checklist**:
- [ ] Opening quote exists: `"` or `'`
- [ ] Closing quote added: same type as opening
- [ ] No unescaped quotes in middle of string
- [ ] Multi-line strings use triple quotes: `"""`

---

## Payload & Configuration Fixes

### Template 5: Missing Payload Field

**Problem**: `KeyError: 'agent_name'` in task handler

**Pattern**: Task handler expects field that API doesn't provide

**Fix Template**:
```python
# Find what handler expects:
# In task_service.py:
# async def handle_recommendation_generation(task):
#     agent_name = task.payload['agent_name']  # REQUIRED
#     symbols = task.payload['symbols']        # REQUIRED

# BEFORE (in configuration.py)
payload = {
    "symbols": symbols,
    "manual_trigger": True
}
task = await task_service.create_task(
    queue_name=queue_name,
    task_type=task_type,
    payload=payload,
    priority=8
)

# AFTER
payload = {
    "symbols": symbols,
    "manual_trigger": True,
    "agent_name": "scan"  # Add missing required field
}
task = await task_service.create_task(
    queue_name=queue_name,
    task_type=task_type,
    payload=payload,
    priority=8
)
```

**Steps**:
1. Find task handler code for that task type
2. Identify all `task.payload['field_name']` accesses
3. Compare to fields provided in API endpoint
4. Add missing fields to payload dictionary
5. Use sensible defaults or required values

**Checklist**:
- [ ] Found task handler code
- [ ] Identified all required fields
- [ ] Added missing fields to payload
- [ ] Used appropriate default values
- [ ] Payload structure matches handler expectations

---

### Template 6: Wrong Function Arguments

**Problem**: `TypeError: function() takes 2 positional arguments but 3 were given`

**Pattern**: Function signature changed but caller wasn't updated

**Fix Template**:
```python
# Find function definition and count parameters:
# def __init__(self, state_manager, config_state):
#     # Expects: state_manager AND config_state

# BEFORE (missing config_state)
self.data_gatherer = PortfolioDataGatherer(state_manager)

# AFTER (provide all required arguments)
self.data_gatherer = PortfolioDataGatherer(state_manager, config_state)
```

**Steps**:
1. Find the function/method being called
2. Read its definition: `def function(param1, param2, param3):`
3. Count required parameters (before any defaults)
4. Count arguments being passed to function
5. Add missing arguments
6. Check argument types match parameter types

**Checklist**:
- [ ] Found function definition
- [ ] Counted required parameters (no defaults)
- [ ] Added all missing arguments
- [ ] Arguments in correct order
- [ ] Argument types match parameter types

---

## Database & State Fixes

### Template 7: Direct Database Access (LOCK CONTENTION)

**Problem**: `database is locked` errors during concurrent operations

**Pattern**: Web endpoint accessing database connection directly instead of using ConfigurationState locked methods

**Fix Template**:
```python
# BEFORE (causes database lock contention)
@router.get("/api/analysis")
async def get_analysis(request: Request, container: DependencyContainer = Depends(get_container)):
    database = await container.get("database")
    conn = database.connection
    cursor = await conn.execute("SELECT * FROM analysis_history")  # NO LOCK!
    return {"analysis": cursor.fetchall()}

# AFTER (uses ConfigurationState's internal locking)
@router.get("/api/analysis")
async def get_analysis(request: Request, container: DependencyContainer = Depends(get_container)):
    configuration_state = await container.get("configuration_state")
    # get_analysis_history() uses asyncio.Lock() internally
    analysis_data = await configuration_state.get_analysis_history()
    return {"analysis": analysis_data}
```

**Steps**:
1. Find web endpoint accessing `database.connection` directly
2. Identify what data is being retrieved
3. Find ConfigurationState method that retrieves same data
4. Replace direct access with ConfigurationState method call
5. Restart server to verify no lock errors

**Available ConfigurationState Methods**:
- `get_analysis_history()` - All analysis records
- `get_all_background_tasks_config()` - Background task config
- `get_all_ai_agents_config()` - AI agent configuration
- `store_analysis_history(symbol, timestamp, data)` - Save analysis
- `store_recommendation(symbol, rec_type, score, reasoning, analysis_type)` - Save recommendation
- `get_global_settings_config()` - Global settings

**Checklist**:
- [ ] Removed direct `database.connection` access
- [ ] Using ConfigurationState method instead
- [ ] Method signature matches expected parameters
- [ ] Server restarted after change
- [ ] No "database is locked" errors in logs

---

### Template 8: Missing Module/File Initialization

**Problem**: Service fails to load because module file is missing

**Pattern**: Expected module file doesn't exist (only `.backup` exists)

**Fix Template**:
```bash
# BEFORE (file missing)
# /src/services/portfolio_intelligence_analyzer.py - MISSING!
# /src/services/portfolio_intelligence_analyzer.py.backup - EXISTS

# AFTER (restore from backup)
cp /src/services/portfolio_intelligence_analyzer.py.backup \
   /src/services/portfolio_intelligence_analyzer.py

# Verify file exists
ls -la /src/services/portfolio_intelligence_analyzer.py
```

**Steps**:
1. Check error message for missing file name
2. Look in same directory for `.backup` version
3. Copy backup to original filename
4. Restart backend server
5. Check logs for next error

**Checklist**:
- [ ] Backup file exists in same directory
- [ ] Copied backup to correct location
- [ ] File name exactly matches import statement
- [ ] File has same permissions as other modules
- [ ] Server restarted
- [ ] New error (not missing file) appears in logs

---

## Testing & Verification Fixes

### Template 9: Verify API Health After Fix

**Problem**: Need to confirm backend recovered after fix

**Fix Template**:
```bash
# Step 1: Check if backend is running
curl -m 5 http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","timestamp":"2025-11-09T10:30:45.123Z"}

# If timeout or no response:
# Step 2: Kill backend and restart
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2
python -m src.main --command web

# Step 3: Wait for startup and verify again
sleep 10
curl -m 5 http://localhost:8000/api/health
```

**Checklist**:
- [ ] Backend responds to health check within 5 seconds
- [ ] Response contains `"status":"healthy"`
- [ ] No timeout errors
- [ ] Server logs show no errors

---

### Template 10: Browser Verification After Fix

**Problem**: Need to verify fix works from UI

**Fix Template**:

1. **Navigate to affected page**:
   - Open browser: `http://localhost:3000`
   - Go to System Health dashboard
   - Look for the scheduler that was failing

2. **Trigger the action that previously failed**:
   - Click "Execute" button on scheduler
   - Wait 5-10 seconds for task to complete

3. **Verify metrics updated**:
   - Reload page (F5)
   - Check "Done" count increased: "0 done" → "1 done"
   - Check "Failed" count didn't increase further
   - Check error message disappeared

4. **Check console for errors**:
   - Open DevTools (F12)
   - Go to Console tab
   - Verify no red error messages
   - Look for success messages

5. **Check backend logs**:
   - Terminal running backend: `tail -50 /path/to/logs/errors.log`
   - Verify no errors related to the task
   - Look for "completed" status messages

**Checklist**:
- [ ] Page loads without errors
- [ ] UI shows appropriate metrics update
- [ ] Console has no errors (F12 → Console tab)
- [ ] Backend logs show task completion
- [ ] Same action works 2+ times without failing again

---

## Quick Reference - When to Use Each Template

| Template | Use When |
|----------|----------|
| 1 - Missing Import | `NameError: name 'X' is not defined` |
| 2 - Wrong Class Name | `ImportError: cannot import name 'X'` |
| 3 - Missing Docstring Quotes | `SyntaxError: unterminated triple-quoted string` |
| 4 - Unterminated String | `SyntaxError: unterminated string literal` |
| 5 - Missing Payload Field | `KeyError: 'X'` in handler |
| 6 - Wrong Arguments | `TypeError: function() takes N args but M given` |
| 7 - Database Lock | `database is locked` or page freezes |
| 8 - Missing Module | `ModuleNotFoundError` or import fails |
| 9 - Verify Health | After backend change |
| 10 - Browser Verification | After frontend/API change |

---

## Error-to-Template Mapping

Keep this mapping handy during debugging:

```
NameError: name 'X' is not defined
  → Template 1 (Missing Import)

ImportError: cannot import name 'X'
  → Template 2 (Wrong Class Name)

SyntaxError: unterminated triple-quoted string literal
  → Template 3 (Missing Docstring Quotes)

SyntaxError: unterminated string literal
  → Template 4 (Unterminated String)

KeyError: 'X'
  → Template 5 (Missing Payload Field)

TypeError: function() takes N but M given
  → Template 6 (Wrong Arguments)

sqlite3.OperationalError: database is locked
  → Template 7 (Direct Database Access)

ModuleNotFoundError: No module named 'X'
  → Template 8 (Missing Module)

Pages freeze during operations
  → Template 7 (Direct Database Access)

API returns 500 error
  → Template 9 (Health check) then Template 10 (Browser test)
```

