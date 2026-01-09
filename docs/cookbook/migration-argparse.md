# Migrating from argparse

This guide shows how to convert argparse-based CLIs to wArgs.

## Basic Example

### Before (argparse)

```python
import argparse

def greet(name: str, greeting: str, times: int) -> None:
    for _ in range(times):
        print(f"{greeting}, {name}!")

def main():
    parser = argparse.ArgumentParser(description="Greet someone.")
    parser.add_argument("--name", required=True, help="Name to greet")
    parser.add_argument("--greeting", default="Hello", help="Greeting to use")
    parser.add_argument("--times", type=int, default=1, help="Number of times")

    args = parser.parse_args()
    greet(args.name, args.greeting, args.times)

if __name__ == "__main__":
    main()
```

### After (wArgs)

```python
from wargs import wargs

@wargs
def greet(name: str, greeting: str = "Hello", times: int = 1) -> None:
    """Greet someone.

    Args:
        name: Name to greet
        greeting: Greeting to use
        times: Number of times
    """
    for _ in range(times):
        print(f"{greeting}, {name}!")

if __name__ == "__main__":
    greet()
```

## Conversion Reference

### Required Arguments

```python
# argparse
parser.add_argument("--name", required=True)

# wArgs - no default = required
def func(name: str): ...
```

### Optional Arguments with Defaults

```python
# argparse
parser.add_argument("--count", type=int, default=1)

# wArgs - has default = optional
def func(count: int = 1): ...
```

### Boolean Flags

```python
# argparse
parser.add_argument("--verbose", action="store_true")

# wArgs - bool with False default
def func(verbose: bool = False): ...
```

### Choices

```python
# argparse
parser.add_argument("--format", choices=["json", "xml", "csv"])

# wArgs - use Literal
from typing import Literal
def func(format: Literal["json", "xml", "csv"]): ...
```

### Type Conversion

```python
# argparse
parser.add_argument("--count", type=int)
parser.add_argument("--rate", type=float)

# wArgs - use type hints
def func(count: int, rate: float): ...
```

### Multiple Values (nargs)

```python
# argparse
parser.add_argument("--files", nargs="+")

# wArgs - use list
def func(files: list[str]): ...
```

### Positional Arguments

```python
# argparse
parser.add_argument("filename")

# wArgs
from typing import Annotated
from wargs import Arg
def func(filename: Annotated[str, Arg(positional=True)]): ...
```

### Short Flags

```python
# argparse
parser.add_argument("-n", "--name")

# wArgs
from typing import Annotated
from wargs import Arg
def func(name: Annotated[str, Arg("-n")]): ...
```

### Help Text

```python
# argparse
parser.add_argument("--name", help="The name to use")

# wArgs - use docstring
def func(name: str) -> None:
    """Do something.

    Args:
        name: The name to use
    """
```

### Metavar

```python
# argparse
parser.add_argument("--config", metavar="FILE")

# wArgs
from typing import Annotated
from wargs import Arg
def func(config: Annotated[str, Arg(metavar="FILE")]): ...
```

### Argument Groups

```python
# argparse
group = parser.add_argument_group("Network")
group.add_argument("--host")
group.add_argument("--port", type=int)

# wArgs
from typing import Annotated
from wargs import Arg
def func(
    host: Annotated[str, Arg(group="Network")],
    port: Annotated[int, Arg(group="Network")],
): ...
```

### Mutually Exclusive

```python
# argparse
group = parser.add_mutually_exclusive_group()
group.add_argument("--json", action="store_true")
group.add_argument("--xml", action="store_true")

# wArgs
from typing import Annotated
from wargs import Arg
def func(
    json: Annotated[bool, Arg(mutually_exclusive="format")] = False,
    xml: Annotated[bool, Arg(mutually_exclusive="format")] = False,
): ...
```

## Subparsers

### Before (argparse)

```python
import argparse

def add(args):
    print(args.a + args.b)

def multiply(args):
    print(args.a * args.b)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

add_parser = subparsers.add_parser("add", help="Add numbers")
add_parser.add_argument("--a", type=int, required=True)
add_parser.add_argument("--b", type=int, required=True)
add_parser.set_defaults(func=add)

mul_parser = subparsers.add_parser("multiply", help="Multiply numbers")
mul_parser.add_argument("--a", type=int, required=True)
mul_parser.add_argument("--b", type=int, required=True)
mul_parser.set_defaults(func=multiply)

args = parser.parse_args()
args.func(args)
```

### After (wArgs)

```python
from wargs import wargs

@wargs
class Calculator:
    """Calculator CLI."""

    def add(self, a: int, b: int) -> None:
        """Add numbers."""
        print(a + b)

    def multiply(self, a: int, b: int) -> None:
        """Multiply numbers."""
        print(a * b)

if __name__ == "__main__":
    Calculator()
```

## Global Options

### Before (argparse)

```python
parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
subparsers = parser.add_subparsers()
# ... add subparsers

args = parser.parse_args()
if args.verbose:
    print("Verbose mode")
```

### After (wArgs)

```python
@wargs
class CLI:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def run(self) -> None:
        if self.verbose:
            print("Verbose mode")
```

## Complete Migration Example

### Before (100+ lines)

```python
import argparse
import sys

def setup_parser():
    parser = argparse.ArgumentParser(
        prog="myapp",
        description="My application"
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("-c", "--config", default="config.yml",
                        help="Configuration file")

    subparsers = parser.add_subparsers(dest="command")

    # Init command
    init = subparsers.add_parser("init", help="Initialize project")
    init.add_argument("--name", required=True, help="Project name")
    init.add_argument("--template", choices=["basic", "full"],
                      default="basic", help="Template to use")

    # Build command
    build = subparsers.add_parser("build", help="Build project")
    build.add_argument("--output", "-o", default="dist",
                       help="Output directory")
    build.add_argument("--minify", action="store_true",
                       help="Minify output")

    return parser

def cmd_init(args):
    print(f"Initializing {args.name} with {args.template} template")

def cmd_build(args):
    print(f"Building to {args.output}")
    if args.minify:
        print("Minifying...")

def main():
    parser = setup_parser()
    args = parser.parse_args()

    if args.verbose:
        print(f"Using config: {args.config}")

    if args.command == "init":
        cmd_init(args)
    elif args.command == "build":
        cmd_build(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### After (30 lines)

```python
from typing import Annotated, Literal
from wargs import wargs, Arg

@wargs(prog="myapp")
class CLI:
    """My application."""

    def __init__(
        self,
        verbose: Annotated[bool, Arg("-v")] = False,
        config: Annotated[str, Arg("-c")] = "config.yml",
    ) -> None:
        self.verbose = verbose
        if verbose:
            print(f"Using config: {config}")

    def init(
        self,
        name: str,
        template: Literal["basic", "full"] = "basic",
    ) -> None:
        """Initialize project."""
        print(f"Initializing {name} with {template} template")

    def build(
        self,
        output: Annotated[str, Arg("-o")] = "dist",
        minify: bool = False,
    ) -> None:
        """Build project."""
        print(f"Building to {output}")
        if minify:
            print("Minifying...")

if __name__ == "__main__":
    CLI()
```
