# Contributing to wArgs

Thank you for your interest in contributing to wArgs! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We want wArgs to be a welcoming project for everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [GitHub Issues](https://github.com/YOUR_USERNAME/wargs/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Python version and OS
   - Minimal code example if applicable

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue describing:
   - The use case for the feature
   - How it would work from a user's perspective
   - Any implementation ideas (optional)

### Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes following the coding standards below
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/wargs.git
cd wargs

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Coding Standards

### Style

- Follow PEP 8 style guidelines
- Use [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Maximum line length: 88 characters (Black-compatible)

### Type Hints

- All public functions and methods must have type hints
- Use `from __future__ import annotations` for forward references
- Run `mypy wargs` to verify type correctness

### Docstrings

- Use Google-style docstrings for all public APIs
- Include Args, Returns, and Raises sections as appropriate
- Example:

```python
def convert_value(value: str, target_type: type[T]) -> T:
    """Convert a string value to the target type.

    Args:
        value: The string value to convert.
        target_type: The type to convert to.

    Returns:
        The converted value.

    Raises:
        ConversionError: If conversion fails.
    """
```

### Testing

- Write tests for all new functionality
- Maintain 100% code coverage
- Use pytest for testing
- Use hypothesis for property-based testing where appropriate

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=wargs --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_exceptions.py

# Run tests matching a pattern
pytest -k "test_conversion"
```

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters
- Add details in the body if needed

Good examples:
- `Add support for Literal type hints`
- `Fix docstring parsing for multi-line descriptions`
- `Update CI to test Python 3.12`

## Project Structure

```
wargs/
├── wargs/                  # Main package
│   ├── __init__.py        # Public API exports
│   ├── _version.py        # Version string
│   ├── py.typed           # PEP 561 marker
│   └── core/              # Core functionality
│       ├── __init__.py
│       └── exceptions.py  # Exception hierarchy
├── tests/                  # Test suite
│   ├── conftest.py        # Shared fixtures
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
├── pyproject.toml         # Build configuration
├── tox.ini                # Multi-environment testing
└── .pre-commit-config.yaml # Pre-commit hooks
```

## Running Quality Checks

Before submitting a PR, ensure all checks pass:

```bash
# Linting
ruff check wargs tests
ruff format --check wargs tests

# Type checking
mypy wargs

# Tests with coverage
pytest --cov=wargs --cov-fail-under=100

# Or run everything via tox
tox
```

## Questions?

If you have questions about contributing, feel free to:
- Open a discussion on GitHub
- Create an issue with the "question" label

Thank you for contributing to wArgs!
