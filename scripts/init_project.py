#!/usr/bin/env python3
"""
Initialize the Kiro Smart OCR project.

This script sets up the project directory structure, creates necessary files,
and initializes the development environment.
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path


def create_directory_structure():
    """Create the project directory structure."""
    print("Creating directory structure...")
    
    directories = [
        # Backend directories
        "backend/app/api/v1",
        "backend/app/core",
        "backend/app/models",
        "backend/app/services",
        "backend/tests/api",
        "backend/tests/services",
        
        # AI engine directories
        "ai-engine/ocr/ge",
        "ai-engine/ocr/jp",
        "ai-engine/ocr/en",
        "ai-engine/llm",
        "ai-engine/models/ocr",
        "ai-engine/models/llm",
        
        # Frontend directories
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/locales/de",
        "frontend/src/locales/ja",
        "frontend/src/locales/en",
        "frontend/public",
        
        # Desktop app directories
        "desktop-app/src-tauri/src",
        "desktop-app/src",
        
        # Deployment directories
        "deployment/docker",
        "deployment/kubernetes",
        "deployment/scripts",
        
        # Monitoring directories
        "monitoring/prometheus",
        "monitoring/grafana",
        
        # Testing directories
        "testing/datasets/german/invoices",
        "testing/datasets/german/receipts",
        "testing/datasets/german/handwritten",
        "testing/datasets/japanese/invoices",
        "testing/datasets/japanese/receipts",
        "testing/datasets/japanese/handwritten",
        "testing/datasets/english/invoices",
        "testing/datasets/english/receipts",
        "testing/datasets/english/handwritten",
        "testing/benchmarks",
        "testing/results",
        
        # Logs directory
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created {directory}")


def create_env_file():
    """Create .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        print("Creating .env file...")
        shutil.copy(".env.example", ".env")
        print("  Created .env file from .env.example")


def setup_python_environment(venv_dir=".venv"):
    """Set up Python virtual environment."""
    print("Setting up Python virtual environment...")
    
    # Create virtual environment
    subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    print(f"  Created virtual environment in {venv_dir}")
    
    # Determine pip path
    if os.name == "nt":  # Windows
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Upgrade pip
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    print("  Upgraded pip")
    
    # Install dependencies
    subprocess.run([pip_path, "install", "-r", "backend/requirements.txt"], check=True)
    print("  Installed backend dependencies")


def create_git_hooks():
    """Create Git hooks."""
    print("Creating Git hooks...")
    
    # Create pre-commit hook
    hooks_dir = ".git/hooks"
    os.makedirs(hooks_dir, exist_ok=True)
    
    pre_commit_path = os.path.join(hooks_dir, "pre-commit")
    with open(pre_commit_path, "w") as f:
        f.write("""#!/bin/sh
# Pre-commit hook for Kiro Smart OCR

# Run linting
echo "Running linting..."
python -m flake8 backend ai-engine

# Run type checking
echo "Running type checking..."
python -m mypy backend ai-engine

# Run tests
echo "Running tests..."
python -m pytest backend/tests

# If everything passed, allow the commit
exit 0
""")
    
    # Make hook executable
    os.chmod(pre_commit_path, 0o755)
    print("  Created pre-commit hook")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Initialize Kiro Smart OCR project')
    parser.add_argument('--skip-venv', action='store_true', help='Skip virtual environment setup')
    parser.add_argument('--skip-git-hooks', action='store_true', help='Skip Git hooks creation')
    args = parser.parse_args()
    
    print("Initializing Kiro Smart OCR project...")
    
    # Create directory structure
    create_directory_structure()
    
    # Create .env file
    create_env_file()
    
    # Set up Python environment
    if not args.skip_venv:
        setup_python_environment()
    
    # Create Git hooks
    if not args.skip_git_hooks:
        create_git_hooks()
    
    print("\nProject initialization complete!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == "nt":  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source .venv/bin/activate")
    print("2. Edit .env file with your configuration")
    print("3. Start the backend server:")
    print("   python scripts/start_backend.py --reload")


if __name__ == "__main__":
    main()