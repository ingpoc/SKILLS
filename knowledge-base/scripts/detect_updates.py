#!/usr/bin/env python3
"""State-tracker for the knowledge-base skill.

Detects upstream changes across five surfaces:
  1. Claude Code docs (weekly whats-new)
  2. Claude Code GitHub CHANGELOG (per-version details)
  3. Claude Agent SDK Python+TS
  4. Claude Managed Agents
  5. Codex SDK

A sixth surface — OpenAI API platform (Responses API + GPT-5.x), rubric slug
`openai-api-rubric` — is maintained but NOT wired here: its docs have no
machine-readable release/CHANGELOG feed, and commit_state() fails loudly on any
fetch error, so a brittle source would break every refresh. Audit Surface 6
manually against https://developers.openai.com/api/docs (see references/surface-urls.md).

A seventh surface — Agent Skills (open SKILL.md format), rubric slug
`agent-skills-rubric` — is likewise maintained but not wired: it has no version
feed. Diff https://agentskills.io/llms.txt against ingested articles to spot new
pages (see references/surface-urls.md).

Two modes:
  --json          Read current upstream state, diff against state.json, emit delta.
  --commit-state  Write current upstream versions to state.json after a successful refresh.

State file:  .claude/skills/knowledge-base/state.json  (committed to git)
Run from:    project root (so the relative .claude path resolves)

Exit codes:
  0 — no changes (state matches upstream) OR commit-state succeeded
  1 — changes detected (delta non-empty)
  2 — fetch error (upstream unreachable)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "state.json"

SOURCES = {
    "claude_code": {
        "name": "Claude Code (CLI/IDE/Desktop/Web)",
        "url": "https://code.claude.com/docs/en/whats-new",
        "version_pattern": r"(2026-w\d+)",
        "section_pattern": r"href=\"/docs/en/whats-new/(2026-w\d+)\"",  # sidebar week links
    },
    "claude_agent_sdk_python": {
        "name": "Claude Agent SDK (Python)",
        "url": "https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/CHANGELOG.md",
        "version_pattern": r"^## (\d+\.\d+\.\d+)",  # changelog headings
        "release_pattern": r"^## (\d+\.\d+\.\d+)\s*\n",
    },
    "claude_agent_sdk_typescript": {
        "name": "Claude Agent SDK (TypeScript)",
        "url": "https://raw.githubusercontent.com/anthropics/claude-agent-sdk-typescript/main/CHANGELOG.md",
        "version_pattern": r"^## (\d+\.\d+\.\d+)",
        "release_pattern": r"^## (\d+\.\d+\.\d+)\s*\n",
    },
    "codex_sdk": {
        "name": "OpenAI Codex SDK / CLI",
        "url": "https://github.com/openai/codex/releases.atom",
        "version_pattern": r"<title>v?(\d+\.\d+\.\d+)</title>",
        "release_pattern": r"<title>(v?\d+\.\d+\.\d+)</title>",
    },
    "claude_code_github": {
        "name": "Claude Code (GitHub CHANGELOG)",
        "url": "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md",
        "version_pattern": r"^## (\d+\.\d+\.\d+)",
        "release_pattern": r"^## (\d+\.\d+\.\d+)\s*\n",
    },
}


def fetch(url: str, timeout: int = 30) -> tuple[str | None, str | None]:
    """Fetch URL content. Returns (content, error_message)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "knowledge-base-skill/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace"), None
    except urllib.error.URLError as e:
        return None, f"urlerror: {e}"
    except Exception as e:  # noqa: BLE001
        return None, f"fetch error: {e}"


def parse_versions(content: str, surface: str) -> list[str]:
    """Extract version markers from upstream content (latest first)."""
    cfg = SOURCES[surface]
    pattern = cfg.get("release_pattern", cfg["version_pattern"])
    if surface == "claude_code":
        # whats-new is week-based; extract week URLs from the sidebar
        matches = re.findall(cfg["section_pattern"], content)
        # dedupe while preserving order
        seen: set[str] = set()
        ordered: list[str] = []
        for w in matches:
            if w not in seen:
                seen.add(w)
                ordered.append(w)
        return ordered[:10]
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches[:10]


def load_state() -> dict:
    """Load persisted state. Empty dict if not yet committed."""
    if not STATE_PATH.exists():
        return {"surfaces": {}, "committed_at": None}
    try:
        return json.loads(STATE_PATH.read_text())
    except json.JSONDecodeError:
        return {"surfaces": {}, "committed_at": None}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["committed_at"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def detect() -> dict:
    """Fetch current upstream, diff against state, return {delta, current, errors}."""
    state = load_state()
    saved = state.get("surfaces", {})

    current: dict[str, list[str]] = {}
    errors: dict[str, str] = {}

    for surface, cfg in SOURCES.items():
        content, err = fetch(cfg["url"])
        if err or content is None:
            errors[surface] = err or "empty response"
            current[surface] = saved.get(surface, [])  # fall back to saved
            continue
        current[surface] = parse_versions(content, surface)

    delta: dict[str, list[str]] = {}
    for surface, vers in current.items():
        saved_vers = set(saved.get(surface, []))
        new_vers = [v for v in vers if v not in saved_vers]
        if new_vers:
            delta[surface] = new_vers

    return {
        "delta": delta,
        "current_versions": current,
        "errors": errors,
        "since_committed_at": state.get("committed_at"),
        "now": datetime.now(timezone.utc).isoformat(),
    }


def commit_state() -> dict:
    """Fetch current upstream and write to state.json. Returns the committed state."""
    previous = load_state()
    state = {"surfaces": {}}
    if "last_rubric_update" in previous:
        state["last_rubric_update"] = previous["last_rubric_update"]
    errors: dict[str, str] = {}
    for surface, cfg in SOURCES.items():
        content, err = fetch(cfg["url"])
        if err or content is None:
            errors[surface] = err or "empty response"
            continue
        state["surfaces"][surface] = parse_versions(content, surface)
    if errors:
        # Don't commit partial state — better to fail loudly
        return {"committed": False, "errors": errors}
    save_state(state)
    return {"committed": True, "state_path": str(STATE_PATH), "surfaces": list(state["surfaces"].keys()), "committed_at": state["committed_at"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="KB upstream state-tracker")
    parser.add_argument("--json", action="store_true", help="Emit JSON delta to stdout (default mode).")
    parser.add_argument("--commit-state", action="store_true", help="Write current upstream versions to state.json.")
    args = parser.parse_args()

    if args.commit_state:
        result = commit_state()
        print(json.dumps(result, indent=2))
        return 0 if result.get("committed") else 2

    # Default: detect mode
    result = detect()
    print(json.dumps(result, indent=2))
    if result["errors"]:
        return 2  # fetch errors — proceed with caution
    return 1 if result["delta"] else 0


if __name__ == "__main__":
    sys.exit(main())
