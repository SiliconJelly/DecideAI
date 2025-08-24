"""
Core module for the AI Employee Decision System.
"""

from .config import config, load_config
from .logging import get_logger, setup_logging

__all__ = ["config", "load_config", "get_logger", "setup_logging"]