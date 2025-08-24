"""
Employee service for the AI Employee Decision System.
"""

import uuid
from typing import Dict, List, Optional, Union, Any

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models import Employee, EmployeeCreate, EmployeeUpdate, Tag

logger = get_logger(__name__)


class EmployeeService:
    """Service for employee operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def get_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees with pagination."""
        return self.db.query(Employee).offset(skip).limit(limit).all()
    
    def get_employee(self, employee_id: uuid.UUID) -> Optional[Employee]:
        """Get an employee by ID."""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get an employee by email."""
        return self.db.query(Employee).filter(Employee.email == email).first()
    
    def create_employee(self, employee_data: EmployeeCreate, user_id: Optional[uuid.UUID] = None) -> Employee:
        """Create a new employee."""
        # Convert Pydantic model to dict
        employee_dict = employee_data.dict()
        
        # Add audit fields
        if user_id:
            employee_dict["created_by_id"] = user_id
            employee_dict["updated_by_id"] = user_id
        
        # Create employee
        employee = Employee(**employee_dict)
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        
        logger.info(f"Created employee: {employee.full_name()}")
        return employee
    
    def update_employee(
        self, employee_id: uuid.UUID, employee_data: EmployeeUpdate, user_id: Optional[uuid.UUID] = None
    ) -> Optional[Employee]:
        """Update an existing employee."""
        employee = self.get_employee(employee_id)
        if not employee:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = employee_data.dict(exclude_unset=True)
        
        # Update audit fields
        if user_id:
            update_data["updated_by_id"] = user_id
        
        # Update employee
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        self.db.commit()
        self.db.refresh(employee)
        
        logger.info(f"Updated employee: {employee.full_name()}")
        return employee
    
    def delete_employee(self, employee_id: uuid.UUID) -> bool:
        """Delete an employee."""
        employee = self.get_employee(employee_id)
        if not employee:
            return False
        
        self.db.delete(employee)
        self.db.commit()
        
        logger.info(f"Deleted employee: {employee.full_name()}")
        return True
    
    def add_tag_to_employee(self, employee_id: uuid.UUID, tag_id: uuid.UUID) -> Optional[Employee]:
        """Add a tag to an employee."""
        employee = self.get_employee(employee_id)
        if not employee:
            return None
        
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None
        
        employee.tags.append(tag)
        self.db.commit()
        self.db.refresh(employee)
        
        logger.info(f"Added tag '{tag.name}' to employee: {employee.full_name()}")
        return employee
    
    def remove_tag_from_employee(self, employee_id: uuid.UUID, tag_id: uuid.UUID) -> Optional[Employee]:
        """Remove a tag from an employee."""
        employee = self.get_employee(employee_id)
        if not employee:
            return None
        
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return None
        
        if tag in employee.tags:
            employee.tags.remove(tag)
            self.db.commit()
            self.db.refresh(employee)
            
            logger.info(f"Removed tag '{tag.name}' from employee: {employee.full_name()}")
        
        return employee