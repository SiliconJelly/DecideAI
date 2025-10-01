#!/usr/bin/env python3
"""
Test script to verify the backend API is working properly.
Tests authentication, health checks, and RAG functionality.
"""
import json
import sys
import time
from typing import Optional

import requests


import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
TEST_USERNAME = os.environ.get("DECIDEAI_TEST_USERNAME")
TEST_PASSWORD = os.environ.get("DECIDEAI_TEST_PASSWORD")
TOKEN: Optional[str] = None


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"  {message}")


def test_health():
    """Test the health endpoint."""
    print_section("Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy: {data}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        print_info("Start the server with: uvicorn ai_employee_decision_system.api.app:app --reload")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


def test_login():
    """Test user login."""
    global TOKEN
    
    print_section("Testing Authentication")
    
    if not TEST_USERNAME or not TEST_PASSWORD:
        print_error("No DECIDEAI_TEST_USERNAME or DECIDEAI_TEST_PASSWORD set; skipping auth tests.")
        return False
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get("access_token")
            print_success("Login successful")
            print_info(f"Token: {TOKEN[:50]}...")
            print_info(f"Expires in: {data.get('expires_in')} seconds")
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False


def test_get_current_user():
    """Test getting current user info."""
    print_section("Testing Get Current User")
    
    if not TOKEN:
        print_error("No auth token available. Login first.")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("User info retrieved")
            print_info(f"Username: {data.get('username')}")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Is Admin: {data.get('is_admin')}")
            return True
        else:
            print_error(f"Get user failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get user error: {e}")
        return False


def test_ai_query_without_rag():
    """Test AI query without RAG."""
    print_section("Testing AI Query (without RAG)")
    
    if not TOKEN:
        print_error("No auth token available. Login first.")
        return False
    
    try:
        query = "What are the key principles of good HR management?"
        print_info(f"Query: {query}")
        
        response = requests.post(
            f"{BASE_URL}/ai/query",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "query": query,
                "use_rag": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Query processed successfully")
            print_info(f"RAG Enabled: {data.get('rag_enabled')}")
            print_info(f"Response: {data.get('response', 'N/A')[:200]}...")
            return True
        else:
            print_error(f"Query failed: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Query error: {e}")
        return False


def test_ai_query_with_rag():
    """Test AI query with RAG."""
    print_section("Testing AI Query (with RAG)")
    
    if not TOKEN:
        print_error("No auth token available. Login first.")
        return False
    
    try:
        query = "How many vacation days do employees get per year?"
        print_info(f"Query: {query}")
        
        response = requests.post(
            f"{BASE_URL}/ai/query",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "query": query,
                "use_rag": True,
                "top_k": 3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Query with RAG processed successfully")
            print_info(f"RAG Enabled: {data.get('rag_enabled')}")
            print_info(f"Response: {data.get('response', 'N/A')[:200]}...")
            return True
        else:
            print_error(f"Query with RAG failed: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Query with RAG error: {e}")
        return False


def test_direct_search():
    """Test direct knowledge base search."""
    print_section("Testing Direct Knowledge Base Search")
    
    if not TOKEN:
        print_error("No auth token available. Login first.")
        return False
    
    try:
        query = "remote work policy"
        print_info(f"Search query: {query}")
        
        response = requests.post(
            f"{BASE_URL}/ai/search",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "query": query,
                "top_k": 3
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Search successful - found {data.get('count', 0)} results")
            
            for i, result in enumerate(data.get('results', [])[:2], 1):
                print_info(f"\nResult {i}:")
                print_info(f"  Score: {result.get('score', 0):.4f}")
                print_info(f"  Text: {result.get('text', '')[:150]}...")
                print_info(f"  Source: {result.get('metadata', {}).get('source', 'N/A')}")
            
            return True
        else:
            print_error(f"Search failed: {response.status_code}")
            if response.status_code == 503:
                print_info("RAG service not available - index may not be created yet")
                print_info("Run: python3 scripts/index_documents.py")
            else:
                print_info(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Search error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  DecideAI Backend API Test Suite")
    print("=" * 70)
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests in sequence
    results.append(("Health Check", test_health()))
    
    if not results[-1][1]:
        print_error("\nServer is not accessible. Please start the server first:")
        print_info("  uvicorn ai_employee_decision_system.api.app:app --reload")
        return 1
    
    results.append(("Authentication", test_login()))
    if not results[-1][1]:
        print_error("\nAuthentication failed. Cannot continue with other tests.")
        return 1
    
    results.append(("Get Current User", test_get_current_user()))
    results.append(("AI Query (no RAG)", test_ai_query_without_rag()))
    results.append(("AI Query (with RAG)", test_ai_query_with_rag()))
    results.append(("Direct Search", test_direct_search()))
    
    # Print summary
    print_section("Test Summary")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_error(f"{test_name}")
            failed += 1
    
    print(f"\n{'=' * 70}")
    print(f"  Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All tests passed! Backend is working correctly.")
        print_info("You can now use the API at http://localhost:8000")
        print_info("API documentation: http://localhost:8000/docs")
    else:
        print(f"\n✗ {failed} test(s) failed. Please check the errors above.")
    
    print("=" * 70 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)