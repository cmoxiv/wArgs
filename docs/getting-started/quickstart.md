# Quick Start

This guide will get you up and running with wArgs in 5 minutes.

## Your First CLI

Create a file called `greet.py`:

```python
from wArgs import wArgs

@wArgs
def greet(name: str, greeting: str = "Hello") -> None:
    """Greet someone.

    Args:
        name: The person to greet
        greeting: The greeting to use
    """
    print(f"{greeting}, {name}!")

if __name__ == "__main__":
    greet()
```

Run it:

```bash
$ python greet.py --help
usage: greet.py [-h] --name NAME [--greeting GREETING]

Greet someone.

options:
  -h, --help           show this help message and exit
  --name NAME          The person to greet
  --greeting GREETING  The greeting to use (default: 'Hello')

$ python greet.py --name World
Hello, World!

$ python greet.py --name Alice --greeting Hi
Hi, Alice!
```

## How It Works

wArgs extracts everything it needs from your function:

| Source | Used For |
|--------|----------|
| Function name | Program name |
| Docstring summary | CLI description |
| Parameter names | Argument names (`--name`) |
| Type hints | Argument types and conversion |
| Default values | Optional vs required, default values |
| Docstring `Args:` | Help text for each argument |

## Type Conversion

wArgs automatically converts arguments based on type hints:

```python
@wArgs
def process(
    count: int,           # Converted to integer
    rate: float,          # Converted to float
    verbose: bool,        # Boolean flag (--verbose)
    files: list[str],     # Multiple values (--files a.txt b.txt)
) -> None:
    print(f"Processing {count} items at {rate}x")
    if verbose:
        print(f"Files: {files}")
```

```bash
$ python process.py --count 5 --rate 1.5 --verbose --files a.txt b.txt
Processing 5 items at 1.5x
Files: ['a.txt', 'b.txt']
```

## Boolean Flags

Boolean parameters with `False` default become flags:

```python
@wArgs
def build(debug: bool = False, optimize: bool = False) -> None:
    """Build the project."""
    print(f"Debug: {debug}, Optimize: {optimize}")
```

```bash
$ python build.py --debug
Debug: True, Optimize: False

$ python build.py --debug --optimize
Debug: True, Optimize: True
```

## Subcommands with Classes

Use a class to create subcommands:

```python
from wArgs import wArgs

@wArgs
class CLI:
    """File management tool."""

    def list(self, path: str = ".") -> None:
        """List files in a directory."""
        print(f"Listing {path}")

    def copy(self, source: str, dest: str) -> None:
        """Copy a file."""
        print(f"Copying {source} to {dest}")

if __name__ == "__main__":
    CLI()
```

```bash
$ python files.py --help
usage: files.py [-h] {list,copy} ...

File management tool.

positional arguments:
  {list,copy}
    list       List files in a directory.
    copy       Copy a file.

$ python files.py list --path /tmp
Listing /tmp

$ python files.py copy --source a.txt --dest b.txt
Copying a.txt to b.txt
```

## Next Steps

- [Tutorial](tutorial.md) - Build a complete CLI application step by step
- [Basic Usage](../guide/basic-usage.md) - Learn more about decorating functions
- [Type System](../guide/type-system.md) - All supported types
- [Subcommands](../guide/subcommands.md) - Complex CLI hierarchies
