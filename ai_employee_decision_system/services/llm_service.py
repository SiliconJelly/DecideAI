"""
Local LLM service using Ollama for the AI Employee Decision System.
"""
import json
import requests
from typing import Dict, List, Optional, Any
from ai_employee_decision_system.core import config, get_logger

logger = get_logger(__name__)


class OllamaLLMService:
    """Service for local LLM operations using Ollama."""
    
    def __init__(self, model_name: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama LLM service.
        
        Args:
            model_name: Name of the Ollama model to use (default: llama3.2:3b for better performance)
            base_url: Base URL for Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self.fallback_models = ["llama3.2:3b", "mistral:7b", "llama2:7b-chat"]  # Try multiple models
        self.available = False
        self.active_model = None
        
        # Try to connect and find available model
        self._initialize_connection()
        
        if self.available:
            logger.info(f"Ollama LLM service initialized with model: {self.active_model}")
        else:
            logger.warning("Ollama not available, using intelligent fallback responses")
    
    def _initialize_connection(self):
        """Initialize connection to Ollama and find available model."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code != 200:
                logger.warning("Ollama service not responding")
                return
            
            models_data = response.json().get("models", [])
            available_models = [model["name"] for model in models_data]
            
            logger.info(f"Available Ollama models: {available_models}")
            
            # Try to find a working model
            models_to_try = [self.model_name] + [m for m in self.fallback_models if m != self.model_name]
            
            for model in models_to_try:
                if model in available_models:
                    # Test the model with a simple query
                    if self._test_model(model):
                        self.active_model = model
                        self.available = True
                        logger.info(f"Successfully connected to model: {model}")
                        return
                else:
                    # Try to pull the model
                    logger.info(f"Model {model} not found, attempting to pull...")
                    if self._pull_model(model):
                        if self._test_model(model):
                            self.active_model = model
                            self.available = True
                            logger.info(f"Successfully pulled and connected to model: {model}")
                            return
            
            logger.warning("No working Ollama models found")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama connection: {e}")
    
    def _test_model(self, model_name: str) -> bool:
        """Test if a model is working with a simple query."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": "Hello, respond with just 'OK'",
                    "stream": False,
                    "options": {"max_tokens": 10}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return "response" in result and len(result["response"].strip()) > 0
            return False
            
        except Exception as e:
            logger.debug(f"Model test failed for {model_name}: {e}")
            return False
    
    def _pull_model(self, model_name: str) -> bool:
        """Pull a model if it's not available."""
        try:
            logger.info(f"Pulling model {model_name}... This may take a few minutes.")
            
            # Use streaming to handle long downloads
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600  # 10 minutes timeout for model download
            )
            
            if response.status_code == 200:
                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "status" in data:
                                logger.debug(f"Model pull status: {data['status']}")
                            if data.get("status") == "success":
                                logger.info(f"Model {model_name} pulled successfully")
                                return True
                        except json.JSONDecodeError:
                            continue
                
                # If we get here, assume success if no error
                logger.info(f"Model {model_name} pull completed")
                return True
            else:
                logger.error(f"Failed to pull model {model_name}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a response using the local LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            context: Additional context for the query
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.available:
            return self._fallback_response(prompt, context)
        
        try:
            # Prepare the system prompt for employee queries
            system_prompt = self._get_system_prompt(context)
            
            # Combine system prompt with user query
            full_prompt = f"{system_prompt}\n\nUser Query: {prompt}\n\nResponse:"
            
            # Call Ollama API with the active model - optimized for speed
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.active_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 200,  # Reduced for faster responses
                        "stop": ["User Query:", "Human:", "Assistant:", "\n\n"],  # Stop tokens to prevent loops
                        "num_ctx": 2048,  # Limit context for speed
                        "repeat_penalty": 1.1
                    }
                },
                timeout=15  # Reduced timeout - fallback if too slow
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                # Clean up the response
                ai_response = self._clean_response(ai_response)
                
                return {
                    "response": ai_response,
                    "confidence": 0.9,
                    "query_type": "llm_generated",
                    "model_used": self.active_model,
                    "processing_time": result.get("total_duration", 0) / 1000000000 if result.get("total_duration") else 0  # Convert nanoseconds to seconds
                }
            else:
                logger.warning(f"Ollama API error: {response.status_code}, falling back to intelligent response")
                return self._fallback_response(prompt, context)
                
        except requests.exceptions.Timeout:
            logger.warning(f"Ollama timeout (>15s), using fast fallback for: {prompt[:50]}...")
            return self._fallback_response(prompt, context)
        except Exception as e:
            logger.warning(f"Ollama error, using fallback: {e}")
            return self._fallback_response(prompt, context)
    
    def _clean_response(self, response: str) -> str:
        """Clean up the AI response."""
        # Remove common artifacts
        response = response.strip()
        
        # Remove repeated prompts or system messages
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and system artifacts
            if (line and 
                not line.startswith("User Query:") and 
                not line.startswith("Response:") and
                not line.startswith("Human:") and
                not line.startswith("Assistant:") and
                not line.startswith("System:")):
                cleaned_lines.append(line)
        
        cleaned_response = '\n'.join(cleaned_lines).strip()
        
        # Ensure we have a meaningful response
        if len(cleaned_response) < 10:
            return response  # Return original if cleaning made it too short
        
        return cleaned_response
    
    def _get_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Get the system prompt for intelligent HR assistance."""
        base_prompt = """You are an intelligent HR assistant for DecideAI, specializing in German and Japanese institutional HR management. You provide expert advice for universities and SMEs.

