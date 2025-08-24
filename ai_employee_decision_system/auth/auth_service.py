"""
Authentication service for the AI Employee Decision System.
"""
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models.user import User
from ai_employee_decision_system.auth.models import UserCreate, UserLogin, Token
from ai_employee_decision_system.auth.password_utils import PasswordUtils
from ai_employee_decision_system.auth.jwt_handler import JWTHandler

logger = get_logger(__name__)


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: Session):
        """
        Initialize authentication service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.password_utils = PasswordUtils()
        self.jwt_handler = JWTHandler()
    
    def create_user(self, user_data: UserCreate) -> Optional[User]:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user or None if creation failed
        """
        try:
            # Validate password strength
            is_valid, errors = self.password_utils.validate_password_strength(user_data.password)
            if not is_valid:
                logger.warning(f"Password validation failed: {errors}")
                return None
            
            # Check if user already exists
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning(f"User with email {user_data.email} already exists")
                return None
            
            existing_user = self.get_user_by_username(user_data.username)
            if existing_user:
                logger.warning(f"User with username {user_data.username} already exists")
                return None
            
            # Hash password
            hashed_password = self.password_utils.hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                is_admin=user_data.is_admin,
                role="admin" if user_data.is_admin else "user",
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created user: {user.username}")
            return user
            
        except Exception as e:
            logger.exception(f"Error creating user: {e}")
            self.db.rollback()
            return None
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            login_data: User login data
            
        Returns:
            Authenticated user or None if authentication failed
        """
        try:
            # Get user by username
            user = self.get_user_by_username(login_data.username)
            if not user:
                logger.warning(f"User not found: {login_data.username}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"User is inactive: {login_data.username}")
                return None
            
            # Verify password
            if not self.password_utils.verify_password(login_data.password, user.hashed_password):
                logger.warning(f"Invalid password for user: {login_data.username}")
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"User authenticated: {user.username}")
            return user
            
        except Exception as e:
            logger.exception(f"Error authenticating user: {e}")
            return None
    
    def create_access_token(self, user: User) -> Token:
        """
        Create an access token for a user.
        
        Args:
            user: User to create token for
            
        Returns:
            Token object
        """
        access_token_expires = timedelta(minutes=self.jwt_handler.access_token_expire_minutes)
        access_token = self.jwt_handler.create_access_token(
            data={"sub": user.username, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.jwt_handler.get_token_expiry()
        )
    
    def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from token.
        
        Args:
            token: JWT token
            
        Returns:
            Current user or None if token is invalid
        """
        token_data = self.jwt_handler.verify_token(token)
        if not token_data:
            return None
        
        user = self.get_user_by_username(token_data.username)
        if not user or not user.is_active:
            return None
        
        return user
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.exception(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.exception(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User or None if not found
        """
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.exception(f"Error getting user by username: {e}")
            return None
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of users
        """
        try:
            return self.db.query(User).offset(skip).limit(limit).all()
        except Exception as e:
            logger.exception(f"Error getting users: {e}")
            return []
    
    def update_user_status(self, user_id: uuid.UUID, is_active: bool) -> Optional[User]:
        """
        Update user active status.
        
        Args:
            user_id: User ID
            is_active: New active status
            
        Returns:
            Updated user or None if not found
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            user.is_active = is_active
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user status: {user.username} -> {is_active}")
            return user
            
        except Exception as e:
            logger.exception(f"Error updating user status: {e}")
            self.db.rollback()
            return None
    
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"Deleted user: {user.username}")
            return True
            
        except Exception as e:
            logger.exception(f"Error deleting user: {e}")
            self.db.rollback()
            return False