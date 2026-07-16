#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


IGNORED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "vendor",
}
PLAN_NAMES = (
    "productplan",
    "product-plan",
    "product_plan",
    "roadmap",
    "product-roadmap",
    "product_roadmap",
)
STATUS_NAMES = (
    "implementation",
    "progress",
    "status",
    "delivery-plan",
    "delivery_plan",
    "exec-plan",
    "exec_plan",
)
SKILL_LINK = re.compile(r"\[\$?([A-Za-z][A-Za-z0-9:_-]{1,80})\]\([^)]*/skills/[^)]*/SKILL\.md\)")
SKILL_TOKEN = re.compile(r"(?<![A-Za-z0-9_])\$([a-z][a-z0-9:_-]{2,80})")


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def project_files(root: Path, max_depth: int = 6) -> Iterable[Path]:
    for directory, names, files in os.walk(root):
        current = Path(directory)
        depth = len(current.relative_to(root).parts)
        names[:] = [name for name in names if name not in IGNORED_DIRS and not name.startswith(".worktree")]
        if depth >= max_depth:
            names[:] = []
        for name in files:
            yield current / name


def rank_candidate(path: Path, root: Path, terms: tuple[str, ...]) -> tuple[int, int, str]:
    relative = path.relative_to(root)
    stem = path.stem.lower()
    exact = 0 if stem in terms else 1
    return exact, len(relative.parts), str(relative).lower()


def candidates(root: Path, terms: tuple[str, ...], limit: int = 20) -> list[str]:
    matches = []
    for path in project_files(root):
        if path.suffix.lower() not in {".md", ".mdx", ".txt", ".json", ".yaml", ".yml"}:
            continue
        normalized = path.stem.lower()
        relative = str(path.relative_to(root)).lower()
        if any(term in normalized or term in relative for term in terms):
            matches.append(path)
    matches.sort(key=lambda path: rank_candidate(path, root, terms))
    return [str(path.relative_to(root)) for path in matches[:limit]]


def instruction_files(root: Path) -> list[str]:
    paths = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        candidate = root / name
        if candidate.is_file():
            paths.append(name)
    return paths


def local_skills(root: Path, limit: int = 40) -> list[str]:
    found: list[str] = []
    for base in (root / ".codex" / "skills", root / ".claude" / "skills", root / "skills"):
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*/SKILL.md")):
            found.append(str(path.relative_to(root)))
            if len(found) >= limit:
                return found
    return found


def recent_commits(root: Path, limit: int = 20) -> list[str]:
    result = git(root, "log", f"-{limit}", "--pretty=format:%h %s")
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def session_roots() -> list[Path]:
    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return [home / "sessions", home / "archived_sessions"]


def recent_session_candidates(days: int, scan_limit: int) -> list[Path]:
    threshold = datetime.now(timezone.utc).timestamp() - timedelta(days=days).total_seconds()
    paths: list[tuple[float, Path]] = []
    for base in session_roots():
        if not base.is_dir():
            continue
        for path in base.rglob("*.jsonl"):
            try:
                modified = path.stat().st_mtime
            except OSError:
                continue
            if modified >= threshold:
                paths.append((modified, path))
    paths.sort(key=lambda item: item[0], reverse=True)
    return [path for _, path in paths[:scan_limit]]


def session_meta(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            first = json.loads(handle.readline())
    except (OSError, json.JSONDecodeError):
        return None
    if first.get("type") != "session_meta" or not isinstance(first.get("payload"), dict):
        return None
    return first["payload"]


def message_text(payload: dict[str, Any]) -> str:
    if payload.get("type") != "message" or payload.get("role") not in {"user", "assistant"}:
        return ""
    parts = []
    for item in payload.get("content") or []:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            parts.append(item["text"])
    text = "\n".join(parts)
    if payload.get("role") == "user" and "# AGENTS.md instructions for" in text:
        return ""
    return text


def session_skill_mentions(path: Path, byte_limit: int = 8 * 1024 * 1024) -> Counter[str]:
    mentions: Counter[str] = Counter()
    consumed = 0
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                consumed += len(line.encode("utf-8", errors="ignore"))
                if consumed > byte_limit:
                    break
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("type") != "response_item" or not isinstance(row.get("payload"), dict):
                    continue
                text = message_text(row["payload"])
                for name in SKILL_LINK.findall(text):
                    mentions[name] += 1
                for name in SKILL_TOKEN.findall(text):
                    if ("-" in name or ":" in name) and not name.endswith(":"):
                        mentions[name] += 1
    except OSError:
        return Counter()
    return mentions


def recent_project_sessions(root: Path, *, days: int = 30, scan_limit: int = 300, limit: int = 8) -> dict[str, Any]:
    sessions = []
    aggregate: Counter[str] = Counter()
    for path in recent_session_candidates(days, scan_limit):
        meta = session_meta(path)
        if not meta:
            continue
        try:
            cwd = Path(str(meta.get("cwd", ""))).expanduser().resolve()
        except (OSError, RuntimeError):
            continue
        if cwd != root:
            continue
        mentions = session_skill_mentions(path)
        aggregate.update(mentions)
        sessions.append({
            "id": meta.get("id") or meta.get("session_id"),
            "timestamp": meta.get("timestamp"),
            "path": str(path),
            "skill_mentions": [name for name, _ in mentions.most_common(12)],
        })
        if len(sessions) >= limit:
            break
    return {
        "lookback_days": days,
        "sessions": sessions,
        "common_skill_mentions": [
            {"name": name, "count": count} for name, count in aggregate.most_common(20)
        ],
        "authority": "hints-only",
    }


def inventory(root: Path, *, session_days: int, session_limit: int) -> dict[str, Any]:
    head = git(root, "rev-parse", "HEAD")
    branch = git(root, "branch", "--show-current")
    return {
        "schema_version": 1,
        "project_root": str(root),
        "git": {
            "head": head.stdout.strip() if head.returncode == 0 else None,
            "branch": branch.stdout.strip() if branch.returncode == 0 else None,
            "recent_commits": recent_commits(root),
        },
        "owner_routing_candidates": instruction_files(root),
        "product_plan_candidates": candidates(root, PLAN_NAMES),
        "implementation_status_candidates": candidates(root, STATUS_NAMES),
        "local_skills": local_skills(root),
        "recent_project_sessions": recent_project_sessions(
            root,
            days=session_days,
            limit=session_limit,
        ),
        "rules": [
            "Owner routes and live acceptance evidence outrank filename heuristics.",
            "Session history and skill mentions are hints, never completion evidence.",
            "Do not infer implementation percentage from file or commit counts.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a bounded, read-only project inventory for session orchestration")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--session-days", type=int, default=30)
    parser.add_argument("--session-limit", type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.session_days <= 90:
        parser.error("--session-days must be between 1 and 90")
    if not 0 <= args.session_limit <= 20:
        parser.error("--session-limit must be between 0 and 20")
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"project_inventory: root is not a directory: {root}", file=sys.stderr)
        return 2
    print(json.dumps(inventory(root, session_days=args.session_days, session_limit=args.session_limit), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
