#!/usr/bin/env python3
"""
Store a decision trace with Voyage AI embedding.
Usage: python store-trace.py "DECISION_TEXT" [--category CAT] [--outcome OK|FAIL]
Config: Reads VOYAGE_API_KEY from env or .claude/config/project.json
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import hashlib

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "voyage-3"  # or voyage-3-lite for faster/cheaper
EMBEDDING_DIM = 1024

def get_voyage_key():
    """Get Voyage AI API key from env or config."""
    # Try environment first
    key = os.environ.get("VOYAGE_API_KEY")
    if key:
        return key

    # Try project config
    config_path = Path(".claude/config/project.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            key = config.get("voyage_api_key")
            if key:
                return key

    # Try global config
    global_config = Path.home() / ".claude" / "config" / "keys.json"
    if global_config.exists():
        with open(global_config) as f:
            config = json.load(f)
            key = config.get("voyage_api_key")
            if key:
                return key

    return None

def get_embedding(text: str, api_key: str) -> list:
    """Get embedding from Voyage AI."""
    try:
        import voyageai
        vo = voyageai.Client(api_key=api_key)
        result = vo.embed([text], model=EMBEDDING_MODEL, input_type="document")
        return result.embeddings[0]
    except ImportError:
        print("Error: voyageai package not installed")
        print("Install with: pip install voyageai")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting embedding: {e}")
        sys.exit(1)

def get_state_context():
    """Get current state context from progress files."""
    context = {
        "state": "unknown",
        "feature_id": None,
        "session_id": None
    }

    state_file = Path(".claude/progress/state.json")
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            context["state"] = state.get("state", "unknown")
            context["feature_id"] = state.get("feature_id")
            context["session_id"] = state.get("session_id")

    return context

def get_chroma_client(project_dir: str = None):
    """Get or create ChromaDB client for a project."""
    import chromadb

    if project_dir:
        db_dir = Path(project_dir) / ".claude" / "chroma"
    else:
        db_dir = Path(".claude/chroma")

    db_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection(name="traces")
    return collection

def store_trace(
    decision: str,
    category: str = "general",
    outcome: str = "pending",
    project_dir: str = None
):
    """Store trace with embedding in ChromaDB."""

    api_key = get_voyage_key()
    if not api_key:
        print("Error: VOYAGE_API_KEY not found")
        print("Set via: export VOYAGE_API_KEY=your_key")
        print("Or add to .claude/config/project.json: {\"voyage_api_key\": \"...\"}")
        sys.exit(1)

    # Generate trace ID
    timestamp = datetime.now().isoformat()
    trace_id = f"trace_{hashlib.sha256(f'{timestamp}{decision}'.encode()).hexdigest()[:12]}"

    # Get state context
    context = get_state_context()

    # Get embedding
    print(f"Getting embedding for: {decision[:50]}...")
    embedding = get_embedding(decision, api_key)

    # Get ChromaDB collection
    collection = get_chroma_client(project_dir)

    # Store in ChromaDB
    collection.add(
        ids=[trace_id],
        embeddings=[embedding],
        metadatas=[{
            "timestamp": timestamp,
            "category": category,
            "decision": decision,
            "outcome": outcome,
            "session_id": context["session_id"] or "",
            "feature_id": context["feature_id"] or "",
            "state": context["state"],
            "project_dir": project_dir or os.getcwd()
        }],
        documents=[decision]
    )

    print(f"Trace stored: {trace_id}")
    print(f"  Category: {category}")
    print(f"  State: {context['state']}")
    print(f"  Outcome: {outcome}")

    return trace_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Store a decision trace")
    parser.add_argument("decision", help="The decision text to store")
    parser.add_argument("--category", "-c", default="general", help="Category (default: general)")
    parser.add_argument("--outcome", "-o", default="pending", choices=["pending", "success", "failure"], help="Outcome")
    parser.add_argument("--project-dir", "-p", default=None, help="Project directory")

    args = parser.parse_args()

    store_trace(
        decision=args.decision,
        category=args.category,
        outcome=args.outcome,
        project_dir=args.project_dir
    )
