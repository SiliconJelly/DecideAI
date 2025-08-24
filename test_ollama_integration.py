#!/usr/bin/env python3
"""
Integration test for Ollama service.
"""
import time
from ai_employee_decision_system.services.ollama_service import OllamaService

def test_ollama_integration():
    """Test Ollama service integration."""
    print("🤖 Testing Ollama Service Integration")
    print("=" * 60)
    
    # Initialize service
    service = OllamaService()
    
    # Test availability
    print(f"🔍 Service available: {service.is_available()}")
    
    if not service.is_available():
        print("❌ Ollama service is not available. Make sure it's running.")
        return False
    
    # Test model listing
    print("\n📋 Available models:")
    models = service.list_models()
    for model in models:
        print(f"  - {model}")
    
    if not models:
        print("⚠️  No models available. Pulling llama2:7b-chat...")
        success = service.pull_model("llama2:7b-chat")
        if not success:
            print("❌ Failed to pull model")
            return False
        models = service.list_models()
    
    # Test response generation
    test_model = models[0] if models else "llama2:7b-chat"
    print(f"\n🧪 Testing response generation with {test_model}")
    
    test_queries = [
        "Hello, can you help me with employee management?",
        "What skills are important for a software developer?",
        "How do I build an effective team?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        start_time = time.time()
        
        response = service.generate_response(query, model=test_model)
        
        if response:
            elapsed = time.time() - start_time
            print(f"✅ Response ({elapsed:.2f}s): {response.response[:200]}...")
            print(f"📊 Model: {response.model}")
            print(f"⚡ Done: {response.done}")
            if response.eval_count:
                print(f"🔢 Tokens: {response.eval_count}")
        else:
            print("❌ Failed to generate response")
    
    # Test chat completion
    print(f"\n💬 Testing chat completion with {test_model}")
    messages = [
        {"role": "system", "content": "You are an HR assistant helping with employee management."},
        {"role": "user", "content": "What are the key factors in employee retention?"}
    ]
    
    start_time = time.time()
    chat_response = service.chat_completion(messages, model=test_model)
    
    if chat_response:
        elapsed = time.time() - start_time
        print(f"✅ Chat response ({elapsed:.2f}s): {chat_response.response[:200]}...")
    else:
        print("❌ Failed to generate chat response")
    
    # Test model info
    print(f"\n📄 Model info for {test_model}:")
    model_info = service.get_model_info(test_model)
    if model_info:
        print(f"  - Parameters: {model_info.get('parameters', 'N/A')}")
        print(f"  - Template: {model_info.get('template', 'N/A')[:100]}...")
    else:
        print("❌ Failed to get model info")
    
    # Test system status
    print("\n🔧 System status:")
    status = service.get_system_status()
    print(f"  - Available: {status['available']}")
    print(f"  - Base URL: {status['base_url']}")
    print(f"  - Models: {len(status['models'])}")
    
    print("\n" + "=" * 60)
    print("🎉 Ollama Integration Test Complete!")
    return True

def main():
    """Main test function."""
    try:
        success = test_ollama_integration()
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()