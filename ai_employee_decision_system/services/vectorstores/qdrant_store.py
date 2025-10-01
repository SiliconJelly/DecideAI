from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except Exception:  # pragma: no cover
    QdrantClient = None  # type: ignore
    Distance = None  # type: ignore
    VectorParams = None  # type: ignore
    PointStruct = None  # type: ignore

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


@dataclass
class QdrantConfig:
    host: str = "localhost"
    port: int = 6333
    collection: str = "decideai"
    embedding_model: str = "intfloat/multilingual-e5-small"


class QdrantVectorStore:
    """Optional Qdrant vector store adapter (requires qdrant-client)."""

    def __init__(self, cfg: Optional[QdrantConfig] = None) -> None:
        if QdrantClient is None:
            raise RuntimeError("qdrant-client is not installed. `pip install qdrant-client`." )
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is not installed. `pip install sentence-transformers`.")
        self.cfg = cfg or QdrantConfig()
        self.client = QdrantClient(host=self.cfg.host, port=self.cfg.port)
        self.model = SentenceTransformer(self.cfg.embedding_model)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        dim = len(self.model.encode(["test"], normalize_embeddings=True)[0])
        try:
            self.client.get_collection(self.cfg.collection)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.cfg.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> int:
        embs = self.model.encode(texts, normalize_embeddings=True)
        points = []
        metas = metadatas or [{} for _ in texts]
        for i, (text, emb, meta) in enumerate(zip(texts, embs, metas)):
            points.append(
                PointStruct(id=None, vector=emb, payload={"text": text, **meta})
            )
        self.client.upsert(collection_name=self.cfg.collection, points=points)
        return len(points)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        q = self.model.encode([query], normalize_embeddings=True)[0]
        results = self.client.search(collection_name=self.cfg.collection, query_vector=q, limit=top_k)
        return [
            {"text": r.payload.get("text", ""), "score": r.score, "metadata": r.payload}
            for r in results
        ]
