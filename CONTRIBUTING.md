# Contributing to AI Employee Decision System

Thank you for your interest in contributing to the AI Employee Decision System! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to support@example.com.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Docker (optional, for containerized development)
- Tesseract OCR

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-employee-decision-system.git
   cd ai-employee-decision-system
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/your-org/ai-employee-decision-system.git
   ```

## Development Setup

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   python -m ai_employee_decision_system init
   ```

### Docker Development

1. Build and start the development environment:
   ```bash
   docker-compose up -d
   ```

2. Access the running containers:
   ```bash
   docker-compose exec app bash
   ```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues in the codebase
- **Feature additions**: Add new functionality
- **Documentation improvements**: Enhance or fix documentation
- **Performance improvements**: Optimize existing code
- **Test coverage**: Add or improve tests
- **Code quality**: Refactor code for better maintainability

### Before You Start

1. **Check existing issues**: Look for existing issues or discussions about your idea
2. **Create an issue**: For significant changes, create an issue to discuss your approach
3. **Get feedback**: Engage with maintainers and community members
4. **Start small**: Begin with small, focused contributions

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/feature-name`: Feature development branches
- `bugfix/bug-description`: Bug fix branches
- `hotfix/critical-fix`: Critical production fixes

### Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**: Follow coding standards and write tests

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**: Open a PR against the appropriate branch

## Pull Request Process

### Before Submitting

- [ ] Code follows the project's coding standards
- [ ] All tests pass locally
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated if needed
- [ ] Commit messages follow conventional commit format
- [ ] No merge conflicts with target branch

### PR Description Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context about the changes.
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs automatically
2. **Code review**: Maintainers and community members review the code
3. **Feedback**: Address any feedback or requested changes
4. **Approval**: At least one maintainer approval required
5. **Merge**: Maintainer merges the PR

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use isort for import sorting
- **Type hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all public functions and classes

### Code Formatting

We use automated code formatting tools:

```bash
# Format code
black ai_employee_decision_system tests

# Sort imports
isort ai_employee_decision_system tests

# Lint code
flake8 ai_employee_decision_system tests

# Type checking
mypy ai_employee_decision_system
```

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Files and modules**: `snake_case`

### Documentation Standards

- **Docstrings**: All public functions, classes, and modules must have docstrings
- **Type hints**: Use type hints for all function parameters and return values
- **Comments**: Explain complex logic and business rules
- **README updates**: Update documentation for new features

### Example Code Style

```python
"""
Module docstring explaining the purpose of the module.
"""
from typing import List, Optional

from ai_employee_decision_system.models import Employee


class EmployeeService:
    """Service for managing employee operations."""
    
    def __init__(self, db_session: Session) -> None:
        """
        Initialize the employee service.
        
        Args:
            db_session: Database session for operations
        """
        self.db = db_session
    
    def get_employees_by_skill(
        self, 
        skill_name: str, 
        min_proficiency: int = 1
    ) -> List[Employee]:
        """
        Get employees with a specific skill.
        
        Args:
            skill_name: Name of the skill to search for
            min_proficiency: Minimum proficiency level (1-8)
            
        Returns:
            List of employees with the specified skill
            
        Raises:
            ValueError: If min_proficiency is not between 1 and 8
        """
        if not 1 <= min_proficiency <= 8:
            raise ValueError("Proficiency must be between 1 and 8")
        
        # Implementation here
        return []
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── api/           # API endpoint tests
├── fixtures/      # Test fixtures and data
└── conftest.py    # Pytest configuration
```

### Writing Tests

- **Test naming**: `test_function_name_scenario`
- **Test structure**: Arrange, Act, Assert
- **Fixtures**: Use pytest fixtures for common setup
- **Mocking**: Mock external dependencies
- **Coverage**: Aim for >80% test coverage

### Example Test

```python
import pytest
from ai_employee_decision_system.services import EmployeeService
from ai_employee_decision_system.models import EmployeeCreate


def test_create_employee_success(db_session):
    """Test successful employee creation."""
    # Arrange
    service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    
    # Act
    employee = service.create_employee(employee_data)
    
    # Assert
    assert employee is not None
    assert employee.first_name == "John"
    assert employee.email == "john.doe@example.com"


def test_create_employee_duplicate_email(db_session):
    """Test employee creation with duplicate email fails."""
    # Arrange
    service = EmployeeService(db_session)
    employee_data = EmployeeCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    
    # Act
    service.create_employee(employee_data)
    duplicate_employee = service.create_employee(employee_data)
    
    # Assert
    assert duplicate_employee is None
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_employee_decision_system

# Run specific test file
pytest tests/test_employee_service.py

# Run tests matching pattern
pytest -k "test_create_employee"

# Run tests with verbose output
pytest -v
```

## Documentation

### Types of Documentation

1. **Code documentation**: Docstrings and comments
2. **API documentation**: OpenAPI/Swagger documentation
3. **User documentation**: User guides and tutorials
4. **Developer documentation**: Architecture and development guides

### Documentation Standards

- **Clear and concise**: Write for your audience
- **Examples**: Include code examples and use cases
- **Up-to-date**: Keep documentation synchronized with code
- **Accessible**: Use clear language and proper formatting

### Building Documentation

```bash
# Generate API documentation
python scripts/generate_api_docs.py

# Build Sphinx documentation
sphinx-build -b html docs/ docs/_build/html
```

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues**: Check if the issue already exists
2. **Check documentation**: Ensure it's not a usage question
3. **Reproduce the issue**: Provide clear reproduction steps
4. **Gather information**: Include relevant system information

### Issue Template

```markdown
## Bug Report / Feature Request

### Description
A clear and concise description of the issue or feature request.

### Steps to Reproduce (for bugs)
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

### Expected Behavior
A clear description of what you expected to happen.

### Actual Behavior
A clear description of what actually happened.

### Environment
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.11.0]
- Package version: [e.g. 1.0.0]
- Browser (if applicable): [e.g. Chrome 91.0]

### Additional Context
Add any other context about the problem here.

### Screenshots
If applicable, add screenshots to help explain your problem.
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Email**: support@example.com for direct support

### Getting Help

1. **Check documentation**: Start with the README and docs
2. **Search issues**: Look for similar problems
3. **Ask questions**: Use GitHub Discussions for questions
4. **Be specific**: Provide context and details

### Recognition

Contributors are recognized in several ways:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in release announcements
- **GitHub**: Contributor statistics and badges
- **Community**: Recognition in community discussions

## Development Workflow

### Setting Up Your Environment

1. **Fork the repository**
2. **Clone your fork**
3. **Set up development environment**
4. **Create a feature branch**
5. **Make your changes**
6. **Test your changes**
7. **Submit a pull request**

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream changes
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

### Release Process

1. **Version bump**: Update version numbers
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Comprehensive testing
4. **Documentation**: Update documentation
5. **Release**: Create GitHub release and publish to PyPI

## Questions?

If you have questions about contributing, please:

1. Check this document first
2. Search existing issues and discussions
3. Create a new discussion or issue
4. Contact the maintainers directly

Thank you for contributing to the AI Employee Decision System! 🎉