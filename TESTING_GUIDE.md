# 🧪 Ollama Integration Testing Guide

## Quick Start Testing

### 1. Health Check (30 seconds)
First, let's make sure everything is working:

```bash
python3 check_ollama_health.py
```

This will check:
- ✅ System resources (RAM, CPU, Disk)
- ✅ Ollama process running
- ✅ Service connectivity
- ✅ Available models
- ✅ Quick response generation

### 2. Comprehensive Testing (5-10 minutes)
For thorough testing of all features:

```bash
python3 test_ollama_comprehensive.py
```

This runs 12 comprehensive tests covering:
- Service connectivity
- Model management
- Response generation
- Chat completion
- Streaming responses
- Multilingual capabilities
- HR-specific queries
- Error handling
- Performance metrics

### 3. Individual Component Tests
Test specific components:

```bash
# Test Ollama service only
python3 test_ollama_integration.py

# Test model manager only
python3 test_model_manager.py
```

## What to Expect

### ✅ Healthy System Output
```
🏥 Ollama Integration Health Check
==================================================
💻 System Resources:
  RAM: 8.2GB / 16.0GB (51.2% used)
  CPU: 15.3% usage
  Disk: 45.1GB / 250.0GB (18.0% used)

🔍 Ollama Process:
  ✅ PID 12345: ollama (Memory: 2048.5MB)

🌐 Service Connectivity:
  Service available: True
  Base URL: http://localhost:11434

📦 Models:
  Available models: 3
    - llama2:7b-chat (3.8GB)
    - llama3.2:1b (1.3GB)
    - llama3.2:3b (2.0GB)

🧪 Quick Response Test:
  ✅ Response generated in 25.3s
  Response length: 245 chars

📊 Health Summary:
  ✅ System Resources
  ✅ Ollama Process
  ✅ Service Connectivity
  ✅ Models Available
  ✅ Response Generation

Overall Health: 100% (5/5)
🎉 System is healthy and ready for testing!
```

### 🔧 Troubleshooting Common Issues

#### Issue: "Ollama service is not available"
**Solution:**
```bash
# Start Ollama service
ollama serve &

# Wait a few seconds, then test again
sleep 5
python3 check_ollama_health.py
```

#### Issue: "No models available"
**Solution:**
```bash
# Download a model
ollama pull llama2:7b-chat

# Or use the model manager
python3 -c "
from ai_employee_decision_system.services.model_manager import ModelManager
manager = ModelManager()
manager.download_model('llama2:7b-chat')
"
```

#### Issue: "Response generation failed"
**Possible causes:**
- Model is still loading (wait 30 seconds)
- Insufficient memory (check system resources)
- Model corruption (re-download model)

**Solution:**
```bash
# Check if model is loading
ollama list

# Re-download if needed
ollama pull llama2:7b-chat
```

## Performance Benchmarks

### Expected Performance (llama2:7b-chat on M3 Mac)
- **Response Time**: 25-45 seconds for complex queries
- **Tokens/Second**: 20-30 tokens/second
- **Memory Usage**: 6-8GB RAM
- **Model Loading**: 10-15 seconds first time

### Performance Testing
```bash
# Run performance-focused tests
python3 -c "
from test_ollama_comprehensive import OllamaTestSuite
suite = OllamaTestSuite()
suite.test_performance_metrics()
"
```

## Testing Different Scenarios

### 1. Multilingual Testing
```bash
python3 -c "
from ai_employee_decision_system.services.ollama_service import OllamaService
service = OllamaService()

# Test German
response = service.generate_response('Was sind die wichtigsten HR-Praktiken?', model='llama3.2:3b')
print('German:', response.response[:100] if response else 'Failed')

# Test French  
response = service.generate_response('Quelles sont les meilleures pratiques RH?', model='llama3.2:3b')
print('French:', response.response[:100] if response else 'Failed')
"
```

### 2. HR-Specific Testing
```bash
python3 -c "
from ai_employee_decision_system.services.ollama_service import OllamaService
service = OllamaService()

hr_queries = [
    'How do I write a job description for a senior developer?',
    'What are effective interview questions for assessing teamwork?',
    'How can I improve employee retention?'
]

for query in hr_queries:
    print(f'Query: {query}')
    response = service.generate_response(query, model='llama2:7b-chat')
    print(f'Response: {response.response[:150] if response else \"Failed\"}...\n')
"
```

### 3. Model Comparison Testing
```bash
python3 -c "
from ai_employee_decision_system.services.model_manager import ModelManager
manager = ModelManager()

# Get recommendations for different scenarios
print('General HR (English, Balanced):')
recs = manager.get_recommended_models('general', 'en', 'balanced')
for rec in recs:
    print(f'  - {rec.name}: {rec.description}')

print('\nMultilingual (German, Fast):')
recs = manager.get_recommended_models('multilingual', 'de', 'fast')
for rec in recs:
    print(f'  - {rec.name}: {rec.description}')
"
```

## Integration with Existing System

### Test with Current AI Service
```bash
python3 -c "
# Test if we can integrate with existing AI service
from ai_employee_decision_system.services.ai_service import AIService
from ai_employee_decision_system.services.ollama_service import OllamaService

# Check current AI service
ai_service = AIService()
print('Current AI service working:', ai_service.process_query('Hello')['response'][:50])

# Test Ollama service
ollama_service = OllamaService()
if ollama_service.is_available():
    response = ollama_service.generate_response('Hello')
    print('Ollama service working:', response.response[:50] if response else 'Failed')
else:
    print('Ollama service not available')
"
```

## Next Steps After Testing

### If All Tests Pass ✅
You're ready to proceed with:
1. **AI Orchestrator** (Task 2.1) - Intelligent routing between AI backends
2. **Language Detection** (Task 3.1) - Multilingual support
3. **Enhanced Capabilities** (Task 4.1) - Advanced AI features

### If Some Tests Fail ⚠️
1. **Review failed tests** in the comprehensive output
2. **Check system resources** (RAM, CPU, disk space)
3. **Verify Ollama installation** and model availability
4. **Run individual component tests** to isolate issues

### If Many Tests Fail ❌
1. **Restart Ollama service**: `ollama serve &`
2. **Re-download models**: `ollama pull llama2:7b-chat`
3. **Check system requirements**: 8GB+ RAM recommended
4. **Review installation**: Run `python3 scripts/install_ollama.py`

## Getting Help

If you encounter issues:

1. **Check logs**: Look for error messages in the test output
2. **System resources**: Ensure sufficient RAM (8GB+) and disk space
3. **Model status**: Verify models are properly downloaded with `ollama list`
4. **Service status**: Confirm Ollama is running with `ps aux | grep ollama`

The testing suite is designed to be comprehensive and help identify exactly what's working and what needs attention before we move to the next development phase.