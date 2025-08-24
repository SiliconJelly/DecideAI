"""
Tests for the authentication service.
"""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from ai_employee_decision_system.auth import AuthService, UserCreate, UserLogin
from ai_employee_decision_system.auth.models import User


@pytest.fixture
def auth_service(db_session: Session):
    """Create an authentication service."""
    return AuthService(db_session)


@pytest.fixture
def sample_user_data():
    """Create sample user data."""
    return UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
        is_admin=False,
    )


def test_create_user(auth_service: AuthService, sample_user_data: UserCreate):
    """Test creating a new user."""
    user = auth_service.create_user(sample_user_data)
    
    assert user is not None
    assert user.email == sample_user_data.email
    assert user.username == sample_user_data.username
    assert user.first_name == sample_user_data.first_name
    assert user.last_name == sample_user_data.last_name
    assert user.is_admin == sample_user_data.is_admin
    assert user.is_active is True
    assert user.hashed_password != sample_user_data.password  # Password should be hashed


def test_create_user_duplicate_email(auth_service: AuthService, sample_user_data: UserCreate):
    """Test creating a user with duplicate email."""
    # Create first user
    user1 = auth_service.create_user(sample_user_data)
    assert user1 is not None
    
    # Try to create second user with same email
    sample_user_data.username = "different_username"
    user2 = auth_service.create_user(sample_user_data)
    assert user2 is None


def test_create_user_duplicate_username(auth_service: AuthService, sample_user_data: UserCreate):
    """Test creating a user with duplicate username."""
    # Create first user
    user1 = auth_service.create_user(sample_user_data)
    assert user1 is not None
    
    # Try to create second user with same username
    sample_user_data.email = "different@example.com"
    user2 = auth_service.create_user(sample_user_data)
    assert user2 is None


def test_create_user_weak_password(auth_service: AuthService, sample_user_data: UserCreate):
    """Test creating a user with weak password."""
    sample_user_data.password = "weak"
    user = auth_service.create_user(sample_user_data)
    assert user is None


def test_authenticate_user(auth_service: AuthService, sample_user_data: UserCreate):
    """Test user authentication."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Test successful authentication
    login_data = UserLogin(username=sample_user_data.username, password=sample_user_data.password)
    authenticated_user = auth_service.authenticate_user(login_data)
    
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.last_login is not None


def test_authenticate_user_wrong_password(auth_service: AuthService, sample_user_data: UserCreate):
    """Test user authentication with wrong password."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Test authentication with wrong password
    login_data = UserLogin(username=sample_user_data.username, password="wrong_password")
    authenticated_user = auth_service.authenticate_user(login_data)
    
    assert authenticated_user is None


def test_authenticate_user_nonexistent(auth_service: AuthService):
    """Test authentication of nonexistent user."""
    login_data = UserLogin(username="nonexistent", password="password")
    authenticated_user = auth_service.authenticate_user(login_data)
    
    assert authenticated_user is None


def test_authenticate_inactive_user(auth_service: AuthService, sample_user_data: UserCreate):
    """Test authentication of inactive user."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Deactivate user
    auth_service.update_user_status(user.id, False)
    
    # Test authentication
    login_data = UserLogin(username=sample_user_data.username, password=sample_user_data.password)
    authenticated_user = auth_service.authenticate_user(login_data)
    
    assert authenticated_user is None


def test_create_access_token(auth_service: AuthService, sample_user_data: UserCreate):
    """Test creating access token."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Create token
    token = auth_service.create_access_token(user)
    
    assert token.access_token is not None
    assert token.token_type == "bearer"
    assert token.expires_in > 0


def test_get_current_user(auth_service: AuthService, sample_user_data: UserCreate):
    """Test getting current user from token."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Create token
    token = auth_service.create_access_token(user)
    
    # Get current user
    current_user = auth_service.get_current_user(token.access_token)
    
    assert current_user is not None
    assert current_user.id == user.id


def test_get_current_user_invalid_token(auth_service: AuthService):
    """Test getting current user with invalid token."""
    current_user = auth_service.get_current_user("invalid_token")
    assert current_user is None


def test_get_user_by_id(auth_service: AuthService, sample_user_data: UserCreate):
    """Test getting user by ID."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Get user by ID
    retrieved_user = auth_service.get_user_by_id(user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


def test_get_user_by_email(auth_service: AuthService, sample_user_data: UserCreate):
    """Test getting user by email."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Get user by email
    retrieved_user = auth_service.get_user_by_email(user.email)
    
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


def test_get_user_by_username(auth_service: AuthService, sample_user_data: UserCreate):
    """Test getting user by username."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Get user by username
    retrieved_user = auth_service.get_user_by_username(user.username)
    
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


def test_get_users(auth_service: AuthService, sample_user_data: UserCreate):
    """Test getting all users."""
    # Create multiple users
    user1 = auth_service.create_user(sample_user_data)
    assert user1 is not None
    
    sample_user_data.email = "test2@example.com"
    sample_user_data.username = "testuser2"
    user2 = auth_service.create_user(sample_user_data)
    assert user2 is not None
    
    # Get all users
    users = auth_service.get_users()
    
    assert len(users) >= 2
    user_ids = [user.id for user in users]
    assert user1.id in user_ids
    assert user2.id in user_ids


def test_update_user_status(auth_service: AuthService, sample_user_data: UserCreate):
    """Test updating user status."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    assert user.is_active is True
    
    # Deactivate user
    updated_user = auth_service.update_user_status(user.id, False)
    
    assert updated_user is not None
    assert updated_user.is_active is False


def test_delete_user(auth_service: AuthService, sample_user_data: UserCreate):
    """Test deleting a user."""
    # Create user
    user = auth_service.create_user(sample_user_data)
    assert user is not None
    
    # Delete user
    result = auth_service.delete_user(user.id)
    assert result is True
    
    # Verify user is deleted
    deleted_user = auth_service.get_user_by_id(user.id)
    assert deleted_user is None