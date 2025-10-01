#!/usr/bin/env python3
"""
Simple script to index documents into FAISS vector store.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_employee_decision_system.services.vectorstores.faiss_store import FAISSVectorStore


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def main():
    # Initialize vector store
    print("Initializing vector store...")
    store = FAISSVectorStore(embedding_model="intfloat/multilingual-e5-small")
    
    # Read sample document
    doc_path = Path("data/workspaces/sample-tenant/documents/sample.txt")
    if not doc_path.exists():
        print(f"Error: {doc_path} not found!")
        print("Please create a sample document first. See docs/RAG_QUICKSTART.md for details.")
        return 1
    
    print(f"Reading document: {doc_path}")
    text = doc_path.read_text()
    
    # Chunk the document
    print("Chunking document...")
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    print(f"Created {len(chunks)} chunks")
    
    # Prepare metadatas
    metadatas = [
        {
            "source": "sample.txt",
            "chunk": i
        }
        for i in range(len(chunks))
    ]
    
    # Add to vector store
    print("Adding documents to vector store...")
    added = store.add_texts(chunks, metadatas=metadatas)
    print(f"  Added {added} chunks")
    
    # Save index
    index_dir = Path("data/workspaces/sample-tenant/index")
    index_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving index to {index_dir}...")
    store.persist(str(index_dir))
    
    print("\n" + "=" * 60)
    print("✓ Indexing complete!")
    print("=" * 60)
    print(f"Indexed {len(chunks)} document chunks")
    print(f"Index saved to: {index_dir}")
    print("\nNext steps:")
    print("  1. Run: python3 test_rag_integration.py")
    print("  2. Start API: uvicorn ai_employee_decision_system.api.app:app --reload")
    print("  3. See docs/RAG_QUICKSTART.md for usage examples")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())