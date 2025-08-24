"""
Multilingual response formatting service for AI Employee Decision System.

This module provides language-specific response formatting, cultural context awareness,
and professional communication formatting for Japanese, German, and English languages
in HR contexts.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .language_service import SupportedLanguage, CulturalContext

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses that can be formatted."""
    EMPLOYEE_LIST = "employee_list"
    SKILL_ANALYSIS = "skill_analysis"
    TEAM_RECOMMENDATION = "team_recommendation"
    PERFORMANCE_FEEDBACK = "performance_feedback"
    HIRING_GUIDANCE = "hiring_guidance"
    GENERAL_ADVICE = "general_advice"
    ERROR_MESSAGE = "error_message"
    GREETING = "greeting"


@dataclass
class FormattingRules:
    """Rules for formatting responses in a specific language."""
    bullet_style: str
    number_format: str
    section_separator: str
    emphasis_markers: Tuple[str, str]
    politeness_prefix: str
    politeness_suffix: str
    date_format: str
    list_connector: str
    formal_address: str


@dataclass
class FormattedResponse:
    """Formatted response with metadata."""
    content: str
    language: SupportedLanguage
    response_type: ResponseType
    formatting_applied: List[str]
    cultural_adaptations: List[str]
    estimated_reading_time: int  # in seconds
    formality_level: str


