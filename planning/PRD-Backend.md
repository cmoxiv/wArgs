# PRD: Backend Requirements

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document details the internal processing logic, algorithms, and data handling requirements for wArgs. Since wArgs is a library (not a server application), "backend" refers to the core processing engine.

## Core Processing Requirements

### BE-001: Type Resolution Engine

**Purpose:** Convert Python type annotations to argparse configurations.

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-001 | Handle all stdlib types (str, int, float, bool, Path) | Must | Basic type support |
| REQ-BE-002 | Handle collections (list, tuple, set, dict) | Must | Collection support |
| REQ-BE-003 | Handle typing module types (Optional, Union, Literal) | Must | Advanced types |
| REQ-BE-004 | Handle Enum subclasses | Must | Constrained values |
| REQ-BE-005 | Handle custom classes via constructors | Must | User types |
| REQ-BE-006 | Handle nested types with repeated args | Must | Complex structures |
| REQ-BE-007 | Handle forward references | Should | String annotations |

**Complex Type Handling:**

```python
# dict[str, list[int]] handling
@wargs
def process(data: dict[str, list[int]]):
    """Process data dictionary."""
    pass

# CLI: --data-key1 1 2 3 --data-key2 4 5
# Result: {'key1': [1, 2, 3], 'key2': [4, 5]}
```

**Implementation Notes:**
- Use `get_origin()` and `get_args()` from `typing`
- Recursively resolve nested types
- For `dict` types, create dynamic key-based arguments

---

### BE-002: *args and **kwargs Handling

**Purpose:** Support variadic arguments in decorated functions.

**`*args` Handling:**

| Behavior | Description |
|----------|-------------|
| Becomes positional | All remaining positional arguments captured |
| Type from annotation | `*args: int` means all captured values are ints |
| No annotation | Treated as strings |

```python
@wargs
def combine(*files: Path):
    """Combine multiple files."""
    for f in files:
        print(f.read_text())

# CLI: combine file1.txt file2.txt file3.txt
```

**`**kwargs` Handling:**

| Behavior | Description |
|----------|-------------|
| Unknown args captured | `--unknown-key value` → `kwargs['unknown_key'] = value` |
| Prefix stripping | `--childclass-key` → `kwargs['childclass_key']` or nested |
| No validation | Values passed as strings unless type hints available |

```python
@wargs
def configure(name: str, **options):
    """Configure with arbitrary options."""
    print(f"Name: {name}")
    print(f"Options: {options}")

# CLI: configure --name myapp --timeout 30 --retry true
# Result: name='myapp', options={'timeout': '30', 'retry': 'true'}
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-008 | *args captures remaining positional arguments | Must | Variadic support |
| REQ-BE-009 | *args type annotation applied to all values | Should | Type safety |
| REQ-BE-010 | **kwargs captures unknown --key value pairs | Must | Flexibility |
| REQ-BE-011 | **kwargs values passed as strings by default | Must | Predictability |

---

### BE-003: Docstring Parsing Engine

**Purpose:** Extract descriptions from function docstrings.

**Supported Formats:**

| Format | Detection Pattern |
|--------|-------------------|
| Google | `Args:`, `Returns:`, `Raises:` |
| NumPy | `Parameters`, `Returns`, `Raises` headers with dashes |
| Sphinx | `:param name:`, `:returns:`, `:raises:` |
| Plain | First paragraph as description, no param extraction |

**Algorithm:**

```
1. Detect format by scanning for format markers
2. Extract first paragraph as function description
3. Parse parameter section for argument help text
4. Handle multi-line descriptions
5. Strip leading/trailing whitespace
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-012 | Auto-detect docstring format | Must | User convenience |
| REQ-BE-013 | Parse Google-style docstrings | Must | Common format |
| REQ-BE-014 | Parse NumPy-style docstrings | Must | Scientific Python |
| REQ-BE-015 | Parse Sphinx-style docstrings | Must | Documentation tools |
| REQ-BE-016 | Handle multi-line parameter descriptions | Should | Thorough docs |
| REQ-BE-017 | Graceful fallback for unparseable docstrings | Must | Robustness |

---

### BE-004: MRO Traversal Engine

**Purpose:** Discover parameters from parent classes.

**Algorithm:**

```
1. Get class MRO via cls.__mro__
2. For each class in MRO (excluding object):
   a. Inspect __init__ signature
   b. Extract parameters with annotations and defaults
   c. Merge with child parameters (child overrides parent)
3. Return combined parameter list
```

**Conflict Resolution:**

| Conflict | Resolution |
|----------|------------|
| Same parameter name | Child definition wins |
| Different defaults | Child default wins |
| Different types | Child type wins (with warning) |

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-018 | Traverse MRO for inherited parameters | Must | Core feature |
| REQ-BE-019 | Child parameters override parent | Must | Expected behavior |
| REQ-BE-020 | Warn on type annotation conflicts | Should | Debugging help |
| REQ-BE-021 | Support multiple inheritance (mixins) | Must | Common pattern |

---

### BE-005: Converter Registry

**Purpose:** Manage type converters for custom types.

