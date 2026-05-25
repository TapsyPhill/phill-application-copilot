"""Local ChromaDB vector store."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from backend.app.config.settings import get_settings


class ChromaStore:
    def __init__(self, collection_name: str) -> None:
        settings = get_settings()
        path = Path(settings.chroma_persist_dir)
        path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(path))
        self._collection = self._client.get_or_create_collection(collection_name)

    def upsert(
        self, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> None:
        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, text: str, n: int = 5) -> dict[str, Any]:
        return self._collection.query(query_texts=[text], n_results=n)
