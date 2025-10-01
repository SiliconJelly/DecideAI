# RAG (Retrieval-Augmented Generation) Integration

## Overview

The AI Employee Decision System now supports **Retrieval-Augmented Generation (RAG)**, enabling the AI to provide more accurate and contextual responses by retrieving relevant information from an indexed knowledge base before generating answers.

## Architecture

The RAG integration consists of three main components:

### 1. Vector Store (FAISS)
- **Location**: `ai_employee_decision_system/services/vectorstores/faiss_store.py`
- **Purpose**: Stores document embeddings and performs similarity search
- **Backend**: Uses Facebook's FAISS library for efficient vector similarity search
- **Alternative**: Qdrant vector store available at `vectorstores/qdrant_store.py`

### 2. Retrieval Service
- **Location**: `ai_employee_decision_system/services/retrieval_service.py`
- **Purpose**: High-level interface for searching the knowledge base
- **Features**:
  - Automatic initialization from environment variables
  - Graceful fallback when index is unavailable
  - Simple search API

### 3. AI Service Integration
- **Location**: `ai_employee_decision_system/services/ai_service.py`
- **Purpose**: Integrates retrieval with LLM query processing
- **Features**:
  - Optional RAG (can be disabled per query)
  - Configurable number of context documents (top_k)
  - Merges retrieved context with user context

## Configuration

### Environment Variables

```bash
# Index directory (default: data/workspaces/sample-tenant/index)
export DECIDEAI_INDEX_DIR=/path/to/index

# Embedding model (default: intfloat/multilingual-e5-small)
export DECIDEAI_EMBEDDING_MODEL=intfloat/multilingual-e5-small
```

### Directory Structure

```
data/
└── workspaces/
    └── sample-tenant/
        ├── index/              # FAISS index files
        │   ├── index.faiss
        │   ├── metadata.json
        │   └── config.json
        └── documents/          # Raw documents
```

## API Endpoints

### 1. AI Query with RAG

**Endpoint**: `POST /ai/query`

**Request Body**:
```json
{
  "query": "What are the key skills for a data scientist?",
  "context": {},
  "use_rag": true,
  "top_k": 5
}
```

**Parameters**:
- `query` (string, required): The natural language query
- `context` (object, optional): Additional context for the query
- `use_rag` (boolean, optional): Whether to use RAG (default: true)
- `top_k` (integer, optional): Number of documents to retrieve (default: 5)

**Response**:
```json
{
  "response": "Based on the retrieved information...",
  "original_query": "What are the key skills...",
  "timestamp": "2025-09-29T19:09:35Z",
  "rag_enabled": true
}
```

### 2. Direct Knowledge Base Search

**Endpoint**: `POST /ai/search`

**Request Body**:
```json
{
  "query": "employee performance metrics",
  "top_k": 10
}
```

**Parameters**:
- `query` (string, required): The search query
- `top_k` (integer, optional): Number of results to return (default: 10)

**Response**:
```json
{
  "query": "employee performance metrics",
  "results": [
    {
      "text": "Performance metrics include...",
      "score": 0.8543,
      "metadata": {
        "source": "hr_handbook.pdf",
        "chunk": 12
      }
    }
  ],
  "count": 10
}
```

## Usage Examples

### Python SDK

```python
from ai_employee_decision_system.services import AIService

# Initialize AI service with RAG
ai_service = AIService()

# Query with RAG enabled (default)
result = ai_service.process_query(
    "What are the requirements for promotion?",
    use_rag=True,
    top_k=5
)

# Query without RAG
result = ai_service.process_query(
    "What are the requirements for promotion?",
    use_rag=False
)
```

### Direct Retrieval Service

```python
from ai_employee_decision_system.services import RetrievalService

# Initialize from environment
retrieval = RetrievalService.from_env()

# Check availability
if retrieval.is_available():
    # Search knowledge base
    results = retrieval.search("performance review process", top_k=5)
    
    for result in results:
        print(f"Score: {result['score']:.4f}")
        print(f"Text: {result['text']}")
        print(f"Metadata: {result['metadata']}")
```

### cURL Examples

