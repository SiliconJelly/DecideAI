"""
Specialization service for the AI Employee Decision System.
"""

import uuid
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models import (
    Employee,
    Specialization,
    SpecializationCreate,
    SpecializationUpdate,
)

logger = get_logger(__name__)


class SpecializationService:
    """Service for specialization operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def get_specializations(self, skip: int = 0, limit: int = 100) -> List[Specialization]:
        """Get all specializations with pagination."""
        return self.db.query(Specialization).offset(skip).limit(limit).all()
    
    def get_specialization(self, specialization_id: uuid.UUID) -> Optional[Specialization]:
        """Get a specialization by ID."""
        return self.db.query(Specialization).filter(Specialization.id == specialization_id).first()
    
    def get_employee_specializations(self, employee_id: uuid.UUID) -> List[Specialization]:
        """Get all specializations for an employee."""
        return self.db.query(Specialization).filter(Specialization.employee_id == employee_id).all()
    
    def create_specialization(
        self, employee_id: uuid.UUID, specialization_data: SpecializationCreate
    ) -> Optional[Specialization]:
        """Create a new specialization for an employee."""
        # Check if employee exists
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            logger.warning(f"Employee with ID {employee_id} not found")
            return None
        
        # Create specialization
        specialization_dict = specialization_data.dict()
        specialization_dict["employee_id"] = employee_id
        
        specialization = Specialization(**specialization_dict)
        self.db.add(specialization)
        self.db.commit()
        self.db.refresh(specialization)
        
        logger.info(f"Created specialization '{specialization.name}' for employee: {employee.full_name()}")
        return specialization
    
    def update_specialization(
        self, specialization_id: uuid.UUID, specialization_data: SpecializationUpdate
    ) -> Optional[Specialization]:
        """Update an existing specialization."""
        specialization = self.get_specialization(specialization_id)
        if not specialization:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = specialization_data.dict(exclude_unset=True)
        
        # Update specialization
        for key, value in update_data.items():
            setattr(specialization, key, value)
        
        self.db.commit()
        self.db.refresh(specialization)
        
        logger.info(f"Updated specialization: {specialization.name}")
        return specialization
    
    def delete_specialization(self, specialization_id: uuid.UUID) -> bool:
        """Delete a specialization."""
        specialization = self.get_specialization(specialization_id)
        if not specialization:
            return False
        
        self.db.delete(specialization)
        self.db.commit()
        
        logger.info(f"Deleted specialization: {specialization.name}")
        return True
    
    def verify_specialization(self, specialization_id: uuid.UUID) -> Optional[Specialization]:
        """Mark a specialization as verified."""
        specialization = self.get_specialization(specialization_id)
        if not specialization:
            return None
        
        specialization.verified = True
        self.db.commit()
        self.db.refresh(specialization)
        
        logger.info(f"Verified specialization: {specialization.name}")
        return specialization