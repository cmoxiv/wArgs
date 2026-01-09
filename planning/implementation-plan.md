# Implementation Plan: wArgs

> **Project:** wArgs
> **Version:** 1.0
> **Created:** 2026-01-09
> **Status:** Ready for Implementation

## Overview

This document outlines the phased implementation plan for wArgs, a Python decorator library that automatically generates argparse-based CLI interfaces. Each phase includes task lists, unit tests, diagnostic tools, and documentation scope.

**Reference Documents:**
- [PRD.md](PRD.md) - Main requirements document
- [PRD-Technical.md](PRD-Technical.md) - Architecture details
- [PRD-Features.md](PRD-Features.md) - Feature specifications

---

## Phase 1: Project Foundation

**Goal:** Set up project structure, tooling, and CI/CD pipeline.

### Tasks

| ID  | Task                           | Description                                                                 | Dependencies |
|-----|--------------------------------|-----------------------------------------------------------------------------|--------------|
| 1.1 | Create repository              | Initialize Git repo with `.gitignore`, `LICENSE` (MIT)                      | None         |
| 1.2 | Set up pyproject.toml          | Configure build system (hatchling), metadata, dependencies                  | 1.1          |
| 1.3 | Create package structure       | Create `wargs/` directory with `__init__.py`, `_version.py`, `py.typed`     | 1.2          |
| 1.4 | Set up development environment | Create dev dependencies, pre-commit hooks                                   | 1.2          |
| 1.5 | Configure GitHub Actions       | CI workflow for tests, linting, type checking                               | 1.3          |
| 1.6 | Set up test infrastructure     | pytest, pytest-cov, hypothesis, tox configuration                           | 1.3          |
| 1.7 | Create exception hierarchy     | `WargsError`, `ConfigurationError`, `IntrospectionError`, `ConversionError` | 1.3          |

### Unit Tests

```
tests/
├── conftest.py                 # Shared fixtures
└── unit/
    └── test_exceptions.py      # Exception hierarchy tests
```

| Test                       | Description                                     |
|----------------------------|-------------------------------------------------|
| `test_exception_hierarchy` | Verify all exceptions inherit from `WargsError` |
| `test_exception_messages`  | Verify exception message formatting             |

### Diagnostic Tools

- `wargs --version` - Display version info (deferred to Phase 2)
- Development: `tox -e lint`, `tox -e typecheck`

### Documentation

- `README.md` - Basic project description, installation, minimal example
- `CONTRIBUTING.md` - Development setup instructions
- `LICENSE` - MIT license text

### Deliverables

```
wargs/
├── __init__.py           # Exports: __version__, exceptions
├── _version.py           # __version__ = "0.1.0"
├── py.typed              # PEP 561 marker
└── core/
    └── exceptions.py     # Exception hierarchy

tests/
├── conftest.py
└── unit/
    └── test_exceptions.py

.github/
└── workflows/
    └── ci.yml            # GitHub Actions CI

pyproject.toml
README.md
CONTRIBUTING.md
LICENSE
.gitignore
.pre-commit-config.yaml
tox.ini
```

---

## Phase 2: Core Introspection Engine

**Goal:** Build the introspection system that extracts metadata from functions.

### Tasks

| ID   | Task                                 | Description                                 | Dependencies |
|------|--------------------------------------|---------------------------------------------|--------------|
| 2.1  | Implement signature analysis         | Extract parameters from function signatures | Phase 1      |
| 2.2  | Implement basic type resolution      | Handle str, int, float, bool, Path          | 2.1          |
| 2.3  | Implement collection types           | Handle list, tuple, set, dict               | 2.2          |
| 2.4  | Implement typing module types        | Handle Optional, Union, Literal             | 2.2          |
| 2.5  | Implement Enum support               | Handle Enum subclasses as choices           | 2.2          |
| 2.6  | Implement forward reference handling | Resolve string annotations                  | 2.2          |
| 2.7  | Create internal data structures      | `ParameterInfo`, `FunctionInfo` dataclasses | 2.1          |
| 2.8  | Implement docstring detection        | Auto-detect Google, NumPy, Sphinx formats   | Phase 1      |
| 2.9  | Implement Google docstring parser    | Parse `Args:` section                       | 2.8          |
| 2.10 | Implement NumPy docstring parser     | Parse `Parameters` section                  | 2.8          |
| 2.11 | Implement Sphinx docstring parser    | Parse `:param:` directives                  | 2.8          |

