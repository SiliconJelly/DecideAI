#!/bin/bash

# AI Employee Decision System Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo -e "${GREEN}🚀 Deploying AI Employee Decision System (${ENVIRONMENT})${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update the .env file with your configuration before continuing.${NC}"
    read -p "Press Enter to continue after updating .env file..."
fi

# Create necessary directories
echo -e "${GREEN}📁 Creating directories...${NC}"
mkdir -p data/uploads data/models logs backups ssl

# Set proper permissions
echo -e "${GREEN}🔒 Setting permissions...${NC}"
chmod 755 data/uploads data/models logs backups
chmod 600 .env

# Pull latest images
echo -e "${GREEN}📥 Pulling Docker images...${NC}"
docker-compose -f $COMPOSE_FILE pull

# Build application image
echo -e "${GREEN}🔨 Building application...${NC}"
docker-compose -f $COMPOSE_FILE build

# Stop existing containers
echo -e "${GREEN}🛑 Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${GREEN}🏥 Checking service health...${NC}"

# Check database
if docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is ready${NC}"
else
    echo -e "${RED}❌ Database is not ready${NC}"
    exit 1
fi

# Check Redis
if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready${NC}"
    exit 1
fi

# Check application
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Application is ready${NC}"
else
    echo -e "${RED}❌ Application is not ready${NC}"
    exit 1
fi

# Run database migrations
echo -e "${GREEN}🗄️  Running database migrations...${NC}"
docker-compose -f $COMPOSE_FILE exec app alembic upgrade head

# Create initial admin user (only in development)
if [ "$ENVIRONMENT" = "development" ]; then
    echo -e "${GREEN}👤 Creating initial admin user...${NC}"
    docker-compose -f $COMPOSE_FILE exec app python -c "
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
        print('⚠️  Admin user already exists or creation failed')
"
fi

# Display service URLs
echo -e "${GREEN}🌐 Services are now available at:${NC}"
echo -e "  API: http://localhost:8000"
echo -e "  API Documentation: http://localhost:8000/docs"
echo -e "  Web Interface: http://localhost:7860"

if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "  Nginx: http://localhost:80"
    echo -e "  Monitoring: http://localhost:3000 (Grafana)"
    echo -e "  Metrics: http://localhost:9090 (Prometheus)"
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Show logs
echo -e "${GREEN}📋 Showing recent logs...${NC}"
docker-compose -f $COMPOSE_FILE logs --tail=50

echo -e "${GREEN}🎉 AI Employee Decision System is now running!${NC}"