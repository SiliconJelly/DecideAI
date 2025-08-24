"""
Tests for the Employee service.
"""

import uuid
from datetime import date

import pytest

from ai_employee_decision_system.models import EmployeeCreate, EmployeeUpdate, TagCreate
from ai_employee_decision_system.services import EmployeeService, TagService


def test_create_employee(db_session):
    """Test creating an employee."""
    # Create employee service
    employee_service = EmployeeService(db_session)
    
    # Create employee data
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        position="Professor",
        department="Computer Science",
        hire_date=date(2020, 1, 15),
        background="PhD in Computer Science with 10 years of teaching experience.",
        custom_fields={
            "office_number": "CS-301",
            "research_interests": ["AI", "Machine Learning", "NLP"]
        }
    )
    
    # Create employee
    employee = employee_service.create_employee(employee_data)
    
    # Check that the employee was created
    assert employee.id is not None
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.email == "john.doe@example.com"
    assert employee.position == "Professor"
    assert employee.department == "Computer Science"
    assert employee.hire_date == date(2020, 1, 15)
    assert employee.background == "PhD in Computer Science with 10 years of teaching experience."
    assert employee.custom_fields == {
        "office_number": "CS-301",
        "research_interests": ["AI", "Machine Learning", "NLP"]
    }


def test_get_employee(db_session):
    """Test getting an employee."""
    # Create employee service
    employee_service = EmployeeService(db_session)
    
    # Create employee data
    employee_data = EmployeeCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
    )
    
    # Create employee
    created_employee = employee_service.create_employee(employee_data)
    
    # Get employee
    employee = employee_service.get_employee(created_employee.id)
    
    # Check that the employee was retrieved
    assert employee is not None
    assert employee.id == created_employee.id
    assert employee.first_name == "Jane"
    assert employee.last_name == "Smith"
    assert employee.email == "jane.smith@example.com"


def test_get_employee_by_email(db_session):
    """Test getting an employee by email."""
    # Create employee service
    employee_service = EmployeeService(db_session)
    
    # Create employee data
    employee_data = EmployeeCreate(
        first_name="Bob",
        last_name="Johnson",
        email="bob.johnson@example.com",
    )
    
    # Create employee
    created_employee = employee_service.create_employee(employee_data)
    
    # Get employee by email
    employee = employee_service.get_employee_by_email("bob.johnson@example.com")
    
    # Check that the employee was retrieved
    assert employee is not None
    assert employee.id == created_employee.id
    assert employee.first_name == "Bob"
    assert employee.last_name == "Johnson"
    assert employee.email == "bob.johnson@example.com"


def test_update_employee(db_session):
    """Test updating an employee."""
    # Create employee service
    employee_service = EmployeeService(db_session)
    
    # Create employee data
    employee_data = EmployeeCreate(
        first_name="Alice",
        last_name="Brown",
        email="alice.brown@example.com",
    )
    
    # Create employee
    created_employee = employee_service.create_employee(employee_data)
    
    # Update employee data
    update_data = EmployeeUpdate(
        position="Associate Professor",
        department="Data Science",
    )
    
    # Update employee
    updated_employee = employee_service.update_employee(created_employee.id, update_data)
    
    # Check that the employee was updated
    assert updated_employee is not None
    assert updated_employee.id == created_employee.id
    assert updated_employee.first_name == "Alice"
    assert updated_employee.last_name == "Brown"
    assert updated_employee.email == "alice.brown@example.com"
    assert updated_employee.position == "Associate Professor"
    assert updated_employee.department == "Data Science"


def test_delete_employee(db_session):
    """Test deleting an employee."""
    # Create employee service
    employee_service = EmployeeService(db_session)
    
    # Create employee data
    employee_data = EmployeeCreate(
        first_name="Charlie",
        last_name="Davis",
        email="charlie.davis@example.com",
    )
    
    # Create employee
    created_employee = employee_service.create_employee(employee_data)
    
    # Delete employee
    result = employee_service.delete_employee(created_employee.id)
    
    # Check that the employee was deleted
    assert result is True
    assert employee_service.get_employee(created_employee.id) is None


def test_add_tag_to_employee(db_session):
    """Test adding a tag to an employee."""
    # Create services
    employee_service = EmployeeService(db_session)
    tag_service = TagService(db_session)
    
    # Create employee
    employee_data = EmployeeCreate(
        first_name="David",
        last_name="Evans",
        email="david.evans@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create tag
    tag_data = TagCreate(
        name="Research",
        description="Faculty involved in research",
    )
    tag = tag_service.create_tag(tag_data)
    
    # Add tag to employee
    updated_employee = employee_service.add_tag_to_employee(employee.id, tag.id)
    
    # Check that the tag was added
    assert updated_employee is not None
    assert len(updated_employee.tags) == 1
    assert updated_employee.tags[0].id == tag.id
    assert updated_employee.tags[0].name == "Research"