# PRD: Technical Architecture

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document describes the internal architecture of wArgs, including package structure, key components, and technical decisions.

## System Requirements

### Python Version Support

| Version | Support Level | Notes |
|---------|--------------|-------|
| 3.8 | Full | Minimum supported version |
| 3.9 | Full | |
| 3.10 | Full | |
| 3.11 | Full | |
| 3.12 | Full | Latest stable |
| 3.13+ | Best effort | Test when released |

**Rationale:** Python 3.8+ provides adequate typing support (`get_type_hints`, `Literal`, `Final`) while maximizing user reach.

### Dependencies

**Core (zero runtime dependencies):**
- Python stdlib only
- `typing_extensions` as optional fallback for older Python

**Optional Extras:**
```toml
[project.optional-dependencies]
yaml = ["pyyaml>=6.0"]      # For YAML config files (future)
toml = ["tomli>=2.0"]       # For TOML config files (future, stdlib in 3.11+)
rich = ["rich>=13.0"]       # For enhanced output (future)
all = ["wargs[yaml,toml,rich]"]
dev = ["pytest", "mypy", "ruff", "coverage"]
docs = ["mkdocs", "mkdocs-material"]
```

---

## Package Structure

```
wargs/
├── __init__.py           # Public API exports
├── _version.py           # Version info
├── core/
│   ├── __init__.py
│   ├── decorator.py      # Main @wargs decorator
│   ├── config.py         # Configuration dataclasses
│   └── exceptions.py     # Custom exceptions
├── introspection/
│   ├── __init__.py
│   ├── types.py          # Type annotation parsing
│   ├── docstrings.py     # Docstring parsing (Google, NumPy, Sphinx)
│   ├── mro.py            # MRO traversal for inheritance
│   └── signatures.py     # Function signature analysis
├── builders/
│   ├── __init__.py
│   ├── parser.py         # ArgumentParser builder
│   ├── arguments.py      # Argument definition builder
│   └── subcommands.py    # Subcommand/subparser builder
├── completion/
│   ├── __init__.py
│   ├── generator.py      # Completion script generator
│   ├── bash.py           # Bash completion
│   ├── zsh.py            # Zsh completion
│   └── fish.py           # Fish completion
├── plugins/
│   ├── __init__.py
│   ├── registry.py       # Plugin registration and discovery
│   └── interface.py      # Plugin base classes/protocols
├── converters/
│   ├── __init__.py
│   ├── builtin.py        # Built-in type converters
│   └── registry.py       # Custom converter registration
└── py.typed              # PEP 561 marker
```

---

## Component Architecture

### High-Level Flow

```
┌─────────────────┐
│  @wargs         │  Decorator applied at import time
│  decorator      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Introspection  │  Extract function metadata
│  Engine         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Configuration  │  Build internal config representation
│  Builder        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parser         │  Generate ArgumentParser (lazy)
│  Builder        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execution      │  Parse args and call function
│  Handler        │
└─────────────────┘
```

### Core Components

#### 1. Introspection Engine

**Purpose:** Extract metadata from decorated functions/classes.

**Modules:**

| Module | Responsibility |
|--------|---------------|
| `types.py` | Parse type annotations into internal representation |
| `docstrings.py` | Parse docstrings for descriptions and parameter help |
| `mro.py` | Traverse class hierarchy for inherited parameters |
| `signatures.py` | Extract function signature and defaults |

**Key Classes:**

```python
@dataclass
class ParameterInfo:
    name: str
    annotation: type | None
    default: Any
    kind: ParameterKind  # POSITIONAL, KEYWORD, etc.
    description: str | None

@dataclass
class FunctionInfo:
    name: str
    description: str
    parameters: list[ParameterInfo]
    return_type: type | None
```

#### 2. Configuration Builder

**Purpose:** Transform introspected metadata into parser configuration.

**Key Classes:**

```python
@dataclass
class ArgumentConfig:
    name: str
    flags: list[str]          # ['--name', '-n']
    type: Callable | None     # Type converter
    default: Any
    required: bool
    help: str
    choices: list | None
    action: str | None
    nargs: str | int | None
    metavar: str | None
    dest: str | None
    group: str | None
    mutually_exclusive: str | None

@dataclass
class ParserConfig:
    prog: str | None
    description: str
    arguments: list[ArgumentConfig]
    subcommands: dict[str, ParserConfig]
```

#### 3. Parser Builder

**Purpose:** Generate `argparse.ArgumentParser` from configuration.

**Strategy:** Lazy generation - parser is only built when first needed.

```python
class ParserBuilder:
    def __init__(self, config: ParserConfig): ...

    def build(self) -> ArgumentParser:
        """Build and return the configured parser."""

    def _add_arguments(self, parser: ArgumentParser) -> None: ...
    def _add_subcommands(self, parser: ArgumentParser) -> None: ...
    def _add_groups(self, parser: ArgumentParser) -> None: ...
```

#### 4. Plugin System

**Purpose:** Allow extension without modifying core code.

**Plugin Types:**

| Plugin Type | Purpose | Example |
|-------------|---------|---------|
| TypeConverter | Custom type handling | `@wargs.converter(MyClass)` |
| DocstringParser | Custom docstring format | YAML-style docstrings |
| CompletionGenerator | Custom shell | PowerShell completion |
| OutputFormatter | Custom help format | Rich-colored output |

**Discovery:**

