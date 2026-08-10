from __future__ import annotations

import json
from pathlib import Path
import re

from project_context.categories import normalize_category, text_categories
from project_context.db import connect, fetch_all_dicts, row_to_dict


QUERY_TOKEN_RE = re.compile(r"[a-z0-9_.-]{3,}")
QUERY_STOP_WORDS = {"and", "the", "for", "with", "this", "that", "from", "into", "when", "what", "should"}


def get_active_decisions(root: Path) -> list[dict]:
    conn = connect(root)
    return fetch_all_dicts(
        conn,
        """
        SELECT
            dv.id AS decision_version_id,
            dv.decision_key,
            dv.decision_type,
            dv.category,
            dv.title,
            dv.summary,
            dv.rationale_text,
            dv.state,
            dv.validated_at,
            ad.activated_at,
            (
                SELECT s.source_ref
                FROM candidate_decisions cd
                JOIN sessions s ON s.id = cd.session_id
                WHERE cd.mining_run_id = dv.validation_run_id
                  AND cd.decision_key = dv.decision_key
                  AND cd.status = 'validated'
                ORDER BY cd.id DESC
                LIMIT 1
            ) AS source_ref,
            (
                SELECT s.sequence_no
                FROM candidate_decisions cd
                JOIN sessions s ON s.id = cd.session_id
                WHERE cd.mining_run_id = dv.validation_run_id
                  AND cd.decision_key = dv.decision_key
                  AND cd.status = 'validated'
                ORDER BY cd.id DESC
                LIMIT 1
            ) AS source_session_sequence
        FROM active_decisions ad
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        ORDER BY dv.decision_key ASC
        """
    )


def get_active_categories(root: Path) -> list[dict]:
    conn = connect(root)
    return fetch_all_dicts(
        conn,
        """
        SELECT dv.category, COUNT(*) AS active_decision_count
        FROM active_decisions ad
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        GROUP BY dv.category
        ORDER BY dv.category
        """,
    )


def query_active_decisions(
    root: Path,
    task: str,
    *,
    categories: list[str] | None = None,
    limit: int = 8,
) -> dict:
    requested_categories = [normalize_category(value) for value in categories or []]
    inferred_categories = [] if requested_categories else text_categories(task)
    rows = get_active_decisions(root)
    active_categories = {row["category"] for row in rows}
    selected_categories = [
        value
        for value in (requested_categories or inferred_categories)
        if value != "general" and value in active_categories
    ]
    task_tokens = {
        token
        for token in QUERY_TOKEN_RE.findall(task.lower())
        if token not in QUERY_STOP_WORDS
    }
    ranked = []
    for row in rows:
        row_tokens = set(
            QUERY_TOKEN_RE.findall(
                f"{row['decision_key']} {row['title']} {row['summary']} {row['rationale_text']}".lower()
            )
        )
        overlap = len(task_tokens & row_tokens)
        category_match = row["category"] in selected_categories
        if selected_categories and not category_match:
            continue
        if not selected_categories and overlap == 0:
            continue
        ranked.append(
            {
                **row,
                "relevance_score": (100 if category_match else 0) + overlap,
                "match_reason": f"category:{row['category']}" if category_match else f"terms:{overlap}",
            }
        )
    ranked.sort(key=lambda row: (-row["relevance_score"], row["decision_key"]))
    return {
        "task": task,
        "categories": selected_categories,
        "inferred_categories": inferred_categories,
        "decision_count": min(len(ranked), max(0, limit)),
        "decisions": ranked[: max(0, limit)],
    }


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
    payload["trace"] = get_decision_trace(root, decision_key)
    return payload


def _decode_json_list(value: str | None) -> list:
    if not value:
        return []
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def get_decision_trace(root: Path, decision_key: str) -> dict | None:
    conn = connect(root)
    row = conn.execute(
        """
        SELECT
            dt.*,
            dv.version_no,
            dv.state,
            dv.category,
            dv.decision_type,
            dv.summary,
            dv.rationale_text,
            dv.validation_run_id,
            ad.activated_at
        FROM active_decisions ad
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        JOIN decision_traces dt ON dt.decision_version_id = dv.id
        WHERE dv.decision_key = ?
        """,
        (decision_key,),
    ).fetchone()
    if row is None:
        return None
    trace = row_to_dict(row)
    trace["inputs_considered"] = _decode_json_list(trace.pop("inputs_considered_json", "[]"))
    trace["evidence_refs"] = _decode_json_list(trace.pop("evidence_refs_json", "[]"))
    trace["links"] = fetch_all_dicts(
        conn,
        """
        SELECT relationship, target_kind, target_key, target_label, evidence_ref, confidence, created_by
        FROM decision_trace_links
        WHERE decision_trace_id = ?
        ORDER BY relationship ASC, target_kind ASC, target_label ASC
        """,
        (trace["id"],),
    )
    return trace


def get_related_decision_context(root: Path, decision_key: str) -> dict | None:
    trace = get_decision_trace(root, decision_key)
    if trace is None:
        return None
    conn = connect(root)
    supersedes = fetch_all_dicts(
        conn,
        """
        SELECT
            edge.relationship,
            source.decision_key AS from_decision_key,
            source.version_no AS from_version_no,
            target.decision_key AS to_decision_key,
            target.version_no AS to_version_no,
            edge.confidence,
            edge.created_by
        FROM supersedes_edges edge
        JOIN decision_versions source ON source.id = edge.from_decision_version_id
        JOIN decision_versions target ON target.id = edge.to_decision_version_id
        WHERE source.decision_key = ? OR target.decision_key = ?
        ORDER BY edge.id ASC
        """,
        (decision_key, decision_key),
    )
    entities = fetch_all_dicts(
        conn,
        """
        SELECT e.entity_type, e.entity_key, e.label, e.metadata_json
        FROM decision_trace_links link
        JOIN context_entities e
          ON e.entity_type = link.target_kind
         AND e.entity_key = link.target_key
        WHERE link.decision_trace_id = ?
        ORDER BY e.entity_type ASC, e.label ASC
        """,
        (trace["id"],),
    )
    for entity in entities:
        try:
            entity["metadata"] = json.loads(entity.pop("metadata_json"))
        except json.JSONDecodeError:
            entity["metadata"] = {}
    return {
        "decision_key": decision_key,
        "trace_links": trace["links"],
        "supersedes_edges": supersedes,
        "entities": entities,
    }