### Unit Tests

```
tests/unit/introspection/
├── test_signatures.py      # Signature extraction
├── test_types.py           # Type resolution
└── test_docstrings.py      # Docstring parsing
```

| Test File            | Key Tests                                                                                                                                                                                                                     |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `test_signatures.py` | `test_extract_required_param`, `test_extract_optional_param`, `test_extract_default_value`, `test_handle_args_kwargs`                                                                                                         |
| `test_types.py`      | `test_resolve_str`, `test_resolve_int`, `test_resolve_bool`, `test_resolve_path`, `test_resolve_list`, `test_resolve_optional`, `test_resolve_union`, `test_resolve_literal`, `test_resolve_enum`, `test_resolve_nested_type` |
| `test_docstrings.py` | `test_detect_google_format`, `test_detect_numpy_format`, `test_detect_sphinx_format`, `test_parse_google_args`, `test_parse_numpy_params`, `test_parse_sphinx_params`, `test_multiline_description`                           |

### Property-Based Tests

```python
# tests/property/test_type_roundtrip.py
@given(st.integers())
def test_int_roundtrip(value):
    """Integer values survive type conversion."""

@given(st.text(min_size=1))
def test_str_roundtrip(value):
    """String values survive type conversion."""
```

### Diagnostic Tools

```python
# wargs/introspection/debug.py
def explain_function(func) -> str:
    """Return human-readable introspection results."""
```

### Documentation

- Docstrings on all public classes and functions
- Type hints on all functions

### Deliverables

```
wargs/
├── introspection/
│   ├── __init__.py
│   ├── signatures.py     # Function signature analysis
│   ├── types.py          # Type annotation resolution
│   ├── docstrings.py     # Docstring parsing
│   └── debug.py          # Diagnostic utilities
└── core/
    └── config.py         # ParameterInfo, FunctionInfo dataclasses

tests/unit/introspection/
├── test_signatures.py
├── test_types.py
└── test_docstrings.py

tests/property/
└── test_type_roundtrip.py
```

---

## Phase 3: Parser Builder

**Goal:** Build the system that generates ArgumentParser from introspected data.

### Tasks

| ID   | Task                                | Description                             | Dependencies |
|------|-------------------------------------|-----------------------------------------|--------------|
| 3.1  | Create ArgumentConfig dataclass     | Define argument configuration structure | Phase 2      |
| 3.2  | Create ParserConfig dataclass       | Define parser configuration structure   | 3.1          |
| 3.3  | Implement argument builder          | Convert ParameterInfo to ArgumentConfig | 3.1          |
| 3.4  | Implement parser builder            | Build ArgumentParser from ParserConfig  | 3.2, 3.3     |
| 3.5  | Implement flag generation           | Generate `--name` from parameter name   | 3.3          |
| 3.6  | Implement short flag support        | Support `-n` via `Arg("-n")`            | 3.5          |
| 3.7  | Implement positional arguments      | Support `Arg(positional=True)`          | 3.3          |
| 3.8  | Implement argument groups           | Support `Arg(group="...")`              | 3.4          |
| 3.9  | Implement mutually exclusive groups | Support `Arg(exclusive="...")`          | 3.4          |
| 3.10 | Implement hidden arguments          | Support `Arg(hidden=True)`              | 3.3          |
| 3.11 | Implement skip arguments            | Support `Arg(skip=True)`                | 3.3          |
| 3.12 | Implement lazy parser construction  | Build parser on first invocation        | 3.4          |
| 3.13 | Implement parser caching            | Cache built parser                      | 3.12         |

