"""
Tests for the FileStorage utility.
"""

import io
import os
import tempfile
from pathlib import Path

import pytest

from ai_employee_decision_system.utils.file_storage import FileStorage


@pytest.fixture
def temp_storage():
    """Create a temporary file storage."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield FileStorage(base_dir=Path(temp_dir))


def test_save_file(temp_storage):
    """Test saving a file."""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    filename = "test.txt"
    
    # Save the file
    file_path, original_file_path = temp_storage.save_file(file_obj, filename)
    
    # Check that the file was saved
    assert file_path == original_file_path
    assert file_path.startswith("original/")
    assert os.path.exists(temp_storage.base_dir / file_path)
    
    # The content should be encrypted, so it should not match the original
    with open(temp_storage.base_dir / file_path, "rb") as f:
        saved_content = f.read()
    
    assert saved_content != file_content


def test_read_file(temp_storage):
    """Test reading a file."""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    filename = "test.txt"
    
    # Save the file
    file_path, _ = temp_storage.save_file(file_obj, filename)
    
    # Read the file
    read_content = temp_storage.read_file(file_path)
    
    # Check that the content matches
    assert read_content == file_content


def test_delete_file(temp_storage):
    """Test deleting a file."""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    filename = "test.txt"
    
    # Save the file
    file_path, _ = temp_storage.save_file(file_obj, filename)
    
    # Check that the file exists
    assert os.path.exists(temp_storage.base_dir / file_path)
    
    # Delete the file
    result = temp_storage.delete_file(file_path)
    
    # Check that the file was deleted
    assert result is True
    assert not os.path.exists(temp_storage.base_dir / file_path)


def test_normalize_document(temp_storage):
    """Test normalizing a document."""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    filename = "test.pdf"
    
    # Save the file
    file_path, _ = temp_storage.save_file(file_obj, filename)
    
    # Normalize the document
    normalized_path = temp_storage.normalize_document(file_path, "CV")
    
    # Check that the normalized file exists
    assert normalized_path is not None
    assert normalized_path.startswith("normalized/")
    assert os.path.exists(temp_storage.base_dir / normalized_path)
    
    # Read the normalized file
    normalized_content = temp_storage.read_file(normalized_path, decrypt=False)
    
    # In our simple implementation, the normalized content should match the original
    assert normalized_content == file_content