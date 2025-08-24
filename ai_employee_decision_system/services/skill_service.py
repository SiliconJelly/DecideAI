"""
Skill service for the AI Employee Decision System.
"""

import uuid
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models import (
    Employee,
    Skill,
    SkillCreate,
    SkillUpdate,
)

logger = get_logger(__name__)


class SkillService:
    """Service for skill operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def get_skills(self, skip: int = 0, limit: int = 100) -> List[Skill]:
        """Get all skills with pagination."""
        return self.db.query(Skill).offset(skip).limit(limit).all()
    
    def get_skill(self, skill_id: uuid.UUID) -> Optional[Skill]:
        """Get a skill by ID."""
        return self.db.query(Skill).filter(Skill.id == skill_id).first()
    
    def get_employee_skills(self, employee_id: uuid.UUID) -> List[Skill]:
        """Get all skills for an employee."""
        return self.db.query(Skill).filter(Skill.employee_id == employee_id).all()
    
    def create_skill(
        self, employee_id: uuid.UUID, skill_data: SkillCreate
    ) -> Optional[Skill]:
        """Create a new skill for an employee."""
        # Check if employee exists
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            logger.warning(f"Employee with ID {employee_id} not found")
            return None
        
        # Create skill
        skill_dict = skill_data.dict()
        skill_dict["employee_id"] = employee_id
        
        skill = Skill(**skill_dict)
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        
        logger.info(f"Created skill '{skill.name}' for employee: {employee.full_name()}")
        return skill
    
    def update_skill(
        self, skill_id: uuid.UUID, skill_data: SkillUpdate
    ) -> Optional[Skill]:
        """Update an existing skill."""
        skill = self.get_skill(skill_id)
        if not skill:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = skill_data.dict(exclude_unset=True)
        
        # Update skill
        for key, value in update_data.items():
            setattr(skill, key, value)
        
        self.db.commit()
        self.db.refresh(skill)
        
        logger.info(f"Updated skill: {skill.name}")
        return skill
    
    def delete_skill(self, skill_id: uuid.UUID) -> bool:
        """Delete a skill."""
        skill = self.get_skill(skill_id)
        if not skill:
            return False
        
        self.db.delete(skill)
        self.db.commit()
        
        logger.info(f"Deleted skill: {skill.name}")
        return True
    
    def verify_skill(self, skill_id: uuid.UUID) -> Optional[Skill]:
        """Mark a skill as verified."""
        skill = self.get_skill(skill_id)
        if not skill:
            return None
        
        skill.verified = True
        self.db.commit()
        self.db.refresh(skill)
        
        logger.info(f"Verified skill: {skill.name}")
        return skill