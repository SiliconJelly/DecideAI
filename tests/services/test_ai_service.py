"""
Tests for the AI service.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest

from ai_employee_decision_system.models import EmployeeCreate
from ai_employee_decision_system.services import AIService, EmployeeService


def test_ai_service_initialization(db_session):
    """Test AI service initialization."""
    ai_service = AIService(db_session)
    
    assert ai_service.db == db_session
    assert ai_service.ocr_processor is not None
    assert ai_service.nlp_processor is not None
    assert ai_service.employee_service is not None


@patch('ai_employee_decision_system.ai.ocr_processor.OCRProcessor.process_document')
def test_process_cv_document_success(mock_ocr, db_session):
    """Test successful CV document processing."""
    # Create test employee
    employee_service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    employee = employee_service.create_employee(employee_data)
    
    # Mock OCR result
    mock_ocr.return_value = {
        "confidence": 0.85,
        "processing_level": 2,
        "language_detected": "english",
        "raw_text": "John Doe Software Engineer Python JavaScript",
        "structured_data": {
            "skills": ["Python", "JavaScript", "SQL"],
            "experience": ["Software Engineer at Tech Corp"]
        }
    }
    
    ai_service = AIService(db_session)
    result = ai_service.process_cv_document(employee.id, "test_cv.pdf")
    
    assert result["success"] is True
    assert result["confidence"] == 0.85
    assert result["processing_level"] == 2
    assert result["language_detected"] == "english"
    assert result["skills_added"] > 0


@patch('ai_employee_decision_system.ai.ocr_processor.OCRProcessor.process_document')
def test_process_cv_document_error(mock_ocr, db_session):
    """Test CV document processing with error."""
    # Create test employee
    employee_service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com"
    )
    employee = employee_service.create_employee(employee_data)
    
    # Mock OCR error
    mock_ocr.return_value = {
        "error": "File not found"
    }
    
    ai_service = AIService(db_session)
    result = ai_service.process_cv_document(employee.id, "nonexistent.pdf")
    
    assert result["success"] is False
    assert "error" in result


def test_process_natural_language_query_employee_search(db_session):
    """Test natural language query processing for employee search."""
    # Create test employees
    employee_service = EmployeeService(db_session)
    
    employee1_data = EmployeeCreate(
        first_name="Alice",
        last_name="Johnson",
        email="alice@example.com",
        department="Engineering"
    )
    employee1 = employee_service.create_employee(employee1_data)
    
    employee2_data = EmployeeCreate(
        first_name="Bob",
        last_name="Smith",
        email="bob@example.com",
        department="Marketing"
    )
    employee2 = employee_service.create_employee(employee2_data)
    
    ai_service = AIService(db_session)
    result = ai_service.process_natural_language_query("find employees in engineering")
    
    assert result["success"] is True
    assert result["intent"]["type"] == "employee_search"
    assert "engineering" in result["response"].lower()


def test_analyze_employee_skills(db_session):
    """Test employee skills analysis."""
    # Create test employee
    employee_service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="Charlie",
        last_name="Brown",
        email="charlie@example.com",
        position="Developer"
    )
    employee = employee_service.create_employee(employee_data)
    
    ai_service = AIService(db_session)
    result = ai_service.analyze_employee_skills(employee.id)
    
    assert result["success"] is True
    assert "employee" in result
    assert result["employee"]["name"] == "Charlie Brown"
    assert "skills_summary" in result
    assert "recommendations" in result


def test_recommend_project_team(db_session):
    """Test project team recommendation."""
    # Create test employees
    employee_service = EmployeeService(db_session)
    
    employees_data = [
        EmployeeCreate(
            first_name="Dev1",
            last_name="Python",
            email="dev1@example.com",
            department="Engineering"
        ),
        EmployeeCreate(
            first_name="Dev2",
            last_name="Java",
            email="dev2@example.com",
            department="Engineering"
        )
    ]
    
    for emp_data in employees_data:
        employee_service.create_employee(emp_data)
    
    ai_service = AIService(db_session)
    
    project_requirements = {
        "description": "Web application development",
        "skills": ["Python", "JavaScript"],
        "team_size": 2
    }
    
    result = ai_service.recommend_project_team(project_requirements)
    
    assert result["success"] is True
    assert "recommendations" in result
    assert len(result["recommendations"]) <= 2
    assert "total_candidates" in result


def test_calculate_employee_project_score(db_session):
    """Test employee project score calculation."""
    # Create test employee with skills
    employee_service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="Skilled",
        last_name="Developer",
        email="skilled@example.com",
        department="Engineering"
    )
    employee = employee_service.create_employee(employee_data)
    
    ai_service = AIService(db_session)
    
    # Test scoring
    required_skills = ["Python", "JavaScript"]
    score = ai_service._calculate_employee_project_score(
        employee, required_skills, "Engineering"
    )
    
    # Should get points for department match
    assert score >= 1.0


def test_get_matching_skills(db_session):
    """Test getting matching skills for an employee."""
    # Create test employee
    employee_service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="Test",
        last_name="Employee",
        email="test@example.com"
    )
    employee = employee_service.create_employee(employee_data)
    
    ai_service = AIService(db_session)
    
    # Test with no skills
    required_skills = ["Python", "JavaScript"]
    matching = ai_service._get_matching_skills(employee, required_skills)
    
    assert isinstance(matching, list)


def test_generate_skill_recommendations(db_session):
    """Test skill recommendation generation."""
    ai_service = AIService(db_session)
    
    # Test with few skills
    few_skills = []
    recommendations = ai_service._generate_skill_recommendations(few_skills, [])
    
    assert len(recommendations) > 0
    assert any("more skills" in rec.lower() for rec in recommendations)
    
    # Test with many unverified skills
    many_unverified_skills = [Mock(verified=False) for _ in range(10)]
    recommendations = ai_service._generate_skill_recommendations(many_unverified_skills, [])
    
    assert any("verified" in rec.lower() for rec in recommendations)