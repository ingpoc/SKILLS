from __future__ import annotations

import argparse
import shlex
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent / "templates"


TOOLS_PYPROJECT = """[project]
name = "project-context"
version = "0.1.0"
description = "Project-local context graph CLI"
requires-python = ">=3.12"

[project.scripts]
project-context = "project_context.cli:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
"""

TOOLS_README = """# Project Context

Local CLI for a project-specific context graph.

Use the repo wrapper instead of invoking this package directly:

```bash
./script/project_context.sh doctor
./script/project_context.sh session-start
```
"""

WRAPPER_SH = """#!/usr/bin/env bash
set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="$REPO_ROOT/tools/project-context"

if command -v uv >/dev/null 2>&1; then
  exec uv run --project "$PROJECT_DIR" project-context --root "$REPO_ROOT" "$@"
fi

export PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m project_context.cli --root "$REPO_ROOT" "$@"
"""

DB_PY = r'''from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT NOT NULL,
    sequence_no INTEGER NOT NULL UNIQUE,
    checksum TEXT,
    ingested_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    event_index INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    role TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    content_text TEXT NOT NULL,
    content_json TEXT,
    artifact_ref TEXT,
    UNIQUE(session_id, event_index)
);

CREATE TABLE IF NOT EXISTS mining_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    from_session_sequence INTEGER NOT NULL,
    to_session_sequence INTEGER NOT NULL,
    status TEXT NOT NULL,
    miner_type TEXT NOT NULL,
    model TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS candidate_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mining_run_id INTEGER NOT NULL REFERENCES mining_runs(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES session_events(id) ON DELETE CASCADE,
    decision_key TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    rationale_text TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    scope_key TEXT NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_key TEXT NOT NULL,
    version_no INTEGER NOT NULL,
    state TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    rationale_text TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    effective_at TEXT NOT NULL,
    validated_at TEXT NOT NULL,
    validation_run_id INTEGER NOT NULL REFERENCES mining_runs(id),
    UNIQUE(decision_key, version_no)
);

CREATE TABLE IF NOT EXISTS active_decisions (
    decision_key TEXT PRIMARY KEY,
    decision_version_id INTEGER NOT NULL REFERENCES decision_versions(id) ON DELETE CASCADE,
    activated_at TEXT NOT NULL,
    reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS supersedes_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_decision_version_id INTEGER NOT NULL REFERENCES decision_versions(id) ON DELETE CASCADE,
    to_decision_version_id INTEGER NOT NULL REFERENCES decision_versions(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_spans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_kind TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    event_start INTEGER NOT NULL,
    event_end INTEGER NOT NULL,
    quote_text TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS validation_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mining_run_id INTEGER NOT NULL REFERENCES mining_runs(id) ON DELETE CASCADE,
    reviewed_at TEXT NOT NULL,
    reviewer_type TEXT NOT NULL,
    status TEXT NOT NULL,
    review_notes TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS decision_search USING fts5(
    decision_key,
    title,
    summary,
    rationale_text,
    content='',
    tokenize='unicode61'
);
"""


@dataclass(slots=True)
class Paths:
    root: Path
    graph_dir: Path
    state_dir: Path
    reviews_dir: Path
    exports_dir: Path
    db_path: Path
    schema_path: Path
    checkpoints_path: Path
    latest_validated_run_path: Path


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def build_paths(root: Path) -> Paths:
    graph_dir = root / ".context-graph"
    state_dir = graph_dir / "state"
    return Paths(
        root=root,
        graph_dir=graph_dir,
        state_dir=state_dir,
        reviews_dir=graph_dir / "reviews",
        exports_dir=graph_dir / "exports",
        db_path=graph_dir / "graph.db",
        schema_path=graph_dir / "schema.sql",
        checkpoints_path=state_dir / "checkpoints.json",
        latest_validated_run_path=state_dir / "latest_validated_run.json",
    )


def ensure_layout(root: Path) -> Paths:
    paths = build_paths(root)
    for path in (
        paths.graph_dir,
        paths.state_dir,
        paths.reviews_dir,
        paths.exports_dir,
        paths.graph_dir / "migrations",
    ):
        path.mkdir(parents=True, exist_ok=True)
    if not paths.schema_path.exists():
        paths.schema_path.write_text(SCHEMA_SQL, encoding="utf-8")
    if not paths.checkpoints_path.exists():
        write_json(
            paths.checkpoints_path,
            {"last_candidate_sequence": 0, "last_promoted_sequence": 0},
        )
    if not paths.latest_validated_run_path.exists():
        write_json(paths.latest_validated_run_path, {"run_id": None})
    return paths


def connect(root: Path) -> sqlite3.Connection:
    paths = ensure_layout(root)
    conn = sqlite3.connect(paths.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA_SQL)
    return conn


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def fetch_all_dicts(conn: sqlite3.Connection, query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in conn.execute(query, params)]
'''