### Unit Tests

```
tests/unit/builders/
├── test_arguments.py      # Argument configuration
└── test_parser.py         # Parser construction
```

| Test File           | Key Tests                                                                                                                                                                                             |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `test_arguments.py` | `test_required_arg`, `test_optional_arg`, `test_flag_generation`, `test_short_flag`, `test_positional_arg`, `test_hidden_arg`, `test_skip_arg`, `test_choices_from_literal`, `test_choices_from_enum` |
| `test_parser.py`    | `test_build_simple_parser`, `test_build_with_groups`, `test_build_with_exclusive`, `test_lazy_construction`, `test_parser_caching`                                                                    |

### Diagnostic Tools

```python
# wargs/builders/debug.py
def dump_parser_config(config: ParserConfig) -> str:
    """Return human-readable parser configuration."""
```

### Deliverables

```
wargs/
├── builders/
│   ├── __init__.py
│   ├── arguments.py      # ParameterInfo -> ArgumentConfig
│   ├── parser.py         # ParserConfig -> ArgumentParser
│   └── debug.py          # Diagnostic utilities
└── core/
    └── config.py         # Add ArgumentConfig, ParserConfig

tests/unit/builders/
├── test_arguments.py
└── test_parser.py
```

---

## Phase 4: Core Decorator

**Goal:** Implement the `@wargs` decorator for functions.

### Tasks

| ID   | Task                              | Description                                          | Dependencies |
|------|-----------------------------------|------------------------------------------------------|--------------|
| 4.1  | Implement basic decorator         | `@wargs` transforms function                         | Phase 3      |
| 4.2  | Support decorator with parens     | `@wargs()` works same as `@wargs`                    | 4.1          |
| 4.3  | Support decorator options         | `@wargs(prog="...", description="...")`              | 4.2          |
| 4.4  | Implement sys.argv parsing        | `func()` parses sys.argv                             | 4.1          |
| 4.5  | Implement list argument parsing   | `func(["--name", "value"])`                          | 4.1          |
| 4.6  | Implement direct call passthrough | `func(name="value")` bypasses parsing                | 4.1          |
| 4.7  | Implement Arg metadata support    | Parse `Annotated[type, Arg(...)]`                    | 4.1          |
| 4.8  | Implement *args handling          | Capture remaining positional args                    | 4.1          |
| 4.9  | Implement **kwargs handling       | Capture unknown --key value pairs                    | 4.1          |
| 4.10 | Create Arg dataclass              | Define Arg configuration                             | Phase 1      |
| 4.11 | Add fail-fast validation          | Raise ConfigurationError at import for invalid usage | 4.1          |

### Unit Tests

```
tests/unit/
└── test_decorator.py

tests/integration/
├── test_basic_cli.py
├── test_invocation.py
└── test_arg_metadata.py
```

| Test File              | Key Tests                                                                                                                                              |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `test_decorator.py`    | `test_decorator_no_parens`, `test_decorator_with_parens`, `test_decorator_with_options`, `test_fail_fast_no_annotation`, `test_fail_fast_invalid_type` |
| `test_basic_cli.py`    | `test_simple_function`, `test_optional_args`, `test_boolean_flags`, `test_list_args`, `test_enum_choices`                                              |
| `test_invocation.py`   | `test_sysargv_parsing`, `test_list_parsing`, `test_direct_call_passthrough`                                                                            |
| `test_arg_metadata.py` | `test_short_flag`, `test_positional`, `test_metavar`, `test_choices`, `test_hidden`, `test_skip`                                                       |

### End-to-End Tests

```
tests/e2e/
├── fixtures/
│   ├── simple_cli.py
│   ├── typed_cli.py
│   └── annotated_cli.py
└── test_subprocess.py
```

### Documentation

