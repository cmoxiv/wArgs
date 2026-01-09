# PRD: Frontend Requirements

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document details the public API design for wArgs - the interface that developers interact with when building CLI applications.

## Import Styles

wArgs supports multiple import patterns to accommodate different preferences:

### Style 1: Single Import (Recommended)

```python
from wArgs import wArgs

@wArgs
def main(name: str):
    print(f"Hello, {name}")
```

### Style 2: Multiple Imports

```python
from wArgs import wArgs, Arg, converter

@wArgs
def main(name: Annotated[str, Arg("-n", help="Your name")]):
    print(f"Hello, {name}")
```

### Style 3: Namespace Import

```python
import wArgs

@wArgs.wargs
def main(name: str):
    print(f"Hello, {name}")
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FE-001 | Support `from wArgs import wArgs` | Must | Primary pattern |
| REQ-FE-002 | Support `from wargs import *` | Should | Convenience |
| REQ-FE-003 | Support `import wArgs` namespace | Should | Alternative |
| REQ-FE-004 | Document recommended import style | Must | User guidance |

---

## Public API

### Core Decorator

```python
def wargs(
    func_or_class: Callable | type | None = None,
    *,
    prog: str | None = None,
    description: str | None = None,
    epilog: str | None = None,
    add_help: bool = True,
    allow_abbrev: bool = True,
    formatter_class: type | None = None,
) -> Callable | type:
    """
    Decorator to transform a function or class into a CLI command.

    Can be used with or without parentheses:
        @wArgs
        def main(name: str): ...

        @wArgs(prog="myapp")
        def main(name: str): ...

    Args:
        func_or_class: The function or class to decorate
        prog: Program name for help text (default: script name)
        description: Override docstring description
        epilog: Text to display after help
        add_help: Add -h/--help option (default: True)
        allow_abbrev: Allow abbreviated options (default: True)
        formatter_class: Custom argparse formatter

    Returns:
        Decorated function/class with CLI capabilities
    """
```

**Decorator Behavior:**

| Usage | Behavior |
|-------|----------|
| `@wArgs` | Use all defaults, introspect everything |
| `@wArgs()` | Same as above |
| `@wArgs(prog="myapp")` | Override specific settings |

**Invocation Behavior:**

| Call Style | Behavior |
|------------|----------|
| `func()` | Parse `sys.argv[1:]` and execute with parsed arguments |
| `func(["--name", "value"])` | Parse provided list and execute (for testing/programmatic use) |
| `func(name="value")` | Bypass parsing, call function directly with provided kwargs |

```python
@wArgs
def greet(name: str, count: int = 1):
    print(f"Hello, {name}!" * count)

# CLI invocation (parses sys.argv)
if __name__ == "__main__":
    greet()

# Programmatic invocation (for testing)
greet(["--name", "World", "--count", "2"])

# Direct call (bypasses wArgs entirely)
greet(name="World", count=3)
```

---

### Argument Configuration

```python
@dataclass
class Arg:
    """
    Configure individual argument behavior.

    Usage with Annotated:
        def main(name: Annotated[str, Arg("-n", help="Your name")]):
            ...

    Args:
        *flags: Short/long option flags ("-n", "--name")
        help: Help text for this argument
        metavar: Display name in help (e.g., "FILE" instead of "FILENAME")
        dest: Attribute name in parsed namespace
        action: argparse action (store, store_true, count, append, etc.)
        nargs: Number of arguments (int, '?', '*', '+')
        const: Constant value for certain actions
        default: Override default value
        type: Override type converter
        choices: Restrict to specific values
        required: Force argument to be required
        group: Argument group name for help organization
        exclusive: Mutually exclusive group name
        positional: Make this a positional argument
        hidden: Hide from help output
        skip: Exclude this parameter from CLI entirely (must have default)
    """
    flags: tuple[str, ...] = ()
    help: str = ""
    metavar: str | None = None
    dest: str | None = None
    action: str | None = None
    nargs: str | int | None = None
    const: Any = None
    default: Any = MISSING
    type: Callable[[str], Any] | None = None
    choices: Sequence | None = None
    required: bool | None = None
    group: str | None = None
    exclusive: str | None = None
    positional: bool = False
    hidden: bool = False
    skip: bool = False

    def __init__(self, *flags: str, **kwargs):
        self.flags = flags
        for key, value in kwargs.items():
            setattr(self, key, value)
