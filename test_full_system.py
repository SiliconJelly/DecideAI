#!/usr/bin/env python3
"""
Full System Integration Test for DecideAI
Tests backend API, frontend connectivity, and end-to-end functionality
"""

import subprocess
import time
import requests
import json
import os
from pathlib import Path

def test_backend_api():
    """Test the backend API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Backend API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test employees endpoint
    try:
        response = requests.get(f"{base_url}/employees", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Employees endpoint working ({data.get('count', 0)} employees)")
        else:
            print(f"❌ Employees endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Employees endpoint error: {e}")
        return False
    
    # Test login endpoint
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/auth/login", 
                               json=login_data, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login endpoint working (token: {data.get('access_token', 'N/A')[:20]}...)")
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login endpoint error: {e}")
        return False
    
    return True

def test_frontend_structure():
    """Test frontend file structure and dependencies."""
    print("\n🌐 Testing Frontend Structure...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check key files
    key_files = [
        "frontend/package.json",
        "frontend/src/app/page.tsx",
        "frontend/src/services/api.ts",
        "frontend/src/types/schema.ts"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    # Check if node_modules exists or can be installed
    if not Path("frontend/node_modules").exists():
        print("⚠️  node_modules not found - run 'npm install' in frontend directory")
    else:
        print("✅ node_modules found")
    
    return True

def start_backend():
    """Start the backend server."""
    print("\n🚀 Starting Backend Server...")
    
    try:
        # Start the simple backend
        process = subprocess.Popen(
            ["python3", "simple_start.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                return process
            else:
                print("❌ Backend server not responding")
                process.terminate()
                return None
        except:
            print("❌ Backend server failed to start")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def test_frontend_api_integration():
    """Test if frontend API service can connect to backend."""
    print("\n🔄 Testing Frontend-Backend Integration...")
    
    # Test API endpoints that frontend uses
    base_url = "http://localhost:8000"
    
    # Test the exact endpoints frontend calls
    endpoints_to_test = [
        ("/health", "Health check"),
        ("/employees", "Get employees"),
        ("/", "Root endpoint")
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: {endpoint}")
            else:
                print(f"❌ {description}: {endpoint} (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ {description}: {endpoint} (Error: {e})")
            return False
    
    return True

def create_frontend_env():
    """Create frontend environment file."""
    frontend_env_path = Path("frontend/.env.local")
    
    env_content = """# DecideAI Frontend Environment
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=DecideAI
NEXT_PUBLIC_APP_VERSION=1.0.0
"""
    
    with open(frontend_env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {frontend_env_path}")

def main():
    """Main test function."""
    print("🧪 DecideAI Full System Integration Test")
    print("=" * 60)
    
    backend_process = None
    
    try:
        # Test frontend structure first
        if not test_frontend_structure():
            print("\n❌ Frontend structure test failed")
            return False
        
        # Create frontend environment
        create_frontend_env()
        
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("\n❌ Backend startup failed")
            return False
        
        # Test backend API
        if not test_backend_api():
            print("\n❌ Backend API test failed")
            return False
        
        # Test integration
        if not test_frontend_api_integration():
            print("\n❌ Frontend-Backend integration test failed")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! ✅")
        print("=" * 60)
        print("\n🚀 System is ready for testing!")
        print("\n📋 Next Steps:")
        print("1. Backend is running on: http://localhost:8000")
        print("2. API docs available at: http://localhost:8000/docs")
        print("3. To start frontend:")
        print("   cd frontend")
        print("   npm install")
        print("   npm run dev")
        print("4. Frontend will be on: http://localhost:3000")
        print("\n🔑 Test Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
        # Keep backend running
        print("\n⏳ Backend server is running... Press Ctrl+C to stop")
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping backend server...")
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    
    finally:
        # Clean up
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)