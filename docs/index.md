# wArgs

> Just decorate and you're done.

**wArgs** is a Python decorator library that automatically generates argparse-based CLI interfaces from your function signatures, type hints, and docstrings.

## Why wArgs?

Writing CLI applications with argparse involves a lot of repetition:

```python
# Traditional argparse approach
import argparse

def greet(name: str, greeting: str = "Hello", times: int = 1) -> None:
    for _ in range(times):
        print(f"{greeting}, {name}!")

parser = argparse.ArgumentParser(description="Greet someone.")
parser.add_argument("--name", required=True, help="The name to greet")
parser.add_argument("--greeting", default="Hello", help="The greeting to use")
parser.add_argument("--times", type=int, default=1, help="Number of times to greet")

if __name__ == "__main__":
    args = parser.parse_args()
    greet(args.name, args.greeting, args.times)
```

With wArgs, the same CLI becomes:

```python
from wargs import wargs

@wargs
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

That's it. No duplication. No boilerplate. Just your function.

## Features

- **Zero boilerplate** - Turn any function into a CLI with a single decorator
- **Type-safe** - Automatic argument conversion based on type hints
- **Docstring parsing** - Extracts help text from Google, NumPy, and Sphinx docstrings
- **Nested subcommands** - Build complex CLI hierarchies with classes
- **Inheritance support** - Share options across commands via class inheritance
- **Custom converters** - Register converters for custom types
- **Debugging utilities** - Inspect generated parsers with `explain()`

## Quick Example

=== "Function-based CLI"

    ```python
    from wargs import wargs

    @wargs
    def hello(name: str, loud: bool = False) -> None:
        """Say hello to someone.

        Args:
            name: Person to greet
            loud: Use uppercase
        """
        msg = f"Hello, {name}!"
        print(msg.upper() if loud else msg)

    if __name__ == "__main__":
        hello()
    ```

    ```bash
    $ python hello.py --name World --loud
    HELLO, WORLD!
    ```

=== "Class-based CLI"

    ```python
    from wargs import wargs

    @wargs
    class Calculator:
        """A simple calculator."""

        def add(self, a: int, b: int) -> None:
            """Add two numbers."""
            print(a + b)

        def multiply(self, a: int, b: int) -> None:
            """Multiply two numbers."""
            print(a * b)

    if __name__ == "__main__":
        Calculator()
    ```

    ```bash
    $ python calc.py add --a 2 --b 3
    5
    $ python calc.py multiply --a 4 --b 5
    20
    ```

## Installation

```bash
pip install wargs
```

See the [Installation Guide](getting-started/installation.md) for more options.

## Next Steps

- [Quick Start](getting-started/quickstart.md) - Get up and running in 5 minutes
- [Tutorial](getting-started/tutorial.md) - Build a complete CLI application
- [User Guide](guide/basic-usage.md) - Learn all the features
- [API Reference](api/decorators.md) - Detailed API documentation
