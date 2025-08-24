"""
Utility functions for the AI Employee Decision System.
"""

from .file_storage import FileStorage
from .i18n import get_current_language, get_text, set_language, setup_i18n

__all__ = ["FileStorage", "get_text", "set_language", "get_current_language", "setup_i18n"]