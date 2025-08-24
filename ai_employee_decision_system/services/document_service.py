"""
Document service for the AI Employee Decision System.
"""

import uuid
from datetime import datetime
from typing import BinaryIO, Dict, List, Optional, Union, Any

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models import Document, DocumentCreate, DocumentUpdate, Employee
from ai_employee_decision_system.utils.file_storage import FileStorage

logger = get_logger(__name__)


class DocumentService:
    """Service for document operations."""
    
    def __init__(self, db: Session, file_storage: Optional[FileStorage] = None):
        """Initialize the service with a database session."""
        self.db = db
        self.file_storage = file_storage or FileStorage()
    
    def get_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents with pagination."""
        return self.db.query(Document).offset(skip).limit(limit).all()
    
    def get_document(self, document_id: uuid.UUID) -> Optional[Document]:
        """Get a document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_employee_documents(self, employee_id: uuid.UUID) -> List[Document]:
        """Get all documents for an employee."""
        return self.db.query(Document).filter(Document.employee_id == employee_id).all()
    
    def create_document(
        self,
        employee_id: uuid.UUID,
        document_data: DocumentCreate,
        file_obj: BinaryIO,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Document]:
        """
        Create a new document for an employee.
        
        Args:
            employee_id: ID of the employee
            document_data: Document metadata
            file_obj: File-like object containing the document
            user_id: ID of the user creating the document
            
        Returns:
            Created document or None if employee not found
        """
        # Check if employee exists
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            logger.warning(f"Employee with ID {employee_id} not found")
            return None
        
        # Save the file
        file_path, original_file_path = self.file_storage.save_file(
            file_obj, document_data.name, encrypt=True
        )
        
        # Create document
        document = Document(
            name=document_data.name,
            type=document_data.type,
            file_path=file_path,
            original_file_path=original_file_path,
            mime_type=document_data.mime_type,
            size=document_data.size,
            upload_date=datetime.utcnow(),
            processing_status="pending",
            employee_id=employee_id,
            created_by_id=user_id,
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Created document '{document.name}' for employee: {employee.full_name()}")
        
        # Start document normalization (async in a real implementation)
        self._normalize_document(document)
        
        return document
    
    def update_document(
        self, document_id: uuid.UUID, document_data: DocumentUpdate
    ) -> Optional[Document]:
        """Update an existing document."""
        document = self.get_document(document_id)
        if not document:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = document_data.dict(exclude_unset=True)
        
        # Update document
        for key, value in update_data.items():
            setattr(document, key, value)
        
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Updated document: {document.name}")
        return document
    
    def delete_document(self, document_id: uuid.UUID) -> bool:
        """Delete a document."""
        document = self.get_document(document_id)
        if not document:
            return False
        
        # Delete the file
        if document.file_path:
            self.file_storage.delete_file(document.file_path)
        
        if document.original_file_path and document.original_file_path != document.file_path:
            self.file_storage.delete_file(document.original_file_path)
        
        if document.normalized_file_path:
            self.file_storage.delete_file(document.normalized_file_path)
        
        # Delete the document record
        self.db.delete(document)
        self.db.commit()
        
        logger.info(f"Deleted document: {document.name}")
        return True
    
    def verify_document(
        self, document_id: uuid.UUID, user_id: Optional[uuid.UUID] = None
    ) -> Optional[Document]:
        """Mark a document as verified."""
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.verified = True
        document.verification_date = datetime.utcnow()
        document.verified_by_id = user_id
        
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Verified document: {document.name}")
        return document
    
    def get_document_content(self, document_id: uuid.UUID) -> Optional[bytes]:
        """Get the content of a document."""
        document = self.get_document(document_id)
        if not document or not document.file_path:
            return None
        
        try:
            return self.file_storage.read_file(document.file_path)
        except Exception as e:
            logger.error(f"Failed to read document {document.name}: {e}")
            return None
    
    def _normalize_document(self, document: Document) -> None:
        """
        Normalize a document for processing.
        
        This is a placeholder for document normalization.
        In a real implementation, this would be an async task.
        """
        try:
            # Update document status
            document.processing_status = "processing"
            self.db.commit()
            
            # Normalize the document
            normalized_path = self.file_storage.normalize_document(
                document.original_file_path, document.type
            )
            
            if normalized_path:
                document.normalized_file_path = normalized_path
                document.processing_status = "completed"
                document.processing_level = 1  # Basic normalization
            else:
                document.processing_status = "failed"
            
            self.db.commit()
            self.db.refresh(document)
            
            logger.info(f"Normalized document: {document.name}")
        except Exception as e:
            logger.error(f"Failed to normalize document {document.name}: {e}")
            document.processing_status = "failed"
            self.db.commit()