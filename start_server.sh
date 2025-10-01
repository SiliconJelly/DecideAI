#!/bin/bash
# Start the DecideAI Backend Server

echo "=========================================="
echo "  Starting DecideAI Backend Server"
echo "=========================================="
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Start the server
uvicorn ai_employee_decision_system.api.app:app --reload --host 0.0.0.0 --port 8000