- Update README with usage examples
- Docstrings on `@wargs` and `Arg`

### Deliverables

```
wargs/
├── __init__.py           # Export: wargs, Arg
├── core/
│   ├── decorator.py      # @wargs implementation
│   └── arg.py            # Arg dataclass

tests/unit/
└── test_decorator.py

tests/integration/
├── test_basic_cli.py
├── test_invocation.py
└── test_arg_metadata.py

tests/e2e/
├── fixtures/
│   ├── simple_cli.py
│   ├── typed_cli.py
│   └── annotated_cli.py
└── test_subprocess.py
```

---

## Phase 5: Class-Based Subcommands

**Goal:** Implement `@wargs` on classes for subcommand support.

### Tasks

| ID  | Task                               | Description                                | Dependencies |
|-----|------------------------------------|--------------------------------------------|--------------|
| 5.1 | Detect class decoration            | `@wargs` on class triggers subcommand mode | Phase 4      |
| 5.2 | Extract __init__ as global options | Class init params become shared args       | 5.1          |
| 5.3 | Extract methods as subcommands     | Public methods become subcommands          | 5.1          |
| 5.4 | Exclude private methods            | Methods starting with `_` excluded         | 5.3          |
| 5.5 | Build subparser structure          | Create argparse subparsers                 | 5.3          |
| 5.6 | Wire up method invocation          | Route to correct method after parsing      | 5.5          |
| 5.7 | Support nested classes             | Inner classes become sub-subcommands       | 5.3          |

### Unit Tests

```
tests/unit/builders/
└── test_subcommands.py

tests/integration/
└── test_subcommands.py
```

| Test File                           | Key Tests                                                                                                                |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `test_subcommands.py` (unit)        | `test_detect_class`, `test_extract_init_params`, `test_extract_methods`, `test_exclude_private`, `test_build_subparsers` |
| `test_subcommands.py` (integration) | `test_class_cli`, `test_global_options`, `test_subcommand_routing`, `test_subcommand_help`, `test_nested_classes`        |

### End-to-End Tests

```
tests/e2e/fixtures/
└── subcommand_cli.py
```

### Deliverables

```
wargs/
└── builders/
    └── subcommands.py    # Subcommand/subparser builder

tests/unit/builders/
└── test_subcommands.py

tests/integration/
└── test_subcommands.py

tests/e2e/fixtures/
└── subcommand_cli.py
```

---

## Phase 6: MRO Traversal

**Goal:** Implement parameter inheritance via Method Resolution Order.

### Tasks

| ID  | Task                    | Description                                   | Dependencies |
|-----|-------------------------|-----------------------------------------------|--------------|
| 6.1 | Implement MRO traversal | Walk class.__mro__ for parameters             | Phase 5      |
| 6.2 | Merge parameters        | Combine parent and child parameters           | 6.1          |
| 6.3 | Handle conflicts        | Child overrides parent, warn on type mismatch | 6.2          |
| 6.4 | Support mixins          | Multiple inheritance contributes args         | 6.1          |
| 6.5 | Add traverse_mro option | `@wargs(traverse_mro=False)` to disable       | 6.1          |
	
### Unit Tests

```
tests/unit/introspection/
└── test_mro.py

tests/integration/
└── test_inheritance.py
```

| Test File             | Key Tests                                                                                                                |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| `test_mro.py`         | `test_traverse_mro`, `test_merge_params`, `test_child_overrides`, `test_type_conflict_warning`, `test_disable_traversal` |
| `test_inheritance.py` | `test_single_inheritance`, `test_mixin_params`, `test_diamond_inheritance`, `test_override_defaults`                     |

### Deliverables

```
wargs/
└── introspection/
    └── mro.py            # MRO traversal implementation

tests/unit/introspection/
└── test_mro.py

tests/integration/
└── test_inheritance.py
```

---

## Phase 7: Converter Registry & Plugin Architecture

**Goal:** Implement custom type converters and plugin system.

