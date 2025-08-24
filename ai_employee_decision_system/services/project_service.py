"""
Project service for the AI Employee Decision System.
"""

import uuid
from typing import Dict, List, Optional, Union, Any

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models import Employee, Project, ProjectCreate, ProjectUpdate

logger = get_logger(__name__)


class ProjectService:
    """Service for project operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with pagination."""
        return self.db.query(Project).offset(skip).limit(limit).all()
    
    def get_project(self, project_id: uuid.UUID) -> Optional[Project]:
        """Get a project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """Get a project by name."""
        return self.db.query(Project).filter(Project.name == name).first()
    
    def create_project(
        self, project_data: ProjectCreate, user_id: Optional[uuid.UUID] = None
    ) -> Project:
        """Create a new project."""
        # Convert Pydantic model to dict
        project_dict = project_data.dict()
        
        # Add audit fields
        if user_id:
            project_dict["created_by_id"] = user_id
            project_dict["updated_by_id"] = user_id
        
        # Create project
        project = Project(**project_dict)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Created project: {project.name}")
        return project
    
    def update_project(
        self, project_id: uuid.UUID, project_data: ProjectUpdate, user_id: Optional[uuid.UUID] = None
    ) -> Optional[Project]:
        """Update an existing project."""
        project = self.get_project(project_id)
        if not project:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = project_data.dict(exclude_unset=True)
        
        # Update audit fields
        if user_id:
            update_data["updated_by_id"] = user_id
        
        # Update project
        for key, value in update_data.items():
            setattr(project, key, value)
        
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Updated project: {project.name}")
        return project
    
    def delete_project(self, project_id: uuid.UUID) -> bool:
        """Delete a project."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        
        logger.info(f"Deleted project: {project.name}")
        return True
    
    def add_team_member(self, project_id: uuid.UUID, employee_id: uuid.UUID) -> Optional[Project]:
        """Add an employee to a project team."""
        project = self.get_project(project_id)
        if not project:
            return None
        
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
        
        # Check if employee is already in the team
        if employee in project.team_members:
            logger.info(f"Employee {employee.full_name()} is already in project {project.name}")
            return project
        
        # Add employee to team
        project.team_members.append(employee)
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Added employee {employee.full_name()} to project {project.name}")
        return project
    
    def remove_team_member(self, project_id: uuid.UUID, employee_id: uuid.UUID) -> Optional[Project]:
        """Remove an employee from a project team."""
        project = self.get_project(project_id)
        if not project:
            return None
        
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
        
        # Check if employee is in the team
        if employee not in project.team_members:
            logger.info(f"Employee {employee.full_name()} is not in project {project.name}")
            return project
        
        # Remove employee from team
        project.team_members.remove(employee)
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Removed employee {employee.full_name()} from project {project.name}")
        return project
    
    def get_employee_projects(self, employee_id: uuid.UUID) -> List[Project]:
        """Get all projects for an employee."""
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return []
        
        return employee.projects