class MultilingualResponseFormatter:
    """
    Service for formatting AI responses according to language-specific rules
    and cultural contexts for professional HR communication.
    """
    
    def __init__(self):
        """Initialize the response formatter."""
        self.logger = logging.getLogger(__name__)
        self.formatting_rules = self._initialize_formatting_rules()
        self.cultural_templates = self._initialize_cultural_templates()
        self.professional_phrases = self._initialize_professional_phrases()
        self.logger.info("Multilingual response formatter initialized")
    
    def format_response(
        self,
        content: str,
        language: SupportedLanguage,
        response_type: ResponseType,
        cultural_context: Optional[CulturalContext] = None,
        formality_level: str = "business",
        context: Optional[Dict[str, Any]] = None
    ) -> FormattedResponse:
        """
        Format a response according to language and cultural rules.
        
        Args:
            content: Raw response content
            language: Target language
            response_type: Type of response
            cultural_context: Cultural context for formatting
            formality_level: Level of formality (casual, business, formal)
            context: Additional context for formatting
            
        Returns:
            FormattedResponse with properly formatted content
        """
        context = context or {}
        formatting_applied = []
        cultural_adaptations = []
        
        # Get formatting rules for the language
        rules = self.formatting_rules[language]
        
        # Apply basic text cleaning and normalization
        formatted_content = self._clean_and_normalize(content)
        formatting_applied.append("text_normalization")
        
        # Apply language-specific formatting
        formatted_content = self._apply_language_formatting(
            formatted_content, language, rules
        )
        formatting_applied.append("language_formatting")
        
        # Apply response type specific formatting
        formatted_content = self._apply_response_type_formatting(
            formatted_content, response_type, language, rules
        )
        formatting_applied.append("response_type_formatting")
        
        # Apply cultural adaptations
        if cultural_context:
            formatted_content, adaptations = self._apply_cultural_adaptations(
                formatted_content, cultural_context, formality_level, rules
            )
            cultural_adaptations.extend(adaptations)
        
        # Apply formality level adjustments
        formatted_content = self._apply_formality_level(
            formatted_content, formality_level, language, rules
        )
        formatting_applied.append("formality_adjustment")
        
        # Add professional framing
        formatted_content = self._add_professional_framing(
            formatted_content, response_type, language, formality_level
        )
        formatting_applied.append("professional_framing")
        
        # Calculate reading time
        reading_time = self._estimate_reading_time(formatted_content, language)
        
        return FormattedResponse(
            content=formatted_content,
            language=language,
            response_type=response_type,
            formatting_applied=formatting_applied,
            cultural_adaptations=cultural_adaptations,
            estimated_reading_time=reading_time,
            formality_level=formality_level
        )
    
    def _clean_and_normalize(self, content: str) -> str:
        """Clean and normalize the content."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Normalize line breaks
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Fix common punctuation issues
        content = re.sub(r'\s+([.!?])', r'\1', content)
        content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
        
        return content
    
    def _apply_language_formatting(
        self, content: str, language: SupportedLanguage, rules: FormattingRules
    ) -> str:
        """Apply language-specific formatting rules."""
        
        if language == SupportedLanguage.JAPANESE:
            # Japanese-specific formatting
            content = self._format_japanese_text(content, rules)
        elif language == SupportedLanguage.GERMAN:
            # German-specific formatting
            content = self._format_german_text(content, rules)
        else:
            # English formatting (default)
            content = self._format_english_text(content, rules)
        
        return content
    
    def _format_japanese_text(self, content: str, rules: FormattingRules) -> str:
        """Apply Japanese-specific formatting."""
        # Ensure proper Japanese punctuation
        content = re.sub(r'\. ', '。', content)
        content = re.sub(r'\? ', '？', content)
        content = re.sub(r'! ', '！', content)
        content = re.sub(r'\.', '。', content)
        content = re.sub(r'\?', '？', content)
        content = re.sub(r'!', '！', content)
        
        # Format lists with Japanese bullet style
        content = re.sub(r'^- ', rules.bullet_style, content, flags=re.MULTILINE)
        
        # Ensure polite endings
        sentences = content.split('。')
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                if not any(ending in sentence for ending in ['です', 'ます', 'であります']):
                    if sentence.endswith('だ'):
                        sentence = sentence[:-1] + 'です'
                    elif not sentence.endswith(('です', 'ます')):
                        sentence += 'です'
                formatted_sentences.append(sentence)
        
        content = '。'.join(formatted_sentences)
        if content and not content.endswith('。'):
            content += '。'
        
        return content
    
    def _format_german_text(self, content: str, rules: FormattingRules) -> str:
        """Apply German-specific formatting."""
        # Capitalize nouns (basic implementation)
        # This is a simplified version - in practice, you'd use a proper German NLP library
        german_nouns = [
            'mitarbeiter', 'unternehmen', 'abteilung', 'fähigkeiten', 'leistung',
            'bewertung', 'entwicklung', 'team', 'projekt', 'aufgabe', 'ziel',
            'erfahrung', 'qualifikation', 'kompetenz', 'führung', 'management'
        ]
        
        for noun in german_nouns:
            # Replace lowercase version with capitalized version
            content = re.sub(rf'\b{noun}\b', noun.capitalize(), content, flags=re.IGNORECASE)
        
        # Format lists with German bullet style
        content = re.sub(r'^- ', rules.bullet_style, content, flags=re.MULTILINE)
        
        # Ensure proper German punctuation spacing
        content = re.sub(r'\\s+([,;:])', r'\\1', content)
        
        return content
    
    def _format_english_text(self, content: str, rules: FormattingRules) -> str:
        """Apply English-specific formatting."""
        # Format lists with English bullet style
        content = re.sub(r'^- ', rules.bullet_style, content, flags=re.MULTILINE)
        
        # Ensure proper capitalization after periods
        content = re.sub(r'(\.) +([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), content)
        
        # Format numbers in lists
        numbered_list_pattern = r'^(\\d+)\\. '
        content = re.sub(numbered_list_pattern, lambda m: rules.number_format.format(m.group(1)), content, flags=re.MULTILINE)
        
        return content
    
    def _apply_response_type_formatting(
        self, content: str, response_type: ResponseType, language: SupportedLanguage, rules: FormattingRules
    ) -> str:
        """Apply formatting specific to the response type."""
        
        if response_type == ResponseType.EMPLOYEE_LIST:
            content = self._format_employee_list(content, language, rules)
        elif response_type == ResponseType.SKILL_ANALYSIS:
            content = self._format_skill_analysis(content, language, rules)
        elif response_type == ResponseType.TEAM_RECOMMENDATION:
            content = self._format_team_recommendation(content, language, rules)
        elif response_type == ResponseType.PERFORMANCE_FEEDBACK:
            content = self._format_performance_feedback(content, language, rules)
        elif response_type == ResponseType.HIRING_GUIDANCE:
            content = self._format_hiring_guidance(content, language, rules)
        elif response_type == ResponseType.ERROR_MESSAGE:
            content = self._format_error_message(content, language, rules)
        elif response_type == ResponseType.GREETING:
            content = self._format_greeting(content, language, rules)
        
        return content
    
    def _format_employee_list(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format employee list responses."""
        # Add structured formatting for employee information
        if language == SupportedLanguage.JAPANESE:
            # Japanese employee list formatting
            content = re.sub(r'Name: ([^\\n]+)', r'名前: \\1', content)
            content = re.sub(r'Skills: ([^\\n]+)', r'スキル: \\1', content)
            content = re.sub(r'Department: ([^\\n]+)', r'部署: \\1', content)
        elif language == SupportedLanguage.GERMAN:
            # German employee list formatting
            content = re.sub(r'Name: ([^\\n]+)', r'Name: \\1', content)
            content = re.sub(r'Skills: ([^\\n]+)', r'Fähigkeiten: \\1', content)
            content = re.sub(r'Department: ([^\\n]+)', r'Abteilung: \\1', content)
        
        return content
    
    def _format_skill_analysis(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format skill analysis responses."""
        # Add structured formatting for skill information
        if language == SupportedLanguage.JAPANESE:
            content = re.sub(r'Skill Level: ([^\\n]+)', r'スキルレベル: \\1', content)
            content = re.sub(r'Experience: ([^\\n]+)', r'経験: \\1', content)
        elif language == SupportedLanguage.GERMAN:
            content = re.sub(r'Skill Level: ([^\\n]+)', r'Fähigkeitslevel: \\1', content)
            content = re.sub(r'Experience: ([^\\n]+)', r'Erfahrung: \\1', content)
        
        return content
    
    def _format_team_recommendation(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format team recommendation responses."""
        # Add structured formatting for team information
        if language == SupportedLanguage.JAPANESE:
            content = re.sub(r'Team Size: ([^\\n]+)', r'チームサイズ: \\1', content)
            content = re.sub(r'Roles: ([^\\n]+)', r'役割: \\1', content)
        elif language == SupportedLanguage.GERMAN:
            content = re.sub(r'Team Size: ([^\\n]+)', r'Teamgröße: \\1', content)
            content = re.sub(r'Roles: ([^\\n]+)', r'Rollen: \\1', content)
        
        return content
    
    def _format_performance_feedback(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format performance feedback responses."""
        # Add structured formatting for performance information
        if language == SupportedLanguage.JAPANESE:
            content = re.sub(r'Strengths: ([^\\n]+)', r'強み: \\1', content)
            content = re.sub(r'Areas for Improvement: ([^\\n]+)', r'改善点: \\1', content)
        elif language == SupportedLanguage.GERMAN:
            content = re.sub(r'Strengths: ([^\\n]+)', r'Stärken: \\1', content)
            content = re.sub(r'Areas for Improvement: ([^\\n]+)', r'Verbesserungsbereiche: \\1', content)
        
        return content
    
    def _format_hiring_guidance(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format hiring guidance responses."""
        # Add structured formatting for hiring information
        if language == SupportedLanguage.JAPANESE:
            content = re.sub(r'Requirements: ([^\\n]+)', r'要件: \\1', content)
            content = re.sub(r'Interview Questions: ([^\\n]+)', r'面接質問: \\1', content)
        elif language == SupportedLanguage.GERMAN:
            content = re.sub(r'Requirements: ([^\\n]+)', r'Anforderungen: \\1', content)
            content = re.sub(r'Interview Questions: ([^\\n]+)', r'Interviewfragen: \\1', content)
        
        return content
    
    def _format_error_message(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format error messages."""
        # Make error messages more polite and professional
        if language == SupportedLanguage.JAPANESE:
            if not content.startswith('申し訳'):
                content = f"申し訳ございませんが、{content}"
        elif language == SupportedLanguage.GERMAN:
            if not content.startswith('Entschuldigung'):
                content = f"Entschuldigung, {content}"
        else:
            if not content.startswith('I apologize'):
                content = f"I apologize, but {content}"
        
        return content
    
    def _format_greeting(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Format greeting responses."""
        # Ensure greetings are appropriately formal
        if language == SupportedLanguage.JAPANESE:
            if not any(greeting in content for greeting in ['こんにちは', 'おはようございます', 'こんばんは']):
                content = f"こんにちは。{content}"
        elif language == SupportedLanguage.GERMAN:
            if not any(greeting in content for greeting in ['Guten Tag', 'Hallo', 'Guten Morgen']):
                content = f"Guten Tag! {content}"
        else:
            if not any(greeting in content for greeting in ['Hello', 'Hi', 'Good morning']):
                content = f"Hello! {content}"
        
        return content
    
    def _apply_cultural_adaptations(
        self, content: str, cultural_context: CulturalContext, formality_level: str, rules: FormattingRules
    ) -> Tuple[str, List[str]]:
        """Apply cultural adaptations to the content."""
        adaptations = []
        
        # Apply formality level adaptations
        if cultural_context.formality_level == "formal":
            content = self._make_more_formal(content, cultural_context.language, rules)
            adaptations.append("formal_language")
        
        # Apply communication style adaptations
        if cultural_context.language == SupportedLanguage.JAPANESE:
            # Japanese cultural adaptations
            if "harmony" in cultural_context.response_structure or "indirect" in cultural_context.response_structure:
                content = self._make_more_indirect(content)
                adaptations.append("indirect_communication")
            
            # Add group harmony considerations
            content = self._add_group_harmony_language(content)
            adaptations.append("group_harmony")
        
        elif cultural_context.language == SupportedLanguage.GERMAN:
            # German cultural adaptations
            if "thorough" in cultural_context.response_structure:
                content = self._make_more_thorough(content)
                adaptations.append("thorough_explanation")
            
            # Add systematic structure
            content = self._add_systematic_structure(content)
            adaptations.append("systematic_structure")
        
        return content, adaptations
    
    def _make_more_formal(self, content: str, language: SupportedLanguage, rules: FormattingRules) -> str:
        """Make content more formal."""
        if language == SupportedLanguage.GERMAN:
            # Use formal address
            content = content.replace("du", "Sie").replace("dich", "Sie").replace("dir", "Ihnen")
        elif language == SupportedLanguage.JAPANESE:
            # Ensure keigo (honorific language) is used
            content = re.sub(r'する', 'いたします', content)
            content = re.sub(r'です', 'でございます', content)
        
        return content
    
    def _make_more_indirect(self, content: str) -> str:
        """Make content more indirect (Japanese style)."""
        # Add softening expressions
        content = re.sub(r'should', 'might want to', content)
        content = re.sub(r'must', 'could consider', content)
        content = re.sub(r'need to', 'might consider', content)
        content = re.sub(r'was below expectations', 'might have room for improvement', content)
        content = re.sub(r'failed to', 'could perhaps', content)
        content = re.sub(r'did not', 'might not have', content)
        
        # Add Japanese softening if content contains Japanese
        if any(ord(char) > 0x3000 for char in content):
            content = re.sub(r'必要です', '必要かもしれません', content)
            content = re.sub(r'してください', 'していただけませんでしょうか', content)
        else:
            # For English content, add softening phrases
            content = re.sub(r'You should', 'You might want to consider', content)
            content = re.sub(r'improve', 'perhaps improve', content)
            content = re.sub(r'Your performance', 'Your performance perhaps', content)
        
        return content
    
    def _add_group_harmony_language(self, content: str) -> str:
        """Add language that emphasizes group harmony."""
        # Add phrases that emphasize collective benefit
        content = re.sub(r'あなた', 'チーム全体', content)
        content = re.sub(r'個人的に', 'チームとして', content)
        
        return content
    
    def _make_more_thorough(self, content: str) -> str:
        """Make content more thorough (German style)."""
        # Add detailed explanations
        content = re.sub(r'(\\.)\\s', r'\\1 Darüber hinaus ', content)
        
        return content
    
    def _add_systematic_structure(self, content: str) -> str:
        """Add systematic structure to content."""
        # Add numbered points if not already present
        if not re.search(r'^\\d+\\.', content, re.MULTILINE):
            lines = content.split('\n')
            structured_lines = []
            counter = 1
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('•', '-', '1.', '2.')):
                    structured_lines.append(f"{counter}. {line}")
                    counter += 1
                else:
                    structured_lines.append(line)
            
            content = '\n'.join(structured_lines)
        
        return content
    
    def _apply_formality_level(
        self, content: str, formality_level: str, language: SupportedLanguage, rules: FormattingRules
    ) -> str:
        """Apply formality level adjustments."""
        if formality_level == "formal":
            # Add formal prefixes and suffixes
            if rules.politeness_prefix and not content.startswith(rules.politeness_prefix):
                content = f"{rules.politeness_prefix} {content}"
            
            if rules.politeness_suffix and not content.endswith(rules.politeness_suffix):
                content = f"{content} {rules.politeness_suffix}"
        
        return content
    
    def _add_professional_framing(
        self, content: str, response_type: ResponseType, language: SupportedLanguage, formality_level: str
    ) -> str:
        """Add professional framing to the response."""
        phrases = self.professional_phrases[language]
        
        # Add appropriate opening based on response type
        if response_type == ResponseType.EMPLOYEE_LIST:
            opening = phrases["employee_search_opening"]
        elif response_type == ResponseType.SKILL_ANALYSIS:
            opening = phrases["analysis_opening"]
        elif response_type == ResponseType.PERFORMANCE_FEEDBACK:
            opening = phrases["feedback_opening"]
        else:
            opening = phrases["general_opening"]
        
        # Add opening if not already present
        if not any(phrase in content[:50] for phrase in phrases.values()):
            content = f"{opening} {content}"
        
        # Add professional closing
        closing = phrases["professional_closing"]
        if not content.endswith(closing) and formality_level in ["business", "formal"]:
            content = f"{content}\n\n{closing}"
        
        return content
    
    def _estimate_reading_time(self, content: str, language: SupportedLanguage) -> int:
        """Estimate reading time in seconds."""
        # Average reading speeds (words per minute)
        reading_speeds = {
            SupportedLanguage.ENGLISH: 200,
            SupportedLanguage.GERMAN: 180,
            SupportedLanguage.JAPANESE: 150  # Slower due to character complexity
        }
        
        # Count words (approximate for Japanese)
        if language == SupportedLanguage.JAPANESE:
            # For Japanese, count characters and divide by average characters per "word"
            char_count = len(re.sub(r'\\s+', '', content))
            word_count = char_count / 2  # Rough approximation
        else:
            word_count = len(content.split())
        
        speed = reading_speeds[language]
        reading_time_minutes = word_count / speed
        return max(int(reading_time_minutes * 60), 5)  # Minimum 5 seconds
    
    def _initialize_formatting_rules(self) -> Dict[SupportedLanguage, FormattingRules]:
        """Initialize formatting rules for each language."""
        return {
            SupportedLanguage.ENGLISH: FormattingRules(
                bullet_style="• ",
                number_format="{}. ",
                section_separator="\\n\\n",
                emphasis_markers=("**", "**"),
                politeness_prefix="",
                politeness_suffix="",
                date_format="%B %d, %Y",
                list_connector=" and ",
                formal_address=""
            ),
            SupportedLanguage.GERMAN: FormattingRules(
                bullet_style="• ",
                number_format="{}. ",
                section_separator="\\n\\n",
                emphasis_markers=("**", "**"),
                politeness_prefix="",
                politeness_suffix="Mit freundlichen Grüßen",
                date_format="%d. %B %Y",
                list_connector=" und ",
                formal_address="Sie"
            ),
            SupportedLanguage.JAPANESE: FormattingRules(
                bullet_style="・",
                number_format="{}. ",
                section_separator="\\n\\n",
                emphasis_markers=("", ""),
                politeness_prefix="",
                politeness_suffix="どうぞよろしくお願いいたします。",
                date_format="%Y年%m月%d日",
                list_connector="と",
                formal_address="さん"
            )
        }
    
    def _initialize_cultural_templates(self) -> Dict[SupportedLanguage, Dict[str, str]]:
        """Initialize cultural templates for different contexts."""
        return {
            SupportedLanguage.ENGLISH: {
                "business_opening": "Thank you for your inquiry.",
                "formal_closing": "Please let me know if you need any additional information.",
                "error_acknowledgment": "I apologize for any inconvenience."
            },
            SupportedLanguage.GERMAN: {
                "business_opening": "Vielen Dank für Ihre Anfrage.",
                "formal_closing": "Bitte lassen Sie mich wissen, wenn Sie weitere Informationen benötigen.",
                "error_acknowledgment": "Ich entschuldige mich für etwaige Unannehmlichkeiten."
            },
            SupportedLanguage.JAPANESE: {
                "business_opening": "お問い合わせいただき、ありがとうございます。",
                "formal_closing": "ご不明な点がございましたら、お気軽にお尋ねください。",
                "error_acknowledgment": "ご迷惑をおかけして申し訳ございません。"
            }
        }
    
    def _initialize_professional_phrases(self) -> Dict[SupportedLanguage, Dict[str, str]]:
        """Initialize professional phrases for different languages."""
        return {
            SupportedLanguage.ENGLISH: {
                "employee_search_opening": "Based on your search criteria, I found the following employees:",
                "analysis_opening": "Here is my analysis of the situation:",
                "feedback_opening": "I'd like to provide the following feedback:",
                "general_opening": "I'm happy to help you with this request.",
                "professional_closing": "Please let me know if you need any additional assistance."
            },
            SupportedLanguage.GERMAN: {
                "employee_search_opening": "Basierend auf Ihren Suchkriterien habe ich folgende Mitarbeiter gefunden:",
                "analysis_opening": "Hier ist meine Analyse der Situation:",
                "feedback_opening": "Ich möchte Ihnen folgendes Feedback geben:",
                "general_opening": "Gerne helfe ich Ihnen bei dieser Anfrage.",
                "professional_closing": "Bitte lassen Sie mich wissen, wenn Sie weitere Unterstützung benötigen."
            },
            SupportedLanguage.JAPANESE: {
                "employee_search_opening": "検索条件に基づいて、以下の従業員を見つけました：",
                "analysis_opening": "状況について以下のように分析いたします：",
                "feedback_opening": "以下のフィードバックをお伝えいたします：",
                "general_opening": "このご要望についてお手伝いさせていただきます。",
                "professional_closing": "ご不明な点がございましたら、お気軽にお申し付けください。"
            }
        }
    
    def get_formatting_statistics(self) -> Dict[str, Any]:
        """Get statistics about formatting capabilities."""
        return {
            "supported_languages": len(self.formatting_rules),
            "response_types": len(ResponseType),
            "languages": [lang.value for lang in self.formatting_rules.keys()],
            "response_types_list": [rt.value for rt in ResponseType],
            "cultural_templates": len(self.cultural_templates),
            "professional_phrases": len(self.professional_phrases)
        }
    
    def validate_formatting_rules(self, language: SupportedLanguage) -> bool:
        """Validate that formatting rules exist for a language."""
        try:
            rules = self.formatting_rules[language]
            required_fields = [
                'bullet_style', 'number_format', 'section_separator',
                'emphasis_markers', 'date_format', 'list_connector'
            ]
            
            for field in required_fields:
                if not hasattr(rules, field):
                    return False
            
            return True
        except KeyError:
            return False