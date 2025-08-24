"""
Multilingual prompt engineering service for AI Employee Decision System.

This module provides language-specific prompt templates, cultural context injection,
and prompt optimization for Japanese, German, and English languages in HR contexts.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .language_service import SupportedLanguage, CulturalContext

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Types of prompts for different HR scenarios."""
    EMPLOYEE_SEARCH = "employee_search"
    SKILL_ANALYSIS = "skill_analysis"
    TEAM_BUILDING = "team_building"
    PERFORMANCE_REVIEW = "performance_review"
    HIRING_ADVICE = "hiring_advice"
    GENERAL_HR = "general_hr"
    GREETING = "greeting"


@dataclass
class PromptTemplate:
    """Template for generating language-specific prompts."""
    system_prompt: str
    user_prompt_template: str
    context_injection: str
    cultural_notes: List[str]
    response_format: str
    examples: List[Dict[str, str]]


@dataclass
class GeneratedPrompt:
    """Generated prompt with metadata."""
    system_prompt: str
    user_prompt: str
    language: SupportedLanguage
    prompt_type: PromptType
    cultural_context_applied: bool
    estimated_tokens: int


class MultilingualPromptEngineer:
    """
    Service for creating culturally-aware, language-specific prompts for HR AI interactions.
    """
    
    def __init__(self):
        """Initialize the prompt engineering service."""
        self.logger = logging.getLogger(__name__)
        self.prompt_templates = self._initialize_prompt_templates()
        self.cultural_adaptations = self._initialize_cultural_adaptations()
        self.logger.info("Multilingual prompt engineer initialized")
    
    def generate_prompt(
        self,
        query: str,
        language: SupportedLanguage,
        prompt_type: PromptType,
        context: Optional[Dict[str, Any]] = None,
        cultural_context: Optional[CulturalContext] = None
    ) -> GeneratedPrompt:
        """
        Generate a culturally-aware prompt for the given query and language.
        
        Args:
            query: User's query
            language: Target language
            prompt_type: Type of HR prompt needed
            context: Additional context (employee data, etc.)
            cultural_context: Cultural context for the language
            
        Returns:
            GeneratedPrompt with system and user prompts
        """
        context = context or {}
        
        # Get base template for language and prompt type
        template = self._get_template(language, prompt_type)
        
        # Apply cultural adaptations
        if cultural_context:
            template = self._apply_cultural_adaptations(template, cultural_context)
        
        # Generate system prompt
        system_prompt = self._generate_system_prompt(template, language, prompt_type, context)
        
        # Generate user prompt
        user_prompt = self._generate_user_prompt(template, query, context)
        
        # Estimate token count (rough approximation)
        estimated_tokens = self._estimate_tokens(system_prompt + user_prompt)
        
        return GeneratedPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            language=language,
            prompt_type=prompt_type,
            cultural_context_applied=cultural_context is not None,
            estimated_tokens=estimated_tokens
        )
    
    def _get_template(self, language: SupportedLanguage, prompt_type: PromptType) -> PromptTemplate:
        """Get the appropriate template for language and prompt type."""
        lang_templates = self.prompt_templates.get(language, self.prompt_templates[SupportedLanguage.ENGLISH])
        return lang_templates.get(prompt_type, lang_templates[PromptType.GENERAL_HR])
    
    def _apply_cultural_adaptations(self, template: PromptTemplate, cultural_context: CulturalContext) -> PromptTemplate:
        """Apply cultural adaptations to the template."""
        # Create a copy of the template with cultural adaptations
        adapted_template = PromptTemplate(
            system_prompt=template.system_prompt,
            user_prompt_template=template.user_prompt_template,
            context_injection=template.context_injection,
            cultural_notes=template.cultural_notes + cultural_context.cultural_notes,
            response_format=template.response_format,
            examples=template.examples
        )
        
        # Apply formality level adaptations
        if cultural_context.formality_level == "formal":
            adapted_template.system_prompt = self._make_formal(adapted_template.system_prompt, cultural_context.language)
        elif cultural_context.formality_level == "polite":
            adapted_template.system_prompt = self._make_polite(adapted_template.system_prompt, cultural_context.language)
        
        return adapted_template
    
    def _generate_system_prompt(
        self, 
        template: PromptTemplate, 
        language: SupportedLanguage, 
        prompt_type: PromptType,
        context: Dict[str, Any]
    ) -> str:
        """Generate the system prompt."""
        system_prompt = template.system_prompt
        
        # Inject context if available
        if context and template.context_injection:
            context_info = self._format_context(context, language)
            system_prompt += f"\n\n{template.context_injection.format(context=context_info)}"
        
        # Add cultural notes
        if template.cultural_notes:
            cultural_section = self._format_cultural_notes(template.cultural_notes, language)
            system_prompt += f"\n\n{cultural_section}"
        
        # Add response format instructions
        if template.response_format:
            system_prompt += f"\n\n{template.response_format}"
        
        return system_prompt
    
    def _generate_user_prompt(self, template: PromptTemplate, query: str, context: Dict[str, Any]) -> str:
        """Generate the user prompt."""
        # Format the user prompt template with the query and context
        user_prompt = template.user_prompt_template.format(
            query=query,
            **context
        )
        
        return user_prompt
    
    def _format_context(self, context: Dict[str, Any], language: SupportedLanguage) -> str:
        """Format context information for injection into prompts."""
        if not context:
            return ""
        
        context_lines = []
        
        # Format employee data if present
        if "employees" in context:
            employees = context["employees"]
            if language == SupportedLanguage.GERMAN:
                context_lines.append(f"Verfügbare Mitarbeiterdaten: {len(employees)} Mitarbeiter")
            elif language == SupportedLanguage.JAPANESE:
                context_lines.append(f"利用可能な従業員データ: {len(employees)}名の従業員")
            else:
                context_lines.append(f"Available employee data: {len(employees)} employees")
        
        # Format skills data if present
        if "skills" in context:
            skills = context["skills"]
            if language == SupportedLanguage.GERMAN:
                context_lines.append(f"Verfügbare Fähigkeiten: {', '.join(skills[:5])}")
            elif language == SupportedLanguage.JAPANESE:
                context_lines.append(f"利用可能なスキル: {', '.join(skills[:5])}")
            else:
                context_lines.append(f"Available skills: {', '.join(skills[:5])}")
        
        # Format department data if present
        if "departments" in context:
            departments = context["departments"]
            if language == SupportedLanguage.GERMAN:
                context_lines.append(f"Abteilungen: {', '.join(departments)}")
            elif language == SupportedLanguage.JAPANESE:
                context_lines.append(f"部署: {', '.join(departments)}")
            else:
                context_lines.append(f"Departments: {', '.join(departments)}")
        
        return "\n".join(context_lines)
    
    def _format_cultural_notes(self, cultural_notes: List[str], language: SupportedLanguage) -> str:
        """Format cultural notes for the system prompt."""
        if not cultural_notes:
            return ""
        
        if language == SupportedLanguage.GERMAN:
            header = "Kulturelle Hinweise:"
        elif language == SupportedLanguage.JAPANESE:
            header = "文化的な注意事項:"
        else:
            header = "Cultural considerations:"
        
        formatted_notes = "\n".join(f"- {note}" for note in cultural_notes)
        return f"{header}\n{formatted_notes}"
    
    def _make_formal(self, text: str, language: SupportedLanguage) -> str:
        """Make text more formal for the given language."""
        if language == SupportedLanguage.GERMAN:
            # Add formal German elements
            text = text.replace("du", "Sie").replace("dich", "Sie").replace("dir", "Ihnen")
            if not text.startswith("Sie sind"):
                text = f"Sie sind {text.lower()}"
        elif language == SupportedLanguage.JAPANESE:
            # Ensure polite forms are used and proper punctuation
            if text.endswith("です"):
                text += "。"
            elif text.endswith("ます"):
                text += "。"
            elif not any(ending in text for ending in ["です。", "ます。", "であります。"]):
                if text.endswith("。"):
                    text = text[:-1] + "です。"
                else:
                    text += "です。"
        
        return text
    
    def _make_polite(self, text: str, language: SupportedLanguage) -> str:
        """Make text more polite for the given language."""
        if language == SupportedLanguage.JAPANESE:
            # Add polite prefixes and suffixes
            if not text.startswith("どうぞ"):
                text = f"どうぞ{text}"
            if not text.endswith(("です。", "ます。")):
                text += "です。"
        elif language == SupportedLanguage.GERMAN:
            # Add polite German elements
            if not text.startswith("Bitte"):
                text = f"Bitte {text.lower()}"
        
        return text
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for the text (rough approximation)."""
        # Rough estimation: 1 token per 4 characters for English, adjust for other languages
        base_tokens = len(text) // 4
        
        # Japanese typically uses more tokens per character
        if any(ord(char) > 0x3000 for char in text):  # Contains CJK characters
            base_tokens = int(base_tokens * 1.5)
        
        return base_tokens
    
    def _initialize_prompt_templates(self) -> Dict[SupportedLanguage, Dict[PromptType, PromptTemplate]]:
        """Initialize prompt templates for all supported languages and prompt types."""
        return {
            SupportedLanguage.ENGLISH: self._get_english_templates(),
            SupportedLanguage.GERMAN: self._get_german_templates(),
            SupportedLanguage.JAPANESE: self._get_japanese_templates()
        }
    
    def _get_english_templates(self) -> Dict[PromptType, PromptTemplate]:
        """Get English prompt templates."""
        return {
            PromptType.EMPLOYEE_SEARCH: PromptTemplate(
                system_prompt="You are an expert HR assistant specializing in employee search and talent management. You help find employees based on skills, experience, and other criteria. Provide clear, actionable recommendations.",
                user_prompt_template="Help me find employees who match these criteria: {query}",
                context_injection="Available data: {context}",
                cultural_notes=[
                    "Be direct and efficient in your responses",
                    "Focus on measurable qualifications and achievements",
                    "Provide specific examples when possible"
                ],
                response_format="Format your response with clear headings and bullet points. Include confidence levels for matches.",
                examples=[
                    {
                        "query": "Find employees with Python programming skills",
                        "response": "Based on the employee database, I found 5 employees with Python skills:\n\n**High Match (90%+)**\n- John Smith: 5 years Python, Django expert\n- Sarah Johnson: 3 years Python, ML focus"
                    }
                ]
            ),
            PromptType.PERFORMANCE_REVIEW: PromptTemplate(
                system_prompt="You are an experienced HR professional specializing in performance reviews and employee development. Provide balanced, constructive feedback and actionable development suggestions.",
                user_prompt_template="Help me with this performance review situation: {query}",
                context_injection="Employee context: {context}",
                cultural_notes=[
                    "Balance positive feedback with areas for improvement",
                    "Focus on specific behaviors and outcomes",
                    "Provide actionable development recommendations"
                ],
                response_format="Structure your response with: Current Performance, Strengths, Areas for Improvement, Development Plan.",
                examples=[
                    {
                        "query": "How to conduct a performance review for a software developer",
                        "response": "**Performance Review Framework for Software Developer:**\n\n**Technical Skills Assessment:**\n- Code quality and best practices\n- Problem-solving approach\n- Technology proficiency"
                    }
                ]
            ),
            PromptType.TEAM_BUILDING: PromptTemplate(
                system_prompt="You are a team dynamics expert and organizational psychologist. Help build effective teams by analyzing team composition, dynamics, and providing actionable team-building strategies.",
                user_prompt_template="Help me with this team building challenge: {query}",
                context_injection="Team context: {context}",
                cultural_notes=[
                    "Consider diverse skill sets and personalities",
                    "Focus on complementary strengths",
                    "Address potential team dynamics issues"
                ],
                response_format="Provide team composition recommendations, potential challenges, and specific team-building activities.",
                examples=[
                    {
                        "query": "Build a team for a new mobile app project",
                        "response": "**Recommended Team Composition:**\n\n**Core Roles:**\n- iOS Developer (Swift expertise)\n- Android Developer (Kotlin/Java)\n- UI/UX Designer\n- Backend Developer\n- QA Engineer"
                    }
                ]
            ),
            PromptType.HIRING_ADVICE: PromptTemplate(
                system_prompt="You are a recruitment specialist with expertise in talent acquisition, interviewing, and candidate assessment. Provide practical hiring advice and best practices.",
                user_prompt_template="I need hiring advice for: {query}",
                context_injection="Hiring context: {context}",
                cultural_notes=[
                    "Focus on objective, measurable criteria",
                    "Emphasize diversity and inclusion",
                    "Provide structured interview approaches"
                ],
                response_format="Include job requirements, interview questions, assessment criteria, and red flags to watch for.",
                examples=[
                    {
                        "query": "How to hire a senior software engineer",
                        "response": "**Senior Software Engineer Hiring Guide:**\n\n**Key Requirements:**\n- 5+ years software development experience\n- Strong problem-solving skills\n- Leadership potential"
                    }
                ]
            ),
            PromptType.SKILL_ANALYSIS: PromptTemplate(
                system_prompt="You are a skills assessment expert who analyzes employee competencies, identifies skill gaps, and recommends development paths. Focus on both technical and soft skills.",
                user_prompt_template="Analyze skills for: {query}",
                context_injection="Skills data: {context}",
                cultural_notes=[
                    "Provide objective skill assessments",
                    "Identify both strengths and gaps",
                    "Recommend specific learning resources"
                ],
                response_format="Present skill analysis with current levels, gaps, and development recommendations.",
                examples=[
                    {
                        "query": "Analyze the programming skills in our development team",
                        "response": "**Team Skills Analysis:**\n\n**Current Strengths:**\n- JavaScript: 8/10 team members (Advanced)\n- Python: 6/10 team members (Intermediate to Advanced)"
                    }
                ]
            ),
            PromptType.GENERAL_HR: PromptTemplate(
                system_prompt="You are a knowledgeable HR generalist with expertise across all areas of human resources including policies, procedures, employee relations, and best practices.",
                user_prompt_template="I have an HR question: {query}",
                context_injection="HR context: {context}",
                cultural_notes=[
                    "Provide practical, actionable advice",
                    "Consider legal and compliance aspects",
                    "Focus on employee well-being and organizational effectiveness"
                ],
                response_format="Provide clear recommendations with rationale and next steps.",
                examples=[
                    {
                        "query": "How to improve employee retention",
                        "response": "**Employee Retention Strategy:**\n\n**Key Factors:**\n- Competitive compensation and benefits\n- Career development opportunities\n- Positive work culture"
                    }
                ]
            ),
            PromptType.GREETING: PromptTemplate(
                system_prompt="You are a friendly, professional HR assistant. Greet users warmly and help them understand how you can assist with their HR needs.",
                user_prompt_template="User greeting: {query}",
                context_injection="",
                cultural_notes=[
                    "Be warm and welcoming",
                    "Explain your capabilities clearly",
                    "Encourage questions and interaction"
                ],
                response_format="Provide a friendly greeting and overview of your HR assistance capabilities.",
                examples=[
                    {
                        "query": "Hello",
                        "response": "Hello! I'm your HR assistant, ready to help with employee management, hiring, performance reviews, team building, and any other HR questions you might have. What can I assist you with today?"
                    }
                ]
            )
        }
    
    def _get_german_templates(self) -> Dict[PromptType, PromptTemplate]:
        """Get German prompt templates."""
        return {
            PromptType.EMPLOYEE_SEARCH: PromptTemplate(
                system_prompt="Sie sind ein erfahrener Personalberater, der sich auf Mitarbeitersuche und Talentmanagement spezialisiert hat. Sie helfen dabei, Mitarbeiter basierend auf Fähigkeiten, Erfahrung und anderen Kriterien zu finden. Geben Sie klare, umsetzbare Empfehlungen.",
                user_prompt_template="Helfen Sie mir, Mitarbeiter zu finden, die diesen Kriterien entsprechen: {query}",
                context_injection="Verfügbare Daten: {context}",
                cultural_notes=[
                    "Seien Sie gründlich und detailliert in Ihren Antworten",
                    "Konzentrieren Sie sich auf messbare Qualifikationen",
                    "Verwenden Sie eine formelle, professionelle Sprache",
                    "Strukturieren Sie Informationen systematisch"
                ],
                response_format="Formatieren Sie Ihre Antwort mit klaren Überschriften und Aufzählungspunkten. Geben Sie Konfidenzlevel für Übereinstimmungen an.",
                examples=[
                    {
                        "query": "Mitarbeiter mit Python-Programmierkenntnissen finden",
                        "response": "Basierend auf der Mitarbeiterdatenbank habe ich 5 Mitarbeiter mit Python-Kenntnissen gefunden:\n\n**Hohe Übereinstimmung (90%+)**\n- Hans Müller: 5 Jahre Python, Django-Experte\n- Anna Schmidt: 3 Jahre Python, ML-Fokus"
                    }
                ]
            ),
            PromptType.PERFORMANCE_REVIEW: PromptTemplate(
                system_prompt="Sie sind ein erfahrener Personalfachmann, der sich auf Leistungsbeurteilungen und Mitarbeiterentwicklung spezialisiert hat. Geben Sie ausgewogenes, konstruktives Feedback und umsetzbare Entwicklungsvorschläge.",
                user_prompt_template="Helfen Sie mir bei dieser Leistungsbeurteilungssituation: {query}",
                context_injection="Mitarbeiterkontext: {context}",
                cultural_notes=[
                    "Verwenden Sie eine strukturierte, systematische Herangehensweise",
                    "Seien Sie direkt aber respektvoll",
                    "Konzentrieren Sie sich auf messbare Leistungsindikatoren",
                    "Berücksichtigen Sie die deutsche Arbeitskultur"
                ],
                response_format="Strukturieren Sie Ihre Antwort mit: Aktuelle Leistung, Stärken, Verbesserungsbereiche, Entwicklungsplan.",
                examples=[
                    {
                        "query": "Wie führe ich eine Leistungsbeurteilung für einen Softwareentwickler durch",
                        "response": "**Leistungsbeurteilungsrahmen für Softwareentwickler:**\n\n**Technische Fähigkeitsbewertung:**\n- Codequalität und Best Practices\n- Problemlösungsansatz\n- Technologiekompetenz"
                    }
                ]
            ),
            PromptType.TEAM_BUILDING: PromptTemplate(
                system_prompt="Sie sind ein Experte für Teamdynamik und Organisationspsychologie. Helfen Sie beim Aufbau effektiver Teams durch Analyse der Teamzusammensetzung, Dynamik und Bereitstellung umsetzbarer Teambuilding-Strategien.",
                user_prompt_template="Helfen Sie mir bei dieser Teambuilding-Herausforderung: {query}",
                context_injection="Teamkontext: {context}",
                cultural_notes=[
                    "Berücksichtigen Sie die deutsche Präferenz für klare Strukturen",
                    "Fokussieren Sie auf Effizienz und Kompetenz",
                    "Respektieren Sie Hierarchien und Fachexpertise",
                    "Planen Sie systematisch und gründlich"
                ],
                response_format="Geben Sie Empfehlungen zur Teamzusammensetzung, potenzielle Herausforderungen und spezifische Teambuilding-Aktivitäten an.",
                examples=[
                    {
                        "query": "Ein Team für ein neues Mobile-App-Projekt zusammenstellen",
                        "response": "**Empfohlene Teamzusammensetzung:**\n\n**Kernrollen:**\n- iOS-Entwickler (Swift-Expertise)\n- Android-Entwickler (Kotlin/Java)\n- UI/UX-Designer\n- Backend-Entwickler\n- QA-Ingenieur"
                    }
                ]
            ),
            PromptType.HIRING_ADVICE: PromptTemplate(
                system_prompt="Sie sind ein Rekrutierungsspezialist mit Expertise in Talentakquisition, Vorstellungsgesprächen und Kandidatenbewertung. Geben Sie praktische Einstellungsberatung und Best Practices.",
                user_prompt_template="Ich brauche Einstellungsberatung für: {query}",
                context_injection="Einstellungskontext: {context}",
                cultural_notes=[
                    "Berücksichtigen Sie deutsche Arbeitsgesetze und -normen",
                    "Fokussieren Sie auf Qualifikationen und Kompetenz",
                    "Verwenden Sie strukturierte Bewertungskriterien",
                    "Beachten Sie Datenschutz und Compliance"
                ],
                response_format="Geben Sie Stellenanforderungen, Interviewfragen, Bewertungskriterien und Warnsignale an.",
                examples=[
                    {
                        "query": "Wie stelle ich einen Senior-Softwareingenieur ein",
                        "response": "**Einstellungsleitfaden für Senior-Softwareingenieur:**\n\n**Hauptanforderungen:**\n- 5+ Jahre Softwareentwicklungserfahrung\n- Starke Problemlösungsfähigkeiten\n- Führungspotenzial"
                    }
                ]
            ),
            PromptType.SKILL_ANALYSIS: PromptTemplate(
                system_prompt="Sie sind ein Experte für Fähigkeitsbewertung, der Mitarbeiterkompetenzen analysiert, Qualifikationslücken identifiziert und Entwicklungswege empfiehlt. Konzentrieren Sie sich sowohl auf technische als auch auf Soft Skills.",
                user_prompt_template="Analysieren Sie Fähigkeiten für: {query}",
                context_injection="Fähigkeitsdaten: {context}",
                cultural_notes=[
                    "Geben Sie objektive, datenbasierte Bewertungen",
                    "Fokussieren Sie auf messbare Kompetenzen",
                    "Empfehlen Sie strukturierte Lernpfade",
                    "Berücksichtigen Sie deutsche Ausbildungsstandards"
                ],
                response_format="Präsentieren Sie die Fähigkeitsanalyse mit aktuellen Levels, Lücken und Entwicklungsempfehlungen.",
                examples=[
                    {
                        "query": "Analysieren Sie die Programmierfähigkeiten in unserem Entwicklungsteam",
                        "response": "**Team-Fähigkeitsanalyse:**\n\n**Aktuelle Stärken:**\n- JavaScript: 8/10 Teammitglieder (Fortgeschritten)\n- Python: 6/10 Teammitglieder (Mittelstufe bis Fortgeschritten)"
                    }
                ]
            ),
            PromptType.GENERAL_HR: PromptTemplate(
                system_prompt="Sie sind ein sachkundiger HR-Generalist mit Expertise in allen Bereichen der Personalwirtschaft einschließlich Richtlinien, Verfahren, Mitarbeiterbeziehungen und Best Practices.",
                user_prompt_template="Ich habe eine HR-Frage: {query}",
                context_injection="HR-Kontext: {context}",
                cultural_notes=[
                    "Geben Sie praktische, umsetzbare Ratschläge",
                    "Berücksichtigen Sie rechtliche und Compliance-Aspekte",
                    "Fokussieren Sie auf Mitarbeiterwohl und organisatorische Effektivität",
                    "Beachten Sie deutsche Arbeitsgesetze und -kultur"
                ],
                response_format="Geben Sie klare Empfehlungen mit Begründung und nächsten Schritten.",
                examples=[
                    {
                        "query": "Wie kann ich die Mitarbeiterbindung verbessern",
                        "response": "**Mitarbeiterbindungsstrategie:**\n\n**Schlüsselfaktoren:**\n- Wettbewerbsfähige Vergütung und Zusatzleistungen\n- Karriereentwicklungsmöglichkeiten\n- Positive Arbeitskultur"
                    }
                ]
            ),
            PromptType.GREETING: PromptTemplate(
                system_prompt="Sie sind ein freundlicher, professioneller HR-Assistent. Begrüßen Sie Benutzer herzlich und helfen Sie ihnen zu verstehen, wie Sie bei ihren HR-Bedürfnissen helfen können.",
                user_prompt_template="Benutzerbegrüßung: {query}",
                context_injection="",
                cultural_notes=[
                    "Seien Sie höflich und professionell",
                    "Verwenden Sie die formelle Anrede 'Sie'",
                    "Erklären Sie Ihre Fähigkeiten klar",
                    "Ermutigen Sie zu Fragen und Interaktion"
                ],
                response_format="Geben Sie eine freundliche Begrüßung und Übersicht Ihrer HR-Unterstützungsfähigkeiten.",
                examples=[
                    {
                        "query": "Hallo",
                        "response": "Guten Tag! Ich bin Ihr HR-Assistent und stehe bereit, um bei Mitarbeiterverwaltung, Einstellungen, Leistungsbeurteilungen, Teambuilding und allen anderen HR-Fragen zu helfen. Womit kann ich Ihnen heute behilflich sein?"
                    }
                ]
            )
        }
    
    def _get_japanese_templates(self) -> Dict[PromptType, PromptTemplate]:
        """Get Japanese prompt templates."""
        return {
            PromptType.EMPLOYEE_SEARCH: PromptTemplate(
                system_prompt="あなたは従業員検索と人材管理を専門とする経験豊富な人事アシスタントです。スキル、経験、その他の基準に基づいて従業員を見つけるお手伝いをします。明確で実行可能な推奨事項を提供してください。",
                user_prompt_template="次の条件に合う従業員を見つけるのを手伝ってください: {query}",
                context_injection="利用可能なデータ: {context}",
                cultural_notes=[
                    "丁寧で敬語を使った回答を心がけてください",
                    "グループの調和を重視してください",
                    "階層と年功序列を尊重してください",
                    "間接的なコミュニケーションスタイルを使用してください"
                ],
                response_format="明確な見出しと箇条書きで回答をフォーマットしてください。マッチングの信頼度レベルを含めてください。",
                examples=[
                    {
                        "query": "Pythonプログラミングスキルを持つ従業員を見つける",
                        "response": "従業員データベースに基づき、Pythonスキルを持つ5名の従業員を見つけました：\n\n**高いマッチング（90%以上）**\n- 田中太郎さん：Python 5年、Django専門家\n- 佐藤花子さん：Python 3年、ML専門"
                    }
                ]
            ),
            PromptType.PERFORMANCE_REVIEW: PromptTemplate(
                system_prompt="あなたは人事評価と従業員開発を専門とする経験豊富な人事専門家です。バランスの取れた建設的なフィードバックと実行可能な開発提案を提供してください。",
                user_prompt_template="この人事評価の状況について手伝ってください: {query}",
                context_injection="従業員の背景: {context}",
                cultural_notes=[
                    "調和を保ちながら改善点を伝えてください",
                    "直接的な批判を避け、建設的な提案を重視してください",
                    "グループの成果と個人の貢献のバランスを考慮してください",
                    "長期的な関係性を重視してください"
                ],
                response_format="現在のパフォーマンス、強み、改善領域、開発計画で回答を構成してください。",
                examples=[
                    {
                        "query": "ソフトウェア開発者の人事評価を行う方法",
                        "response": "**ソフトウェア開発者の人事評価フレームワーク：**\n\n**技術スキル評価：**\n- コード品質とベストプラクティス\n- 問題解決アプローチ\n- 技術習熟度"
                    }
                ]
            ),
            PromptType.TEAM_BUILDING: PromptTemplate(
                system_prompt="あなたはチームダイナミクスの専門家であり組織心理学者です。チーム構成、ダイナミクスを分析し、実行可能なチームビルディング戦略を提供することで効果的なチーム構築を支援してください。",
                user_prompt_template="このチームビルディングの課題について手伝ってください: {query}",
                context_injection="チームの背景: {context}",
                cultural_notes=[
                    "グループの調和（和）を最優先に考えてください",
                    "コンセンサス形成を重視してください",
                    "階層と年功序列を尊重してください",
                    "長期的な関係構築に焦点を当ててください"
                ],
                response_format="チーム構成の推奨事項、潜在的な課題、具体的なチームビルディング活動を提供してください。",
                examples=[
                    {
                        "query": "新しいモバイルアプリプロジェクトのチームを構築する",
                        "response": "**推奨チーム構成：**\n\n**コア役割：**\n- iOSデベロッパー（Swift専門知識）\n- Androidデベロッパー（Kotlin/Java）\n- UI/UXデザイナー\n- バックエンドデベロッパー\n- QAエンジニア"
                    }
                ]
            ),
            PromptType.HIRING_ADVICE: PromptTemplate(
                system_prompt="あなたは人材獲得、面接、候補者評価の専門知識を持つ採用スペシャリストです。実践的な採用アドバイスとベストプラクティスを提供してください。",
                user_prompt_template="次について採用アドバイスが必要です: {query}",
                context_injection="採用の背景: {context}",
                cultural_notes=[
                    "長期的な雇用関係を前提とした採用を考慮してください",
                    "チームとの調和を重視してください",
                    "謙虚さと協調性を評価してください",
                    "面接では相互の敬意を示してください"
                ],
                response_format="職務要件、面接質問、評価基準、注意すべき点を含めてください。",
                examples=[
                    {
                        "query": "シニアソフトウェアエンジニアを採用する方法",
                        "response": "**シニアソフトウェアエンジニア採用ガイド：**\n\n**主要要件：**\n- ソフトウェア開発経験5年以上\n- 強い問題解決能力\n- リーダーシップの可能性"
                    }
                ]
            ),
            PromptType.SKILL_ANALYSIS: PromptTemplate(
                system_prompt="あなたは従業員の能力を分析し、スキルギャップを特定し、開発パスを推奨するスキル評価の専門家です。技術スキルとソフトスキルの両方に焦点を当ててください。",
                user_prompt_template="次についてスキル分析をしてください: {query}",
                context_injection="スキルデータ: {context}",
                cultural_notes=[
                    "継続的な学習と改善を重視してください",
                    "チーム全体のスキル向上を考慮してください",
                    "謙虚な自己評価を奨励してください",
                    "メンターシップと知識共有を促進してください"
                ],
                response_format="現在のレベル、ギャップ、開発推奨事項を含むスキル分析を提示してください。",
                examples=[
                    {
                        "query": "開発チームのプログラミングスキルを分析する",
                        "response": "**チームスキル分析：**\n\n**現在の強み：**\n- JavaScript: チームメンバー10名中8名（上級レベル）\n- Python: チームメンバー10名中6名（中級から上級レベル）"
                    }
                ]
            ),
            PromptType.GENERAL_HR: PromptTemplate(
                system_prompt="あなたは人事のすべての分野にわたる専門知識を持つ知識豊富な人事ジェネラリストです。ポリシー、手順、従業員関係、ベストプラクティスを含みます。",
                user_prompt_template="人事に関する質問があります: {query}",
                context_injection="人事の背景: {context}",
                cultural_notes=[
                    "従業員の福祉と組織の調和を重視してください",
                    "長期的な関係と安定性を考慮してください",
                    "グループの利益を個人の利益より優先してください",
                    "丁寧で敬意のあるコミュニケーションを維持してください"
                ],
                response_format="理由と次のステップを含む明確な推奨事項を提供してください。",
                examples=[
                    {
                        "query": "従業員の定着率を向上させる方法",
                        "response": "**従業員定着戦略：**\n\n**主要要因：**\n- 競争力のある報酬と福利厚生\n- キャリア開発機会\n- 良好な職場文化"
                    }
                ]
            ),
            PromptType.GREETING: PromptTemplate(
                system_prompt="あなたは親しみやすく専門的な人事アシスタントです。ユーザーを温かく迎え、人事ニーズにどのように支援できるかを理解してもらってください。",
                user_prompt_template="ユーザーの挨拶: {query}",
                context_injection="",
                cultural_notes=[
                    "丁寧で敬語を使った挨拶をしてください",
                    "謙虚で親しみやすい態度を示してください",
                    "能力を明確に説明してください",
                    "質問と交流を奨励してください"
                ],
                response_format="親しみやすい挨拶と人事支援能力の概要を提供してください。",
                examples=[
                    {
                        "query": "こんにちは",
                        "response": "こんにちは！私はあなたの人事アシスタントです。従業員管理、採用、人事評価、チームビルディング、その他の人事に関するご質問にお答えする準備ができています。本日はどのようなお手伝いをさせていただけますでしょうか？"
                    }
                ]
            )
        }
    
    def _initialize_cultural_adaptations(self) -> Dict[SupportedLanguage, Dict[str, Any]]:
        """Initialize cultural adaptation rules."""
        return {
            SupportedLanguage.ENGLISH: {
                "formality_markers": ["please", "thank you", "would you", "could you"],
                "directness_level": "high",
                "hierarchy_awareness": "low"
            },
            SupportedLanguage.GERMAN: {
                "formality_markers": ["bitte", "danke", "würden Sie", "könnten Sie"],
                "directness_level": "high",
                "hierarchy_awareness": "medium"
            },
            SupportedLanguage.JAPANESE: {
                "formality_markers": ["お願いします", "ありがとうございます", "いただけませんか"],
                "directness_level": "low",
                "hierarchy_awareness": "high"
            }
        }
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get statistics about available prompt templates."""
        stats = {
            "total_languages": len(self.prompt_templates),
            "total_prompt_types": len(PromptType),
            "languages": list(lang.value for lang in self.prompt_templates.keys()),
            "prompt_types": list(pt.value for pt in PromptType)
        }
        
        # Count templates per language
        for language, templates in self.prompt_templates.items():
            stats[f"{language.value}_templates"] = len(templates)
        
        return stats
    
    def validate_prompt_template(self, language: SupportedLanguage, prompt_type: PromptType) -> bool:
        """Validate that a prompt template exists and is properly formatted."""
        try:
            template = self._get_template(language, prompt_type)
            
            # Check required fields
            required_fields = ['system_prompt', 'user_prompt_template', 'response_format']
            for field in required_fields:
                if not getattr(template, field):
                    return False
            
            # Check that template has placeholder for query
            if '{query}' not in template.user_prompt_template:
                return False
            
            return True
        except Exception:
            return False