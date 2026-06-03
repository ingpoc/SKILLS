#!/usr/bin/env python3
"""Validate an app-side browser test bridge.

The script is intentionally small and dependency-free so agents can run it as a
deterministic first check before spending context on screenshots or UI trees.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class FetchResult:
    ok: bool
    status: int | None
    body: str
    error: str | None = None


def request(method: str, url: str, timeout: float) -> FetchResult:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return FetchResult(
                ok=200 <= response.status < 300,
                status=response.status,
                body=response.read().decode("utf-8", errors="replace"),
            )
    except urllib.error.HTTPError as exc:
        return FetchResult(
            ok=False,
            status=exc.code,
            body=exc.read().decode("utf-8", errors="replace"),
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 - report deterministic failure JSON
        return FetchResult(ok=False, status=None, body="", error=str(exc))


def parse_json(body: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "expected JSON object"
    return value, None


def byte_len(value: str) -> int:
    return len(value.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate /__debug browser bridge endpoints.")
    parser.add_argument("--base-url", required=True, help="Base URL, e.g. http://127.0.0.1:9876")
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--max-state-bytes", type=int, default=6000)
    parser.add_argument("--max-events-bytes", type=int, default=12000)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    endpoints = {
        "state": f"{base}/__debug/browser-state",
        "events": f"{base}/__debug/browser-events",
        "clear": f"{base}/__debug/clear",
    }

    clear = request("POST", endpoints["clear"], args.timeout)
    state = request("GET", endpoints["state"], args.timeout)
    events = request("GET", endpoints["events"], args.timeout)

    state_json, state_json_error = parse_json(state.body) if state.body else (None, "empty body")
    events_json, events_json_error = parse_json(events.body) if events.body else (None, "empty body")
    events_value = events_json.get("events") if isinstance(events_json, dict) else None

    state_has_bridge_shape = (
        isinstance(state_json, dict)
        and (
            isinstance(state_json.get("eventCount"), int)
            or isinstance(state_json.get("latest"), list)
            or isinstance(state_json.get("events"), list)
        )
    )
    checks = {
        "clear_ok": clear.ok or clear.status == 204,
        "state_ok": state.ok and state_json_error is None and state_has_bridge_shape,
        "events_ok": events.ok and events_json_error is None and isinstance(events_value, list),
        "state_compact": byte_len(state.body) <= args.max_state_bytes,
        "events_compact": byte_len(events.body) <= args.max_events_bytes,
    }
    ok = all(checks.values())
    report = {
        "ok": ok,
        "base_url": base,
        "checks": checks,
        "bytes": {
            "state": byte_len(state.body),
            "events": byte_len(events.body),
        },
        "status": {
            "clear": clear.status,
            "state": state.status,
            "events": events.status,
        },
        "errors": {
            "clear": clear.error,
            "state": state.error or state_json_error or (None if state_has_bridge_shape else "missing bridge state shape"),
            "events": events.error or events_json_error,
        },
        "event_count": len(events_value) if isinstance(events_value, list) else None,
        "next": (
            "Use /__debug/browser-state for compact internal browser evidence."
            if ok
            else "Add or fix the dev-only browser bridge before relying on internal browser evidence."
        ),
    }
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