**Registry Architecture:**

```python
class ConverterRegistry:
    _converters: dict[type, Callable[[str], Any]] = {}

    def register(self, type_: type, converter: Callable) -> None:
        """Register converter (last wins on conflict)."""
        self._converters[type_] = converter

    def get(self, type_: type) -> Callable | None:
        """Get converter for type, checking inheritance."""
        if type_ in self._converters:
            return self._converters[type_]
        for base in type_.__mro__:
            if base in self._converters:
                return self._converters[base]
        return None
```

**Built-in Converters:**

| Type | Converter |
|------|-----------|
| `Path` | `pathlib.Path` |
| `datetime` | `datetime.fromisoformat` |
| `date` | `date.fromisoformat` |
| `time` | `time.fromisoformat` |
| `UUID` | `uuid.UUID` |
| `Decimal` | `decimal.Decimal` |

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-022 | Global converter registry | Must | Extensibility |
| REQ-BE-023 | @wargs.converter decorator for registration | Must | User API |
| REQ-BE-024 | Last-registered converter wins on conflict | Must | Deterministic |
| REQ-BE-025 | Check type inheritance for converter lookup | Should | Convenience |
| REQ-BE-026 | Built-in converters for common stdlib types | Should | Convenience |

---

### BE-006: ArgumentParser Builder

**Purpose:** Construct argparse.ArgumentParser from configuration.

**Builder Pattern:**

```python
class ParserBuilder:
    def __init__(self, config: ParserConfig):
        self.config = config
        self._parser: ArgumentParser | None = None

    def build(self) -> ArgumentParser:
        if self._parser is not None:
            return self._parser

        # Use standard HelpFormatter by default (consistent with REQ-UX-005)
        # Developer can override via @wargs(formatter_class=...)
        self._parser = ArgumentParser(
            prog=self.config.prog,
            description=self.config.description,
        )

        self._add_arguments()
        self._add_groups()
        self._add_subcommands()

        return self._parser
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-027 | Build ArgumentParser from ParserConfig | Must | Core functionality |
| REQ-BE-028 | Support all argparse argument options | Must | Full parity |
| REQ-BE-029 | Lazy construction (build on first use) | Must | Performance |
| REQ-BE-030 | Cache built parser | Must | Performance |

---

### BE-007: Subcommand Builder

**Purpose:** Handle class-based and decorator-based subcommands.

**Class-Based Flow:**

```
1. Detect @wargs on class
2. Find __init__ for global arguments
3. Find public methods (not starting with _)
4. Create subparser for each method
5. Wire up method invocation
```

**Decorator-Based Flow:**

```
1. Create group with @wargs.group()
2. Register commands with @group.command()
3. Build parent parser with subparsers
4. Wire up function invocation
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-031 | Class methods become subcommands | Must | Core feature |
| REQ-BE-032 | __init__ params become global options | Must | Shared arguments |
| REQ-BE-033 | Private methods (_foo) excluded | Must | Convention |
| REQ-BE-034 | @wargs.group() creates command group | Should | Alternative API |
| REQ-BE-035 | Nested classes for deep hierarchies | Should | Complex CLIs |

---

### BE-008: Completion Script Generator

**Purpose:** Generate shell completion scripts.

**Shell Support:**

| Shell | Script Location | Approach |
|-------|-----------------|----------|
| Bash | `~/.bash_completion.d/` or `~/.bashrc` | Complete function |
| Zsh | `~/.zfunc/` or fpath | `_command` function |
| Fish | `~/.config/fish/completions/` | `complete` commands |

**Generation Algorithm:**

```
1. Introspect all arguments and subcommands
2. Generate completion function/script for target shell
3. Include:
   - Option names (--foo, -f)
   - Option values (for choices/enums)
   - Subcommand names
   - File/path completion for Path types
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-036 | Generate Bash completion scripts | Should | Popular shell |
| REQ-BE-037 | Generate Zsh completion scripts | Should | Popular shell |
| REQ-BE-038 | Generate Fish completion scripts | Should | Modern shell |
| REQ-BE-039 | Auto-detect current shell | Should | User convenience |
| REQ-BE-040 | Complete option names | Should | Basic completion |
| REQ-BE-041 | Complete choice/enum values | Should | Value completion |
| REQ-BE-042 | Complete subcommand names | Should | Subcommand completion |

---

## Data Handling

### Internal Data Structures

```python
@dataclass(frozen=True)
class ParameterInfo:
    """Immutable representation of a function parameter."""
    name: str
    annotation: type | None
    default: Any = MISSING
    kind: ParameterKind = ParameterKind.KEYWORD_ONLY
    description: str = ""

@dataclass
class ArgumentConfig:
    """Configuration for a single argument."""
    name: str
    flags: tuple[str, ...] = ()
    type_converter: Callable[[str], Any] | None = None
    default: Any = MISSING
    required: bool = True
    help: str = ""
    choices: tuple | None = None
    action: str | None = None
    nargs: str | int | None = None
    metavar: str | None = None
    dest: str | None = None
    group: str | None = None
    exclusive_group: str | None = None