```

**Usage Examples:**

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def process(
    # Positional argument
    input_file: Annotated[Path, Arg(positional=True, metavar="FILE")],

    # Short and long flag
    output: Annotated[Path, Arg("-o", "--output", metavar="FILE")] = None,

    # Counter flag
    verbose: Annotated[int, Arg("-v", action="count")] = 0,

    # Boolean flag
    dry_run: Annotated[bool, Arg("--dry-run", "-n")] = False,

    # Choices
    format: Annotated[str, Arg(choices=["json", "yaml", "toml"])] = "json",

    # Hidden argument
    debug: Annotated[bool, Arg(hidden=True)] = False,
):
    """Process a file and output results."""
    pass
```

---

### Converter Registration

```python
def converter(type_: type) -> Callable[[Callable], Callable]:
    """
    Register a type converter.

    Usage:
        @wArgs.converter(MyClass)
        def parse_myclass(value: str) -> MyClass:
            return MyClass.from_string(value)

    Args:
        type_: The type to register the converter for

    Returns:
        Decorator function
    """
```

**Example:**

```python
from wArgs import wArgs, converter
from datetime import datetime

@converter(datetime)
def parse_datetime(value: str) -> datetime:
    """Support multiple datetime formats."""
    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y"]:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {value}")

@wArgs
def schedule(event: str, when: datetime):
    """Schedule an event."""
    print(f"Scheduled '{event}' for {when}")
```

---

### Command Groups (Subcommands)

#### Class-Based API

```python
@wArgs
class CLI:
    """Main CLI with subcommands."""

    def __init__(self, verbose: bool = False):
        """Global options available to all subcommands."""
        self.verbose = verbose

    def init(self, name: str, template: str = "default"):
        """Initialize a new project."""
        if self.verbose:
            print(f"Creating project '{name}' from template '{template}'")

    def build(self, target: str = "release"):
        """Build the project."""
        if self.verbose:
            print(f"Building target: {target}")

if __name__ == "__main__":
    CLI()
```

#### Decorator-Based API

```python
from wArgs import wArgs

@wArgs.group()
def cli():
    """Main CLI with subcommands."""
    pass

@cli.command()
def init(name: str, template: str = "default"):
    """Initialize a new project."""
    print(f"Creating project '{name}'")

@cli.command()
def build(target: str = "release"):
    """Build the project."""
    print(f"Building target: {target}")

if __name__ == "__main__":
    cli()
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FE-005 | @wArgs.group() creates command group | Should | Decorator API |
| REQ-FE-006 | @group.command() registers subcommand | Should | Decorator API |
| REQ-FE-007 | Class methods as subcommands | Must | Class-based API |
| REQ-FE-008 | __init__ params as global options | Must | Shared arguments |

---

### Utility Functions

```python
def explain(func_or_class: Callable | type) -> None:
    """
    Print what wArgs detected from a decorated function/class.

    Useful for debugging and understanding wArgs behavior.

    Args:
        func_or_class: A @wArgs decorated function or class
    """

def get_parser(func_or_class: Callable | type) -> ArgumentParser:
    """
    Get the ArgumentParser instance for a decorated function/class.

    Useful for testing or advanced customization.

    Args:
        func_or_class: A @wArgs decorated function or class

    Returns:
        The configured ArgumentParser
    """

def get_config(func_or_class: Callable | type) -> ParserConfig:
    """
    Get the internal configuration for a decorated function/class.

    Args:
        func_or_class: A @wArgs decorated function or class

    Returns:
        ParserConfig dataclass with all detected settings
    """
```

---

### Shell Completion

```python
def install_completion(
    shell: str | None = None,
    path: Path | None = None,
) -> None:
    """
    Install shell completion for the current CLI.

    Auto-detects shell if not specified.

    Args:
        shell: Target shell (bash, zsh, fish) or None for auto-detect
        path: Custom installation path or None for default
    """

def generate_completion(shell: str) -> str:
    """
    Generate completion script without installing.

    Args:
        shell: Target shell (bash, zsh, fish)

    Returns:
        Completion script as string
    """
```

**Auto-Added Subcommand (classes/groups only):**

When using `@wArgs` on a class or `@wArgs.group()`, an `install-completion` subcommand is automatically available:

```bash
$ myapp install-completion
Detected shell: zsh
Installed completion to ~/.zfunc/_myapp
Run 'source ~/.zshrc' or start a new shell to enable completions.
```

**For simple functions (no subcommands):**

Use the utility function instead:

```python
from wArgs import wArgs, install_completion

