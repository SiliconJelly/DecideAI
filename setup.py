"""
Setup configuration for AI Employee Decision System.
"""
from pathlib import Path
from setuptools import setup, find_packages

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read development requirements
dev_requirements = []
with open("requirements-dev.txt", "r", encoding="utf-8") as f:
    dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="ai-employee-decision-system",
    version="1.0.0",
    author="AI Employee Decision System Team",
    author_email="support@example.com",
    description="An intelligent system for managing employee data and making AI-powered organizational decisions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/ai-employee-decision-system",
    project_urls={
        "Bug Reports": "https://github.com/your-org/ai-employee-decision-system/issues",
        "Source": "https://github.com/your-org/ai-employee-decision-system",
        "Documentation": "https://docs.example.com",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Human Resources",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
        ],
        "docs": [
            "sphinx>=6.2.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-employee-system=ai_employee_decision_system.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_employee_decision_system": [
            "locales/**/*.json",
            "data/**/*",
            "templates/**/*",
            "static/**/*",
        ],
    },
    zip_safe=False,
    keywords=[
        "ai",
        "employee",
        "decision-support",
        "hr",
        "machine-learning",
        "ocr",
        "nlp",
        "fastapi",
        "gradio",
    ],
    platforms=["any"],
    license="MIT",
)