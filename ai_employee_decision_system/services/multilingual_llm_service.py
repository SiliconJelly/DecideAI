"""
Multilingual LLM service for the AI Employee Decision System.

This service integrates language detection, cultural context, and model selection
to provide high-quality multilingual responses.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple

from ai_employee_decision_system.services.ollama_service import OllamaService
from ai_employee_decision_system.services.model_manager import ModelManager
from ai_employee_decision_system.services.language_service import (
    LanguageService, SupportedLanguage
)

logger = logging.getLogger(__name__)


class MultilingualLLMService:
    """
    Multilingual LLM service that integrates language detection, cultural context,
    and model selection for high-quality multilingual responses.
    """
    
    def __init__(
        self,
        ollama_service: Optional[OllamaService] = None,
        model_manager: Optional[ModelManager] = None,
        language_service: Optional[LanguageService] = None
    ):
        """
        Initialize the multilingual LLM service.
        
        Args:
            ollama_service: Optional OllamaService instance
            model_manager: Optional ModelManager instance
            language_service: Optional LanguageService instance
        """
        self.ollama_service = ollama_service or OllamaService()
        self.model_manager = model_manager or ModelManager(self.ollama_service)
        self.language_service = language_service or LanguageService()
        
        # Cache for language-specific models
        self.language_model_cache: Dict[str, str] = {}
        
        # Performance tracking
        self.response_times: Dict[str, List[float]] = {}
        self.confidence_scores: Dict[str, List[float]] = {}
        
        logger.info("Multilingual LLM service initialized")
    
    def process_query(
        self,
        query: str,
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query with language detection and appropriate model selection.
        
        Args:
            query: The user query
            language: Optional language code (auto-detected if not provided)
            context: Optional context information
            model_name: Optional specific model to use
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        context = context or {}
        
        try:
            # Step 1: Detect language if not provided
            detected_language, language_code = self._detect_or_validate_language(query, language)
            
            # Step 2: Select appropriate model
            selected_model = self._select_model(query, language_code, model_name)
            
            # Step 3: Get cultural context and prepare system prompt
            system_prompt = self._prepare_system_prompt(language_code, context)
            
            # Step 4: Generate response
            ollama_response = self.ollama_service.generate_response(
                prompt=query,
                model=selected_model,
                system_prompt=system_prompt,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1
                }
            )
            
            if not ollama_response:
                return self._create_error_response(
                    "Failed to generate response", language_code
                )
            
            # Step 5: Format response according to cultural context
            raw_response = ollama_response.response
            formatted_response = self.language_service.format_response(
                raw_response, 
                SupportedLanguage(language_code),
                "general"
            )
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(
                query, raw_response, language_code, selected_model
            )
            
            # Track performance
            processing_time = time.time() - start_time
            self._track_performance(language_code, processing_time, confidence)
            
            return {
                "response": formatted_response,
                "confidence": confidence,
                "language": language_code,
                "detected_language": detected_language.value if detected_language else language_code,
                "model_used": selected_model,
                "processing_time": processing_time,
                "query_type": self._determine_query_type(query, language_code),
                "cultural_context_applied": True,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing multilingual query: {e}")
            processing_time = time.time() - start_time
            
            return {
                "response": self._get_error_message(language or "en", str(e)),
                "confidence": 0.3,
                "language": language or "en",
                "model_used": "error_fallback",
                "processing_time": processing_time,
                "query_type": "error",
                "cultural_context_applied": False,
                "status": "error",
                "error": str(e)
            }
    
    def _detect_or_validate_language(
        self, query: str, language: Optional[str]
    ) -> Tuple[Optional[SupportedLanguage], str]:
        """
        Detect language or validate provided language code.
        
        Args:
            query: The user query
            language: Optional language code
            
        Returns:
            Tuple of (detected language object, language code)
        """
        if language and self.language_service.is_supported_language(language):
            # Use provided language if supported
            return None, language
        
        # Detect language
        detection_result = self.language_service.detect_language(query)
        detected_language = detection_result.language
        
        logger.info(
            f"Language detected: {detected_language.value} "
            f"(confidence: {detection_result.confidence:.2f})"
        )
        
        return detected_language, detected_language.value
    
    def _select_model(
        self, query: str, language_code: str, preferred_model: Optional[str]
    ) -> str:
        """
        Select the best model for the query and language.
        
        Args:
            query: The user query
            language_code: Language code
            preferred_model: Optional preferred model
            
        Returns:
            Selected model name
        """
        # Use preferred model if specified
        if preferred_model:
            available_models = self.ollama_service.list_models()
            if preferred_model in available_models:
                return preferred_model
        
        # Check cache for previously successful model for this language
        if language_code in self.language_model_cache:
            cached_model = self.language_model_cache[language_code]
            available_models = self.ollama_service.list_models()
            if cached_model in available_models:
                return cached_model
        
        # Get recommended model from model manager
        recommended_models = self.model_manager.get_recommended_models(
            use_case="multilingual" if language_code != "en" else "general",
            language=language_code,
            performance_tier="balanced"
        )
        
        if recommended_models:
            # Use the first recommended model
            model_name = recommended_models[0].name
            # Cache this model for future queries in this language
            self.language_model_cache[language_code] = model_name
            return model_name
        
        # Fallback to default model
        available_models = self.ollama_service.list_models()
        if not available_models:
            raise ValueError("No models available")
        
        # Prefer Llama 3 models for multilingual support
        for model in available_models:
            if "llama3" in model.lower():
                return model
        
        # Last resort: use first available model
        return available_models[0]
    
    def _prepare_system_prompt(
        self, language_code: str, context: Dict[str, Any]
    ) -> str:
        """
        Prepare a culturally appropriate system prompt.
        
        Args:
            language_code: Language code
            context: Additional context
            
        Returns:
            System prompt
        """
        # Get cultural context
        try:
            language = SupportedLanguage(language_code)
            cultural_context = self.language_service.get_cultural_context(language)
            
            # Base prompts for different languages
            base_prompts = {
                "en": """You are a helpful AI assistant specializing in HR and employee management. 
