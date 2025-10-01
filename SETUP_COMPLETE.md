# DecideAI Backend - Setup Complete! 🎉

Your DecideAI backend is now fully set up and ready to test!

## What Has Been Done

### ✅ 1. Dependencies Installed
- All Python packages installed (FastAPI, SQLAlchemy, FAISS, Sentence Transformers, etc.)
- SQLAlchemy upgraded to 2.0.43 for compatibility

### ✅ 2. Database Initialized
- SQLite database created at: `data/employee_system.db`
- All database tables created
- Admin user can be created via environment variables (not created by default):
  - Set DECIDEAI_ADMIN_USERNAME and DECIDEAI_ADMIN_PASSWORD then run `python3 scripts/init_db.py`

### ✅ 3. RAG System Ready
- Sample HR policy document created
- FAISS vector index built with 10 document chunks
- Index saved at: `data/workspaces/sample-tenant/index/`
- Retrieval service configured and ready

### ✅ 4. Scripts Created
- **`start_server.sh`** - Start the FastAPI server
- **`scripts/init_db.py`** - Initialize database (already run)
- **`scripts/index_documents.py`** - Index documents for RAG (already run)
- **`scripts/test_api.py`** - Test all API endpoints

## How to Start the Server

### Option 1: Using the startup script (Recommended)
```bash
./start_server.sh
```

### Option 2: Direct uvicorn command
```bash
uvicorn ai_employee_decision_system.api.app:app --reload
```

The server will start at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## How to Test the Backend

### Option 1: Run the automated test script
In a **new terminal window** (keep the server running):
```bash
python3 scripts/test_api.py
```

This will test:
- ✓ Health check
- ✓ User authentication
- ✓ User info retrieval
- ✓ AI queries without RAG
- ✓ AI queries with RAG
- ✓ Direct knowledge base search

### Option 2: Use the interactive API docs
1. Open http://localhost:8000/docs in your browser
2. Click "Authorize" button
3. Login with your created credentials (create via init_db.py or register via API)
4. Try any endpoint interactively

### Option 3: Using curl

**1. Login to get a token:**
```bash
# Provide USERNAME and PASSWORD via environment (do not print them)
USERNAME={{ADMIN_USERNAME}} PASSWORD={{ADMIN_PASSWORD}} \
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": '"\"$USERNAME\""', "password": '"\"$PASSWORD\""'}'
```

**2. Save the token (replace YOUR_TOKEN):**
```bash
TOKEN="YOUR_TOKEN_HERE"
```

**3. Test health check:**
```bash
curl http://localhost:8000/health
```

**4. Get current user info:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**5. Query AI with RAG:**
```bash
curl -X POST http://localhost:8000/ai/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many vacation days do employees get?",
    "use_rag": true,
    "top_k": 3
  }'
```

**6. Search knowledge base directly:**
```bash
curl -X POST http://localhost:8000/ai/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "remote work policy",
    "top_k": 5
  }'
```

## Available API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info
- `GET /auth/users` - List users (admin only)

### Health
- `GET /` - Root endpoint
- `GET /health` - Health check

### AI & RAG
- `POST /ai/query` - Ask questions (with optional RAG)
  - Parameters: `query`, `context`, `use_rag`, `top_k`
- `POST /ai/search` - Search knowledge base directly
  - Parameters: `query`, `top_k`

### Employees
- `GET /employees/` - List employees
- `GET /employees/{id}` - Get employee details
- `POST /employees/` - Create employee
- `PUT /employees/{id}` - Update employee
- `DELETE /employees/{id}` - Delete employee (admin only)
- `POST /employees/bulk-upload` - Bulk upload from CSV

### Documents
- `GET /documents/` - List documents
- `GET /documents/{id}` - Get document details
- `POST /employees/{id}/documents/` - Upload document
- `POST /documents/{id}/process` - Process with OCR/AI

### Projects, Skills, etc.
- Various CRUD endpoints for projects, skills, specializations

## Testing Example Queries

Here are some questions you can ask the AI (with RAG enabled):

1. **"How many vacation days do employees get per year?"**
   - Should retrieve: "20 days of paid vacation"

2. **"What is the remote work policy?"**
   - Should retrieve: hybrid schedules, requirements, etc.

3. **"What are the promotion criteria?"**
   - Should retrieve: 12 months minimum, performance ratings, etc.

4. **"What professional development budget do employees have?"**
   - Should retrieve: "$2,000 annual budget"

5. **"What are the health benefits?"**
   - Should retrieve: medical, dental, vision, gym membership, etc.

## Project Structure

```
DecideAI/
├── ai_employee_decision_system/    # Main application package
│   ├── api/                        # FastAPI application
│   ├── auth/                       # Authentication
│   ├── core/                       # Core configuration
│   ├── models/                     # Database models
│   └── services/                   # Business logic
│       ├── ai_service.py          # AI query processing with RAG
│       ├── retrieval_service.py   # RAG retrieval wrapper
│       └── vectorstores/          # FAISS/Qdrant implementations
├── data/                           # Data directory
│   ├── employee_system.db         # SQLite database
│   └── workspaces/                # Tenant workspaces
│       └── sample-tenant/
│           ├── documents/         # Source documents
│           └── index/             # FAISS index
├── docs/                           # Documentation
│   ├── RAG_INTEGRATION.md         # Complete RAG docs
│   └── RAG_QUICKSTART.md          # Quick start guide
├── scripts/                        # Utility scripts
│   ├── init_db.py                 # Database initialization
│   ├── index_documents.py         # Document indexing
│   └── test_api.py                # API testing
└── start_server.sh                 # Server startup script
```

## Credentials

Admin user is not created by default. To create one, set environment variables and run:

```bash
DECIDEAI_ADMIN_USERNAME=admin \
DECIDEAI_ADMIN_PASSWORD='StrongRandomPassword!' \
DECIDEAI_ADMIN_EMAIL=admin@example.com \
python3 scripts/init_db.py
```

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
lsof -ti:8000

# Kill the process if needed
kill -9 $(lsof -ti:8000)
```

### Dependencies issues
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

### Database issues
```bash
# Reinitialize database
rm data/employee_system.db
python3 scripts/init_db.py
```

### RAG not working
```bash
# Reindex documents
python3 scripts/index_documents.py
```

## Next Steps

1. **Start the server**: `./start_server.sh`
2. **Run tests**: `python3 scripts/test_api.py` (in new terminal)
3. **Explore the API**: Visit http://localhost:8000/docs
4. **Add more documents**: Place files in `data/workspaces/sample-tenant/documents/` and reindex
5. **Try different queries**: Test the RAG system with various questions

## Documentation

- **RAG Integration**: See `docs/RAG_INTEGRATION.md`
- **Quick Start Guide**: See `docs/RAG_QUICKSTART.md`
- **API Documentation**: http://localhost:8000/docs (when server is running)

## Performance Notes

- First query may be slow (model loading)
- Subsequent queries should be fast (<1 second)
- RAG retrieval adds ~100-200ms overhead
- FAISS index search is sub-millisecond

## Support

If you encounter any issues:
1. Check the server logs in the terminal
2. Review the documentation in `docs/`
3. Run the test script to identify specific issues
4. Check that all dependencies are installed

---

**Status**: ✅ Ready to test!

**Server Command**: `./start_server.sh`

**Test Command**: `python3 scripts/test_api.py`

**API Docs**: http://localhost:8000/docs