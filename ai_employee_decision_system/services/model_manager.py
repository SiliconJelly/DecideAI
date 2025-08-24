"""
Model management system for Ollama models.
"""
import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from ai_employee_decision_system.core import get_logger
from ai_employee_decision_system.services.ollama_service import OllamaService, ModelInfo

logger = get_logger(__name__)


@dataclass
class ModelDownloadProgress:
    """Progress information for model downloads."""
    model_name: str
    status: str  # "downloading", "completed", "failed", "cancelled"
    progress_percent: float
    downloaded_bytes: int
    total_bytes: int
    speed_mbps: float
    eta_seconds: Optional[int]
    error_message: Optional[str] = None


@dataclass
class ModelMetadata:
    """Metadata for a model."""
    name: str
    size_gb: float
    description: str
    languages: List[str]
    capabilities: List[str]
    recommended_use_cases: List[str]
    performance_tier: str  # "fast", "balanced", "quality"
    memory_requirements_gb: float
    last_updated: str
    download_url: Optional[str] = None


class ModelManager:
    """Manages Ollama models including downloading, updating, and metadata."""
    
    # Predefined model catalog with metadata
    MODEL_CATALOG = {
        "llama2:7b-chat": ModelMetadata(
            name="llama2:7b-chat",
            size_gb=3.8,
            description="Llama 2 7B Chat - Good balance of speed and quality with multilingual capabilities",
            languages=["en", "de", "fr", "es", "it", "pt"],
            capabilities=["chat", "completion", "instruction-following", "multilingual"],
            recommended_use_cases=["general chat", "Q&A", "employee assistance", "multilingual support"],
            performance_tier="balanced",
            memory_requirements_gb=8.0,
            last_updated="2023-07-18"
        ),
        "mistral:7b": ModelMetadata(
            name="mistral:7b",
            size_gb=4.1,
            description="Mistral 7B - High quality responses",
            languages=["en", "fr", "de", "es", "it"],
            capabilities=["chat", "completion", "reasoning", "code"],
            recommended_use_cases=["complex analysis", "professional writing", "code assistance"],
            performance_tier="quality",
            memory_requirements_gb=8.0,
            last_updated="2023-09-27"
        ),
        "codellama:7b": ModelMetadata(
            name="codellama:7b",
            size_gb=3.8,
            description="Code Llama 7B - Specialized for code generation",
            languages=["en"],
            capabilities=["code", "completion", "debugging", "explanation"],
            recommended_use_cases=["code generation", "technical documentation", "debugging"],
            performance_tier="balanced",
            memory_requirements_gb=8.0,
            last_updated="2023-08-24"
        )
    }
    
    def __init__(self, ollama_service: Optional[OllamaService] = None):
        """Initialize model manager.
        
        Args:
            ollama_service: Optional OllamaService instance
        """
        self.ollama_service = ollama_service or OllamaService()
        self.download_progress: Dict[str, ModelDownloadProgress] = {}
        self.download_callbacks: Dict[str, List[Callable]] = {}
        self._download_threads: Dict[str, threading.Thread] = {}
        self._cancel_flags: Dict[str, threading.Event] = {}
        
        logger.info("Model manager initialized")
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models with metadata.
        
        Returns:
            List of ModelInfo objects
        """
        if not self.ollama_service.is_available():
            logger.warning("Ollama service not available")
            return []
        
        installed_models = self.ollama_service.list_models()
        model_infos = []
        
        for model_name in installed_models:
            metadata = self.MODEL_CATALOG.get(model_name)
            if metadata:
                model_info = ModelInfo(
                    name=model_name,
                    size=f"{metadata.size_gb:.1f}GB",
                    description=metadata.description,
                    languages=metadata.languages,
                    capabilities=metadata.capabilities,
                    status="available",
                    performance_metrics=self._get_performance_metrics(model_name)
                )
            else:
                # Fallback for unknown models
                model_info = ModelInfo(
                    name=model_name,
                    size="Unknown",
                    description="Custom or unknown model",
                    languages=["en"],
                    capabilities=["chat", "completion"],
                    status="available",
                    performance_metrics={}
                )
            
            model_infos.append(model_info)
        
        return model_infos
    
    def get_model_catalog(self) -> Dict[str, ModelMetadata]:
        """Get the full model catalog.
        
        Returns:
            Dictionary of model metadata
        """
        return self.MODEL_CATALOG.copy()
    
    def get_recommended_models(self, 
                             use_case: str = "general",
                             language: str = "en",
                             performance_tier: str = "balanced") -> List[ModelMetadata]:
        """Get recommended models based on criteria.
        
        Args:
            use_case: Use case (e.g., "chat", "multilingual", "code")
            language: Required language support
            performance_tier: Performance preference ("fast", "balanced", "quality")
            
        Returns:
            List of recommended models
        """
        recommendations = []
        
        for model_name, metadata in self.MODEL_CATALOG.items():
            # Check language support
            if language not in metadata.languages:
                continue
            
            # Check use case alignment
            use_case_match = any(
                use_case.lower() in capability.lower() or 
                use_case.lower() in use_case_item.lower()
                for capability in metadata.capabilities
                for use_case_item in metadata.recommended_use_cases
            )
            
            if not use_case_match and use_case != "general":
                continue
            
            # Prefer matching performance tier, but include others
            score = 1.0
            if metadata.performance_tier == performance_tier:
                score += 0.5
            
            recommendations.append((metadata, score))
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [metadata for metadata, _ in recommendations[:3]]
    
    def download_model(self, 
                      model_name: str, 
                      progress_callback: Optional[Callable[[ModelDownloadProgress], None]] = None) -> bool:
        """Download a model asynchronously.
        
        Args:
            model_name: Name of the model to download
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if download started successfully, False otherwise
        """
        if not self.ollama_service.is_available():
            logger.error("Ollama service not available")
            return False
        
        if model_name in self._download_threads and self._download_threads[model_name].is_alive():
            logger.warning(f"Model {model_name} is already being downloaded")
            return False
        
        # Initialize progress tracking
        self.download_progress[model_name] = ModelDownloadProgress(
            model_name=model_name,
            status="downloading",
            progress_percent=0.0,
            downloaded_bytes=0,
            total_bytes=0,
            speed_mbps=0.0,
            eta_seconds=None
        )
        
        # Set up callbacks
        if progress_callback:
            if model_name not in self.download_callbacks:
                self.download_callbacks[model_name] = []
            self.download_callbacks[model_name].append(progress_callback)
        
        # Create cancel flag
        self._cancel_flags[model_name] = threading.Event()
        
        # Start download thread
        download_thread = threading.Thread(
            target=self._download_model_thread,
            args=(model_name,),
            daemon=True
        )
        self._download_threads[model_name] = download_thread
        download_thread.start()
        
        logger.info(f"Started downloading model: {model_name}")
        return True
    
    def _download_model_thread(self, model_name: str) -> None:
        """Download model in a separate thread.
        
        Args:
            model_name: Name of the model to download
        """
        try:
            start_time = time.time()
            
            # Use Ollama's pull method with streaming
            success = self.ollama_service.pull_model(model_name, stream=True)
            
            if success and not self._cancel_flags[model_name].is_set():
                # Update progress to completed
                elapsed_time = time.time() - start_time
                self.download_progress[model_name].status = "completed"
                self.download_progress[model_name].progress_percent = 100.0
                
                logger.info(f"Model {model_name} downloaded successfully in {elapsed_time:.1f}s")
                
                # Notify callbacks
                self._notify_progress_callbacks(model_name)
                
            elif self._cancel_flags[model_name].is_set():
                self.download_progress[model_name].status = "cancelled"
                logger.info(f"Model {model_name} download cancelled")
                
            else:
                self.download_progress[model_name].status = "failed"
                self.download_progress[model_name].error_message = "Download failed"
                logger.error(f"Failed to download model: {model_name}")
                
        except Exception as e:
            self.download_progress[model_name].status = "failed"
            self.download_progress[model_name].error_message = str(e)
            logger.error(f"Error downloading model {model_name}: {e}")
        
        finally:
            # Notify callbacks of final status
            self._notify_progress_callbacks(model_name)
            
            # Cleanup
            if model_name in self._cancel_flags:
                del self._cancel_flags[model_name]
    
    def cancel_download(self, model_name: str) -> bool:
        """Cancel an ongoing download.
        
        Args:
            model_name: Name of the model to cancel
            
        Returns:
            True if cancellation was initiated, False otherwise
        """
        if model_name not in self._cancel_flags:
            logger.warning(f"No active download found for model: {model_name}")
            return False
        
        self._cancel_flags[model_name].set()
        logger.info(f"Cancellation requested for model: {model_name}")
        return True
    
    def get_download_progress(self, model_name: str) -> Optional[ModelDownloadProgress]:
        """Get download progress for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelDownloadProgress object or None if not found
        """
        return self.download_progress.get(model_name)
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ollama_service.is_available():
            logger.error("Ollama service not available")
            return False
        
        success = self.ollama_service.delete_model(model_name)
        if success:
            logger.info(f"Model {model_name} deleted successfully")
            
            # Clean up any progress tracking
            if model_name in self.download_progress:
                del self.download_progress[model_name]
            if model_name in self.download_callbacks:
                del self.download_callbacks[model_name]
        
        return success
    
    def update_model(self, model_name: str) -> bool:
        """Update a model to the latest version.
        
        Args:
            model_name: Name of the model to update
            
        Returns:
            True if update started successfully, False otherwise
        """
        logger.info(f"Updating model: {model_name}")
        return self.download_model(model_name)  # Re-download to get latest version
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary or None if not found
        """
        if not self.ollama_service.is_available():
            return None
        
        # Get info from Ollama
        ollama_info = self.ollama_service.get_model_info(model_name)
        
        # Combine with catalog metadata
        metadata = self.MODEL_CATALOG.get(model_name)
        
        result = {}
        if ollama_info:
            result.update(ollama_info)
        
        if metadata:
            result.update({
                "metadata": asdict(metadata),
                "performance_metrics": self._get_performance_metrics(model_name)
            })
        
        return result if result else None
    
    def _get_performance_metrics(self, model_name: str) -> Dict[str, float]:
        """Get performance metrics for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Performance metrics dictionary
        """
        # This would typically come from benchmarking or monitoring
        # For now, return estimated values based on model metadata
        metadata = self.MODEL_CATALOG.get(model_name)
        if not metadata:
            return {}
        
        # Estimated metrics based on model tier
        if metadata.performance_tier == "fast":
            return {
                "tokens_per_second": 35.0,
                "latency_ms": 150,
                "memory_usage_gb": metadata.memory_requirements_gb * 0.8
            }
        elif metadata.performance_tier == "balanced":
            return {
                "tokens_per_second": 25.0,
                "latency_ms": 250,
                "memory_usage_gb": metadata.memory_requirements_gb * 0.9
            }
        else:  # quality
            return {
                "tokens_per_second": 15.0,
                "latency_ms": 400,
                "memory_usage_gb": metadata.memory_requirements_gb
            }
    
    def _notify_progress_callbacks(self, model_name: str) -> None:
        """Notify all progress callbacks for a model.
        
        Args:
            model_name: Name of the model
        """
        if model_name not in self.download_callbacks:
            return
        
        progress = self.download_progress.get(model_name)
        if not progress:
            return
        
        for callback in self.download_callbacks[model_name]:
            try:
                callback(progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status including model information.
        
        Returns:
            System status dictionary
        """
        status = {
            "ollama_available": self.ollama_service.is_available(),
            "installed_models": len(self.get_available_models()),
            "active_downloads": len([
                p for p in self.download_progress.values() 
                if p.status == "downloading"
            ]),
            "catalog_size": len(self.MODEL_CATALOG),
            "timestamp": time.time()
        }
        
        if status["ollama_available"]:
            status["available_models"] = [
                {
                    "name": model.name,
                    "size": model.size,
                    "languages": model.languages,
                    "status": model.status
                }
                for model in self.get_available_models()
            ]
        
        return status
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model.
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            # Check if model is available
            available_models = [model.name for model in self.get_available_models()]
            
            if model_name not in available_models:
                logger.warning(f"Model {model_name} not available. Available models: {available_models}")
                
                # Try to download the model if it's in our catalog
                if model_name in self.MODEL_CATALOG:
                    logger.info(f"Attempting to download model {model_name}")
                    success = self.download_model(model_name)
                    if not success:
                        logger.error(f"Failed to download model {model_name}")
                        return False
                else:
                    logger.error(f"Model {model_name} not found in catalog")
                    return False
            
            # Test the model by making a simple query
            try:
                test_response = self.ollama_service.generate_response(
                    prompt="Hello",
                    model=model_name,
                    system_prompt="You are a helpful assistant."
                )
                
                if test_response:
                    logger.info(f"Successfully switched to model {model_name}")
                    return True
                else:
                    logger.error(f"Model {model_name} failed test query")
                    return False
                    
            except Exception as e:
                logger.error(f"Error testing model {model_name}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching to model {model_name}: {e}")
            return False
    
    def get_recommended_model(self, use_case: str = "general") -> Optional[str]:
        """Get recommended model for a specific use case.
        
        Args:
            use_case: The use case ("general", "fast", "quality", "multilingual")
            
        Returns:
            Recommended model name or None
        """
        available_models = [model.name for model in self.get_available_models()]
        
        if not available_models:
            return None
        
        # Filter models based on use case
        if use_case == "fast":
            # Prefer fast models
            for model_name in available_models:
                metadata = self.MODEL_CATALOG.get(model_name)
                if metadata and metadata.performance_tier == "fast":
                    return model_name
        
        elif use_case == "quality":
            # Prefer quality models
            for model_name in available_models:
                metadata = self.MODEL_CATALOG.get(model_name)
                if metadata and metadata.performance_tier == "quality":
                    return model_name
        
        elif use_case == "multilingual":
            # Prefer models with multiple language support
            best_model = None
            max_languages = 0
            
            for model_name in available_models:
                metadata = self.MODEL_CATALOG.get(model_name)
                if metadata and len(metadata.languages) > max_languages:
                    max_languages = len(metadata.languages)
                    best_model = model_name
            
            if best_model:
                return best_model
        
        # Default: return first available model
        return available_models[0] if available_models else None
    
    def cleanup(self) -> None:
        """Clean up resources and cancel any ongoing downloads."""
        logger.info("Cleaning up model manager")
        
        # Cancel all active downloads
        for model_name in list(self._cancel_flags.keys()):
            self.cancel_download(model_name)
        
        # Wait for threads to finish (with timeout)
        for thread in self._download_threads.values():
            if thread.is_alive():
                thread.join(timeout=5.0)
        
        # Clear all tracking data
        self.download_progress.clear()
        self.download_callbacks.clear()
        self._download_threads.clear()
        self._cancel_flags.clear()