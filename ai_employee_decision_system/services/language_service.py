"""
Language detection and processing service for multilingual AI capabilities.

This module provides language detection, text processing, and cultural context
for Japanese, German, and English languages in HR contexts.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SupportedLanguage(Enum):
    """Supported languages."""
    ENGLISH = "en"
    GERMAN = "de"
    JAPANESE = "ja"


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""
    language: SupportedLanguage
    confidence: float
    detected_features: List[str]
    fallback_used: bool


@dataclass
class CulturalContext:
    """Cultural context for language-specific responses."""
    language: SupportedLanguage
    formality_level: str  # "formal", "casual", "business"
    greeting_style: str
    response_structure: str
    cultural_notes: List[str]


class LanguageDetector:
    """Advanced language detection for HR contexts."""
    
    # Language-specific patterns and features
    LANGUAGE_PATTERNS = {
        SupportedLanguage.JAPANESE: {
            'hiragana': r'[\u3040-\u309F]',
            'katakana': r'[\u30A0-\u30FF]',
            'kanji': r'[\u4E00-\u9FAF]',
            'japanese_punctuation': r'[。、！？]',
            'common_words': [
                'です', 'である', 'ます', 'だ', 'の', 'に', 'を', 'は', 'が', 'と',
                '人事', '従業員', '会社', '仕事', '管理', '評価', '採用', '研修'
            ],
            'hr_terms': [
                '人事管理', '従業員評価', '採用活動', '人材開発', '労務管理',
                '給与', '昇進', '転職', '面接', '履歴書', 'スキル', 'チーム'
            ]
        },
        SupportedLanguage.GERMAN: {
            'umlauts': r'[äöüÄÖÜß]',
            'compound_words': r'\b\w{10,}\b',  # German loves compound words
            'common_words': [
                'der', 'die', 'das', 'und', 'ist', 'zu', 'ein', 'eine', 'mit', 'von',
                'auf', 'für', 'als', 'wird', 'werden', 'haben', 'hat', 'sind', 'war'
            ],
            'hr_terms': [
                'Personalwesen', 'Mitarbeiter', 'Bewerbung', 'Einstellung', 'Kündigung',
                'Gehalt', 'Beförderung', 'Ausbildung', 'Führung', 'Team', 'Fähigkeiten',
                'Leistung', 'Bewertung', 'Unternehmen', 'Arbeitsplatz', 'Vorstellungsgespräch'
            ],
            'formal_indicators': ['Sie', 'Ihnen', 'Ihrer', 'sehr geehrte', 'mit freundlichen Grüßen']
        },
        SupportedLanguage.ENGLISH: {
            'common_words': [
                'the', 'and', 'is', 'to', 'a', 'an', 'of', 'in', 'for', 'with',
                'on', 'at', 'by', 'from', 'as', 'are', 'was', 'will', 'have', 'has'
            ],
            'hr_terms': [
                'employee', 'management', 'hiring', 'recruitment', 'performance',
                'evaluation', 'skills', 'team', 'leadership', 'training', 'development',
                'salary', 'promotion', 'interview', 'resume', 'cv', 'human resources'
            ],
            'contractions': r"\b\w+'\w+\b"  # can't, won't, it's, etc.
        }
    }
    
    def __init__(self):
        """Initialize the language detector."""
        self.logger = logging.getLogger(__name__)
        self.detection_cache = {}  # Simple cache for repeated queries
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            LanguageDetectionResult with detected language and confidence
        """
        if not text or not text.strip():
            return LanguageDetectionResult(
                language=SupportedLanguage.ENGLISH,
                confidence=0.5,
                detected_features=["empty_text"],
                fallback_used=True
            )
        
        # Check cache first
        text_key = text.strip().lower()[:100]  # Use first 100 chars as key
        if text_key in self.detection_cache:
            return self.detection_cache[text_key]
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Handle special case for whitespace-only text after cleaning
        if not cleaned_text.strip():
            return LanguageDetectionResult(
                language=SupportedLanguage.ENGLISH,
                confidence=0.5,
                detected_features=["empty_text"],
                fallback_used=True
            )
        
        # Calculate scores for each language
        scores = {}
        features = {}
        
        for language in SupportedLanguage:
            score, detected_features = self._calculate_language_score(cleaned_text, language)
            scores[language] = score
            features[language] = detected_features
        
        # Determine best match
        best_language = max(scores.keys(), key=lambda x: scores[x])
        best_score = scores[best_language]
        
        # Apply confidence thresholds and normalize scores
        confidence = min(best_score / 30.0, 1.0)  # Adjusted threshold for better detection
        fallback_used = confidence < 0.3  # More lenient fallback threshold
        
        # If confidence is too low, default to English
        if fallback_used and best_score < 5:  # Only fallback if score is very low
            best_language = SupportedLanguage.ENGLISH
            confidence = 0.5
        
        result = LanguageDetectionResult(
            language=best_language,
            confidence=confidence,
            detected_features=features[best_language],
            fallback_used=fallback_used
        )
        
        # Cache the result
        self.detection_cache[text_key] = result
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs and email addresses
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!?]{2,}', '!', text)
        
        return text
    
    def _calculate_language_score(self, text: str, language: SupportedLanguage) -> Tuple[float, List[str]]:
        """Calculate language score based on various features."""
        patterns = self.LANGUAGE_PATTERNS[language]
        score = 0.0
        detected_features = []
        
        text_lower = text.lower()
        
        if language == SupportedLanguage.JAPANESE:
            # Check for Japanese scripts
            if re.search(patterns['hiragana'], text):
                score += 40
                detected_features.append('hiragana')
            
            if re.search(patterns['katakana'], text):
                score += 35
                detected_features.append('katakana')
            
            if re.search(patterns['kanji'], text):
                score += 45
                detected_features.append('kanji')
            
            if re.search(patterns['japanese_punctuation'], text):
                score += 10
                detected_features.append('japanese_punctuation')
            
            # Check for common Japanese words
            japanese_word_count = sum(1 for word in patterns['common_words'] if word in text_lower)
            score += japanese_word_count * 5
            if japanese_word_count > 0:
                detected_features.append(f'common_words_{japanese_word_count}')
            
            # Check for HR-specific terms
            hr_term_count = sum(1 for term in patterns['hr_terms'] if term in text)
            score += hr_term_count * 8
            if hr_term_count > 0:
                detected_features.append(f'hr_terms_{hr_term_count}')
        
        elif language == SupportedLanguage.GERMAN:
            # Check for German-specific characters
            if re.search(patterns['umlauts'], text):
                score += 30
                detected_features.append('umlauts')
            
            # Check for compound words (German characteristic)
            compound_matches = re.findall(patterns['compound_words'], text)
            if compound_matches:
                score += len(compound_matches) * 5
                detected_features.append(f'compound_words_{len(compound_matches)}')
            
            # Check for common German words
            german_word_count = sum(1 for word in patterns['common_words'] 
                                  if f' {word} ' in f' {text_lower} ' or text_lower.startswith(word + ' ') or text_lower.endswith(' ' + word))
            score += german_word_count * 4
            if german_word_count > 0:
                detected_features.append(f'common_words_{german_word_count}')
            
            # Check for HR-specific terms
            hr_term_count = sum(1 for term in patterns['hr_terms'] if term.lower() in text_lower)
            score += hr_term_count * 8
            if hr_term_count > 0:
                detected_features.append(f'hr_terms_{hr_term_count}')
            
            # Check for formal indicators
            formal_count = sum(1 for indicator in patterns['formal_indicators'] 
                             if indicator.lower() in text_lower)
            if formal_count > 0:
                score += formal_count * 5
                detected_features.append(f'formal_indicators_{formal_count}')
        
        elif language == SupportedLanguage.ENGLISH:
            # Check for English contractions
            if re.search(patterns['contractions'], text):
                score += 15
                detected_features.append('contractions')
            
            # Check for common English words
            english_word_count = sum(1 for word in patterns['common_words'] 
                                   if f' {word} ' in f' {text_lower} ' or text_lower.startswith(word + ' ') or text_lower.endswith(' ' + word))
            score += english_word_count * 3
            if english_word_count > 0:
                detected_features.append(f'common_words_{english_word_count}')
            
            # Check for HR-specific terms
            hr_term_count = sum(1 for term in patterns['hr_terms'] if term in text_lower)
            score += hr_term_count * 6
            if hr_term_count > 0:
                detected_features.append(f'hr_terms_{hr_term_count}')
            
            # Bonus for ASCII-only text (common in English)
            if text.isascii():
                score += 10
                detected_features.append('ascii_only')
        
        return score, detected_features
    
    def get_language_info(self, language: SupportedLanguage) -> Dict[str, Any]:
        """Get detailed information about a language."""
        language_info = {
            SupportedLanguage.ENGLISH: {
                'name': 'English',
                'native_name': 'English',
                'code': 'en',
                'direction': 'ltr',
                'script': 'Latin',
                'formality_levels': ['casual', 'business', 'formal'],
                'cultural_context': 'Direct communication, individual focus'
            },
            SupportedLanguage.GERMAN: {
                'name': 'German',
                'native_name': 'Deutsch',
                'code': 'de',
                'direction': 'ltr',
                'script': 'Latin',
                'formality_levels': ['Du', 'Sie'],
                'cultural_context': 'Formal business culture, hierarchical, detailed'
            },
            SupportedLanguage.JAPANESE: {
                'name': 'Japanese',
                'native_name': '日本語',
                'code': 'ja',
                'direction': 'ltr',
                'script': 'Hiragana, Katakana, Kanji',
                'formality_levels': ['casual', 'polite', 'honorific'],
                'cultural_context': 'Hierarchical, group harmony, indirect communication'
            }
        }
        
        return language_info.get(language, {})


