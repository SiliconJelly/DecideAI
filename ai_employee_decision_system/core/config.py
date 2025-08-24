"""
Configuration module for the AI Employee Decision System.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration."""
    
    url: str = Field(
        default="sqlite:///./data/employee_system.db",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        description="Echo SQL statements to stdout"
    )


class SecurityConfig(BaseModel):
    """Security configuration."""
    
    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",
        description="Secret key for JWT token generation"
    )
    algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT token generation"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    password_min_length: int = Field(
        default=8,
        description="Minimum password length"
    )


class AIModelConfig(BaseModel):
    """AI model configuration."""
    
    model_path: Path = Field(
        default=Path("./data/models"),
        description="Path to AI models"
    )
    ocr_confidence_threshold: float = Field(
        default=0.7,
        description="Confidence threshold for OCR results"
    )
    use_gpu: bool = Field(
        default=False,
        description="Use GPU for model inference if available"
    )


class LocalizationConfig(BaseModel):
    """Localization configuration."""
    
    default_language: str = Field(
        default="en",
        description="Default language"
    )
    available_languages: List[str] = Field(
        default=["en", "de", "ja"],
        description="Available languages"
    )


class AppConfig(BaseModel):
    """Main application configuration."""
    
    app_name: str = Field(
        default="AI Employee Decision System",
        description="Application name"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    data_dir: Path = Field(
        default=Path("./data"),
        description="Data directory"
    )
    upload_dir: Path = Field(
        default=Path("./data/uploads"),
        description="Upload directory"
    )
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration"
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration"
    )
    ai: AIModelConfig = Field(
        default_factory=AIModelConfig,
        description="AI model configuration"
    )
    localization: LocalizationConfig = Field(
        default_factory=LocalizationConfig,
        description="Localization configuration"
    )
    
    # JWT Configuration (for backward compatibility)
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key."""
        return self.security.secret_key
    
    @property
    def jwt_algorithm(self) -> str:
        """Get JWT algorithm."""
        return self.security.algorithm
    
    @property
    def jwt_access_token_expire_minutes(self) -> int:
        """Get JWT access token expiration time."""
        return self.security.access_token_expire_minutes


def load_config() -> AppConfig:
    """Load configuration from environment variables and defaults."""
    
    # Create a base config with defaults
    config = AppConfig()
    
    # Override with environment variables if present
    if db_url := os.environ.get("EMPLOYEE_SYSTEM_DB_URL"):
        config.database.url = db_url
    
    if secret_key := os.environ.get("EMPLOYEE_SYSTEM_SECRET_KEY"):
        config.security.secret_key = secret_key
    
    if algorithm := os.environ.get("EMPLOYEE_SYSTEM_JWT_ALGORITHM"):
        config.security.algorithm = algorithm
    
    if expire_minutes := os.environ.get("EMPLOYEE_SYSTEM_JWT_EXPIRE_MINUTES"):
        try:
            config.security.access_token_expire_minutes = int(expire_minutes)
        except ValueError:
            pass
    
    if debug := os.environ.get("EMPLOYEE_SYSTEM_DEBUG"):
        config.debug = debug.lower() in ("true", "1", "yes")
    
    # Ensure directories exist
    config.data_dir.mkdir(exist_ok=True, parents=True)
    config.upload_dir.mkdir(exist_ok=True, parents=True)
    config.ai.model_path.mkdir(exist_ok=True, parents=True)
    
    return config


# Global config instance
config = load_config()

def get_settings() -> AppConfig:
    """Get the global configuration instance."""
    return config