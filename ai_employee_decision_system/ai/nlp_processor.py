"""
Natural Language Processing module for handling user queries and generating responses.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ai_employee_decision_system.core import get_logger

logger = get_logger(__name__)


class QueryType(Enum):
    """Types of queries the system can handle."""
    EMPLOYEE_SEARCH = "employee_search"
    SKILL_ANALYSIS = "skill_analysis"
    PROJECT_ASSIGNMENT = "project_assignment"
    PROMOTION_CANDIDATES = "promotion_candidates"
    SKILL_GAP_ANALYSIS = "skill_gap_analysis"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"


@dataclass
class QueryIntent:
    """Represents the parsed intent of a user query."""
    query_type: QueryType
    entities: Dict[str, Any]
    confidence: float
    parameters: Dict[str, Any]


class NLPProcessor:
    """
    Natural Language Processor for understanding user queries and generating responses.
    This is a simplified implementation that would use a fine-tuned model in production.
    """
    
    def __init__(self, language: str = "english"):
        """
        Initialize the NLP processor.
        
        Args:
            language: Primary language for processing (english, german, japanese)
        """
        self.language = language
        self.query_patterns = self._initialize_query_patterns()
        
        logger.info("NLP Processor initialized for language: %s", language)
    
    def process_query(self, query: str) -> QueryIntent:
        """
        Process a natural language query and extract intent.
        
        Args:
            query: User's natural language query
            
        Returns:
            QueryIntent object with parsed information
        """
        logger.debug("Processing query: %s", query)
        
        # Clean and normalize the query
        normalized_query = self._normalize_query(query)
        
        # Extract intent and entities
        query_type, confidence = self._classify_query(normalized_query)
        entities = self._extract_entities(normalized_query, query_type)
        parameters = self._extract_parameters(normalized_query, query_type)
        
        intent = QueryIntent(
            query_type=query_type,
            entities=entities,
            confidence=confidence,
            parameters=parameters
        )
        
        logger.debug("Query processed: type=%s, confidence=%f", query_type.value, confidence)
        return intent
    
    def generate_response(self, intent: QueryIntent, results: Any) -> str:
        """
        Generate a natural language response based on query intent and results.
        
        Args:
            intent: Parsed query intent
            results: Results from the query execution
            
        Returns:
            Natural language response
        """
        logger.debug("Generating response for query type: %s", intent.query_type.value)
        
        if intent.query_type == QueryType.EMPLOYEE_SEARCH:
            return self._generate_employee_search_response(intent, results)
        elif intent.query_type == QueryType.SKILL_ANALYSIS:
            return self._generate_skill_analysis_response(intent, results)
        elif intent.query_type == QueryType.PROJECT_ASSIGNMENT:
            return self._generate_project_assignment_response(intent, results)
        elif intent.query_type == QueryType.PROMOTION_CANDIDATES:
            return self._generate_promotion_response(intent, results)
        elif intent.query_type == QueryType.SKILL_GAP_ANALYSIS:
            return self._generate_skill_gap_response(intent, results)
        else:
            return self._generate_default_response(intent, results)
    
    def _initialize_query_patterns(self) -> Dict[QueryType, List[str]]:
        """Initialize patterns for query classification."""
        patterns = {
            QueryType.EMPLOYEE_SEARCH: [
                r"find.*employee.*with.*skill",
                r"who.*knows.*(?:python|java|javascript|programming)",
                r"search.*employee.*(?:name|email|department)",
                r"list.*employees.*in.*department",
                r"show.*me.*employees.*who"
            ],
            QueryType.SKILL_ANALYSIS: [
                r"what.*skills.*does.*(?:employee|person).*have",
                r"analyze.*skills.*of",
                r"skill.*profile.*of",
                r"competencies.*of",
                r"expertise.*of"
            ],
            QueryType.PROJECT_ASSIGNMENT: [
                r"who.*(?:best|suitable).*for.*project",
                r"assign.*employee.*to.*project",
                r"recommend.*team.*for",
                r"best.*fit.*for.*(?:project|task)",
                r"who.*should.*work.*on"
            ],
            QueryType.PROMOTION_CANDIDATES: [
                r"who.*ready.*for.*promotion",
                r"promotion.*candidates",
                r"who.*should.*be.*promoted",
                r"eligible.*for.*promotion",
                r"next.*level.*candidates"
            ],
            QueryType.SKILL_GAP_ANALYSIS: [
                r"skill.*gap.*analysis",
                r"what.*skills.*(?:missing|lacking|needed)",
                r"training.*needs.*analysis",
                r"skill.*deficiencies",
                r"what.*skills.*should.*we.*develop"
            ]
        }
        
        # Compile regex patterns
        compiled_patterns = {}
        for query_type, pattern_list in patterns.items():
            compiled_patterns[query_type] = [re.compile(pattern, re.IGNORECASE) for pattern in pattern_list]
        
        return compiled_patterns
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the query for processing."""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove punctuation at the end
        normalized = re.sub(r'[.!?]+$', '', normalized)
        
        return normalized
    
    def _classify_query(self, query: str) -> Tuple[QueryType, float]:
        """Classify the query type and return confidence score."""
        best_match = QueryType.UNKNOWN
        best_confidence = 0.0
        
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    # Higher base confidence for pattern matches
                    confidence = 0.85 + (len(pattern.pattern) / 2000)  # Longer patterns = higher confidence
                    if confidence > best_confidence:
                        best_match = query_type
                        best_confidence = min(confidence, 1.0)
        
        # If no pattern matches, try keyword-based classification
        if best_match == QueryType.UNKNOWN:
            best_match, best_confidence = self._keyword_classification(query)
        
        return best_match, best_confidence
    
    def _keyword_classification(self, query: str) -> Tuple[QueryType, float]:
        """Fallback classification based on keywords."""
        keywords = {
            QueryType.EMPLOYEE_SEARCH: ['employee', 'person', 'staff', 'worker', 'find', 'search'],
            QueryType.SKILL_ANALYSIS: ['skill', 'ability', 'competency', 'expertise', 'knowledge'],
            QueryType.PROJECT_ASSIGNMENT: ['project', 'task', 'assignment', 'team', 'work'],
            QueryType.PROMOTION_CANDIDATES: ['promotion', 'advance', 'promote', 'next level'],
            QueryType.SKILL_GAP_ANALYSIS: ['gap', 'missing', 'lacking', 'need', 'training']
        }
        
        scores = {}
        for query_type, keyword_list in keywords.items():
            score = sum(1 for keyword in keyword_list if keyword in query)
            if score > 0:
                scores[query_type] = score / len(keyword_list)
        
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type, min(scores[best_type] * 0.8, 0.9)  # Higher confidence for keyword matching
        
        return QueryType.GENERAL_INFO, 0.3
    
    def _extract_entities(self, query: str, query_type: QueryType) -> Dict[str, Any]:
        """Extract entities from the query based on type."""
        entities = {}
        
        # Extract common entities
        entities.update(self._extract_skills(query))
        entities.update(self._extract_departments(query))
        entities.update(self._extract_names(query))
        
        return entities
    
    def _extract_skills(self, query: str) -> Dict[str, List[str]]:
        """Extract skill mentions from the query."""
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'sql', 'mysql', 'postgresql', 'mongodb',
            'aws', 'azure', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data science'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in query.lower():
                found_skills.append(skill)
        
        return {"skills": found_skills} if found_skills else {}
    
    def _extract_departments(self, query: str) -> Dict[str, List[str]]:
        """Extract department mentions from the query."""
        departments = [
            'engineering', 'development', 'it', 'marketing', 'sales', 'hr',
            'finance', 'operations', 'research', 'design', 'qa', 'testing'
        ]
        
        found_departments = []
        for dept in departments:
            if dept.lower() in query.lower():
                found_departments.append(dept)
        
        return {"departments": found_departments} if found_departments else {}
    
    def _extract_names(self, query: str) -> Dict[str, List[str]]:
        """Extract potential names from the query."""
        # Simple name extraction - look for capitalized words
        words = query.split()
        potential_names = []
        
        for word in words:
            if word.istitle() and len(word) > 2 and word.isalpha():
                potential_names.append(word)
        
        return {"names": potential_names} if potential_names else {}
    
    def _extract_parameters(self, query: str, query_type: QueryType) -> Dict[str, Any]:
        """Extract parameters specific to the query type."""
        parameters = {}
        
        # Extract numbers (could be years of experience, team size, etc.)
        numbers = re.findall(r'\b\d+\b', query)
        if numbers:
            parameters["numbers"] = [int(n) for n in numbers]
        
        # Extract time-related terms
        time_terms = re.findall(r'\b(?:year|month|week|day)s?\b', query, re.IGNORECASE)
        if time_terms:
            parameters["time_units"] = time_terms
        
        return parameters
    
    def _generate_employee_search_response(self, intent: QueryIntent, results: Any) -> str:
        """Generate response for employee search queries."""
        if not results:
            return "I couldn't find any employees matching your criteria."
        
        if isinstance(results, list):
            if len(results) == 1:
                employee = results[0]
                return f"I found {employee.full_name()} in the {employee.department} department. They work as a {employee.position}."
            else:
                names = [emp.full_name() for emp in results[:5]]  # Limit to first 5
                return f"I found {len(results)} employees: {', '.join(names)}{'...' if len(results) > 5 else ''}."
        
        return "Here are the employee search results."
    
    def _generate_skill_analysis_response(self, intent: QueryIntent, results: Any) -> str:
        """Generate response for skill analysis queries."""
        if not results:
            return "I couldn't find skill information for the specified employee."
        
        return "Here's the skill analysis you requested."
    
    def _generate_project_assignment_response(self, intent: QueryIntent, results: Any) -> str:
        """Generate response for project assignment queries."""
        if not results:
            return "I couldn't find suitable candidates for this project."
        
        return "Based on the project requirements, here are my recommendations."
    
    def _generate_promotion_response(self, intent: QueryIntent, results: Any) -> str:
        """Generate response for promotion candidate queries."""
        if not results:
            return "I couldn't identify any promotion candidates at this time."
        
        return "Here are the employees who might be ready for promotion."
    
    def _generate_skill_gap_response(self, intent: QueryIntent, results: Any) -> str:
        """Generate response for skill gap analysis queries."""
        return "Here's the skill gap analysis for your team."
    
    def _generate_default_response(self, intent: QueryIntent, results: Any) -> str:
        """Generate a default response for unknown query types."""
        return "I understand you're asking about employees or skills. Could you please rephrase your question more specifically?"
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return ["english", "german", "japanese"]
    
    def set_language(self, language: str) -> bool:
        """Set the processing language."""
        if language in self.get_supported_languages():
            self.language = language
            logger.info("Language set to: %s", language)
            return True
        return False