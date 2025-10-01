# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: DecideAI — AI-powered HR decision support for German & Japanese institutions

Repository orientation
- Primary backend API: ai_employee_decision_system/api/app.py (FastAPI)
- Primary UI: ai_employee_decision_system/ui/app.py (Gradio, launches via python -m ai_employee_decision_system)
- Domain model and services: ai_employee_decision_system/models/* and ai_employee_decision_system/services/*
- Next.js app: frontend/ (independent web app)
- One-click orchestration: START_DECIDEAI.py and DEPLOY_DECIDEAI.py

1) Commands you will commonly use

Environment bootstrap
- Create venv and install deps
  - python -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt
  - pip install -e .
- Install dev extras (lint/format/test helpers)
  - pip install -e .[dev]
  - or: make dev-install

Configuration and initialization
- Initialize directories, DB, and default admin
  - python init_system.py
- CLI entry points
  - ai-employee-system init-db
  - ai-employee-system version
- Environment variables (read by ai_employee_decision_system/core/config.py)
  - EMPLOYEE_SYSTEM_DB_URL (default sqlite:///./data/employee_system.db)
  - EMPLOYEE_SYSTEM_SECRET_KEY
  - EMPLOYEE_SYSTEM_JWT_ALGORITHM (default HS256)
  - EMPLOYEE_SYSTEM_JWT_EXPIRE_MINUTES (default 30)
  - EMPLOYEE_SYSTEM_DEBUG (true/false)

Running services locally
- API (FastAPI via Uvicorn)
  - uvicorn ai_employee_decision_system.api.app:app --reload --host 0.0.0.0 --port 8000
- UI (Gradio; launches full UI against local API)
  - python -m ai_employee_decision_system --debug
  - The UI expects API at http://localhost:8000
- Orchestrated start (manages Ollama → API → UI in order)
  - python START_DECIDEAI.py
- Frontend (Next.js)
  - cd frontend && npm install
  - npm run dev         # http://localhost:3000
  - npm run build && npm start

LLM/Ollama helpers
- Verify Ollama and basic health
  - python check_ollama_health.py
- Make sure models exist (examples)
  - ollama list
  - ollama pull llama3.2:3b

Linting and formatting (Python)
- make lint              # flake8 ai_employee_decision_system tests
- make format            # black + isort

Testing
- Run all tests (pytest.ini sets testpaths=tests and coverage)
  - pytest
- Run single test file
  - pytest tests/test_config.py -q
- Run single test function
  - pytest tests/test_config.py::test_config_defaults -q
- Coverage (already configured via addopts)
  - pytest --cov=ai_employee_decision_system --cov-report=term-missing
- System integration tests
  - python test_ai_system.py
  - python check_ollama_health.py

Packaging/build
- Build sdist and wheel
  - python setup.py sdist bdist_wheel
  - or: make dist

Notes about Docker/compose
- docker-compose.yml references Dockerfile.api, Dockerfile.ui, Dockerfile.model-init and deployment/nginx/*.
  - These files are not present in this tree. Compose will fail until those Dockerfiles and configs are added.

API testing with curl
- Health check
  - curl http://localhost:8000/health
- Login and get JWT token
  - curl -X POST "http://localhost:8000/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "AdminPassword123!"}'
- Use JWT token for authenticated requests
  - export TOKEN="your_jwt_token_here"
  - curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/employees/
- Add employee
  - curl -X POST "http://localhost:8000/employees/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"first_name": "John", "last_name": "Doe", "email": "john@company.com", "position": "Developer", "department": "Engineering"}'
- AI query
  - curl -X POST "http://localhost:8000/ai/query" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"query": "Who are our employees?"}'
- Bulk upload employees via CSV
  - curl -X POST "http://localhost:8000/employees/bulk-upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@sample_employees.csv"

2) High-level architecture and flow

Overview
- The system is a modular FastAPI backend with a Gradio UI and optional Next.js frontend. It integrates a local LLM (Ollama) with multilingual and cultural-context handling for German and Japanese HR use cases.

Key modules
- core/
  - config.py: Centralized AppConfig (database, security/JWT, AI, localization). Reads EMPLOYEE_SYSTEM_* env vars. Ensures data and model directories exist.
  - logging.py: Structured JSON logging to logs/app.log and console; toggles format based on debug.
- models/ (SQLAlchemy ORM + Pydantic schemas)
  - base.py: BaseModel with UUID primary key, created_at/updated_at, to_dict serialization with ISO timestamps.
  - database.py: Engine/session management; db_session context manager; init_db creates tables.
  - user.py, employee.py (+ Tag association), document.py, project.py (+ team associations), skill.py (+ Specialization), validation.py (Pydantic create/update schemas and validation rules).
- auth/
  - password_utils.py, jwt_handler.py, models.py (Token/TokenData/UserCreate etc.), auth_service.py (CRUD/auth, password hashing, JWT issuance/verification).
- services/ (business logic)
  - EmployeeService, DocumentService, ProjectService, SkillService, SpecializationService, TagService: CRUD and operations with audit patterns; FileStorage handles encrypted storage and “normalization” stubs.
  - LLM and AI orchestration (sophisticated multi-tier system):
    - ollama_service.py: Thin client over Ollama /api (generate/chat/list/pull/delete) with streaming, metrics, model health checks.
    - llm_service.py: Higher-level LLM wrapper (OllamaLLMService, HuggingFaceLLMService) that auto-detects available models, pulls if needed, provides intelligent fallbacks with cultural context when Ollama unavailable.
    - language_service.py: Advanced language detection (EN/DE/JA) via heuristic features (hiragana/katakana/kanji detection, German umlauts/compounds, English contractions); cultural context provider; formatting by language with business/formal/casual modes.
    - multilingual_llm_service.py: End-to-end flow: detect/validate language → select model via ModelManager → prepare culturally appropriate system prompt → generate → format response → compute confidence. Caches language-specific models.
    - ai_orchestrator.py: Central orchestrator - chooses best backend (OLLAMA → STANDALONE → FALLBACK), tracks backend health with 30s intervals, retries/timeouts, returns AIResponse with rich metadata including processing time, confidence scores, fallback usage.
    - model_manager.py: Model lifecycle management (download, version, performance tracking, recommendations by use case/language/performance tier).
    - service_orchestration.py: Production-ready process orchestration for local dev runtime (start/stop Ollama, API, UI with health checks, dependency order, graceful shutdown). Used by START_DECIDEAI.py.
    - production_ai_service.py, response_formatter.py, prompt_engineering.py: Production enhancements for enterprise deployment.
- api/
  - app.py: FastAPI app with CORS; health; JWT-protected resources; endpoints for auth, employees, documents (upload + OCR/processing placeholder), projects, skills; /ai/query routes to AIService (backed by LLM pipeline).
  - docs.py: OpenAPI metadata, tags, example responses.
- ui/
  - app.py: Gradio Blocks app. Handles login (JWT), "Ask AI," employee CRUD, bulk CSV upload, and document upload. Talks to API via requests, expects API at :8000.
- frontend/ (Next.js 15.4.1 with React 19)
  - Standalone React app with TypeScript, ESLint
  - package.json: npm run dev (turbopack), build, start, lint
  - Independent from the Gradio UI - can run simultaneously
  - Expected to connect to same FastAPI backend at :8000
- cli.py and __main__.py
  - ai-employee-system console script exposes init-db/version; python -m ai_employee_decision_system starts the Gradio UI after ensuring config/db setup.

Data and request flow (typical path)
- UI → API (JWT bearer)
- API endpoint → corresponding Service (e.g., EmployeeService/DocumentService)
- Services → models/database for persistence; FileStorage for secure file operations
- /ai/query → AIService → LLM pipeline (OllamaService/LanguageService/MultilingualLLMService/AIOrchestrator) → response formatted by language and context

Security and auth
- JWT via HS256 (configurable) with expiry from EMPLOYEE_SYSTEM_JWT_EXPIRE_MINUTES.
- AuthService handles user creation, login, status updates, and permission flags; get_current_user/get_current_admin_user dependencies protect routes.

Localization and cultural context
- Default language en; available languages [en, de, ja] (core/config.py). i18n setup in utils/i18n.py. LanguageService adds cultural formatting rules per language.

Logging and observability
- Structured logs to logs/app.log. Service orchestration logs to logs/service_orchestration.log. Health endpoints: /health for API; Ollama health via /api/tags.

Important references from repo docs
- README.md: Quick start options, ports, and default login (admin / AdminPassword123!) and endpoints:
  - Web UI: http://localhost:7860
  - API docs: http://localhost:8000/docs
- DEPLOYMENT_GUIDE.md: Local dev path (pip install -r requirements.txt; uvicorn ai_employee_decision_system.api.app:app --reload) and environment variable setup. Mirrors the commands listed above.
- TESTING_GUIDE.md: Use python check_ollama_health.py and python test_ollama_integration.py to validate Ollama setup and integration.

Caveats and gotchas
- docker-compose.yml references Dockerfile.api/ui/model-init and deployment/nginx/* which are not in this tree—compose won’t work until those files exist.
- backend/ appears to be a separate/legacy FastAPI skeleton; the active API lives under ai_employee_decision_system/api/app.py.
- start_full_system.py references start_ui.py which is not in the repo. Prefer python -m ai_employee_decision_system or python START_DECIDEAI.py.
