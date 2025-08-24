"""
AI Orchestrator - Central component for managing AI operations and backends.

This module provides the AIOrchestrator class that manages multiple AI backends,
handles fallback scenarios, and coordinates AI operations across the system.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from .ollama_service import OllamaService
from .llm_service import OllamaLLMService
from .model_manager import ModelManager
from .multilingual_llm_service import MultilingualLLMService
from .language_service import LanguageService

logger = logging.getLogger(__name__)


class AIBackend(Enum):
    """Available AI backends."""
    OLLAMA = "ollama"
    STANDALONE = "standalone"
    FALLBACK = "fallback"


@dataclass
class AIResponse:
    """Enhanced AI response with metadata."""
    response: str
    confidence: float
    query_type: str
    language: str
    model_used: str
    processing_time: float
    fallback_used: bool
    context_maintained: bool
    backend_used: AIBackend
    metadata: Dict[str, Any]


@dataclass
class SystemStatus:
    """System status information."""
    primary_backend: AIBackend
    available_backends: List[AIBackend]
    active_models: List[str]
    health_status: str
    performance_metrics: Dict[str, float]
    last_updated: float


class AIOrchestrator:
    """
    Central orchestrator for AI operations.
    
    Manages multiple AI backends, handles fallback scenarios, and provides
    a unified interface for AI operations across the system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI orchestrator."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize backends
        self.ollama_service = None
        self.standalone_service = None
        self.model_manager = None
        self.multilingual_service = None
        self.language_service = None
        
        # Configuration
        self.preferred_backend = AIBackend.OLLAMA
        self.fallback_enabled = True
        self.timeout_seconds = 30
        self.max_retries = 2
        
        # State tracking
        self.backend_health = {}
        self.performance_metrics = {}
        self.last_health_check = 0
        self.health_check_interval = 60  # seconds
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize available AI backends."""
        try:
            # Initialize Ollama service
            self.ollama_service = OllamaService()
            self.model_manager = ModelManager(self.ollama_service)
            
            # Initialize language service
            self.language_service = LanguageService()
            
            # Initialize multilingual service
            self.multilingual_service = MultilingualLLMService(
                self.ollama_service, 
                self.model_manager, 
                self.language_service
            )
            
            # Initialize standalone service
            self.standalone_service = OllamaLLMService()
            
            # Check initial health
            self._update_backend_health()
            
            self.logger.info("AI Orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI backends: {e}")
            self.fallback_enabled = True
    
    def _update_backend_health(self):
        """Update health status of all backends."""
        current_time = time.time()
        
        # Check if we need to update health status
        if current_time - self.last_health_check < self.health_check_interval:
            return
        
        try:
            # Check Ollama health
            if self.ollama_service:
                ollama_healthy = self.ollama_service.is_available()
                self.backend_health[AIBackend.OLLAMA] = {
                    'healthy': ollama_healthy,
                    'last_check': current_time,
                    'models_available': len(self.ollama_service.list_models()) if ollama_healthy else 0
                }
            
            # Check standalone service health
            if self.standalone_service:
                standalone_healthy = True  # Standalone is always available
                self.backend_health[AIBackend.STANDALONE] = {
                    'healthy': standalone_healthy,
                    'last_check': current_time,
                    'models_available': 1
                }
            
            self.last_health_check = current_time
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    def _get_best_backend(self) -> AIBackend:
        """Determine the best available backend."""
        self._update_backend_health()
        
        # Try preferred backend first
        if self.preferred_backend in self.backend_health:
            if self.backend_health[self.preferred_backend]['healthy']:
                return self.preferred_backend
        
        # Try Ollama if available
        if (AIBackend.OLLAMA in self.backend_health and 
            self.backend_health[AIBackend.OLLAMA]['healthy']):
            return AIBackend.OLLAMA
        
        # Fall back to standalone
        if (AIBackend.STANDALONE in self.backend_health and 
            self.backend_health[AIBackend.STANDALONE]['healthy']):
            return AIBackend.STANDALONE
        
        # Last resort fallback
        return AIBackend.FALLBACK
    
    def process_query(
        self, 
        query: str, 
        context: Optional[Dict] = None,
        language: Optional[str] = None,
        model_preference: Optional[str] = None
    ) -> AIResponse:
        """
        Process a query using the best available AI backend.
        
        Args:
            query: The user query to process
            context: Optional context for the query
            language: Preferred language for response
            model_preference: Preferred model to use
            
        Returns:
            AIResponse with the processed result
        """
        start_time = time.time()
        context = context or {}
        language = language or "en"
        
        # Determine best backend
        backend = self._get_best_backend()
        fallback_used = backend != self.preferred_backend
        
        try:
            # Process with selected backend
            if backend == AIBackend.OLLAMA:
                response = self._process_with_ollama(
                    query, context, language, model_preference
                )
            elif backend == AIBackend.STANDALONE:
                response = self._process_with_standalone(
                    query, context, language
                )
            else:
                response = self._process_with_fallback(query, language)
            
            processing_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(backend, processing_time, True)
            
            return AIResponse(
                response=response,
                confidence=0.8 if backend == AIBackend.OLLAMA else 0.6,
                query_type="general",
                language=language,
                model_used=model_preference or "default",
                processing_time=processing_time,
                fallback_used=fallback_used,
                context_maintained=bool(context),
                backend_used=backend,
                metadata={
                    'backend_health': self.backend_health.get(backend, {}),
                    'retry_count': 0
                }
            )
            
        except Exception as e:
            self.logger.error(f"Query processing failed with {backend}: {e}")
            
            # Try fallback if enabled and not already using fallback
            if self.fallback_enabled and backend != AIBackend.FALLBACK:
                return self._process_with_fallback_on_error(
                    query, language, start_time, str(e)
                )
            
            # Return error response
            processing_time = time.time() - start_time
            self._update_performance_metrics(backend, processing_time, False)
            
            return AIResponse(
                response=f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}",
                confidence=0.0,
                query_type="error",
                language=language,
                model_used="error",
                processing_time=processing_time,
                fallback_used=True,
                context_maintained=False,
                backend_used=AIBackend.FALLBACK,
                metadata={'error': str(e)}
            )
    
    def _process_with_ollama(
        self, 
        query: str, 
        context: Dict, 
        language: str, 
        model_preference: Optional[str]
    ) -> str:
        """Process query with Ollama backend using multilingual service."""
        if not self.multilingual_service:
            raise Exception("Multilingual service not available")
        
        # Use the multilingual service for enhanced processing
        result = self.multilingual_service.process_query(
            query=query,
            language=language,
            context=context,
            model_name=model_preference
        )
        
        if result.get("status") == "error":
            raise Exception(result.get("error", "Unknown error"))
        
        return result.get("response", "No response generated")
    
    def _process_with_standalone(
        self, 
        query: str, 
        context: Dict, 
        language: str
    ) -> str:
        """Process query with standalone backend."""
        if not self.standalone_service:
            raise Exception("Standalone service not available")
        
        # Use existing standalone service
        result = self.standalone_service.generate_response(query, context)
        response = result.get('response', 'No response generated')
        
        # Add language-specific formatting if needed
        if language != "en":
            response = f"[{language.upper()}] {response}"
        
        return response
    
    def _process_with_fallback(self, query: str, language: str) -> str:
        """Process query with basic fallback responses."""
        fallback_responses = {
            "en": "I'm currently experiencing technical difficulties. Please try again later or contact support.",
            "de": "Ich habe derzeit technische Schwierigkeiten. Bitte versuchen Sie es später erneut oder wenden Sie sich an den Support.",
            "ja": "現在技術的な問題が発生しています。後でもう一度お試しいただくか、サポートにお問い合わせください。"
        }
        
        return fallback_responses.get(language, fallback_responses["en"])
    
    def _process_with_fallback_on_error(
        self, 
        query: str, 
        language: str, 
        start_time: float, 
        error: str
    ) -> AIResponse:
        """Handle fallback processing when primary backend fails."""
        try:
            # Try standalone service as fallback
            if (self.standalone_service and 
                self.backend_health.get(AIBackend.STANDALONE, {}).get('healthy', False)):
                
                response = self._process_with_standalone(query, {}, language)
                processing_time = time.time() - start_time
                
                return AIResponse(
                    response=response,
                    confidence=0.4,
                    query_type="fallback",
                    language=language,
                    model_used="standalone_fallback",
                    processing_time=processing_time,
                    fallback_used=True,
                    context_maintained=False,
                    backend_used=AIBackend.STANDALONE,
                    metadata={'original_error': error, 'fallback_reason': 'primary_backend_failed'}
                )
            
            # Use basic fallback
            response = self._process_with_fallback(query, language)
            processing_time = time.time() - start_time
            
            return AIResponse(
                response=response,
                confidence=0.1,
                query_type="fallback",
                language=language,
                model_used="basic_fallback",
                processing_time=processing_time,
                fallback_used=True,
                context_maintained=False,
                backend_used=AIBackend.FALLBACK,
                metadata={'original_error': error, 'fallback_reason': 'all_backends_failed'}
            )
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback processing also failed: {fallback_error}")
            processing_time = time.time() - start_time
            
            return AIResponse(
                response="System temporarily unavailable. Please try again later.",
                confidence=0.0,
                query_type="error",
                language=language,
                model_used="error",
                processing_time=processing_time,
                fallback_used=True,
                context_maintained=False,
                backend_used=AIBackend.FALLBACK,
                metadata={
                    'original_error': error,
                    'fallback_error': str(fallback_error)
                }
            )
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for the specified language."""
        prompts = {
            "en": "You are a helpful AI assistant for HR and employee management. Provide professional, accurate, and helpful responses.",
            "de": "Sie sind ein hilfreicher KI-Assistent für HR und Mitarbeiterverwaltung. Geben Sie professionelle, genaue und hilfreiche Antworten.",
            "ja": "あなたは人事・従業員管理のための有用なAIアシスタントです。専門的で正確、かつ有用な回答を提供してください。"
        }
        
        return prompts.get(language, prompts["en"])
    
    def _update_performance_metrics(
        self, 
        backend: AIBackend, 
        processing_time: float, 
        success: bool
    ):
        """Update performance metrics for a backend."""
        if backend not in self.performance_metrics:
            self.performance_metrics[backend] = {
                'total_requests': 0,
                'successful_requests': 0,
                'average_response_time': 0.0,
                'last_response_time': 0.0
            }
        
        metrics = self.performance_metrics[backend]
        metrics['total_requests'] += 1
        metrics['last_response_time'] = processing_time
        
        if success:
            metrics['successful_requests'] += 1
        
        # Update average response time
        if metrics['total_requests'] > 0:
            success_rate = metrics['successful_requests'] / metrics['total_requests']
            metrics['average_response_time'] = (
                (metrics['average_response_time'] * (metrics['total_requests'] - 1) + processing_time) /
                metrics['total_requests']
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available models across all backends."""
        models = []
        
        try:
            if (self.ollama_service and 
                self.backend_health.get(AIBackend.OLLAMA, {}).get('healthy', False)):
                models.extend(self.ollama_service.list_models())
        except Exception as e:
            self.logger.error(f"Failed to get Ollama models: {e}")
        
        # Add standalone model
        if self.backend_health.get(AIBackend.STANDALONE, {}).get('healthy', False):
            models.append("standalone")
        
        return models
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        try:
            if self.model_manager:
                return self.model_manager.switch_model(model_name)
            return False
        except Exception as e:
            self.logger.error(f"Failed to switch model to {model_name}: {e}")
            return False
    
    def get_system_status(self) -> SystemStatus:
        """Get current system status."""
        self._update_backend_health()
        
        available_backends = [
            backend for backend, health in self.backend_health.items()
            if health.get('healthy', False)
        ]
        
        primary_backend = self._get_best_backend()
        
        return SystemStatus(
            primary_backend=primary_backend,
            available_backends=available_backends,
            active_models=self.get_available_models(),
            health_status="healthy" if available_backends else "degraded",
            performance_metrics=self.performance_metrics,
            last_updated=time.time()
        )
    
    def set_fallback_mode(self, enabled: bool) -> None:
        """Enable or disable fallback mode."""
        self.fallback_enabled = enabled
        self.logger.info(f"Fallback mode {'enabled' if enabled else 'disabled'}")
    
    def set_preferred_backend(self, backend: AIBackend) -> None:
        """Set the preferred AI backend."""
        self.preferred_backend = backend
        self.logger.info(f"Preferred backend set to {backend.value}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.logger.info("AI Orchestrator cleaned up")