@wArgs
def mytool(name: str):
    """My simple tool."""
    print(f"Hello, {name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "install-completion":
        install_completion(mytool)
    else:
        mytool()
```

---

## Public Exports (`__all__`)

```python
__all__ = [
    # Core
    "wargs",

    # Configuration
    "Arg",

    # Registration
    "converter",

    # Utilities
    "explain",
    "get_parser",
    "get_config",
    "install_completion",
    "generate_completion",

    # Types (for type hints)
    "ParserConfig",
    "ArgumentConfig",

    # Exceptions
    "WargsError",
    "ConfigurationError",
    "IntrospectionError",
    "ConversionError",
]
```

---

## Type Hints

All public APIs must have complete type hints:

```python
from typing import Annotated, Callable, TypeVar, overload

F = TypeVar('F', bound=Callable)
C = TypeVar('C', bound=type)

@overload
def wargs(func: F) -> F: ...

@overload
def wargs(func: None = None, *, prog: str | None = None, ...) -> Callable[[F], F]: ...

@overload
def wargs(cls: C) -> C: ...

@overload
def wargs(cls: None = None, *, prog: str | None = None, ...) -> Callable[[C], C]: ...

def wargs(
    func_or_class: F | C | None = None,
    *,
    prog: str | None = None,
    description: str | None = None,
    ...
) -> F | C | Callable[[F | C], F | C]:
    ...
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FE-009 | Complete type hints on all public APIs | Must | IDE support |
| REQ-FE-010 | Overloaded signatures for decorator flexibility | Should | Better type inference |
| REQ-FE-011 | py.typed marker (PEP 561) | Must | Type checker support |

---

## Error Messages

Public API errors should be clear and actionable:

```python
# Good error message
wargs.ConfigurationError: Cannot create CLI for function 'process'

  Problem: Parameter 'data' has type 'CustomClass' with no registered converter.

  Solutions:
    1. Register a converter:
       @wArgs.converter(CustomClass)
       def parse_custom(value: str) -> CustomClass:
           return CustomClass(value)

    2. Add a default value to make it optional:
       def process(data: CustomClass = None):

  Location: myapp.py:42
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FE-012 | Error messages include problem description | Must | Debuggability |
| REQ-FE-013 | Error messages include suggested solutions | Should | User guidance |
| REQ-FE-014 | Error messages include source location | Should | Debuggability |

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FE-001 | Support single import pattern | Must | Primary usage |
| REQ-FE-002 | Support star import | Should | Convenience |
| REQ-FE-003 | Support namespace import | Should | Alternative |
| REQ-FE-004 | Document recommended style | Must | User guidance |
| REQ-FE-005 | @wArgs.group() for command groups | Should | Decorator API |
| REQ-FE-006 | @group.command() for subcommands | Should | Decorator API |
| REQ-FE-007 | Class methods as subcommands | Must | Class-based API |
| REQ-FE-008 | __init__ as global options | Must | Shared arguments |
| REQ-FE-009 | Complete type hints | Must | IDE support |
| REQ-FE-010 | Overloaded decorator signatures | Should | Type inference |
| REQ-FE-011 | py.typed marker | Must | Type checker support |
| REQ-FE-012 | Clear error messages | Must | Debuggability |
| REQ-FE-013 | Solution suggestions in errors | Should | User guidance |
| REQ-FE-014 | Source location in errors | Should | Debuggability |
| REQ-FE-015 | `func()` parses sys.argv | Must | CLI invocation |
| REQ-FE-016 | `func([...])` parses provided list | Must | Testing/programmatic |
| REQ-FE-017 | `func(kwarg=...)` bypasses parsing | Must | Direct call support |

## Decisions

- [x] **`Arg` naming:** Keep as `Arg` - shorter, used frequently in annotations, matches CLI convention
- [x] **Programmatic invocation:** See Invocation Behavior table above
- [x] **Async functions:** Future feature (v2.0+), will auto-detect and use `asyncio.run()`
- [x] **`install-completion` for simple functions:** Not auto-added; use `wargs.install_completion(func)` utility instead

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| API surface too large | Learning curve | Clear "getting started" path |
| Type hints too complex | IDE confusion | Test with major IDEs |
| Decorator magic unexpected | User frustration | Explicit `explain()` function |
