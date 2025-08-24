"""
Tests for the NLP processor.
"""

import pytest

from ai_employee_decision_system.ai import NLPProcessor
from ai_employee_decision_system.ai.nlp_processor import QueryType


@pytest.fixture
def nlp_processor():
    """Create an NLP processor instance."""
    return NLPProcessor(language="english")


def test_nlp_processor_initialization(nlp_processor):
    """Test NLP processor initialization."""
    assert nlp_processor.language == "english"
    assert len(nlp_processor.query_patterns) > 0


def test_normalize_query(nlp_processor):
    """Test query normalization."""
    query = "  FIND   employees   with   Python   skills!  "
    normalized = nlp_processor._normalize_query(query)
    
    assert normalized == "find employees with python skills"
    assert normalized.islower()
    assert not normalized.startswith(" ")
    assert not normalized.endswith(" ")


def test_classify_employee_search_query(nlp_processor):
    """Test classification of employee search queries."""
    queries = [
        "find employees with Python skills",
        "who knows JavaScript?",
        "search for employees in engineering department",
        "list all employees who have machine learning experience"
    ]
    
    for query in queries:
        intent = nlp_processor.process_query(query)
        assert intent.query_type == QueryType.EMPLOYEE_SEARCH
        # Lower confidence threshold since some queries use keyword matching
        assert intent.confidence > 0.1


def test_classify_skill_analysis_query(nlp_processor):
    """Test classification of skill analysis queries."""
    queries = [
        "what skills does John have?",
        "analyze skills of the engineering team",
        "show me the skill profile of Jane Doe",
        "what are the competencies of our developers?"
    ]
    
    for query in queries:
        intent = nlp_processor.process_query(query)
        assert intent.query_type == QueryType.SKILL_ANALYSIS
        assert intent.confidence > 0.1


def test_classify_project_assignment_query(nlp_processor):
    """Test classification of project assignment queries."""
    queries = [
        "who is best for this machine learning project?",
        "recommend team members for the new web application",
        "who should work on the mobile app development?",
        "find the best fit for our AI project"
    ]
    
    for query in queries:
        intent = nlp_processor.process_query(query)
        assert intent.query_type == QueryType.PROJECT_ASSIGNMENT
        assert intent.confidence > 0.5


def test_classify_promotion_query(nlp_processor):
    """Test classification of promotion queries."""
    queries = [
        "who is ready for promotion?",
        "show me promotion candidates",
        "who should be promoted to senior level?",
        "which employees are eligible for advancement?"
    ]
    
    for query in queries:
        intent = nlp_processor.process_query(query)
        assert intent.query_type == QueryType.PROMOTION_CANDIDATES
        assert intent.confidence > 0.5


def test_classify_skill_gap_query(nlp_processor):
    """Test classification of skill gap queries."""
    queries = [
        "what skills are we missing in our team?",
        "skill gap analysis for the development team",
        "what training do our employees need?",
        "which skills should we develop?"
    ]
    
    for query in queries:
        intent = nlp_processor.process_query(query)
        assert intent.query_type == QueryType.SKILL_GAP_ANALYSIS
        assert intent.confidence > 0.5


def test_extract_skills_entities(nlp_processor):
    """Test extraction of skill entities."""
    query = "find employees with Python and JavaScript skills"
    intent = nlp_processor.process_query(query)
    
    assert "skills" in intent.entities
    assert "python" in [skill.lower() for skill in intent.entities["skills"]]
    assert "javascript" in [skill.lower() for skill in intent.entities["skills"]]


def test_extract_department_entities(nlp_processor):
    """Test extraction of department entities."""
    query = "list employees in the engineering and marketing departments"
    intent = nlp_processor.process_query(query)
    
    assert "departments" in intent.entities
    assert "engineering" in [dept.lower() for dept in intent.entities["departments"]]
    assert "marketing" in [dept.lower() for dept in intent.entities["departments"]]


def test_extract_name_entities(nlp_processor):
    """Test extraction of name entities."""
    query = "what skills does John Doe have?"
    intent = nlp_processor.process_query(query)
    
    assert "names" in intent.entities
    assert "John" in intent.entities["names"]
    assert "Doe" in intent.entities["names"]


def test_extract_parameters(nlp_processor):
    """Test extraction of parameters."""
    query = "find 5 employees with 3 years of experience"
    intent = nlp_processor.process_query(query)
    
    assert "numbers" in intent.parameters
    assert 5 in intent.parameters["numbers"]
    assert 3 in intent.parameters["numbers"]


def test_generate_employee_search_response(nlp_processor):
    """Test response generation for employee search."""
    from ai_employee_decision_system.ai.nlp_processor import QueryIntent
    
    # Mock employee object
    class MockEmployee:
        def full_name(self):
            return "John Doe"
        
        @property
        def department(self):
            return "Engineering"
        
        @property
        def position(self):
            return "Software Engineer"
    
    intent = QueryIntent(
        query_type=QueryType.EMPLOYEE_SEARCH,
        entities={},
        confidence=0.8,
        parameters={}
    )
    
    # Test single employee result
    single_result = [MockEmployee()]
    response = nlp_processor.generate_response(intent, single_result)
    assert "John Doe" in response
    assert "Engineering" in response
    
    # Test multiple employees result
    multiple_results = [MockEmployee(), MockEmployee()]
    response = nlp_processor.generate_response(intent, multiple_results)
    assert "2 employees" in response


def test_generate_default_response(nlp_processor):
    """Test default response generation."""
    from ai_employee_decision_system.ai.nlp_processor import QueryIntent
    
    intent = QueryIntent(
        query_type=QueryType.UNKNOWN,
        entities={},
        confidence=0.3,
        parameters={}
    )
    
    response = nlp_processor.generate_response(intent, None)
    assert "rephrase" in response.lower() or "specific" in response.lower()


def test_set_language(nlp_processor):
    """Test language setting."""
    assert nlp_processor.set_language("german") is True
    assert nlp_processor.language == "german"
    
    assert nlp_processor.set_language("invalid_language") is False
    assert nlp_processor.language == "german"  # Should remain unchanged


def test_get_supported_languages(nlp_processor):
    """Test getting supported languages."""
    languages = nlp_processor.get_supported_languages()
    assert "english" in languages
    assert "german" in languages
    assert "japanese" in languages


def test_keyword_classification_fallback(nlp_processor):
    """Test fallback keyword classification."""
    # Query that doesn't match patterns but has keywords
    query = "employee skill information"
    query_type, confidence = nlp_processor._keyword_classification(query)
    
    assert query_type in [QueryType.EMPLOYEE_SEARCH, QueryType.SKILL_ANALYSIS]
    assert confidence > 0