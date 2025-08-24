#!/usr/bin/env python3
"""
Unit tests for the Multilingual Response Formatter.

This test suite validates the response formatting, cultural adaptation,
and multilingual capabilities of the response formatting system.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai_employee_decision_system.services.response_formatter import (
    MultilingualResponseFormatter, ResponseType, FormattingRules, FormattedResponse
)
from ai_employee_decision_system.services.language_service import (
    SupportedLanguage, CulturalContext
)


class TestMultilingualResponseFormatter(unittest.TestCase):
    """Test cases for the MultilingualResponseFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = MultilingualResponseFormatter()
    
    def test_initialization(self):
        """Test that the formatter initializes correctly."""
        self.assertIsInstance(self.formatter, MultilingualResponseFormatter)
        self.assertIsInstance(self.formatter.formatting_rules, dict)
        self.assertIsInstance(self.formatter.cultural_templates, dict)
        self.assertIsInstance(self.formatter.professional_phrases, dict)
        
        # Check that all supported languages have formatting rules
        for language in SupportedLanguage:
            self.assertIn(language, self.formatter.formatting_rules)
            self.assertIn(language, self.formatter.cultural_templates)
            self.assertIn(language, self.formatter.professional_phrases)
    
    def test_format_response_english(self):
        """Test response formatting for English."""
        content = "Here are the employees with Python skills: John Smith, Jane Doe."
        result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.EMPLOYEE_LIST
        )
        
        self.assertIsInstance(result, FormattedResponse)
        self.assertEqual(result.language, SupportedLanguage.ENGLISH)
        self.assertEqual(result.response_type, ResponseType.EMPLOYEE_LIST)
        self.assertIn(content, result.content)
        self.assertGreater(len(result.formatting_applied), 0)
        self.assertGreater(result.estimated_reading_time, 0)
    
    def test_format_response_german(self):
        """Test response formatting for German."""
        content = "Hier sind die Mitarbeiter mit Python-Kenntnissen: Hans Müller, Anna Schmidt."
        result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.GERMAN,
            response_type=ResponseType.EMPLOYEE_LIST
        )
        
        self.assertIsInstance(result, FormattedResponse)
        self.assertEqual(result.language, SupportedLanguage.GERMAN)
        self.assertEqual(result.response_type, ResponseType.EMPLOYEE_LIST)
        self.assertIn("Mitarbeiter", result.content)
        self.assertGreater(len(result.formatting_applied), 0)
    
    def test_format_response_japanese(self):
        """Test response formatting for Japanese."""
        content = "Pythonスキルを持つ従業員は以下の通りです：田中太郎、佐藤花子。"
        result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.JAPANESE,
            response_type=ResponseType.EMPLOYEE_LIST
        )
        
        self.assertIsInstance(result, FormattedResponse)
        self.assertEqual(result.language, SupportedLanguage.JAPANESE)
        self.assertEqual(result.response_type, ResponseType.EMPLOYEE_LIST)
        self.assertIn("従業員", result.content)
        self.assertGreater(len(result.formatting_applied), 0)
    
    def test_format_response_with_cultural_context(self):
        """Test response formatting with cultural context."""
        content = "Performance review feedback for the employee."
        cultural_context = CulturalContext(
            language=SupportedLanguage.GERMAN,
            formality_level="formal",
            greeting_style="respectful",
            response_structure="thorough-detailed-systematic",
            cultural_notes=["Use formal address", "Be thorough"]
        )
        
        result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.GERMAN,
            response_type=ResponseType.PERFORMANCE_FEEDBACK,
            cultural_context=cultural_context,
            formality_level="formal"
        )
        
        self.assertTrue(len(result.cultural_adaptations) > 0)
        self.assertEqual(result.formality_level, "formal")
    
    def test_clean_and_normalize(self):
        """Test text cleaning and normalization."""
        messy_content = "This   is    a   messy   text  .  With  weird   spacing !"
        cleaned = self.formatter._clean_and_normalize(messy_content)
        
        self.assertNotIn("  ", cleaned)  # No double spaces
        self.assertIn("text.", cleaned)  # Proper punctuation spacing
        self.assertIn("spacing!", cleaned)
    
    def test_japanese_text_formatting(self):
        """Test Japanese-specific text formatting."""
        rules = self.formatter.formatting_rules[SupportedLanguage.JAPANESE]
        content = "これはテストです. 日本語の文章だ."
        
        formatted = self.formatter._format_japanese_text(content, rules)
        
        self.assertIn("です。", formatted)  # Proper Japanese punctuation
        self.assertNotIn("だ.", formatted)  # Should be converted to polite form
    
    def test_german_text_formatting(self):
        """Test German-specific text formatting."""
        rules = self.formatter.formatting_rules[SupportedLanguage.GERMAN]
        content = "Das ist ein test mit mitarbeiter und unternehmen."
        
        formatted = self.formatter._format_german_text(content, rules)
        
        # Should capitalize German nouns
        self.assertIn("Mitarbeiter", formatted)
        self.assertIn("Unternehmen", formatted)
    
    def test_english_text_formatting(self):
        """Test English-specific text formatting."""
        rules = self.formatter.formatting_rules[SupportedLanguage.ENGLISH]
        content = "this is a test. with proper capitalization."
        
        formatted = self.formatter._format_english_text(content, rules)
        
        # Should capitalize after periods
        self.assertIn("test. With", formatted)
    
    def test_employee_list_formatting(self):
        """Test employee list specific formatting."""
        content = "Name: John Smith\\nSkills: Python, Java\\nDepartment: Engineering"
        
        # English formatting
        formatted_en = self.formatter._format_employee_list(
            content, SupportedLanguage.ENGLISH, self.formatter.formatting_rules[SupportedLanguage.ENGLISH]
        )
        self.assertIn("Name: John Smith", formatted_en)
        
        # Japanese formatting
        formatted_ja = self.formatter._format_employee_list(
            content, SupportedLanguage.JAPANESE, self.formatter.formatting_rules[SupportedLanguage.JAPANESE]
        )
        self.assertIn("名前:", formatted_ja)
        self.assertIn("スキル:", formatted_ja)
        
        # German formatting
        formatted_de = self.formatter._format_employee_list(
            content, SupportedLanguage.GERMAN, self.formatter.formatting_rules[SupportedLanguage.GERMAN]
        )
        self.assertIn("Fähigkeiten:", formatted_de)
        self.assertIn("Abteilung:", formatted_de)
    
    def test_skill_analysis_formatting(self):
        """Test skill analysis specific formatting."""
        content = "Skill Level: Advanced\\nExperience: 5 years"
        
        # Japanese formatting
        formatted_ja = self.formatter._format_skill_analysis(
            content, SupportedLanguage.JAPANESE, self.formatter.formatting_rules[SupportedLanguage.JAPANESE]
        )
        self.assertIn("スキルレベル:", formatted_ja)
        self.assertIn("経験:", formatted_ja)
        
        # German formatting
        formatted_de = self.formatter._format_skill_analysis(
            content, SupportedLanguage.GERMAN, self.formatter.formatting_rules[SupportedLanguage.GERMAN]
        )
        self.assertIn("Fähigkeitslevel:", formatted_de)
        self.assertIn("Erfahrung:", formatted_de)
    
    def test_error_message_formatting(self):
        """Test error message formatting."""
        content = "An error occurred while processing your request."
        
        # English
        formatted_en = self.formatter._format_error_message(
            content, SupportedLanguage.ENGLISH, self.formatter.formatting_rules[SupportedLanguage.ENGLISH]
        )
        self.assertTrue(formatted_en.startswith("I apologize"))
        
        # German
        formatted_de = self.formatter._format_error_message(
            content, SupportedLanguage.GERMAN, self.formatter.formatting_rules[SupportedLanguage.GERMAN]
        )
        self.assertTrue(formatted_de.startswith("Entschuldigung"))
        
        # Japanese
        formatted_ja = self.formatter._format_error_message(
            content, SupportedLanguage.JAPANESE, self.formatter.formatting_rules[SupportedLanguage.JAPANESE]
        )
        self.assertTrue(formatted_ja.startswith("申し訳"))
    
    def test_greeting_formatting(self):
        """Test greeting formatting."""
        content = "I can help you with HR tasks."
        
        # English
        formatted_en = self.formatter._format_greeting(
            content, SupportedLanguage.ENGLISH, self.formatter.formatting_rules[SupportedLanguage.ENGLISH]
        )
        self.assertTrue(any(greeting in formatted_en for greeting in ["Hello", "Hi"]))
        
        # German
        formatted_de = self.formatter._format_greeting(
            content, SupportedLanguage.GERMAN, self.formatter.formatting_rules[SupportedLanguage.GERMAN]
        )
        self.assertTrue(formatted_de.startswith("Guten Tag"))
        
        # Japanese
        formatted_ja = self.formatter._format_greeting(
            content, SupportedLanguage.JAPANESE, self.formatter.formatting_rules[SupportedLanguage.JAPANESE]
        )
        self.assertTrue(formatted_ja.startswith("こんにちは"))
    
    def test_formality_levels(self):
        """Test different formality levels."""
        content = "This is a test response."
        
        # Casual
        result_casual = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.GENERAL_ADVICE,
            formality_level="casual"
        )
        self.assertEqual(result_casual.formality_level, "casual")
        
        # Business
        result_business = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.GENERAL_ADVICE,
            formality_level="business"
        )
        self.assertEqual(result_business.formality_level, "business")
        
        # Formal
        result_formal = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.GERMAN,
            response_type=ResponseType.GENERAL_ADVICE,
            formality_level="formal"
        )
        self.assertEqual(result_formal.formality_level, "formal")
    
    def test_cultural_adaptations(self):
        """Test cultural adaptations."""
        content = "You should improve your performance."
        cultural_context = CulturalContext(
            language=SupportedLanguage.JAPANESE,
            formality_level="polite",
            greeting_style="respectful",
            response_structure="context-harmony-consensus",
            cultural_notes=["Indirect communication", "Group harmony"]
        )
        
        result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.JAPANESE,
            response_type=ResponseType.PERFORMANCE_FEEDBACK,
            cultural_context=cultural_context
        )
        
        self.assertGreater(len(result.cultural_adaptations), 0)
        # Japanese adaptations should make the message more indirect (English content will have English indirect markers)
        self.assertTrue(any(marker in result.content for marker in ["might want to", "perhaps", "consider"]))
    
    def test_reading_time_estimation(self):
        """Test reading time estimation."""
        # Short content
        short_content = "Hello."
        short_time = self.formatter._estimate_reading_time(short_content, SupportedLanguage.ENGLISH)
        self.assertEqual(short_time, 5)  # Minimum 5 seconds
        
        # Long content
        long_content = "This is a much longer piece of content that should take more time to read. " * 20
        long_time = self.formatter._estimate_reading_time(long_content, SupportedLanguage.ENGLISH)
        self.assertGreater(long_time, short_time)
        
        # Japanese should take longer than English for same character count
        japanese_content = "これは日本語のテストです。" * 10
        english_content = "This is an English test." * 10
        
        japanese_time = self.formatter._estimate_reading_time(japanese_content, SupportedLanguage.JAPANESE)
        english_time = self.formatter._estimate_reading_time(english_content, SupportedLanguage.ENGLISH)
        
        # Japanese reading should generally take longer due to character complexity
        self.assertGreaterEqual(japanese_time, english_time * 0.8)  # Allow some variance
    
    def test_all_response_types(self):
        """Test that all response types can be formatted."""
        content = "Test content for formatting."
        
        for response_type in ResponseType:
            with self.subTest(response_type=response_type):
                result = self.formatter.format_response(
                    content=content,
                    language=SupportedLanguage.ENGLISH,
                    response_type=response_type
                )
                
                self.assertIsInstance(result, FormattedResponse)
                self.assertEqual(result.response_type, response_type)
                self.assertIn(content, result.content)
    
    def test_all_languages(self):
        """Test that all supported languages can format responses."""
        content = "Test content for formatting."
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                result = self.formatter.format_response(
                    content=content,
                    language=language,
                    response_type=ResponseType.GENERAL_ADVICE
                )
                
                self.assertIsInstance(result, FormattedResponse)
                self.assertEqual(result.language, language)
                self.assertGreater(len(result.formatting_applied), 0)
    
    def test_professional_framing(self):
        """Test professional framing addition."""
        content = "Here is the information you requested."
        
        result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.EMPLOYEE_LIST,
            formality_level="business"
        )
        
        # Should have professional opening and closing
        self.assertIn("Based on your search criteria", result.content)
        self.assertIn("additional assistance", result.content)
    
    def test_formatting_statistics(self):
        """Test formatting statistics retrieval."""
        stats = self.formatter.get_formatting_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["supported_languages"], len(SupportedLanguage))
        self.assertEqual(stats["response_types"], len(ResponseType))
        self.assertIn("languages", stats)
        self.assertIn("response_types_list", stats)
    
    def test_validate_formatting_rules(self):
        """Test formatting rules validation."""
        # Valid languages should pass validation
        for language in SupportedLanguage:
            with self.subTest(language=language):
                is_valid = self.formatter.validate_formatting_rules(language)
                self.assertTrue(is_valid, f"Formatting rules for {language.value} should be valid")
    
    def test_formatting_rules_structure(self):
        """Test that all formatting rules have the required structure."""
        required_fields = [
            'bullet_style', 'number_format', 'section_separator',
            'emphasis_markers', 'date_format', 'list_connector'
        ]
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                rules = self.formatter.formatting_rules[language]
                
                for field in required_fields:
                    self.assertTrue(hasattr(rules, field), f"Missing field {field} for {language.value}")
                    self.assertIsNotNone(getattr(rules, field), f"Field {field} is None for {language.value}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty content
        result = self.formatter.format_response(
            content="",
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.GENERAL_ADVICE
        )
        self.assertIsInstance(result, FormattedResponse)
        
        # Very long content
        long_content = "This is a very long piece of content. " * 1000
        result = self.formatter.format_response(
            content=long_content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.GENERAL_ADVICE
        )
        self.assertIsInstance(result, FormattedResponse)
        self.assertGreater(result.estimated_reading_time, 60)  # Should be more than 1 minute
        
        # Content with special characters
        special_content = "Content with émojis 😊 and spëcial chäractërs!"
        result = self.formatter.format_response(
            content=special_content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.GENERAL_ADVICE
        )
        self.assertIsInstance(result, FormattedResponse)
    
    def test_consistency_across_languages(self):
        """Test that formatting is consistent across languages."""
        content = "Find employees with leadership skills and project management experience."
        
        results = {}
        for language in SupportedLanguage:
            results[language] = self.formatter.format_response(
                content=content,
                language=language,
                response_type=ResponseType.EMPLOYEE_LIST
            )
        
        # All should have similar structure
        for language, result in results.items():
            self.assertEqual(result.response_type, ResponseType.EMPLOYEE_LIST)
            self.assertEqual(result.language, language)
            self.assertGreater(len(result.formatting_applied), 3)  # Should have multiple formatting steps
            self.assertGreater(result.estimated_reading_time, 0)


class TestFormattingRulesIntegration(unittest.TestCase):
    """Integration tests for formatting rules with different scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = MultilingualResponseFormatter()
    
    def test_hr_workflow_formatting(self):
        """Test formatting for a complete HR workflow."""
        # Employee search result
        search_content = "Found 3 employees: John (Python, 5 years), Jane (Java, 3 years), Bob (React, 2 years)"
        search_result = self.formatter.format_response(
            content=search_content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.EMPLOYEE_LIST,
            formality_level="business"
        )
        
        self.assertIn("Based on your search criteria", search_result.content)
        self.assertIn("John", search_result.content)
        
        # Performance feedback
        feedback_content = "Strengths: Good technical skills. Areas for Improvement: Communication skills."
        feedback_result = self.formatter.format_response(
            content=feedback_content,
            language=SupportedLanguage.ENGLISH,
            response_type=ResponseType.PERFORMANCE_FEEDBACK,
            formality_level="formal"
        )
        
        self.assertIn("feedback", feedback_result.content.lower())
        self.assertIn("Strengths:", feedback_result.content)
    
    def test_multilingual_consistency(self):
        """Test that the same content is formatted consistently across languages."""
        content = "Team recommendation: Need 1 senior developer, 2 junior developers, 1 designer."
        
        results = {}
        for language in SupportedLanguage:
            results[language] = self.formatter.format_response(
                content=content,
                language=language,
                response_type=ResponseType.TEAM_RECOMMENDATION,
                formality_level="business"
            )
        
        # All should have professional framing
        for language, result in results.items():
            self.assertGreater(len(result.content), len(content))  # Should be enhanced
            self.assertIn("1", result.content)  # Numbers should be preserved
            self.assertIn("2", result.content)
    
    def test_cultural_context_integration(self):
        """Test integration with cultural context across different scenarios."""
        content = "Your performance this quarter was below expectations."
        
        # Japanese cultural context (indirect)
        japanese_context = CulturalContext(
            language=SupportedLanguage.JAPANESE,
            formality_level="polite",
            greeting_style="respectful",
            response_structure="context-harmony-consensus",
            cultural_notes=["Indirect communication", "Preserve harmony"]
        )
        
        japanese_result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.JAPANESE,
            response_type=ResponseType.PERFORMANCE_FEEDBACK,
            cultural_context=japanese_context
        )
        
        # Should be more indirect and polite (English content will have English indirect markers)
        self.assertTrue(any(marker in japanese_result.content for marker in ["might want to", "perhaps", "consider", "might have room"]))
        self.assertGreater(len(japanese_result.cultural_adaptations), 0)
        
        # German cultural context (direct and thorough)
        german_context = CulturalContext(
            language=SupportedLanguage.GERMAN,
            formality_level="formal",
            greeting_style="respectful",
            response_structure="thorough-detailed-systematic",
            cultural_notes=["Be thorough", "Use formal address"]
        )
        
        german_result = self.formatter.format_response(
            content=content,
            language=SupportedLanguage.GERMAN,
            response_type=ResponseType.PERFORMANCE_FEEDBACK,
            cultural_context=german_context
        )
        
        # Should be more systematic and formal
        self.assertGreater(len(german_result.cultural_adaptations), 0)
        self.assertEqual(german_result.formality_level, "business")  # Applied formality


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestMultilingualResponseFormatter,
        TestFormattingRulesIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)