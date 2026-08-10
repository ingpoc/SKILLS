from __future__ import annotations

import re


CATEGORY_KEYWORDS = {
    "validation.native": {"xcrun", "swiftc", "build", "simulator", "xcode", "verify", "verification"},
    "architecture.swiftui": {"swiftui", "view", "views", "component", "components", "screen", "screens"},
    "ui.motion": {"animation", "animate", "motion", "transition", "gsap"},
    "ui.content": {"copy", "text", "prose", "icon", "icons", "image", "images", "label", "labels"},
    "ui.identity": {"identity", "brand", "branded", "personality", "visual", "motif", "styling"},
    "project.bootstrap": {"scaffold", "framework", "dependency", "backend", "api", "infra", "placeholder"},
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_category(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9.]+", ".", value.strip().lower()).strip(".")
    return normalized or "general"


def text_categories(value: str) -> list[str]:
    tokens = set(TOKEN_RE.findall(value.lower()))
    matches = [
        (category, len(tokens & keywords))
        for category, keywords in CATEGORY_KEYWORDS.items()
        if tokens & keywords
    ]
    return [category for category, _score in matches] or ["general"]


def infer_decision_category(decision_key: str, title: str, summary: str) -> str:
    tokens = set(TOKEN_RE.findall(f"{decision_key} {title} {summary}".lower()))
    matches = [
        (category, len(tokens & keywords))
        for category, keywords in CATEGORY_KEYWORDS.items()
        if tokens & keywords
    ]
    if not matches:
        return "general"
    return max(matches, key=lambda item: item[1])[0]
