# Benchmarking Framework for Kiro Smart OCR

This directory contains benchmarking tools and results for evaluating the performance and accuracy of Kiro Smart OCR.

## Benchmarking Categories

### 1. Accuracy Benchmarks

Measures the OCR and field extraction accuracy across different languages and document types.

**Metrics:**
- Character Error Rate (CER)
- Word Error Rate (WER)
- Field Extraction Accuracy
- Confidence Score Calibration

### 2. Performance Benchmarks

Measures the processing speed and resource utilization.

**Metrics:**
- Processing Time per Document
- Throughput (Documents per Minute)
- Memory Usage
- CPU Utilization
- GPU Utilization (if applicable)

### 3. Multilingual Benchmarks

Specialized benchmarks for language-specific features.

**Metrics:**
- German Compound Word Recognition
- Japanese Multi-script Accuracy
- Mixed-language Document Handling

### 4. Scalability Benchmarks

Measures system performance under load.

**Metrics:**
- Concurrent Processing Capacity
- Queue Processing Efficiency
- Database Performance
- API Response Times

## Benchmark Execution

### Running Benchmarks

```bash
# Run all benchmarks
python -m testing.benchmarks.run_all

# Run specific benchmark category
python -m testing.benchmarks.run_accuracy
python -m testing.benchmarks.run_performance
python -m testing.benchmarks.run_multilingual
python -m testing.benchmarks.run_scalability

# Run specific benchmark with custom parameters
python -m testing.benchmarks.run_accuracy --language=german --doc-type=invoice
```

### Benchmark Results Format

Results are stored in JSON format:

```json
{
  "benchmark_id": "accuracy_german_invoices_20250722",
  "timestamp": "2025-07-22T15:30:00Z",
  "system_info": {
    "version": "1.0.0",
    "environment": "test",
    "hardware": "CPU: Intel i9, RAM: 32GB"
  },
  "parameters": {
    "language": "german",
    "document_type": "invoice",
    "sample_size": 100
  },
  "results": {
    "character_error_rate": 0.005,
    "word_error_rate": 0.008,
    "field_extraction_accuracy": 0.992,
    "confidence_calibration_error": 0.015
  },
  "comparison": {
    "baseline_id": "accuracy_german_invoices_20250701",
    "improvement": {
      "character_error_rate": -0.002,
      "word_error_rate": -0.003,
      "field_extraction_accuracy": 0.005,
      "confidence_calibration_error": -0.008
    }
  }
}
```

## Visualization

Benchmark results can be visualized using the included dashboard:

```bash
python -m testing.benchmarks.dashboard
```

This will start a local web server with interactive visualizations of benchmark results, including:

- Accuracy trends over time
- Performance comparisons across languages
- Resource utilization graphs
- Scalability charts