EXTRACTION_PY = r'''from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


DECISION_RE = re.compile(r"^\[(?P<tag>[a-z_]+)\s+(?P<attrs>[^\]]+)\]\s*(?P<body>.+)$")
ATTR_RE = re.compile(r"([a-z_]+)=([^\s]+)")


@dataclass(slots=True)
class ExtractedDecision:
    decision_key: str
    decision_type: str
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
    return ExtractedDecision(
        decision_key=decision_key,
        decision_type=decision_type,
        title=title,
        summary=body,
        rationale_text=body,
        scope_key=scope_key,
        confidence=confidence,
        payload={"attrs": attrs, "body": body},
    )


def payload_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True)
'''

MINING_PY = r'''from __future__ import annotations

from pathlib import Path

from project_context.db import connect, fetch_all_dicts, read_json, utc_now, write_json
from project_context.extraction import parse_decision_text, payload_json


def list_unmined_sessions(root: Path) -> list[dict]:
    conn = connect(root)
    checkpoints = read_json((root / ".context-graph" / "state" / "checkpoints.json"))
    last_promoted = checkpoints.get("last_promoted_sequence", 0)
    return fetch_all_dicts(
        conn,
        """
        SELECT id, source_ref, sequence_no, started_at, ended_at
        FROM sessions
        WHERE sequence_no > ?
        ORDER BY sequence_no ASC
        """,
        (last_promoted,),
    )


def latest_pending_run(root: Path) -> dict | None:
    conn = connect(root)
    pending = conn.execute(
        """
        SELECT id, from_session_sequence, to_session_sequence, status
        FROM mining_runs
        WHERE status IN ('mined', 'validated_partial', 'validated_approved')
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()
    return None if pending is None else dict(pending)


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
                    mining_run_id, session_id, event_id, decision_key, decision_type, title,
                    summary, rationale_text, payload_json, scope_key, confidence, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    run_id,
                    session["id"],
                    event["id"],
                    extracted.decision_key,
                    extracted.decision_type,
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
'''

RETRIEVAL_PY = r'''from __future__ import annotations

from pathlib import Path

from project_context.db import connect, fetch_all_dicts, row_to_dict


def get_active_decisions(root: Path) -> list[dict]:
    conn = connect(root)
    return fetch_all_dicts(
        conn,
        """
        SELECT
            dv.id AS decision_version_id,
            dv.decision_key,
            dv.decision_type,
            dv.title,
            dv.summary,
            dv.rationale_text,
            dv.state,
            dv.validated_at,
            ad.activated_at
        FROM active_decisions ad
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        ORDER BY dv.decision_key ASC
        """
    )


def get_decision_history(root: Path, decision_key: str) -> list[dict]:
    conn = connect(root)
    return fetch_all_dicts(
        conn,
        """
        SELECT id, decision_key, version_no, state, title, summary, rationale_text, effective_at, validated_at
        FROM decision_versions
        WHERE decision_key = ?
        ORDER BY version_no ASC
        """,
        (decision_key,),
    )


def explain_decision(root: Path, decision_key: str) -> dict | None:
    conn = connect(root)
    row = conn.execute(
        """
        SELECT
            dv.*,
            ad.activated_at
        FROM active_decisions ad
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        WHERE dv.decision_key = ?
        """,
        (decision_key,),
    ).fetchone()
    if row is None:
        return None
    payload = row_to_dict(row)
    evidence = fetch_all_dicts(
        conn,
        """
        SELECT es.quote_text, es.source_ref, es.hash
        FROM evidence_spans es
        JOIN candidate_decisions cd ON cd.event_id = es.event_start
        WHERE cd.decision_key = ?
        ORDER BY es.id DESC
        LIMIT 3
        """,
        (decision_key,),
    )
    payload["evidence"] = evidence
    return payload
'''

