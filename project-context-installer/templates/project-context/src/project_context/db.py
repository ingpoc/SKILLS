from __future__ import annotations

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

CREATE TABLE IF NOT EXISTS source_session_resolutions (
    source_ref TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    path TEXT NOT NULL,
    parent_thread_id TEXT,
    started_at TEXT,
    last_timestamp TEXT,
    line_count INTEGER NOT NULL,
    resolution_status TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence_ref TEXT,
    resolved_at TEXT NOT NULL,
    resolver_type TEXT NOT NULL
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
    category TEXT NOT NULL,
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
    category TEXT NOT NULL,
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

CREATE TABLE IF NOT EXISTS context_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    label TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(entity_type, entity_key)
);

CREATE TABLE IF NOT EXISTS decision_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_version_id INTEGER NOT NULL REFERENCES decision_versions(id) ON DELETE CASCADE,
    decision_key TEXT NOT NULL,
    task_text TEXT NOT NULL,
    situation_text TEXT NOT NULL,
    inputs_considered_json TEXT NOT NULL,
    rule_or_policy TEXT NOT NULL,
    exception_or_override TEXT NOT NULL,
    precedent_used TEXT NOT NULL,
    approval_or_operator_signal TEXT NOT NULL,
    outcome_text TEXT NOT NULL,
    evidence_refs_json TEXT NOT NULL,
    confidence REAL NOT NULL,
    validation_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(decision_version_id)
);

