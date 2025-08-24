"""
Internationalization utilities for the AI Employee Decision System.
"""

import os
from pathlib import Path
from typing import Dict, Optional

import i18n

from ai_employee_decision_system.core import config, get_logger

logger = get_logger(__name__)


def setup_i18n() -> None:
    """Set up internationalization."""
    logger.info("Setting up internationalization")
    
    # Set up i18n configuration
    i18n.load_path.append(os.path.join(os.path.dirname(__file__), "../locales"))
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("file_format", "json")
    i18n.set("locale", config.localization.default_language)
    i18n.set("fallback", "en")
    i18n.set("enable_memoization", True)


def get_text(key: str, **kwargs) -> str:
    """Get translated text for the given key."""
    return i18n.t(key, **kwargs)


def set_language(language: str) -> None:
    """Set the current language."""
    if language in config.localization.available_languages:
        i18n.set("locale", language)
        logger.info(f"Language set to {language}")
    else:
        logger.warning(
            f"Language {language} not available. Using default: {config.localization.default_language}"
        )
        i18n.set("locale", config.localization.default_language)


def get_current_language() -> str:
    """Get the current language."""
    return i18n.get("locale")