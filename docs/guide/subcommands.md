# Subcommands

wArgs supports building complex CLI applications with subcommands using classes.

## Basic Class CLI

Decorate a class to turn its methods into subcommands:

```python
from wargs import wargs

@wargs
class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> None:
        """Add two numbers."""
        print(a + b)

    def subtract(self, a: int, b: int) -> None:
        """Subtract two numbers."""
        print(a - b)

if __name__ == "__main__":
    Calculator()
```

```bash
$ python calc.py --help
usage: calc.py [-h] {add,subtract} ...

A simple calculator.

positional arguments:
  {add,subtract}
    add           Add two numbers.
    subtract      Subtract two numbers.

$ python calc.py add --a 5 --b 3
8

$ python calc.py subtract --a 10 --b 4
6
```

## Method Naming

Python method names with underscores become hyphenated subcommands:

```python
@wargs
class CLI:
    def list_users(self) -> None:
        """List all users."""
        ...

    def add_user(self, name: str) -> None:
        """Add a new user."""
        ...
```

```bash
$ python app.py list-users
$ python app.py add-user --name alice
```

## Private Methods

Methods starting with `_` are excluded from subcommands:

```python
@wargs
class CLI:
    def public(self) -> None:
        """This is a subcommand."""
        self._helper()

    def _helper(self) -> None:
        """This is NOT a subcommand."""
        print("Helper method")
```

```bash
$ python app.py --help
  {public}
    public    This is a subcommand.
# _helper is not listed
```

## Global Options

Parameters in `__init__` become global options:

```python
@wargs
class CLI:
    """File manager with global options."""

    def __init__(self, verbose: bool = False, dry_run: bool = False) -> None:
        """Initialize with global options.

        Args:
            verbose: Enable verbose output.
            dry_run: Don't actually perform operations.
        """
        self.verbose = verbose
        self.dry_run = dry_run

    def delete(self, path: str) -> None:
        """Delete a file."""
        if self.verbose:
            print(f"Deleting: {path}")
        if not self.dry_run:
            print(f"Deleted: {path}")
        else:
            print("(dry run - not deleted)")

    def copy(self, source: str, dest: str) -> None:
        """Copy a file."""
        if self.verbose:
            print(f"Copying: {source} -> {dest}")
        if not self.dry_run:
            print(f"Copied: {source} -> {dest}")
```

```bash
$ python files.py --help
usage: files.py [-h] [--verbose] [--dry-run] {delete,copy} ...

File manager with global options.

options:
  --verbose   Enable verbose output.
  --dry-run   Don't actually perform operations.

$ python files.py --verbose --dry-run delete --path test.txt
Deleting: test.txt
(dry run - not deleted)
```

Global options must come **before** the subcommand:

```bash
$ python files.py --verbose delete --path test.txt  # Correct
$ python files.py delete --verbose --path test.txt  # Wrong!
```

## Subcommand Help

Each subcommand has its own help:

```bash
$ python calc.py add --help
usage: calc.py add [-h] --a A --b B

Add two numbers.

options:
  -h, --help  show this help message and exit
  --a A
  --b B
```

## Combining Global and Local Options

```python
@wargs
class CLI:
    def __init__(self, config: str = "config.yml") -> None:
        """Global options.

        Args:
            config: Path to configuration file.
        """
        self.config = config

    def deploy(self, env: str, force: bool = False) -> None:
        """Deploy the application.

        Args:
            env: Target environment.
            force: Force deployment even if checks fail.
        """
        print(f"Using config: {self.config}")
        print(f"Deploying to: {env}")
        if force:
            print("Force mode enabled")
```

```bash
$ python app.py --config prod.yml deploy --env production --force
Using config: prod.yml
Deploying to: production
Force mode enabled
```

## Direct Instantiation

You can still create instances directly:

```python
@wargs
class Calculator:
    def add(self, a: int, b: int) -> None:
        print(a + b)

# CLI mode
if __name__ == "__main__":
    Calculator()

# Direct use in code
calc = Calculator()
calc.add(2, 3)  # Prints: 5
```

## No Subcommand

When no subcommand is given, help is shown:

```bash
$ python calc.py
usage: calc.py [-h] {add,subtract} ...

A simple calculator.

positional arguments:
  {add,subtract}
    add           Add two numbers.
    subtract      Subtract two numbers.
```

## Customizing the Parser

```python
@wargs(
    prog="myapp",
    description="Custom description",
)
class CLI:
    ...
```

## Next Steps

- [Inheritance](inheritance.md) - Share options across commands
- [Advanced](advanced.md) - Advanced patterns
