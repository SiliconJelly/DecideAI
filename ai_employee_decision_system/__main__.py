"""
Main entry point for the AI Employee Decision System.
"""

import argparse
import sys
from pathlib import Path

from ai_employee_decision_system.core import config, get_logger, setup_logging


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Employee Decision System"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the log level",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="Data directory",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Update config with command line arguments
    if args.debug:
        config.debug = True
    
    if args.data_dir:
        config.data_dir = args.data_dir
        config.data_dir.mkdir(exist_ok=True, parents=True)
        config.upload_dir = config.data_dir / "uploads"
        config.upload_dir.mkdir(exist_ok=True, parents=True)
    
    # Set up logging
    setup_logging(args.log_level)
    logger = get_logger(__name__)
    
    logger.info(
        "Starting AI Employee Decision System",
        extra={"data": {"version": config.app_name}},
    )
    
    try:
        # Set up internationalization
        from ai_employee_decision_system.utils import setup_i18n
        setup_i18n()
        
        # Initialize database if needed
        from ai_employee_decision_system.models import init_db
        init_db()
        
        # Import here to avoid circular imports
        from ai_employee_decision_system.ui.app import run_app
        
        run_app()
    except ImportError:
        logger.error("Failed to import required modules. The application may not be fully installed.")
        return 1
    except Exception as e:
        logger.exception(f"Error running application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())