VALIDATION_PY = r'''from __future__ import annotations

from pathlib import Path

from project_context.db import connect, fetch_all_dicts, utc_now, write_json


def validate_run(root: Path, run_id: int, reviewer_type: str = "main_agent") -> dict:
    conn = connect(root)
    candidates = fetch_all_dicts(
        conn,
        """
        SELECT cd.id, cd.event_id, cd.decision_key, cd.summary, cd.status
        FROM candidate_decisions cd
        WHERE cd.mining_run_id = ?
        ORDER BY cd.id ASC
        """,
        (run_id,),
    )
    failures: list[str] = []
    validated_ids: list[int] = []
    for candidate in candidates:
        evidence_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM evidence_spans
            WHERE source_ref = ?
            """,
            (str(candidate["event_id"]),),
        ).fetchone()[0]
        if not candidate["decision_key"] or not candidate["summary"]:
            failures.append(f"candidate {candidate['id']} missing required fields")
            conn.execute("UPDATE candidate_decisions SET status = 'rejected' WHERE id = ?", (candidate["id"],))
            continue
        if evidence_count == 0:
            failures.append(f"candidate {candidate['id']} missing evidence")
            conn.execute("UPDATE candidate_decisions SET status = 'rejected' WHERE id = ?", (candidate["id"],))
            continue
        conn.execute("UPDATE candidate_decisions SET status = 'validated' WHERE id = ?", (candidate["id"],))
        validated_ids.append(candidate["id"])

    status = "approved" if not failures else ("partial" if validated_ids else "rejected")
    run_status = "validated_approved" if status == "approved" else ("validated_partial" if status == "partial" else "rejected")
    conn.execute("UPDATE mining_runs SET status = ? WHERE id = ?", (run_status, run_id))
    conn.execute(
        """
        INSERT INTO validation_reviews(mining_run_id, reviewed_at, reviewer_type, status, review_notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (run_id, utc_now(), reviewer_type, status, "\n".join(failures) or "validated"),
    )
    conn.commit()
    return {"status": status, "validated_candidate_ids": validated_ids, "failures": failures}


def promote_run(root: Path, run_id: int) -> dict:
    conn = connect(root)
    review = conn.execute(
        """
        SELECT status
        FROM validation_reviews
        WHERE mining_run_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    if review is None or review["status"] == "rejected":
        raise ValueError(f"run {run_id} is not approved for promotion")

    candidates = fetch_all_dicts(
        conn,
        """
        SELECT
            cd.*,
            s.started_at,
            s.sequence_no
        FROM candidate_decisions cd
        JOIN sessions s ON s.id = cd.session_id
        WHERE cd.mining_run_id = ? AND cd.status = 'validated'
        ORDER BY s.sequence_no ASC, cd.id ASC
        """,
        (run_id,),
    )
    promoted = 0
    latest_sequence = 0
    for candidate in candidates:
        latest_sequence = max(latest_sequence, candidate["sequence_no"])
        current = conn.execute(
            """
            SELECT dv.*
            FROM active_decisions ad
            JOIN decision_versions dv ON dv.id = ad.decision_version_id
            WHERE ad.decision_key = ?
            """,
            (candidate["decision_key"],),
        ).fetchone()
        if current is not None and current["summary"] == candidate["summary"]:
            continue
        next_version = 1
        if current is not None:
            next_version = current["version_no"] + 1
            conn.execute("UPDATE decision_versions SET state = 'superseded' WHERE id = ?", (current["id"],))
        new_id = conn.execute(
            """
            INSERT INTO decision_versions(
                decision_key, version_no, state, decision_type, title, summary,
                rationale_text, payload_json, effective_at, validated_at, validation_run_id
            ) VALUES (?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate["decision_key"],
                next_version,
                candidate["decision_type"],
                candidate["title"],
                candidate["summary"],
                candidate["rationale_text"],
                candidate["payload_json"],
                candidate["started_at"],
                utc_now(),
                run_id,
            ),
        ).lastrowid
        if current is not None:
            conn.execute(
                """
                INSERT INTO supersedes_edges(
                    from_decision_version_id, to_decision_version_id, relationship, confidence, created_by
                ) VALUES (?, ?, 'supersedes', 1.0, 'promote_run')
                """,
                (new_id, current["id"]),
            )
        conn.execute(
            """
            INSERT INTO active_decisions(decision_key, decision_version_id, activated_at, reason)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(decision_key) DO UPDATE SET
                decision_version_id = excluded.decision_version_id,
                activated_at = excluded.activated_at,
                reason = excluded.reason
            """,
            (candidate["decision_key"], new_id, utc_now(), f"promoted from run {run_id}"),
        )
        conn.execute(
            """
            INSERT INTO decision_search(rowid, decision_key, title, summary, rationale_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                new_id,
                candidate["decision_key"],
                candidate["title"],
                candidate["summary"],
                candidate["rationale_text"],
            ),
        )
        promoted += 1

    checkpoints_path = root / ".context-graph" / "state" / "checkpoints.json"
    latest_validated_run_path = root / ".context-graph" / "state" / "latest_validated_run.json"
    from project_context.db import read_json  # local import to avoid cycle
    checkpoints = read_json(checkpoints_path)
    checkpoints["last_promoted_sequence"] = max(checkpoints.get("last_promoted_sequence", 0), latest_sequence)
    write_json(checkpoints_path, checkpoints)
    write_json(latest_validated_run_path, {"run_id": run_id})
    conn.execute("UPDATE mining_runs SET status = 'promoted' WHERE id = ?", (run_id,))
    conn.commit()
    return {"status": "promoted", "run_id": run_id, "promoted_count": promoted}
'''

