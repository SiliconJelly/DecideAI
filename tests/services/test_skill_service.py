"""
Tests for the Skill service.
"""

import uuid

import pytest

from ai_employee_decision_system.models import EmployeeCreate, SkillCreate, SkillUpdate
from ai_employee_decision_system.services import EmployeeService, SkillService


def test_create_skill(db_session):
    """Test creating a skill."""
    # Create services
    employee_service = EmployeeService(db_session)
    skill_service = SkillService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a skill
    skill_data = SkillCreate(
        name="Python",
        category="Programming",
        level=5,
        verified=True,
        source="cv",
        description="Advanced Python programming skills",
    )
    skill = skill_service.create_skill(employee.id, skill_data)
    
    # Check that the skill was created
    assert skill is not None
    assert skill.id is not None
    assert skill.name == "Python"
    assert skill.category == "Programming"
    assert skill.level == 5
    assert skill.verified is True
    assert skill.source == "cv"
    assert skill.description == "Advanced Python programming skills"
    assert skill.employee_id == employee.id


def test_get_skill(db_session):
    """Test getting a skill."""
    # Create services
    employee_service = EmployeeService(db_session)
    skill_service = SkillService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a skill
    skill_data = SkillCreate(
        name="Java",
        category="Programming",
        level=4,
    )
    created_skill = skill_service.create_skill(employee.id, skill_data)
    
    # Get the skill
    skill = skill_service.get_skill(created_skill.id)
    
    # Check that the skill was retrieved
    assert skill is not None
    assert skill.id == created_skill.id
    assert skill.name == "Java"
    assert skill.category == "Programming"
    assert skill.level == 4
    assert skill.employee_id == employee.id


def test_get_employee_skills(db_session):
    """Test getting all skills for an employee."""
    # Create services
    employee_service = EmployeeService(db_session)
    skill_service = SkillService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Bob",
        last_name="Johnson",
        email="bob.johnson@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create skills
    skill_data1 = SkillCreate(
        name="Python",
        category="Programming",
        level=5,
    )
    skill_data2 = SkillCreate(
        name="JavaScript",
        category="Programming",
        level=4,
    )
    skill1 = skill_service.create_skill(employee.id, skill_data1)
    skill2 = skill_service.create_skill(employee.id, skill_data2)
    
    # Get the employee's skills
    skills = skill_service.get_employee_skills(employee.id)
    
    # Check that the skills were retrieved
    assert len(skills) == 2
    assert any(s.id == skill1.id for s in skills)
    assert any(s.id == skill2.id for s in skills)


def test_update_skill(db_session):
    """Test updating a skill."""
    # Create services
    employee_service = EmployeeService(db_session)
    skill_service = SkillService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Alice",
        last_name="Brown",
        email="alice.brown@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a skill
    skill_data = SkillCreate(
        name="Python",
        category="Programming",
        level=3,
    )
    skill = skill_service.create_skill(employee.id, skill_data)
    
    # Update the skill
    update_data = SkillUpdate(
        level=5,
        verified=True,
        description="Advanced Python programming skills",
    )
    updated_skill = skill_service.update_skill(skill.id, update_data)
    
    # Check that the skill was updated
    assert updated_skill is not None
    assert updated_skill.id == skill.id
    assert updated_skill.name == "Python"
    assert updated_skill.category == "Programming"
    assert updated_skill.level == 5
    assert updated_skill.verified is True
    assert updated_skill.description == "Advanced Python programming skills"


def test_delete_skill(db_session):
    """Test deleting a skill."""
    # Create services
    employee_service = EmployeeService(db_session)
    skill_service = SkillService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Charlie",
        last_name="Davis",
        email="charlie.davis@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a skill
    skill_data = SkillCreate(
        name="SQL",
        category="Database",
        level=4,
    )
    skill = skill_service.create_skill(employee.id, skill_data)
    
    # Delete the skill
    result = skill_service.delete_skill(skill.id)
    
    # Check that the skill was deleted
    assert result is True
    assert skill_service.get_skill(skill.id) is None


def test_verify_skill(db_session):
    """Test verifying a skill."""
    # Create services
    employee_service = EmployeeService(db_session)
    skill_service = SkillService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="David",
        last_name="Evans",
        email="david.evans@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a skill
    skill_data = SkillCreate(
        name="C++",
        category="Programming",
        level=4,
        verified=False,
    )
    skill = skill_service.create_skill(employee.id, skill_data)
    
    # Verify the skill
    verified_skill = skill_service.verify_skill(skill.id)
    
    # Check that the skill was verified
    assert verified_skill is not None
    assert verified_skill.id == skill.id
    assert verified_skill.verified is True