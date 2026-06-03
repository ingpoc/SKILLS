#!/usr/bin/env python3
"""
Initialize ChromaDB for trace storage.
Usage: python init-db.py [project_dir]
Creates: .claude/chroma/ with traces collection
"""

import sys
from pathlib import Path

EMBEDDING_DIM = 1024  # Voyage AI voyage-3 outputs 1024 dimensions

def init_database(project_dir: str = None):
    """Initialize ChromaDB with traces collection."""
    import chromadb

    # Determine database path
    if project_dir:
        db_dir = Path(project_dir) / ".claude" / "chroma"
    else:
        db_dir = Path(".claude/chroma")

    db_dir.mkdir(parents=True, exist_ok=True)

    # Create persistent client and collection
    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection(
        name="traces",
        metadata={"embedding_dim": EMBEDDING_DIM}
    )

    print(f"ChromaDB initialized: {db_dir}")
    print(f"Embedding dimensions: {EMBEDDING_DIM}")
    print("Collection: traces")

if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    init_database(project_dir)