BOOTSTRAP_PY = r'''from __future__ import annotations

from pathlib import Path

from project_context.mining import list_unmined_sessions, latest_pending_run, run_mining
from project_context.retrieval import get_active_decisions
from project_context.validation import promote_run, validate_run


def session_start(root: Path) -> dict:
    pending = latest_pending_run(root)
    if pending is not None and pending["status"] != "promoted":
        validation_result = validate_run(root, pending["id"])
        if validation_result["status"] == "rejected":
            return {
                "status": "blocked",
                "reason": "validation rejected pending mining run",
                "run_id": pending["id"],
                "active_decisions": get_active_decisions(root),
            }
        promote_result = promote_run(root, pending["id"])
        return {
            "status": "ready",
            "run_id": pending["id"],
            "promoted_count": promote_result["promoted_count"],
            "active_decisions": get_active_decisions(root),
        }

    unmined = list_unmined_sessions(root)
    if not unmined:
        return {"status": "ready", "unmined_sessions": 0, "active_decisions": get_active_decisions(root)}
    mine_result = run_mining(root)
    if mine_result["status"] == "noop":
        return {"status": "ready", "unmined_sessions": 0, "active_decisions": get_active_decisions(root)}
    validation_result = validate_run(root, mine_result["run_id"])
    if validation_result["status"] == "rejected":
        return {
            "status": "blocked",
            "reason": "validation rejected mining run",
            "run_id": mine_result["run_id"],
            "active_decisions": get_active_decisions(root),
        }
    promote_result = promote_run(root, mine_result["run_id"])
    return {
        "status": "ready",
        "run_id": mine_result["run_id"],
        "promoted_count": promote_result["promoted_count"],
        "active_decisions": get_active_decisions(root),
    }
'''

