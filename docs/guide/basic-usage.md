# Basic Usage

This guide covers the fundamentals of using wArgs to create CLI applications.

## The @wargs Decorator

The `@wargs` decorator transforms a function or class into a CLI:

```python
from wargs import wargs

@wargs
def my_command(name: str) -> None:
    """Do something with a name."""
    print(f"Hello, {name}!")
```

### With Options

You can pass options to customize the CLI:

```python
@wargs(
    prog="myapp",           # Program name in help
    description="My app",    # Override docstring description
    add_help=True,          # Add -h/--help (default: True)
)
def my_command(name: str) -> None:
    ...
```

## Parameters to Arguments

wArgs converts function parameters to CLI arguments:

| Parameter | CLI Argument |
|-----------|--------------|
| `name: str` | `--name NAME` (required) |
| `name: str = "default"` | `--name NAME` (optional, default: "default") |
| `verbose: bool = False` | `--verbose` (flag) |
| `count: int = 1` | `--count COUNT` (optional, converted to int) |

### Naming Conventions

Python underscores become CLI hyphens:

```python
@wargs
def process(input_file: str, output_dir: str) -> None:
    ...
```

```bash
$ python app.py --input-file data.txt --output-dir ./out
```

## Required vs Optional

Arguments are **required** if they have no default value:

```python
@wargs
def greet(
    name: str,              # Required
    greeting: str = "Hi",   # Optional (default: "Hi")
) -> None:
    print(f"{greeting}, {name}!")
```

```bash
$ python greet.py --name World
Hi, World!

$ python greet.py
# Error: --name is required
```

## Boolean Flags

Boolean parameters with `False` default become flags:

```python
@wargs
def build(
    debug: bool = False,     # --debug flag
    optimize: bool = False,  # --optimize flag
) -> None:
    print(f"Debug: {debug}, Optimize: {optimize}")
```

```bash
$ python build.py
Debug: False, Optimize: False

$ python build.py --debug
Debug: True, Optimize: False

$ python build.py --debug --optimize
Debug: True, Optimize: True
```

!!! note
    Only `bool` parameters with `False` as default become flags.
    Other boolean parameters work like regular arguments.

## Calling Decorated Functions

Decorated functions can be called in multiple ways:

### CLI Mode (no arguments)

When called without arguments, parses `sys.argv`:

```python
if __name__ == "__main__":
    my_command()  # Parses CLI arguments
```

### Direct Call (with arguments)

When called with arguments, bypasses CLI parsing:

```python
# Direct call - no CLI parsing
my_command(name="World")

# Also works with positional args
my_command("World")
```

### Explicit Parsing

Use `.run()` or `.parse_args()` for explicit control:

```python
# Parse and execute
result = my_command.run(["--name", "World"])

# Just parse, don't execute
args = my_command.parse_args(["--name", "World"])
print(args.name)  # "World"
```

## Accessing the Parser

Get the underlying `ArgumentParser`:

```python
from wargs import wargs, get_parser

@wargs
def my_command(name: str) -> None:
    ...

# Get the parser
parser = get_parser(my_command)

# Or via property
parser = my_command.parser

# Extend it if needed
parser.add_argument("--extra", help="Extra option")
```

## Debugging with explain()

Use `explain()` to see how wArgs interprets your function:

```python
from wargs import wargs, explain

@wargs
def greet(name: str, count: int = 1) -> None:
    """Greet someone.

    Args:
        name: Person to greet
        count: Number of times
    """
    ...

print(explain(greet))
```

Output:

```
Function: greet
Type: Single-command CLI

Arguments:
  --name (str) [required]
  --count (int) [default: 1]
```

Use `verbose=True` for more detail:

```python
print(explain(greet, verbose=True))
```

## Debug Output

Set `WARGS_DEBUG=1` for debug output:

```bash
$ WARGS_DEBUG=1 python greet.py --name World
[wargs] Building parser for function: greet
[wargs] Parsing args: ['--name', 'World']
[wargs] Parsed result: Namespace(name='World', count=1)
Hello, World!
```

## Next Steps

- [Type System](type-system.md) - All supported types
- [Docstrings](docstrings.md) - Help text from docstrings
- [Subcommands](subcommands.md) - Class-based CLIs
