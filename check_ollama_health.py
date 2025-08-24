#!/usr/bin/env python3
"""
Quick health check for Ollama integration.
"""
import time
import psutil
from ai_employee_decision_system.services.ollama_service import OllamaService
from ai_employee_decision_system.services.model_manager import ModelManager

def check_system_resources():
    """Check system resources."""
    print("💻 System Resources:")
    
    # Memory
    memory = psutil.virtual_memory()
    print(f"  RAM: {memory.used/1024**3:.1f}GB / {memory.total/1024**3:.1f}GB ({memory.percent:.1f}% used)")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"  CPU: {cpu_percent:.1f}% usage")
    
    # Disk
    disk = psutil.disk_usage('/')
    print(f"  Disk: {disk.used/1024**3:.1f}GB / {disk.total/1024**3:.1f}GB ({disk.percent:.1f}% used)")
    
    return memory.percent < 90 and cpu_percent < 90 and disk.percent < 90

def check_ollama_process():
    """Check if Ollama process is running."""
    print("\n🔍 Ollama Process:")
    
    ollama_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            if 'ollama' in proc.info['name'].lower():
                ollama_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if ollama_processes:
        for proc in ollama_processes:
            memory_mb = proc.info['memory_info'].rss / 1024 / 1024
            print(f"  ✅ PID {proc.info['pid']}: {proc.info['name']} (Memory: {memory_mb:.1f}MB)")
        return True
    else:
        print("  ❌ No Ollama processes found")
        return False

def quick_health_check():
    """Perform a quick health check."""
    print("🏥 Ollama Integration Health Check")
    print("=" * 50)
    
    health_status = {
        "system_resources": False,
        "ollama_process": False,
        "service_connectivity": False,
        "models_available": False,
        "response_generation": False
    }
    
    # Check system resources
    health_status["system_resources"] = check_system_resources()
    
    # Check Ollama process
    health_status["ollama_process"] = check_ollama_process()
    
    # Check service connectivity
    print("\n🌐 Service Connectivity:")
    try:
        service = OllamaService()
        health_status["service_connectivity"] = service.is_available()
        print(f"  Service available: {health_status['service_connectivity']}")
        
        if health_status["service_connectivity"]:
            print(f"  Base URL: {service.base_url}")
    except Exception as e:
        print(f"  ❌ Service check failed: {e}")
    
    # Check models
    print("\n📦 Models:")
    try:
        manager = ModelManager()
        models = manager.get_available_models()
        health_status["models_available"] = len(models) > 0
        
        print(f"  Available models: {len(models)}")
        for model in models:
            print(f"    - {model.name} ({model.size})")
    except Exception as e:
        print(f"  ❌ Model check failed: {e}")
    
    # Quick response test
    print("\n🧪 Quick Response Test:")
    try:
        if health_status["service_connectivity"] and health_status["models_available"]:
            start_time = time.time()
            response = service.generate_response(
                "Hello, this is a quick test. Please respond briefly.",
                model=models[0].name if models else "llama2:7b-chat"
            )
            elapsed = time.time() - start_time
            
            if response and response.response:
                health_status["response_generation"] = True
                print(f"  ✅ Response generated in {elapsed:.1f}s")
                print(f"  Response length: {len(response.response)} chars")
            else:
                print(f"  ❌ Failed to generate response")
        else:
            print(f"  ⏭️  Skipped (service or models not available)")
    except Exception as e:
        print(f"  ❌ Response test failed: {e}")
    
    # Summary
    print("\n📊 Health Summary:")
    total_checks = len(health_status)
    passed_checks = sum(1 for status in health_status.values() if status)
    
    for check, status in health_status.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {check.replace('_', ' ').title()}")
    
    health_percentage = (passed_checks / total_checks) * 100
    print(f"\nOverall Health: {health_percentage:.0f}% ({passed_checks}/{total_checks})")
    
    if health_percentage >= 80:
        print("🎉 System is healthy and ready for testing!")
        return True
    elif health_percentage >= 60:
        print("⚠️  System has some issues but may still work")
        return True
    else:
        print("❌ System has significant issues that need attention")
        return False

if __name__ == "__main__":
    healthy = quick_health_check()
    exit(0 if healthy else 1)