# Deployment for Kiro Smart OCR

This directory contains deployment configurations and scripts for Kiro Smart OCR.

## Directory Structure

```
deployment/
├── docker/                 # Docker configurations
│   ├── Dockerfile          # Backend Dockerfile
│   ├── Dockerfile.frontend # Frontend Dockerfile
│   └── docker-compose.yml  # Docker Compose configuration
├── kubernetes/             # Kubernetes manifests
│   ├── namespace.yaml      # Namespace configuration
│   ├── backend-deployment.yaml # Backend deployment
│   ├── frontend-deployment.yaml # Frontend deployment
│   ├── database-deployment.yaml # Database deployment
│   ├── redis-deployment.yaml # Redis deployment
│   └── storage.yaml        # Persistent volume claims
└── scripts/                # Deployment scripts
    ├── deploy.sh           # Main deployment script
    ├── backup.sh           # Database backup script
    └── update-models.sh    # AI model update script
```

## Deployment Options

### Docker Deployment

For local development or small-scale deployments:

```bash
cd docker
docker-compose up -d
```

This will start:
- Backend API
- Frontend web application
- PostgreSQL database
- Redis cache
- Prometheus monitoring
- Grafana dashboards

### Kubernetes Deployment

For production deployments:

```bash
cd scripts
./deploy.sh production latest
```

This will deploy:
- Backend API with auto-scaling
- Frontend with Ingress
- PostgreSQL StatefulSet
- Redis deployment
- Persistent volumes for data storage
- Monitoring and logging infrastructure

## Configuration

### Environment Variables

The deployment scripts use the following environment variables:

- `ENVIRONMENT`: Deployment environment (development, staging, production)
- `IMAGE_TAG`: Docker image tag
- `DOCKER_REGISTRY`: Docker registry URL
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL

### Secrets Management

Kubernetes secrets are used for sensitive information:

- `kiro-app-secrets`: Application secrets
- `kiro-db-credentials`: Database credentials
- `kiro-redis-credentials`: Redis credentials

## Scaling

### Horizontal Scaling

The Kubernetes deployment includes HorizontalPodAutoscaler for automatic scaling:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kiro-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kiro-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

Resource requests and limits are configured for all containers:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

## Monitoring

The deployment includes:

- Prometheus for metrics collection
- Grafana for visualization
- Structured logging with JSON format
- Health checks and readiness probes

## Backup and Recovery

Database backup script:

```bash
cd scripts
./backup.sh
```

This will create a backup of the PostgreSQL database and store it in a secure location.

## CI/CD Integration

The deployment scripts are designed to be used with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    - name: Login to Docker Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.DOCKER_REGISTRY }}
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    - name: Build and push Docker images
      run: |
        cd deployment/scripts
        ./deploy.sh production ${{ github.sha }}
```
