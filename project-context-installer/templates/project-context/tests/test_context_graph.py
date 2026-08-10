from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

from project_context.bootstrap import session_start
from project_context.cli import cmd_import_session, cmd_search
from project_context.db import connect, ensure_layout, insert_session_with_events, utc_now
from project_context.importers import parse_rollout_summary
from project_context.mining import (
    list_source_inventory,
    resolve_source_session,
    resolve_source_sessions,
    run_mining,
    summarize_pending_mining,
)
from project_context.retrieval import get_active_decisions, get_decision_history, get_decision_trace, get_related_decision_context, query_active_decisions
from project_context.validation import audit_active_decisions, evaluate_candidate_quality, promote_run, review_run, validate_run


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


def test_pending_mining_reports_sessions_until_candidate_checkpoint_advances(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=alpha.rule type=rule] First rule."}],
    )

    pending = summarize_pending_mining(tmp_path)
    assert pending["status"] == "pending_mining"
    assert pending["has_pending_mining"] is True
    assert pending["pending_mining_sessions"][0]["source_ref"] == "session-1.json"

    run_mining(tmp_path)
    pending = summarize_pending_mining(tmp_path)
    assert pending["status"] == "pending_validation"
    assert pending["has_pending_mining"] is False
    assert pending["pending_run"]["status"] == "mined"


def test_pending_mining_reports_unimported_codex_sessions(tmp_path: Path, monkeypatch) -> None:
    ensure_layout(tmp_path)
    sessions_dir = tmp_path / "codex-sessions"
    sessions_dir.mkdir()
    started = datetime.now(UTC) - timedelta(minutes=20)
    session_id = "raw-session-1"
    raw_session = sessions_dir / f"rollout-2026-06-21T00-00-00-{session_id}.jsonl"
    raw_session.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": started.isoformat(),
                        "type": "session_meta",
                        "payload": {
                            "id": session_id,
                            "timestamp": started.isoformat(),
                            "cwd": str(tmp_path),
                        },
                    }
                ),
                json.dumps(
                    {
                        "timestamp": (started + timedelta(minutes=1)).isoformat(),
                        "type": "response_item",
                        "payload": {"type": "message", "role": "user", "content": []},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROJECT_CONTEXT_CODEX_SESSIONS_DIR", str(sessions_dir))

    pending = summarize_pending_mining(tmp_path)

    assert pending["status"] == "source_inventory_gap"
    assert pending["has_pending_mining"] is True
    assert pending["pending_mining_count"] == 1
    assert pending["pending_mining_imported_session_count"] == 0
    assert pending["pending_mining_source_gap_count"] == 1
    assert pending["pending_mining_work_packet"] == "unimported_source_sessions"
    assert pending["context_graph_review"] == "model_backed_review_required"
    assert pending["has_source_inventory_gap"] is True
    assert pending["source_inventory_gap_count"] == 1
    assert pending["unimported_source_sessions"][0]["source_ref"] == session_id


def test_session_start_reports_source_inventory_gap(tmp_path: Path, monkeypatch) -> None:
    ensure_layout(tmp_path)
    sessions_dir = tmp_path / "codex-sessions"
    sessions_dir.mkdir()
    started = datetime.now(UTC) - timedelta(minutes=20)
    session_id = "raw-session-at-start"
    raw_session = sessions_dir / f"rollout-2026-06-21T00-00-00-{session_id}.jsonl"
    raw_session.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": started.isoformat(),
                        "type": "session_meta",
                        "payload": {
                            "id": session_id,
                            "timestamp": started.isoformat(),
                            "cwd": str(tmp_path),
                        },
                    }
                ),
                json.dumps(
                    {
                        "timestamp": (started + timedelta(minutes=1)).isoformat(),
                        "type": "response_item",
                        "payload": {"type": "message", "role": "assistant", "content": []},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROJECT_CONTEXT_CODEX_SESSIONS_DIR", str(sessions_dir))

    result = session_start(tmp_path)

    assert result["status"] == "source_inventory_gap"
    assert result["source_inventory_gap_count"] == 1
    assert result["unimported_source_sessions"][0]["source_ref"] == session_id


def test_resolve_source_session_persists_out_of_scope_decision(tmp_path: Path, monkeypatch) -> None:
    ensure_layout(tmp_path)
    sessions_dir = tmp_path / "codex-sessions"
    sessions_dir.mkdir()
    started = datetime.now(UTC) - timedelta(minutes=20)
    session_id = "control-child"
    raw_session = sessions_dir / f"rollout-2026-06-21T00-00-00-{session_id}.jsonl"
    raw_session.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": started.isoformat(),
                        "type": "session_meta",
                        "payload": {
                            "id": session_id,
                            "parent_thread_id": "parent",
                            "timestamp": started.isoformat(),
                            "cwd": str(tmp_path),
                        },
                    }
                ),
                json.dumps(
                    {
                        "timestamp": (started + timedelta(minutes=1)).isoformat(),
                        "type": "response_item",
                        "payload": {"type": "message", "role": "user", "content": []},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PROJECT_CONTEXT_CODEX_SESSIONS_DIR", str(sessions_dir))

    resolve_source_session(
        tmp_path,
        source_ref=session_id,
        resolution_status="out_of_scope_control_thread",
        reason="permission control child",
        evidence_ref="test",
    )
    inventory = list_source_inventory(tmp_path)
    pending = summarize_pending_mining(tmp_path)

    assert inventory["unimported_sessions"] == []
    assert inventory["resolved_source_sessions"][0]["source_ref"] == session_id
    assert pending["status"] == "clear"
    assert pending["source_inventory_gap_count"] == 0


def test_resolve_source_sessions_bulk_uses_one_inventory_pass(tmp_path: Path, monkeypatch) -> None:
    ensure_layout(tmp_path)
    sessions_dir = tmp_path / "codex-sessions"
    sessions_dir.mkdir()
    started = datetime.now(UTC) - timedelta(minutes=20)
    for session_id in ("child-one", "child-two"):
        raw_session = sessions_dir / f"rollout-2026-06-21T00-00-00-{session_id}.jsonl"
        raw_session.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "timestamp": started.isoformat(),
                            "type": "session_meta",
                            "payload": {
                                "id": session_id,
                                "parent_thread_id": "parent",
                                "timestamp": started.isoformat(),
                                "cwd": str(tmp_path),
                            },
                        }
                    ),
                    json.dumps(
                        {
                            "timestamp": (started + timedelta(minutes=1)).isoformat(),
                            "type": "response_item",
                            "payload": {"type": "message", "role": "user", "content": []},
                        }
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    monkeypatch.setenv("PROJECT_CONTEXT_CODEX_SESSIONS_DIR", str(sessions_dir))

    results = resolve_source_sessions(
        tmp_path,
        [
            {
                "source_ref": "child-one",
                "resolution_status": "out_of_scope_duplicate_child",
                "reason": "covered by parent",
            },
            {
                "source_ref": "child-two",
                "resolution_status": "out_of_scope_duplicate_child",
                "reason": "covered by parent",
            },
        ],
    )
    pending = summarize_pending_mining(tmp_path)

    assert [result["source_ref"] for result in results] == ["child-one", "child-two"]
    assert pending["status"] == "clear"
    assert pending["source_inventory_gap_count"] == 0
    assert len(pending["resolved_source_sessions"]) == 2


def test_session_start_requires_agent_review_before_promotion(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=graph.rule type=rule] First version."}],
    )
    result = session_start(tmp_path)
    assert result["status"] == "needs_review"
    assert result["review_candidate_ids"]
    assert "active_decisions" not in result
    assert "available_categories" not in result
    assert "task_retrieval" not in result
    assert get_active_decisions(tmp_path) == []


