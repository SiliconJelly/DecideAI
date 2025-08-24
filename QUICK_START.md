# AI Employee Decision System - Quick Start Guide

## 🚀 Quick Deployment (5 minutes)

### Step 1: Initialize the System
```bash
# Run the initialization script
python init_system.py
```

This will:
- Create necessary directories (`data/`, `logs/`, etc.)
- Set up the database
- Create an admin user
- Generate a `.env` configuration file

### Step 2: Start the System
```bash
# Start the API server
python start_system.py
```

### Step 3: Test the Deployment
```bash
# In a new terminal, run the test script
python test_deployment.py
```

## 🎯 Access Points

Once running, you can access:

- **API Server**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Default Credentials

- **Username**: `admin`
- **Password**: `AdminPassword123!`
- **Email**: `admin@example.com`

## 🧪 Manual Testing Steps

### 1. Test Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test User Registration
```bash
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
```

### 3. Test Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

Save the `access_token` from the response for the next steps.

### 4. Test Protected Endpoint
```bash
# Replace YOUR_TOKEN with the actual token from step 3
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Test Employee Management
```bash
# Create an employee
curl -X POST "http://localhost:8000/employees/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "department": "Engineering",
    "position": "Software Developer"
  }'

# Get all employees
curl -X GET "http://localhost:8000/employees/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Test AI Query
```bash
curl -X POST "http://localhost:8000/ai/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who is the best employee for a Python project?",
    "context": {"skills": ["Python"]}
  }'
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Test deployment
python test_deployment.py
```

## 🔧 Troubleshooting

### Common Issues

1. **Port 8000 already in use**:
   ```bash
   # Find and kill the process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Import errors**:
   ```bash
   # Make sure you're in the right directory and have installed the package
   pip install -e .
   ```

3. **Database errors**:
   ```bash
   # Remove the database and reinitialize
   rm -f data/employee_system.db
   python init_system.py
   ```

4. **Permission errors**:
   ```bash
   # Make scripts executable
   chmod +x *.py
   chmod +x scripts/*.sh
   ```

### Checking Logs

```bash
# Check application logs
tail -f logs/app.log

# For Docker deployment
docker-compose logs -f app
```

### Resetting the System

```bash
# Stop the server (Ctrl+C)
# Remove data and reinitialize
rm -rf data/ logs/
python init_system.py
python start_system.py
```

## 📊 What to Test

### Core Features
- ✅ User authentication (register, login, logout)
- ✅ Employee management (create, read, update, delete)
- ✅ Document upload and processing
- ✅ AI-powered queries
- ✅ Project management
- ✅ Skills and specializations

### API Features
- ✅ Interactive API documentation
- ✅ Authentication middleware
- ✅ Error handling
- ✅ Input validation
- ✅ Response formatting

### Security Features
- ✅ JWT token authentication
- ✅ Password hashing
- ✅ Role-based access control
- ✅ Input sanitization

## 🎉 Next Steps

Once the system is running successfully:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Create test data**: Add employees, skills, and projects
3. **Upload documents**: Test the OCR and AI processing
4. **Try AI queries**: Ask natural language questions
5. **Test different user roles**: Create admin and regular users
6. **Customize configuration**: Update the `.env` file as needed

## 📞 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify the database is properly initialized
5. Check that all required ports are available

## 🏆 Success Indicators

You'll know the deployment is successful when:

- ✅ Health check returns `{"status": "healthy"}`
- ✅ API documentation is accessible at `/docs`
- ✅ User registration and login work
- ✅ Protected endpoints require authentication
- ✅ Employee CRUD operations work
- ✅ AI queries return responses
- ✅ All tests in `test_deployment.py` pass

Happy testing! 🚀