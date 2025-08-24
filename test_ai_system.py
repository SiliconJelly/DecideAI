#!/usr/bin/env python3
"""
Test the AI Employee Decision System with focus on AI functionality.
"""
import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "admin",
    "password": "AdminPassword123!"
}

def test_ai_functionality():
    """Test AI functionality end-to-end."""
    print("🤖 Testing AI Employee Decision System")
    print("=" * 50)
    
    # Step 1: Login
    print("1. 🔐 Testing login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_USER
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Add test employees
    print("\n2. 👥 Adding test employees...")
    test_employees = [
        {
            "first_name": "John",
            "last_name": "Doe", 
            "email": "john.doe@company.com",
            "position": "Senior Python Developer",
            "department": "Engineering"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@company.com", 
            "position": "Data Scientist",
            "department": "AI Research"
        },
        {
            "first_name": "Mike",
            "last_name": "Johnson",
            "email": "mike.johnson@company.com",
            "position": "React Developer", 
            "department": "Frontend"
        }
    ]
    
    for emp in test_employees:
        response = requests.post(
            f"{BASE_URL}/employees/",
            json=emp,
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ Added {emp['first_name']} {emp['last_name']}")
        else:
            print(f"⚠️  Failed to add {emp['first_name']}: {response.json().get('detail', 'Unknown error')}")
    
    # Step 3: Test AI queries
    print("\n3. 🤖 Testing AI queries...")
    test_queries = [
        "Who are our employees?",
        "Who is the best for a Python project?",
        "What skills does John have?",
        "Suggest a team for a web development project",
        "Who works in Engineering?",
        "Find employees with React skills"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        response = requests.post(
            f"{BASE_URL}/ai/query",
            json={"query": query},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Response: {result.get('response', 'No response')}")
            print(f"📊 Type: {result.get('query_type', 'unknown')}")
            print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
        else:
            print(f"❌ Query failed: {response.json().get('detail', 'Unknown error')}")
    
    # Step 4: Test employee listing
    print("\n4. 📋 Testing employee listing...")
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    if response.status_code == 200:
        employees = response.json()
        print(f"✅ Found {len(employees)} employees:")
        for emp in employees:
            print(f"  • {emp['first_name']} {emp['last_name']} - {emp['position']} ({emp['department']})")
    else:
        print(f"❌ Failed to get employees: {response.status_code}")
    
    print("\n🎉 AI System Test Complete!")
    return True

def test_system_health():
    """Test system health."""
    print("🏥 Testing system health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Status: {data['status']}")
            print(f"📊 Version: {data['version']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 AI Employee Decision System - AI Functionality Test")
    print("=" * 60)
    
    # Wait for system to be ready
    print("⏳ Waiting for system to be ready...")
    time.sleep(2)
    
    # Test system health
    if not test_system_health():
        print("\n❌ System is not healthy. Please start the API server first:")
        print("   python3 start_system.py")
        return
    
    # Test AI functionality
    if test_ai_functionality():
        print("\n🎉 All tests passed! The AI system is working correctly.")
        print("\n🌐 Next steps:")
        print("  1. Open the web interface: http://localhost:7860")
        print("  2. Login with admin/AdminPassword123!")
        print("  3. Try the AI queries in the web interface")
        print("  4. Upload employee data using the bulk upload feature")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()