#!/bin/bash
# Kiro Smart OCR Deployment Script

set -e

# Configuration
ENVIRONMENT=${1:-production}
IMAGE_TAG=${2:-latest}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"kiro-registry.example.com"}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying Kiro Smart OCR to ${ENVIRONMENT} environment with tag ${IMAGE_TAG}${NC}"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl is not installed. Please install kubectl and try again.${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

# Set Kubernetes context based on environment
case $ENVIRONMENT in
    production)
        KUBE_CONTEXT="production-cluster"
        ;;
    staging)
        KUBE_CONTEXT="staging-cluster"
        ;;
    development)
        KUBE_CONTEXT="dev-cluster"
        ;;
    *)
        echo -e "${RED}Invalid environment: ${ENVIRONMENT}. Must be production, staging, or development.${NC}"
        exit 1
        ;;
esac

echo -e "${YELLOW}Setting Kubernetes context to ${KUBE_CONTEXT}...${NC}"
kubectl config use-context $KUBE_CONTEXT

# Create namespace if it doesn't exist
echo -e "${YELLOW}Creating namespace if it doesn't exist...${NC}"
kubectl apply -f kubernetes/namespace.yaml

# Apply secrets
echo -e "${YELLOW}Applying secrets...${NC}"
kubectl apply -f kubernetes/database-deployment.yaml --namespace=kiro-smart-ocr
kubectl apply -f kubernetes/redis-deployment.yaml --namespace=kiro-smart-ocr

# Create app secrets if they don't exist
if ! kubectl get secret kiro-app-secrets --namespace=kiro-smart-ocr &> /dev/null; then
    echo -e "${YELLOW}Creating app secrets...${NC}"
    # Generate random secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    
    # Create secret
    kubectl create secret generic kiro-app-secrets \
        --from-literal=secret-key=$SECRET_KEY \
        --from-literal=jwt-secret-key=$JWT_SECRET_KEY \
        --namespace=kiro-smart-ocr
fi

# Apply storage resources
echo -e "${YELLOW}Applying storage resources...${NC}"
kubectl apply -f kubernetes/storage.yaml

# Apply database and Redis deployments
echo -e "${YELLOW}Deploying database and Redis...${NC}"
kubectl apply -f kubernetes/database-deployment.yaml
kubectl apply -f kubernetes/redis-deployment.yaml

# Wait for database and Redis to be ready
echo -e "${YELLOW}Waiting for database and Redis to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=kiro-postgres --timeout=300s --namespace=kiro-smart-ocr
kubectl wait --for=condition=ready pod -l app=kiro-redis --timeout=300s --namespace=kiro-smart-ocr

# Build and push Docker images
echo -e "${YELLOW}Building and pushing Docker images...${NC}"
docker build -t ${DOCKER_REGISTRY}/kiro-smart-ocr-backend:${IMAGE_TAG} -f docker/Dockerfile ../..
docker push ${DOCKER_REGISTRY}/kiro-smart-ocr-backend:${IMAGE_TAG}

docker build -t ${DOCKER_REGISTRY}/kiro-smart-ocr-frontend:${IMAGE_TAG} -f docker/Dockerfile.frontend ../..
docker push ${DOCKER_REGISTRY}/kiro-smart-ocr-frontend:${IMAGE_TAG}

# Replace placeholders in deployment files
echo -e "${YELLOW}Preparing deployment files...${NC}"
sed -i "s|\${DOCKER_REGISTRY}|${DOCKER_REGISTRY}|g" kubernetes/backend-deployment.yaml
sed -i "s|\${IMAGE_TAG}|${IMAGE_TAG}|g" kubernetes/backend-deployment.yaml
sed -i "s|\${DOCKER_REGISTRY}|${DOCKER_REGISTRY}|g" kubernetes/frontend-deployment.yaml
sed -i "s|\${IMAGE_TAG}|${IMAGE_TAG}|g" kubernetes/frontend-deployment.yaml

# Apply backend and frontend deployments
echo -e "${YELLOW}Deploying backend and frontend...${NC}"
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/frontend-deployment.yaml

# Wait for deployments to be ready
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available deployment/kiro-backend --timeout=300s --namespace=kiro-smart-ocr
kubectl wait --for=condition=available deployment/kiro-frontend --timeout=300s --namespace=kiro-smart-ocr

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Backend API is available at: https://api.kiro-ocr.com${NC}"
echo -e "${GREEN}Frontend is available at: https://kiro-ocr.com${NC}"