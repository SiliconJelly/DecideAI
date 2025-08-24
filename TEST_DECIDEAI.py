#!/usr/bin/env python3
"""
🧪 DecideAI Test Launcher

Easy testing interface for DecideAI HR Helper System.
Choose what you want to test!
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print test banner."""
    print("=" * 70)
    print("🧪 DecideAI Testing Suite")
    print("   For German & Japanese Institutions")
    print("=" * 70)

def print_menu():
    """Print testing menu."""
    print("\n🎯 What would you like to test?")
    print()
    print("1. 🚀 Quick System Check (2 minutes)")
    print("   - Check if system is running")
    print("   - Test basic functionality")
    print()
    print("2. 🤖 Interactive Testing (15 minutes)")
    print("   - Step-by-step guided testing")
    print("   - Manual verification with prompts")
    print()
    print("3. ⚡ Automated Production Tests (5 minutes)")
    print("   - Comprehensive automated testing")
    print("   - Performance and security validation")
    print()
    print("4. 🌍 Multilingual AI Testing (10 minutes)")
    print("   - Test German, Japanese, English queries")
    print("   - Cultural context validation")
    print()
    print("5. 📊 Load Sample Data")
    print("   - Load German university test data")
    print("   - Load Japanese SME test data")
    print()
    print("6. 📋 View Testing Checklist")
    print("   - Complete manual testing guide")
    print("   - Step-by-step instructions")
    print()
    print("7. 🔧 System Diagnostics")
    print("   - Check system health")
    print("   - View logs and status")
    print()
    print("0. ❌ Exit")

def quick_system_check():
    """Quick system health check."""
    print("\n🚀 Quick System Check")
    print("=" * 50)
    
    # First check if services are running via orchestration
    try:
        # Add project root to path
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from ai_employee_decision_system.services.service_orchestration import (
            ServiceManager, get_default_service_configs
        )
        
        # Create service manager and check status
        manager = ServiceManager()
        for config in get_default_service_configs():
            manager.register_service(config)
        
        print("📊 Service Status (via orchestration):")
        
        # Check each service
        services_ok = True
        for service_name in ["ollama", "api", "ui"]:
            status = manager.get_service_status(service_name)
            
            if service_name == "ollama":
                # Check if Ollama is available
                try:
                    result = subprocess.run(['ollama', 'list'], 
                                          capture_output=True, text=True, check=True)
                    print("✅ Ollama AI: Available")
                except:
                    print("❌ Ollama AI: Not available")
                    print("   Install with: python DEPLOY_DECIDEAI.py")
                    services_ok = False
            
            elif service_name == "api":
                # Check API server
                try:
                    import requests
                    response = requests.get("http://localhost:8000/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ API Server: Running")
                    else:
                        print("❌ API Server: Not responding properly")
                        services_ok = False
                except:
                    print("❌ API Server: Not running")
                    print("   Start with: python START_DECIDEAI.py")
                    services_ok = False
            
            elif service_name == "ui":
                # Check UI server
                try:
                    import requests
                    response = requests.get("http://localhost:7860", timeout=5)
                    if response.status_code == 200:
                        print("✅ Web Interface: Accessible")
                    else:
                        print("❌ Web Interface: Not responding properly")
                        services_ok = False
                except:
                    print("❌ Web Interface: Not accessible")
                    services_ok = False
        
    except ImportError:
        print("⚠️  Service orchestration not available, using basic checks...")
        services_ok = basic_system_check()
    
    # Check database
    db_path = Path("data/employee_system.db")
    if db_path.exists():
        print("✅ Database: Found")
    else:
        print("❌ Database: Not found")
        print("   Initialize with: python init_system.py")
        services_ok = False
    
    print("\n🎉 Quick check complete!")
    if services_ok:
        print("✅ System is ready for testing!")
    else:
        print("❌ Some issues found. Start with: python START_DECIDEAI.py")
    
    return services_ok

def basic_system_check():
    """Basic system check without orchestration."""
    services_ok = True
    
    # Check API
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server: Running")
        else:
            print("❌ API Server: Not responding properly")
            services_ok = False
    except:
        print("❌ API Server: Not running")
        services_ok = False
    
    # Check UI
    try:
        import requests
        response = requests.get("http://localhost:7860", timeout=5)
        if response.status_code == 200:
            print("✅ Web Interface: Accessible")
        else:
            print("❌ Web Interface: Not responding properly")
            services_ok = False
    except:
        print("❌ Web Interface: Not accessible")
        services_ok = False
    
    # Check Ollama
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, check=True)
        print("✅ Ollama AI: Running")
    except:
        print("❌ Ollama AI: Not running")
        services_ok = False
    
    return services_ok

