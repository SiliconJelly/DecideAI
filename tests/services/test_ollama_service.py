"""
Tests for Ollama service.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import requests

from ai_employee_decision_system.services.ollama_service import (
    OllamaService, 
    OllamaResponse, 
    ModelInfo
)


class TestOllamaService:
    """Test cases for OllamaService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('ai_employee_decision_system.services.ollama_service.requests.Session'):
            self.service = OllamaService()
    
    def test_init_default_url(self):
        """Test initialization with default URL."""
        with patch('ai_employee_decision_system.services.ollama_service.requests.Session'):
            service = OllamaService()
            assert service.base_url == "http://localhost:11434"
    
    def test_init_custom_url(self):
        """Test initialization with custom URL."""
        with patch('ai_employee_decision_system.services.ollama_service.requests.Session'):
            service = OllamaService("http://custom:8080/")
            assert service.base_url == "http://custom:8080"
    
    @patch('ai_employee_decision_system.services.ollama_service.requests.Session')
    def test_check_availability_success(self, mock_session_class):
        """Test successful availability check."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.head.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        service = OllamaService()
        assert service.available is True
    
    @patch('ai_employee_decision_system.services.ollama_service.requests.Session')
    def test_check_availability_failure(self, mock_session_class):
        """Test failed availability check."""
        mock_session = Mock()
        mock_session.head.side_effect = requests.exceptions.RequestException("Connection failed")
        mock_session_class.return_value = mock_session
        
        service = OllamaService()
        assert service.available is False
    
    def test_is_available(self):
        """Test is_available method."""
        self.service.available = True
        assert self.service.is_available() is True
        
        self.service.available = False
        with patch.object(self.service, '_check_availability'):
            self.service.is_available()
    
    def test_list_models_success(self):
        """Test successful model listing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:7b-chat"},
                {"name": "mistral:7b"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        self.service.session.get.return_value = mock_response
        self.service.available = True
        
        models = self.service.list_models()
        assert models == ["llama2:7b-chat", "mistral:7b"]
    
    def test_list_models_service_unavailable(self):
        """Test model listing when service is unavailable."""
        self.service.available = False
        models = self.service.list_models()
        assert models == []
    
    def test_list_models_request_failure(self):
        """Test model listing with request failure."""
        self.service.session.get.side_effect = requests.exceptions.RequestException("Request failed")
        self.service.available = True
        
        models = self.service.list_models()
        assert models == []
    
    def test_pull_model_success(self):
        """Test successful model pulling."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        result = self.service.pull_model("llama2:7b-chat")
        assert result is True
    
    def test_pull_model_service_unavailable(self):
        """Test model pulling when service is unavailable."""
        self.service.available = False
        result = self.service.pull_model("llama2:7b-chat")
        assert result is False
    
    def test_pull_model_with_error(self):
        """Test model pulling with error response."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Model not found"}
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        result = self.service.pull_model("nonexistent:model")
        assert result is False
    
    def test_generate_response_success(self):
        """Test successful response generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Hello, I can help with employee management!",
            "model": "llama2:7b-chat",
            "created_at": "2025-07-21T10:00:00Z",
            "done": True,
            "total_duration": 1000000,
            "eval_count": 50
        }
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        result = self.service.generate_response("Hello, can you help with employee management?")
        
        assert result is not None
        assert isinstance(result, OllamaResponse)
        assert result.response == "Hello, I can help with employee management!"
        assert result.model == "llama2:7b-chat"
        assert result.done is True
    
    def test_generate_response_service_unavailable(self):
        """Test response generation when service is unavailable."""
        self.service.available = False
        result = self.service.generate_response("Hello")
        assert result is None
    
    def test_generate_response_with_system_prompt(self):
        """Test response generation with system prompt."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "I am an HR assistant.",
            "model": "llama2:7b-chat",
            "created_at": "2025-07-21T10:00:00Z",
            "done": True
        }
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        result = self.service.generate_response(
            "Who are you?",
            system_prompt="You are an HR assistant."
        )
        
        assert result is not None
        assert result.response == "I am an HR assistant."
    
    def test_chat_completion_success(self):
        """Test successful chat completion."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": {
                "content": "I can help you with employee management tasks."
            },
            "model": "llama2:7b-chat",
            "created_at": "2025-07-21T10:00:00Z",
            "done": True
        }
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        messages = [
            {"role": "user", "content": "Can you help with HR tasks?"}
        ]
        result = self.service.chat_completion(messages)
        
        assert result is not None
        assert isinstance(result, OllamaResponse)
        assert result.response == "I can help you with employee management tasks."
    
    def test_chat_completion_service_unavailable(self):
        """Test chat completion when service is unavailable."""
        self.service.available = False
        messages = [{"role": "user", "content": "Hello"}]
        result = self.service.chat_completion(messages)
        assert result is None
    
    def test_get_model_info_success(self):
        """Test successful model info retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "modelfile": "FROM llama2:7b-chat",
            "parameters": "temperature 0.7",
            "template": "{{ .Prompt }}"
        }
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        result = self.service.get_model_info("llama2:7b-chat")
        
        assert result is not None
        assert "modelfile" in result
        assert result["modelfile"] == "FROM llama2:7b-chat"
    
    def test_get_model_info_service_unavailable(self):
        """Test model info retrieval when service is unavailable."""
        self.service.available = False
        result = self.service.get_model_info("llama2:7b-chat")
        assert result is None
    
    def test_delete_model_success(self):
        """Test successful model deletion."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        self.service.session.delete.return_value = mock_response
        self.service.available = True
        
        result = self.service.delete_model("old-model:latest")
        assert result is True
    
    def test_delete_model_service_unavailable(self):
        """Test model deletion when service is unavailable."""
        self.service.available = False
        result = self.service.delete_model("old-model:latest")
        assert result is False
    
    def test_get_system_status_available(self):
        """Test system status when service is available."""
        self.service.available = True
        with patch.object(self.service, 'list_models', return_value=["llama2:7b-chat"]):
            status = self.service.get_system_status()
        
        assert status["available"] is True
        assert status["base_url"] == self.service.base_url
        assert status["models"] == ["llama2:7b-chat"]
        assert "timestamp" in status
    
    def test_get_system_status_unavailable(self):
        """Test system status when service is unavailable."""
        self.service.available = False
        status = self.service.get_system_status()
        
        assert status["available"] is False
        assert status["models"] == []
    
    def test_generate_response_streaming(self):
        """Test streaming response generation."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello", "done": false}',
            b'{"response": " there!", "done": false}',
            b'{"response": "", "done": true, "created_at": "2025-07-21T10:00:00Z"}'
        ]
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        result = self.service.generate_response("Hello", stream=True)
        
        assert result is not None
        assert result.response == "Hello there!"
        assert result.done is True
    
    def test_chat_completion_streaming(self):
        """Test streaming chat completion."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'{"message": {"content": "I can"}, "done": false}',
            b'{"message": {"content": " help you"}, "done": false}',
            b'{"message": {"content": ""}, "done": true, "created_at": "2025-07-21T10:00:00Z"}'
        ]
        mock_response.raise_for_status.return_value = None
        self.service.session.post.return_value = mock_response
        self.service.available = True
        
        messages = [{"role": "user", "content": "Can you help?"}]
        result = self.service.chat_completion(messages, stream=True)
        
        assert result is not None
        assert result.response == "I can help you"
        assert result.done is True


class TestOllamaResponse:
    """Test cases for OllamaResponse dataclass."""
    
    def test_ollama_response_creation(self):
        """Test OllamaResponse creation."""
        response = OllamaResponse(
            response="Hello world",
            model="llama2:7b-chat",
            created_at="2025-07-21T10:00:00Z",
            done=True,
            total_duration=1000000,
            eval_count=50
        )
        
        assert response.response == "Hello world"
        assert response.model == "llama2:7b-chat"
        assert response.done is True
        assert response.total_duration == 1000000
        assert response.eval_count == 50


class TestModelInfo:
    """Test cases for ModelInfo dataclass."""
    
    def test_model_info_creation(self):
        """Test ModelInfo creation."""
        model_info = ModelInfo(
            name="llama2:7b-chat",
            size="3.8GB",
            description="Llama 2 7B Chat model",
            languages=["en", "de", "fr"],
            capabilities=["chat", "completion"],
            status="available",
            performance_metrics={"tokens_per_second": 25.5}
        )
        
        assert model_info.name == "llama2:7b-chat"
        assert model_info.size == "3.8GB"
        assert "en" in model_info.languages
        assert "chat" in model_info.capabilities
        assert model_info.status == "available"
        assert model_info.performance_metrics["tokens_per_second"] == 25.5