class CulturalContextProvider:
    """Provides cultural context for different languages in HR settings."""
    
    CULTURAL_CONTEXTS = {
        SupportedLanguage.ENGLISH: CulturalContext(
            language=SupportedLanguage.ENGLISH,
            formality_level="business",
            greeting_style="direct",
            response_structure="problem-solution-action",
            cultural_notes=[
                "Direct communication is preferred",
                "Individual achievements are highlighted",
                "Time-efficient responses valued",
                "Casual but professional tone acceptable"
            ]
        ),
        SupportedLanguage.GERMAN: CulturalContext(
            language=SupportedLanguage.GERMAN,
            formality_level="formal",
            greeting_style="respectful",
            response_structure="thorough-detailed-systematic",
            cultural_notes=[
                "Formal address (Sie) in business contexts",
                "Detailed, thorough explanations expected",
                "Punctuality and precision highly valued",
                "Hierarchical respect important",
                "Direct but polite communication"
            ]
        ),
        SupportedLanguage.JAPANESE: CulturalContext(
            language=SupportedLanguage.JAPANESE,
            formality_level="polite",
            greeting_style="respectful",
            response_structure="context-harmony-consensus",
            cultural_notes=[
                "Polite forms (です/ます) in business",
                "Group harmony over individual needs",
                "Indirect communication preferred",
                "Respect for hierarchy and seniority",
                "Consensus-building approach",
                "Avoid direct confrontation"
            ]
        )
    }
    
    def get_cultural_context(self, language: SupportedLanguage) -> CulturalContext:
        """Get cultural context for a language."""
        return self.CULTURAL_CONTEXTS.get(language, self.CULTURAL_CONTEXTS[SupportedLanguage.ENGLISH])
    
    def format_hr_response(self, content: str, language: SupportedLanguage, query_type: str = "general") -> str:
        """Format HR response according to cultural context."""
        context = self.get_cultural_context(language)
        
        if language == SupportedLanguage.GERMAN:
            return self._format_german_response(content, context, query_type)
        elif language == SupportedLanguage.JAPANESE:
            return self._format_japanese_response(content, context, query_type)
        else:
            return self._format_english_response(content, context, query_type)
    
    def _format_english_response(self, content: str, context: CulturalContext, query_type: str) -> str:
        """Format response for English speakers."""
        # Add professional greeting if needed
        if query_type in ["greeting", "introduction"]:
            content = f"Hello! {content}"
        
        # Ensure clear, direct structure
        if not content.endswith(('.', '!', '?')):
            content += "."
        
        return content
    
    def _format_german_response(self, content: str, context: CulturalContext, query_type: str) -> str:
        """Format response for German speakers."""
        # Add formal greeting
        if query_type in ["greeting", "introduction"]:
            content = f"Guten Tag! {content}"
        
        # Ensure formal structure
        if not content.endswith(('.', '!', '?')):
            content += "."
        
        # Add polite closing for longer responses
        if len(content) > 200:
            content += " Ich hoffe, das hilft Ihnen weiter."
        
        return content
    
    def _format_japanese_response(self, content: str, context: CulturalContext, query_type: str) -> str:
        """Format response for Japanese speakers."""
        # Add polite greeting
        if query_type in ["greeting", "introduction"]:
            content = f"こんにちは。{content}"
        
        # Ensure polite ending
        if not content.endswith(('。', '！', '？', 'ます。', 'です。')):
            if content.endswith(('.', '!', '?')):
                content = content[:-1] + "。"
            else:
                content += "。"
        
        # Add polite closing for longer responses
        if len(content) > 100:  # Shorter threshold for Japanese
            content += "どうぞよろしくお願いいたします。"
        
        return content