CORE EXPERTISE:
- HR best practices and employee relations
- Cultural intelligence for German and Japanese workplaces
- Diversity, inclusion, and multicultural team management
- Conflict resolution and team building
- Performance management and career development
- Legal compliance awareness (German labor law, Japanese employment practices)

CULTURAL INTELLIGENCE:
- German workplace culture: Direct communication, work-life balance, co-determination, GDPR compliance
- Japanese workplace culture: Hierarchical respect, consensus-building (nemawashi), group harmony (wa), long-term employment
- Religious sensitivity: Islamic practices, Christian traditions, Buddhist customs, dietary restrictions
- International team dynamics and cross-cultural communication

RESPONSE GUIDELINES:
- Provide thoughtful, professional HR advice
- Consider cultural context and sensitivities
- Acknowledge when legal consultation is needed
- Suggest practical, actionable solutions
- Maintain professional boundaries while being helpful
- Adapt communication style to cultural context (German directness vs Japanese politeness)
- Respond in the same language as the query (German, Japanese, or English)

EXAMPLE SCENARIOS YOU HANDLE:
- "How can I help my foreign employees integrate better?"
- "What are appropriate team building activities for a multicultural team?"
- "How should I handle religious accommodation requests?"
- "What's the best way to give feedback to Japanese employees?"
- "How do I resolve conflicts between German and international staff?"

Remember: You're an expert HR advisor, not just an employee database query tool."""

        # Add specific context if available
        if context:
            if "employees" in context and len(context["employees"]) > 0:
                employees_info = "\n\nCURRENT TEAM CONTEXT:\n"
                for emp in context["employees"][:10]:  # Limit to first 10
                    name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}"
                    position = emp.get('position', 'N/A')
                    department = emp.get('department', 'N/A')
                    employees_info += f"- {name}: {position} in {department}\n"
                base_prompt += employees_info
            
            if "skills" in context and len(context["skills"]) > 0:
                skills_info = f"\n\nAVAILABLE SKILLS: {', '.join(context['skills'][:20])}"  # Limit skills list
                base_prompt += skills_info
            
            if "departments" in context and len(context["departments"]) > 0:
                dept_info = f"\n\nDEPARTMENTS: {', '.join(context['departments'])}"
                base_prompt += dept_info
        
        return base_prompt
    
    def _fallback_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Intelligent fallback responses when LLM is not available."""
        prompt_lower = prompt.lower()
        
        # Detect language and cultural context
        is_german = any(word in prompt_lower for word in ['wie', 'was', 'wer', 'wo', 'warum', 'können', 'sollte', 'mitarbeiter', 'kollegen'])
        is_japanese = any(char in prompt for char in 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん')
        
        # Handle cultural/religious sensitivity questions
        if any(word in prompt_lower for word in ['muslim', 'islamic', 'halal', 'sake', 'alcohol', 'pork', 'religious', 'culture', 'foreign']):
            if is_german:
                response = """Das ist eine wichtige Frage zur kulturellen Sensibilität. Hier sind einige Überlegungen:

