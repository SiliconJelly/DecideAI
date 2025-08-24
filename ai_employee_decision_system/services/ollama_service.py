"""
Ollama service for local LLM integration.
"""
import json
import time
import requests
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass
from urllib.parse import urljoin

from ai_employee_decision_system.core import get_logger

logger = get_logger(__name__)


@dataclass
class ModelInfo:
    """Information about an Ollama model."""
    name: str
    size: str
    description: str
    languages: List[str]
    capabilities: List[str]
    status: str  # "available", "downloading", "not_installed"
    performance_metrics: Dict[str, float]


@dataclass
class OllamaResponse:
    """Response from Ollama API."""
    response: str
    model: str
    created_at: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


class OllamaService:
    """Service for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama service.
        
        Args:
            base_url: Base URL for Ollama API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        self.available = False
        self._check_availability()
        
        logger.info(f"Ollama service initialized with base URL: {self.base_url}")
    
    def _check_availability(self) -> None:
        """Check if Ollama service is available."""
        try:
            response = self.session.head(self.base_url)
            self.available = response.status_code == 200
            if self.available:
                logger.info("Ollama service is available")
            else:
                logger.warning(f"Ollama service returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.available = False
            logger.warning(f"Ollama service is not available: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        if not self.available:
            self._check_availability()
        return self.available
    
    def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names
        """
        if not self.is_available():
            logger.error("Ollama service is not available")
            return []
        
        try:
            url = urljoin(self.base_url, "/api/tags")
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            logger.info(f"Found {len(models)} models: {models}")
            return models
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse model list response: {e}")
            return []
    
    def pull_model(self, model_name: str, stream: bool = False) -> bool:
        """Pull/download a model.
        
        Args:
            model_name: Name of the model to pull
            stream: Whether to stream the download progress
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("Ollama service is not available")
            return False
        
        try:
            url = urljoin(self.base_url, "/api/pull")
            payload = {"name": model_name, "stream": stream}
            
            logger.info(f"Pulling model: {model_name}")
            response = self.session.post(url, json=payload, stream=stream)
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("status"):
                                logger.info(f"Pull progress: {data['status']}")
                            if data.get("error"):
                                logger.error(f"Pull error: {data['error']}")
                                return False
                        except json.JSONDecodeError:
                            continue
            else:
                data = response.json()
                if data.get("error"):
                    logger.error(f"Failed to pull model: {data['error']}")
                    return False
            
            logger.info(f"Successfully pulled model: {model_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def generate_response(
        self, 
        prompt: str, 
        model: str = "llama2:7b-chat",
        system_prompt: Optional[str] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[OllamaResponse]:
        """Generate a response using Ollama.
        
        Args:
            prompt: The prompt to send to the model
            model: Model name to use
            system_prompt: Optional system prompt
            stream: Whether to stream the response
            options: Additional options for the model
            
        Returns:
            OllamaResponse object or None if failed
        """
        if not self.is_available():
            logger.error("Ollama service is not available")
            return None
        
        try:
            url = urljoin(self.base_url, "/api/generate")
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if options:
                payload["options"] = options
            
            logger.debug(f"Generating response with model {model}")
            start_time = time.time()
            
            response = self.session.post(url, json=payload, stream=stream)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("response"):
                                full_response += data["response"]
                            if data.get("done", False):
                                processing_time = time.time() - start_time
                                logger.info(f"Response generated in {processing_time:.2f}s")
                                return OllamaResponse(
                                    response=full_response,
                                    model=model,
                                    created_at=data.get("created_at", ""),
                                    done=True,
                                    context=data.get("context"),
                                    total_duration=data.get("total_duration"),
                                    load_duration=data.get("load_duration"),
                                    prompt_eval_count=data.get("prompt_eval_count"),
                                    prompt_eval_duration=data.get("prompt_eval_duration"),
                                    eval_count=data.get("eval_count"),
                                    eval_duration=data.get("eval_duration")
                                )
                        except json.JSONDecodeError:
                            continue
            else:
                # Handle non-streaming response
                data = response.json()
                processing_time = time.time() - start_time
                logger.info(f"Response generated in {processing_time:.2f}s")
                
                return OllamaResponse(
                    response=data.get("response", ""),
                    model=model,
                    created_at=data.get("created_at", ""),
                    done=data.get("done", True),
                    context=data.get("context"),
                    total_duration=data.get("total_duration"),
                    load_duration=data.get("load_duration"),
                    prompt_eval_count=data.get("prompt_eval_count"),
                    prompt_eval_duration=data.get("prompt_eval_duration"),
                    eval_count=data.get("eval_count"),
                    eval_duration=data.get("eval_duration")
                )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate response: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse response: {e}")
            return None
        
        return None
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama2:7b-chat",
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[OllamaResponse]:
        """Generate a chat completion using Ollama.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            stream: Whether to stream the response
            options: Additional options for the model
            
        Returns:
            OllamaResponse object or None if failed
        """
        if not self.is_available():
            logger.error("Ollama service is not available")
            return None
        
        try:
            url = urljoin(self.base_url, "/api/chat")
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            if options:
                payload["options"] = options
            
            logger.debug(f"Chat completion with model {model}")
            start_time = time.time()
            
            response = self.session.post(url, json=payload, stream=stream)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("message", {}).get("content"):
                                full_response += data["message"]["content"]
                            if data.get("done", False):
                                processing_time = time.time() - start_time
                                logger.info(f"Chat completion generated in {processing_time:.2f}s")
                                return OllamaResponse(
                                    response=full_response,
                                    model=model,
                                    created_at=data.get("created_at", ""),
                                    done=True,
                                    total_duration=data.get("total_duration"),
                                    load_duration=data.get("load_duration"),
                                    prompt_eval_count=data.get("prompt_eval_count"),
                                    prompt_eval_duration=data.get("prompt_eval_duration"),
                                    eval_count=data.get("eval_count"),
                                    eval_duration=data.get("eval_duration")
                                )
                        except json.JSONDecodeError:
                            continue
            else:
                # Handle non-streaming response
                data = response.json()
                processing_time = time.time() - start_time
                logger.info(f"Chat completion generated in {processing_time:.2f}s")
                
                message_content = data.get("message", {}).get("content", "")
                return OllamaResponse(
                    response=message_content,
                    model=model,
                    created_at=data.get("created_at", ""),
                    done=data.get("done", True),
                    total_duration=data.get("total_duration"),
                    load_duration=data.get("load_duration"),
                    prompt_eval_count=data.get("prompt_eval_count"),
                    prompt_eval_duration=data.get("prompt_eval_duration"),
                    eval_count=data.get("eval_count"),
                    eval_duration=data.get("eval_duration")
                )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate chat completion: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse chat completion response: {e}")
            return None
        
        return None
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary or None if failed
        """
        if not self.is_available():
            logger.error("Ollama service is not available")
            return None
        
        try:
            url = urljoin(self.base_url, "/api/show")
            payload = {"name": model_name}
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            return None
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("Ollama service is not available")
            return False
        
        try:
            url = urljoin(self.base_url, "/api/delete")
            payload = {"name": model_name}
            
            response = self.session.delete(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Successfully deleted model: {model_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information.
        
        Returns:
            System status dictionary
        """
        status = {
            "available": self.is_available(),
            "base_url": self.base_url,
            "models": [],
            "timestamp": time.time()
        }
        
        if status["available"]:
            status["models"] = self.list_models()
        
        return status