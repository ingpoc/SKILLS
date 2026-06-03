# Prompt Versioning Patterns

## Why Version Prompts

From [Kubiya - Deterministic AI Architecture](https://www.kubiya.ai/blog/deterministic-ai-architecture):

> "Non-versioned prompts cause drift. Treat prompts as versioned source code, not dynamic input."

### Problems with Unversioned Prompts

| Problem | Symptom | Impact |
|---------|---------|--------|
| Drift | Prompt changes over time | Different behavior per session |
| No audit | Can't reproduce past behavior | Debugging impossible |
| No rollback | Can't undo bad changes | Stuck with regressions |
| No testing | Changes untested | Silent failures |

## Versioning Schema

### File Header

```markdown
<!-- Prompt: orchestrator -->
<!-- Version: 1.2.0 -->
<!-- SHA256: a3f2b8c9d4e5f6a7b8c9d0e1f2a3b4c5... -->
<!-- Last validated: 2025-12-28 -->
<!-- Compatibility: Claude Code 2.0.70+ -->

# Orchestrator

You are the main orchestrator...
```

### Version Format

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (different behavior)
MINOR: New capabilities (backward compatible)
PATCH: Bug fixes, clarifications
```

### Examples

| Change | Version Bump |
|--------|--------------|
| Complete rewrite | 1.0.0 → 2.0.0 |
| Add new state | 1.0.0 → 1.1.0 |
| Fix typo | 1.0.0 → 1.0.1 |
| Clarify instruction | 1.0.0 → 1.0.1 |
| Remove capability | 1.0.0 → 2.0.0 |

## Hash Validation

### Generate Hash

```bash
#!/bin/bash
# scripts/hash-prompt.sh

PROMPT_FILE=$1

# Strip version header, hash content only
CONTENT=$(grep -v "^<!--" "$PROMPT_FILE" | grep -v "^$")
HASH=$(echo "$CONTENT" | sha256sum | cut -d' ' -f1)

echo "SHA256: ${HASH:0:32}..."
```

### Validate Hash

```python
#!/usr/bin/env python3
# scripts/validate-prompt.py

import hashlib
import re
import sys

def validate_prompt(filepath: str) -> bool:
    with open(filepath) as f:
        content = f.read()

    # Extract declared hash
    match = re.search(r'SHA256: ([a-f0-9]+)', content)
    if not match:
        print(f"WARN: No hash declared in {filepath}")
        return True  # No hash = no validation

    declared = match.group(1)

    # Calculate actual hash (strip headers)
    lines = content.split('\n')
    body = '\n'.join(l for l in lines if not l.startswith('<!--'))
    actual = hashlib.sha256(body.encode()).hexdigest()

    if actual.startswith(declared):
        print(f"PASS: Hash valid for {filepath}")
        return True
    else:
        print(f"FAIL: Hash mismatch in {filepath}")
        print(f"  Declared: {declared}")
        print(f"  Actual:   {actual[:32]}...")
        return False

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "PROMPT.md"
    exit(0 if validate_prompt(filepath) else 1)
```

## Prompt Directory Structure

```
.claude/prompts/
├── orchestrator.md      # v1.2.0
├── orchestrator.v1.1.0.md  # Previous version (archived)
├── orchestrator.v1.0.0.md  # Previous version (archived)
├── validation.log       # Hash validation results
└── CHANGELOG.md         # Version history
```

## Changelog Format

```markdown
# Prompt Changelog

## orchestrator.md

### 1.2.0 (2025-12-28)
- Added compression trigger at 80% context
- Changed state machine to single orchestrator pattern
- Removed subagent spawning

### 1.1.0 (2025-12-25)
- Added TEST state with verification
- Added retry logic (max 3 attempts)

### 1.0.0 (2025-12-20)
- Initial version
- Basic state machine: INIT → IMPLEMENT → COMPLETE
```

## Validation Hook

```python
#!/usr/bin/env python3
# .claude/hooks/validate-prompts.py
# SessionStart hook - validates all prompts before session

import os
import sys
import hashlib
import re
import json

PROMPTS_DIR = ".claude/prompts"

def validate_all():
    results = []

    for filename in os.listdir(PROMPTS_DIR):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(PROMPTS_DIR, filename)
        with open(filepath) as f:
            content = f.read()

        # Check for version
        version_match = re.search(r'Version: ([\d.]+)', content)
        if not version_match:
            results.append({
                "file": filename,
                "status": "warn",
                "message": "No version declared"
            })
            continue

        # Check for hash
        hash_match = re.search(r'SHA256: ([a-f0-9]+)', content)
        if hash_match:
            declared = hash_match.group(1)
            body = '\n'.join(l for l in content.split('\n') if not l.startswith('<!--'))
            actual = hashlib.sha256(body.encode()).hexdigest()

            if actual.startswith(declared):
                results.append({
                    "file": filename,
                    "version": version_match.group(1),
                    "status": "pass"
                })
            else:
                results.append({
                    "file": filename,
                    "status": "fail",
                    "message": "Hash mismatch"
                })
        else:
            results.append({
                "file": filename,
                "version": version_match.group(1),
                "status": "pass",
                "message": "No hash (not validated)"
            })

    # Output results
    failed = [r for r in results if r["status"] == "fail"]
    if failed:
        print(json.dumps({"prompts_valid": False, "results": results}))
        sys.exit(2)

    print(json.dumps({"prompts_valid": True, "results": results}))
    sys.exit(0)

if __name__ == "__main__":
    validate_all()
```

## Rollback Pattern

```bash
#!/bin/bash
# scripts/rollback-prompt.sh

PROMPT=$1  # e.g., "orchestrator"
VERSION=$2 # e.g., "1.1.0"

PROMPTS_DIR=".claude/prompts"
CURRENT="$PROMPTS_DIR/$PROMPT.md"
BACKUP="$PROMPTS_DIR/$PROMPT.$(date +%Y%m%d%H%M%S).bak"
TARGET="$PROMPTS_DIR/$PROMPT.v$VERSION.md"

if [ ! -f "$TARGET" ]; then
    echo "FAIL: Version $VERSION not found for $PROMPT"
    exit 1
fi

# Backup current
cp "$CURRENT" "$BACKUP"

# Restore target version
cp "$TARGET" "$CURRENT"

echo "Rolled back $PROMPT to v$VERSION"
echo "Backup saved to $BACKUP"
```

## Testing Prompts

### Prompt Test Suite

```python
#!/usr/bin/env python3
# tests/test_prompts.py

import pytest
import os
import re

PROMPTS_DIR = ".claude/prompts"

def get_prompt_files():
    return [f for f in os.listdir(PROMPTS_DIR) if f.endswith('.md')]

@pytest.mark.parametrize("filename", get_prompt_files())
def test_prompt_has_version(filename):
    """Each prompt should declare version"""
    with open(os.path.join(PROMPTS_DIR, filename)) as f:
        content = f.read()
    assert re.search(r'Version: \d+\.\d+\.\d+', content), \
        f"{filename} missing version"

@pytest.mark.parametrize("filename", get_prompt_files())
def test_prompt_has_purpose(filename):
    """Each prompt should have clear purpose"""
    with open(os.path.join(PROMPTS_DIR, filename)) as f:
        content = f.read()
    assert "## Purpose" in content or "You are" in content[:500], \
        f"{filename} missing purpose statement"

@pytest.mark.parametrize("filename", get_prompt_files())
def test_prompt_not_too_long(filename):
    """Prompts should be concise"""
    with open(os.path.join(PROMPTS_DIR, filename)) as f:
        content = f.read()
    lines = len(content.split('\n'))
    assert lines < 200, f"{filename} too long ({lines} lines)"
```

## Best Practices

| Practice | Why |
|----------|-----|
| Version all prompts | Reproducibility |
| Hash critical prompts | Detect tampering/drift |
| Keep archived versions | Enable rollback |
| Changelog per prompt | Track evolution |
| Test after changes | Catch regressions |
| Validate on session start | Early detection |
