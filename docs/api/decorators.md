# Decorators

## wArgs

The main decorator for creating CLI applications.

::: wArgs.wArgs
    options:
      show_root_heading: true
      show_source: false

## WargsWrapper

Wrapper class for decorated functions.

::: wArgs.WargsWrapper
    options:
      show_root_heading: true
      members:
        - func
        - parser
        - parse_args
        - run

## WargsClassWrapper

Wrapper class for decorated classes.

::: wArgs.WargsClassWrapper
    options:
      show_root_heading: true
      members:
        - cls
        - parser
        - parse_args
        - run

## Arg

Metadata class for configuring arguments.

::: wArgs.Arg
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Function Decorator

```python
from wArgs import wArgs

@wArgs
def greet(name: str) -> None:
    """Greet someone."""
    print(f"Hello, {name}!")

# Usage
greet()  # CLI mode
greet(name="World")  # Direct call
greet.run(["--name", "World"])  # Explicit
```

### Class Decorator

```python
from wArgs import wArgs

@wArgs
class CLI:
    """My CLI tool."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def run(self) -> None:
        """Run the command."""
        print("Running...")

# Usage
CLI()  # CLI mode
CLI(verbose=True)  # Direct instantiation
CLI.run(["--verbose", "run"])  # Explicit
```

### With Options

```python
@wArgs(
    prog="myapp",
    description="My application",
    add_help=True,
    formatter_class="RawDescriptionHelpFormatter",
)
def my_command() -> None:
    ...
```

### With Arg Metadata

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def process(
    input_file: Annotated[str, Arg("-i", help="Input file")],
    verbose: Annotated[bool, Arg("-v")] = False,
) -> None:
    ...
```
