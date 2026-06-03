#!/usr/bin/env python3
"""
Query traces by semantic similarity using Voyage AI embeddings.
Usage: python query-traces.py "SEARCH_QUERY" [--limit N] [--category CAT]
Returns: Top-k most similar traces
"""

import sys
import os
import json
import argparse
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "voyage-3"
DEFAULT_LIMIT = 5

def get_voyage_key():
    """Get Voyage AI API key from env or config."""
    key = os.environ.get("VOYAGE_API_KEY")
    if key:
        return key

    config_path = Path(".claude/config/project.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            key = config.get("voyage_api_key")
            if key:
                return key

    global_config = Path.home() / ".claude" / "config" / "keys.json"
    if global_config.exists():
        with open(global_config) as f:
            config = json.load(f)
            key = config.get("voyage_api_key")
            if key:
                return key

    return None

def get_query_embedding(text: str, api_key: str) -> list:
    """Get embedding for query text."""
    try:
        import voyageai
        vo = voyageai.Client(api_key=api_key)
        result = vo.embed([text], model=EMBEDDING_MODEL, input_type="query")
        return result.embeddings[0]
    except ImportError:
        print("Error: voyageai package not installed")
        print("Install with: pip install voyageai")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting embedding: {e}")
        sys.exit(1)

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

def query_traces(
    query: str,
    limit: int = DEFAULT_LIMIT,
    category: str = None,
    outcome: str = None,
    project_dir: str = None
):
    """Query traces by semantic similarity."""

    api_key = get_voyage_key()
    if not api_key:
        print("Error: VOYAGE_API_KEY not found")
        sys.exit(1)

    # Get query embedding
    print(f"Searching for: {query}")
    query_embedding = get_query_embedding(query, api_key)

    # Get ChromaDB collection
    collection = get_chroma_client(project_dir)

    # Build where clause for filters
    where = {}
    if category:
        where["category"] = category
    if outcome:
        where["outcome"] = outcome

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit,
        where=where if where else None
    )

    # Display results
    if not results or not results["ids"][0]:
        print("\n=== No traces found ===")
        print("Run init-db.py and store-trace.py first")
        return []

    print(f"\n=== Found {len(results['ids'][0])} similar traces ===\n")

    output = []
    for i, trace_id in enumerate(results["ids"][0], 1):
        metadata = results["metadatas"][0][i-1]
        document = results["documents"][0][i-1]
        distance = results["distances"][0][i-1]

        # Convert L2 distance to similarity (0-1 scale)
        similarity = 1 / (1 + distance)

        result = {
            "rank": i,
            "id": trace_id,
            "similarity": round(similarity, 3),
            "category": metadata.get("category"),
            "decision": metadata.get("decision") or document,
            "outcome": metadata.get("outcome"),
            "state": metadata.get("state"),
            "feature_id": metadata.get("feature_id"),
            "timestamp": metadata.get("timestamp")
        }
        output.append(result)

        print(f"[{i}] {result['decision'][:80]}...")
        print(f"    Similarity: {result['similarity']}")
        print(f"    Category: {result['category']} | Outcome: {result['outcome']} | State: {result['state']}")
        print(f"    ID: {trace_id}")
        print()

    # Also output JSON for programmatic use
    if os.environ.get("OUTPUT_JSON"):
        print(json.dumps(output, indent=2))

    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query traces by semantic similarity")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-n", type=int, default=DEFAULT_LIMIT, help="Number of results")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--outcome", "-o", choices=["pending", "success", "failure"], help="Filter by outcome")
    parser.add_argument("--project-dir", "-p", default=None, help="Project directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.json:
        os.environ["OUTPUT_JSON"] = "1"

    query_traces(
        query=args.query,
        limit=args.limit,
        category=args.category,
        outcome=args.outcome,
        project_dir=args.project_dir
    )