### Tasks

| ID  | Task                              | Description                                         | Dependencies |
|-----|-----------------------------------|-----------------------------------------------------|--------------|
| 7.1 | Create ConverterRegistry          | Central registry for type converters                | Phase 4      |
| 7.2 | Implement @converter decorator    | `@wargs.converter(MyClass)` registration            | 7.1          |
| 7.3 | Register built-in converters      | datetime, date, time, UUID, Decimal, Path           | 7.1          |
| 7.4 | Implement converter lookup        | Check registry, then inheritance chain              | 7.1          |
| 7.5 | Implement entry point discovery   | Load converters from `wargs.converters` entry point | 7.1          |
| 7.6 | Support custom class constructors | Use class constructor if no converter               | 7.1          |
| 7.7 | Implement dataclass expansion     | Dataclass fields become prefixed args               | 7.1          |

### Unit Tests

```
tests/unit/converters/
├── test_registry.py
└── test_builtin.py

tests/integration/
└── test_custom_types.py
```

| Test File              | Key Tests                                                                                            |
|------------------------|------------------------------------------------------------------------------------------------------|
| `test_registry.py`     | `test_register_converter`, `test_last_wins`, `test_inheritance_lookup`, `test_entry_point_discovery` |
| `test_builtin.py`      | `test_datetime_converter`, `test_date_converter`, `test_uuid_converter`, `test_decimal_converter`    |
| `test_custom_types.py` | `test_custom_class`, `test_dataclass_expansion`, `test_registered_converter`                         |
|                        |                                                                                                      |

### Deliverables

```
wargs/
├── __init__.py           # Export: converter
├── converters/
│   ├── __init__.py
│   ├── registry.py       # ConverterRegistry
│   └── builtin.py        # Built-in converters
└── plugins/
    ├── __init__.py
    ├── registry.py       # Plugin discovery
    └── interface.py      # Plugin protocols

tests/unit/converters/
├── test_registry.py
└── test_builtin.py

tests/integration/
└── test_custom_types.py
```

---

## Phase 8: Utilities & Debugging

**Goal:** Implement utility functions for testing and debugging.

### Tasks

| ID  | Task                              | Description                          | Dependencies |
|-----|-----------------------------------|--------------------------------------|--------------|
| 8.1 | Implement explain()               | Print detected configuration         | Phase 6      |
| 8.2 | Implement get_parser()            | Return ArgumentParser instance       | Phase 4      |
| 8.3 | Implement get_config()            | Return ParserConfig instance         | Phase 4      |
| 8.4 | Add WARGS_DEBUG env var           | Enable verbose debug output          | 8.1          |
| 8.5 | Implement _wargs_config attribute | Attach config to decorated functions | Phase 4      |

### Unit Tests

```
tests/unit/
└── test_utilities.py
```

| Test                             | Description                                 |
|----------------------------------|---------------------------------------------|
| `test_explain_output`            | Verify explain() produces readable output   |
| `test_get_parser_returns_parser` | Verify get_parser() returns ArgumentParser  |
| `test_get_config_returns_config` | Verify get_config() returns ParserConfig    |
| `test_debug_env_var`             | Verify WARGS_DEBUG enables debug output     |
| `test_wargs_config_attribute`    | Verify decorated function has _wargs_config |

### Deliverables

```
wargs/
├── __init__.py           # Export: explain, get_parser, get_config
└── utilities.py          # Utility functions

tests/unit/
└── test_utilities.py
```

---

## Phase 9: Documentation & Examples

**Goal:** Create comprehensive documentation and examples.

### Tasks

