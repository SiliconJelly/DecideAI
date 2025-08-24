"""
File storage utilities for the AI Employee Decision System.
"""

import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, BinaryIO

from cryptography.fernet import Fernet

from ai_employee_decision_system.core import config, get_logger

logger = get_logger(__name__)


class FileStorage:
    """File storage utility with encryption support."""
    
    def __init__(self, base_dir: Optional[Path] = None, encryption_key: Optional[str] = None):
        """Initialize the file storage utility."""
        self.base_dir = base_dir or config.upload_dir
        self.base_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up encryption
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            # Generate a new key if not provided
            self.encryption_key = Fernet.generate_key()
        
        self.cipher = Fernet(self.encryption_key)
        
        # Create subdirectories
        self.original_dir = self.base_dir / "original"
        self.normalized_dir = self.base_dir / "normalized"
        self.processed_dir = self.base_dir / "processed"
        
        self.original_dir.mkdir(exist_ok=True)
        self.normalized_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
    
    def save_file(
        self, file_obj: BinaryIO, filename: str, encrypt: bool = True
    ) -> Tuple[str, str]:
        """
        Save a file to storage.
        
        Args:
            file_obj: File-like object to save
            filename: Original filename
            encrypt: Whether to encrypt the file
            
        Returns:
            Tuple of (file_path, original_file_path)
        """
        # Generate a unique filename
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{timestamp}_{unique_id}{ext}"
        
        # Save original file
        original_path = self.original_dir / unique_filename
        
        with open(original_path, "wb") as f:
            file_obj.seek(0)
            content = file_obj.read()
            
            if encrypt:
                encrypted_content = self.cipher.encrypt(content)
                f.write(encrypted_content)
            else:
                f.write(content)
        
        logger.info(f"Saved file: {original_path}")
        
        # Return the file paths
        return str(original_path.relative_to(self.base_dir)), str(original_path.relative_to(self.base_dir))
    
    def read_file(self, file_path: str, decrypt: bool = True) -> bytes:
        """
        Read a file from storage.
        
        Args:
            file_path: Path to the file, relative to base_dir
            decrypt: Whether to decrypt the file
            
        Returns:
            File content as bytes
        """
        full_path = self.base_dir / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, "rb") as f:
            content = f.read()
            
            if decrypt:
                try:
                    decrypted_content = self.cipher.decrypt(content)
                    return decrypted_content
                except Exception as e:
                    logger.error(f"Failed to decrypt file {file_path}: {e}")
                    # Return the raw content if decryption fails
                    return content
            else:
                return content
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file, relative to base_dir
            
        Returns:
            True if the file was deleted, False otherwise
        """
        full_path = self.base_dir / file_path
        
        if not full_path.exists():
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        try:
            os.remove(full_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def normalize_document(
        self, original_file_path: str, document_type: str
    ) -> Optional[str]:
        """
        Normalize a document for processing.
        
        Args:
            original_file_path: Path to the original file, relative to base_dir
            document_type: Type of document (CV, certificate, etc.)
            
        Returns:
            Path to the normalized file, relative to base_dir, or None if normalization failed
        """
        # This is a placeholder for document normalization
        # In a real implementation, this would convert documents to standard formats
        # For example, convert Word documents to PDF, extract text from PDFs, etc.
        
        try:
            # For now, just copy the file to the normalized directory
            original_full_path = self.base_dir / original_file_path
            
            if not original_full_path.exists():
                logger.error(f"Original file not found for normalization: {original_file_path}")
                return None
            
            # Read the original file (decrypt if needed)
            content = self.read_file(original_file_path)
            
            # Generate a normalized filename
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            ext = os.path.splitext(original_file_path)[1]
            normalized_filename = f"normalized_{timestamp}_{unique_id}{ext}"
            
            # Save the normalized file
            normalized_path = self.normalized_dir / normalized_filename
            
            with open(normalized_path, "wb") as f:
                # In a real implementation, this would be the normalized content
                f.write(content)
            
            logger.info(f"Normalized document: {normalized_path}")
            
            return str(normalized_path.relative_to(self.base_dir))
        except Exception as e:
            logger.error(f"Failed to normalize document {original_file_path}: {e}")
            return None