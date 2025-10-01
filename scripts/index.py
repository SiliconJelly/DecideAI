#!/usr/bin/env python3
import argparse
import yaml
from pathlib import Path
from ingestion.pipeline import IngestionConfig, build_index


def main():
    parser = argparse.ArgumentParser(description="Index documents into a local vector store (FAISS by default)")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")
    parser.add_argument("--input", help="Override input directory")
    parser.add_argument("--index", help="Override index directory")
    parser.add_argument("--model", help="Override embedding model")
    parser.add_argument("--size", type=int, help="Chunk size override")
    parser.add_argument("--overlap", type=int, help="Chunk overlap override")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    data = {}
    if cfg_path.exists():
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

    input_dir = args.input or data.get("ingestion", {}).get("input_dir", "data/workspaces/sample-tenant/raw")
    index_dir = args.index or data.get("vector_store", {}).get("index_dir", "data/workspaces/sample-tenant/index")
    model = args.model or data.get("embedding", {}).get("model_name", "intfloat/multilingual-e5-small")
    size = args.size or data.get("chunking", {}).get("size", 800)
    overlap = args.overlap or data.get("chunking", {}).get("overlap", 120)

    cfg = IngestionConfig(
        input_dir=input_dir,
        index_dir=index_dir,
        embedding_model=model,
        chunk_size=size,
        chunk_overlap=overlap,
    )

    files, chunks = build_index(cfg)
    print(f"Indexed {files} files into {index_dir} ({chunks} chunks)")


if __name__ == "__main__":
    main()
