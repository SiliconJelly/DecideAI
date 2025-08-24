# AI Employee Decision System API Documentation

## Overview

The AI Employee Decision System API provides a comprehensive set of endpoints for managing employee data, processing documents, and leveraging AI-powered decision support. This RESTful API is built with FastAPI and includes JWT-based authentication, automatic OpenAPI documentation, and comprehensive error handling.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.example.com`

## Authentication

The API uses JWT (JSON Web Token) authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Getting Started

1. **Register a new user**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "user@example.com",
          "username": "username",
          "password": "SecurePassword123!",
          "first_name": "John",
          "last_name": "Doe",
          "is_admin": false
        }'
   ```

2. **Login to get access token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
          "username": "username",
          "password": "SecurePassword123!"
        }'
   ```

3. **Use the token in subsequent requests**:
   ```bash
   curl -X GET "http://localhost:8000/employees/" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and get access token | No |
| GET | `/auth/me` | Get current user info | Yes |
| GET | `/auth/users` | Get all users (admin only) | Yes (Admin) |
| PUT | `/auth/users/{user_id}/status` | Update user status (admin only) | Yes (Admin) |

### Employee Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/employees/` | Get all employees | Yes |
| GET | `/employees/{employee_id}` | Get employee by ID | Yes |
| POST | `/employees/` | Create new employee | Yes |
| PUT | `/employees/{employee_id}` | Update employee | Yes |
| DELETE | `/employees/{employee_id}` | Delete employee (admin only) | Yes (Admin) |

### Document Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/documents/` | Get all documents | Yes |
| GET | `/documents/{document_id}` | Get document by ID | Yes |
| POST | `/employees/{employee_id}/documents/` | Upload document for employee | Yes |
| POST | `/documents/{document_id}/process` | Process document with OCR/AI | Yes |

### Project Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/projects/` | Get all projects | Yes |
| POST | `/projects/` | Create new project | Yes |

### Skills Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/skills/` | Get all skills | Yes |
| POST | `/skills/` | Create new skill | Yes |

### AI Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/ai/query` | Process natural language query | Yes |

## Data Models

### User Model

```json
{
  "id": "uuid",
  "email": "string",
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "is_active": "boolean",
  "is_admin": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime"
}
```

### Employee Model

```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "department": "string",
  "position": "string",
  "hire_date": "date",
  "is_active": "boolean",
  "skills": ["skill_objects"],
  "specializations": ["specialization_objects"],
  "documents": ["document_objects"]
}
```

### Document Model

```json
{
  "id": "uuid",
  "name": "string",
  "type": "string",
  "file_path": "string",
  "mime_type": "string",
  "size": "integer",
  "processing_status": "string",
  "processing_level": "integer",
  "extraction_confidence": "integer",
  "extracted_data": "json",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Error Handling

The API returns standard HTTP status codes and detailed error messages:

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated users**: 100 requests per minute
- **Unauthenticated endpoints**: 10 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Pagination

List endpoints support pagination with query parameters:

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100, max: 1000)

Example:
```bash
curl "http://localhost:8000/employees/?skip=20&limit=10" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## File Upload

Document upload endpoints accept multipart/form-data:

### Supported File Types
- PDF files (.pdf)
- Image files (.jpg, .jpeg, .png, .tiff, .bmp)
- Maximum file size: 10MB

### Upload Example
```bash
curl -X POST "http://localhost:8000/employees/{employee_id}/documents/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@document.pdf" \
     -F "document_type=CV"
```

## Natural Language Queries

The AI endpoint supports natural language queries for employee recommendations:

### Example Queries
- "Who is the best employee for a Python project?"
- "What are the skills of John Doe?"
- "Suggest a team of 5 for a machine learning project"

### Query Example
```bash
curl -X POST "http://localhost:8000/ai/query" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Who is the best employee for a Python project?",
       "context": {"skills": ["Python", "Django"]}
     }'
```

## Interactive Documentation

The API provides interactive documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- Explore all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- Understand authentication requirements

## SDK and Client Libraries

### Python Client Example

```python
import requests

class AIEmployeeSystemClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, username, password):
        response = self.session.post(
            f'{self.base_url}/auth/login',
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            self.token = response.json()['access_token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
        return response.json()
    
    def get_employees(self, skip=0, limit=100):
        response = self.session.get(
            f'{self.base_url}/employees/',
            params={'skip': skip, 'limit': limit}
        )
        return response.json()
    
    def query_ai(self, query, context=None):
        data = {'query': query}
        if context:
            data['context'] = context
        response = self.session.post(
            f'{self.base_url}/ai/query',
            json=data
        )
        return response.json()

# Usage
client = AIEmployeeSystemClient('http://localhost:8000')
client.login('username', 'password')
employees = client.get_employees()
ai_response = client.query_ai('Who is the best Python developer?')
```

### JavaScript Client Example

```javascript
class AIEmployeeSystemClient {
    constructor(baseUrl, token = null) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        if (response.ok) {
            const data = await response.json();
            this.token = data.access_token;
            return data;
        }
        throw new Error('Login failed');
    }
    
    async getEmployees(skip = 0, limit = 100) {
        const response = await fetch(
            `${this.baseUrl}/employees/?skip=${skip}&limit=${limit}`,
            {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            }
        );
        return response.json();
    }
    
    async queryAI(query, context = null) {
        const body = { query };
        if (context) body.context = context;
        
        const response = await fetch(`${this.baseUrl}/ai/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`,
            },
            body: JSON.stringify(body),
        });
        return response.json();
    }
}

// Usage
const client = new AIEmployeeSystemClient('http://localhost:8000');
await client.login('username', 'password');
const employees = await client.getEmployees();
const aiResponse = await client.queryAI('Who is the best Python developer?');
```

## Best Practices

### Security
- Always use HTTPS in production
- Store JWT tokens securely (not in localStorage for web apps)
- Implement proper token refresh mechanisms
- Validate all input data
- Use strong passwords and enforce password policies

### Performance
- Use pagination for large datasets
- Implement caching where appropriate
- Compress large responses
- Use appropriate HTTP methods (GET for retrieval, POST for creation, etc.)

### Error Handling
- Always check response status codes
- Implement retry logic for transient failures
- Log errors appropriately
- Provide meaningful error messages to users

## Support

For API support and questions:
- **Email**: support@example.com
- **GitHub Issues**: https://github.com/your-org/ai-employee-decision-system/issues
- **Documentation**: https://docs.example.com

## Changelog

### Version 1.0.0 (Current)
- Initial API release
- JWT authentication
- Employee management
- Document processing
- AI-powered queries
- Comprehensive documentation