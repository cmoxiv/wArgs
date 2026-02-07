# wArgs

> Just decorate and you're done.

[![CI](https://github.com/cmoxiv/wArgs/actions/workflows/ci.yml/badge.svg)](https://github.com/cmoxiv/wArgs/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/wargs.svg)](https://badge.fury.io/py/wargs)
[![Python versions](https://img.shields.io/pypi/pyversions/wargs.svg)](https://pypi.org/project/wargs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**wArgs** is a Python decorator library that automatically generates argparse-based CLI interfaces from your function signatures, type hints, and docstrings.

## Features

- **Zero boilerplate** - Turn any function into a CLI with a single decorator
- **Type-safe** - Automatic argument conversion based on type hints
- **Docstring parsing** - Extracts help text from Google, NumPy, and Sphinx docstrings
- **Nested subcommands** - Build complex CLI hierarchies with classes
- **Shell completion** - Auto-generated completions for bash, zsh, and fish
- **Plugin system** - Extend functionality via entry points

## Installation

```bash
pip install git+https://github.com/cmoxiv/wArgs.git
```

## Quick Start

```python
from wArgs import wArgs

@wArgs
def greet(name: str, greeting: str = "Hello", times: int = 1) -> None:
    """Greet someone.

    Args:
        name: The name to greet
        greeting: The greeting to use
        times: Number of times to greet
    """
    for _ in range(times):
        print(f"{greeting}, {name}!")

if __name__ == "__main__":
    greet()
```

```bash
$ python greet.py --help
usage: greet.py [-h] --name NAME [--greeting GREETING] [--times TIMES]

Greet someone.

options:
  -h, --help           show this help message and exit
  --name NAME          The name to greet
  --greeting GREETING  The greeting to use (default: Hello)
  --times TIMES        Number of times to greet (default: 1)

$ python greet.py --name World --times 3
Hello, World!
Hello, World!
Hello, World!
```

## Subcommands with Classes

```python
from wArgs import wArgs

@wArgs
class CLI:
    """My awesome CLI tool."""

    def add(self, a: int, b: int) -> None:
        """Add two numbers."""
        print(a + b)

    def multiply(self, a: int, b: int) -> None:
        """Multiply two numbers."""
        print(a * b)

if __name__ == "__main__":
    CLI()
```

```bash
$ python calc.py add --a 2 --b 3
5

$ python calc.py multiply --a 2 --b 3
6
```

## Type Support

wArgs supports all common Python types out of the box:

- Primitives: `str`, `int`, `float`, `bool`
- Collections: `list`, `tuple`, `set`, `frozenset`
- Optionals: `Optional[T]`, `T | None`
- Literals: `Literal["a", "b", "c"]`
- Enums: Any `enum.Enum` subclass
- Paths: `pathlib.Path`
- And more...

## Documentation

Full documentation is available at [https://cmoxiv.github.io/wArgs/](https://cmoxiv.github.io/wArgs/)

## Requirements

- Python 3.8+
- No runtime dependencies

## Testing & Quality

wArgs maintains high code quality standards with comprehensive test coverage and rigorous quality checks.

### Test Suite

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=wArgs --cov-report=term-missing
```

**Current Statistics:**
- ✅ **600 tests** passing (100% pass rate)
- 📊 **94% code coverage** (target: 97%)
- ⚡ **2.13 seconds** test execution time
- 🧪 **19 test modules** covering all components
  - 18 unit test modules
  - 1 property-based test module (Hypothesis)

### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| **Core** | ~150 | Decorator, configuration, exceptions |
| **Introspection** | ~200 | Signatures, types, docstrings, MRO |
| **Builders** | ~100 | Argument building, parser construction |
| **Converters** | ~80 | Type conversion, registry, plugins |
| **Completion** | ~50 | Shell completion generation |
| **Integration** | ~20 | End-to-end workflows |

### Coverage Report

| Module | Coverage | Notes |
|--------|----------|-------|
| Core modules | 100% | Full coverage |
| Introspection | 93-99% | Type resolution edge cases |
| Builders | 84-95% | Dictionary expansion paths |
| Converters | 100% | Full coverage |
| Completion | 97-99% | Shell-specific paths |

*See `htmlcov/index.html` for detailed coverage report after running `pytest --cov`*

### Quality Checks

```bash
# Run all quality checks
tox

# Or run individual checks:
ruff check wArgs tests      # Linting
ruff format --check wArgs tests  # Formatting
mypy wArgs                  # Type checking
```

### CI/CD

All tests and quality checks run automatically on:
- Every push
- Every pull request
- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Multiple platforms (Linux, macOS, Windows)

See [CI status](https://github.com/cmoxiv/wArgs/actions)

## Development

```bash
# Clone the repository
git clone https://github.com/cmoxiv/wArgs.git
cd wargs

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check wArgs tests
ruff format --check wArgs tests

# Run type checking
mypy wArgs
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
