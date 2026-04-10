#!/usr/bin/env python3
"""
Detect which skill to load based on user prompt and current state.

Usage:
    detect-skill.py "user prompt" [state]

Output:
    JSON: {"skill": "implementation", "reason": "IMPLEMENT state"}
    Or:   {"skill": null, "reason": "simple question"}
"""

import json
import re
import sys
from pathlib import Path


def get_current_state() -> str:
    """Get current state from state.json."""
    state_file = Path(".claude/progress/state.json")
    if state_file.exists():
        try:
            with open(state_file) as f:
                data = json.load(f)
                return data.get("state", "START")
        except (json.JSONDecodeError, KeyError):
            pass
    return "START"


def detect_skill(prompt: str, state: str) -> tuple[str | None, str]:
    """
    Detect which skill to load based on prompt and state.

    Returns:
        (skill_name, reason) or (None, reason)
    """
    prompt_lower = prompt.lower().strip()

    # Priority 0: Simple questions (no skill needed regardless of state)
    simple_question_patterns = [
        r"^what\s+(is|are|does|do)\s+",
        r"^explain\s+",
        r"^describe\s+",
        r"^tell\s+me\s+(about|what)",
        r"^how\s+does\s+.*\s+work",
        r"^why\s+(is|are|does|do)\s+",
        r"^can\s+you\s+explain",
    ]

    for pattern in simple_question_patterns:
        if re.search(pattern, prompt_lower):
            if not any(kw in prompt_lower for kw in ["implement", "create", "build", "add", "fix", "test"]):
                return (None, "simple knowledge question - no skill needed")

    # Priority 1: Slash commands (handled by Skill tool)
    if prompt_lower.strip().startswith("/"):
        return (None, "slash command - handled by Skill tool")

    # Priority 2: Explicit action requests
    if re.search(r"run\s+tests?", prompt_lower):
        return ("testing", "explicit test request")
    if re.search(r"setup|initialize|init\s+project", prompt_lower):
        return ("initialization", "setup request")

    # Priority 3: State-based detection
    state_skills = {
        "INIT": ("initialization", "INIT state - project needs setup"),
        "IMPLEMENT": ("implementation", "IMPLEMENT state - feature work"),
        "TEST": ("testing", "TEST state - validation needed"),
        "COMPLETE": ("context-graph", "COMPLETE state - capture learnings"),
        "FIX_BROKEN": ("enforcement", "FIX_BROKEN state - health check failed"),
    }

    if state in state_skills:
        return state_skills[state]

    # Priority 4: Keyword-based detection
    keyword_patterns = {
        "implementation": {
            "keywords": ["implement", "add feature", "create", "build", "develop", "code"],
            "reason": "implementation keywords detected"
        },
        "testing": {
            "keywords": ["test", "verify", "validate", "check", "qa"],
            "reason": "testing keywords detected"
        },
        "browser-testing": {
            "keywords": ["browser", "click", "form", "ui test", "page", "selenium", "playwright"],
            "reason": "browser testing keywords detected"
        },
        "context-graph": {
            "keywords": ["pattern", "decision", "trace", "learn", "past sessions"],
            "reason": "learning/pattern keywords detected"
        },
        "skill-creator": {
            "keywords": ["create skill", "new skill", "update skill", "skill template"],
            "reason": "skill creation keywords detected"
        },
        "claude-md-creator": {
            "keywords": ["claude.md", "update claude", "project instructions"],
            "reason": "CLAUDE.md keywords detected"
        },
    }

    for skill, config in keyword_patterns.items():
        for keyword in config["keywords"]:
            if keyword in prompt_lower:
                return (skill, config["reason"])

    # Priority 5: General questions (no skill)
    question_patterns = [
        r"^(what|how|why|when|where|who|which|can you|could you|would you)",
        r"\?$",
    ]

    for pattern in question_patterns:
        if re.search(pattern, prompt_lower):
            if any(kw in prompt_lower for kw in ["implement", "build", "create", "add"]):
                return ("implementation", "implementation question detected")
            return (None, "simple question - no skill needed")

    # Default
    if state == "START":
        return (None, "START state - no skill yet")

    return (None, "no matching pattern")


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"skill": None, "reason": "no prompt provided", "error": True}))
        sys.exit(1)

    prompt = sys.argv[1]
    state = sys.argv[2] if len(sys.argv) > 2 else get_current_state()

    skill, reason = detect_skill(prompt, state)

    result = {
        "skill": skill,
        "reason": reason,
        "state": state,
        "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