```python
# Entry points in pyproject.toml
[project.entry-points."wargs.converters"]
myconverter = "mypackage:MyConverter"

[project.entry-points."wargs.docstring_parsers"]
yaml = "mypackage:YamlDocstringParser"
```

**Registration API:**

```python
from wargs.plugins import register_converter, register_docstring_parser

@register_converter(MyClass)
def convert_myclass(value: str) -> MyClass:
    return MyClass.from_string(value)
```

---

## Performance Considerations

### Import Time Optimization

**Goal:** Decorating a function should add minimal import overhead.

**Strategies:**

1. **Lazy introspection:** Only introspect when parser is first needed
2. **Cached results:** Cache introspection results per function
3. **No heavy imports at module level:** Defer imports of completion, plugins, etc.

**Benchmark Target:** < 5ms overhead per decorated function at import.

### Parse Time Optimization

**Goal:** Argument parsing should be as fast as raw argparse.

**Strategies:**

1. **Build parser once:** Parser is built on first invocation, cached afterward
2. **Minimal wrapper:** Thin wrapper around argparse, not a replacement
3. **Native argparse:** Use argparse's optimized C code for actual parsing

**Benchmark Target:** < 10% overhead vs raw argparse for parsing.

### Caching Architecture

```python
class DecoratedFunction:
    _parser: ArgumentParser | None = None
    _config: ParserConfig | None = None

    @property
    def parser(self) -> ArgumentParser:
        if self._parser is None:
            self._config = self._introspect()
            self._parser = self._build_parser()
        return self._parser
```

---

## Type System Architecture

### Type Resolution Pipeline

```
Annotation String/Type
        │
        ▼
┌───────────────────┐
│  typing.get_type_hints()  │  Resolve forward refs
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Origin Extraction │  Get List from List[str]
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Converter Lookup  │  Find appropriate converter
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  argparse Config   │  Generate type=, nargs=, etc.
└───────────────────┘
```

### Supported Type Mapping

```python
TYPE_MAPPING = {
    str: {'type': str},
    int: {'type': int},
    float: {'type': float},
    bool: {'action': 'store_true'},  # or BooleanOptionalAction
    Path: {'type': Path},
    # Complex types handled by type resolver
}

def resolve_type(annotation) -> ArgumentConfig:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list:
        return {'nargs': '*', 'type': resolve_type(args[0])['type']}
    elif origin is Union:
        if type(None) in args:  # Optional
            return {'required': False, **resolve_type(args[0])}
    elif origin is Literal:
        return {'choices': list(args)}
    # ... etc
```

---

## Error Handling Architecture

### Exception Hierarchy

```python
class WargsError(Exception):
    """Base exception for all wArgs errors."""

class ConfigurationError(WargsError):
    """Error in decorator configuration (raised at import)."""

class IntrospectionError(WargsError):
    """Error during function introspection (raised at import)."""

class ConversionError(WargsError):
    """Error converting argument value (raised at runtime)."""

class PluginError(WargsError):
    """Error in plugin system."""
```

### Error Context

```python
@dataclass
class ErrorContext:
    function_name: str
    parameter_name: str | None
    source_file: str
    line_number: int

    def format_message(self, message: str) -> str:
        return f"""
wArgs Configuration Error in '{self.function_name}'
  File: {self.source_file}:{self.line_number}
  Parameter: {self.parameter_name or 'N/A'}

  {message}
"""
```

---

## Testing Architecture

### Test Organization

```
tests/
├── unit/
│   ├── test_introspection/
│   │   ├── test_types.py
│   │   ├── test_docstrings.py
│   │   └── test_mro.py
│   ├── test_builders/
│   │   ├── test_parser.py
│   │   └── test_arguments.py
│   └── test_converters/
├── integration/
│   ├── test_basic_usage.py
│   ├── test_subcommands.py
│   ├── test_inheritance.py
│   └── test_completion.py
├── e2e/
│   ├── test_cli_invocation.py
│   └── test_real_world_patterns.py
└── conftest.py
```

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-TECH-001 | Support Python 3.8+ | Must | Minimum version |
| REQ-TECH-002 | Zero runtime dependencies (core) | Must | stdlib only |
| REQ-TECH-003 | Optional extras for enhanced features | Should | yaml, toml, rich |
| REQ-TECH-004 | Plugin architecture via entry points | Must | Extensibility |
| REQ-TECH-005 | < 5ms import overhead per function | Should | Performance |
| REQ-TECH-006 | < 10% parse time overhead vs argparse | Should | Performance |
| REQ-TECH-007 | Lazy parser construction | Must | Performance |
| REQ-TECH-008 | Full package structure | Must | Maintainability |
| REQ-TECH-009 | Comprehensive exception hierarchy | Must | Debuggability |
| REQ-TECH-010 | PEP 561 compliant (py.typed) | Must | Type checker support |

## Decisions

- [x] **Cython compilation:** No - focus on clean Python code, optimize algorithms instead of adding build complexity
- [x] **Circular imports in type annotations:** Use `from __future__ import annotations` (PEP 563) and string annotations for forward references
- [x] **MRO traversal:** Opt-out - enabled by default for classes, disable with `@wargs(traverse_mro=False)`

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Python 3.8 typing limitations | Code complexity | Conditional imports, typing_extensions |
| Plugin API stability | Breaking changes | Versioned plugin protocol |
| Performance regression | Slow CLIs | Benchmark suite in CI |
