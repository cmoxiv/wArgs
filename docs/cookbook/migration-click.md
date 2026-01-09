# Migrating from Click

This guide shows how to convert Click-based CLIs to wArgs.

## Key Differences

| Feature | Click | wArgs |
|---------|-------|-------|
| Decorator | `@click.command()` | `@wargs` |
| Options | `@click.option()` | Type hints + `Arg` |
| Arguments | `@click.argument()` | `Arg(positional=True)` |
| Groups | `@click.group()` | Class with methods |
| Help | `help=` parameter | Docstrings |
| Types | `type=click.INT` | Type hints |

## Basic Command

### Before (Click)

```python
import click

@click.command()
@click.option("--name", required=True, help="Name to greet")
@click.option("--count", default=1, type=int, help="Number of times")
def greet(name: str, count: int):
    """Greet someone."""
    for _ in range(count):
        click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

### After (wArgs)

```python
from wargs import wargs

@wargs
def greet(name: str, count: int = 1) -> None:
    """Greet someone.

    Args:
        name: Name to greet
        count: Number of times
    """
    for _ in range(count):
        print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

## Conversion Reference

### Options

```python
# Click
@click.option("--name", required=True)
@click.option("--count", default=1, type=int)

# wArgs
def func(name: str, count: int = 1): ...
```

### Short Options

```python
# Click
@click.option("-n", "--name")

# wArgs
from typing import Annotated
from wargs import Arg
def func(name: Annotated[str, Arg("-n")]): ...
```

### Boolean Flags

```python
# Click
@click.option("--verbose/--no-verbose", default=False)
# or
@click.option("--verbose", is_flag=True)

# wArgs
def func(verbose: bool = False): ...
```

### Multiple Values

```python
# Click
@click.option("--file", multiple=True)

# wArgs
def func(file: list[str]): ...
```

### Choices

```python
# Click
@click.option("--format", type=click.Choice(["json", "xml"]))

# wArgs
from typing import Literal
def func(format: Literal["json", "xml"]): ...
```

### Arguments (Positional)

```python
# Click
@click.argument("filename")

# wArgs
from typing import Annotated
from wargs import Arg
def func(filename: Annotated[str, Arg(positional=True)]): ...
```

### File Arguments

```python
# Click
@click.argument("input", type=click.File("r"))
@click.argument("output", type=click.File("w"))

# wArgs - use Path, handle file opening yourself
from pathlib import Path
def func(input: Path, output: Path) -> None:
    content = input.read_text()
    output.write_text(content)
```

### Path Arguments

```python
# Click
@click.option("--path", type=click.Path(exists=True))

# wArgs
from pathlib import Path
def func(path: Path): ...
# Note: wArgs doesn't validate existence; do it in your code
```

## Command Groups

### Before (Click)

```python
import click

@click.group()
@click.option("--verbose", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.argument("name")
@click.pass_context
def add(ctx, name):
    """Add an item."""
    if ctx.obj["verbose"]:
        click.echo(f"Adding {name}")
    click.echo(f"Added: {name}")

@cli.command()
@click.argument("item_id", type=int)
@click.pass_context
def remove(ctx, item_id):
    """Remove an item."""
    if ctx.obj["verbose"]:
        click.echo(f"Removing {item_id}")
    click.echo(f"Removed: {item_id}")

if __name__ == "__main__":
    cli()
```

### After (wArgs)

```python
from typing import Annotated
from wargs import wargs, Arg

@wargs
class CLI:
    """CLI tool."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def add(self, name: Annotated[str, Arg(positional=True)]) -> None:
        """Add an item."""
        if self.verbose:
            print(f"Adding {name}")
        print(f"Added: {name}")

    def remove(self, item_id: Annotated[int, Arg(positional=True)]) -> None:
        """Remove an item."""
        if self.verbose:
            print(f"Removing {item_id}")
        print(f"Removed: {item_id}")

if __name__ == "__main__":
    CLI()
```

## Context and State

### Before (Click)

