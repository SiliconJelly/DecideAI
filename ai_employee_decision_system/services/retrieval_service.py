"""
Retrieval service wrapping the local FAISS vector store.
Falls back gracefully when the index or dependencies are not available.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from ai_employee_decision_system.services.vectorstores.faiss_store import (
        FAISSVectorStore,
        SearchResult,
    )
except Exception:  # pragma: no cover
    FAISSVectorStore = None  # type: ignore
    SearchResult = None  # type: ignore


DEFAULT_INDEX_DIR = "data/workspaces/sample-tenant/index"
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"


@dataclass
class RetrievalConfig:
    index_dir: str = DEFAULT_INDEX_DIR
    embedding_model: str = DEFAULT_EMBEDDING_MODEL


class RetrievalService:
    """Simple retrieval wrapper used for RAG."""

    def __init__(self, cfg: RetrievalConfig) -> None:
        self.cfg = cfg
        self._store = None
        self._available = False
        try:
            if FAISSVectorStore is not None and Path(self.cfg.index_dir).exists():
                # Load existing index (if present), else create lazily when needed
                self._store = FAISSVectorStore.load(
                    dir_path=self.cfg.index_dir,
                    embedding_model=self.cfg.embedding_model,
                )
                self._available = True
        except Exception:
            self._available = False

    @classmethod
    def from_env(cls) -> "RetrievalService":
        index_dir = os.environ.get("DECIDEAI_INDEX_DIR", DEFAULT_INDEX_DIR)
        embedding_model = os.environ.get(
            "DECIDEAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        )
        return cls(RetrievalConfig(index_dir=index_dir, embedding_model=embedding_model))

    def is_available(self) -> bool:
        return bool(self._available and self._store is not None)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.is_available():
            return []
        try:
            results: List[SearchResult] = self._store.search(query, top_k=top_k)  # type: ignore
            out: List[Dict[str, Any]] = []
            for r in results:
                # r.metadata may contain 'source' and 'chunk'
                out.append(
                    {
                        "text": r.text,
                        "score": r.score,
                        "metadata": r.metadata,
                    }
                )
            return out
        except Exception:
            return []