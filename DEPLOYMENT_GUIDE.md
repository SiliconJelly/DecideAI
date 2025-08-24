# AI Employee Decision System - Deployment Guide

## Quick Start Deployment

### Prerequisites
- Python 3.9+ installed
- Docker and Docker Compose installed (optional but recommended)
- Git installed

### Option 1: Local Python Deployment (Recommended for testing)

1. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your settings:
   ```bash
   # Basic configuration for local testing
   EMPLOYEE_SYSTEM_DB_URL=sqlite:///./data/employee_system.db
   EMPLOYEE_SYSTEM_SECRET_KEY=your-secret-key-change-this
   EMPLOYEE_SYSTEM_DEBUG=true
   ```

2. **Install dependencies**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Initialize the database**:
   ```bash
   # Create data directory
   mkdir -p data/uploads data/models
   
   # Initialize database (if alembic is set up)
   # alembic upgrade head
   
   # Or create tables directly
   python -c "
   from ai_employee_decision_system.models import Base, engine
   Base.metadata.create_all(engine)
   print('Database initialized successfully!')
   "
   ```

4. **Create initial admin user**:
   ```bash
   python -c "
   from ai_employee_decision_system.auth import AuthService, UserCreate
   from ai_employee_decision_system.models import db_session
   
   with db_session() as session:
       auth_service = AuthService(session)
       admin_data = UserCreate(
           email='admin@example.com',
           username='admin',
           password='AdminPassword123!',
           first_name='System',
           last_name='Administrator',
           is_admin=True
       )
       user = auth_service.create_user(admin_data)
       if user:
           print('✅ Admin user created successfully')
           print('Username: admin')
           print('Password: AdminPassword123!')
       else:
           print('⚠️  Admin user creation failed or already exists')
   "
   ```

5. **Start the API server**:
   ```bash
   python -m ai_employee_decision_system.api.app
   # Or using uvicorn directly:
   uvicorn ai_employee_decision_system.api.app:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Test the deployment**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Docker Deployment

1. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Deploy with Docker Compose**:
   ```bash
   # Make deploy script executable
   chmod +x scripts/deploy.sh
   
   # Deploy in development mode
   ./scripts/deploy.sh development
   ```

3. **Check services**:
   ```bash
   docker-compose ps
   docker-compose logs app
   ```

## Testing the Deployment

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### 2. Authentication Test
```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "is_admin": false
  }'

# Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

### 3. API Documentation
Visit http://localhost:8000/docs to see the interactive API documentation.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've installed the package with `pip install -e .`
2. **Database Errors**: Ensure the data directory exists and has proper permissions
3. **Port Already in Use**: Change the port in the uvicorn command or stop other services
4. **Permission Errors**: Make sure the deploy script is executable with `chmod +x scripts/deploy.sh`

### Logs
Check logs for debugging:
```bash
# For local deployment
tail -f logs/app.log

# For Docker deployment
docker-compose logs -f app
```