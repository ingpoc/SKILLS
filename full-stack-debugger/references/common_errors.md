# Common Error Patterns

This reference guide helps quickly identify root causes of common Python and application errors that occur during development and testing.

## Python Syntax Errors

### Unterminated String/Quote Errors

**Pattern**: `unterminated string literal` or `unterminated triple-quoted string literal`

**Recognition**:
```
SyntaxError: unterminated string literal (detected at line 11) (__init__.py, line 7)
```

**Common Causes**:
- Missing closing quote on string: `text = "hello` (missing `"`)
- Missing opening triple quotes on docstring: `Multi-line docstring text here"""`
- Unescaped quotes within string: `text = "He said "hello""`

**Location**: Look at the line mentioned in error message and preceding lines for unclosed quotes

**Example Fix**:
```python
# BEFORE
"""
Module docstring
without opening quotes
"""

# AFTER
"""
Module docstring
with proper opening quotes
"""
```

## Import Errors

### Name Not Defined

**Pattern**: `name 'X' is not defined`

**Recognition**:
```
NameError: name 'Optional' is not defined
NameError: name 'Dict' is not defined
```

**Common Causes**:
- Missing import statement: Using `Optional` without `from typing import Optional`
- Typo in imported name
- Import inside function/block that doesn't execute before usage

**Root Cause Analysis**:
1. Find the line using the undefined name
2. Search file for import of that name
3. If not found, add to imports
4. If found but still error, check indentation (import inside `if __name__ == "__main__"`)

**Example Fix**:
```python
# BEFORE
from typing import Dict, List, Any

def get_data() -> Optional[Dict]:  # Optional not imported!
    pass

# AFTER
from typing import Dict, List, Any, Optional

def get_data() -> Optional[Dict]:
    pass
```

### Cannot Import Name

**Pattern**: `cannot import name 'X' from 'Y'`

**Recognition**:
```
ImportError: cannot import name 'DataGatherer' from 'src.services.portfolio_intelligence.data_gatherer'
```

**Common Causes**:
- Class/function name doesn't exist in module
- Class was renamed but imports not updated
- Typo in class name
- Class is in different module than expected

**Root Cause Analysis**:
1. Find the module mentioned: `src.services.portfolio_intelligence.data_gatherer`
2. Read the file and search for the class name: `class DataGatherer`
3. If not found, search for similar class names (e.g., `PortfolioDataGatherer`)
4. Update import to match actual class name

**Example Fix**:
```python
# BEFORE
from src.services.portfolio_intelligence.data_gatherer import DataGatherer
self.data_gatherer = DataGatherer()

# AFTER (if actual class is PortfolioDataGatherer)
from src.services.portfolio_intelligence.data_gatherer import PortfolioDataGatherer
self.data_gatherer = PortfolioDataGatherer(config_state)
```

## Attribute & Key Errors

### Dictionary Key Not Found

**Pattern**: `KeyError: 'X'`

**Recognition**:
```
KeyError: 'agent_name'
KeyError: 'symbols'
```

**Common Causes**:
- Expected key not provided in dictionary
- Typo in key name
- Key name mismatch between caller and handler (different capitalization or naming)

**Root Cause Analysis**:
1. Find the code accessing the key: `payload['agent_name']`
2. Find where payload is created/passed
3. Verify key was included in the dictionary
4. Check for capitalization mismatches: `agent_name` vs `agentName` vs `agent-name`

**Example Fix**:
```python
# BEFORE
payload = {"symbols": symbols, "manual_trigger": True}
# Later code expects: payload['agent_name']

# AFTER
payload = {
    "symbols": symbols,
    "manual_trigger": True,
    "agent_name": "scan"  # Added missing key
}
```

### Object Attribute Not Found

**Pattern**: `AttributeError: 'dict' object has no attribute 'X'` or `AttributeError: 'X' object has no attribute 'Y'`

**Recognition**:
```
AttributeError: 'dict' object has no attribute 'symbol'
AttributeError: 'NoneType' object has no attribute 'get'
```