def test_review_run_enables_promotion_and_history(tmp_path: Path) -> None:
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
    validation = validate_run(tmp_path, run_id)
    assert validation["status"] == "needs_review"
    review = review_run(tmp_path, run_id, approved_ids=validation["review_candidate_ids"], rejected_ids=[])
    assert review["status"] == "approved"
    promote_run(tmp_path, run_id)
    active = get_active_decisions(tmp_path)
    assert len(active) == 1
    assert active[0]["summary"] == "Use memory only when the task is not trivial."
    history = get_decision_history(tmp_path, "memory.rule")
    assert [item["state"] for item in history] == ["superseded", "active"]


def test_task_query_returns_only_relevant_active_categories(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [
            {
                "timestamp": "2026-06-19T09:00:00+00:00",
                "role": "user",
                "content_text": "[decision key=ui.copy type=preference category=ui.content] Keep interface copy short.",
            },
            {
                "timestamp": "2026-06-19T09:01:00+00:00",
                "role": "user",
                "content_text": "[decision key=workflow.agent type=rule category=workflow.orchestration] Keep orchestration in the main agent.",
            },
        ],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validation = validate_run(tmp_path, run_id)
    review_run(tmp_path, run_id, approved_ids=validation["review_candidate_ids"], rejected_ids=[])
    promote_run(tmp_path, run_id)

    result = query_active_decisions(tmp_path, "Design a screen with short copy and icons")

    assert result["categories"] == ["ui.content"]
    assert [item["decision_key"] for item in result["decisions"]] == ["ui.copy"]
    assert result["decisions"][0]["source_ref"] == "session-1.json"


def test_validate_run_after_review_keeps_reviewed_statuses(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=memory.rule type=rule] Use memory at session start."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    first_validation = validate_run(tmp_path, run_id)
    assert first_validation["status"] == "needs_review"
    review_run(tmp_path, run_id, approved_ids=first_validation["review_candidate_ids"], rejected_ids=[])

    second_validation = validate_run(tmp_path, run_id)
    assert second_validation["status"] == "approved"
    assert second_validation["review_candidate_ids"] == []
    assert second_validation["validated_candidate_ids"] == first_validation["review_candidate_ids"]

    promote_run(tmp_path, run_id)
    active = get_active_decisions(tmp_path)
    assert len(active) == 1
    assert active[0]["decision_key"] == "memory.rule"

    after_promotion = validate_run(tmp_path, run_id)
    assert after_promotion["status"] == "promoted"
    assert after_promotion["run_status"] == "promoted"
    assert summarize_pending_mining(tmp_path)["status"] == "clear"


def test_search_returns_active_decision_fields(tmp_path: Path, capsys) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=search.rule type=rule] Use searchable session bootstrap."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validation = validate_run(tmp_path, run_id)
    review_run(tmp_path, run_id, approved_ids=validation["review_candidate_ids"], rejected_ids=[])
    promote_run(tmp_path, run_id)

    cmd_search(argparse.Namespace(root=str(tmp_path), query="searchable"))

    payload = json.loads(capsys.readouterr().out)
    assert payload == [
        {
            "decision_key": "search.rule",
            "decision_version_id": 1,
            "summary": "Use searchable session bootstrap.",
            "title": "search.rule",
        }
    ]


