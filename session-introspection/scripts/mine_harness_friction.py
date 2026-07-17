#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SESSIONS_ROOT = Path.home() / ".codex" / "sessions"

PATTERNS = {
    "broad_retrieval": re.compile(
        r"\bworkflow\s+(list|search|ask)\b|"
        r"\bworkflow\s+(summary|read)\b|"
        r"\bproject_context\.sh\s+query\b|"
        r"\brg\b.*(AGENTS|docs|skills|workflows)",
        re.IGNORECASE,
    ),
    "known_route": re.compile(
        r"route_contract|Known route contract|source_inventory_gap|first_command",
        re.IGNORECASE,
    ),
    "first_command": re.compile(r"\bpending-mining\b|first_command", re.IGNORECASE),
    "generic_checkpoint": re.compile(
        r"normal repo retrieval|first incomplete change|generic next_action",
        re.IGNORECASE,
    ),
    "hook_block_or_loop": re.compile(
        r"Owner topology changed|\"decision\"\s*:\s*\"block\"|"
        r"\bhook\s+(?:blocked|kept blocking|looped|entered (?:a )?loop)\b|too blocking",
        re.IGNORECASE,
    ),
    "handoff_nudge": re.compile(
        r"Large session\. Finish current activity|context_handoff_nudge status=nudged",
        re.IGNORECASE,
    ),
}


@dataclass
class SessionScan:
    path: Path
    source_ref: str | None
    cwd: str | None
    parent_thread_id: str | None
    line_count: int
    text_by_line: list[tuple[int, str, str]]


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_strings(child)


def evidence_strings(record: dict[str, Any]) -> Iterable[tuple[str, str]]:
    """Yield evidence-bearing Codex records, excluding injected instructions.

    Session JSONL contains full system/developer prompts and user-provided skill
    payloads. Those strings describe hooks, routes, and checkpoint anti-patterns
    without proving that any of them occurred. Restrict classification to
    assistant messages plus actual tool calls. Tool outputs are excluded because
    read-only retrieval commonly echoes old memory, skill text, and source-code
    regexes that look like fresh friction events.
    """

    if record.get("type") != "response_item":
        return
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return

    item_type = payload.get("type")
    if item_type == "message":
        if payload.get("role") != "assistant":
            return
        for text in iter_strings(payload.get("content", [])):
            yield "assistant_message", text
        return

    if item_type in {"custom_tool_call", "function_call"}:
        strings: list[str] = []
        for key in ("input", "arguments"):
            strings.extend(iter_strings(payload.get(key)))
        combined = "\n".join(strings)
        if re.search(r"\b(?:const\s+patch\s*=|apply_patch\s*\()", combined):
            return
        for text in strings:
            yield "tool_call", text
        return

def scan_session(path: Path) -> SessionScan | None:
    source_ref = None
    cwd = None
    parent_thread_id = None
    text_by_line: list[tuple[int, str, str]] = []
    line_count = 0

    try:
        with path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                line_count += 1
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if payload.get("type") == "session_meta":
                    meta = payload.get("payload", {})
                    if isinstance(meta, dict):
                        source_ref = meta.get("id") if isinstance(meta.get("id"), str) else source_ref
                        cwd = meta.get("cwd") if isinstance(meta.get("cwd"), str) else cwd
                        parent_thread_id = (
                            meta.get("parent_thread_id")
                            if isinstance(meta.get("parent_thread_id"), str)
                            else parent_thread_id
                        )
                strings_by_kind: dict[str, list[str]] = defaultdict(list)
                for kind, text in evidence_strings(payload):
                    if text.strip():
                        strings_by_kind[kind].append(text.strip())
                for kind, strings in strings_by_kind.items():
                    text_by_line.append((index, kind, "\n".join(strings)))
    except OSError:
        return None

    return SessionScan(
        path=path,
        source_ref=source_ref,
        cwd=cwd,
        parent_thread_id=parent_thread_id,
        line_count=line_count,
        text_by_line=text_by_line,
    )


