# Contributing to EasyRag

Thank you for your interest in contributing to EasyRag! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/EasyRag.git
   cd EasyRag
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/TimCodes/EasyRag.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip or uv for package management
- Git

### Install Development Dependencies

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Set Up Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Use descriptive branch names:
- `feature/add-reranking-strategy`
- `fix/embedding-batch-error`
- `docs/update-readme`

### 2. Make Your Changes

- Follow the existing code structure
- Keep changes focused and minimal
- Add docstrings to new functions and classes
- Update relevant documentation

### 3. Write Tests

Add tests for new functionality in the `tests/` directory:

```python
# tests/test_new_feature.py
import pytest
from easyrag import YourNewFeature

def test_new_feature():
    """Test your new feature"""
    feature = YourNewFeature()
    result = feature.do_something()
    assert result == expected_value
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
pytest tests/test_basic.py
pytest tests/test_basic.py::TestKeywordExtractor
```

### Run with Coverage

```bash
pytest --cov=easyrag --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

### Test Requirements

- All new features must have tests
- Aim for at least 80% code coverage
- Tests should be clear and maintainable
- Use mocks for external services (Supabase, OpenAI)

## Code Style

EasyRag uses `ruff` for linting and code formatting.

### Run Linter

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check src/ --fix
```

### Format Code

```bash
ruff format src/
```

### Code Style Guidelines

- Follow PEP 8 conventions
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Use descriptive variable names
- Add docstrings to public functions and classes

#### Docstring Format

```python
def function_name(param1: str, param2: int = 5) -> dict:
    """
    Brief description of the function.
    
    More detailed description if needed. Explain the purpose,
    any important behavior, and edge cases.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        
    Example:
        >>> result = function_name("test", 10)
        >>> print(result)
        {'key': 'value'}
    """
    # Implementation
    pass
```

## Submitting Changes

### 1. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "Add feature: implement reranking strategy

- Add RerankingStrategy class
- Integrate with RAGService
- Add tests for reranking
- Update documentation"
```

Commit message format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed explanation (if needed)
- List specific changes with bullet points

### 2. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

Resolve any conflicts if they occur.

### 3. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 4. Create a Pull Request

1. Go to the [EasyRag repository](https://github.com/TimCodes/EasyRag)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - Describe the changes
   - Link related issues
   - List any breaking changes
   - Add screenshots if applicable

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Ensure all tests pass
- Update documentation if needed
- Respond to review feedback promptly
- Squash commits if requested

## Reporting Issues

### Before Reporting

1. Check if the issue already exists
2. Try to reproduce with the latest version
3. Gather relevant information:
   - Python version
   - EasyRag version
   - Error messages and stack traces
   - Steps to reproduce

### Creating an Issue

Use the appropriate issue template:

**Bug Report:**
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details

**Feature Request:**
- Description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Alternatives considered

## Development Guidelines

### Adding New Features

1. **Discuss first**: Open an issue to discuss major features
2. **Keep it simple**: Follow the existing architecture
3. **Document thoroughly**: Add docs and examples
4. **Test extensively**: Cover edge cases
5. **Update changelog**: Add entry to CHANGELOG.md

### Adding New Search Strategies

To add a new search strategy:

1. Create a new file in `src/easyrag/strategies/`
2. Implement the strategy class
3. Integrate with `RAGService`
4. Add tests
5. Update documentation
6. Add example usage

Example structure:
```python
# src/easyrag/strategies/new_strategy.py
from ..config.logging import get_logger

logger = get_logger(__name__)

class NewSearchStrategy:
    """New search strategy implementation"""
    
    def __init__(self, supabase_client):
        self.supabase_client = supabase_client
    
    async def search(self, query: str, **kwargs):
        """Implement search logic"""
        pass
```

### Adding New Embedding Providers

To add support for a new embedding provider:

1. Add provider adapter in `embedding_service.py`
2. Update configuration handling
3. Add tests with mocked provider
4. Update documentation

## Questions?

If you have questions:
- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
