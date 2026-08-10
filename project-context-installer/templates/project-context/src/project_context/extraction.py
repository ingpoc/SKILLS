from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from project_context.categories import infer_decision_category, normalize_category


DECISION_RE = re.compile(r"^\[(?P<tag>[a-z_]+)\s+(?P<attrs>[^\]]+)\]\s*(?P<body>.+)$")
ATTR_RE = re.compile(r"([a-z_]+)=([^\s]+)")


@dataclass(slots=True)
class ExtractedDecision:
    decision_key: str
    decision_type: str
    category: str
    title: str
    summary: str
    rationale_text: str
    scope_key: str
    confidence: float
    payload: dict[str, Any]


def parse_decision_text(content_text: str) -> ExtractedDecision | None:
    match = DECISION_RE.match(content_text.strip())
    if not match:
        return None
    attrs = {key: value for key, value in ATTR_RE.findall(match.group("attrs"))}
    decision_key = attrs.get("key")
    decision_type = attrs.get("type", match.group("tag"))
    title = attrs.get("title", decision_key or "")
    scope_key = attrs.get("scope", "project")
    confidence = float(attrs.get("confidence", "0.7"))
    body = match.group("body").strip()
    if not decision_key or not body:
        return None
    category = normalize_category(attrs["category"]) if attrs.get("category") else infer_decision_category(decision_key, title, body)
    return ExtractedDecision(
        decision_key=decision_key,
        decision_type=decision_type,
        category=category,
        title=title,
        summary=body,
        rationale_text=body,
        scope_key=scope_key,
        confidence=confidence,
        payload={"attrs": attrs, "body": body},
    )


def payload_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True)
