# DecideAI

General-purpose multilingual AI backend for HR tasks powered by open models (Ollama) with optional offline operation and Retrieval-Augmented Generation (RAG).

## Overview

DecideAI provides a secure, local-first FastAPI backend that integrates with Ollama (or HuggingFace) for LLM inference, supports multilingual prompting (English, German, Japanese), and includes a FAISS-backed RAG pipeline for knowledge-grounded answers. It is privacy-centric and suitable for SMEs and institutions that require on-prem or offline capability.

### Key Features

- Multilingual (en, de, ja) prompts and responses
- Local/offline LLM inference via Ollama with HuggingFace fallback
- RAG with FAISS vector store and simple retrieval service
- FastAPI backend with authentication (JWT) and role support
- Ingestion and indexing helpers for text/PDF/DOCX/CSV (basic)
- Simple, production-lean repository layout and infra docker-compose

### Directory Structure

```
DecideAI/
├── ai_employee_decision_system/      # Main Python package
│   ├── api/                          # FastAPI app (endpoints)
│   ├── auth/                         # Auth models/services
│   ├── core/                         # Config & logging
│   ├── models/                       # SQLAlchemy models
│   └── services/                     # LLM, RAG, vectorstores, etc.
├── infra/                            # docker-compose.yml
├── scripts/                          # Dev utilities (init_db, index docs, tests)
├── docs/                             # Documentation
├── data/                             # Local data (ignored): db, workspaces/*
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Quick Start

### 1) Install dependencies
```bash
pip3 install -r requirements.txt
```

### 2) Initialize database schema (optional admin)
```bash
python3 scripts/init_db.py
# or create admin non-interactively
DECIDEAI_ADMIN_USERNAME=admin DECIDEAI_ADMIN_PASSWORD='StrongPassword!' \
python3 scripts/init_db.py
```

### 3) Index sample documents (for RAG)
```bash
python3 scripts/index_documents.py
```

### 4) Start API server
```bash
uvicorn ai_employee_decision_system.api.app:app --reload
# API docs: http://localhost:8000/docs
```

## System Requirements

### Minimum Requirements:
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.8+ (automatically checked)

### What Gets Installed:
- ✅ DecideAI HR Helper System
- ✅ Ollama AI Engine (local, private)
- ✅ Required AI models for German/Japanese support
- ✅ Web interface and API

## After Installation

- API Docs: http://localhost:8000/docs
- Create a user via /auth/register or by using scripts/init_db.py with env variables
- Try multilingual queries via /ai/query (en, de, ja)

### Target Institutions

#### German Institutions
- **Universities**: Technical universities, research institutions, Fachhochschulen
- **SMEs**: German Mittelstand companies, startups, consulting firms
- **Compliance**: GDPR-compliant, German labor law awareness

#### Japanese Institutions  
- **Universities**: National, public, and private universities, research institutes
- **SMEs**: Japanese small-medium enterprises, technology companies
- **Cultural Awareness**: Japanese business etiquette, hierarchical structures

## Tech Stack

Backend: FastAPI, SQLAlchemy (SQLite by default), Pydantic
LLM: Ollama (offline) or HuggingFace fallback
RAG: FAISS vector store, sentence-transformers embeddings
Auth: JWT, bcrypt
Infra: docker-compose (optional), GitHub Actions (optional)
Testing: pytest

## Features

- Multilingual HR-focused prompts and responses (en/de/ja)
- Offline/edge deployment with Ollama
- RAG for grounded responses
- Basic ingestion and indexing helpers
- Secure auth and role-based access

## 📈 Business Model

- **Freemium**: Basic features for small teams (up to 10 employees)
- **Professional**: Advanced AI features and integrations ($29/month)
- **Enterprise**: Custom deployment and support ($99/month)
- **White-label**: Partner program for resellers

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

© 2025 DecideAI - HR Helper System