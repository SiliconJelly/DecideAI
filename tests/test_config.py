"""
Tests for the configuration module.
"""

from pathlib import Path

import pytest

from ai_employee_decision_system.core import config, load_config


def test_config_defaults():
    """Test that the default configuration is loaded correctly."""
    # Load a fresh config
    test_config = load_config()
    
    # Check default values
    assert test_config.app_name == "AI Employee Decision System"
    assert test_config.debug is False
    assert isinstance(test_config.data_dir, Path)
    assert isinstance(test_config.upload_dir, Path)
    assert test_config.database.url.startswith("sqlite:///")
    assert test_config.security.algorithm == "HS256"
    assert test_config.localization.default_language == "en"
    assert "de" in test_config.localization.available_languages
    assert "ja" in test_config.localization.available_languages


def test_config_environment_override(monkeypatch):
    """Test that environment variables override default configuration."""
    # Set environment variables
    monkeypatch.setenv("EMPLOYEE_SYSTEM_DB_URL", "postgresql://user:pass@localhost/testdb")
    monkeypatch.setenv("EMPLOYEE_SYSTEM_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("EMPLOYEE_SYSTEM_DEBUG", "true")
    
    # Load config with environment variables
    test_config = load_config()
    
    # Check overridden values
    assert test_config.database.url == "postgresql://user:pass@localhost/testdb"
    assert test_config.security.secret_key == "test_secret_key"
    assert test_config.debug is True