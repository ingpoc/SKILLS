#!/usr/bin/env python3
"""
Compile state-specific context from CLAUDE.md files.

Reduces ~500 lines to ~100 lines by extracting only relevant sections.

Usage:
    compile-context.py [state] [--force]

Output:
    Compiled context to stdout (for injection into session)
    Cache stored in ~/.claude/cache/
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


CACHE_DIR = Path.home() / ".claude" / "cache"
GLOBAL_CLAUDE = Path.home() / ".claude" / "CLAUDE.md"
PROJECT_CLAUDE = Path(".claude/CLAUDE.md")
ROOT_CLAUDE = Path("CLAUDE.md")


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of file contents."""
    if not path.exists():
        return ""
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def get_cache_key(state: str) -> str:
    """Generate cache key from state + file hashes."""
    hashes = [
        get_file_hash(GLOBAL_CLAUDE),
        get_file_hash(PROJECT_CLAUDE),
        get_file_hash(ROOT_CLAUDE),
    ]
    combined = f"{state}:{':'.join(hashes)}"
    return hashlib.md5(combined.encode()).hexdigest()[:12]


def load_cached(state: str) -> Optional[str]:
    """Load cached compiled context if valid."""
    cache_file = CACHE_DIR / f"context-{state}.md"
    hash_file = CACHE_DIR / f"context-{state}.hash"

    if not cache_file.exists() or not hash_file.exists():
        return None

    current_key = get_cache_key(state)
    cached_key = hash_file.read_text().strip()

    if current_key != cached_key:
        return None

    return cache_file.read_text()


def save_cache(state: str, content: str):
    """Save compiled context to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / f"context-{state}.md"
    hash_file = CACHE_DIR / f"context-{state}.hash"

    cache_file.write_text(content)
    hash_file.write_text(get_cache_key(state))


def extract_section(content: str, header: str) -> str:
    """Extract a markdown section by header."""
    pattern = rf"^##\s+{re.escape(header)}\s*\n(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_table(content: str, header: str) -> str:
    """Extract a table under a header."""
    section = extract_section(content, header)
    lines = section.split("\n")
    table_lines = [l for l in lines if l.strip().startswith("|") or l.strip().startswith("-")]
    return "\n".join(table_lines)


def compile_global_essentials() -> str:
    """Extract essential commands/rules from global CLAUDE.md."""
    if not GLOBAL_CLAUDE.exists():
        return ""

    content = GLOBAL_CLAUDE.read_text()

    # Extract only the most critical sections
    essentials = []

    # Token efficiency rules (always relevant)
    token_section = extract_section(content, "Token Scarcity")
    if token_section:
        essentials.append("## Token Budget\n" + token_section[:200])

    # Execution decision table
    exec_table = extract_table(content, "Execution Decision")
    if exec_table:
        essentials.append("## Execution\n" + exec_table)

    # Core rules (condensed)
    core_section = extract_section(content, "Core Rules")
    if core_section:
        # Just keep bullet points
        bullets = [l for l in core_section.split("\n") if l.strip().startswith("-")][:5]
        essentials.append("## Rules\n" + "\n".join(bullets))

    return "\n\n".join(essentials)


def compile_project_essentials() -> str:
    """Extract project-specific essentials."""
    essentials = []

    # From .claude/CLAUDE.md
    if PROJECT_CLAUDE.exists():
        content = PROJECT_CLAUDE.read_text()

        # Commands table
        cmd_table = extract_table(content, "Commands")
        if cmd_table:
            essentials.append("## Commands\n" + cmd_table)

        # Config paths
        config_table = extract_table(content, "Config")
        if config_table:
            essentials.append("## Config\n" + config_table)

    # From root CLAUDE.md
    if ROOT_CLAUDE.exists():
        content = ROOT_CLAUDE.read_text()
        # State → Skill mapping
        state_table = extract_table(content, "State → Skill Loading")
        if state_table:
            essentials.append("## State → Skill\n" + state_table)

    return "\n\n".join(essentials)


def compile_state_specific(state: str) -> str:
    """Extract state-specific context."""
    state_context = {
        "INIT": """## INIT State
- Run initialization skill
- Create feature-list.json
- Setup project hooks
- Check dependencies""",

        "IMPLEMENT": """## IMPLEMENT State
- Get current feature: `.claude/scripts/get-current-feature.sh`
- Use token-efficient MCP for data >50 items
- Query context-graph before implementing
- Commit with feature ID""",

        "TEST": """## TEST State
- Run tests with determinism (exit codes, not judgment)
- Verify no regressions
- Mark feature tested on pass""",

        "COMPLETE": """## COMPLETE State
- Store decision traces
- Extract patterns from session
- Update skill references""",

        "FIX_BROKEN": """## FIX_BROKEN State
- Health check failed
- Fix critical issues first
- Return to previous state after fix""",
    }

    return state_context.get(state, f"## {state} State\nNo specific guidance.")


def compile_current_feature() -> str:
    """Get current feature summary if available."""
    feature_file = Path(".claude/progress/feature-list.json")
    if not feature_file.exists():
        return ""

    try:
        with open(feature_file) as f:
            data = json.load(f)

        # Find current feature
        for feat in data.get("features", []):
            if feat.get("status") == "in_progress":
                return f"""## Current Feature
- ID: {feat.get('id', 'unknown')}
- Description: {feat.get('description', '')[:100]}
- Priority: {feat.get('priority', 'P1')}"""

        # Find next pending
        for feat in data.get("features", []):
            if feat.get("status") == "pending":
                return f"""## Next Feature
- ID: {feat.get('id', 'unknown')}
- Description: {feat.get('description', '')[:100]}"""
    except:
        pass

    return ""


def compile_context(state: str, force: bool = False) -> str:
    """Compile full context for state."""

    # Check cache first
    if not force:
        cached = load_cached(state)
        if cached:
            return cached

    # Compile fresh
    sections = []

    # Header
    sections.append(f"# Compiled Context [{state}]")
    sections.append("_Auto-compiled from CLAUDE.md files. ~100 lines vs ~500._")

    # Global essentials
    global_ctx = compile_global_essentials()
    if global_ctx:
        sections.append(global_ctx)

    # Project essentials
    project_ctx = compile_project_essentials()
    if project_ctx:
        sections.append(project_ctx)

    # State-specific
    sections.append(compile_state_specific(state))

    # Current feature
    feature_ctx = compile_current_feature()
    if feature_ctx:
        sections.append(feature_ctx)

    compiled = "\n\n".join(sections)

    # Save to cache
    save_cache(state, compiled)

    return compiled


def main():
    state = sys.argv[1] if len(sys.argv) > 1 else "START"
    force = "--force" in sys.argv

    compiled = compile_context(state, force)
    print(compiled)


if __name__ == "__main__":
    main()
