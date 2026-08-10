from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from project_context.bootstrap import session_start
from project_context.db import build_paths, connect, ensure_layout, fetch_all_dicts, insert_session_with_events, utc_now
from project_context.importers import parse_rollout_summary
from project_context.mining import (
    list_source_inventory,
    list_unmined_sessions,
    resolve_source_session,
    resolve_source_sessions,
    run_mining,
    summarize_pending_mining,
)
from project_context.retrieval import (
    explain_decision,
    get_active_categories,
    get_active_decisions,
    get_decision_history,
    get_decision_trace,
    get_related_decision_context,
    query_active_decisions,
)
from project_context.validation import audit_active_decisions, list_review_candidates, promote_run, review_run, validate_run

SEARCH_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _extract_message_text(payload: dict) -> str:
    content = payload.get("content")
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
        if chunks:
            return "\n".join(chunks)
    text = payload.get("text")
    if isinstance(text, str):
        return text
    return ""


def _normalize_session_event(event: dict) -> dict:
    if "content_text" in event:
        return event
    event_type = event.get("type", "message")
    payload = event.get("payload")
    normalized = {
        "timestamp": event.get("timestamp"),
        "event_type": event_type,
        "role": event.get("role", "unknown"),
        "content_text": "",
        "artifact_ref": event.get("artifact_ref"),
    }
    if isinstance(payload, dict):
        normalized["role"] = payload.get("role", normalized["role"])
        normalized["content_text"] = _extract_message_text(payload)
    if event_type == "session_meta":
        normalized["role"] = "system"
    return normalized


def _load_session_events(session_path: Path) -> list[dict]:
    raw = session_path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            payload.append(json.loads(line))
    if not isinstance(payload, list):
        raise SystemExit("import-session expects a JSON array or JSONL event stream")
    return [_normalize_session_event(event) for event in payload]


def _fts_match_query(raw_query: str) -> str:
    tokens = SEARCH_TOKEN_RE.findall(raw_query)
    if not tokens:
        return '"__project_context_no_match__"'
    return " OR ".join(f'"{token}"' for token in tokens)


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
    session_path = Path(args.path).resolve()
    events = _load_session_events(session_path)
    started_at = args.started_at or events[0].get("timestamp") or utc_now()
    ended_at = args.ended_at or events[-1].get("timestamp") or started_at
    conn = connect(root)
    session_id, sequence_no = insert_session_with_events(
        conn,
        project_id=args.project_id,
        source_type=args.source_type,
        source_ref=args.source_ref or session_path.name,
        started_at=started_at,
        ended_at=ended_at,
        ingested_at=utc_now(),
        events=events,
    )
    _print({"status": "imported", "session_id": session_id, "sequence_no": sequence_no, "event_count": len(events)})


def _import_events(
    root: Path,
    events: list[dict],
    *,
    project_id: str,
    source_type: str,
    source_ref: str,
    started_at: str | None = None,
    ended_at: str | None = None,
) -> dict:
    conn = connect(root)
    started = started_at or events[0].get("timestamp") or utc_now()
    ended = ended_at or events[-1].get("timestamp") or started
    session_id, sequence_no = insert_session_with_events(
        conn,
        project_id=project_id,
        source_type=source_type,
        source_ref=source_ref,
        started_at=started,
        ended_at=ended,
        ingested_at=utc_now(),
        events=events,
    )
    return {"status": "imported", "session_id": session_id, "sequence_no": sequence_no, "event_count": len(events)}


