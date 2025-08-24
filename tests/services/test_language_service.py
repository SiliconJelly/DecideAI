#!/usr/bin/env python3
"""
Unit tests for the Language Service.

This test suite validates the language detection, cultural context,
and multilingual processing capabilities.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai_employee_decision_system.services.language_service import (
    LanguageService, LanguageDetector, CulturalContextProvider,
    SupportedLanguage, LanguageDetectionResult, CulturalContext
)


class TestLanguageDetector(unittest.TestCase):
    """Test cases for the LanguageDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = LanguageDetector()
    
    def test_detect_english(self):
        """Test English language detection."""
        test_cases = [
            "How can I improve employee performance?",
            "I need help with hiring new team members.",
            "What are the best practices for performance reviews?",
            "Can you help me find employees with Python skills?"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = self.detector.detect_language(text)
                self.assertEqual(result.language, SupportedLanguage.ENGLISH)
                self.assertGreaterEqual(result.confidence, 0.5)
                self.assertFalse(result.fallback_used)
                # Should detect some English features (common words, HR terms, or ASCII)
                features_str = str(result.detected_features)
                self.assertTrue(any(feature in features_str for feature in ['common_words', 'hr_terms', 'ascii_only']))
    
    def test_detect_german(self):
        """Test German language detection."""
        test_cases = [
            "Wie kann ich die Mitarbeiterleistung verbessern?",
            "Ich brauche Hilfe bei der Einstellung neuer Teammitglieder.",
            "Was sind die besten Praktiken für Leistungsbeurteilungen?",
            "Können Sie mir helfen, Mitarbeiter mit Python-Fähigkeiten zu finden?"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = self.detector.detect_language(text)
                self.assertEqual(result.language, SupportedLanguage.GERMAN)
                self.assertGreater(result.confidence, 0.4)
                self.assertIn('common_words', str(result.detected_features))
    
    def test_detect_japanese(self):
        """Test Japanese language detection."""
        test_cases = [
            "従業員のパフォーマンスを向上させるにはどうすればよいですか？",
            "新しいチームメンバーの採用を手伝ってください。",
            "パフォーマンスレビューのベストプラクティスは何ですか？",
            "Pythonスキルを持つ従業員を見つけるのを手伝ってもらえますか？"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                result = self.detector.detect_language(text)
                self.assertEqual(result.language, SupportedLanguage.JAPANESE)
                self.assertGreater(result.confidence, 0.5)
                self.assertTrue(any(feature in ['hiragana', 'katakana', 'kanji'] 
                                 for feature in result.detected_features))
    
    def test_detect_empty_text(self):
        """Test detection with empty or whitespace text."""
        test_cases = ["", "   ", "\n\t  \n"]
        
        for text in test_cases:
            with self.subTest(text=repr(text)):
                result = self.detector.detect_language(text)
                self.assertEqual(result.language, SupportedLanguage.ENGLISH)
                self.assertEqual(result.confidence, 0.5)
                self.assertTrue(result.fallback_used)
                self.assertIn("empty_text", result.detected_features)
    
    def test_detect_mixed_language(self):
        """Test detection with mixed language content."""
        mixed_texts = [
            "Hello, wie geht es dir?",  # English-German
            "こんにちは, how are you?",  # Japanese-English
            "Guten Tag, 元気ですか？"    # German-Japanese
        ]
        
        for text in mixed_texts:
            with self.subTest(text=text):
                result = self.detector.detect_language(text)
                # Should detect one of the languages with reasonable confidence
                self.assertIn(result.language, [SupportedLanguage.ENGLISH, 
                                              SupportedLanguage.GERMAN, 
                                              SupportedLanguage.JAPANESE])
                self.assertGreaterEqual(result.confidence, 0.2)
    
    def test_hr_specific_terms(self):
        """Test detection accuracy with HR-specific terms."""
        hr_texts = {
            SupportedLanguage.ENGLISH: [
                "We need to conduct performance evaluations for all employees.",
                "The recruitment process for the new position is starting.",
                "Team leadership skills are essential for this role."
            ],
            SupportedLanguage.GERMAN: [
                "Wir müssen Leistungsbeurteilungen für alle Mitarbeiter durchführen.",
                "Der Rekrutierungsprozess für die neue Position beginnt.",
                "Teamführungsfähigkeiten sind für diese Rolle unerlässlich."
            ],
            SupportedLanguage.JAPANESE: [
                "すべての従業員に対してパフォーマンス評価を実施する必要があります。",
                "新しいポジションの採用プロセスが始まっています。",
                "チームリーダーシップスキルはこの役割に不可欠です。"
            ]
        }
        
        for expected_lang, texts in hr_texts.items():
            for text in texts:
                with self.subTest(language=expected_lang.value, text=text[:30]):
                    result = self.detector.detect_language(text)
                    self.assertEqual(result.language, expected_lang)
                    self.assertGreaterEqual(result.confidence, 0.4)
                    # HR terms detection is optional but should work for most cases
    
    def test_confidence_scoring(self):
        """Test confidence scoring accuracy."""
        # High confidence cases
        high_confidence_texts = [
            ("This is a clear English sentence with common words.", SupportedLanguage.ENGLISH),
            ("Das ist ein klarer deutscher Satz mit häufigen Wörtern.", SupportedLanguage.GERMAN),
            ("これは一般的な単語を含む明確な日本語の文です。", SupportedLanguage.JAPANESE)
        ]
        
        for text, expected_lang in high_confidence_texts:
            with self.subTest(text=text[:30]):
                result = self.detector.detect_language(text)
                self.assertEqual(result.language, expected_lang)
                self.assertGreaterEqual(result.confidence, 0.6)
                self.assertFalse(result.fallback_used)
        
        # Low confidence cases (ambiguous or short text)
        low_confidence_texts = [
            "OK",
            "123",
            "???",
            "a"
        ]
        
        for text in low_confidence_texts:
            with self.subTest(text=text):
                result = self.detector.detect_language(text)
                # Should still return a result, but with lower confidence or fallback
                self.assertIsInstance(result.language, SupportedLanguage)
                self.assertTrue(result.confidence <= 0.8 or result.fallback_used)
    
    def test_caching(self):
        """Test that language detection results are cached."""
        text = "This is a test sentence for caching."
        
        # First call
        result1 = self.detector.detect_language(text)
        
        # Second call should use cache
        result2 = self.detector.detect_language(text)
        
        # Results should be identical
        self.assertEqual(result1.language, result2.language)
        self.assertEqual(result1.confidence, result2.confidence)
        self.assertEqual(result1.detected_features, result2.detected_features)
        
        # Check that cache is being used
        self.assertIn(text.strip().lower()[:100], self.detector.detection_cache)
    
    def test_get_language_info(self):
        """Test language information retrieval."""
        for language in SupportedLanguage:
            with self.subTest(language=language):
                info = self.detector.get_language_info(language)
                self.assertIsInstance(info, dict)
                self.assertIn('name', info)
                self.assertIn('code', info)
                self.assertEqual(info['code'], language.value)


class TestCulturalContextProvider(unittest.TestCase):
    """Test cases for the CulturalContextProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = CulturalContextProvider()
    
    def test_get_cultural_context(self):
        """Test cultural context retrieval for all supported languages."""
        for language in SupportedLanguage:
            with self.subTest(language=language):
                context = self.provider.get_cultural_context(language)
                self.assertIsInstance(context, CulturalContext)
                self.assertEqual(context.language, language)
                self.assertIsInstance(context.formality_level, str)
                self.assertIsInstance(context.greeting_style, str)
                self.assertIsInstance(context.response_structure, str)
                self.assertIsInstance(context.cultural_notes, list)
                self.assertGreater(len(context.cultural_notes), 0)
    
    def test_format_hr_response_english(self):
        """Test HR response formatting for English."""
        test_cases = [
            ("Hello", "greeting", "Hello! Hello"),
            ("This is a response", "general", "This is a response."),
            ("How are you", "introduction", "Hello! How are you.")
        ]
        
        for content, query_type, expected_start in test_cases:
            with self.subTest(content=content, query_type=query_type):
                result = self.provider.format_hr_response(content, SupportedLanguage.ENGLISH, query_type)
                if expected_start:
                    self.assertTrue(result.startswith(expected_start.split('!')[0]))
                self.assertTrue(result.endswith(('.', '!', '?')))
    
    def test_format_hr_response_german(self):
        """Test HR response formatting for German."""
        test_cases = [
            ("Hallo", "greeting", "Guten Tag!"),
            ("Das ist eine Antwort", "general", None),
            ("Wie geht es", "introduction", "Guten Tag!")
        ]
        
        for content, query_type, expected_start in test_cases:
            with self.subTest(content=content, query_type=query_type):
                result = self.provider.format_hr_response(content, SupportedLanguage.GERMAN, query_type)
                if expected_start:
                    self.assertTrue(result.startswith(expected_start))
                self.assertTrue(result.endswith(('.', '!', '?')))
                
                # Long responses should have polite closing
                if len(result) > 200:
                    self.assertIn("Ich hoffe, das hilft Ihnen weiter", result)
    
    def test_format_hr_response_japanese(self):
        """Test HR response formatting for Japanese."""
        test_cases = [
            ("こんにちは", "greeting", "こんにちは。"),
            ("これは回答です", "general", None),
            ("元気ですか", "introduction", "こんにちは。")
        ]
        
        for content, query_type, expected_start in test_cases:
            with self.subTest(content=content, query_type=query_type):
                result = self.provider.format_hr_response(content, SupportedLanguage.JAPANESE, query_type)
                if expected_start and query_type in ["greeting", "introduction"]:
                    self.assertTrue(result.startswith("こんにちは。"))
                self.assertTrue(result.endswith(('。', '！', '？')))
                
                # Long responses should have polite closing
                if len(result) > 100:
                    self.assertIn("どうぞよろしくお願いいたします", result)


class TestLanguageService(unittest.TestCase):
    """Test cases for the main LanguageService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = LanguageService()
    
    def test_detect_language(self):
        """Test language detection through main service."""
        result = self.service.detect_language("Hello, how can I help you?")
        self.assertIsInstance(result, LanguageDetectionResult)
        self.assertEqual(result.language, SupportedLanguage.ENGLISH)
    
    def test_get_cultural_context(self):
        """Test cultural context retrieval through main service."""
        context = self.service.get_cultural_context(SupportedLanguage.GERMAN)
        self.assertIsInstance(context, CulturalContext)
        self.assertEqual(context.language, SupportedLanguage.GERMAN)
    
    def test_format_response(self):
        """Test response formatting through main service."""
        result = self.service.format_response(
            "This is a test response", 
            SupportedLanguage.ENGLISH, 
            "general"
        )
        self.assertIsInstance(result, str)
        self.assertTrue(result.endswith('.'))
    
    def test_is_supported_language(self):
        """Test language support checking."""
        # Supported languages
        self.assertTrue(self.service.is_supported_language("en"))
        self.assertTrue(self.service.is_supported_language("de"))
        self.assertTrue(self.service.is_supported_language("ja"))
        
        # Unsupported languages
        self.assertFalse(self.service.is_supported_language("fr"))
        self.assertFalse(self.service.is_supported_language("es"))
        self.assertFalse(self.service.is_supported_language("invalid"))
    
    def test_get_supported_languages(self):
        """Test supported languages list retrieval."""
        languages = self.service.get_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertEqual(len(languages), len(SupportedLanguage))
        
        for lang_info in languages:
            self.assertIn('code', lang_info)
            self.assertIn('name', lang_info)
            self.assertIn('native_name', lang_info)
            self.assertIn(lang_info['code'], ['en', 'de', 'ja'])
    
    def test_translate_hr_terms(self):
        """Test HR terms translation."""
        terms = ['employee', 'manager', 'team', 'skills']
        
        # English (no translation)
        en_translations = self.service.translate_hr_terms(terms, SupportedLanguage.ENGLISH)
        for term in terms:
            self.assertEqual(en_translations[term], term)
        
        # German translations
        de_translations = self.service.translate_hr_terms(terms, SupportedLanguage.GERMAN)
        self.assertEqual(de_translations['employee'], 'Mitarbeiter')
        self.assertEqual(de_translations['manager'], 'Manager')
        self.assertEqual(de_translations['team'], 'Team')
        self.assertEqual(de_translations['skills'], 'Fähigkeiten')
        
        # Japanese translations
        ja_translations = self.service.translate_hr_terms(terms, SupportedLanguage.JAPANESE)
        self.assertEqual(ja_translations['employee'], '従業員')
        self.assertEqual(ja_translations['manager'], 'マネージャー')
        self.assertEqual(ja_translations['team'], 'チーム')
        self.assertEqual(ja_translations['skills'], 'スキル')
    
    def test_get_language_templates(self):
        """Test language-specific templates retrieval."""
        for language in SupportedLanguage:
            with self.subTest(language=language):
                templates = self.service.get_language_templates(language)
                self.assertIsInstance(templates, dict)
                
                # Check required template keys
                required_keys = ['greeting', 'employee_search', 'no_results', 'error', 'help']
                for key in required_keys:
                    self.assertIn(key, templates)
                    self.assertIsInstance(templates[key], str)
                    self.assertGreater(len(templates[key]), 0)
    
    def test_integration_workflow(self):
        """Test complete workflow integration."""
        # Test text in different languages
        test_queries = [
            ("How can I find employees with Python skills?", SupportedLanguage.ENGLISH),
            ("Wie kann ich Mitarbeiter mit Python-Kenntnissen finden?", SupportedLanguage.GERMAN),
            ("Pythonスキルを持つ従業員をどうやって見つけることができますか？", SupportedLanguage.JAPANESE)
        ]
        
        for query, expected_lang in test_queries:
            with self.subTest(query=query[:30]):
                # Step 1: Detect language
                detection_result = self.service.detect_language(query)
                self.assertEqual(detection_result.language, expected_lang)
                
                # Step 2: Get cultural context
                context = self.service.get_cultural_context(detection_result.language)
                self.assertEqual(context.language, expected_lang)
                
                # Step 3: Format response
                sample_response = "I found 5 employees with Python skills."
                formatted_response = self.service.format_response(
                    sample_response, 
                    detection_result.language, 
                    "employee_search"
                )
                
                # Verify formatting
                self.assertIsInstance(formatted_response, str)
                self.assertGreater(len(formatted_response), 0)


class TestLanguageServicePerformance(unittest.TestCase):
    """Performance tests for the language service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = LanguageService()
    
    def test_detection_performance(self):
        """Test language detection performance with various text lengths."""
        import time
        
        test_texts = [
            "Short text",
            "This is a medium length text that contains several words and should be processed efficiently by the language detection system.",
            "This is a very long text that contains many words and sentences. " * 20
        ]
        
        for text in test_texts:
            with self.subTest(length=len(text)):
                start_time = time.time()
                result = self.service.detect_language(text)
                end_time = time.time()
                
                # Detection should be fast (under 1 second for any text)
                self.assertLess(end_time - start_time, 1.0)
                self.assertIsInstance(result, LanguageDetectionResult)
    
    def test_caching_performance(self):
        """Test that caching improves performance."""
        import time
        
        text = "This is a test text for caching performance evaluation."
        
        # First call (no cache)
        start_time = time.time()
        result1 = self.service.detect_language(text)
        first_call_time = time.time() - start_time
        
        # Second call (should use cache)
        start_time = time.time()
        result2 = self.service.detect_language(text)
        second_call_time = time.time() - start_time
        
        # Results should be identical
        self.assertEqual(result1.language, result2.language)
        self.assertEqual(result1.confidence, result2.confidence)
        
        # Second call should be faster (or at least not significantly slower)
        self.assertLessEqual(second_call_time, first_call_time * 2)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestLanguageDetector,
        TestCulturalContextProvider,
        TestLanguageService,
        TestLanguageServicePerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)