"""
API documentation configuration for the AI Employee Decision System.
"""
from typing import Dict, Any

# API metadata
API_METADATA = {
    "title": "AI Employee Decision System API",
    "description": """
# AI Employee Decision System API

A comprehensive API for managing employee data, documents, and AI-powered decision support.

## Features

- **Employee Management**: Create, read, update, and delete employee profiles
- **Document Processing**: Upload and process CVs with OCR and AI analysis
- **AI Decision Support**: Natural language queries for employee recommendations
- **Project Management**: Manage projects and team assignments
- **Skills & Specializations**: Track employee skills and specializations
- **Authentication**: Secure JWT-based authentication system

## Authentication

This API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. Register a new user account using `/auth/register`
2. Login using `/auth/login` to get an access token
3. Include the token in the Authorization header: `Bearer <your_token>`

## Rate Limiting

API requests are rate-limited to prevent abuse. Current limits:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated endpoints

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

Error responses include a detailed message and error code for debugging.

## Data Formats

All API endpoints accept and return JSON data. Date/time values are in ISO 8601 format.

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100, max: 1000)

## Supported File Types

Document upload endpoints support:
- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png, .tiff, .bmp)
- Maximum file size: 10MB

## API Versioning

This is version 1.0 of the API. Future versions will be available at `/v2/`, `/v3/`, etc.
    """,
    "version": "1.0.0",
    "contact": {
        "name": "AI Employee Decision System Support",
        "email": "support@example.com",
        "url": "https://github.com/your-org/ai-employee-decision-system",
    },
    "license": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# Tags for organizing endpoints
TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization endpoints",
    },
    {
        "name": "Employees",
        "description": "Employee management operations",
    },
    {
        "name": "Documents",
        "description": "Document upload and processing operations",
    },
    {
        "name": "Projects",
        "description": "Project management operations",
    },
    {
        "name": "Skills",
        "description": "Skills and specializations management",
    },
    {
        "name": "AI",
        "description": "AI-powered decision support and natural language queries",
    },
]

# Security schemes
SECURITY_SCHEMES = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token obtained from /auth/login endpoint",
    }
}

# Example responses
EXAMPLE_RESPONSES = {
    "401": {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid authentication credentials"
                }
            }
        }
    },
    "403": {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Not enough permissions"
                }
            }
        }
    },
    "404": {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Resource not found"
                }
            }
        }
    },
    "422": {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["body", "email"],
                            "msg": "field required",
                            "type": "value_error.missing"
                        }
                    ]
                }
            }
        }
    },
    "500": {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal server error"
                }
            }
        }
    }
}

# OpenAPI configuration
def get_openapi_config() -> Dict[str, Any]:
    """Get OpenAPI configuration."""
    return {
        "openapi": "3.0.2",
        "info": API_METADATA,
        "tags": TAGS_METADATA,
        "components": {
            "securitySchemes": SECURITY_SCHEMES
        },
        "security": [{"bearerAuth": []}],
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.example.com",
                "description": "Production server"
            }
        ]
    }