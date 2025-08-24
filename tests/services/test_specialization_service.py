"""
Tests for the Specialization service.
"""

import uuid

import pytest

from ai_employee_decision_system.models import EmployeeCreate, SpecializationCreate, SpecializationUpdate
from ai_employee_decision_system.services import EmployeeService, SpecializationService


def test_create_specialization(db_session):
    """Test creating a specialization."""
    # Create services
    employee_service = EmployeeService(db_session)
    specialization_service = SpecializationService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a specialization
    specialization_data = SpecializationCreate(
        name="Machine Learning",
        description="Expertise in machine learning algorithms and applications",
        years_experience=5,
        verified=True,
        source="cv",
    )
    specialization = specialization_service.create_specialization(employee.id, specialization_data)
    
    # Check that the specialization was created
    assert specialization is not None
    assert specialization.id is not None
    assert specialization.name == "Machine Learning"
    assert specialization.description == "Expertise in machine learning algorithms and applications"
    assert specialization.years_experience == 5
    assert specialization.verified is True
    assert specialization.source == "cv"
    assert specialization.employee_id == employee.id


def test_get_specialization(db_session):
    """Test getting a specialization."""
    # Create services
    employee_service = EmployeeService(db_session)
    specialization_service = SpecializationService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a specialization
    specialization_data = SpecializationCreate(
        name="Data Science",
        description="Expertise in data analysis and visualization",
        years_experience=3,
    )
    created_specialization = specialization_service.create_specialization(employee.id, specialization_data)
    
    # Get the specialization
    specialization = specialization_service.get_specialization(created_specialization.id)
    
    # Check that the specialization was retrieved
    assert specialization is not None
    assert specialization.id == created_specialization.id
    assert specialization.name == "Data Science"
    assert specialization.description == "Expertise in data analysis and visualization"
    assert specialization.years_experience == 3
    assert specialization.employee_id == employee.id


def test_get_employee_specializations(db_session):
    """Test getting all specializations for an employee."""
    # Create services
    employee_service = EmployeeService(db_session)
    specialization_service = SpecializationService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Bob",
        last_name="Johnson",
        email="bob.johnson@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create specializations
    specialization_data1 = SpecializationCreate(
        name="Machine Learning",
        years_experience=5,
    )
    specialization_data2 = SpecializationCreate(
        name="Natural Language Processing",
        years_experience=3,
    )
    specialization1 = specialization_service.create_specialization(employee.id, specialization_data1)
    specialization2 = specialization_service.create_specialization(employee.id, specialization_data2)
    
    # Get the employee's specializations
    specializations = specialization_service.get_employee_specializations(employee.id)
    
    # Check that the specializations were retrieved
    assert len(specializations) == 2
    assert any(s.id == specialization1.id for s in specializations)
    assert any(s.id == specialization2.id for s in specializations)


def test_update_specialization(db_session):
    """Test updating a specialization."""
    # Create services
    employee_service = EmployeeService(db_session)
    specialization_service = SpecializationService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Alice",
        last_name="Brown",
        email="alice.brown@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a specialization
    specialization_data = SpecializationCreate(
        name="Machine Learning",
        years_experience=3,
    )
    specialization = specialization_service.create_specialization(employee.id, specialization_data)
    
    # Update the specialization
    update_data = SpecializationUpdate(
        years_experience=5,
        verified=True,
        description="Advanced expertise in machine learning algorithms and applications",
    )
    updated_specialization = specialization_service.update_specialization(specialization.id, update_data)
    
    # Check that the specialization was updated
    assert updated_specialization is not None
    assert updated_specialization.id == specialization.id
    assert updated_specialization.name == "Machine Learning"
    assert updated_specialization.years_experience == 5
    assert updated_specialization.verified is True
    assert updated_specialization.description == "Advanced expertise in machine learning algorithms and applications"


def test_delete_specialization(db_session):
    """Test deleting a specialization."""
    # Create services
    employee_service = EmployeeService(db_session)
    specialization_service = SpecializationService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="Charlie",
        last_name="Davis",
        email="charlie.davis@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a specialization
    specialization_data = SpecializationCreate(
        name="Database Design",
        years_experience=4,
    )
    specialization = specialization_service.create_specialization(employee.id, specialization_data)
    
    # Delete the specialization
    result = specialization_service.delete_specialization(specialization.id)
    
    # Check that the specialization was deleted
    assert result is True
    assert specialization_service.get_specialization(specialization.id) is None


def test_verify_specialization(db_session):
    """Test verifying a specialization."""
    # Create services
    employee_service = EmployeeService(db_session)
    specialization_service = SpecializationService(db_session)
    
    # Create an employee
    employee_data = EmployeeCreate(
        first_name="David",
        last_name="Evans",
        email="david.evans@example.com",
    )
    employee = employee_service.create_employee(employee_data)
    
    # Create a specialization
    specialization_data = SpecializationCreate(
        name="Artificial Intelligence",
        years_experience=4,
        verified=False,
    )
    specialization = specialization_service.create_specialization(employee.id, specialization_data)
    
    # Verify the specialization
    verified_specialization = specialization_service.verify_specialization(specialization.id)
    
    # Check that the specialization was verified
    assert verified_specialization is not None
    assert verified_specialization.id == specialization.id
    assert verified_specialization.verified is True