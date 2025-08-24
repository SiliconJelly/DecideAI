"""
Authentication models for the AI Employee Decision System.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


# Pydantic models for API
class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    is_admin: bool = False


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_admin: bool
    created_at: str
    updated_at: str
    last_login: Optional[str] = None


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    user_id: Optional[str] = None