#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from entry import REFERENCE_SECTIONS, WORKFLOW

HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*$")


def extract_section(lines: list[str], title: str) -> list[str]:
    start = None
    level = None
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match and match.group(2) == title:
            start = index
            level = len(match.group(1))
            break
    if start is None or level is None:
        raise ValueError(f"workflow section not found: {title}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = HEADING.match(lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return lines[start:end]


def render(action: str, workflow: Path = WORKFLOW) -> str:
    sections = REFERENCE_SECTIONS.get(action, [])
    if not sections:
        return ""
    lines = workflow.read_text(encoding="utf-8").splitlines()
    rendered: list[str] = []
    covered: set[int] = set()
    for title in sections:
        chunk = extract_section(lines, title)
        start = lines.index(chunk[0])
        indexes = set(range(start, start + len(chunk)))
        if indexes <= covered:
            continue
        if rendered:
            rendered.append("")
        rendered.extend(chunk)
        covered.update(indexes)
    return "\n".join(rendered).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read only the workflow sections required by an entry action")
    parser.add_argument("--action", choices=sorted(REFERENCE_SECTIONS), required=True)
    args = parser.parse_args()
    try:
        sys.stdout.write(render(args.action))
    except (OSError, ValueError) as exc:
        print(f"workflow_slice: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