```bash
# Query with RAG
curl -X POST http://localhost:8000/ai/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the company vacation policies?",
    "use_rag": true,
    "top_k": 5
  }'

# Direct search
curl -X POST http://localhost:8000/ai/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vacation policy",
    "top_k": 10
  }'
```

## Indexing Documents

To enable RAG, you need to index documents into the vector store. This is typically done through the ingestion pipeline.

### 1. Using the Ingestion Pipeline

```python
from ai_employee_decision_system.services.vectorstores.faiss_store import FAISSVectorStore

# Initialize vector store
store = FAISSVectorStore(
    embedding_model="intfloat/multilingual-e5-small"
)

# Add documents
documents = [
    {
        "text": "Employee handbook section on vacation policies...",
        "metadata": {"source": "handbook.pdf", "page": 42}
    },
    {
        "text": "Performance review process documentation...",
        "metadata": {"source": "hr_guide.pdf", "page": 15}
    }
]

for doc in documents:
    store.add_document(doc["text"], metadata=doc["metadata"])

# Save index
store.save("data/workspaces/sample-tenant/index")
```

### 2. Bulk Ingestion (Coming Soon)

A dedicated ingestion service will support:
- PDF extraction
- DOCX processing
- CSV/Excel parsing
- Automatic chunking and indexing

## Testing

Run the RAG integration test suite:

```bash
python3 test_rag_integration.py
```

This will test:
1. Retrieval service initialization
2. Vector store availability
3. Search functionality
4. AI service integration
5. Query processing with and without RAG

## Performance Considerations

### Index Size
- Small index (<10K documents): Sub-second search times
- Medium index (10K-100K documents): 1-2 second search times
- Large index (>100K documents): Consider using Qdrant or other scalable alternatives

### Embedding Models

The default model `intfloat/multilingual-e5-small` provides:
- Good multilingual support (English, German, Japanese)
- Fast inference (~20ms per query)
- Reasonable quality (0.5-0.7 on standard benchmarks)

For better quality, consider:
- `intfloat/multilingual-e5-large`: Higher quality, slower
- Custom fine-tuned models: Best quality for domain-specific tasks

### Caching

The retrieval service caches the loaded index in memory. For production:
- Use a shared index location
- Consider Redis for distributed caching
- Implement index versioning for updates

## Troubleshooting

### RAG Not Available

If you see warnings like "Retrieval service initialization failed":

1. **Check index exists**:
   ```bash
   ls -la data/workspaces/sample-tenant/index/
   ```

2. **Verify FAISS installation**:
   ```bash
   pip install faiss-cpu  # or faiss-gpu
   ```

3. **Check dependencies**:
   ```bash
   pip install sentence-transformers
   ```

### Poor Search Results

1. **Check embedding model**: Ensure the model is appropriate for your language
2. **Verify document quality**: Ensure documents are properly chunked
3. **Tune top_k**: Adjust the number of retrieved documents
4. **Check metadata**: Ensure source attribution is correct

### Performance Issues

1. **Use GPU acceleration**: Install `faiss-gpu` for faster search
2. **Reduce index size**: Filter out irrelevant documents
3. **Optimize chunk size**: Experiment with different chunking strategies
4. **Enable caching**: Use Redis or memcached for frequent queries

## Roadmap

### Phase 1 (Current)
- ✅ FAISS vector store integration
- ✅ Basic retrieval service
- ✅ AI service RAG integration
- ✅ REST API endpoints

### Phase 2 (In Progress)
- 🔄 Document ingestion pipeline
- 🔄 Automatic chunking strategies
- 🔄 Metadata extraction
- 🔄 Index management CLI

### Phase 3 (Planned)
- ⏳ Qdrant integration for production scale
- ⏳ Multi-tenant index isolation
- ⏳ Real-time index updates
- ⏳ Query analytics and optimization
- ⏳ Hybrid search (keyword + vector)

## References

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)
- [Vector Search Guide](https://www.pinecone.io/learn/vector-search/)

## Support

For questions or issues:
- Check the logs: `logs/ai_service.log`
- Run diagnostics: `python3 test_rag_integration.py`
- Review the documentation: `docs/`
- Open an issue on GitHub