class LanguageService:
    """Main language service combining detection and cultural context."""
    
    def __init__(self):
        """Initialize the language service."""
        self.detector = LanguageDetector()
        self.cultural_provider = CulturalContextProvider()
        self.logger = logging.getLogger(__name__)
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect language of input text."""
        return self.detector.detect_language(text)
    
    def get_cultural_context(self, language: SupportedLanguage) -> CulturalContext:
        """Get cultural context for a language."""
        return self.cultural_provider.get_cultural_context(language)
    
    def format_response(self, content: str, language: SupportedLanguage, query_type: str = "general") -> str:
        """Format response according to language and cultural context."""
        return self.cultural_provider.format_hr_response(content, language, query_type)
    
    def is_supported_language(self, language_code: str) -> bool:
        """Check if a language is supported."""
        try:
            SupportedLanguage(language_code)
            return True
        except ValueError:
            return False
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages."""
        languages = []
        for lang in SupportedLanguage:
            info = self.detector.get_language_info(lang)
            languages.append({
                'code': lang.value,
                'name': info.get('name', lang.value),
                'native_name': info.get('native_name', lang.value)
            })
        return languages
    
    def translate_hr_terms(self, terms: List[str], target_language: SupportedLanguage) -> Dict[str, str]:
        """Translate common HR terms to target language."""
        # Basic HR term translations
        translations = {
            SupportedLanguage.GERMAN: {
                'employee': 'Mitarbeiter',
                'manager': 'Manager',
                'team': 'Team',
                'skills': 'Fähigkeiten',
                'performance': 'Leistung',
                'evaluation': 'Bewertung',
                'training': 'Ausbildung',
                'development': 'Entwicklung',
                'recruitment': 'Rekrutierung',
                'interview': 'Vorstellungsgespräch',
                'salary': 'Gehalt',
                'promotion': 'Beförderung',
                'department': 'Abteilung',
                'company': 'Unternehmen',
                'position': 'Position'
            },
            SupportedLanguage.JAPANESE: {
                'employee': '従業員',
                'manager': 'マネージャー',
                'team': 'チーム',
                'skills': 'スキル',
                'performance': '成果',
                'evaluation': '評価',
                'training': '研修',
                'development': '開発',
                'recruitment': '採用',
                'interview': '面接',
                'salary': '給与',
                'promotion': '昇進',
                'department': '部署',
                'company': '会社',
                'position': 'ポジション'
            }
        }
        
        if target_language == SupportedLanguage.ENGLISH:
            return {term: term for term in terms}  # No translation needed
        
        lang_translations = translations.get(target_language, {})
        return {term: lang_translations.get(term.lower(), term) for term in terms}
    
    def get_language_templates(self, language: SupportedLanguage) -> Dict[str, str]:
        """Get language-specific templates for common HR responses."""
        templates = {
            SupportedLanguage.ENGLISH: {
                'greeting': "Hello! How can I help you with HR matters today?",
                'employee_search': "I found {count} employees matching your criteria:",
                'no_results': "I couldn't find any employees matching those criteria.",
                'error': "I'm sorry, I encountered an error. Please try again.",
                'help': "I can help you with employee management, skills assessment, team building, and HR queries."
            },
            SupportedLanguage.GERMAN: {
                'greeting': "Guten Tag! Wie kann ich Ihnen heute bei HR-Angelegenheiten helfen?",
                'employee_search': "Ich habe {count} Mitarbeiter gefunden, die Ihren Kriterien entsprechen:",
                'no_results': "Ich konnte keine Mitarbeiter finden, die diesen Kriterien entsprechen.",
                'error': "Entschuldigung, es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.",
                'help': "Ich kann Ihnen bei Mitarbeiterverwaltung, Fähigkeitsbewertung, Teambildung und HR-Anfragen helfen."
            },
            SupportedLanguage.JAPANESE: {
                'greeting': "こんにちは！本日は人事に関してどのようなお手伝いができますでしょうか？",
                'employee_search': "条件に一致する従業員を{count}名見つけました：",
                'no_results': "その条件に一致する従業員は見つかりませんでした。",
                'error': "申し訳ございませんが、エラーが発生しました。もう一度お試しください。",
                'help': "従業員管理、スキル評価、チーム構築、人事に関するお問い合わせをお手伝いできます。"
            }
        }
        
        return templates.get(language, templates[SupportedLanguage.ENGLISH])