def test_search_escapes_punctuation_and_hyphenated_terms(tmp_path: Path, capsys) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [
            {
                "timestamp": "2026-06-19T09:00:00+00:00",
                "role": "user",
                "content_text": "[decision key=design.rule type=rule] DESIGN.md keeps auto-place user-confirm product doctrine.",
            }
        ],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validation = validate_run(tmp_path, run_id)
    review_run(tmp_path, run_id, approved_ids=validation["review_candidate_ids"], rejected_ids=[])
    promote_run(tmp_path, run_id)

    cmd_search(argparse.Namespace(root=str(tmp_path), query="DESIGN.md auto-place user-confirm Reflect -> Place"))

    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["decision_key"] == "design.rule"


def test_import_session_accepts_jsonl_event_stream(tmp_path: Path, capsys) -> None:
    ensure_layout(tmp_path)
    session_path = tmp_path / "session.jsonl"
    session_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-06-19T09:00:00+00:00",
                        "type": "session_meta",
                        "payload": {"id": "jsonl-session"},
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-06-19T09:01:00+00:00",
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [{"type": "output_text", "text": "Imported from JSONL."}],
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    cmd_import_session(
        argparse.Namespace(
            root=str(tmp_path),
            path=str(session_path),
            project_id="test",
            source_type="codex_jsonl",
            source_ref="jsonl-session",
            started_at=None,
            ended_at=None,
        )
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "imported"
    assert payload["event_count"] == 2
    conn = connect(tmp_path)
    row = conn.execute("SELECT source_ref, source_type FROM sessions").fetchone()
    assert row["source_ref"] == "jsonl-session"
    assert row["source_type"] == "codex_jsonl"


def test_rejected_run_does_not_affect_trusted_retrieval(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=owner.rule type=rule] Codex owns Codex work."}],
    )
    first_run = run_mining(tmp_path)["run_id"]
    first_validation = validate_run(tmp_path, first_run)
    review_run(tmp_path, first_run, approved_ids=first_validation["review_candidate_ids"], rejected_ids=[])
    promote_run(tmp_path, first_run)

    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T12:00:00+00:00", "role": "user", "content_text": "[decision key=broken.rule type=rule] This should fail validation."}],
    )
    second_run = run_mining(tmp_path)["run_id"]
    conn = connect(tmp_path)
    conn.execute(
        "DELETE FROM evidence_spans WHERE source_ref = (SELECT CAST(event_id AS TEXT) FROM candidate_decisions WHERE mining_run_id = ? LIMIT 1)",
        (second_run,),
    )
    conn.commit()
    result = validate_run(tmp_path, second_run)
    assert result["status"] == "rejected"
    active = get_active_decisions(tmp_path)
    assert len(active) == 1
    assert active[0]["decision_key"] == "owner.rule"


