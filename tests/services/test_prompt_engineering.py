#!/usr/bin/env python3
"""
Unit tests for the Multilingual Prompt Engineering Service.

This test suite validates the prompt generation, cultural adaptation,
and multilingual capabilities of the prompt engineering system.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai_employee_decision_system.services.prompt_engineering import (
    MultilingualPromptEngineer, PromptType, PromptTemplate, GeneratedPrompt
)
from ai_employee_decision_system.services.language_service import (
    SupportedLanguage, CulturalContext
)


class TestMultilingualPromptEngineer(unittest.TestCase):
    """Test cases for the MultilingualPromptEngineer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engineer = MultilingualPromptEngineer()
    
    def test_initialization(self):
        """Test that the prompt engineer initializes correctly."""
        self.assertIsInstance(self.engineer, MultilingualPromptEngineer)
        self.assertIsInstance(self.engineer.prompt_templates, dict)
        self.assertIsInstance(self.engineer.cultural_adaptations, dict)
        
        # Check that all supported languages have templates
        for language in SupportedLanguage:
            self.assertIn(language, self.engineer.prompt_templates)
            
        # Check that all prompt types are covered
        for language in SupportedLanguage:
            templates = self.engineer.prompt_templates[language]
            for prompt_type in PromptType:
                self.assertIn(prompt_type, templates)
    
    def test_generate_prompt_english(self):
        """Test prompt generation for English."""
        query = "Find employees with Python skills"
        result = self.engineer.generate_prompt(
            query=query,
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.EMPLOYEE_SEARCH
        )
        
        self.assertIsInstance(result, GeneratedPrompt)
        self.assertEqual(result.language, SupportedLanguage.ENGLISH)
        self.assertEqual(result.prompt_type, PromptType.EMPLOYEE_SEARCH)
        self.assertIn("HR assistant", result.system_prompt)
        self.assertIn(query, result.user_prompt)
        self.assertGreater(result.estimated_tokens, 0)
        self.assertFalse(result.cultural_context_applied)
    
    def test_generate_prompt_german(self):
        """Test prompt generation for German."""
        query = "Mitarbeiter mit Python-Kenntnissen finden"
        result = self.engineer.generate_prompt(
            query=query,
            language=SupportedLanguage.GERMAN,
            prompt_type=PromptType.EMPLOYEE_SEARCH
        )
        
        self.assertIsInstance(result, GeneratedPrompt)
        self.assertEqual(result.language, SupportedLanguage.GERMAN)
        self.assertEqual(result.prompt_type, PromptType.EMPLOYEE_SEARCH)
        self.assertIn("Personalberater", result.system_prompt)
        self.assertIn(query, result.user_prompt)
        self.assertGreater(result.estimated_tokens, 0)
    
    def test_generate_prompt_japanese(self):
        """Test prompt generation for Japanese."""
        query = "Pythonスキルを持つ従業員を見つける"
        result = self.engineer.generate_prompt(
            query=query,
            language=SupportedLanguage.JAPANESE,
            prompt_type=PromptType.EMPLOYEE_SEARCH
        )
        
        self.assertIsInstance(result, GeneratedPrompt)
        self.assertEqual(result.language, SupportedLanguage.JAPANESE)
        self.assertEqual(result.prompt_type, PromptType.EMPLOYEE_SEARCH)
        self.assertIn("人事アシスタント", result.system_prompt)
        self.assertIn(query, result.user_prompt)
        self.assertGreater(result.estimated_tokens, 0)
    
    def test_generate_prompt_with_context(self):
        """Test prompt generation with additional context."""
        query = "Find Python developers"
        context = {
            "employees": [{"name": "John", "skills": ["Python", "Django"]}],
            "departments": ["Engineering", "Data Science"]
        }
        
        result = self.engineer.generate_prompt(
            query=query,
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.EMPLOYEE_SEARCH,
            context=context
        )
        
        self.assertIn("1 employees", result.system_prompt)
        self.assertIn("Engineering, Data Science", result.system_prompt)
    
    def test_generate_prompt_with_cultural_context(self):
        """Test prompt generation with cultural context."""
        query = "How to conduct performance reviews?"
        cultural_context = CulturalContext(
            language=SupportedLanguage.GERMAN,
            formality_level="formal",
            greeting_style="respectful",
            response_structure="thorough-detailed-systematic",
            cultural_notes=["Use formal address", "Be thorough"]
        )
        
        result = self.engineer.generate_prompt(
            query=query,
            language=SupportedLanguage.GERMAN,
            prompt_type=PromptType.PERFORMANCE_REVIEW,
            cultural_context=cultural_context
        )
        
        self.assertTrue(result.cultural_context_applied)
        self.assertIn("Use formal address", result.system_prompt)
        self.assertIn("Be thorough", result.system_prompt)
    
    def test_all_prompt_types(self):
        """Test that all prompt types can be generated."""
        query = "Test query"
        
        for prompt_type in PromptType:
            with self.subTest(prompt_type=prompt_type):
                result = self.engineer.generate_prompt(
                    query=query,
                    language=SupportedLanguage.ENGLISH,
                    prompt_type=prompt_type
                )
                
                self.assertIsInstance(result, GeneratedPrompt)
                self.assertEqual(result.prompt_type, prompt_type)
                self.assertIn(query, result.user_prompt)
    
    def test_all_languages(self):
        """Test that all supported languages can generate prompts."""
        query = "Test query"
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                result = self.engineer.generate_prompt(
                    query=query,
                    language=language,
                    prompt_type=PromptType.GENERAL_HR
                )
                
                self.assertIsInstance(result, GeneratedPrompt)
                self.assertEqual(result.language, language)
                self.assertIn(query, result.user_prompt)
    
    def test_context_formatting_english(self):
        """Test context formatting for English."""
        context = {
            "employees": [{"name": "John"}, {"name": "Jane"}],
            "skills": ["Python", "JavaScript", "React"],
            "departments": ["Engineering", "Design"]
        }
        
        formatted = self.engineer._format_context(context, SupportedLanguage.ENGLISH)
        
        self.assertIn("Available employee data: 2 employees", formatted)
        self.assertIn("Available skills: Python, JavaScript, React", formatted)
        self.assertIn("Departments: Engineering, Design", formatted)
    
    def test_context_formatting_german(self):
        """Test context formatting for German."""
        context = {
            "employees": [{"name": "Hans"}, {"name": "Anna"}],
            "skills": ["Python", "Java"],
            "departments": ["Entwicklung", "Design"]
        }
        
        formatted = self.engineer._format_context(context, SupportedLanguage.GERMAN)
        
        self.assertIn("Verfügbare Mitarbeiterdaten: 2 Mitarbeiter", formatted)
        self.assertIn("Verfügbare Fähigkeiten: Python, Java", formatted)
        self.assertIn("Abteilungen: Entwicklung, Design", formatted)
    
    def test_context_formatting_japanese(self):
        """Test context formatting for Japanese."""
        context = {
            "employees": [{"name": "田中"}, {"name": "佐藤"}],
            "skills": ["Python", "Java"],
            "departments": ["開発", "デザイン"]
        }
        
        formatted = self.engineer._format_context(context, SupportedLanguage.JAPANESE)
        
        self.assertIn("利用可能な従業員データ: 2名の従業員", formatted)
        self.assertIn("利用可能なスキル: Python, Java", formatted)
        self.assertIn("部署: 開発, デザイン", formatted)
    
    def test_cultural_notes_formatting(self):
        """Test cultural notes formatting for different languages."""
        notes = ["Be respectful", "Consider hierarchy"]
        
        # English
        formatted_en = self.engineer._format_cultural_notes(notes, SupportedLanguage.ENGLISH)
        self.assertIn("Cultural considerations:", formatted_en)
        self.assertIn("- Be respectful", formatted_en)
        
        # German
        formatted_de = self.engineer._format_cultural_notes(notes, SupportedLanguage.GERMAN)
        self.assertIn("Kulturelle Hinweise:", formatted_de)
        self.assertIn("- Be respectful", formatted_de)
        
        # Japanese
        formatted_ja = self.engineer._format_cultural_notes(notes, SupportedLanguage.JAPANESE)
        self.assertIn("文化的な注意事項:", formatted_ja)
        self.assertIn("- Be respectful", formatted_ja)
    
    def test_make_formal_german(self):
        """Test making text formal in German."""
        text = "du bist ein Assistent"
        formal_text = self.engineer._make_formal(text, SupportedLanguage.GERMAN)
        
        self.assertIn("Sie", formal_text)
        self.assertNotIn("du", formal_text)
    
    def test_make_formal_japanese(self):
        """Test making text formal in Japanese."""
        text = "助手です"
        formal_text = self.engineer._make_formal(text, SupportedLanguage.JAPANESE)
        
        # The text already ends with です, so it should just add 。
        self.assertTrue(formal_text.endswith("です。") or formal_text.endswith("です"))
    
    def test_make_polite_japanese(self):
        """Test making text polite in Japanese."""
        text = "助手です"
        polite_text = self.engineer._make_polite(text, SupportedLanguage.JAPANESE)
        
        self.assertTrue(polite_text.startswith("どうぞ"))
        self.assertTrue(polite_text.endswith("です。"))
    
    def test_make_polite_german(self):
        """Test making text polite in German."""
        text = "helfen Sie mir"
        polite_text = self.engineer._make_polite(text, SupportedLanguage.GERMAN)
        
        self.assertTrue(polite_text.startswith("Bitte"))
    
    def test_token_estimation(self):
        """Test token count estimation."""
        # English text
        english_text = "This is a test sentence with multiple words."
        english_tokens = self.engineer._estimate_tokens(english_text)
        self.assertGreater(english_tokens, 0)
        
        # Japanese text (should have more tokens per character)
        japanese_text = "これはテストの文章です。"
        japanese_tokens = self.engineer._estimate_tokens(japanese_text)
        self.assertGreater(japanese_tokens, 0)
        
        # Japanese should have higher token density
        self.assertGreater(japanese_tokens / len(japanese_text), english_tokens / len(english_text))
    
    def test_get_prompt_statistics(self):
        """Test prompt statistics retrieval."""
        stats = self.engineer.get_prompt_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["total_languages"], len(SupportedLanguage))
        self.assertEqual(stats["total_prompt_types"], len(PromptType))
        self.assertIn("languages", stats)
        self.assertIn("prompt_types", stats)
        
        # Check language-specific template counts
        for language in SupportedLanguage:
            key = f"{language.value}_templates"
            self.assertIn(key, stats)
            self.assertEqual(stats[key], len(PromptType))
    
    def test_validate_prompt_template(self):
        """Test prompt template validation."""
        # Valid templates should pass validation
        for language in SupportedLanguage:
            for prompt_type in PromptType:
                with self.subTest(language=language, prompt_type=prompt_type):
                    is_valid = self.engineer.validate_prompt_template(language, prompt_type)
                    self.assertTrue(is_valid, f"Template for {language.value} {prompt_type.value} should be valid")
    
    def test_template_structure(self):
        """Test that all templates have the required structure."""
        for language in SupportedLanguage:
            for prompt_type in PromptType:
                with self.subTest(language=language, prompt_type=prompt_type):
                    template = self.engineer._get_template(language, prompt_type)
                    
                    # Check required fields
                    self.assertIsInstance(template.system_prompt, str)
                    self.assertIsInstance(template.user_prompt_template, str)
                    self.assertIsInstance(template.context_injection, str)
                    self.assertIsInstance(template.cultural_notes, list)
                    self.assertIsInstance(template.response_format, str)
                    self.assertIsInstance(template.examples, list)
                    
                    # Check that system prompt is not empty
                    self.assertGreater(len(template.system_prompt), 0)
                    
                    # Check that user prompt template has query placeholder
                    self.assertIn("{query}", template.user_prompt_template)
    
    def test_performance_review_prompts(self):
        """Test performance review specific prompts."""
        query = "How to give constructive feedback?"
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                result = self.engineer.generate_prompt(
                    query=query,
                    language=language,
                    prompt_type=PromptType.PERFORMANCE_REVIEW
                )
                
                # Should contain performance-related keywords
                system_prompt_lower = result.system_prompt.lower()
                self.assertTrue(any(keyword in system_prompt_lower for keyword in [
                    "performance", "review", "feedback", "evaluation",
                    "leistung", "bewertung", "beurteilung",  # German
                    "評価", "パフォーマンス", "フィードバック"  # Japanese
                ]))
    
    def test_team_building_prompts(self):
        """Test team building specific prompts."""
        query = "How to build an effective team?"
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                result = self.engineer.generate_prompt(
                    query=query,
                    language=language,
                    prompt_type=PromptType.TEAM_BUILDING
                )
                
                # Should contain team-related keywords
                system_prompt_lower = result.system_prompt.lower()
                self.assertTrue(any(keyword in system_prompt_lower for keyword in [
                    "team", "group", "collaboration",
                    "team", "gruppe", "zusammenarbeit",  # German
                    "チーム", "グループ", "協力"  # Japanese
                ]))
    
    def test_hiring_advice_prompts(self):
        """Test hiring advice specific prompts."""
        query = "How to interview candidates?"
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                result = self.engineer.generate_prompt(
                    query=query,
                    language=language,
                    prompt_type=PromptType.HIRING_ADVICE
                )
                
                # Should contain hiring-related keywords
                system_prompt_lower = result.system_prompt.lower()
                self.assertTrue(any(keyword in system_prompt_lower for keyword in [
                    "recruitment", "hiring", "interview", "candidate",
                    "rekrutierung", "einstellung", "interview", "kandidat",  # German
                    "採用", "面接", "候補者"  # Japanese
                ]))
    
    def test_greeting_prompts(self):
        """Test greeting specific prompts."""
        query = "Hello"
        
        for language in SupportedLanguage:
            with self.subTest(language=language):
                result = self.engineer.generate_prompt(
                    query=query,
                    language=language,
                    prompt_type=PromptType.GREETING
                )
                
                # Should be friendly and welcoming
                system_prompt_lower = result.system_prompt.lower()
                self.assertTrue(any(keyword in system_prompt_lower for keyword in [
                    "friendly", "welcoming", "greet",
                    "freundlich", "begrüßen",  # German
                    "親しみやすい", "挨拶"  # Japanese
                ]))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty query
        result = self.engineer.generate_prompt(
            query="",
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.GENERAL_HR
        )
        self.assertIsInstance(result, GeneratedPrompt)
        
        # Very long query
        long_query = "How to improve employee performance? " * 100
        result = self.engineer.generate_prompt(
            query=long_query,
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.PERFORMANCE_REVIEW
        )
        self.assertIsInstance(result, GeneratedPrompt)
        self.assertGreater(result.estimated_tokens, 100)  # Should be a lot of tokens
    
    def test_consistency_across_languages(self):
        """Test that similar prompts are generated consistently across languages."""
        query = "Find employees with leadership skills"
        
        results = {}
        for language in SupportedLanguage:
            results[language] = self.engineer.generate_prompt(
                query=query,
                language=language,
                prompt_type=PromptType.EMPLOYEE_SEARCH
            )
        
        # All should be employee search type
        for language, result in results.items():
            self.assertEqual(result.prompt_type, PromptType.EMPLOYEE_SEARCH)
            self.assertEqual(result.language, language)
            self.assertIn(query, result.user_prompt)


