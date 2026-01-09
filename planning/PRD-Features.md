# PRD: Features & User Stories

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document details the functional requirements for wArgs, organized by feature area with user stories and acceptance criteria.

## Feature Prioritization (MoSCoW)

| Priority | Features |
|----------|----------|
| **Must** | Core decorator, type introspection, docstring parsing, class-based subcommands, argparse parity, MRO traversal |
| **Should** | Shell completion, nested decorator patterns, custom actions |
| **Could** | Config file support |
| **Won't (v1)** | Module-based command hierarchy |

---

## Core Features (Must-Have)

### F-001: Basic Decorator

**Description:** Single decorator transforms a function into a CLI command.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-001 | As a developer, I want to add `@wArgs` to my function so that it becomes a CLI command | Function runs with parsed arguments when script is executed |
| US-002 | As a developer, I want my function's parameters to become CLI arguments automatically | All parameters appear in `--help` output |
| US-003 | As a developer, I want default values to make arguments optional | Parameters with defaults are optional CLI args |

**Example Usage:**

```python
from wArgs import wArgs

@wArgs
def greet(name: str, count: int = 1):
    """Greet someone multiple times.

    Args:
        name: The person to greet
        count: Number of greetings
    """
    for _ in range(count):
        print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()
```

**CLI Behavior:**
```bash
$ python greet.py --help
usage: greet.py [-h] --name NAME [--count COUNT]

Greet someone multiple times.

options:
  -h, --help     show this help message and exit
  --name NAME    The person to greet
  --count COUNT  Number of greetings (default: 1)

$ python greet.py --name World --count 3
Hello, World!
Hello, World!
Hello, World!
```

---

### F-002: Type Introspection

**Description:** Automatically extract and apply type information from annotations.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-004 | As a developer, I want type hints to define argument types | `int` annotation creates integer argument |
| US-005 | As a developer, I want `bool` types to create flags | `--flag` / `--no-flag` behavior |
| US-006 | As a developer, I want `Path` types to validate file paths | Path validation and conversion applied |
| US-007 | As a developer, I want `list[str]` to accept multiple values | `--items a --items b` or `--items a b` |
| US-008 | As a developer, I want `Optional[X]` for nullable arguments | Argument is optional, accepts None |
| US-009 | As a developer, I want `Union[X, Y]` for multiple valid types | Attempts type conversion in order |
| US-010 | As a developer, I want `Literal['a', 'b']` for choices | Creates `choices=['a', 'b']` in argparse |
| US-011 | As a developer, I want `Enum` types for constrained values | Enum members become valid choices |

**Supported Types:**

| Type | argparse Behavior |
|------|------------------|
| `str` | Default string argument |
| `int` | `type=int` |
| `float` | `type=float` |
| `bool` | `action='store_true'` / `'store_false'` |
| `Path` | `type=Path` with validation |
| `list[T]` | `nargs='*'` or `action='append'` |
| `tuple[T, ...]` | `nargs='+'` |
| `set[T]` | `nargs='*'` with deduplication |
| `Optional[T]` | Optional argument, can be None |
| `Union[T1, T2]` | Try T1 first, then T2 |
| `Literal['a', 'b']` | `choices=['a', 'b']` |
| `Enum` subclass | `choices=[e.value for e in Enum]` |
| Custom class | Use class constructor or custom converter |

---

### F-003: Custom Type Support

**Description:** Support for user-defined classes as argument types.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-012 | As a developer, I want to use my own classes as argument types | Class constructor called with string value |
| US-013 | As a developer, I want to register custom converters | `@wArgs.converter(MyClass)` for custom parsing |
| US-014 | As a developer, I want dataclasses to expand to multiple args | Each field becomes a CLI argument |

**Example:**

```python
from dataclasses import dataclass
from wArgs import wArgs

@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080

@wArgs
def serve(config: Config, debug: bool = False):
    """Start the server with the given configuration."""
    print(f"Starting server at {config.host}:{config.port}")
```

**CLI:**
```bash
$ python serve.py --config-host 0.0.0.0 --config-port 9000 --debug
Starting server at 0.0.0.0:9000
```

---

### F-004: Docstring Parsing

