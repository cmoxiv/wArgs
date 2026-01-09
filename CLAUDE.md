# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

wArgs is a Python decorator library that automatically generates argparse-based CLI interfaces from function signatures, type hints, and docstrings. The project is in development (Phase 2 complete - Core Introspection Engine implemented).

## Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=wArgs --cov-report=term-missing

# Run a single test file
pytest tests/unit/test_exceptions.py

# Run tests matching a pattern
pytest -k "test_conversion"

# Linting
ruff check wArgs tests
ruff format --check wArgs tests

# Type checking
mypy wArgs

# Run all checks via tox
tox

# Run specific tox environment
tox -e lint
tox -e typecheck
tox -e coverage
```

## Architecture

### Current Package Structure

```
wArgs/
├── __init__.py              # Public API exports
├── _version.py              # Version string
├── py.typed                 # PEP 561 marker
├── core/
│   ├── config.py            # ParameterInfo, FunctionInfo, TypeInfo dataclasses
│   └── exceptions.py        # Exception hierarchy (WargsError base class)
└── introspection/
    ├── signatures.py        # Function signature analysis (extract_parameters, extract_function_info)
    ├── types.py             # Type annotation resolution (resolve_type)
    └── docstrings.py        # Docstring parsing (Google/NumPy/Sphinx format detection)
```

### Architecture Flow

The system flow (partially implemented):
1. **Introspection Engine** (Phase 2 - Complete)
   - `signatures.py`: Extracts parameters from function signatures
   - `types.py`: Resolves type annotations (primitives, Optional, Union, Literal, Enum, collections)
   - `docstrings.py`: Auto-detects and parses Google/NumPy/Sphinx docstrings
2. **Configuration Builder** (Phase 3 - Pending) - Builds internal config representation
3. **@wArgs decorator** (Phase 4 - Pending) - Applied at import time
4. **Parser Builder** (Phase 3 - Pending) - Generates ArgumentParser (lazy construction)
5. **Execution Handler** (Phase 4 - Pending) - Parses args and calls function

### Key Data Structures

- `ParameterInfo`: Extracted parameter metadata (name, type, default, kind, description)
- `FunctionInfo`: Complete function metadata (name, parameters, return type, docstring)
- `TypeInfo`: Resolved type information (origin, args, is_optional, is_literal, is_enum, converter)
- `DocstringInfo`: Parsed docstring (summary, description, params, returns, raises, format)

### Planned Modules

- `wArgs/builders/` - ArgumentParser and argument construction
- `wArgs/converters/` - Type converter registry
- `wArgs/completion/` - Shell completion generation (bash/zsh/fish)
- `wArgs/plugins/` - Entry point-based plugin system

### Exception Hierarchy

```
WargsError (base)
├── ConfigurationError  # Invalid decorator config (import-time)
├── IntrospectionError  # Function analysis errors (import-time)
└── ConversionError     # Argument conversion errors (runtime)
```

## Code Standards

- Python 3.8+ compatibility (use `from __future__ import annotations`)
- Google-style docstrings
- Type hints on all public APIs
- 100% test coverage target
- ruff for linting/formatting (88 char line length)
- mypy strict mode