**Common Causes**:
- Trying to access dictionary as object with dot notation instead of bracket notation
- Object is `None` (not initialized)
- Wrong object type (expected class instance, got dict)
- Method/attribute doesn't exist in class

**Root Cause Analysis**:
1. Check if accessing dict with `obj.key` instead of `obj['key']`
2. Check if object might be `None` (check initialization, return values)
3. Verify object type matches expected type
4. Check class definition for the attribute/method

**Example Fix**:
```python
# BEFORE - Dict with dot notation
data = {"symbol": "AAPL"}
symbol = data.symbol  # AttributeError!

# AFTER - Dict with bracket notation
symbol = data["symbol"]

# OR if expecting object, initialize it
class StockData:
    def __init__(self, symbol):
        self.symbol = symbol

data = StockData("AAPL")
symbol = data.symbol  # Now correct!
```

## Type & Payload Errors

### Wrong Argument Type

**Pattern**: Error about function receiving wrong type (mismatched function signatures)

**Recognition**:
```
TypeError: function() takes 2 positional arguments but 3 were given
TypeError: descriptor '__init__' for 'Example' object doesn't apply to a 'NoneType' object
```

**Common Causes**:
- Function signature changed but callers not updated
- Missing required arguments
- Passing wrong number of arguments
- Class constructor expects different parameters

**Root Cause Analysis**:
1. Find the function being called
2. Read its signature: `def function(param1, param2):`
3. Find where it's called
4. Count arguments being passed
5. Compare to expected parameters

**Example Fix**:
```python
# Function definition
def create_gatherer(state_manager, config_state):
    pass

# BEFORE - Missing config_state argument
self.data_gatherer = DataGatherer(state_manager)

# AFTER - Provide both required arguments
self.data_gatherer = DataGatherer(state_manager, config_state)
```

### Missing Required Fields in Payload

**Pattern**: Handler/service expects field not provided in task payload

**Recognition**:
```
KeyError: 'agent_name'  # In task handler processing
```

**Common Causes**:
- Task creation doesn't include all required fields
- Payload structure changed but callers not updated
- Different payloads for different task types not documented

**Root Cause Analysis**:
1. Find task handler: `handle_recommendation_generation(task)`
2. Read code to identify required fields: `task.payload['agent_name']`
3. Find task creation code
4. Add missing fields to payload

**Example Fix**:
```python
# Handler expects:
payload['agent_name']  # Required
payload['symbols']     # Required

# BEFORE - Missing agent_name
task = await task_service.create_task(
    queue_name=QueueName.AI_ANALYSIS,
    task_type=TaskType.RECOMMENDATION_GENERATION,
    payload={"symbols": ["AAPL"]}
)

# AFTER - Include all required fields
task = await task_service.create_task(
    queue_name=QueueName.AI_ANALYSIS,
    task_type=TaskType.RECOMMENDATION_GENERATION,
    payload={
        "symbols": ["AAPL"],
        "agent_name": "scan"  # Added
    }
)
```

## Recognition Quick Reference

| Error Message | Look For | Common Cause |
|---|---|---|
| `unterminated string literal` | Unclosed quotes | Missing opening/closing quote or triple quotes |
| `name 'X' is not defined` | Import statement | Missing `from Y import X` |
| `cannot import name 'X'` | Class definition in module | Wrong class name, class was renamed |
| `KeyError: 'X'` | Dictionary creation | Missing key in payload/config dictionary |
| `AttributeError: 'dict'` | Dot vs bracket notation | Using `dict.key` instead of `dict['key']` |
| `TypeError: takes N args` | Function signature | Wrong number of arguments provided |

## Debugging Checklist

When encountering an error:

1. ✅ Read the full error message (traceback often shows the real problem)
2. ✅ Find the file and line mentioned in error
3. ✅ Check imports at top of file
4. ✅ Verify object/dict access syntax (dot vs bracket)
5. ✅ Count function arguments vs parameters
6. ✅ Check for None/uninitialized values
7. ✅ Search for where variable is defined/assigned
8. ✅ Look for recent changes that might have broken compatibility