Provide clear, concise, and professional responses. Focus on being accurate and helpful.""",
                
                "de": """Sie sind ein hilfreicher KI-Assistent, der sich auf Personalwesen und 
Mitarbeitermanagement spezialisiert hat. Geben Sie klare, präzise und professionelle 
Antworten. Achten Sie auf Genauigkeit und Hilfsbereitschaft.""",
                
                "ja": """あなたは人事と従業員管理を専門とする役立つAIアシスタントです。
明確で簡潔、そしてプロフェッショナルな回答を提供してください。
正確さと有用性に重点を置いてください。"""
            }
            
            # Get base prompt for language or fall back to English
            base_prompt = base_prompts.get(language_code, base_prompts["en"])
            
            # Add cultural context notes
            cultural_notes = "\n\n"
            if cultural_context.cultural_notes:
                if language_code == "en":
                    cultural_notes += "Communication style: Direct and solution-focused."
                elif language_code == "de":
                    cultural_notes += "Kommunikationsstil: Formal, gründlich und strukturiert."
                elif language_code == "ja":
                    cultural_notes += "コミュニケーションスタイル：丁寧で調和を重視します。"
            
            # Add context-specific information
            context_info = ""
            if context:
                if "employees" in context and context["employees"]:
                    if language_code == "en":
                        context_info += "\n\nYou have access to employee information."
                    elif language_code == "de":
                        context_info += "\n\nSie haben Zugriff auf Mitarbeiterinformationen."
                    elif language_code == "ja":
                        context_info += "\n\n従業員情報にアクセスできます。"
                
                if "skills" in context and context["skills"]:
                    if language_code == "en":
                        context_info += "\n\nYou can reference employee skills."
                    elif language_code == "de":
                        context_info += "\n\nSie können auf Mitarbeiterfähigkeiten verweisen."
                    elif language_code == "ja":
                        context_info += "\n\n従業員のスキルを参照できます。"
            
            return base_prompt + cultural_notes + context_info
            
        except ValueError:
            # Fallback to English prompt
            return """You are a helpful AI assistant specializing in HR and employee management. 