| ID  | Task                        | Description                     | Dependencies |
|-----|-----------------------------|---------------------------------|--------------|
| 9.1 | Set up MkDocs               | Configure documentation site    | Phase 8      |
| 9.2 | Write Getting Started guide | Installation, first CLI         | 9.1          |
| 9.3 | Write User Guide            | Basic usage, types, subcommands | 9.2          |
| 9.4 | Write API Reference         | Auto-generated from docstrings  | 9.1          |
| 9.5 | Write Cookbook              | Common patterns, 10+ recipes    | 9.3          |
| 9.6 | Write Migration Guide       | From argparse, from Click       | 9.3          |
| 9.7 | Create example projects     | 5+ complete example CLIs        | 9.3          |
| 9.8 | Add doctest examples        | Runnable examples in docs       | 9.3          |

### Documentation Structure

```
docs/
├── index.md                    # Landing page
├── getting-started/
│   ├── installation.md
│   ├── quickstart.md
│   └── tutorial.md
├── guide/
│   ├── basic-usage.md
│   ├── type-system.md
│   ├── docstrings.md
│   ├── subcommands.md
│   ├── inheritance.md
│   └── advanced.md
├── cookbook/
│   ├── patterns.md
│   ├── migration-argparse.md
│   ├── migration-click.md
│   └── testing.md
├── api/
│   ├── decorators.md
│   ├── types.md
│   └── utilities.md
└── changelog.md

examples/
├── simple/
│   └── greet.py
├── typed/
│   └── process.py
├── subcommands/
│   └── git_clone.py
├── inheritance/
│   └── mixins.py
└── advanced/
    └── custom_types.py
```

### Deliverables

- Complete MkDocs documentation site
- 10+ cookbook recipes
- 5+ example projects
- Migration guides

---

## Phase 10: Quality Assurance & Release

**Goal:** Final testing, performance validation, and PyPI release.

### Tasks

| ID    | Task                     | Description                          | Dependencies |
|-------|--------------------------|--------------------------------------|--------------|
| 10.1  | Achieve 100% coverage    | Fill any coverage gaps               | All phases   |
| 10.2  | Run full tox matrix      | Test Python 3.8-3.12                 | 10.1         |
| 10.3  | Performance benchmarking | Measure import/parse time            | 10.1         |
| 10.4  | Security review          | Review for injection vulnerabilities | 10.1         |
| 10.5  | Documentation review     | Verify all docs are current          | Phase 9      |
| 10.6  | Create CHANGELOG.md      | Document all features                | 10.5         |
| 10.7  | Test on Test PyPI        | Upload and verify installation       | 10.2         |
| 10.8  | Release to PyPI          | `python -m twine upload dist/*`      | 10.7         |
| 10.9  | Create GitHub Release    | Tag v1.0.0, release notes            | 10.8         |
| 10.10 | Announce release         | README badges, social media          | 10.9         |

### Quality Gates

| Gate          | Requirement                                 |
|---------------|---------------------------------------------|
| Coverage      | 100% (with justified exclusions)            |
| Type checking | mypy strict mode passes                     |
| Linting       | ruff check passes                           |
| Tests         | All Python versions pass                    |
| Performance   | < 5ms import overhead, < 10% parse overhead |
| Documentation | All public APIs documented                  |

### Performance Benchmarks

```python
# benchmarks/bench_import.py
def bench_import_overhead():
    """Measure decorator overhead at import time."""

# benchmarks/bench_parse.py
def bench_parse_vs_argparse():
    """Compare parse time to raw argparse."""
```

### Deliverables

- 100% test coverage
- Performance benchmark results
- CHANGELOG.md
- v1.0.0 on PyPI
- GitHub Release

---

## Phase 11: Shell Completion (v1.1)

**Goal:** Implement shell completion script generation.

### Tasks

| ID   | Task                              | Description                     | Dependencies |
|------|-----------------------------------|---------------------------------|--------------|
| 11.1 | Implement completion generator    | Core completion logic           | v1.0         |
| 11.2 | Implement Bash completion         | Generate bash completion script | 11.1         |
| 11.3 | Implement Zsh completion          | Generate zsh completion script  | 11.1         |
| 11.4 | Implement Fish completion         | Generate fish completion script | 11.1         |
| 11.5 | Implement shell detection         | Auto-detect current shell       | 11.1         |
| 11.6 | Implement install_completion()    | Utility for simple functions    | 11.1         |
| 11.7 | Add install-completion subcommand | Auto-add for classes/groups     | 11.1         |

