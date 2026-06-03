#!/usr/bin/env python3
"""Lightweight checks for macOS WidgetKit design and local-data internals."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FINDINGS: list[tuple[str, str]] = []


def add(severity: str, message: str) -> None:
    FINDINGS.append((severity, message))


def read_swift(root: Path) -> dict[Path, str]:
    files: dict[Path, str] = {}
    for path in root.rglob("*.swift"):
        if any(part in {".build", "DerivedData"} for part in path.parts):
            continue
        try:
            files[path] = path.read_text(errors="replace")
        except OSError as exc:
            add("WARN", f"Could not read {path}: {exc}")
    return files


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def check_widget_surface(root: Path, files: dict[Path, str]) -> None:
    all_text = "\n".join(files.values())
    widget_files = {
        path: text
        for path, text in files.items()
        if "WidgetConfiguration" in text
        or "WidgetBundle" in text
        or "TimelineProvider" in text
        or "AppIntentTimelineProvider" in text
    }

    if not widget_files:
        add("FAIL", "No WidgetKit surface found: expected WidgetConfiguration, WidgetBundle, or TimelineProvider.")
        return

    if "containerBackground(for: .widget)" not in all_text:
        add("FAIL", "Missing containerBackground(for: .widget); desktop widgets need a real WidgetKit background.")

    for path, text in files.items():
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if "containerBackground(for: .widget)" not in line:
                continue
            window = "\n".join(lines[index : index + 16])
            if re.search(r"\.ultraThinMaterial|\.thinMaterial|\.regularMaterial", window):
                add("WARN", f"{rel(root, path)} uses material inside containerBackground; verify it does not whitewash on desktop.")

    if "Color.black" not in all_text:
        add("WARN", "No Color.black usage found; this design system expects a black or near-black authored surface.")


def check_banned_washes(root: Path, files: dict[Path, str]) -> None:
    beige = re.compile(r"\b(beige|cream|sand|tan|espresso|brown)\b", re.IGNORECASE)
    blue_wash = re.compile(
        r"\b(cyan|teal|aqua|blueGlass|glassBlue|translucentWash)\b|Color\(red:\s*0\.\d+,\s*green:\s*0\.\d+,\s*blue:\s*0\.[5-9]",
        re.IGNORECASE,
    )

    for path, text in files.items():
        if beige.search(text):
            add("WARN", f"{rel(root, path)} mentions beige/cream/sand/tan/brown; avoid these for this widget surface.")
        if blue_wash.search(text):
            add("WARN", f"{rel(root, path)} may hardcode blue/cyan glass tint; wallpaper/system should supply tint if needed.")


def check_internals(root: Path, files: dict[Path, str]) -> None:
    all_text = "\n".join(files.values())

    if "WidgetCenter.shared.reloadAllTimelines" not in all_text and "WidgetCenter.shared.reloadTimelines" not in all_text:
        add("WARN", "No WidgetCenter timeline reload call found after cache updates/local install.")

    app_group_markers = ["containerURL(forSecurityApplicationGroupIdentifier", "appGroup", "AppGroup", "group."]
    if not any(marker in all_text for marker in app_group_markers):
        add("WARN", "No app-group storage marker found; local widget data usually needs app-group cache access.")

    fallback_markers = ["Application Support", "candidateURLs", "fallback", "mirror"]
    if not any(marker in all_text for marker in fallback_markers):
        add("WARN", "No cache fallback/mirror marker found; local installs often need candidate cache paths.")

    trust_markers = ["stale", "battery_low", "battery_critical", "possibly_dead", "no_sensor_timestamp", "Unavailable", "No signal"]
    missing = [marker for marker in trust_markers if marker not in all_text]
    if len(missing) >= 4:
        add("WARN", "Few missing-data/ring-health markers found; stale sync and dead/low battery should be visible states.")

    network_in_widget = False
    for path, text in files.items():
        if ("TimelineProvider" in text or "AppIntentTimelineProvider" in text) and ("URLSession" in text or ".data(from:" in text):
            network_in_widget = True
            add("WARN", f"{rel(root, path)} appears to fetch network data in the widget timeline provider; prefer cached snapshots.")
    if not network_in_widget and "URLSession" not in all_text:
        add("INFO", "No URLSession found; if the widget needs live data, ensure another sync path writes the cache.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository or widget project root")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"FAIL: root does not exist: {root}")
        return 2

    files = read_swift(root)
    if not files:
        print(f"FAIL: no Swift files found under {root}")
        return 2

    check_widget_surface(root, files)
    check_banned_washes(root, files)
    check_internals(root, files)

    if not FINDINGS:
        print("PASS: mac-widget-design checks found no obvious design or internals issues.")
        return 0

    for severity, message in FINDINGS:
        print(f"{severity}: {message}")

    return 1 if any(severity == "FAIL" for severity, _ in FINDINGS) else 0


if __name__ == "__main__":
    sys.exit(main())