def test_promoted_decision_has_trace_and_related_context(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [
            {
                "timestamp": "2026-06-19T09:00:00+00:00",
                "role": "user",
                "content_text": (
                    "[decision key=trace.rule type=rule category=workflow.context "
                    "policy=agent-query applies_to=docs/workflows/context-graph.md] "
                    "Agents should query durable decisions before non-trivial work."
                ),
            }
        ],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validation = validate_run(tmp_path, run_id)
    review_run(tmp_path, run_id, approved_ids=validation["review_candidate_ids"], rejected_ids=[])
    promote_run(tmp_path, run_id)

    trace = get_decision_trace(tmp_path, "trace.rule")
    assert trace is not None
    assert trace["rule_or_policy"] == "agent-query"
    assert trace["approval_or_operator_signal"] == "explicit agent review"
    assert trace["inputs_considered"][0]["kind"] == "session_event"
    relationships = {link["relationship"] for link in trace["links"]}
    assert {"derived_from", "validated_by", "applies_to"} <= relationships

    related = get_related_decision_context(tmp_path, "trace.rule")
    assert related is not None
    assert any(entity["entity_type"] == "session" for entity in related["entities"])
    assert any(link["target_key"] == "docs/workflows/context-graph.md" for link in related["trace_links"])


def test_audit_active_removes_unreviewed_legacy_entries(tmp_path: Path) -> None:
    ensure_layout(tmp_path)
    create_session(
        tmp_path,
        [{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": "[decision key=legacy.rule type=rule] Legacy active rule."}],
    )
    run_id = run_mining(tmp_path)["run_id"]
    validation = validate_run(tmp_path, run_id)
    review_run(tmp_path, run_id, approved_ids=validation["review_candidate_ids"], rejected_ids=[])
    promote_run(tmp_path, run_id)

    conn = connect(tmp_path)
    conn.execute("DELETE FROM candidate_reviews WHERE mining_run_id = ?", (run_id,))
    conn.commit()

    audit = audit_active_decisions(tmp_path)
    assert audit["removed_count"] == 1
    assert get_active_decisions(tmp_path) == []


def test_parse_rollout_summary_extracts_preference_and_reusable_lines(tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    summary.write_text(
        "\n".join(
            [
                "thread_id: abc",
                "updated_at: 2026-06-18T08:37:34+00:00",
                "",
                "Preference signals:",
                '- The user said "operate as orchestrator" -> keep the main thread focused on routing and durable edits.',
                "",
                "Key steps:",
                "- This line should not be imported.",
                "",
                "Reusable knowledge:",
                "- When a workflow may become noisy or repetitive, explicitly document whether to use a pinned subagent or verifier.",
            ]
        ),
        encoding="utf-8",
    )
    parsed = parse_rollout_summary(summary)
    assert parsed["metadata"]["thread_id"] == "abc"
    assert len(parsed["events"]) == 2
    assert "keep the main thread focused on routing and durable edits." in parsed["events"][0]["content_text"]
    assert "workflow may become noisy or repetitive" in parsed["events"][1]["content_text"]
    assert "The user said" not in parsed["events"][0]["content_text"]


def test_parallel_session_inserts_allocate_unique_sequence_numbers(tmp_path: Path) -> None:
    ensure_layout(tmp_path)

    def insert_one(content: str) -> int:
        conn = connect(tmp_path)
        _, sequence_no = insert_session_with_events(
            conn,
            project_id="test",
            source_type="json",
            source_ref=content,
            started_at="2026-06-19T09:00:00+00:00",
            ended_at="2026-06-19T09:00:00+00:00",
            ingested_at=utc_now(),
            events=[{"timestamp": "2026-06-19T09:00:00+00:00", "role": "user", "content_text": content}],
        )
        conn.close()
        return sequence_no

    with ThreadPoolExecutor(max_workers=2) as executor:
        sequences = sorted(executor.map(insert_one, ["a", "b"]))
    assert sequences == [1, 2]


def test_evaluate_candidate_quality_requires_agent_review() -> None:
    valid, reason = evaluate_candidate_quality(
        "reusable_knowledge.example",
        "rule",
        "The design system should use warm neutral canvas.",
    )
    assert not valid
    assert "agent review" in reason


def test_evaluate_candidate_quality_rejects_meta_system() -> None:
    valid, reason = evaluate_candidate_quality(
        "reusable_knowledge.beta.validation",
        "rule",
        "beta validation must verify source-of-truth coverage independently.",
    )
    assert not valid
    assert "meta-system" in reason