🕌 **Religiöse Rücksichtnahme:**
- Muslimische Kollegen trinken keinen Alkohol (einschließlich Sake)
- Bessere Alternative: Gemeinsames Essen in einem Restaurant mit Halal-Optionen
- Oder kultureller Austausch ohne Alkohol (Tee-Zeremonie, Kochkurs)

🤝 **Kulturelle Integration:**
- Fragen Sie nach Präferenzen und Einschränkungen
- Organisieren Sie inklusive Aktivitäten
- Zeigen Sie Interesse an verschiedenen Kulturen

⚠️ **Wichtiger Hinweis:** Respektieren Sie immer religiöse und kulturelle Grenzen. Zwingen Sie niemanden zu Aktivitäten, die gegen ihre Überzeugungen verstoßen."""
            elif is_japanese:
                response = """文化的配慮に関する重要な質問ですね。以下の点を考慮してください：

🕌 **宗教的配慮：**
- イスラム教徒の同僚はアルコール（日本酒を含む）を飲みません
- より良い代替案：ハラル対応レストランでの食事会
- またはアルコールなしの文化交流（茶道体験、料理教室など）

🤝 **文化統合：**
- 個人の好みや制限について尋ねる
- 包括的な活動を企画する
- 異なる文化に興味を示す

⚠️ **重要な注意：** 常に宗教的・文化的境界を尊重してください。信念に反する活動を強要してはいけません。"""
            else:
                response = """This is an important question about cultural sensitivity. Here are some considerations:

🕌 **Religious Considerations:**
- Muslim colleagues don't drink alcohol (including sake)
- Better alternative: Shared meal at a restaurant with halal options
- Or cultural exchange without alcohol (tea ceremony, cooking class)

🤝 **Cultural Integration:**
- Ask about preferences and restrictions
- Organize inclusive activities
- Show genuine interest in different cultures

⚠️ **Important:** Always respect religious and cultural boundaries. Never pressure anyone into activities that go against their beliefs."""
            
            return {
                "response": response,
                "confidence": 0.9,
                "query_type": "cultural_sensitivity",
                "model_used": "intelligent_fallback"
            }
        
        # Handle team building questions
        elif any(word in prompt_lower for word in ['team', 'zusammen', 'activity', 'event', 'building', 'チーム', '活動']):
            if is_german:
                response = """Hier sind kulturell angemessene Teambuilding-Ideen:

🍽️ **Inklusive Aktivitäten:**
- Internationales Potluck (jeder bringt Essen aus seiner Kultur mit)
- Kochkurs mit verschiedenen Küchen
- Kultureller Austausch-Workshop

🎯 **Professionelle Aktivitäten:**
- Escape Room (problemlösungsorientiert)
- Gemeinsame Freiwilligenarbeit
- Workshops zu interkultureller Kommunikation

⚠️ **Zu vermeiden:**
- Alkohol-zentrierte Events
- Aktivitäten, die religiöse/kulturelle Grenzen überschreiten"""
            else:
                response = """Here are culturally appropriate team building ideas:

🍽️ **Inclusive Activities:**
- International potluck (everyone brings food from their culture)
- Cooking class featuring different cuisines
- Cultural exchange workshop

🎯 **Professional Activities:**
- Escape room (problem-solving focused)
- Volunteer work together
- Cross-cultural communication workshops

