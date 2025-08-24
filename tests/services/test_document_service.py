"""
Tests for the Document service.
"""

import io
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from ai_employee_decision_system.models import DocumentCreate, EmployeeCreate
from ai_employee_decision_system.services import DocumentService, EmployeeService
from ai_employee_decision_system.utils.file_storage import FileStorage


@pytest.fixture
def mock_file_storage():
    """Create a mock file storage."""
    storage = MagicMock(spec=FileStorage)
    storage.save_file.return_value = ("test/path.pdf", "test/original_path.pdf")
    storage.normalize_document.return_value = "test/normalized_path.pdf"
    storage.read_file.return_value = b"test file content"
    storage.delete_file.return_value = True
    return storage


def test_create_document(db_session, mock_file_storage):
    """Test creating a document."""
    # Create services
    employee_service = EmployeeService(db_session)
    document_service = DocumentService(db_session, mock_file_storage)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a document
    document_data = DocumentCreate(
        name="John_Doe_CV.pdf",
        type="CV",
        mime_type="application/pdf",
        size=1024567,
    )
    file_obj = io.BytesIO(b"test file content")
    
    document = document_service.create_document(employee.id, document_data, file_obj)
    
    # Check that the document was created
    assert document is not None
    assert document.id is not None
    assert document.name == "John_Doe_CV.pdf"
    assert document.type == "CV"
    assert document.file_path == "test/path.pdf"
    assert document.original_file_path == "test/original_path.pdf"
    assert document.mime_type == "application/pdf"
    assert document.size == 1024567
    assert document.upload_date is not None
    assert document.employee_id == employee.id
    
    # Check that the file was saved
    mock_file_storage.save_file.assert_called_once()
    
    # Check that normalization was attempted
    assert document.normalized_file_path == "test/normalized_path.pdf"
    assert document.processing_status == "completed"
    assert document.processing_level == 1


def test_get_document(db_session, mock_file_storage):
    """Test getting a document."""
    # Create services
    employee_service = EmployeeService(db_session)
    document_service = DocumentService(db_session, mock_file_storage)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a document
    document_data = DocumentCreate(
        name="Jane_Smith_CV.pdf",
        type="CV",
        mime_type="application/pdf",
        size=1024567,
    )
    file_obj = io.BytesIO(b"test file content")
    
    created_document = document_service.create_document(employee.id, document_data, file_obj)
    
    # Get the document
    document = document_service.get_document(created_document.id)
    
    # Check that the document was retrieved
    assert document is not None
    assert document.id == created_document.id
    assert document.name == "Jane_Smith_CV.pdf"
    assert document.type == "CV"
    assert document.employee_id == employee.id


def test_get_employee_documents(db_session, mock_file_storage):
    """Test getting all documents for an employee."""
    # Create services
    employee_service = EmployeeService(db_session)
    document_service = DocumentService(db_session, mock_file_storage)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Bob",
        last_name="Johnson",
        email="bob.johnson@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create documents
    document_data1 = DocumentCreate(
        name="Bob_Johnson_CV.pdf",
        type="CV",
        mime_type="application/pdf",
        size=1024567,
    )
    document_data2 = DocumentCreate(
        name="Bob_Johnson_Certificate.pdf",
        type="Certificate",
        mime_type="application/pdf",
        size=512345,
    )
    file_obj1 = io.BytesIO(b"test file content 1")
    file_obj2 = io.BytesIO(b"test file content 2")
    
    document1 = document_service.create_document(employee.id, document_data1, file_obj1)
    document2 = document_service.create_document(employee.id, document_data2, file_obj2)
    
    # Get the employee's documents
    documents = document_service.get_employee_documents(employee.id)
    
    # Check that the documents were retrieved
    assert len(documents) == 2
    assert any(d.id == document1.id for d in documents)
    assert any(d.id == document2.id for d in documents)


def test_verify_document(db_session, mock_file_storage):
    """Test verifying a document."""
    # Create services
    employee_service = EmployeeService(db_session)
    document_service = DocumentService(db_session, mock_file_storage)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Charlie",
        last_name="Davis",
        email="charlie.davis@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a document
    document_data = DocumentCreate(
        name="Charlie_Davis_CV.pdf",
        type="CV",
        mime_type="application/pdf",
        size=1024567,
    )
    file_obj = io.BytesIO(b"test file content")
    
    document = document_service.create_document(employee.id, document_data, file_obj)
    
    # Verify the document
    user_id = uuid.uuid4()
    verified_document = document_service.verify_document(document.id, user_id)
    
    # Check that the document was verified
    assert verified_document is not None
    assert verified_document.id == document.id
    assert verified_document.verified is True
    assert verified_document.verification_date is not None
    assert verified_document.verified_by_id == user_id


def test_get_document_content(db_session, mock_file_storage):
    """Test getting document content."""
    # Create services
    employee_service = EmployeeService(db_session)
    document_service = DocumentService(db_session, mock_file_storage)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="David",
        last_name="Evans",
        email="david.evans@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a document
    document_data = DocumentCreate(
        name="David_Evans_CV.pdf",
        type="CV",
        mime_type="application/pdf",
        size=1024567,
    )
    file_obj = io.BytesIO(b"test file content")
    
    document = document_service.create_document(employee.id, document_data, file_obj)
    
    # Get the document content
    content = document_service.get_document_content(document.id)
    
    # Check that the content was retrieved
    assert content == b"test file content"
    mock_file_storage.read_file.assert_called_once_with("test/path.pdf")


def test_delete_document(db_session, mock_file_storage):
    """Test deleting a document."""
    # Create services
    employee_service = EmployeeService(db_session)
    document_service = DocumentService(db_session, mock_file_storage)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Eve",
        last_name="Franklin",
        email="eve.franklin@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a document
    document_data = DocumentCreate(
        name="Eve_Franklin_CV.pdf",
        type="CV",
        mime_type="application/pdf",
        size=1024567,
    )
    file_obj = io.BytesIO(b"test file content")
    
    document = document_service.create_document(employee.id, document_data, file_obj)
    
    # Delete the document
    result = document_service.delete_document(document.id)
    
    # Check that the document was deleted
    assert result is True
    assert document_service.get_document(document.id) is None
    
    # Check that the files were deleted
    assert mock_file_storage.delete_file.call_count == 3  # file_path, original_file_path, normalized_file_path