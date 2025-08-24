"""
Logging configuration for Kiro Smart OCR.

This module provides structured logging with multilingual support for error messages
and performance metrics. It configures loggers for different components of the system
and provides utilities for logging in different languages.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configure default logging format
DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
JSON_FORMAT = {
    "timestamp": "%(asctime)s",
    "level": "%(levelname)s",
    "logger": "%(name)s",
    "message": "%(message)s",
    "module": "%(module)s",
    "function": "%(funcName)s",
    "line": "%(lineno)d",
}

# Language-specific error messages
ERROR_MESSAGES = {
    "en": {
        "file_not_found": "File not found: {path}",
        "processing_error": "Error processing document: {error}",
        "model_loading_error": "Failed to load model: {model_name}",
        "database_error": "Database error: {error}",
        "auth_error": "Authentication error: {error}",
    },
    "de": {
        "file_not_found": "Datei nicht gefunden: {path}",
        "processing_error": "Fehler bei der Dokumentenverarbeitung: {error}",
        "model_loading_error": "Fehler beim Laden des Modells: {model_name}",
        "database_error": "Datenbankfehler: {error}",
        "auth_error": "Authentifizierungsfehler: {error}",
    },
    "ja": {
        "file_not_found": "ファイルが見つかりません: {path}",
        "processing_error": "ドキュメント処理エラー: {error}",
        "model_loading_error": "モデルの読み込みに失敗しました: {model_name}",
        "database_error": "データベースエラー: {error}",
        "auth_error": "認証エラー: {error}",
    }
}


class MultilingualLogger:
    """Logger with multilingual support for error messages."""
    
    def __init__(self, name: str, default_language: str = "en"):
        """
        Initialize a multilingual logger.
        
        Args:
            name: Logger name
            default_language: Default language for error messages
        """
        self.logger = logging.getLogger(name)
        self.default_language = default_language
    
    def error(self, message_key: str, language: Optional[str] = None, **kwargs):
        """
        Log an error message in the specified language.
        
        Args:
            message_key: Key for the error message template
            language: Language code (en, de, ja)
            **kwargs: Format parameters for the message template
        """
        lang = language or self.default_language
        if lang not in ERROR_MESSAGES:
            lang = self.default_language
            
        if message_key in ERROR_MESSAGES[lang]:
            message = ERROR_MESSAGES[lang][message_key].format(**kwargs)
        else:
            # Fallback to English if message key not found
            message = ERROR_MESSAGES["en"].get(
                message_key, 
                f"Unknown error: {message_key}"
            ).format(**kwargs)
            
        self.logger.error(message)
    
    def info(self, message: str, **kwargs):
        """Log an info message."""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log a critical message."""
        self.logger.critical(message, **kwargs)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
            
        # Add extra fields
        if hasattr(record, "extra"):
            log_record["extra"] = record.extra
            
        return json.dumps(log_record)


def configure_logging(
    level: int = logging.INFO,
    json_output: bool = False,
    log_file: Optional[str] = None
):
    """
    Configure logging for the application.
    
    Args:
        level: Logging level
        json_output: Whether to output logs in JSON format
        log_file: Path to log file (if None, logs to stdout)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # Set formatter
    if json_output:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(DEFAULT_FORMAT)
    
    # Configure handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    # Create component loggers
    logging.getLogger("kiro.ocr").setLevel(level)
    logging.getLogger("kiro.llm").setLevel(level)
    logging.getLogger("kiro.api").setLevel(level)
    logging.getLogger("kiro.auth").setLevel(level)
    logging.getLogger("kiro.db").setLevel(level)
    
    # Log startup message
    logging.getLogger("kiro").info(
        f"Logging configured: level={logging.getLevelName(level)}, "
        f"json_output={json_output}, log_file={log_file or 'stdout'}"
    )


def get_logger(name: str, language: str = "en") -> MultilingualLogger:
    """
    Get a multilingual logger for a component.
    
    Args:
        name: Logger name
        language: Default language for error messages
        
    Returns:
        MultilingualLogger instance
    """
    return MultilingualLogger(name, language)