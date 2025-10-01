# Server Management Commands

## Server is Currently Running ✅

Your DecideAI backend server is **running right now** in the background!

- **PID**: 16471
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Logs**: `server.log`

## Server Management

### Check if server is running
```bash
ps aux | grep "uvicorn ai_employee_decision_system.api.app:app" | grep -v grep
```

### View server logs
```bash
tail -f server.log
```

### Stop the server
```bash
kill 16471
```

Or find and kill:
```bash
kill $(ps aux | grep "uvicorn ai_employee_decision_system.api.app:app" | grep -v grep | awk '{print $2}')
```

### Start the server (if stopped)

**Option 1: Foreground (with live logs)**
```bash
uvicorn ai_employee_decision_system.api.app:app --reload
```

**Option 2: Background**
```bash
nohup uvicorn ai_employee_decision_system.api.app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

**Option 3: Using the startup script**
```bash
./start_server.sh
```

## Quick Test Commands

### Test from command line
```bash
# Health check
curl http://localhost:8000/health

# Login (provide credentials via environment)
USERNAME={{ADMIN_USERNAME}} PASSWORD={{ADMIN_PASSWORD}} \
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": '"\"$USERNAME\""', "password": '"\"$PASSWORD\""'}'
```

### Run full test suite
```bash
python3 scripts/test_api.py
```

## Access Points

### Interactive API Documentation
Open in browser: **http://localhost:8000/docs**
- Click "Authorize"
- Login with your created credentials
- Try endpoints interactively

### Alternative Documentation
Open in browser: **http://localhost:8000/redoc**

### Root Endpoint
```bash
curl http://localhost:8000/
```

## Test Results Summary

✅ **All 6 Tests Passed Successfully!**

1. ✓ Health Check
2. ✓ Authentication
3. ✓ Get Current User
4. ✓ AI Query (without RAG)
5. ✓ AI Query (with RAG)
6. ✓ Direct Knowledge Base Search

## Example API Calls

### Get Auth Token (without printing secret)
```bash
# Provide USERNAME and PASSWORD via environment variables; avoid printing them
USERNAME={{ADMIN_USERNAME}} PASSWORD={{ADMIN_PASSWORD}} \
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": '"\"$USERNAME\""', "password": '"\"$PASSWORD\""'}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

### Query AI with RAG
```bash
curl -X POST http://localhost:8000/ai/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many vacation days do employees get?",
    "use_rag": true,
    "top_k": 3
  }' | python3 -m json.tool
```

### Search Knowledge Base
```bash
curl -X POST http://localhost:8000/ai/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "remote work",
    "top_k": 5
  }' | python3 -m json.tool
```

### Create an Employee
```bash
curl -X POST http://localhost:8000/employees/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "position": "Software Engineer",
    "department": "Engineering"
  }' | python3 -m json.tool
```

### List Employees
```bash
curl -X GET http://localhost:8000/employees/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Troubleshooting

### Port already in use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 $(lsof -ti:8000)
```

### Server won't start
```bash
# Check logs
cat server.log

# Check Python path
which python3

# Reinstall dependencies
pip3 install -r requirements.txt
```

### Database errors
```bash
# Reset database
rm data/employee_system.db
python3 scripts/init_db.py
```

## Credentials

Admin user is not created by default. To create one, set environment variables and run the init script:

```bash
DECIDEAI_ADMIN_USERNAME=admin \
DECIDEAI_ADMIN_PASSWORD='StrongRandomPassword!' \
DECIDEAI_ADMIN_EMAIL=admin@example.com \
python3 scripts/init_db.py
```

## Files

- **Server Log**: `server.log`
- **Database**: `data/employee_system.db`
- **FAISS Index**: `data/workspaces/sample-tenant/index/`
- **Documents**: `data/workspaces/sample-tenant/documents/`

## Next Steps

1. **Open API docs**: http://localhost:8000/docs
2. **Try some queries**: Use the test examples above
3. **Add more documents**: Place files in `data/workspaces/sample-tenant/documents/` and run `python3 scripts/index_documents.py`
4. **Explore endpoints**: Check out all available endpoints in the docs

---

**Current Status**: 🟢 Server is running on PID 16471