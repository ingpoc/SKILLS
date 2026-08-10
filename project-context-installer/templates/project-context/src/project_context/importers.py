from __future__ import annotations

import hashlib
import re
from pathlib import Path


HEADER_RE = re.compile(r"^(thread_id|updated_at|rollout_path|cwd):\s*(.+)$")
SECTION_STARTERS = ("Preference signals:", "Reusable knowledge:")
SECTION_END_RE = re.compile(r"^(##\s+.+|[A-Z][A-Za-z ]+:)$")


def _slugify(text: str, limit: int = 48) -> str:
    lowered = text.lower()
    collapsed = re.sub(r"[^a-z0-9]+", ".", lowered).strip(".")
    if not collapsed:
        collapsed = "decision"
    if len(collapsed) > limit:
        collapsed = collapsed[:limit].rstrip(".")
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{collapsed}.{digest}"


def _extract_body(bullet: str) -> str:
    for separator in ("->", "→"):
        if separator in bullet:
            return bullet.split(separator, 1)[1].strip()
    return bullet


def parse_rollout_summary(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata: dict[str, str] = {}
    events: list[dict[str, str]] = []
    current_section: str | None = None
    for line in lines:
        header_match = HEADER_RE.match(line)
        if header_match:
            metadata[header_match.group(1)] = header_match.group(2).strip()
            continue
        if line.strip() in SECTION_STARTERS:
            current_section = line.strip().rstrip(":").lower().replace(" ", "_")
            continue
        if current_section is not None and SECTION_END_RE.match(line.strip()) and line.strip() not in SECTION_STARTERS:
            current_section = None
            continue
        if current_section is None or not line.startswith("- "):
            continue
        bullet = line[2:].strip()
        if not bullet:
            continue
        body = _extract_body(bullet)
        decision_type = "preference" if current_section == "preference_signals" else "rule"
        key = f"{current_section}.{_slugify(body)}"
        timestamp = metadata.get("updated_at", "1970-01-01T00:00:00+00:00")
        events.append(
            {
                "timestamp": timestamp,
                "event_type": "rollout_summary_inference",
                "role": "reviewer",
                "content_text": f"[decision key={key} type={decision_type} scope=repo] {body}",
            }
        )
    return {"metadata": metadata, "events": events}