CLI_PY = r'''from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_context.bootstrap import session_start
from project_context.db import build_paths, connect, ensure_layout, fetch_all_dicts, utc_now
from project_context.mining import list_unmined_sessions, run_mining
from project_context.retrieval import explain_decision, get_active_decisions, get_decision_history
from project_context.validation import promote_run, validate_run


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_init(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    paths = ensure_layout(root)
    connect(root).close()
    _print({"status": "initialized", "root": str(root), "db_path": str(paths.db_path)})


def cmd_doctor(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    paths = build_paths(root)
    payload = {
        "root": str(root),
        "exists": {
            "graph_dir": paths.graph_dir.exists(),
            "db_path": paths.db_path.exists(),
            "schema_path": paths.schema_path.exists(),
            "checkpoints_path": paths.checkpoints_path.exists(),
        },
    }
    _print(payload)


def cmd_import_session(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    conn = connect(root)
    session_path = Path(args.path).resolve()
    events = json.loads(session_path.read_text(encoding="utf-8"))
    current_max = conn.execute("SELECT COALESCE(MAX(sequence_no), 0) FROM sessions").fetchone()[0]
    sequence_no = current_max + 1
    started_at = args.started_at or events[0].get("timestamp") or utc_now()
    ended_at = args.ended_at or events[-1].get("timestamp") or started_at
    session_id = conn.execute(
        """
        INSERT INTO sessions(project_id, source_type, source_ref, started_at, ended_at, sequence_no, checksum, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            args.project_id,
            args.source_type,
            args.source_ref or session_path.name,
            started_at,
            ended_at,
            sequence_no,
            None,
            utc_now(),
        ),
    ).lastrowid
    for index, event in enumerate(events, start=1):
        conn.execute(
            """
            INSERT INTO session_events(session_id, event_index, event_type, role, timestamp, content_text, content_json, artifact_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                index,
                event.get("event_type", "message"),
                event.get("role", "unknown"),
                event.get("timestamp", started_at),
                event["content_text"],
                json.dumps(event, sort_keys=True),
                event.get("artifact_ref"),
            ),
        )
    conn.commit()
    _print({"status": "imported", "session_id": session_id, "sequence_no": sequence_no, "event_count": len(events)})


def cmd_scan_unmined(args: argparse.Namespace) -> None:
    _print(list_unmined_sessions(Path(args.root).resolve()))


def cmd_mine(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(run_mining(root, from_sequence=args.from_sequence, to_sequence=args.to_sequence))


def cmd_validate(args: argparse.Namespace) -> None:
    _print(validate_run(Path(args.root).resolve(), args.run_id))


def cmd_promote(args: argparse.Namespace) -> None:
    _print(promote_run(Path(args.root).resolve(), args.run_id))


def cmd_active(args: argparse.Namespace) -> None:
    _print(get_active_decisions(Path(args.root).resolve()))


def cmd_history(args: argparse.Namespace) -> None:
    _print(get_decision_history(Path(args.root).resolve(), args.decision_key))


def cmd_explain(args: argparse.Namespace) -> None:
    _print(explain_decision(Path(args.root).resolve(), args.decision_key))


def cmd_session_start(args: argparse.Namespace) -> None:
    _print(session_start(Path(args.root).resolve()))


def cmd_search(args: argparse.Namespace) -> None:
    conn = connect(Path(args.root).resolve())
    rows = fetch_all_dicts(
        conn,
        """
        SELECT rowid AS decision_version_id, decision_key, title, summary
        FROM decision_search
        WHERE decision_search MATCH ?
        ORDER BY rank
        LIMIT 10
        """,
        (args.query,),
    )
    _print(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-context")
    parser.add_argument("--root", default=".", help="Project root; defaults to cwd.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(func=cmd_init)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.set_defaults(func=cmd_doctor)

    import_parser = subparsers.add_parser("import-session")
    import_parser.add_argument("path")
    import_parser.add_argument("--project-id", default="default")
    import_parser.add_argument("--source-type", default="json")
    import_parser.add_argument("--source-ref")
    import_parser.add_argument("--started-at")
    import_parser.add_argument("--ended-at")
    import_parser.set_defaults(func=cmd_import_session)

    scan_parser = subparsers.add_parser("scan-unmined")
    scan_parser.set_defaults(func=cmd_scan_unmined)

    mine_parser = subparsers.add_parser("mine")
    mine_parser.add_argument("--from-sequence", type=int)
    mine_parser.add_argument("--to-sequence", type=int)
    mine_parser.set_defaults(func=cmd_mine)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-id", type=int, required=True)
    validate_parser.set_defaults(func=cmd_validate)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--run-id", type=int, required=True)
    promote_parser.set_defaults(func=cmd_promote)

    active_parser = subparsers.add_parser("active")
    active_parser.set_defaults(func=cmd_active)

    history_parser = subparsers.add_parser("history")
    history_parser.add_argument("--decision-key", required=True)
    history_parser.set_defaults(func=cmd_history)

    explain_parser = subparsers.add_parser("explain")
    explain_parser.add_argument("--decision-key", required=True)
    explain_parser.set_defaults(func=cmd_explain)

    session_start_parser = subparsers.add_parser("session-start")
    session_start_parser.set_defaults(func=cmd_session_start)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.set_defaults(func=cmd_search)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
'''

INIT_PY = '"""Project-local context graph package."""\n'

