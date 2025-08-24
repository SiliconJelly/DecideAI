"""
Unit tests for AI Orchestrator.

Tests the AI orchestrator's ability to manage multiple backends,
handle fallbacks, and coordinate AI operations.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from ai_employee_decision_system.services.ai_orchestrator import (
    AIOrchestrator, AIBackend, AIResponse, SystemStatus
)


class TestAIOrchestrator:
    """Test cases for AI Orchestrator."""
    
    @pytest.fixture
    def mock_ollama_service(self):
        """Mock Ollama service."""
        mock = Mock()
        mock.is_available.return_value = True
        mock.list_models.return_value = ["llama3.2:3b", "llama3.2:1b"]
        mock.generate_response.return_value = "Test response from Ollama"
        return mock
    
    @pytest.fixture
    def mock_standalone_service(self):
        """Mock standalone service."""
        mock = Mock()
        mock.generate_response.return_value = {"response": "Test response from standalone"}
        return mock
    
    @pytest.fixture
    def mock_model_manager(self):
        """Mock model manager."""
        mock = Mock()
        mock.switch_model.return_value = True
        return mock
    
    @pytest.fixture
    def orchestrator(self, mock_ollama_service, mock_standalone_service, mock_model_manager):
        """Create AI orchestrator with mocked dependencies."""
        with patch('ai_employee_decision_system.services.ai_orchestrator.OllamaService') as mock_ollama_cls, \
             patch('ai_employee_decision_system.services.ai_orchestrator.OllamaLLMService') as mock_standalone_cls, \
             patch('ai_employee_decision_system.services.ai_orchestrator.ModelManager') as mock_manager_cls:
            
            mock_ollama_cls.return_value = mock_ollama_service
            mock_standalone_cls.return_value = mock_standalone_service
            mock_manager_cls.return_value = mock_model_manager
            
            orchestrator = AIOrchestrator()
            return orchestrator
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.preferred_backend == AIBackend.OLLAMA
        assert orchestrator.fallback_enabled is True
        assert orchestrator.ollama_service is not None
        assert orchestrator.standalone_service is not None
        assert orchestrator.model_manager is not None
    
    def test_backend_health_check(self, orchestrator, mock_ollama_service):
        """Test backend health checking."""
        # Test healthy Ollama
        mock_ollama_service.is_available.return_value = True
        orchestrator._update_backend_health()
        
        assert AIBackend.OLLAMA in orchestrator.backend_health
        assert orchestrator.backend_health[AIBackend.OLLAMA]['healthy'] is True
        assert orchestrator.backend_health[AIBackend.STANDALONE]['healthy'] is True
    
    def test_get_best_backend_ollama_healthy(self, orchestrator, mock_ollama_service):
        """Test backend selection when Ollama is healthy."""
        mock_ollama_service.is_available.return_value = True
        backend = orchestrator._get_best_backend()
        assert backend == AIBackend.OLLAMA
    
    def test_get_best_backend_ollama_unhealthy(self, orchestrator, mock_ollama_service):
        """Test backend selection when Ollama is unhealthy."""
        mock_ollama_service.is_available.return_value = False
        backend = orchestrator._get_best_backend()
        assert backend == AIBackend.STANDALONE
    
    def test_process_query_with_ollama(self, orchestrator, mock_ollama_service):
        """Test query processing with Ollama backend."""
        mock_ollama_service.is_available.return_value = True
        
        response = orchestrator.process_query("Test query")
        
        assert isinstance(response, AIResponse)
        assert response.response == "Test response from Ollama"
        assert response.backend_used == AIBackend.OLLAMA
        assert response.fallback_used is False
        assert response.confidence > 0.5
        
        mock_ollama_service.generate_response.assert_called_once()
    
    def test_process_query_with_standalone_fallback(self, orchestrator, mock_ollama_service, mock_standalone_service):
        """Test query processing falls back to standalone when Ollama fails."""
        mock_ollama_service.is_available.return_value = False
        
        response = orchestrator.process_query("Test query")
        
        assert isinstance(response, AIResponse)
        assert response.response == "Test response from standalone"
        assert response.backend_used == AIBackend.STANDALONE
        assert response.fallback_used is True
        
        mock_standalone_service.generate_response.assert_called_once_with("Test query", {})
    
    def test_process_query_with_error_fallback(self, orchestrator, mock_ollama_service, mock_standalone_service):
        """Test query processing with error fallback."""
        mock_ollama_service.is_available.return_value = True
        mock_ollama_service.generate_response.side_effect = Exception("Ollama error")
        mock_standalone_service.generate_response.return_value = {"response": "Fallback response"}
        
        response = orchestrator.process_query("Test query")
        
        assert isinstance(response, AIResponse)
        assert response.response == "Fallback response"
        assert response.backend_used == AIBackend.STANDALONE
        assert response.fallback_used is True
        assert "original_error" in response.metadata
    
    def test_process_query_complete_failure(self, orchestrator, mock_ollama_service, mock_standalone_service):
        """Test query processing when all backends fail."""
        mock_ollama_service.is_available.return_value = True
        mock_ollama_service.generate_response.side_effect = Exception("Ollama error")
        mock_standalone_service.generate_response.side_effect = Exception("Standalone error")
        
        response = orchestrator.process_query("Test query")
        
        assert isinstance(response, AIResponse)
        assert response.backend_used == AIBackend.FALLBACK
        assert response.fallback_used is True
        assert response.confidence == 0.1
        assert "technical difficulties" in response.response.lower()
    
    def test_multilingual_system_prompts(self, orchestrator):
        """Test language-specific system prompts."""
        en_prompt = orchestrator._get_system_prompt("en")
        de_prompt = orchestrator._get_system_prompt("de")
        ja_prompt = orchestrator._get_system_prompt("ja")
        
        assert "helpful AI assistant" in en_prompt
        assert "hilfreicher KI-Assistent" in de_prompt
        assert "有用なAIアシスタント" in ja_prompt
        
        # Test fallback to English for unsupported language
        unknown_prompt = orchestrator._get_system_prompt("fr")
        assert unknown_prompt == en_prompt
    
    def test_get_available_models(self, orchestrator, mock_ollama_service):
        """Test getting available models."""
        mock_ollama_service.is_available.return_value = True
        mock_ollama_service.list_models.return_value = ["llama3.2:3b", "llama3.2:1b"]
        
        models = orchestrator.get_available_models()
        
        assert "llama3.2:3b" in models
        assert "llama3.2:1b" in models
        assert "standalone" in models
    
    def test_switch_model(self, orchestrator, mock_model_manager):
        """Test model switching."""
        mock_model_manager.switch_model.return_value = True
        
        result = orchestrator.switch_model("llama3.2:1b")
        
        assert result is True
        mock_model_manager.switch_model.assert_called_once_with("llama3.2:1b")
    
    def test_get_system_status(self, orchestrator, mock_ollama_service):
        """Test getting system status."""
        mock_ollama_service.is_available.return_value = True
        
        status = orchestrator.get_system_status()
        
        assert isinstance(status, SystemStatus)
        assert status.primary_backend == AIBackend.OLLAMA
        assert AIBackend.OLLAMA in status.available_backends
        assert AIBackend.STANDALONE in status.available_backends
        assert status.health_status == "healthy"
        assert len(status.active_models) > 0
    
    def test_set_fallback_mode(self, orchestrator):
        """Test setting fallback mode."""
        orchestrator.set_fallback_mode(False)
        assert orchestrator.fallback_enabled is False
        
        orchestrator.set_fallback_mode(True)
        assert orchestrator.fallback_enabled is True
    
    def test_set_preferred_backend(self, orchestrator):
        """Test setting preferred backend."""
        orchestrator.set_preferred_backend(AIBackend.STANDALONE)
        assert orchestrator.preferred_backend == AIBackend.STANDALONE
    
    def test_performance_metrics_tracking(self, orchestrator, mock_ollama_service):
        """Test performance metrics tracking."""
        mock_ollama_service.is_available.return_value = True
        
        # Process a query to generate metrics
        orchestrator.process_query("Test query")
        
        assert AIBackend.OLLAMA in orchestrator.performance_metrics
        metrics = orchestrator.performance_metrics[AIBackend.OLLAMA]
        assert metrics['total_requests'] == 1
        assert metrics['successful_requests'] == 1
        assert metrics['average_response_time'] > 0
    
    def test_model_preference_handling(self, orchestrator, mock_ollama_service):
        """Test handling of model preferences."""
        mock_ollama_service.is_available.return_value = True
        mock_ollama_service.list_models.return_value = ["llama3.2:3b", "llama3.2:1b"]
        
        response = orchestrator.process_query("Test query", model_preference="llama3.2:1b")
        
        # Verify the preferred model was used
        mock_ollama_service.generate_response.assert_called_once()
        call_args = mock_ollama_service.generate_response.call_args
        assert call_args[1]['model'] == "llama3.2:1b"
    
    def test_model_fallback_when_preferred_unavailable(self, orchestrator, mock_ollama_service):
        """Test model fallback when preferred model is unavailable."""
        mock_ollama_service.is_available.return_value = True
        mock_ollama_service.list_models.return_value = ["llama3.2:1b"]  # Only 1b available
        
        response = orchestrator.process_query("Test query", model_preference="llama3.2:3b")
        
        # Should fall back to available model
        mock_ollama_service.generate_response.assert_called_once()
        call_args = mock_ollama_service.generate_response.call_args
        assert call_args[1]['model'] == "llama3.2:1b"
    
    def test_context_handling(self, orchestrator, mock_ollama_service):
        """Test context handling in queries."""
        mock_ollama_service.is_available.return_value = True
        
        context = {"user_id": "123", "session_id": "abc"}
        response = orchestrator.process_query("Test query", context=context)
        
        assert response.context_maintained is True
        assert isinstance(response.metadata, dict)
    
    def test_language_specific_processing(self, orchestrator, mock_ollama_service):
        """Test language-specific query processing."""
        mock_ollama_service.is_available.return_value = True
        
        # Test German query
        response = orchestrator.process_query("Hallo", language="de")
        
        assert response.language == "de"
        mock_ollama_service.generate_response.assert_called_once()
        
        # Verify German system prompt was used
        call_args = mock_ollama_service.generate_response.call_args
        system_prompt = call_args[1]['system_prompt']
        assert "hilfreicher KI-Assistent" in system_prompt
    
    def test_cleanup(self, orchestrator):
        """Test orchestrator cleanup."""
        orchestrator.cleanup()
        # Should not raise any exceptions
        assert True


class TestAIResponse:
    """Test cases for AIResponse dataclass."""
    
    def test_ai_response_creation(self):
        """Test AIResponse creation."""
        response = AIResponse(
            response="Test response",
            confidence=0.8,
            query_type="general",
            language="en",
            model_used="llama3.2:3b",
            processing_time=1.5,
            fallback_used=False,
            context_maintained=True,
            backend_used=AIBackend.OLLAMA,
            metadata={"test": "data"}
        )
        
        assert response.response == "Test response"
        assert response.confidence == 0.8
        assert response.backend_used == AIBackend.OLLAMA
        assert response.metadata["test"] == "data"


class TestSystemStatus:
    """Test cases for SystemStatus dataclass."""
    
    def test_system_status_creation(self):
        """Test SystemStatus creation."""
        status = SystemStatus(
            primary_backend=AIBackend.OLLAMA,
            available_backends=[AIBackend.OLLAMA, AIBackend.STANDALONE],
            active_models=["llama3.2:3b"],
            health_status="healthy",
            performance_metrics={"avg_time": 1.2},
            last_updated=time.time()
        )
        
        assert status.primary_backend == AIBackend.OLLAMA
        assert len(status.available_backends) == 2
        assert status.health_status == "healthy"
        assert "avg_time" in status.performance_metrics


if __name__ == "__main__":
    pytest.main([__file__])