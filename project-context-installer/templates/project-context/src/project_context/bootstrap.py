from __future__ import annotations

from pathlib import Path

from project_context.mining import list_unimported_codex_sessions, list_unmined_sessions, latest_pending_run, run_mining
from project_context.validation import list_review_candidates, promote_run, validate_run


def session_start(root: Path) -> dict:
    pending = latest_pending_run(root)
    if pending is not None and pending["status"] != "promoted":
        if pending["status"] == "review_required":
            return {
                "status": "needs_review",
                "reason": "agent review required before promotion",
                "run_id": pending["id"],
                "review_candidate_ids": [candidate["id"] for candidate in list_review_candidates(root, pending["id"])],
            }
        validation_result = validate_run(root, pending["id"]) if pending["status"] == "mined" else {"status": "approved"}
        if validation_result["status"] == "rejected":
            return {
                "status": "blocked",
                "reason": "validation rejected pending mining run",
                "run_id": pending["id"],
            }
        if validation_result["status"] == "needs_review":
            return {
                "status": "needs_review",
                "reason": "agent review required before promotion",
                "run_id": pending["id"],
                "review_candidate_ids": validation_result["review_candidate_ids"],
            }
        promote_result = promote_run(root, pending["id"])
        return {
            "status": "ready",
            "run_id": pending["id"],
            "promoted_count": promote_result["promoted_count"],
        }

    source_inventory = list_unimported_codex_sessions(root)
    if source_inventory["unimported_sessions"]:
        return {
            "status": "source_inventory_gap",
            "reason": "raw Codex sessions for this repo are not imported into the context graph",
            "source_inventory_gap_count": len(source_inventory["unimported_sessions"]),
            "unimported_source_sessions": source_inventory["unimported_sessions"],
            "recent_unimported_source_sessions": source_inventory["recent_unimported_sessions"],
            "source_inventory": {
                "scanned": source_inventory["scanned"],
                "sessions_root": source_inventory["sessions_root"],
            },
        }

    unmined = list_unmined_sessions(root)
    if not unmined:
        return {"status": "ready", "unmined_sessions": 0}
    mine_result = run_mining(root)
    if mine_result["status"] == "noop":
        return {"status": "ready", "unmined_sessions": 0}
    validation_result = validate_run(root, mine_result["run_id"])
    if validation_result["status"] == "rejected":
        return {
            "status": "blocked",
            "reason": "validation rejected mining run",
            "run_id": mine_result["run_id"],
        }
    if validation_result["status"] == "needs_review":
        return {
            "status": "needs_review",
            "reason": "agent review required before promotion",
            "run_id": mine_result["run_id"],
            "review_candidate_ids": validation_result["review_candidate_ids"],
        }
    promote_result = promote_run(root, mine_result["run_id"])
    return {
        "status": "ready",
        "run_id": mine_result["run_id"],
        "promoted_count": promote_result["promoted_count"],
    }