TEST_PY = r'''from __future__ import annotations

import json
from pathlib import Path

from project_context.bootstrap import session_start
from project_context.db import connect, ensure_layout
from project_context.mining import run_mining
from project_context.retrieval import get_active_decisions, get_decision_history
from project_context.validation import promote_run, validate_run


def create_session(root: Path, events: list[dict]) -> int:
    conn = connect(root)
    current_max = conn.execute("SELECT COALESCE(MAX(sequence_no), 0) FROM sessions").fetchone()[0]
    sequence_no = current_max + 1
    session_id = conn.execute(
        """
        INSERT INTO sessions(project_id, source_type, source_ref, started_at, ended_at, sequence_no, checksum, ingested_at)
        VALUES ('test', 'json', ?, ?, ?, ?, NULL, ?)
        """,
        (
            f"session-{sequence_no}.json",
            events[0]["timestamp"],
            events[-1]["timestamp"],
            sequence_no,
            events[-1]["timestamp"],
        ),
    ).lastrowid
    for index, event in enumerate(events, start=1):
        conn.execute(
            """
            INSERT INTO session_events(session_id, event_index, event_type, role, timestamp, content_text, content_json, artifact_ref)
            VALUES (?, ?, 'message', ?, ?, ?, ?, NULL)
            """,
            (session_id, index, event["role"], event["timestamp"], event["content_text"], json.dumps(event)),
        )
    conn.commit()
    return session_id


def test_chronological_mining_preserves_order(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=alpha.rule type=rule] First rule."}],
    )
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T10:00:00+00:00", "role": "user", "content_text": "[decision key=beta.rule type=rule] Second rule."}],
    )
    result = run_mining(tmp_path)
    assert result["from_sequence"] == 1
    assert result["to_sequence"] == 2


def test_same_day_override_marks_prior_inactive(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=memory.rule type=rule] Use memory at session start."}],
    )
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T11:00:00+00:00", "role": "user", "content_text": "[decision key=memory.rule type=rule] Use memory only when the task is not trivial."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validate_run(tmp_path, run_id)
    promote_run(tmp_path, run_id)
    active = get_active_decisions(tmp_path)
    assert len(active) == 1
    assert active[0]["summary"] == "Use memory only when the task is not trivial."
    history = get_decision_history(tmp_path, "memory.rule")
    assert [item["state"] for item in history] == ["superseded", "active"]


def test_rejected_run_does_not_affect_trusted_retrieval(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=owner.rule type=rule] Codex owns Codex work."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validate_run(tmp_path, run_id)
    promote_run(tmp_path, run_id)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T12:00:00+00:00", "role": "user", "content_text": "[decision key=broken.rule type=rule] This should fail validation."}],
    )
    second_run = run_mining(tmp_path)["run_id"]
    conn = connect(tmp_path)
    conn.execute("DELETE FROM evidence_spans WHERE source_ref = (SELECT CAST(event_id AS TEXT) FROM candidate_decisions WHERE mining_run_id = ? LIMIT 1)", (second_run,))
    conn.commit()
    result = validate_run(tmp_path, second_run)
    assert result["status"] == "rejected"
    active = get_active_decisions(tmp_path)
    assert [item["decision_key"] for item in active] == ["owner.rule"]


def test_missing_evidence_prevents_promotion(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T12:00:00+00:00", "role": "user", "content_text": "[decision key=broken.rule type=rule] Missing evidence should block promotion."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    conn = connect(tmp_path)
    conn.execute("DELETE FROM evidence_spans")
    conn.commit()
    result = validate_run(tmp_path, run_id)
    assert result["status"] == "rejected"


def test_active_retrieval_excludes_superseded_versions(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=route.rule type=rule] Start in scan lane."}],
    )
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T10:00:00+00:00", "role": "user", "content_text": "[decision key=route.rule type=rule] Classify the lane before acting."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validate_run(tmp_path, run_id)
    promote_run(tmp_path, run_id)
    active = get_active_decisions(tmp_path)
    assert len(active) == 1
    assert active[0]["summary"] == "Classify the lane before acting."


def test_lineage_query_shows_full_supersession_chain(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=graph.rule type=rule] First version."}],
    )
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T10:00:00+00:00", "role": "user", "content_text": "[decision key=graph.rule type=rule] Second version."}],
    )
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T11:00:00+00:00", "role": "user", "content_text": "[decision key=graph.rule type=rule] Third version."}],
    )
    result = session_start(tmp_path)
    assert result["status"] == "ready"
    history = get_decision_history(tmp_path, "graph.rule")
    assert [item["summary"] for item in history] == ["First version.", "Second version.", "Third version."]
'''

CONFTEST_PY = r'''from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
'''

def workflow_summary_command(target: Path, doc: str) -> str:
    docs_dir = shlex.quote(str(target / "docs"))
    return f"workflow --docs-dir {docs_dir} summary {doc}"


