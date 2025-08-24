"""
Tests for authentication API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ai_employee_decision_system.api.app import app
from ai_employee_decision_system.auth import AuthService, UserCreate


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """Create sample user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "is_admin": False,
    }


@pytest.fixture
def admin_user_data():
    """Create admin user data."""
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPassword123!",
        "first_name": "Admin",
        "last_name": "User",
        "is_admin": True,
    }


def test_register_user(client: TestClient, sample_user_data: dict):
    """Test user registration endpoint."""
    response = client.post("/auth/register", json=sample_user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["username"] == sample_user_data["username"]
    assert data["first_name"] == sample_user_data["first_name"]
    assert data["last_name"] == sample_user_data["last_name"]
    assert data["is_admin"] == sample_user_data["is_admin"]
    assert data["is_active"] is True
    assert "id" in data


def test_register_user_duplicate_email(client: TestClient, sample_user_data: dict):
    """Test registering user with duplicate email."""
    # Register first user
    response1 = client.post("/auth/register", json=sample_user_data)
    assert response1.status_code == 200
    
    # Try to register second user with same email
    sample_user_data["username"] = "different_username"
    response2 = client.post("/auth/register", json=sample_user_data)
    assert response2.status_code == 400


def test_register_user_weak_password(client: TestClient, sample_user_data: dict):
    """Test registering user with weak password."""
    sample_user_data["password"] = "weak"
    response = client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 400


def test_login_user(client: TestClient, sample_user_data: dict):
    """Test user login endpoint."""
    # Register user first
    register_response = client.post("/auth/register", json=sample_user_data)
    assert register_response.status_code == 200
    
    # Login
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_user_wrong_password(client: TestClient, sample_user_data: dict):
    """Test user login with wrong password."""
    # Register user first
    register_response = client.post("/auth/register", json=sample_user_data)
    assert register_response.status_code == 200
    
    # Login with wrong password
    login_data = {
        "username": sample_user_data["username"],
        "password": "wrong_password",
    }
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 401


def test_login_nonexistent_user(client: TestClient):
    """Test login with nonexistent user."""
    login_data = {
        "username": "nonexistent",
        "password": "password",
    }
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 401


def test_get_current_user_info(client: TestClient, sample_user_data: dict):
    """Test getting current user info."""
    # Register and login user
    register_response = client.post("/auth/register", json=sample_user_data)
    assert register_response.status_code == 200
    
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    
    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["username"] == sample_user_data["username"]


def test_get_current_user_info_invalid_token(client: TestClient):
    """Test getting current user info with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 401


def test_get_users_admin_only(client: TestClient, admin_user_data: dict, sample_user_data: dict):
    """Test getting all users (admin only)."""
    # Register admin user
    admin_response = client.post("/auth/register", json=admin_user_data)
    assert admin_response.status_code == 200
    
    # Register regular user
    user_response = client.post("/auth/register", json=sample_user_data)
    assert user_response.status_code == 200
    
    # Login as admin
    admin_login = {
        "username": admin_user_data["username"],
        "password": admin_user_data["password"],
    }
    admin_login_response = client.post("/auth/login", json=admin_login)
    assert admin_login_response.status_code == 200
    admin_token = admin_login_response.json()["access_token"]
    
    # Get all users as admin
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/auth/users", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_users_non_admin_forbidden(client: TestClient, sample_user_data: dict):
    """Test getting all users as non-admin user."""
    # Register and login regular user
    register_response = client.post("/auth/register", json=sample_user_data)
    assert register_response.status_code == 200
    
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Try to get all users as regular user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users", headers=headers)
    
    assert response.status_code == 403


def test_protected_endpoint_without_auth(client: TestClient):
    """Test accessing protected endpoint without authentication."""
    response = client.get("/employees/")
    assert response.status_code == 401


def test_protected_endpoint_with_auth(client: TestClient, sample_user_data: dict):
    """Test accessing protected endpoint with authentication."""
    # Register and login user
    register_response = client.post("/auth/register", json=sample_user_data)
    assert register_response.status_code == 200
    
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/employees/", headers=headers)
    
    assert response.status_code == 200