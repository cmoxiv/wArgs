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

Full documentation is available at [https://wargs.readthedocs.io](https://wargs.readthedocs.io)

## Requirements

- Python 3.8+
- No runtime dependencies

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