def project_context_block(target: Path) -> str:
    context_graph_summary = workflow_summary_command(target, "context-graph")
    return f"""

## Context Graph

- A repo-local context graph is installed under `tools/project-context` with the stable wrapper `./script/project_context.sh`.
- Runtime graph state lives under `.context-graph/` and is local-only.
- `session-start` reports graph health only and never supplies decisions.
- During every non-trivial task, agents should explicitly query relevant durable decisions with `./script/project_context.sh query --task "<current task>"`.
- Every decision has a normalized category used to narrow retrieval; `active` is for full-corpus audit/debugging.
- Use `./script/project_context.sh trace --decision-key <key>` for the full "why" record and `./script/project_context.sh related --decision-key <key>` for evidence-backed links.
- Relationships are evidence-backed only; category and shared source are metadata, not automatic edges.
- Durable decision retrieval should go through `{context_graph_summary}` and then the repo-local CLI.
- Pending context-graph work should be checked with `./script/project_context.sh pending-mining`; the response identifies exact pending session ids and source refs.
"""

VALIDATION_BLOCK = """

The project-local context graph can be checked with:

```sh
./script/project_context.sh doctor
./script/project_context.sh pending-mining
./script/project_context.sh session-start
./script/project_context.sh categories
./script/project_context.sh query --task "current task"
./script/project_context.sh trace --decision-key <key>
./script/project_context.sh related --decision-key <key>
./script/project_context.sh render-html
rg -q "nodeSearchText|MAX_RENDERED_NODES|replaceChildren" .context-graph/artifacts/context-graph.html
rg -q 'Active decision graph|Task query preview|Decision trace|Inputs considered|No explicit relationship recorded|detail-reveal' .context-graph/artifacts/context-graph.html
if rg -q "decision_relationships" .context-graph/artifacts/context-graph.html; then exit 1; fi
if rg -q "candidate_reviews" .context-graph/artifacts/context-graph.html; then exit 1; fi
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tools/project-context/tests -q
```
"""

OPERATOR_INTENT_BLOCK = """

## Context Graph Integration

When mined intent becomes durable project behavior, first choose the smallest correct durable owner surface.

- Put cross-project behavior in global `AGENTS.md`.
- Put repo startup routing and boundaries in local `AGENTS.md`.
- Put repeatable operational routes in workflow docs.
- Put stable facts in reference docs.
- Put specialized worker behavior in `.codex/agents/*.toml`.

Use the repo-local context graph for durable repo-local precedent and retrieval, not as a second copy of doctrine that is already correctly owned by one of the surfaces above. If the proper owner surface now exists, move the rule there and stop treating the graph entry as active control context.

Use:

```sh
./script/project_context.sh pending-mining
./script/project_context.sh session-start
./script/project_context.sh query --task "current task"
./script/project_context.sh trace --decision-key <key>
```
"""

def agents_context_trigger(target: Path) -> str:
    context_graph_summary = workflow_summary_command(target, "context-graph")
    return f"- BEFORE relying on durable project decision history or context graph state: `{context_graph_summary}`"


def agents_query_trigger() -> str:
    return '- BEFORE or DURING every non-trivial task: try `./script/project_context.sh query --task "<current task>"`; load only returned durable decisions that apply, and re-query when the task or decision point changes.'


def agents_viewer_trigger(target: Path) -> str:
    context_graph_summary = workflow_summary_command(target, "context-graph")
    return f"- BEFORE viewing or changing the interactive context graph HTML artifact: `{context_graph_summary}`, then `./script/project_context.sh render-html`."


AGENTS_RULE = "- When project decision-history, context-graph stack, generated HTML viewer, or validation commands change, update `docs/workflows/context-graph.md`, `docs/references/project-context.md`, and `docs/workflows/validation.md` in the same change."


