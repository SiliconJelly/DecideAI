"""
AI service for the AI Employee Decision System.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from ai_employee_decision_system.core import config, get_logger
from ai_employee_decision_system.services.llm_service import OllamaLLMService, HuggingFaceLLMService
from ai_employee_decision_system.services.retrieval_service import RetrievalService

logger = get_logger(__name__)


class AIService:
    """Service for AI operations using local LLM."""
    
    def __init__(self, model_path: Optional[Path] = None, use_ollama: bool = True):
        """Initialize the AI service with local LLM."""
        self.model_path = model_path or config.ai.model_path
        self.use_ollama = use_ollama
        
        # Initialize LLM service
        if use_ollama:
            self.llm_service = OllamaLLMService()
        else:
            self.llm_service = HuggingFaceLLMService()
        
        # Initialize retrieval service for RAG
        try:
            self.retrieval_service = RetrievalService.from_env()
            if self.retrieval_service.is_available():
                logger.info("Retrieval service initialized for RAG")
            else:
                logger.warning("Retrieval service initialized but index not available. RAG will be disabled.")
                self.retrieval_service = None
        except Exception as e:
            logger.warning(f"Retrieval service initialization failed: {e}. RAG will be disabled.")
            self.retrieval_service = None
        
        logger.info(f"AI Service initialized with {'Ollama' if use_ollama else 'Hugging Face'} LLM")
    
    def _get_employee_context(self) -> Dict[str, Any]:
        """Get employee context for LLM queries."""
        try:
            # Try to get actual employee data from database
            from ai_employee_decision_system.models.database import get_db
            from ai_employee_decision_system.models.employee import Employee
            from sqlalchemy.orm import Session
            
            # This is a simplified version - in production, you'd inject the database session
            context = {
                "employees": [],
                "skills": [],
                "departments": []
            }
            
            # For now, return basic context structure
            # The actual database integration would happen here
            return context
            
        except Exception as e:
            logger.debug(f"Could not fetch employee context: {e}")
            return {
                "employees": [],
                "skills": [],
                "departments": []
            }
    
    def process_query(self, query: str, context: Dict[str, Any] = None, use_rag: bool = True, top_k: int = 5) -> Dict[str, Any]:
        """
        Process a natural language query using local LLM with optional RAG.
        Args:
            query: Natural language query
            context: Additional context for the query
            use_rag: Whether to use retrieval-augmented generation
            top_k: Number of documents to retrieve for RAG context
        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Processing query with LLM: {query}")
        
        # Get employee context for better responses
        employee_context = self._get_employee_context()
        if context:
            employee_context.update(context)
        
        # Retrieve relevant context if RAG is enabled
        if use_rag and self.retrieval_service:
            try:
                results = self.retrieval_service.search(query, top_k=top_k)
                if results:
                    retrieved_texts = []
                    for i, result in enumerate(results):
                        doc_text = f"[Document {i+1} - Score: {result['score']:.3f}]\n{result['text']}"
                        if result.get('metadata'):
                            doc_text += f"\nMetadata: {result['metadata']}"
                        retrieved_texts.append(doc_text)
                    
                    employee_context["retrieved_knowledge"] = "\n\n".join(retrieved_texts)
                    logger.info(f"Retrieved {len(results)} documents for RAG context")
            except Exception as e:
                logger.warning(f"Retrieval failed, continuing without RAG: {e}")
        
        # Use LLM to generate response
        result = self.llm_service.generate_response(query, employee_context)
        
        # Add query metadata
        result["original_query"] = query
        result["timestamp"] = self._get_timestamp()
        result["rag_enabled"] = use_rag and self.retrieval_service is not None
        
        return result
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Legacy methods removed - now using LLM for all queries
    