class TestPromptTemplateIntegration(unittest.TestCase):
    """Integration tests for prompt templates with different scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engineer = MultilingualPromptEngineer()
    
    def test_hr_workflow_integration(self):
        """Test a complete HR workflow with different prompt types."""
        # Simulate an HR workflow: greeting -> employee search -> performance review
        
        # Step 1: Greeting
        greeting_result = self.engineer.generate_prompt(
            query="Hello, I need help with HR tasks",
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.GREETING
        )
        self.assertIn("HR", greeting_result.system_prompt)
        
        # Step 2: Employee search
        search_result = self.engineer.generate_prompt(
            query="Find employees with project management experience",
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.EMPLOYEE_SEARCH,
            context={"employees": [{"name": "John", "skills": ["PM", "Agile"]}]}
        )
        self.assertIn("1 employees", search_result.system_prompt)
        
        # Step 3: Performance review
        review_result = self.engineer.generate_prompt(
            query="How to review John's performance?",
            language=SupportedLanguage.ENGLISH,
            prompt_type=PromptType.PERFORMANCE_REVIEW,
            context={"employee_name": "John"}
        )
        self.assertIn("performance", review_result.system_prompt.lower())
    
    def test_multilingual_consistency(self):
        """Test that the same HR scenario works consistently across languages."""
        query = "How to build a development team?"
        context = {"departments": ["Engineering", "QA"]}
        
        results = {}
        for language in SupportedLanguage:
            results[language] = self.engineer.generate_prompt(
                query=query,
                language=language,
                prompt_type=PromptType.TEAM_BUILDING,
                context=context
            )
        
        # All should have similar structure and context
        for language, result in results.items():
            self.assertEqual(result.prompt_type, PromptType.TEAM_BUILDING)
            self.assertIn(query, result.user_prompt)
            # Context should be formatted appropriately for each language
            if language == SupportedLanguage.GERMAN:
                self.assertIn("Abteilungen", result.system_prompt)
            elif language == SupportedLanguage.JAPANESE:
                self.assertIn("部署", result.system_prompt)
            else:
                self.assertIn("Departments", result.system_prompt)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestMultilingualPromptEngineer,
        TestPromptTemplateIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)