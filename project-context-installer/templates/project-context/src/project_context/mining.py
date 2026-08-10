from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from project_context.db import connect, fetch_all_dicts, read_json, utc_now, write_json
from project_context.extraction import parse_decision_text, payload_json

ACTIVE_SESSION_GRACE_SECONDS = 300
SOURCE_RESOLUTION_TERMINAL_STATUSES = {
    "covered_by_curated_summary",
    "imported_filtered_codex_jsonl",
    "out_of_scope_recent_active",
    "out_of_scope_aborted_child",
    "out_of_scope_control_thread",
    "out_of_scope_duplicate_child",
}


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _codex_sessions_root() -> Path:
    override = os.environ.get("PROJECT_CONTEXT_CODEX_SESSIONS_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".codex" / "sessions"


def _raw_codex_session_meta(path: Path, project_root: Path) -> dict | None:
    meta: dict | None = None
    last_timestamp: str | None = None
    line_count = 0
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                line_count += 1
                payload = json.loads(line)
                last_timestamp = payload.get("timestamp") or last_timestamp
                if payload.get("type") == "session_meta":
                    meta = payload.get("payload", {})
    except (OSError, json.JSONDecodeError):
        return None
    if not meta or Path(meta.get("cwd", "")).resolve() != project_root:
        return None
    source_ref = meta.get("id")
    if not source_ref:
        return None
    return {
        "source_ref": source_ref,
        "source_type": "codex_jsonl",
        "path": str(path),
        "parent_thread_id": meta.get("parent_thread_id"),
        "started_at": meta.get("timestamp"),
        "last_timestamp": last_timestamp or meta.get("timestamp"),
        "line_count": line_count,
    }


def list_unimported_codex_sessions(root: Path) -> dict:
    project_root = root.resolve()
    sessions_root = _codex_sessions_root()
    if not sessions_root.exists():
        return {
            "scanned": False,
            "sessions_root": str(sessions_root),
            "unimported_sessions": [],
            "recent_unimported_sessions": [],
            "resolved_source_sessions": [],
        }

    conn = connect(root)
    imported_refs = {
        row["source_ref"]
        for row in fetch_all_dicts(conn, "SELECT source_ref FROM sessions")
    }
    resolutions = {
        row["source_ref"]: row
        for row in fetch_all_dicts(conn, "SELECT * FROM source_session_resolutions")
    }
    cutoff = datetime.now(UTC).timestamp() - ACTIVE_SESSION_GRACE_SECONDS
    unimported: list[dict] = []
    recent: list[dict] = []
    resolved: list[dict] = []
    for path in sorted(sessions_root.glob("**/rollout-*.jsonl")):
        meta = _raw_codex_session_meta(path, project_root)
        if meta is None or meta["source_ref"] in imported_refs:
            continue
        resolution = resolutions.get(meta["source_ref"])
        if resolution is not None and resolution["resolution_status"] in SOURCE_RESOLUTION_TERMINAL_STATUSES:
            resolved.append({**meta, "resolution": dict(resolution)})
            continue
        if resolution is not None:
            meta = {**meta, "resolution": dict(resolution)}
        parsed_last = _parse_timestamp(meta.get("last_timestamp"))
        if parsed_last is not None and parsed_last.timestamp() > cutoff:
            recent.append(meta)
        else:
            unimported.append(meta)
    return {
        "scanned": True,
        "sessions_root": str(sessions_root),
        "unimported_sessions": unimported,
        "recent_unimported_sessions": recent,
        "resolved_source_sessions": resolved,
    }


def list_source_inventory(root: Path) -> dict:
    inventory = list_unimported_codex_sessions(root)
    conn = connect(root)
    imported = fetch_all_dicts(
        conn,
        """
        SELECT source_ref, source_type, sequence_no, started_at, ended_at
        FROM sessions
        ORDER BY sequence_no
        """,
    )
    return {**inventory, "imported_sessions": imported}


def resolve_source_session(
    root: Path,
    *,
    source_ref: str,
    resolution_status: str,
    reason: str,
    resolver_type: str = "main_agent",
    evidence_ref: str | None = None,
) -> dict:
    return resolve_source_sessions(
        root,
        [
            {
                "source_ref": source_ref,
                "resolution_status": resolution_status,
                "reason": reason,
                "evidence_ref": evidence_ref,
            }
        ],
        resolver_type=resolver_type,
    )[0]


def resolve_source_sessions(root: Path, resolutions: list[dict], *, resolver_type: str = "main_agent") -> list[dict]:
    inventory = list_unimported_codex_sessions(root)
    all_sessions = [
        *inventory["unimported_sessions"],
        *inventory["recent_unimported_sessions"],
        *inventory["resolved_source_sessions"],
    ]
    sessions_by_ref = {item["source_ref"]: item for item in all_sessions}
    conn = connect(root)
    results: list[dict] = []
    resolved_at = utc_now()
    conn.execute("BEGIN IMMEDIATE")
    try:
        for resolution in resolutions:
            source_ref = resolution["source_ref"]
            session = sessions_by_ref.get(source_ref)
            if session is None:
                raise ValueError(f"source_ref not found in raw Codex inventory: {source_ref}")
            resolution_status = resolution["resolution_status"]
            reason = resolution["reason"]
            evidence_ref = resolution.get("evidence_ref")
            conn.execute(
                """
                INSERT INTO source_session_resolutions(
                    source_ref, source_type, path, parent_thread_id, started_at, last_timestamp,
                    line_count, resolution_status, reason, evidence_ref, resolved_at, resolver_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_ref) DO UPDATE SET
                    source_type = excluded.source_type,
                    path = excluded.path,
                    parent_thread_id = excluded.parent_thread_id,
                    started_at = excluded.started_at,
                    last_timestamp = excluded.last_timestamp,
                    line_count = excluded.line_count,
                    resolution_status = excluded.resolution_status,
                    reason = excluded.reason,
                    evidence_ref = excluded.evidence_ref,
                    resolved_at = excluded.resolved_at,
                    resolver_type = excluded.resolver_type
                """,
                (
                    session["source_ref"],
                    session["source_type"],
                    session["path"],
                    session.get("parent_thread_id"),
                    session.get("started_at"),
                    session.get("last_timestamp"),
                    session.get("line_count", 0),
                    resolution_status,
                    reason,
                    evidence_ref,
                    resolved_at,
                    resolver_type,
                ),
            )
            results.append(
                {
                    "status": "resolved",
                    "source_ref": source_ref,
                    "resolution_status": resolution_status,
                    "reason": reason,
                }
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return results


def list_unmined_sessions(root: Path) -> list[dict]:
    conn = connect(root)
    checkpoints = read_json((root / ".context-graph" / "state" / "checkpoints.json"))
    last_promoted = checkpoints.get("last_promoted_sequence", 0)
    return fetch_all_dicts(
        conn,
        """
        SELECT id, project_id, source_type, source_ref, sequence_no, started_at, ended_at
        FROM sessions
        WHERE sequence_no > ?
        ORDER BY sequence_no ASC
        """,
        (last_promoted,),
    )


def list_pending_mining_sessions(root: Path) -> list[dict]:
    conn = connect(root)
    checkpoints = read_json((root / ".context-graph" / "state" / "checkpoints.json"))
    last_candidate = checkpoints.get("last_candidate_sequence", 0)
    return fetch_all_dicts(
        conn,
        """
        SELECT id, project_id, source_type, source_ref, sequence_no, started_at, ended_at
        FROM sessions
        WHERE sequence_no > ?
        ORDER BY sequence_no ASC
        """,
        (last_candidate,),
    )


def latest_pending_run(root: Path) -> dict | None:
    conn = connect(root)
    pending = conn.execute(
        """
        SELECT id, from_session_sequence, to_session_sequence, status
        FROM mining_runs
        WHERE status IN ('mined', 'review_required', 'validated_partial', 'validated_approved')
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    return None if pending is None else dict(pending)


def summarize_pending_mining(root: Path) -> dict:
    checkpoints = read_json((root / ".context-graph" / "state" / "checkpoints.json"))
    pending_sessions = list_pending_mining_sessions(root)
    pending_run = latest_pending_run(root)
    source_inventory = list_unimported_codex_sessions(root)
    unimported_source_sessions = source_inventory["unimported_sessions"]
    has_source_inventory_gap = bool(unimported_source_sessions)
    imported_pending_count = len(pending_sessions)
    source_gap_count = len(unimported_source_sessions)
    has_pending_mining = bool(pending_sessions) or has_source_inventory_gap
    if pending_sessions:
        status = "pending_mining"
    elif pending_run is not None:
        if pending_run["status"] == "mined":
            status = "pending_validation"
        elif pending_run["status"] == "review_required":
            status = "pending_review"
        else:
            status = "pending_promotion"
    elif has_source_inventory_gap:
        status = "source_inventory_gap"
    else:
        status = "clear"
    return {
        "status": status,
        "has_pending_mining": has_pending_mining,
        "pending_mining_count": imported_pending_count + source_gap_count,
        "pending_mining_imported_session_count": imported_pending_count,
        "pending_mining_source_gap_count": source_gap_count,
        "pending_mining_sessions": pending_sessions,
        "pending_mining_work_packet": (
            "unimported_source_sessions"
            if has_source_inventory_gap
            else "pending_mining_sessions"
            if pending_sessions
            else None
        ),
        "context_graph_review": "model_backed_review_required" if has_pending_mining else None,
        "has_source_inventory_gap": has_source_inventory_gap,
        "source_inventory_gap_count": source_gap_count,
        "unimported_source_sessions": unimported_source_sessions,
        "recent_unimported_source_sessions": source_inventory["recent_unimported_sessions"],
        "resolved_source_sessions": source_inventory["resolved_source_sessions"],
        "source_inventory": {
            "scanned": source_inventory["scanned"],
            "sessions_root": source_inventory["sessions_root"],
            "active_session_grace_seconds": ACTIVE_SESSION_GRACE_SECONDS,
        },
        "pending_run": pending_run,
        "checkpoints": {
            "last_candidate_sequence": checkpoints.get("last_candidate_sequence", 0),
            "last_promoted_sequence": checkpoints.get("last_promoted_sequence", 0),
        },
    }


def run_mining(root: Path, from_sequence: int | None = None, to_sequence: int | None = None) -> dict:
    conn = connect(root)
    checkpoints_path = root / ".context-graph" / "state" / "checkpoints.json"
    checkpoints = read_json(checkpoints_path)
    start_sequence = from_sequence or checkpoints.get("last_promoted_sequence", 0) + 1
    end_filter = ""
    params: list[object] = [start_sequence]
    if to_sequence is not None:
        end_filter = "AND sequence_no <= ?"
        params.append(to_sequence)
    sessions = fetch_all_dicts(
        conn,
        f"""
        SELECT id, sequence_no
        FROM sessions
        WHERE sequence_no >= ? {end_filter}
        ORDER BY sequence_no ASC
        """,
        params,
    )
    if not sessions:
        return {"status": "noop", "reason": "no sessions to mine"}

    run_id = conn.execute(
        """
        INSERT INTO mining_runs(started_at, from_session_sequence, to_session_sequence, status, miner_type, model, notes)
        VALUES (?, ?, ?, 'running', 'deterministic', NULL, '')
        """,
        (utc_now(), sessions[0]["sequence_no"], sessions[-1]["sequence_no"]),
    ).lastrowid

    candidate_count = 0
    for session in sessions:
        events = fetch_all_dicts(
            conn,
            """
            SELECT id, event_index, content_text
            FROM session_events
            WHERE session_id = ?
            ORDER BY event_index ASC
            """,
            (session["id"],),
        )
        for event in events:
            extracted = parse_decision_text(event["content_text"])
            if extracted is None:
                continue
            conn.execute(
                """
                INSERT INTO candidate_decisions(
                    mining_run_id, session_id, event_id, decision_key, decision_type, category, title,
                    summary, rationale_text, payload_json, scope_key, confidence, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    run_id,
                    session["id"],
                    event["id"],
                    extracted.decision_key,
                    extracted.decision_type,
                    extracted.category,
                    extracted.title,
                    extracted.summary,
                    extracted.rationale_text,
                    payload_json(extracted.payload),
                    extracted.scope_key,
                    extracted.confidence,
                ),
            )
            conn.execute(
                """
                INSERT INTO evidence_spans(source_kind, source_ref, session_id, event_start, event_end, quote_text, hash)
                VALUES ('session_event', ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event["id"]),
                    session["id"],
                    event["id"],
                    event["id"],
                    event["content_text"],
                    f"event:{event['id']}",
                ),
            )
            candidate_count += 1

    conn.execute("UPDATE mining_runs SET ended_at = ?, status = 'mined' WHERE id = ?", (utc_now(), run_id))
    conn.commit()
    checkpoints["last_candidate_sequence"] = sessions[-1]["sequence_no"]
    write_json(checkpoints_path, checkpoints)
    return {
        "status": "mined",
        "run_id": run_id,
        "session_count": len(sessions),
        "candidate_count": candidate_count,
        "from_sequence": sessions[0]["sequence_no"],
        "to_sequence": sessions[-1]["sequence_no"],
    }