def cmd_import_rollout_summary(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    summary_path = Path(args.path).resolve()
    parsed = parse_rollout_summary(summary_path)
    if not parsed["events"]:
        raise SystemExit(f"no decision-like bullets found in {summary_path}")
    metadata = parsed["metadata"]
    source_ref = args.source_ref or metadata.get("thread_id") or summary_path.name
    result = _import_events(
        root,
        parsed["events"],
        project_id=args.project_id,
        source_type="rollout_summary",
        source_ref=source_ref,
        started_at=metadata.get("updated_at"),
        ended_at=metadata.get("updated_at"),
    )
    result["imported_from"] = str(summary_path)
    result["metadata"] = metadata
    _print(result)


def cmd_scan_unmined(args: argparse.Namespace) -> None:
    _print(list_unmined_sessions(Path(args.root).resolve()))


def cmd_pending_mining(args: argparse.Namespace) -> None:
    _print(summarize_pending_mining(Path(args.root).resolve()))


def cmd_source_inventory(args: argparse.Namespace) -> None:
    _print(list_source_inventory(Path(args.root).resolve()))


def cmd_resolve_source(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(
        resolve_source_session(
            root,
            source_ref=args.source_ref,
            resolution_status=args.status,
            reason=args.reason,
            evidence_ref=args.evidence_ref,
            resolver_type=args.resolver_type,
        )
    )


def cmd_resolve_sources(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("resolve-sources expects a JSON array")
    _print(resolve_source_sessions(root, payload, resolver_type=args.resolver_type))


def cmd_mine(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(run_mining(root, from_sequence=args.from_sequence, to_sequence=args.to_sequence))


def cmd_validate(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(validate_run(root, args.run_id))


def cmd_review_queue(args: argparse.Namespace) -> None:
    _print({"run_id": args.run_id, "candidates": list_review_candidates(Path(args.root).resolve(), args.run_id)})


def cmd_review_run(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    approved_ids = [int(value) for value in args.approve]
    rejected_ids = [int(value) for value in args.reject]
    result = review_run(
            root,
            args.run_id,
            approved_ids=approved_ids,
            rejected_ids=rejected_ids,
            reviewer_type=args.reviewer_type,
    )
    _print(result)


def cmd_promote(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(promote_run(root, args.run_id))


def cmd_active(args: argparse.Namespace) -> None:
    _print(get_active_decisions(Path(args.root).resolve()))


def cmd_categories(args: argparse.Namespace) -> None:
    _print(get_active_categories(Path(args.root).resolve()))


def cmd_query(args: argparse.Namespace) -> None:
    _print(
        query_active_decisions(
            Path(args.root).resolve(),
            args.task,
            categories=args.category,
            limit=args.limit,
        )
    )


def cmd_audit_active(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(audit_active_decisions(root))


def cmd_history(args: argparse.Namespace) -> None:
    _print(get_decision_history(Path(args.root).resolve(), args.decision_key))


def cmd_explain(args: argparse.Namespace) -> None:
    _print(explain_decision(Path(args.root).resolve(), args.decision_key))


def cmd_trace(args: argparse.Namespace) -> None:
    _print(get_decision_trace(Path(args.root).resolve(), args.decision_key))


def cmd_related(args: argparse.Namespace) -> None:
    _print(get_related_decision_context(Path(args.root).resolve(), args.decision_key))


def cmd_session_start(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    _print(session_start(root))


def cmd_search(args: argparse.Namespace) -> None:
    conn = connect(Path(args.root).resolve())
    match_query = _fts_match_query(args.query)
    rows = fetch_all_dicts(
        conn,
        """
        SELECT dv.id AS decision_version_id, dv.decision_key, dv.title, dv.summary
        FROM decision_versions dv
        JOIN (
            SELECT rowid, rank
            FROM decision_search
            WHERE decision_search MATCH ?
            ORDER BY rank
            LIMIT 10
        ) matched ON matched.rowid = dv.id
        ORDER BY matched.rank
        """,
        (match_query,),
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

    rollout_parser = subparsers.add_parser("import-rollout-summary")
    rollout_parser.add_argument("path")
    rollout_parser.add_argument("--project-id", default="default")
    rollout_parser.add_argument("--source-ref")
    rollout_parser.set_defaults(func=cmd_import_rollout_summary)

    scan_parser = subparsers.add_parser("scan-unmined")
    scan_parser.set_defaults(func=cmd_scan_unmined)

    pending_parser = subparsers.add_parser("pending-mining")
    pending_parser.set_defaults(func=cmd_pending_mining)

    source_inventory_parser = subparsers.add_parser("source-inventory")
    source_inventory_parser.set_defaults(func=cmd_source_inventory)

    resolve_source_parser = subparsers.add_parser("resolve-source")
    resolve_source_parser.add_argument("--source-ref", required=True)
    resolve_source_parser.add_argument(
        "--status",
        required=True,
        choices=[
            "covered_by_curated_summary",
            "imported_filtered_codex_jsonl",
            "out_of_scope_recent_active",
            "out_of_scope_aborted_child",
            "out_of_scope_control_thread",
            "out_of_scope_duplicate_child",
            "needs_human_review",
        ],
    )
    resolve_source_parser.add_argument("--reason", required=True)
    resolve_source_parser.add_argument("--evidence-ref")
    resolve_source_parser.add_argument("--resolver-type", default="main_agent")
    resolve_source_parser.set_defaults(func=cmd_resolve_source)

    resolve_sources_parser = subparsers.add_parser("resolve-sources")
    resolve_sources_parser.add_argument("path")
    resolve_sources_parser.add_argument("--resolver-type", default="main_agent")
    resolve_sources_parser.set_defaults(func=cmd_resolve_sources)

    mine_parser = subparsers.add_parser("mine")
    mine_parser.add_argument("--from-sequence", type=int)
    mine_parser.add_argument("--to-sequence", type=int)
    mine_parser.set_defaults(func=cmd_mine)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-id", type=int, required=True)
    validate_parser.set_defaults(func=cmd_validate)

    review_queue_parser = subparsers.add_parser("review-queue")
    review_queue_parser.add_argument("--run-id", type=int, required=True)
    review_queue_parser.set_defaults(func=cmd_review_queue)

    review_run_parser = subparsers.add_parser("review-run")
    review_run_parser.add_argument("--run-id", type=int, required=True)
    review_run_parser.add_argument("--approve", action="append", default=[])
    review_run_parser.add_argument("--reject", action="append", default=[])
    review_run_parser.add_argument("--reviewer-type", default="main_agent")
    review_run_parser.set_defaults(func=cmd_review_run)

    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--run-id", type=int, required=True)
    promote_parser.set_defaults(func=cmd_promote)

    active_parser = subparsers.add_parser("active")
    active_parser.set_defaults(func=cmd_active)

    categories_parser = subparsers.add_parser("categories")
    categories_parser.set_defaults(func=cmd_categories)

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--task", required=True)
    query_parser.add_argument("--category", action="append", default=[])
    query_parser.add_argument("--limit", type=int, default=8)
    query_parser.set_defaults(func=cmd_query)

    audit_parser = subparsers.add_parser("audit-active")
    audit_parser.set_defaults(func=cmd_audit_active)

    history_parser = subparsers.add_parser("history")
    history_parser.add_argument("--decision-key", required=True)
    history_parser.set_defaults(func=cmd_history)

    explain_parser = subparsers.add_parser("explain")
    explain_parser.add_argument("--decision-key", required=True)
    explain_parser.set_defaults(func=cmd_explain)

    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("--decision-key", required=True)
    trace_parser.set_defaults(func=cmd_trace)

    related_parser = subparsers.add_parser("related")
    related_parser.add_argument("--decision-key", required=True)
    related_parser.set_defaults(func=cmd_related)

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
