#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PATTERNS: dict[str, re.Pattern[str]] = {
    "correction": re.compile(
        r"\b(do not|don't|never|stop|instead|not patch|root cause)\b", re.I
    ),
    "tool_preference": re.compile(r"\b(use|don't use|do not use)\s+[@$]?[A-Za-z0-9_-]+", re.I),
    "cleanup": re.compile(r"\b(cleanup|stale|duplicate|redirect|owner surface|AGENTS\.md)\b", re.I),
    "browser": re.compile(r"\b(Chrome|Browser|browser verification|DevTools|Playwright)\b", re.I),
    "subagent": re.compile(r"\b(subagent|delegate|parallel agent|cleanup auditor)\b", re.I),
    "automation": re.compile(r"\b(automation|hook|Stop hook|UserPromptSubmit|SessionStart)\b", re.I),
    "verification": re.compile(r"\b(test|quality-gate|lint|verify|evidence|metrics|logs)\b", re.I),
    "deterministic_first": re.compile(
        r"\b(deterministic|not a model backed|evidence|quality-gate|lint|verify|metrics|logs)\b",
        re.I,
    ),
    "context_pollution": re.compile(r"\b(pollute|pollution|main agent context|context)\b", re.I),
    "session_analysis": re.compile(
        r"\b(qmd|Obsidian|transcript|session analysis|Claude-Sessions)\b", re.I
    ),
}

NOISE_PREFIXES = (
    "# AGENTS.md instructions",
    "<environment_context>",
    "<INSTRUCTIONS>",
    "<goal_context>",
    "<turn_aborted>",
    "<subagent_notification>",
    "<skill>",
    "# Diff comments:",
    "Automation:",
    "You are an expert unknown developer.",
    "You are the improvement-scoping guide",
    "You are a helpful AI assistant for the project rooted",
)


def extract_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(extract_text(item) for item in value)
    if isinstance(value, dict):
        parts: list[str] = []
        for key in ("text", "content", "message", "prompt", "body"):
            if key in value:
                parts.append(extract_text(value[key]))
        return " ".join(parts)
    return ""


def user_message_text(record: dict[str, Any]) -> str:
    payload = record.get("payload")
    if isinstance(payload, dict) and payload.get("type") == "message":
        if payload.get("role") == "user":
            return extract_text(payload.get("content")).strip()
        return ""
    if record.get("role") == "user":
        return extract_text(record.get("content")).strip()
    return ""


def is_noise(text: str) -> bool:
    compact = text.lstrip()
    if compact.startswith(NOISE_PREFIXES):
        return True
    if "Global AGENTS.md" in compact[:1200] and "<INSTRUCTIONS>" in compact[:1200]:
        return True
    if "<system-reminder>" in compact[:500]:
        return True
    return "<hook_prompt hook_run_id=" in compact[:300] and "Before stopping:" in compact[:1200]


def iter_jsonl_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        expanded = path.expanduser()
        if expanded.is_dir():
            files.extend(expanded.rglob("*.jsonl"))
        elif expanded.is_file() and expanded.suffix == ".jsonl":
            files.append(expanded)
    return sorted(set(files))


def is_subagent_session(record: dict[str, Any]) -> bool:
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return False
    source = payload.get("source")
    return isinstance(source, dict) and "subagent" in source


def scan_files(
    files: list[Path],
    *,
    project: str | None,
    max_examples: int,
    include_subagents: bool,
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = {name: [] for name in PATTERNS}
    parse_errors = 0
    sessions_seen = 0
    sessions_matched = 0
    subagent_sessions_skipped = 0
    user_messages_before_noise = 0
    user_messages = 0
    noise_removed = 0

    for path in files:
        session_matches = project is None
        skip_session = False
        session_counted = False
        try:
            handle = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line_number, raw in enumerate(handle, 1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    record = json.loads(raw)
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue

                if record.get("type") == "session_meta":
                    sessions_seen += 1
                    skip_session = not include_subagents and is_subagent_session(record)
                    if skip_session:
                        subagent_sessions_skipped += 1
                    cwd = str((record.get("payload") or {}).get("cwd") or "")
                    session_matches = (
                        not skip_session
                        and (project is None or project in cwd or project in str(path))
                    )
                    if session_matches:
                        sessions_matched += 1
                    continue

                text = user_message_text(record)
                if not text:
                    continue
                if not session_counted and session_matches:
                    session_counted = True
                if not session_matches:
                    continue

                user_messages_before_noise += 1
                if is_noise(text):
                    noise_removed += 1
                    continue
                user_messages += 1
                compact = re.sub(r"\s+", " ", text).strip()[:240]
                for name, pattern in PATTERNS.items():
                    if pattern.search(text):
                        counts[name] += 1
                        if len(examples[name]) < max_examples:
                            examples[name].append(
                                {
                                    "file": str(path),
                                    "line": line_number,
                                    "snippet": compact,
                                }
                            )

    return {
        "files_scanned": len(files),
        "sessions_seen": sessions_seen,
        "sessions_matched": sessions_matched,
        "subagent_sessions_skipped": subagent_sessions_skipped,
        "parse_errors": parse_errors,
        "user_messages_before_noise": user_messages_before_noise,
        "noise_removed": noise_removed,
        "user_messages": user_messages,
        "signals": [
            {"signal": name, "count": counts[name], "examples": examples[name]}
            for name in sorted(PATTERNS)
            if counts[name]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministically scan raw Codex JSONL transcripts for user steering signals."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="JSONL file or directory roots. Defaults to ~/.codex/sessions and ~/.codex/archived_sessions.",
    )
    parser.add_argument(
        "--project",
        help="Only include sessions whose cwd or transcript path contains this string.",
    )
    parser.add_argument("--max-examples", type=int, default=3)
    parser.add_argument(
        "--include-subagents",
        action="store_true",
        help="Include spawned subagent transcripts. Default excludes them because their user prompts are assistant-authored delegation prompts.",
    )
    args = parser.parse_args()

    paths = args.paths or [
        Path("~/.codex/sessions"),
        Path("~/.codex/archived_sessions"),
    ]
    files = iter_jsonl_files(paths)
    if not files:
        print("no JSONL transcripts found", file=sys.stderr)
        return 2

    output = scan_files(
        files,
        project=args.project,
        max_examples=args.max_examples,
        include_subagents=args.include_subagents,
    )
    output["method"] = "raw_codex_jsonl"
    output["project_filter"] = args.project
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
