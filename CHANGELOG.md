# Changelog

All notable changes to wArgs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Core Framework**
  - `@wArgs` decorator for automatic CLI generation from functions and classes
  - Support for function-based and class-based CLI patterns
  - Subcommand support via class methods
  - Global options via `__init__` parameters

- **Type System**
  - Automatic type conversion for all Python primitives (str, int, float, bool)
  - Support for `pathlib.Path` type
  - Collection types: `list`, `tuple`, `set`, `frozenset`
  - `Optional` and `Union` type handling
  - `Literal` types for choices
  - `Enum` types with automatic member name conversion
  - `Annotated` types with `Arg` metadata

- **`Arg` Metadata Class**
  - Short and long flag customization (`-n`, `--name`)
  - Custom help text per argument
  - Positional arguments support
  - Default value overrides
  - Choices constraints
  - Action customization (store_true, store_false, count, etc.)
  - Argument groups and mutually exclusive options
  - Hidden arguments for internal/debug options
  - Skip option to exclude parameters from CLI

- **Docstring Parsing**
  - Automatic docstring detection and parsing
  - Google-style docstring support
  - NumPy-style docstring support
  - Sphinx/reST docstring support
  - Parameter descriptions extracted to help text

- **Inheritance Support**
  - MRO (Method Resolution Order) traversal for inherited parameters
  - Mixin classes for reusable options
  - Cooperative inheritance with `**kwargs`
  - Type conflict warnings
  - `traverse_mro` option to disable inheritance

- **Plugin System**
  - Entry point-based plugin discovery (`wargs.converters`)
  - Custom converter registration
  - `PluginRegistry` for managing loaded plugins
  - `ConverterRegistry` for type converters
  - `@converter` decorator for registering custom converters

- **Dataclass Support**
  - `expand_dataclass()` for expanding dataclass fields to CLI args
  - `reconstruct_dataclass()` for building dataclass from parsed args
  - Support for `default_factory` fields

- **Utilities**
  - `explain()` function for debugging wargs-decorated functions
  - `get_parser()` to access the underlying ArgumentParser
  - `get_config()` to access the ParserConfig
  - `is_debug_enabled()` and `debug_print()` for debugging
  - `_wargs_config` property on wrappers

- **Documentation**
  - Full MkDocs documentation site
  - Getting Started guide
  - User Guide with type system, docstrings, subcommands, inheritance
  - Cookbook with 13 recipes for common patterns
  - Migration guides from argparse and Click
  - API reference documentation

- **Examples**
  - Simple greeting CLI (`simple/greet.py`)
  - Typed file processing (`typed/process.py`)
  - Git-like subcommands (`subcommands/git_clone.py`)
  - Mixin-based inheritance (`inheritance/mixins.py`)
  - Advanced custom types (`advanced/custom_types.py`)

### Infrastructure

- Python 3.8-3.12 support
- Full test suite with 485+ tests
- 97%+ code coverage
- Type annotations with mypy strict mode
- ruff for linting and formatting
- tox for multi-version testing
- MkDocs documentation with mkdocstrings

## [0.1.0] - Unreleased

Initial development release.

### Core Modules

- `wargs/core/` - Configuration dataclasses and exceptions
- `wargs/introspection/` - Function and type analysis
- `wargs/builders/` - ArgumentParser construction
- `wargs/converters/` - Type converter registry
- `wargs/plugins/` - Plugin discovery system
- `wargs/decorator.py` - Main `@wArgs` decorator
- `wargs/utilities.py` - Debugging utilities
