# Monitoring Infrastructure for Kiro Smart OCR

This directory contains monitoring configuration and tools for Kiro Smart OCR.

## Monitoring Components

### 1. Prometheus Configuration

Prometheus is used for metrics collection and storage. The configuration includes:

- Scrape configurations for all services
- Alert rules for critical conditions
- Recording rules for common queries
- Service discovery for dynamic environments

### 2. Grafana Dashboards

Grafana dashboards provide visualization of system metrics:

- **System Overview**: High-level view of all components
- **OCR Processing**: Detailed metrics on OCR processing
- **LLM Performance**: Metrics for LLM service
- **API Performance**: Request rates, latencies, and error rates
- **Resource Utilization**: CPU, memory, and disk usage
- **Language-specific Metrics**: Performance by language

### 3. Alerting Configuration

Alerts are configured for critical conditions:

- High error rates
- Processing time exceeding thresholds
- Resource exhaustion
- Service unavailability
- Security incidents

### 4. Logging Infrastructure

Structured logging with:

- JSON format for machine parsing
- Log levels for filtering
- Context enrichment for traceability
- Multilingual error messages

## Key Metrics

### OCR Engine Metrics

- **Processing Time**: Time to process a document
- **Accuracy Rate**: Estimated accuracy based on confidence scores
- **Error Rate**: Processing failures
- **Language Distribution**: Documents processed by language
- **Document Type Distribution**: Documents processed by type

### LLM Service Metrics

- **Inference Time**: Time to structure document
- **Token Usage**: Number of tokens processed
- **Field Extraction Rate**: Fields successfully extracted
- **Confidence Distribution**: Distribution of confidence scores

### API Metrics

- **Request Rate**: Requests per second
- **Response Time**: Time to respond to requests
- **Error Rate**: Failed requests
- **Concurrent Users**: Number of active users
- **Document Upload Rate**: Documents uploaded per minute

### Resource Metrics

- **CPU Usage**: Per service and total
- **Memory Usage**: Per service and total
- **Disk I/O**: Read/write operations
- **Network Traffic**: Inbound/outbound traffic
- **Queue Length**: Processing queue length

## Usage

### Starting Monitoring Stack

```bash
cd deployment/docker
docker-compose -f docker-compose.monitoring.yml up -d
```

### Accessing Dashboards

- **Grafana**: http://localhost:3000 (default credentials: admin/admin)
- **Prometheus**: http://localhost:9090

### Adding Custom Metrics

1. Define metrics in the application code:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
DOCUMENTS_PROCESSED = Counter(
    'kiro_documents_processed_total',
    'Total number of documents processed',
    ['language', 'document_type', 'status']
)

PROCESSING_TIME = Histogram(
    'kiro_document_processing_seconds',
    'Time spent processing documents',
    ['language', 'document_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

CONFIDENCE_SCORE = Gauge(
    'kiro_document_confidence_score',
    'Confidence score for processed documents',
    ['language', 'document_type']
)

# Use metrics in code
def process_document(document, language, document_type):
    start_time = time.time()
    try:
        result = perform_processing(document)
        DOCUMENTS_PROCESSED.labels(language=language, document_type=document_type, status='success').inc()
        CONFIDENCE_SCORE.labels(language=language, document_type=document_type).set(result.confidence)
        return result
    except Exception:
        DOCUMENTS_PROCESSED.labels(language=language, document_type=document_type, status='error').inc()
        raise
    finally:
        processing_time = time.time() - start_time
        PROCESSING_TIME.labels(language=language, document_type=document_type).observe(processing_time)
```

2. Update Prometheus configuration to scrape the new metrics
3. Create or update Grafana dashboards to visualize the metrics