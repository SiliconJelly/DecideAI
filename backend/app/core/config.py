"""
Configuration management for Kiro Smart OCR.

This module provides configuration management with support for different environments
(development, testing, production) and language-specific settings.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseSettings, Field, validator


class LanguageConfig(BaseSettings):
    """Language-specific configuration."""
    
    language_code: str
    display_name: str
    native_name: str
    date_format: str
    currency_symbol: str
    currency_code: str
    formality_levels: List[str]
    
    class Config:
        env_prefix = "KIRO_LANG_"


class OCRConfig(BaseSettings):
    """OCR engine configuration."""
    
    confidence_threshold: float = 0.7
    max_document_size_mb: int = 10
    supported_formats: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
    tesseract_path: Optional[str] = None
    vit_model_path: str = "ai-engine/models/vit_ocr_model"
    handwriting_model_path: str = "ai-engine/models/handwriting_model"
    
    # Language-specific OCR settings
    german_compound_word_threshold: int = 10
    japanese_vertical_text_enabled: bool = True
    
    class Config:
        env_prefix = "KIRO_OCR_"


class LLMConfig(BaseSettings):
    """LLM service configuration."""
    
    model_path: str = "ai-engine/models/llm_model"
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.9
    context_window: int = 4096
    
    # Language-specific LLM settings
    german_formality_level: str = "formal"
    japanese_formality_level: str = "polite"
    
    class Config:
        env_prefix = "KIRO_LLM_"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    url: str = "postgresql://postgres:postgres@localhost:5432/kiro_ocr"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    
    class Config:
        env_prefix = "KIRO_DB_"


class RedisConfig(BaseSettings):
    """Redis configuration."""
    
    url: str = "redis://localhost:6379/0"
    password: Optional[str] = None
    
    class Config:
        env_prefix = "KIRO_REDIS_"


class APIConfig(BaseSettings):
    """API configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 4
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_prefix = "KIRO_API_"


class AuthConfig(BaseSettings):
    """Authentication configuration."""
    
    secret_key: str = "change_this_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    class Config:
        env_prefix = "KIRO_AUTH_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    testing: bool = False
    
    # Application info
    app_name: str = "Kiro Smart OCR"
    version: str = "0.1.0"
    description: str = "Multilingual OCR platform with German and Japanese support"
    
    # Default language
    default_language: str = "en"
    
    # Component configurations
    ocr: OCRConfig = OCRConfig()
    llm: LLMConfig = LLMConfig()
    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    api: APIConfig = APIConfig()
    auth: AuthConfig = AuthConfig()
    
    # Language configurations
    languages: Dict[str, LanguageConfig] = {}
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "testing", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    class Config:
        env_prefix = "KIRO_"


def load_language_configs() -> Dict[str, LanguageConfig]:
    """
    Load language configurations from JSON files.
    
    Returns:
        Dictionary of language configurations
    """
    languages = {}
    
    # Define base language configurations
    base_configs = {
        "en": {
            "language_code": "en",
            "display_name": "English",
            "native_name": "English",
            "date_format": "%m/%d/%Y",
            "currency_symbol": "$",
            "currency_code": "USD",
            "formality_levels": ["casual", "business", "formal"]
        },
        "de": {
            "language_code": "de",
            "display_name": "German",
            "native_name": "Deutsch",
            "date_format": "%d.%m.%Y",
            "currency_symbol": "€",
            "currency_code": "EUR",
            "formality_levels": ["du", "sie"]
        },
        "ja": {
            "language_code": "ja",
            "display_name": "Japanese",
            "native_name": "日本語",
            "date_format": "%Y年%m月%d日",
            "currency_symbol": "¥",
            "currency_code": "JPY",
            "formality_levels": ["casual", "polite", "honorific"]
        }
    }
    
    # Create language configurations
    for lang_code, config in base_configs.items():
        languages[lang_code] = LanguageConfig(**config)
    
    return languages


def get_settings() -> Settings:
    """
    Get application settings.
    
    Returns:
        Settings instance
    """
    settings = Settings()
    
    # Load environment-specific settings
    env_file = f".env.{settings.environment}"
    if os.path.exists(env_file):
        settings = Settings(_env_file=env_file)
    
    # Load language configurations
    settings.languages = load_language_configs()
    
    return settings


# Create global settings instance
settings = get_settings()