# RAG Quick Start Guide

This guide will help you get started with Retrieval-Augmented Generation (RAG) in the AI Employee Decision System in under 5 minutes.

## Prerequisites

```bash
# Install required dependencies
pip install faiss-cpu sentence-transformers

# Or for GPU support
pip install faiss-gpu sentence-transformers
```

## Step 1: Create Sample Documents

Create a directory for test documents:

```bash
mkdir -p data/workspaces/sample-tenant/documents
```

Create a sample document (`data/workspaces/sample-tenant/documents/sample.txt`):

```text
Employee Handbook: Vacation Policy

All full-time employees are entitled to 20 days of paid vacation per year.
Vacation days accumulate at a rate of 1.67 days per month.
Employees must request vacation at least 2 weeks in advance.
Unused vacation days can be carried over to the next year, up to a maximum of 10 days.

Performance Review Process

Performance reviews are conducted annually in January.
Managers meet with each employee to discuss:
- Goal achievement from the previous year
- Areas of strength and improvement
- Career development goals
- Compensation adjustments

Promotions

Employees are eligible for promotion after a minimum of 12 months in their current role.
Promotion criteria include:
- Consistent high performance
- Demonstrated leadership
- Additional responsibilities taken on
- Positive peer feedback
```

## Step 2: Index the Documents

Create an indexing script (`scripts/index_documents.py`):

```python
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
        return 1
    
    print(f"Reading document: {doc_path}")
    text = doc_path.read_text()
    
    # Chunk the document
    print("Chunking document...")
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    print(f"Created {len(chunks)} chunks")
    
    # Add to vector store
    print("Adding documents to vector store...")
    for i, chunk in enumerate(chunks):
        store.add_document(
            chunk,
            metadata={
                "source": "sample.txt",
                "chunk": i
            }
        )
    
    # Save index
    index_dir = Path("data/workspaces/sample-tenant/index")
    index_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving index to {index_dir}...")
    store.save(str(index_dir))
    
    print("✓ Indexing complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

Run the indexing script:

```bash
python3 scripts/index_documents.py
```

## Step 3: Test RAG Integration

Run the test suite:

```bash
python3 test_rag_integration.py
```

Expected output:
```
============================================================
RAG Integration Test Suite
============================================================

============================================================
Testing Retrieval Service
============================================================
✓ Retrieval service created
  Available: True

✓ Search executed for query: 'employee performance review'
  Results found: 3

  Result 1:
    Score: 0.8543
    Text: Performance Review Process Performance reviews are conducted annually...
    Metadata: {'source': 'sample.txt', 'chunk': 3}

============================================================
Testing AI Service with RAG
============================================================
✓ AI service created
  RAG available: True

--- Testing query without RAG ---
✓ Query processed (without RAG)
  Response keys: ['response', 'original_query', 'timestamp', 'rag_enabled']
  RAG enabled: False

--- Testing query with RAG ---
✓ Query processed (with RAG)
  Response keys: ['response', 'original_query', 'timestamp', 'rag_enabled']
  RAG enabled: True

============================================================
Test Summary
============================================================
✓ PASS: Retrieval Service
✓ PASS: AI Service with RAG

============================================================
✓ All tests passed!
============================================================
```

## Step 4: Use RAG in Your Application

### Python

```python
from ai_employee_decision_system.services import AIService

# Initialize service
ai_service = AIService()

# Query with RAG
result = ai_service.process_query(
    "How many vacation days do employees get?",
    use_rag=True,
    top_k=3
)

print(result['response'])
# Output: "Full-time employees are entitled to 20 days of paid vacation per year..."
```

### REST API

Start the API server:

```bash
# Option 1: Using uvicorn directly
uvicorn ai_employee_decision_system.api.app:app --reload

# Option 2: Using docker-compose
docker-compose -f infra/docker-compose.yml up
```

Make a request:

```bash
# First, get an authentication token
# Provide credentials via environment to avoid printing secrets
USERNAME={{ADMIN_USERNAME}} PASSWORD={{ADMIN_PASSWORD}} \
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": '"\"$USERNAME\""', "password": '"\"$PASSWORD\""'}' | jq -r '.access_token')

# Query with RAG
curl -X POST http://localhost:8000/ai/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the promotion criteria?",
    "use_rag": true,
    "top_k": 5
  }' | jq
```

## Step 5: Explore Direct Search

You can also search the knowledge base directly:

```bash
curl -X POST http://localhost:8000/ai/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vacation policy",
    "top_k": 5
  }' | jq
```

Expected response:
```json
{
  "query": "vacation policy",
  "results": [
    {
      "text": "Employee Handbook: Vacation Policy All full-time employees are entitled to 20 days...",
      "score": 0.8765,
      "metadata": {
        "source": "sample.txt",
        "chunk": 0
      }
    }
  ],
  "count": 5
}
```

## Troubleshooting

### "Index not available" Warning

If you see this warning, it means the index directory doesn't exist or is empty:

```bash
# Check if index exists
ls -la data/workspaces/sample-tenant/index/

# Re-run indexing
python3 scripts/index_documents.py
```

### Import Errors

Install missing dependencies:

```bash
pip install faiss-cpu sentence-transformers torch
```

### Environment Variables

If you want to use a custom index location:

```bash
export DECIDEAI_INDEX_DIR=/custom/path/to/index
export DECIDEAI_EMBEDDING_MODEL=intfloat/multilingual-e5-small
```

## Next Steps

1. **Index more documents**: Add PDF, DOCX, CSV files to your knowledge base
2. **Tune parameters**: Experiment with `top_k` and embedding models
3. **Monitor performance**: Check response times and relevance scores
4. **Scale up**: Consider Qdrant for production workloads

For more detailed information, see [RAG_INTEGRATION.md](./RAG_INTEGRATION.md).

## Quick Reference

### Key Files

- **AI Service**: `ai_employee_decision_system/services/ai_service.py`
- **Retrieval Service**: `ai_employee_decision_system/services/retrieval_service.py`
- **Vector Store**: `ai_employee_decision_system/services/vectorstores/faiss_store.py`
- **API Endpoints**: `ai_employee_decision_system/api/app.py`

### API Endpoints

- `POST /ai/query` - Query with RAG
- `POST /ai/search` - Direct knowledge base search
- `GET /health` - Health check

### Environment Variables

- `DECIDEAI_INDEX_DIR` - Index directory path
- `DECIDEAI_EMBEDDING_MODEL` - Embedding model name

### Common Commands

```bash
# Run tests
python3 test_rag_integration.py

# Start API
uvicorn ai_employee_decision_system.api.app:app --reload

# Index documents
python3 scripts/index_documents.py
```