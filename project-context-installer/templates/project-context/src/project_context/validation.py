from __future__ import annotations

import json
from pathlib import Path

from project_context.categories import infer_decision_category
from project_context.db import connect, fetch_all_dicts, read_json, utc_now, write_json


REJECTED_CATEGORIES = {"agent.instructions", "workflow.context", "workflow.orchestration"}

META_SYSTEM_KEYWORDS = frozenset({
    "agents.md", "control owner", "subagent", "beta-feature", "beta workflow",
    "beta validation", "beta exit", "context-graph", "context graph",
    "mining", "promotion", "promote", "resume-session", "save-session",
    "session-start", "hooks", "operator-intent", "beta run", "beta registry",
    "satisfied run", "graduation", "sidecar", "verifier agent",
})


def _is_meta_system_content(category: str, summary: str) -> bool:
    if category in REJECTED_CATEGORIES:
        return True
    lower = summary.lower()
    return any(kw in lower for kw in META_SYSTEM_KEYWORDS)


def evaluate_candidate_quality(decision_key: str, decision_type: str, summary: str) -> tuple[bool, str]:
    category = infer_decision_category(decision_key, "", summary)
    if _is_meta_system_content(category, summary):
        return False, "meta-system content — belongs in AGENTS.md, skills, or workflow docs, not the decision graph"
    return False, "candidate requires explicit agent review before promotion"


def list_review_candidates(root: Path, run_id: int) -> list[dict]:
    conn = connect(root)
    return _list_review_candidates(conn, run_id)


def _list_review_candidates(conn, run_id: int) -> list[dict]:
    return fetch_all_dicts(
        conn,
        """
        SELECT id, decision_key, decision_type, title, summary, rationale_text, status
        FROM candidate_decisions
        WHERE mining_run_id = ?
          AND status IN ('needs_review', 'validated')
          AND NOT EXISTS (
              SELECT 1
              FROM candidate_reviews cr
              WHERE cr.candidate_decision_id = candidate_decisions.id
                AND cr.mining_run_id = candidate_decisions.mining_run_id
                AND cr.status IN ('approved', 'rejected')
          )
        ORDER BY id ASC
        """,
        (run_id,),
    )


def _latest_validation_status(conn, run_id: int) -> str | None:
    row = conn.execute(
        """
        SELECT status
        FROM validation_reviews
        WHERE mining_run_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (run_id,),
    ).fetchone()
    return None if row is None else row["status"]


def _update_run_status(conn, run_id: int) -> str:
    counts = conn.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'validated' THEN 1 ELSE 0 END) AS validated_count,
            SUM(CASE WHEN status = 'needs_review' THEN 1 ELSE 0 END) AS needs_review_count,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected_count
        FROM candidate_decisions
        WHERE mining_run_id = ?
        """,
        (run_id,),
    ).fetchone()
    validated_count = counts["validated_count"] or 0
    needs_review_count = counts["needs_review_count"] or 0
    rejected_count = counts["rejected_count"] or 0

    active_validated_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM candidate_decisions cd
        JOIN active_decisions ad ON ad.decision_key = cd.decision_key
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        WHERE cd.mining_run_id = ?
          AND cd.status = 'validated'
          AND dv.validation_run_id = ?
        """,
        (run_id, run_id),
    ).fetchone()[0]

    if validated_count and active_validated_count == validated_count and not needs_review_count:
        run_status = "promoted"
    elif needs_review_count:
        run_status = "review_required"
    elif validated_count and rejected_count:
        run_status = "validated_partial"
    elif validated_count:
        run_status = "validated_approved"
    else:
        run_status = "rejected"

    conn.execute("UPDATE mining_runs SET status = ? WHERE id = ?", (run_status, run_id))
    return run_status


def validate_run(root: Path, run_id: int, reviewer_type: str = "main_agent") -> dict:
    conn = connect(root)
    candidates = fetch_all_dicts(
        conn,
        """
        SELECT cd.id, cd.event_id, cd.decision_key, cd.decision_type, cd.summary
        FROM candidate_decisions cd
        WHERE cd.mining_run_id = ?
        ORDER BY cd.id ASC
        """,
        (run_id,),
    )
    failures: list[str] = []
    review_required: list[int] = []
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
        valid, reason = evaluate_candidate_quality(
            candidate["decision_key"], candidate["decision_type"], candidate["summary"]
        )
        if not valid and "meta-system" in reason:
            failures.append(f"candidate {candidate['id']} rejected: {reason}")
            conn.execute("UPDATE candidate_decisions SET status = 'rejected' WHERE id = ?", (candidate["id"],))
            continue
        review = conn.execute(
            """
            SELECT status
            FROM candidate_reviews
            WHERE candidate_decision_id = ?
              AND mining_run_id = ?
              AND status IN ('approved', 'rejected')
            ORDER BY id DESC
            LIMIT 1
            """,
            (candidate["id"], run_id),
        ).fetchone()
        if review is not None and review["status"] == "approved":
            conn.execute("UPDATE candidate_decisions SET status = 'validated' WHERE id = ?", (candidate["id"],))
            validated_ids.append(candidate["id"])
            continue
        if review is not None and review["status"] == "rejected":
            conn.execute("UPDATE candidate_decisions SET status = 'rejected' WHERE id = ?", (candidate["id"],))
            continue

        conn.execute("UPDATE candidate_decisions SET status = 'needs_review' WHERE id = ?", (candidate["id"],))
        review_required.append(candidate["id"])

    run_status = _update_run_status(conn, run_id)
    if run_status == "review_required":
        overall_status = "needs_review"
    elif run_status == "validated_partial":
        overall_status = "partial"
    elif run_status == "validated_approved":
        overall_status = "approved"
    elif run_status == "promoted":
        overall_status = "promoted"
    else:
        overall_status = "rejected"
    notes: list[str] = []
    if failures:
        notes.extend(failures)
    if review_required:
        notes.append(f"{len(review_required)} candidates require explicit review before promotion")
    if not notes:
        notes.append("validated")
    conn.execute(
        """
        INSERT INTO validation_reviews(mining_run_id, reviewed_at, reviewer_type, status, review_notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (run_id, utc_now(), reviewer_type, overall_status, "\n".join(notes)),
    )
    conn.commit()
    return {
        "status": overall_status,
        "run_status": run_status,
        "validated_candidate_ids": validated_ids,
        "review_candidate_ids": review_required,
        "failures": failures,
    }


