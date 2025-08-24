"""
JWT token handling for the AI Employee Decision System.
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError

from ai_employee_decision_system.core import config, get_logger
from ai_employee_decision_system.auth.models import TokenData

logger = get_logger(__name__)


class JWTHandler:
    """JWT token handler."""
    
    def __init__(self):
        """Initialize JWT handler."""
        self.secret_key = config.jwt_secret_key
        self.algorithm = config.jwt_algorithm
        self.access_token_expire_minutes = config.jwt_access_token_expire_minutes
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if username is None:
                return None
                
            token_data = TokenData(username=username, user_id=user_id)
            return token_data
            
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def get_token_expiry(self) -> int:
        """
        Get token expiry time in seconds.
        
        Returns:
            Token expiry time in seconds
        """
        return self.access_token_expire_minutes * 60