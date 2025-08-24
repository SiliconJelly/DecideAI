"""
Tag service for the AI Employee Decision System.
"""

import uuid
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Session

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.models import Tag, TagCreate, TagUpdate

logger = get_logger(__name__)


class TagService:
    """Service for tag operations."""
    
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
    
    def get_tags(self, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Get all tags with pagination."""
        return self.db.query(Tag).offset(skip).limit(limit).all()
    
    def get_tag(self, tag_id: uuid.UUID) -> Optional[Tag]:
        """Get a tag by ID."""
        return self.db.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        return self.db.query(Tag).filter(Tag.name == name).first()
    
    def create_tag(self, tag_data: TagCreate) -> Tag:
        """Create a new tag."""
        # Check if tag already exists
        existing_tag = self.get_tag_by_name(tag_data.name)
        if existing_tag:
            return existing_tag
        
        # Create tag
        tag = Tag(**tag_data.dict())
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        
        logger.info(f"Created tag: {tag.name}")
        return tag
    
    def update_tag(self, tag_id: uuid.UUID, tag_data: TagUpdate) -> Optional[Tag]:
        """Update an existing tag."""
        tag = self.get_tag(tag_id)
        if not tag:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = tag_data.dict(exclude_unset=True)
        
        # Check if name is being updated and already exists
        if "name" in update_data and update_data["name"] != tag.name:
            existing_tag = self.get_tag_by_name(update_data["name"])
            if existing_tag:
                logger.warning(f"Tag name '{update_data['name']}' already exists")
                return None
        
        # Update tag
        for key, value in update_data.items():
            setattr(tag, key, value)
        
        self.db.commit()
        self.db.refresh(tag)
        
        logger.info(f"Updated tag: {tag.name}")
        return tag
    
    def delete_tag(self, tag_id: uuid.UUID) -> bool:
        """Delete a tag."""
        tag = self.get_tag(tag_id)
        if not tag:
            return False
        
        # Check if tag is used by any employees
        if tag.employees:
            logger.warning(f"Cannot delete tag '{tag.name}' as it is used by {len(tag.employees)} employees")
            return False
        
        self.db.delete(tag)
        self.db.commit()
        
        logger.info(f"Deleted tag: {tag.name}")
        return True