```python
import click

@click.group()
@click.option("--config", default="config.yml")
@click.pass_context
def cli(ctx, config):
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)

@cli.command()
@click.pass_context
def show(ctx):
    print(ctx.obj["config"])
```

### After (wArgs)

```python
from wargs import wargs

@wargs
class CLI:
    def __init__(self, config: str = "config.yml") -> None:
        self.config_data = load_config(config)

    def show(self) -> None:
        print(self.config_data)
```

## Callbacks and Validation

### Before (Click)

```python
def validate_port(ctx, param, value):
    if value < 1 or value > 65535:
        raise click.BadParameter("Port must be 1-65535")
    return value

@click.command()
@click.option("--port", type=int, callback=validate_port)
def serve(port):
    print(f"Serving on port {port}")
```

### After (wArgs)

```python
from wargs import wargs

@wargs
def serve(port: int) -> None:
    """Start server.

    Args:
        port: Port number (1-65535)
    """
    if port < 1 or port > 65535:
        raise ValueError("Port must be 1-65535")
    print(f"Serving on port {port}")
```

## Progress Bars

Click has built-in progress bars. With wArgs, use tqdm or rich:

```python
from wargs import wargs
from tqdm import tqdm

@wargs
def process(files: list[str]) -> None:
    """Process files."""
    for f in tqdm(files, desc="Processing"):
        # process file
        pass
```

## Prompts

Click has built-in prompts. With wArgs, use standard input:

```python
from wargs import wargs

@wargs
def login(username: str, password: str = "") -> None:
    """Login to service."""
    if not password:
        password = input("Password: ")
    print(f"Logging in as {username}")
```

Or use `getpass` for hidden input:

```python
from getpass import getpass
from wargs import wargs

@wargs
def login(username: str) -> None:
    """Login to service."""
    password = getpass("Password: ")
    print(f"Logging in as {username}")
```

## Complete Migration Example

### Before (Click)

```python
import click

@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("-c", "--config", default="config.yml", help="Config file")
@click.pass_context
def cli(ctx, verbose, config):
    """My CLI application."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

@cli.command()
@click.argument("name")
@click.option("--template", type=click.Choice(["basic", "full"]),
              default="basic", help="Project template")
@click.pass_context
def init(ctx, name, template):
    """Initialize a new project."""
    if ctx.obj["verbose"]:
        click.echo(f"Config: {ctx.obj['config']}")
    click.echo(f"Creating {name} with {template} template")

@cli.command()
@click.option("-o", "--output", default="dist", help="Output directory")
@click.option("--minify", is_flag=True, help="Minify output")
@click.pass_context
def build(ctx, output, minify):
    """Build the project."""
    if ctx.obj["verbose"]:
        click.echo(f"Building to {output}")
    if minify:
        click.echo("Minifying...")
    click.echo("Build complete!")

if __name__ == "__main__":
    cli()
```

### After (wArgs)

```python
from typing import Annotated, Literal
from wargs import wargs, Arg

@wargs
class CLI:
    """My CLI application."""

    def __init__(
        self,
        verbose: Annotated[bool, Arg("-v")] = False,
        config: Annotated[str, Arg("-c")] = "config.yml",
    ) -> None:
        self.verbose = verbose
        self.config = config

    def init(
        self,
        name: Annotated[str, Arg(positional=True)],
        template: Literal["basic", "full"] = "basic",
    ) -> None:
        """Initialize a new project."""
        if self.verbose:
            print(f"Config: {self.config}")
        print(f"Creating {name} with {template} template")

    def build(
        self,
        output: Annotated[str, Arg("-o")] = "dist",
        minify: bool = False,
    ) -> None:
        """Build the project."""
        if self.verbose:
            print(f"Building to {output}")
        if minify:
            print("Minifying...")
        print("Build complete!")

if __name__ == "__main__":
    CLI()
```

## Why Migrate?

1. **Less boilerplate** - No separate decorator for each option
2. **Type safety** - Type hints are the source of truth
3. **Standard Python** - Uses standard library only
4. **Testability** - Easy to test directly or via CLI
5. **IDE support** - Better autocomplete and type checking
