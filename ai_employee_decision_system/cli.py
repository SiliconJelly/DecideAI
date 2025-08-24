"""
Command-line interface for the AI Employee Decision System.
"""

import argparse
import sys

from ai_employee_decision_system.core import config, get_logger, setup_logging
from ai_employee_decision_system.models import init_db


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Employee Decision System CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init DB command
    init_db_parser = subparsers.add_parser(
        "init-db",
        help="Initialize the database",
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information",
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    if args.command == "init-db":
        logger.info("Initializing database")
        init_db()
        logger.info("Database initialized successfully")
    elif args.command == "version":
        from ai_employee_decision_system import __version__
        print(f"AI Employee Decision System v{__version__}")
    else:
        print("No command specified. Use --help for usage information.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())