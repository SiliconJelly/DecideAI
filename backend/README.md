# Backend for Kiro Smart OCR

This directory contains the FastAPI backend for Kiro Smart OCR, providing API endpoints for document processing, user management, and system administration.

## Directory Structure

```
backend/
├── app/                    # Application code
│   ├── api/                # API endpoints
│   │   ├── v1/             # API version 1
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── documents.py # Document processing endpoints
│   │   │   ├── users.py    # User management endpoints
│   │   │   └── admin.py    # Admin endpoints
│   │   └── api.py          # API router
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration management
│   │   ├── security.py     # Security utilities
│   │   ├── logging.py      # Logging configuration
│   │   └── errors.py       # Error handling
│   ├── models/             # Data models
│   │   ├── ocr.py          # OCR models
│   │   ├── user.py         # User models
│   │   └── document.py     # Document models
│   ├── services/           # Business logic
│   │   ├── ocr_service.py  # OCR service
│   │   ├── llm_service.py  # LLM service
│   │   ├── auth_service.py # Authentication service
│   │   └── storage_service.py # Storage service
│   └── main.py             # Application entry point
└── tests/                  # Tests
    ├── api/                # API tests
    ├── services/           # Service tests
    └── conftest.py         # Test configuration
```

## API Endpoints

### Document Processing

- `POST /api/v1/documents`: Upload and process a document
- `GET /api/v1/documents/{document_id}`: Get document details
- `GET /api/v1/documents`: List documents
- `PUT /api/v1/documents/{document_id}`: Update document (corrections)
- `DELETE /api/v1/documents/{document_id}`: Delete document

### Authentication

- `POST /api/v1/auth/login`: User login
- `POST /api/v1/auth/register`: User registration
- `POST /api/v1/auth/refresh`: Refresh access token
- `POST /api/v1/auth/logout`: User logout

### User Management

- `GET /api/v1/users/me`: Get current user
- `PUT /api/v1/users/me`: Update current user
- `GET /api/v1/users`: List users (admin only)
- `POST /api/v1/users`: Create user (admin only)
- `PUT /api/v1/users/{user_id}`: Update user (admin only)
- `DELETE /api/v1/users/{user_id}`: Delete user (admin only)

### Organization Management

- `GET /api/v1/organizations`: List organizations (admin only)
- `POST /api/v1/organizations`: Create organization (admin only)
- `GET /api/v1/organizations/{org_id}`: Get organization details
- `PUT /api/v1/organizations/{org_id}`: Update organization
- `DELETE /api/v1/organizations/{org_id}`: Delete organization (admin only)

### System Administration

- `GET /api/v1/admin/stats`: Get system statistics
- `GET /api/v1/admin/logs`: Get system logs
- `POST /api/v1/admin/models`: Update AI models

## Development

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 7+

### Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:

```bash
uvicorn app.main:app --reload
```

### Testing

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app
```

## Deployment

### Docker

Build and run with Docker:

```bash
docker build -t kiro-smart-ocr-backend .
docker run -p 8000:8000 kiro-smart-ocr-backend
```

### Docker Compose

Run with Docker Compose:

```bash
docker-compose up -d
```

### Kubernetes

Deploy to Kubernetes:

```bash
kubectl apply -f deployment/kubernetes/backend-deployment.yaml
```