⚠️ **Avoid:**
- Alcohol-centered events
- Activities that cross religious/cultural boundaries"""
            
            return {
                "response": response,
                "confidence": 0.8,
                "query_type": "team_building",
                "model_used": "intelligent_fallback"
            }
        
        # Handle employee queries with better context
        elif "employee" in prompt_lower or "mitarbeiter" in prompt_lower or "従業員" in prompt:
            if context and "employees" in context and len(context["employees"]) > 0:
                emp_count = len(context["employees"])
                if is_german:
                    response = f"Ich kann Ihnen bei der Analyse Ihrer {emp_count} Mitarbeiter helfen. Fragen Sie mich nach spezifischen Fähigkeiten, Abteilungen oder Projektempfehlungen."
                else:
                    response = f"I can help you analyze your {emp_count} employees. Ask me about specific skills, departments, or project recommendations."
            else:
                if is_german:
                    response = "Bitte fügen Sie zuerst Mitarbeiterdaten hinzu, dann kann ich Ihnen bei der Analyse und Empfehlungen helfen."
                else:
                    response = "Please add employee data first, then I can help with analysis and recommendations."
            
            return {
                "response": response,
                "confidence": 0.7,
                "query_type": "employee_query",
                "model_used": "intelligent_fallback"
            }
        
        # Default intelligent response
        else:
            if is_german:
                response = """Ich bin Ihr intelligenter HR-Assistent für deutsche und japanische Institutionen. Ich kann helfen bei:

🏢 **HR-Expertise:**
- Mitarbeiterführung und Teamdynamik
- Kulturelle Integration und Vielfalt
- Konfliktlösung und Mediation
- Leistungsmanagement

🌍 **Kulturelle Intelligenz:**
- Deutsche Arbeitskultur und Gesetze
- Japanische Geschäftsetikette
- Religiöse und kulturelle Sensibilität

Stellen Sie mir gerne komplexe HR-Fragen!"""
            elif is_japanese:
                response = """私はドイツと日本の機関向けのインテリジェントHRアシスタントです。以下のサポートが可能です：

🏢 **HR専門知識:**
- 従業員管理とチームダイナミクス
- 文化統合と多様性
- 紛争解決と調停
- パフォーマンス管理

🌍 **文化的知性:**
- ドイツの職場文化と法律
- 日本のビジネスエチケット
- 宗教的・文化的配慮

複雑なHRの質問をお気軽にどうぞ！"""
            else:
                response = """I'm your intelligent HR assistant for German and Japanese institutions. I can help with:

🏢 **HR Expertise:**
- Employee management and team dynamics
- Cultural integration and diversity
- Conflict resolution and mediation
- Performance management

🌍 **Cultural Intelligence:**
- German workplace culture and laws
- Japanese business etiquette
- Religious and cultural sensitivity

Feel free to ask me complex HR questions!"""
            
            return {
                "response": response,
                "confidence": 0.8,
                "query_type": "general_help",
                "model_used": "intelligent_fallback"
            }


class HuggingFaceLLMService:
    """Alternative LLM service using Hugging Face Transformers."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """Initialize Hugging Face LLM service."""
        self.model_name = model_name
        self.available = False
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.available = True
            
            logger.info(f"Hugging Face LLM initialized: {model_name} on {self.device}")
            
        except ImportError:
            logger.warning("Transformers library not available. Install with: pip install transformers torch")
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model: {e}")
    
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Hugging Face model."""
        if not self.available:
            return self._fallback_response(prompt, context)
        
        try:
            # Encode the prompt
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the original prompt from response
            response = response[len(prompt):].strip()
            
            return {
                "response": response,
                "confidence": 0.8,
                "query_type": "llm_generated",
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._fallback_response(prompt, context)
    
    def _fallback_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback response when model is not available."""
        return {
            "response": "I'm having trouble processing your request right now. Please try a simpler question about employees or skills.",
            "confidence": 0.3,
            "query_type": "error",
            "model_used": "fallback"
        }