**Description:** Extract help text from function and parameter docstrings.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-015 | As a developer, I want my docstring to become the command description | First line/paragraph appears in `--help` |
| US-016 | As a developer, I want parameter docs to become argument help | `Args:` section parsed for help text |
| US-017 | As a developer, I want any docstring format to work | Google, NumPy, Sphinx all auto-detected |

**Supported Formats:**

```python
# Google style
def func(name: str):
    """Short description.

    Args:
        name: The name to use
    """

# NumPy style
def func(name: str):
    """Short description.

    Parameters
    ----------
    name : str
        The name to use
    """

# Sphinx style
def func(name: str):
    """Short description.

    :param name: The name to use
    """
```

---

### F-005: Subcommands (Class-Based)

**Description:** Class methods become subcommands automatically.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-018 | As a developer, I want class methods to become subcommands | `@wArgs class Git` → `git commit`, `git push` |
| US-019 | As a developer, I want class-level arguments shared by subcommands | `__init__` params become global options |
| US-020 | As a developer, I want nested classes for deeper hierarchies | Inner classes create sub-subcommands |

**Example:**

```python
from wArgs import wArgs

@wArgs
class Git:
    """A distributed version control system."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def commit(self, message: str, amend: bool = False):
        """Record changes to the repository."""
        print(f"Committing: {message}")

    def push(self, remote: str = "origin", branch: str = "main"):
        """Update remote refs."""
        print(f"Pushing to {remote}/{branch}")
```

**CLI:**
```bash
$ python git.py --help
usage: git.py [-h] [--verbose] {commit,push} ...

A distributed version control system.

options:
  --verbose  Enable verbose output

subcommands:
  {commit,push}
    commit     Record changes to the repository
    push       Update remote refs

$ python git.py commit --message "Initial commit"
Committing: Initial commit
```

---

### F-006: MRO Traversal

**Description:** Discover arguments from parent classes via Method Resolution Order.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-021 | As a developer, I want child classes to inherit parent arguments | Parent `__init__` params appear in child CLI |
| US-022 | As a developer, I want to override inherited argument defaults | Child can redefine default values |
| US-023 | As a developer, I want mixins to contribute arguments | Mixin class params added to CLI |

**Example:**

```python
from wArgs import wArgs

class LoggingMixin:
    def __init__(self, log_level: str = "INFO"):
        self.log_level = log_level

class DatabaseMixin:
    def __init__(self, db_url: str = "sqlite:///app.db"):
        self.db_url = db_url

@wArgs
class App(LoggingMixin, DatabaseMixin):
    """Application with logging and database support."""

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def run(self):
        print(f"Running {self.name} at {self.log_level} with {self.db_url}")
```

**CLI:**
```bash
$ python app.py --help
usage: app.py [-h] --name NAME [--log-level LOG_LEVEL] [--db-url DB_URL]

Application with logging and database support.

options:
  --name NAME            Application name
  --log-level LOG_LEVEL  Logging level (default: INFO)
  --db-url DB_URL        Database URL (default: sqlite:///app.db)
```

---

### F-007: Full Argparse Parity

**Description:** Support all argparse features via decorator options or annotations.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-024 | As a developer, I want mutually exclusive argument groups | `@wArgs.exclusive` or `Annotated` metadata |
| US-025 | As a developer, I want logical argument groups | Arguments grouped in help output |
| US-026 | As a developer, I want short option names | `-v` for `--verbose` |
| US-027 | As a developer, I want positional arguments | First N args can be positional |
| US-028 | As a developer, I want custom metavar names | `--output FILE` not `--output OUTPUT` |
| US-029 | As a developer, I want argument actions (count, append) | `Annotated[int, wargs.Count()]` |

**Example with Annotated:**

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def tool(
    input_file: Annotated[Path, Arg(positional=True, metavar="FILE")],
    output: Annotated[Path, Arg("-o", metavar="FILE")] = None,
    verbose: Annotated[int, Arg("-v", action="count")] = 0,
):
    """Process a file."""
    pass
```

**CLI:**
```bash
$ python tool.py --help
usage: tool.py [-h] [-o FILE] [-v] FILE

Process a file.

positional arguments:
  FILE           Input file

options:
  -o FILE        Output file
  -v             Increase verbosity (can be repeated)
