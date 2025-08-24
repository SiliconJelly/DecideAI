"""
Pytest configuration for the AI Employee Decision System.
"""

import os
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_employee_decision_system.core import config


@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(scope="session")
def test_config(temp_dir):
    """Create a test configuration."""
    # Create a copy of the config
    test_config = config.copy(deep=True)
    
    # Update paths to use temporary directory
    test_config.data_dir = temp_dir / "data"
    test_config.upload_dir = temp_dir / "data" / "uploads"
    test_config.ai.model_path = temp_dir / "data" / "models"
    
    # Create directories
    test_config.data_dir.mkdir(exist_ok=True, parents=True)
    test_config.upload_dir.mkdir(exist_ok=True, parents=True)
    test_config.ai.model_path.mkdir(exist_ok=True, parents=True)
    
    # Use in-memory SQLite database
    test_config.database.url = "sqlite:///:memory:"
    
    return test_config


@pytest.fixture(scope="session")
def engine(test_config):
    """Create a database engine."""
    return create_engine(test_config.database.url, echo=test_config.database.echo)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a database session."""
    # Import here to avoid circular imports
    from ai_employee_decision_system.models.base import Base
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        
    # Drop tables
    Base.metadata.drop_all(engine)