### Deliverables

```
wargs/
└── completion/
    ├── __init__.py
    ├── generator.py      # Core completion logic
    ├── bash.py           # Bash completion
    ├── zsh.py            # Zsh completion
    └── fish.py           # Fish completion
```

---

## Phase 12: Decorator Groups (v1.2)

**Goal:** Implement `@wargs.group()` decorator pattern.
	
### Tasks

| ID   | Task                       | Description                         | Dependencies |
|------|----------------------------|-------------------------------------|--------------|
| 12.1 | Implement @wargs.group()   | Create command group decorator      | v1.0         |
| 12.2 | Implement @group.command() | Register command with group         | 12.1         |
| 12.3 | Support shared options     | Group function params become shared | 12.1         |
| 12.4 | Support nested groups      | Groups can contain groups           | 12.1         |

### Deliverables

```
wargs/
└── core/
    └── groups.py         # Group decorator implementation
```

---

## Summary: Task Count by Phase

| Phase          | Name               | Task Count | Estimated Complexity |
|----------------|--------------------|------------|----------------------|
| 1              | Project Foundation | 7          | Low                  |
| 2              | Core Introspection | 11         | High                 |
| 3              | Parser Builder     | 13         | High                 |
| 4              | Core Decorator     | 11         | High                 |
| 5              | Class Subcommands  | 7          | Medium               |
| 6              | MRO Traversal      | 5          | Medium               |
| 7              | Converter Registry | 7          | Medium               |
| 8              | Utilities          | 5          | Low                  |
| 9              | Documentation      | 8          | Medium               |
| 10             | QA & Release       | 10         | Medium               |
| **Total v1.0** |                    | **84**     |                      |
| 11             | Shell Completion   | 7          | Medium               |
| 12             | Decorator Groups   | 4          | Medium               |
| **Total v1.2** |                    | **95**     |                      |

---

## Dependency Graph

```
Phase 1: Foundation
    │
    ▼
Phase 2: Introspection ──────────────────┐
    │                                    │
    ▼                                    │
Phase 3: Parser Builder                  │
    │                                    │
    ▼                                    │
Phase 4: Core Decorator ◄────────────────┘
    │
    ├──────────────────┬─────────────────┐
    ▼                  ▼                 ▼
Phase 5: Subcommands   Phase 7: Converters
    │                      │
    ▼                      │
Phase 6: MRO ◄─────────────┘
    │
    ▼
Phase 8: Utilities
    │
    ▼
Phase 9: Documentation
    │
    ▼
Phase 10: QA & Release (v1.0)
    │
    ├─────────────────────┐
    ▼                     ▼
Phase 11: Completion   Phase 12: Groups
         (v1.1)              (v1.2)
```

---

## Test Coverage Requirements

| Module                 | Coverage Target |
|------------------------|-----------------|
| `wargs/core/`          | 100%            |
| `wargs/introspection/` | 100%            |
| `wargs/builders/`      | 100%            |
| `wargs/converters/`    | 100%            |
| `wargs/plugins/`       | 100%            |
| `wargs/completion/`    | 100%            |
| **Total**              | **100%**        |

### Coverage Exclusions

```python
# Allowed exclusions (must use pragma: no cover)
if TYPE_CHECKING:          # Type checking only
if __name__ == "__main__": # Script entry points
raise NotImplementedError  # Defensive code
```

---

## Next Steps

1. **Review this plan** - Confirm task breakdown is appropriate
2. **Set up repository** - Execute Phase 1 tasks
3. **Begin TDD cycle** - Start with Phase 2 tests first
4. **Track progress** - Update task status as work progresses

---

*Generated from wArgs PRD documents*
