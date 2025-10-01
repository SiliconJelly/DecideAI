import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ingestion.loaders.pdf_loader import load_pdf_text
from ingestion.loaders.docx_loader import load_docx_text
from ingestion.loaders.text_loader import load_text

from ai_employee_decision_system.services.vectorstores.faiss_store import FAISSVectorStore


SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}


def _read_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return load_pdf_text(path)
    if ext == ".docx":
        return load_docx_text(path)
    if ext in {".txt", ".md"}:
        return load_text(path)
    return ""


def chunk_text(text: str, size: int = 800, overlap: int = 120) -> List[str]:
    if not text:
        return []
    text = " ".join(text.split())  # normalize whitespace
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


@dataclass
class IngestionConfig:
    input_dir: str
    index_dir: str
    embedding_model: str = "intfloat/multilingual-e5-small"
    chunk_size: int = 800
    chunk_overlap: int = 120


def build_index(cfg: IngestionConfig) -> Tuple[int, int]:
    """Build a FAISS index from files under input_dir.

    Returns: (documents_count, chunks_count)
    """
    input_dir = Path(cfg.input_dir)
    index_dir = Path(cfg.index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)

    store = FAISSVectorStore(embedding_model=cfg.embedding_model)

    file_count = 0
    chunk_count = 0
    for path in input_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        text = _read_file(path)
        if not text:
            continue
        chunks = chunk_text(text, size=cfg.chunk_size, overlap=cfg.chunk_overlap)
        metas = [{"source": path.as_posix(), "chunk": i} for i in range(len(chunks))]
        store.add_texts(chunks, metas)
        file_count += 1
        chunk_count += len(chunks)

    store.persist(index_dir.as_posix())
    return file_count, chunk_count


def main():
    parser = argparse.ArgumentParser(description="Build a local FAISS index from documents.")
    parser.add_argument("--input", required=True, help="Input directory with documents")
    parser.add_argument("--index", required=True, help="Output index directory")
    parser.add_argument("--model", default="intfloat/multilingual-e5-small", help="Embedding model name")
    parser.add_argument("--size", type=int, default=800, help="Chunk size (chars)")
    parser.add_argument("--overlap", type=int, default=120, help="Chunk overlap (chars)")
    args = parser.parse_args()

    cfg = IngestionConfig(
        input_dir=args.input,
        index_dir=args.index,
        embedding_model=args.model,
        chunk_size=args.size,
        chunk_overlap=args.overlap,
    )
    files, chunks = build_index(cfg)
    print(json.dumps({"files_indexed": files, "chunks_indexed": chunks, "index_dir": args.index}))


if __name__ == "__main__":
    main()