```

---

## Secondary Features (Should-Have)

### F-008: Shell Completion

**Description:** Auto-generate and install shell completion scripts.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-030 | As a developer, I want to install completions with one command | `myapp install-completion` works |
| US-031 | As a user, I want tab-completion for my CLI tool | After install, Tab completes arguments |
| US-032 | As a developer, I want completions for bash, zsh, and fish | All major shells supported |

**Implementation:**
- `@wArgs` adds hidden `install-completion` subcommand
- Detects current shell from `$SHELL`
- Writes completion script to appropriate location
- Supports `--shell` override for explicit shell selection

---

### F-009: Nested Decorator Pattern

**Description:** Alternative to class-based using decorator groups.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-033 | As a developer, I want Click-style `@group` and `@command` | `@wArgs.group()` creates command group |
| US-034 | As a developer, I want to add commands to groups dynamically | `@mygroup.command()` registers command |

**Example:**

```python
from wArgs import wArgs

@wArgs.group()
def cli():
    """My CLI application."""
    pass

@cli.command()
def init(name: str):
    """Initialize a new project."""
    print(f"Creating {name}")

@cli.command()
def build(target: str = "release"):
    """Build the project."""
    print(f"Building {target}")
```

---

## Future Features (Nice-to-Have)

### F-010: Configuration File Support

**Description:** Load argument defaults from config files.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-035 | As a user, I want to save my common options in a config file | `~/.myapprc` or `myapp.toml` loaded |
| US-036 | As a developer, I want CLI args to override config file values | Precedence: CLI > env > config > default |

**Supported Formats:** TOML, YAML, JSON

**Priority:** v2.0+

---

### F-011: Module-Based Commands

**Description:** Directory structure defines command hierarchy.

**User Stories:**

| ID | Story | Acceptance Criteria |
|----|-------|---------------------|
| US-037 | As a developer, I want a `commands/` folder to define subcommands | Each `.py` file becomes a subcommand |
| US-038 | As a developer, I want nested folders for nested commands | `commands/db/migrate.py` → `app db migrate` |

**Priority:** v2.0+

---

## Requirements Summary

### Must-Have (v1.0)

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FEAT-001 | Basic `@wArgs` decorator | Must | Core functionality |
| REQ-FEAT-002 | Full Python type hint support | Must | str, int, float, bool, Path, collections, Optional, Union, Literal, Enum |
| REQ-FEAT-003 | Custom class type support | Must | Constructor or registered converter |
| REQ-FEAT-004 | Docstring parsing (all formats) | Must | Google, NumPy, Sphinx auto-detect |
| REQ-FEAT-005 | Class-based subcommands | Must | Methods become subcommands |
| REQ-FEAT-006 | MRO traversal for inheritance | Must | Parent args inherited |
| REQ-FEAT-007 | Full argparse feature parity | Must | All argparse capabilities accessible |

### Should-Have (v1.x)

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FEAT-008 | Shell completion with auto-install | Should | bash/zsh/fish |
| REQ-FEAT-009 | Nested decorator pattern | Should | `@group` / `@command` |
| REQ-FEAT-010 | Custom argparse actions | Should | count, append, etc. |

### Could-Have (v2.0+)

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-FEAT-011 | Config file support | Could | TOML/YAML/JSON |
| REQ-FEAT-012 | Module-based commands | Could | Directory hierarchy |

## Decisions

- [x] **Positional arguments:** Opt-in via `Arg(positional=True)` - flags are the default (matches argparse convention)
- [x] **`*args` handling:** Captures remaining positional arguments with optional type annotation
- [x] **`**kwargs` handling:** Captures unknown `--key value` pairs as strings
- [x] **Bypass wArgs:** Use `Arg(skip=True)` to exclude a parameter from CLI (parameter must have default value)

## Dependencies

- Requires: Python 3.8+ for `typing.get_type_hints` reliability
- Optional: `typing_extensions` for Python 3.8-3.9 (backports typing features like `get_origin`, `get_args`)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Type introspection edge cases | Broken CLI generation | Comprehensive test suite |
| Docstring parsing ambiguity | Wrong help text | User override via `Arg()` |
| MRO complexity | Unexpected argument order | Document behavior clearly |