def write_file(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def append_once(path: Path, block: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if block.strip() in text:
        return False
    path.write_text(text.rstrip() + "\n" + block.rstrip() + "\n", encoding="utf-8")
    return True


def insert_after_line(path: Path, needle: str, line_to_add: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if line_to_add in text:
        return False
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == needle.strip():
            lines.insert(index + 1, line_to_add)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


def insert_after_matching_line(path: Path, needle_text: str, line_to_add: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if line_to_add in text:
        return False
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if needle_text in line:
            lines.insert(index + 1, line_to_add)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


def ensure_matching_line(path: Path, needle_text: str, line_to_add: str) -> bool:
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if needle_text in line:
            if line == line_to_add:
                return False
            lines[index] = line_to_add
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


def ensure_gitignore_entry(path: Path, entry: str) -> bool:
    if not path.exists():
        path.write_text(entry + "\n", encoding="utf-8")
        return True
    text = path.read_text(encoding="utf-8")
    if entry in text.splitlines():
        return False
    path.write_text(text.rstrip() + "\n" + entry + "\n", encoding="utf-8")
    return True


def template_content(relative_path: str) -> str:
    path = TEMPLATE_ROOT / relative_path
    return path.read_text(encoding="utf-8")


def install(target: Path) -> dict:
    created: list[str] = []
    updated: list[str] = []

    files = {
        "tools/project-context/pyproject.toml": template_content("project-context/pyproject.toml"),
        "tools/project-context/README.md": template_content("project-context/README.md"),
        "tools/project-context/src/project_context/__init__.py": template_content("project-context/src/project_context/__init__.py"),
        "tools/project-context/src/project_context/categories.py": template_content("project-context/src/project_context/categories.py"),
        "tools/project-context/src/project_context/db.py": template_content("project-context/src/project_context/db.py"),
        "tools/project-context/src/project_context/extraction.py": template_content("project-context/src/project_context/extraction.py"),
        "tools/project-context/src/project_context/importers.py": template_content("project-context/src/project_context/importers.py"),
        "tools/project-context/src/project_context/mining.py": template_content("project-context/src/project_context/mining.py"),
        "tools/project-context/src/project_context/retrieval.py": template_content("project-context/src/project_context/retrieval.py"),
        "tools/project-context/src/project_context/validation.py": template_content("project-context/src/project_context/validation.py"),
        "tools/project-context/src/project_context/bootstrap.py": template_content("project-context/src/project_context/bootstrap.py"),
        "tools/project-context/src/project_context/cli.py": template_content("project-context/src/project_context/cli.py"),
        "tools/project-context/tests/test_context_graph.py": template_content("project-context/tests/test_context_graph.py"),
        "tools/project-context/tests/conftest.py": template_content("project-context/tests/conftest.py"),
        "script/project_context.sh": template_content("script/project_context.sh"),
        "docs/workflows/context-graph.md": template_content("docs/workflows/context-graph.md"),
    }
    for rel_path, content in files.items():
        dest = target / rel_path
        existed = dest.exists()
        write_file(dest, content, executable=rel_path.endswith(".sh"))
        (updated if existed else created).append(rel_path)

    gitignore_changed = ensure_gitignore_entry(target / ".gitignore", ".context-graph/")
    if gitignore_changed:
        updated.append(".gitignore")

    if (target / "AGENTS.md").exists():
        agents_path = target / "AGENTS.md"
        if insert_after_matching_line(agents_path, "BEFORE mining sessions, prompt history, or operator intent:", agents_context_trigger(target)):
            updated.append("AGENTS.md")
        if insert_after_matching_line(agents_path, "BEFORE relying on durable project decision history or context graph state:", agents_viewer_trigger(target)):
            updated.append("AGENTS.md")
        if insert_after_matching_line(agents_path, "BEFORE relying on durable project decision history or context graph state:", agents_query_trigger()):
            updated.append("AGENTS.md")
        if ensure_matching_line(agents_path, "When project decision-history, context-graph stack,", AGENTS_RULE):
            updated.append("AGENTS.md")
        elif insert_after_matching_line(agents_path, "When stack choices, runnable surfaces, or validation commands change", AGENTS_RULE):
            updated.append("AGENTS.md")

    if append_once(target / "docs/README.md", "- `context-graph`: repo-local durable decision graph workflow and validation contract."):
        updated.append("docs/README.md")
    if append_once(target / "docs/references/project-context.md", project_context_block(target)):
        updated.append("docs/references/project-context.md")
    if append_once(target / "docs/workflows/operator-intent-mining.md", OPERATOR_INTENT_BLOCK):
        updated.append("docs/workflows/operator-intent-mining.md")
    if append_once(target / "docs/workflows/validation.md", VALIDATION_BLOCK):
        updated.append("docs/workflows/validation.md")

    return {"created": created, "updated": sorted(set(updated))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Absolute path to the target repo.")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"target does not exist: {target}")
    result = install(target)
    print(result)


if __name__ == "__main__":
    main()