def review_run(
    root: Path,
    run_id: int,
    *,
    approved_ids: list[int],
    rejected_ids: list[int],
    reviewer_type: str = "main_agent",
) -> dict:
    conn = connect(root)
    pending = {
        row["id"]: row
        for row in fetch_all_dicts(
            conn,
            """
            SELECT id, decision_key, summary
            FROM candidate_decisions
            WHERE mining_run_id = ?
              AND status IN ('needs_review', 'validated')
              AND NOT EXISTS (
                  SELECT 1
                  FROM candidate_reviews cr
                  WHERE cr.candidate_decision_id = candidate_decisions.id
                    AND cr.mining_run_id = candidate_decisions.mining_run_id
                    AND cr.status IN ('approved', 'rejected')
              )
            ORDER BY id ASC
            """,
            (run_id,),
        )
    }
    overlap = set(approved_ids) & set(rejected_ids)
    if overlap:
        raise ValueError(f"candidate ids cannot be both approved and rejected: {sorted(overlap)}")

    unknown_ids = (set(approved_ids) | set(rejected_ids)) - set(pending)
    if unknown_ids:
        raise ValueError(f"candidate ids are not pending review for run {run_id}: {sorted(unknown_ids)}")

    for candidate_id in approved_ids:
        conn.execute("UPDATE candidate_decisions SET status = 'validated' WHERE id = ?", (candidate_id,))
        conn.execute(
            """
            INSERT INTO candidate_reviews(candidate_decision_id, mining_run_id, reviewed_at, reviewer_type, status, notes)
            VALUES (?, ?, ?, ?, 'approved', ?)
            ON CONFLICT(candidate_decision_id, mining_run_id, reviewer_type) DO UPDATE SET
                reviewed_at = excluded.reviewed_at,
                status = excluded.status,
                notes = excluded.notes
            """,
            (candidate_id, run_id, utc_now(), reviewer_type, pending[candidate_id]["summary"]),
        )

    for candidate_id in rejected_ids:
        conn.execute("UPDATE candidate_decisions SET status = 'rejected' WHERE id = ?", (candidate_id,))
        conn.execute(
            """
            INSERT INTO candidate_reviews(candidate_decision_id, mining_run_id, reviewed_at, reviewer_type, status, notes)
            VALUES (?, ?, ?, ?, 'rejected', ?)
            ON CONFLICT(candidate_decision_id, mining_run_id, reviewer_type) DO UPDATE SET
                reviewed_at = excluded.reviewed_at,
                status = excluded.status,
                notes = excluded.notes
            """,
            (candidate_id, run_id, utc_now(), reviewer_type, pending[candidate_id]["summary"]),
        )

    remaining = _list_review_candidates(conn, run_id)
    run_status = _update_run_status(conn, run_id)
    if remaining:
        status = "needs_review"
    elif approved_ids and rejected_ids:
        status = "partial"
    elif approved_ids:
        status = "approved"
    elif rejected_ids:
        status = "rejected"
    else:
        status = _latest_validation_status(conn, run_id) or "needs_review"

    conn.execute(
        """
        INSERT INTO validation_reviews(mining_run_id, reviewed_at, reviewer_type, status, review_notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            run_id,
            utc_now(),
            reviewer_type,
            status,
            f"approved={sorted(approved_ids)} rejected={sorted(rejected_ids)} remaining={len(remaining)}",
        ),
    )
    conn.commit()
    return {
        "status": status,
        "run_status": run_status,
        "approved_ids": sorted(approved_ids),
        "rejected_ids": sorted(rejected_ids),
        "remaining_review_candidates": remaining,
    }


def _json_list(value: object) -> str:
    if value is None:
        return "[]"
    if isinstance(value, list):
        return json.dumps(value, sort_keys=True)
    return json.dumps([str(value)], sort_keys=True)


def _payload_attrs(candidate: dict) -> dict:
    try:
        payload = json.loads(candidate["payload_json"])
    except json.JSONDecodeError:
        return {}
    attrs = payload.get("attrs")
    return attrs if isinstance(attrs, dict) else {}


def _upsert_entity(conn, *, entity_type: str, entity_key: str, label: str, metadata: dict) -> None:
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
    conn,
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


def _create_decision_trace(conn, *, decision_version_id: int, candidate: dict, run_id: int) -> int:
    attrs = _payload_attrs(candidate)
    evidence_ref = f"session_event:{candidate['event_id']}"
    source_key = f"session:{candidate['source_session_sequence']}"
    run_key = f"mining_run:{run_id}"
    _upsert_entity(
        conn,
        entity_type="session",
        entity_key=source_key,
        label=f"Session {candidate['source_session_sequence']}",
        metadata={"source_ref": candidate["source_ref"], "sequence_no": candidate["source_session_sequence"]},
    )
    _upsert_entity(
        conn,
        entity_type="validation_run",
        entity_key=run_key,
        label=f"Mining run {run_id}",
        metadata={"run_id": run_id},
    )
    trace_id = conn.execute(
        """
        INSERT INTO decision_traces(
            decision_version_id, decision_key, task_text, situation_text, inputs_considered_json,
            rule_or_policy, exception_or_override, precedent_used, approval_or_operator_signal,
            outcome_text, evidence_refs_json, confidence, validation_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(decision_version_id) DO UPDATE SET
            decision_key = excluded.decision_key,
            task_text = excluded.task_text,
            situation_text = excluded.situation_text,
            inputs_considered_json = excluded.inputs_considered_json,
            rule_or_policy = excluded.rule_or_policy,
            exception_or_override = excluded.exception_or_override,
            precedent_used = excluded.precedent_used,
            approval_or_operator_signal = excluded.approval_or_operator_signal,
            outcome_text = excluded.outcome_text,
            evidence_refs_json = excluded.evidence_refs_json,
            confidence = excluded.confidence,
            validation_status = excluded.validation_status,
            created_at = excluded.created_at
        RETURNING id
        """,
        (
            decision_version_id,
            candidate["decision_key"],
            attrs.get("task", candidate["title"] or candidate["decision_key"]),
            attrs.get("situation", candidate["summary"]),
            _json_list(
                [
                    {
                        "kind": "session_event",
                        "source_ref": candidate["source_ref"],
                        "session_sequence": candidate["source_session_sequence"],
                        "event_id": candidate["event_id"],
                        "quote": candidate["content_text"],
                    }
                ]
            ),
            attrs.get("policy", f"{candidate['decision_type']} in {candidate['category']}"),
            attrs.get("exception", ""),
            attrs.get("precedent", ""),
            attrs.get("approval", "explicit agent review"),
            attrs.get("outcome", candidate["summary"]),
            _json_list([evidence_ref]),
            float(candidate["confidence"]),
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
        target_label=f"Session {candidate['source_session_sequence']}",
        evidence_ref=evidence_ref,
        confidence=1.0,
        created_by="promote_run",
    )
    _insert_trace_link(
        conn,
        trace_id=trace_id,
        relationship="validated_by",
        target_kind="validation_run",
        target_key=run_key,
        target_label=f"Mining run {run_id}",
        evidence_ref=evidence_ref,
        confidence=1.0,
        created_by="promote_run",
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
            created_by="promote_run",
        )
    return trace_id


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
    if review is None:
        raise RuntimeError("run must be validated before promotion")
    if review["status"] == "needs_review":
        raise RuntimeError("run still has candidates pending explicit review")
    if review["status"] == "rejected":
        raise RuntimeError("run did not pass validation")

    candidates = fetch_all_dicts(
        conn,
        """
        SELECT cd.*, s.started_at, s.source_ref, s.sequence_no AS source_session_sequence, se.content_text
        FROM candidate_decisions cd
        JOIN sessions s ON s.id = cd.session_id
        JOIN session_events se ON se.id = cd.event_id
        WHERE cd.mining_run_id = ? AND cd.status = 'validated'
        ORDER BY cd.id ASC
        """,
        (run_id,),
    )
    latest_sequence = conn.execute(
        """
        SELECT to_session_sequence
        FROM mining_runs
        WHERE id = ?
        """,
        (run_id,),
    ).fetchone()[0]

    promoted = 0
    for candidate in candidates:
        current = conn.execute(
            """
            SELECT dv.id, dv.version_no
            FROM active_decisions ad
            JOIN decision_versions dv ON dv.id = ad.decision_version_id
            WHERE ad.decision_key = ?
            """,
            (candidate["decision_key"],),
        ).fetchone()
        next_version = 1 if current is None else current["version_no"] + 1
        new_id = conn.execute(
            """
            INSERT INTO decision_versions(
                decision_key, version_no, state, decision_type, category, title, summary,
                rationale_text, payload_json, effective_at, validated_at, validation_run_id
            ) VALUES (?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate["decision_key"],
                next_version,
                candidate["decision_type"],
                candidate["category"],
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
            conn.execute("UPDATE decision_versions SET state = 'superseded' WHERE id = ?", (current["id"],))
        trace_id = _create_decision_trace(conn, decision_version_id=new_id, candidate=candidate, run_id=run_id)
        if current is not None:
            _insert_trace_link(
                conn,
                trace_id=trace_id,
                relationship="supersedes",
                target_kind="decision_version",
                target_key=str(current["id"]),
                target_label=f"{candidate['decision_key']} v{current['version_no']}",
                evidence_ref=f"session_event:{candidate['event_id']}",
                confidence=1.0,
                created_by="promote_run",
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
    checkpoints = read_json(checkpoints_path)
    checkpoints["last_promoted_sequence"] = max(checkpoints.get("last_promoted_sequence", 0), latest_sequence)
    write_json(checkpoints_path, checkpoints)
    write_json(latest_validated_run_path, {"run_id": run_id})
    conn.execute("UPDATE mining_runs SET status = 'promoted' WHERE id = ?", (run_id,))
    conn.commit()
    return {"status": "promoted", "run_id": run_id, "promoted_count": promoted}


def audit_active_decisions(root: Path) -> dict:
    conn = connect(root)
    active = fetch_all_dicts(
        conn,
        """
        SELECT ad.decision_key, dv.id AS decision_version_id, dv.validation_run_id
        FROM active_decisions ad
        JOIN decision_versions dv ON dv.id = ad.decision_version_id
        ORDER BY ad.decision_key ASC
        """,
    )
    removed: list[str] = []
    for decision in active:
        approved_review_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM candidate_reviews cr
            JOIN candidate_decisions cd ON cd.id = cr.candidate_decision_id
            WHERE cr.mining_run_id = ?
              AND cd.decision_key = ?
              AND cr.status = 'approved'
            """,
            (decision["validation_run_id"], decision["decision_key"]),
        ).fetchone()[0]
        if approved_review_count > 0:
            continue
        conn.execute("DELETE FROM active_decisions WHERE decision_key = ?", (decision["decision_key"],))
        conn.execute("UPDATE decision_versions SET state = 'archived' WHERE id = ?", (decision["decision_version_id"],))
        removed.append(decision["decision_key"])
    conn.commit()
    return {"status": "audited", "removed_count": len(removed), "removed_decision_keys": removed}
