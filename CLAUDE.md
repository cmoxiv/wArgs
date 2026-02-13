# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

wArgs is a Python decorator library that automatically generates argparse-based CLI interfaces from function signatures, type hints, and docstrings. The project is fully functional with 600 passing tests.

## Quick Reference

```python
from wArgs import wArgs, Arg
from typing import Annotated

# Function-based CLI
@wArgs
def greet(name: str, count: int = 1):
    """Greet someone."""
    for _ in range(count):
        print(f"Hello, {name}!")

# Class-based CLI with subcommands
@wArgs
class CLI:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def add(self, name: str):
        """Add an item."""
        print(f"Adding {name}")

# Command groups
@wArgs.group()
def cli():
    pass

@cli.command()
def hello(name: str):
    return f"Hello, {name}!"
```

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
├── __init__.py              # Public API exports (wArgs, Arg, group, etc.)
├── _version.py              # Version string
├── py.typed                 # PEP 561 marker
├── decorator.py             # @wArgs decorator, WargsWrapper, WargsClassWrapper
├── utilities.py             # Helper functions (explain, get_config, get_parser)
├── core/
│   ├── arg.py               # Arg() for Annotated type hints
│   ├── config.py            # ParameterInfo, FunctionInfo, TypeInfo, ParserConfig, DictExpansion
│   ├── exceptions.py        # Exception hierarchy (WargsError base class)
│   └── groups.py            # WargsGroup for @wArgs.group() command groups
├── builders/
│   ├── arguments.py         # ArgumentConfig builder, dict expansion, arg prefixing
│   ├── parser.py            # ArgumentParser construction
│   └── subcommands.py       # Class method → subcommand extraction
├── introspection/
│   ├── signatures.py        # Function signature analysis
│   ├── types.py             # Type annotation resolution
│   ├── docstrings.py        # Docstring parsing (Google/NumPy/Sphinx)
│   └── mro.py               # MRO traversal for inherited __init__ params
├── converters/
│   ├── builtin.py           # Built-in type converters
│   ├── dataclasses.py       # Dataclass converters
│   └── registry.py          # Converter registry with plugin support
├── completion/
│   ├── generator.py         # Shell completion generation
│   ├── bash.py              # Bash completion scripts
│   ├── zsh.py               # Zsh completion scripts
│   └── fish.py              # Fish completion scripts
└── plugins/
    ├── interface.py          # Plugin interface definitions
    └── registry.py           # Entry point plugin system
```

### Key Features

1. **Argument Prefixing**: All arguments are prefixed with callable name
   - `greet(name: str)` → `--greet-name`
   - `CLI.__init__(verbose: bool)` → `--CLI-verbose`

2. **Dictionary Expansion**: Dict defaults expand to multiple args
   - `f(config={"host": "localhost", "port": 8080})` → `--f-config-host`, `--f-config-port`

3. **Command Groups**: Click-style command groups via `@wArgs.group()`

4. **Shell Completion**: Auto-generated completions for bash/zsh/fish

5. **Plugin System**: Entry point-based converter plugins

### Key Data Structures

- `ParameterInfo`: Extracted parameter metadata (name, type, default, kind, description)
- `FunctionInfo`: Complete function metadata (name, parameters, return type, docstring)
- `TypeInfo`: Resolved type information (origin, args, is_optional, is_literal, is_enum, converter)
- `ParserConfig`: Full parser configuration with arguments and subcommands
- `DictExpansion`: Tracks dict parameters expanded into multiple CLI args
- `ArgumentConfig`: Single CLI argument configuration

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
- 100% test coverage target (currently 600 tests passing)
- ruff for linting/formatting (88 char line length)
- mypy strict mode

## Recent Changes

- Module renamed from `wargs` to `wArgs`
- Decorator renamed from `wargs` to `wArgs`
- Argument names prefixed with callable name (e.g., `--greet-name` instead of `--name`)
- Dictionary parameters auto-expand to multiple CLI arguments
- `dest` set to original param name when using prefixed flags