def classify(scan: SessionScan) -> list[dict[str, object]]:
    hits: dict[str, list[int]] = defaultdict(list)
    signal_sources = {
        "broad_retrieval": {"tool_call"},
        "known_route": {"assistant_message", "tool_call"},
        "first_command": {"assistant_message", "tool_call"},
        "generic_checkpoint": {"assistant_message"},
        "hook_block_or_loop": {"assistant_message"},
        "handoff_nudge": {"assistant_message"},
    }
    for line_no, kind, text in scan.text_by_line:
        for name, pattern in PATTERNS.items():
            if kind in signal_sources[name] and pattern.search(text):
                hits[name].append(line_no)

    findings: list[dict[str, object]] = []
    broad_lines = hits.get("broad_retrieval", [])
    known_lines = hits.get("known_route", [])
    first_lines = hits.get("first_command", [])

    if broad_lines and known_lines:
        first_known = min(known_lines)
        first_command = min(first_lines) if first_lines else None
        broad_before_command = [
            line for line in broad_lines if line > first_known and (first_command is None or line < first_command)
        ]
        if broad_before_command:
            findings.append(
                {
                    "type": "broad_retrieval_before_known_route",
                    "lines": broad_before_command[:5],
                    "evidence": "broad retrieval appeared after a known route signal and before the first route command",
                }
            )

    for signal, finding_type in (
        ("generic_checkpoint", "generic_save_session_checkpoint"),
        ("hook_block_or_loop", "hook_block_or_loop"),
        ("handoff_nudge", "large_context_handoff_nudge"),
    ):
        lines = hits.get(signal, [])
        if lines:
            findings.append({"type": finding_type, "lines": lines[:5], "evidence": f"{signal} signal found"})

    return findings


def candidate_paths(root: Path) -> list[Path]:
    return sorted(root.glob("**/rollout-*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mine recent Codex sessions for repeated harness friction.")
    parser.add_argument("--sessions-root", default=str(DEFAULT_SESSIONS_ROOT))
    parser.add_argument("--cwd", default=None, help="Only include sessions from this cwd when session metadata is present.")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--current-transcript", default=None)
    parser.add_argument(
        "--include-latest-family",
        action="store_true",
        help="Include the newest matching root session and its subagents (excluded by default as the active family).",
    )
    args = parser.parse_args()

    sessions_root = Path(args.sessions_root).expanduser()
    limit = max(args.limit, 1)
    paths = candidate_paths(sessions_root) if sessions_root.exists() else []
    if args.current_transcript:
        current = Path(args.current_transcript).expanduser()
        if current.exists() and current not in paths:
            paths.insert(0, current)

    scan_cache: dict[Path, SessionScan | None] = {}

    def get_scan(path: Path) -> SessionScan | None:
        if path not in scan_cache:
            scan_cache[path] = scan_session(path)
        return scan_cache[path]

    current_family_id: str | None = None
    if not args.include_latest_family:
        for path in paths:
            scan = get_scan(path)
            if scan is None:
                continue
            if args.cwd and scan.cwd and Path(scan.cwd).resolve() != Path(args.cwd).resolve():
                continue
            current_family_id = scan.parent_thread_id or scan.source_ref
            if current_family_id:
                break

    scanned: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    candidate_files_examined = 0
    for path in paths:
        if len(scanned) >= limit:
            break
        candidate_files_examined += 1
        scan = get_scan(path)
        if scan is None:
            continue
        if args.cwd and scan.cwd and Path(scan.cwd).resolve() != Path(args.cwd).resolve():
            continue
        family_id = scan.parent_thread_id or scan.source_ref
        if current_family_id and family_id == current_family_id:
            continue
        findings = classify(scan)
        for finding in findings:
            counts[str(finding["type"])] += 1
        scanned.append(
            {
                "path": str(path),
                "source_ref": scan.source_ref,
                "cwd": scan.cwd,
                "parent_thread_id": scan.parent_thread_id,
                "line_count": scan.line_count,
                "findings": findings,
            }
        )

    recurring = [
        {"type": finding_type, "session_count": count}
        for finding_type, count in counts.most_common()
        if count >= 2
    ]
    print(
        json.dumps(
            {
                "status": "ok",
                "candidate_files_examined": candidate_files_examined,
                "excluded_current_family": current_family_id,
                "sessions_considered": len(scanned),
                "sessions_reported": len(scanned),
                "recurring_findings": recurring,
                "sessions": scanned,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