def run_interactive_tests():
    """Run interactive testing."""
    print("\n🤖 Starting Interactive Tests...")
    try:
        subprocess.run([sys.executable, "test_scenarios.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Interactive tests failed")
    except FileNotFoundError:
        print("❌ test_scenarios.py not found")

def run_automated_tests():
    """Run automated production tests."""
    print("\n⚡ Starting Automated Tests...")
    try:
        subprocess.run([sys.executable, "test_production_readiness.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Automated tests failed")
    except FileNotFoundError:
        print("❌ test_production_readiness.py not found")

def test_multilingual_ai():
    """Test multilingual AI capabilities."""
    print("\n🌍 Multilingual AI Testing")
    print("=" * 50)
    
    # Load test queries
    import json
    try:
        with open("test_queries.json", 'r', encoding='utf-8') as f:
            queries = json.load(f)
    except FileNotFoundError:
        print("❌ test_queries.json not found")
        return
    
    print("Please test these queries manually in the web interface:")
    print("Web Interface: http://localhost:7860")
    print()
    
    print("📝 English Queries:")
    for query in queries["english_queries"][:3]:
        print(f"   • {query}")
    
    print("\n📝 German Queries:")
    for query in queries["german_queries"][:3]:
        print(f"   • {query}")
    
    print("\n📝 Japanese Queries:")
    for query in queries["japanese_queries"][:3]:
        print(f"   • {query}")
    
    print("\n🎯 Test each query and verify:")
    print("   ✅ AI responds in the correct language")
    print("   ✅ Responses are contextually appropriate")
    print("   ✅ Cultural awareness is demonstrated")

def load_sample_data():
    """Load sample test data."""
    print("\n📊 Load Sample Data")
    print("=" * 50)
    
    data_files = [
        ("sample_employees.csv", "Mixed German/Japanese sample data"),
        ("test_data_german_university.csv", "German university faculty data"),
        ("test_data_japanese_sme.csv", "Japanese SME employee data")
    ]
    
    print("Available test data files:")
    for i, (filename, description) in enumerate(data_files, 1):
        if Path(filename).exists():
            print(f"   {i}. ✅ {filename} - {description}")
        else:
            print(f"   {i}. ❌ {filename} - {description} (not found)")
    
    print("\nTo load data:")
    print("1. Go to http://localhost:7860")
    print("2. Navigate to Employees → Bulk Upload")
    print("3. Select and upload the desired CSV file")
    print("4. Verify the data appears correctly")

def view_testing_checklist():
    """View the testing checklist."""
    print("\n📋 Opening Testing Checklist...")
    
    checklist_file = Path("TESTING_CHECKLIST.md")
    if checklist_file.exists():
        print(f"✅ Found: {checklist_file}")
        print("\nOpening in default editor...")
        
        # Try to open with default system editor
        import platform
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["open", str(checklist_file)])
            elif system == "Windows":
                subprocess.run(["start", str(checklist_file)], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(checklist_file)])
            
            print("📖 Checklist opened in your default editor")
        except:
            print("Could not open automatically. Please open manually:")
            print(f"   File: {checklist_file}")
    else:
        print("❌ TESTING_CHECKLIST.md not found")

def system_diagnostics():
    """Run system diagnostics."""
    print("\n🔧 System Diagnostics")
    print("=" * 50)
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # System info
    import platform
    print(f"Operating System: {platform.system()} {platform.release()}")
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage(".")
    print(f"Disk Space: {free // (1024**3)}GB free of {total // (1024**3)}GB total")
    
    # Check memory (if psutil is available)
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"Memory: {memory.available // (1024**3)}GB available of {memory.total // (1024**3)}GB total")
    except ImportError:
        print("Memory: Unable to check (psutil not installed)")
    
    # Check log files
    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"Log Files: {len(log_files)} found")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"   • {log_file.name}: {size} bytes")
    else:
        print("Log Files: logs/ directory not found")
    
    # Check data directory
    data_dir = Path("data")
    if data_dir.exists():
        db_file = data_dir / "employee_system.db"
        if db_file.exists():
            size = db_file.stat().st_size
            print(f"Database: {size} bytes")
        else:
            print("Database: Not found")
    else:
        print("Data Directory: Not found")

def main():
    """Main function."""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("\n🎯 Enter your choice (0-7): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                quick_system_check()
            elif choice == "2":
                run_interactive_tests()
            elif choice == "3":
                run_automated_tests()
            elif choice == "4":
                test_multilingual_ai()
            elif choice == "5":
                load_sample_data()
            elif choice == "6":
                view_testing_checklist()
            elif choice == "7":
                system_diagnostics()
            else:
                print("❌ Invalid choice. Please enter 0-7.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Testing cancelled")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()