CREATE TABLE IF NOT EXISTS decision_trace_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_trace_id INTEGER NOT NULL REFERENCES decision_traces(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL,
    target_kind TEXT NOT NULL,
    target_key TEXT NOT NULL,
    target_label TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_by TEXT NOT NULL,
    UNIQUE(decision_trace_id, relationship, target_kind, target_key)
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

CREATE TABLE IF NOT EXISTS candidate_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_decision_id INTEGER NOT NULL REFERENCES candidate_decisions(id) ON DELETE CASCADE,
    mining_run_id INTEGER NOT NULL REFERENCES mining_runs(id) ON DELETE CASCADE,
    reviewed_at TEXT NOT NULL,
    reviewer_type TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT NOT NULL,
    UNIQUE(candidate_decision_id, mining_run_id, reviewer_type)
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
        paths.graph_dir / "migrations",
    ):
        path.mkdir(parents=True, exist_ok=True)
    if not paths.schema_path.exists() or paths.schema_path.read_text(encoding="utf-8") != SCHEMA_SQL:
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
    conn = sqlite3.connect(paths.db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        conn.execute("PRAGMA journal_mode = WAL")
    except sqlite3.OperationalError as exc:
        if "locked" not in str(exc).lower():
            raise
    conn.executescript(SCHEMA_SQL)
    _migrate_categories(conn)
    _migrate_decision_traces(conn)
    return conn


def _migrate_categories(conn: sqlite3.Connection) -> None:
    from project_context.categories import infer_decision_category

    for table in ("candidate_decisions", "decision_versions"):
        columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if "category" not in columns:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN category TEXT NOT NULL DEFAULT 'general'")
            except sqlite3.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
        rows = conn.execute(
            f"SELECT id, decision_key, title, summary, payload_json FROM {table}"
        ).fetchall()
        for row in rows:
            payload = json.loads(row["payload_json"])
            explicit = payload.get("attrs", {}).get("category")
            category = explicit or infer_decision_category(row["decision_key"], row["title"], row["summary"])
            conn.execute(f"UPDATE {table} SET category = ? WHERE id = ?", (category, row["id"]))
    conn.commit()


def _insert_context_entity(
    conn: sqlite3.Connection,
    *,
    entity_type: str,
    entity_key: str,
    label: str,
    metadata: dict[str, Any],
) -> None:
    conn.execute(
        """
        INSERT INTO context_entities(entity_type, entity_key, label, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(entity_type, entity_key) DO UPDATE SET
            label = excluded.label,
            metadata_json = excluded.metadata_json
        """,
        (entity_type, entity_key, label, json.dumps(metadata, sort_keys=True), utc_now()),
    )


def _insert_trace_link(
    conn: sqlite3.Connection,
    *,
    trace_id: int,
    relationship: str,
    target_kind: str,
    target_key: str,
    target_label: str,
    evidence_ref: str,
    confidence: float,
    created_by: str,
) -> None:
    conn.execute(
        """
        INSERT INTO decision_trace_links(
            decision_trace_id, relationship, target_kind, target_key, target_label,
            evidence_ref, confidence, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(decision_trace_id, relationship, target_kind, target_key) DO UPDATE SET
            target_label = excluded.target_label,
            evidence_ref = excluded.evidence_ref,
            confidence = excluded.confidence,
            created_by = excluded.created_by
        """,
        (trace_id, relationship, target_kind, target_key, target_label, evidence_ref, confidence, created_by),
    )


def _migrate_decision_traces(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT
            dv.id AS decision_version_id,
            dv.decision_key,
            dv.version_no,
            dv.decision_type,
            dv.category,
            dv.title,
            dv.summary,
            dv.rationale_text,
            dv.payload_json,
            dv.validation_run_id,
            cd.event_id,
            cd.confidence,
            s.source_ref,
            s.sequence_no AS source_session_sequence,
            se.content_text
        FROM decision_versions dv
        JOIN candidate_decisions cd
          ON cd.mining_run_id = dv.validation_run_id
         AND cd.decision_key = dv.decision_key
         AND cd.status = 'validated'
        JOIN sessions s ON s.id = cd.session_id
        JOIN session_events se ON se.id = cd.event_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM decision_traces dt
            WHERE dt.decision_version_id = dv.id
        )
        ORDER BY dv.id ASC, cd.id DESC
        """
    ).fetchall()
    seen_versions: set[int] = set()
    for row in rows:
        if row["decision_version_id"] in seen_versions:
            continue
        seen_versions.add(row["decision_version_id"])
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            payload = {}
        attrs = payload.get("attrs") if isinstance(payload, dict) else {}
        attrs = attrs if isinstance(attrs, dict) else {}
        evidence_ref = f"session_event:{row['event_id']}"
        source_key = f"session:{row['source_session_sequence']}"
        run_key = f"mining_run:{row['validation_run_id']}"
        _insert_context_entity(
            conn,
            entity_type="session",
            entity_key=source_key,
            label=f"Session {row['source_session_sequence']}",
            metadata={"source_ref": row["source_ref"], "sequence_no": row["source_session_sequence"]},
        )
        _insert_context_entity(
            conn,
            entity_type="validation_run",
            entity_key=run_key,
            label=f"Mining run {row['validation_run_id']}",
            metadata={"run_id": row["validation_run_id"]},
        )
        trace_id = conn.execute(
            """
            INSERT INTO decision_traces(
                decision_version_id, decision_key, task_text, situation_text, inputs_considered_json,
                rule_or_policy, exception_or_override, precedent_used, approval_or_operator_signal,
                outcome_text, evidence_refs_json, confidence, validation_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
            """,
            (
                row["decision_version_id"],
                row["decision_key"],
                attrs.get("task", row["title"] or row["decision_key"]),
                attrs.get("situation", row["summary"]),
                json.dumps(
                    [
                        {
                            "kind": "session_event",
                            "source_ref": row["source_ref"],
                            "session_sequence": row["source_session_sequence"],
                            "event_id": row["event_id"],
                            "quote": row["content_text"],
                        }
                    ],
                    sort_keys=True,
                ),
                attrs.get("policy", f"{row['decision_type']} in {row['category']}"),
                attrs.get("exception", ""),
                attrs.get("precedent", ""),
                attrs.get("approval", "explicit agent review"),
                attrs.get("outcome", row["summary"]),
                json.dumps([evidence_ref], sort_keys=True),
                float(row["confidence"]),
                "validated",
                utc_now(),
            ),
        ).fetchone()[0]
        _insert_trace_link(
            conn,
            trace_id=trace_id,
            relationship="derived_from",
            target_kind="session",
            target_key=source_key,
            target_label=f"Session {row['source_session_sequence']}",
            evidence_ref=evidence_ref,
            confidence=1.0,
            created_by="migration",
        )
        _insert_trace_link(
            conn,
            trace_id=trace_id,
            relationship="validated_by",
            target_kind="validation_run",
            target_key=run_key,
            target_label=f"Mining run {row['validation_run_id']}",
            evidence_ref=evidence_ref,
            confidence=1.0,
            created_by="migration",
        )
        if attrs.get("applies_to"):
            _insert_trace_link(
                conn,
                trace_id=trace_id,
                relationship="applies_to",
                target_kind="surface",
                target_key=attrs["applies_to"],
                target_label=attrs["applies_to"],
                evidence_ref=evidence_ref,
                confidence=0.8,
                created_by="migration",
            )
    supersedes = conn.execute(
        """
        SELECT
            edge.from_decision_version_id,
            edge.to_decision_version_id,
            edge.relationship,
            edge.confidence,
            edge.created_by,
            dt.id AS trace_id,
            dv.decision_key,
            target.version_no AS target_version_no
        FROM supersedes_edges edge
        JOIN decision_traces dt ON dt.decision_version_id = edge.from_decision_version_id
        JOIN decision_versions dv ON dv.id = edge.from_decision_version_id
        JOIN decision_versions target ON target.id = edge.to_decision_version_id
        """
    ).fetchall()
    for row in supersedes:
        _insert_trace_link(
            conn,
            trace_id=row["trace_id"],
            relationship=row["relationship"],
            target_kind="decision_version",
            target_key=str(row["to_decision_version_id"]),
            target_label=f"{row['decision_key']} v{row['target_version_no']}",
            evidence_ref=f"decision_version:{row['from_decision_version_id']}",
            confidence=float(row["confidence"]),
            created_by=row["created_by"],
        )
    conn.commit()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def fetch_all_dicts(conn: sqlite3.Connection, query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in conn.execute(query, params)]


def insert_session_with_events(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    source_type: str,
    source_ref: str,
    started_at: str,
    ended_at: str,
    ingested_at: str,
    events: list[dict[str, Any]],
) -> tuple[int, int]:
    conn.execute("BEGIN IMMEDIATE")
    try:
        sequence_no = conn.execute("SELECT COALESCE(MAX(sequence_no), 0) + 1 FROM sessions").fetchone()[0]
        session_id = conn.execute(
            """
            INSERT INTO sessions(project_id, source_type, source_ref, started_at, ended_at, sequence_no, checksum, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, source_type, source_ref, started_at, ended_at, sequence_no, None, ingested_at),
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
    except Exception:
        conn.rollback()
        raise
    return session_id, sequence_no
