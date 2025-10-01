import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


@dataclass
class SearchResult:
    text: str
    metadata: Dict
    score: float


class FAISSVectorStore:
    """Minimal FAISS-based local vector store with JSON metadata.

    - Cosine similarity via normalized embeddings and IndexFlatIP.
    - Persists index to <dir>/index.faiss and metadata to <dir>/metadatas.json and texts.json
    """

    def __init__(self, embedding_model: str = "intfloat/multilingual-e5-small") -> None:
        if faiss is None:
            raise RuntimeError("faiss-cpu is not installed. Please `pip install faiss-cpu`." )
        if SentenceTransformer is None:
            raise RuntimeError(
                "sentence-transformers is not installed. Please `pip install sentence-transformers`."
            )
        self.model_name = embedding_model
        self.model = SentenceTransformer(self.model_name)
        self.index = None  # type: ignore
        self.texts: List[str] = []
        self.metadatas: List[Dict] = []

    def _embed(self, texts: List[str]) -> np.ndarray:
        embs = self.model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
        return np.asarray(embs, dtype="float32")

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> int:
        if not texts:
            return 0
        metas = metadatas or [{} for _ in texts]
        if len(metas) != len(texts):
            raise ValueError("metadatas length must match texts length")

        embs = self._embed(texts)
        dim = embs.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)
        self.index.add(embs)
        self.texts.extend(texts)
        self.metadatas.extend(metas)
        return len(texts)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if self.index is None:
            return []
        q = self._embed([query])
        D, I = self.index.search(q, top_k)
        results: List[SearchResult] = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            results.append(
                SearchResult(
                    text=self.texts[idx],
                    metadata=self.metadatas[idx],
                    score=float(score),
                )
            )
        return results

    def persist(self, dir_path: str) -> None:
        d = Path(dir_path)
        d.mkdir(parents=True, exist_ok=True)
        if self.index is None:
            # Create empty index on persist if nothing added
            # Use model dimension
            tmp = self._embed(["placeholder"])
            dim = tmp.shape[1]
            self.index = faiss.IndexFlatIP(dim)
        faiss.write_index(self.index, (d / "index.faiss").as_posix())
        (d / "texts.json").write_text(json.dumps(self.texts, ensure_ascii=False), encoding="utf-8")
        (d / "metadatas.json").write_text(json.dumps(self.metadatas, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, dir_path: str, embedding_model: str = "intfloat/multilingual-e5-small") -> "FAISSVectorStore":
        d = Path(dir_path)
        store = cls(embedding_model=embedding_model)
        index_path = d / "index.faiss"
        if index_path.exists():
            store.index = faiss.read_index(index_path.as_posix())
        texts_path = d / "texts.json"
        metas_path = d / "metadatas.json"
        if texts_path.exists():
            store.texts = json.loads(texts_path.read_text(encoding="utf-8"))
        if metas_path.exists():
            store.metadatas = json.loads(metas_path.read_text(encoding="utf-8"))
        return store