Provide clear, concise, and professional responses."""
    
    def _calculate_confidence(
        self, query: str, response: str, language_code: str, model_name: str
    ) -> float:
        """
        Calculate confidence score for the response.
        
        Args:
            query: Original query
            response: Generated response
            language_code: Language code
            model_name: Model used
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        confidence = 0.7
        
        # Adjust based on response length (too short or too long responses may indicate issues)
        response_length = len(response)
        if response_length < 20:
            confidence -= 0.2
        elif 50 <= response_length <= 1000:
            confidence += 0.1
        elif response_length > 2000:
            confidence -= 0.1
        
        # Adjust based on model
        if "llama3" in model_name.lower():
            confidence += 0.1
        
        # Adjust based on language match
        try:
            detected_language = self.language_service.detect_language(response)
            if detected_language.language.value == language_code:
                confidence += 0.1
            else:
                confidence -= 0.2
        except:
            pass
        
        # Ensure confidence is within bounds
        return max(0.1, min(confidence, 0.95))
    
    def _determine_query_type(self, query: str, language_code: str) -> str:
        """
        Determine the type of query.
        
        Args:
            query: The user query
            language_code: Language code
            
        Returns:
            Query type string
        """
        query_lower = query.lower()
        
        # HR-related query types
        hr_keywords = {
            "en": ["employee", "staff", "team", "hire", "recruit", "performance", "review"],
            "de": ["mitarbeiter", "personal", "team", "einstellen", "rekrutieren", "leistung", "bewertung"],
            "ja": ["従業員", "スタッフ", "チーム", "採用", "パフォーマンス", "評価"]
        }
        
        # Check for HR keywords in the appropriate language
        keywords = hr_keywords.get(language_code, hr_keywords["en"])
        if any(keyword in query_lower for keyword in keywords):
            return "hr_query"
        
        # Check for greeting
        greeting_keywords = {
            "en": ["hello", "hi", "hey", "greetings"],
            "de": ["hallo", "guten tag", "grüß"],
            "ja": ["こんにちは", "おはよう", "こんばんは"]
        }
        
        lang_greetings = greeting_keywords.get(language_code, greeting_keywords["en"])
        if any(greeting in query_lower for greeting in lang_greetings):
            return "greeting"
        
        # Default
        return "general"
    
    def _track_performance(self, language_code: str, response_time: float, confidence: float):
        """
        Track performance metrics.
        
        Args:
            language_code: Language code
            response_time: Response time in seconds
            confidence: Confidence score
        """
        if language_code not in self.response_times:
            self.response_times[language_code] = []
        if language_code not in self.confidence_scores:
            self.confidence_scores[language_code] = []
        
        self.response_times[language_code].append(response_time)
        self.confidence_scores[language_code].append(confidence)
        
        # Keep only the last 100 entries
        if len(self.response_times[language_code]) > 100:
            self.response_times[language_code] = self.response_times[language_code][-100:]
        if len(self.confidence_scores[language_code]) > 100:
            self.confidence_scores[language_code] = self.confidence_scores[language_code][-100:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all languages.
        
        Returns:
            Dictionary of performance metrics
        """
        metrics = {}
        
        for language_code in set(list(self.response_times.keys()) + list(self.confidence_scores.keys())):
            response_times = self.response_times.get(language_code, [])
            confidence_scores = self.confidence_scores.get(language_code, [])
            
            metrics[language_code] = {
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                "request_count": len(response_times),
                "last_response_time": response_times[-1] if response_times else 0,
                "last_confidence": confidence_scores[-1] if confidence_scores else 0
            }
        
        return metrics
    
    def _create_error_response(self, error_message: str, language_code: str) -> Dict[str, Any]:
        """
        Create an error response.
        
        Args:
            error_message: Error message
            language_code: Language code
            
        Returns:
            Error response dictionary
        """
        return {
            "response": self._get_error_message(language_code, error_message),
            "confidence": 0.3,
            "language": language_code,
            "model_used": "error_fallback",
            "processing_time": 0.0,
            "query_type": "error",
            "cultural_context_applied": False,
            "status": "error",
            "error": error_message
        }
    
    def _get_error_message(self, language_code: str, error: str) -> str:
        """
        Get a localized error message.
        
        Args:
            language_code: Language code
            error: Error details
            
        Returns:
            Localized error message
        """
        error_messages = {
            "en": "I'm sorry, I encountered an error while processing your request. Please try again later.",
            "de": "Es tut mir leid, bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.",
            "ja": "申し訳ありませんが、リクエストの処理中にエラーが発生しました。後でもう一度お試しください。"
        }
        
        return error_messages.get(language_code, error_messages["en"])