@dataclass
class SubcommandConfig:
    """Configuration for a subcommand."""
    name: str
    description: str
    handler: Callable
    arguments: list[ArgumentConfig]
    subcommands: dict[str, 'SubcommandConfig']

@dataclass
class ParserConfig:
    """Complete parser configuration."""
    prog: str | None = None
    description: str = ""
    arguments: list[ArgumentConfig] = field(default_factory=list)
    subcommands: dict[str, SubcommandConfig] = field(default_factory=dict)
    global_arguments: list[ArgumentConfig] = field(default_factory=list)
```

---

## Async Support (Future)

**Status:** Planned for future release, not v1.0.

**Design Notes:**

```python
# Future API
@wargs
async def fetch(url: str, timeout: int = 30):
    """Fetch data from URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.text()

# Internally: asyncio.run(fetch()) when invoked
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-043 | Detect async functions automatically | Future | Auto asyncio.run() |
| REQ-BE-044 | Support @wargs.async for explicit async | Future | Alternative API |

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-BE-001 | Handle all stdlib types | Must | Type resolution |
| REQ-BE-002 | Handle collections | Must | Type resolution |
| REQ-BE-003 | Handle typing module types | Must | Type resolution |
| REQ-BE-004 | Handle Enum subclasses | Must | Type resolution |
| REQ-BE-005 | Handle custom classes | Must | Type resolution |
| REQ-BE-006 | Handle nested types with repeated args | Must | Complex types |
| REQ-BE-007 | Handle forward references | Should | String annotations |
| REQ-BE-008 | *args captures remaining positional | Must | Variadic support |
| REQ-BE-009 | *args type annotation applied | Should | Type safety |
| REQ-BE-010 | **kwargs captures unknown args | Must | Flexibility |
| REQ-BE-011 | **kwargs values as strings | Must | Predictability |
| REQ-BE-012 | Auto-detect docstring format | Must | User convenience |
| REQ-BE-013 | Parse Google-style docstrings | Must | Common format |
| REQ-BE-014 | Parse NumPy-style docstrings | Must | Scientific Python |
| REQ-BE-015 | Parse Sphinx-style docstrings | Must | Documentation tools |
| REQ-BE-016 | Handle multi-line descriptions | Should | Thorough docs |
| REQ-BE-017 | Graceful docstring fallback | Must | Robustness |
| REQ-BE-018 | Traverse MRO for inherited params | Must | Core feature |
| REQ-BE-019 | Child overrides parent params | Must | Expected behavior |
| REQ-BE-020 | Warn on type conflicts | Should | Debugging |
| REQ-BE-021 | Support multiple inheritance | Must | Mixins |
| REQ-BE-022 | Global converter registry | Must | Extensibility |
| REQ-BE-023 | @wargs.converter decorator | Must | User API |
| REQ-BE-024 | Last-registered converter wins | Must | Deterministic |
| REQ-BE-025 | Check inheritance for converters | Should | Convenience |
| REQ-BE-026 | Built-in stdlib converters | Should | Convenience |
| REQ-BE-027 | Build ArgumentParser from config | Must | Core functionality |
| REQ-BE-028 | Support all argparse options | Must | Full parity |
| REQ-BE-029 | Lazy parser construction | Must | Performance |
| REQ-BE-030 | Cache built parser | Must | Performance |
| REQ-BE-031 | Class methods as subcommands | Must | Core feature |
| REQ-BE-032 | __init__ params as global options | Must | Shared arguments |
| REQ-BE-033 | Private methods excluded | Must | Convention |
| REQ-BE-034 | @wargs.group() for command groups | Should | Alternative API |
| REQ-BE-035 | Nested classes for hierarchies | Should | Complex CLIs |
| REQ-BE-036 | Bash completion generation | Should | Popular shell |
| REQ-BE-037 | Zsh completion generation | Should | Popular shell |
| REQ-BE-038 | Fish completion generation | Should | Modern shell |
| REQ-BE-039 | Auto-detect current shell | Should | Convenience |
| REQ-BE-040 | Complete option names | Should | Basic completion |
| REQ-BE-041 | Complete choice/enum values | Should | Value completion |
| REQ-BE-042 | Complete subcommand names | Should | Subcommand completion |
| REQ-BE-043 | Async function support | Future | Auto asyncio.run() |
| REQ-BE-044 | @wargs.async decorator | Future | Explicit async |

## Decisions

- [x] **`**kwargs` with type hints:** `**kwargs: int` means all captured values are converted to int (same pattern as `*args: int`)
- [x] **Repeated arg keys case sensitivity:** Case-insensitive for matching, normalized to lowercase with underscores (`--My-Option` → `my_option`)
- [x] **Nested dict/list depth:** Maximum 2 levels deep (e.g., `dict[str, list[int]]`), deeper nesting requires JSON string input

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Edge cases in type resolution | Broken CLIs | Comprehensive test suite |
| **kwargs parsing ambiguity | Unexpected behavior | Clear documentation |
| MRO conflicts in diamond inheritance | Wrong arguments | Document behavior, warn |
