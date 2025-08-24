#!/usr/bin/env python3
"""
Start the Kiro Smart OCR backend server.

This script starts the FastAPI backend server for Kiro Smart OCR.
"""

import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Start Kiro Smart OCR backend server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    parser.add_argument('--env-file', default='.env', help='Path to .env file')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv(args.env_file)
    
    print(f"Starting Kiro Smart OCR backend server on {args.host}:{args.port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Debug mode: {os.getenv('DEBUG', 'true')}")
    
    # Start server
    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info"
    )


if __name__ == '__main__':
    main()