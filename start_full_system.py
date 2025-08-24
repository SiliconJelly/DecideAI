#!/usr/bin/env python3
"""
Start the complete AI Employee Decision System (API + UI).
"""
import subprocess
import sys
import time
import threading
import signal
import os

def start_api_server():
    """Start the API server."""
    print("🚀 Starting API server on port 8000...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "ai_employee_decision_system.api.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("🛑 API server stopped")

def start_ui_server():
    """Start the UI server."""
    print("🌐 Starting UI server on port 7860...")
    time.sleep(3)  # Wait for API to start
    try:
        subprocess.run([sys.executable, "start_ui.py"])
    except KeyboardInterrupt:
        print("🛑 UI server stopped")

def main():
    """Start both servers."""
    print("🎯 Starting AI Employee Decision System")
    print("=" * 50)
    
    # Check if system is initialized
    if not os.path.exists("data/employee_system.db"):
        print("⚠️  System not initialized. Running initialization...")
        try:
            subprocess.run([sys.executable, "init_system.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Initialization failed")
            sys.exit(1)
    
    print("\n🌟 System Information:")
    print("  - API Server: http://localhost:8000")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Web Interface: http://localhost:7860")
    print("  - Admin Username: admin")
    print("  - Admin Password: AdminPassword123!")
    print("\n🚀 Starting services...")
    print("   Press Ctrl+C to stop all services")
    
    # Start API server in a thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Start UI server in main thread
    try:
        start_ui_server()
    except KeyboardInterrupt:
        print("\n👋 Shutting down all services...")
        sys.exit(0)

if __name__ == "__main__":
    main()