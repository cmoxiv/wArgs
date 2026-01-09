# Changelog

All notable changes to wArgs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of wArgs
- `@wargs` decorator for functions and classes
- Automatic argument parsing from type hints
- Support for Google, NumPy, and Sphinx docstring formats
- `Arg` metadata class for fine-grained control
- Class-based subcommand support
- MRO traversal for inherited parameters
- Built-in type converters (datetime, UUID, Decimal, etc.)
- Custom converter registry with `@converter` decorator
- Utility functions: `explain()`, `get_parser()`, `get_config()`
- `WARGS_DEBUG` environment variable for debugging
- Comprehensive documentation and examples

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [0.1.0] - Unreleased

Initial development release.

### Features
- Function decoration with `@wargs`
- Class decoration for subcommands
- Type hint-based argument conversion
- Docstring parsing for help text
- `Arg` metadata for customization
- Inheritance and mixin support
- Custom type converters
- Debug utilities
