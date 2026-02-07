# Frequently Asked Questions

## General

### Why wArgs vs Click/Typer?

**wArgs** takes a different approach from Click and Typer:

- **Decorator-first**: Just add `@wArgs` to your function - no additional annotations needed
- **Type-native**: Uses Python's native type hints exclusively (no custom parameter objects)
- **No runtime overhead**: wArgs generates standard `argparse.ArgumentParser` objects
- **Class-based subcommands**: Natural support for class-based CLIs with `__init__` parameters
- **Zero dependencies**: Pure Python standard library (except dev dependencies)

**Click/Typer** require custom decorators for each parameter and introduce runtime dependencies, while wArgs leverages Python's built-in introspection.

### Does wArgs work with async functions?

Not currently. Async function support is planned for v2.0. The main challenge is that `argparse` and the standard CLI model are synchronous. We're exploring options for:

- Automatic event loop management
- Integration with `asyncio.run()`
- Support for async context managers

Follow [#123](https://github.com/cmoxiv/wArgs/issues) for updates.

### Can I use wArgs with existing argparse code?

Yes! wArgs generates standard `ArgumentParser` objects that you can customize:

```python
from wArgs import wArgs, get_parser

@wArgs
def my_cli(name: str):
    """My CLI tool."""
    print(f"Hello, {name}!")

# Get the parser and add custom arguments
parser = get_parser(my_cli)
parser.add_argument("--legacy-flag", action="store_true")

# Use it
if __name__ == "__main__":
    parser.parse_args()
```

See [cookbook/migration-argparse.md](cookbook/migration-argparse.md) for more examples.

### Is wArgs compatible with Python 3.8?

Yes! wArgs supports Python 3.8+ and uses `from __future__ import annotations` for backward compatibility. We test against all supported Python versions in CI.

### How does wArgs handle argument prefixing?

All arguments are automatically prefixed with the callable name to avoid conflicts:

```python
@wArgs
def greet(name: str, count: int = 1):
    pass

# CLI: --greet-name, --greet-count
```

This is especially useful for class-based CLIs where `__init__` and methods share argument names.

## Type System

### How do I handle custom types?

Use the `@converter` decorator to register type converters:

```python
from wArgs import wArgs, converter
from pathlib import Path

@converter(Path)
def convert_path(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise ValueError(f"Path does not exist: {value}")
    return path

@wArgs
def process_file(input: Path):
    """Process a file."""
    print(f"Processing {input}")
```

See [examples/advanced/custom_types.py](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/custom_types.py) for complete examples.

### Why isn't my Optional[str] working?

`Optional[str]` alone doesn't make an argument optional in the CLI - you need a default value:

```python
# ❌ Wrong - still required
def greet(name: Optional[str]):
    pass

# ✅ Correct - optional with default
def greet(name: Optional[str] = None):
    pass

# ✅ Also correct - using new union syntax
def greet(name: str | None = None):
    pass
```

The type hint describes what values are *valid*, while the default value controls whether the argument is *required*.

### How do I use Annotated for advanced configuration?

Use `Annotated` with `Arg()` for fine-grained control:

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def deploy(
    env: Annotated[str, Arg(choices=["dev", "staging", "prod"], help="Target environment")],
    verbose: Annotated[bool, Arg(short="-v")] = False,
):
    """Deploy to environment."""
    pass
```

See [guide/type-system.md](guide/type-system.md) for more details.

### Can I use Pydantic models?

Not directly, but you can use dataclasses:

```python
from dataclasses import dataclass
from wArgs import wArgs

@dataclass
class Config:
    host: str
    port: int

@wArgs
def serve(config: Config):
    """Start server."""
    print(f"Serving on {config.host}:{config.port}")
```

Full Pydantic integration is planned for v1.2.

## Common Issues

### "TypeError: unsupported type for argument"

This means wArgs doesn't know how to convert the CLI string to your type. Solutions:

1. **Use a built-in type**: `str`, `int`, `float`, `bool`, `Path`
2. **Register a converter**: Use `@converter` decorator
3. **Debug with `explain()`**: See what wArgs detected

```python
from wArgs import explain

explain(my_function)  # Shows full introspection details
```

### Subcommands not appearing

Check these common issues:

1. **Forgot `@wArgs` decorator**: Class must be decorated
2. **`__init__` signature**: Parameters in `__init__` become global options, not subcommands
3. **Method naming**: Only public methods (not starting with `_`) become subcommands
4. **traverse_mro**: Set to `False` if inherited methods shouldn't be subcommands

```python
# ✅ Correct
@wArgs
class CLI:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def hello(self, name: str):
        """This becomes a subcommand."""
        print(f"Hello, {name}!")

# ❌ Wrong - no methods
@wArgs
class CLI:
    def __init__(self, name: str):
        print(f"Hello, {name}!")
```

### Dictionary expansion not working

Dictionary defaults automatically expand to multiple arguments:

```python
@wArgs
def connect(config: dict = {"host": "localhost", "port": 8080}):
    pass

# CLI: --connect-config-host, --connect-config-port
```

If you want a single argument that takes JSON, use `str` and parse manually.

## Performance

### Does wArgs add overhead?

**Parse-time overhead**: Minimal - introspection happens once when the decorator is applied (import time), not on each invocation.

**Runtime overhead**: None - wArgs generates standard `argparse.ArgumentParser` objects that handle argument parsing. The decorated function runs directly after parsing.

**Memory overhead**: Negligible - cached introspection metadata is small (~1KB per function).

### Is introspection cached?

Yes! Function introspection happens once at decoration time (when the module is imported). The results are cached in the `WargsWrapper` object, so there's no repeated introspection overhead.

### Can I use wArgs in production?

Absolutely! wArgs is:

- **Battle-tested**: 600+ passing tests with 100% coverage target
- **Type-safe**: Full mypy compliance in strict mode
- **Stable API**: Semantic versioning, no breaking changes in minor releases
- **Pure Python**: No C extensions or complex dependencies

Used in production by several projects (see [examples](examples.md)).

## Development

### How do I contribute?

See the [CONTRIBUTING.md](https://github.com/cmoxiv/wArgs/blob/main/CONTRIBUTING.md) file in the repository for development setup, coding standards, and the contribution process.

### How do I request a feature?

1. Check [ROADMAP.md](https://github.com/cmoxiv/wArgs/blob/main/ROADMAP.md) to see if it's already planned
2. Search [issues](https://github.com/cmoxiv/wArgs/issues) for similar requests
3. Create a [Feature Request](https://github.com/cmoxiv/wArgs/issues/new?template=feature_request.yml) with details

### Where can I get help?

- **Documentation**: Start with [Getting Started](getting-started/quickstart.md)
- **Examples**: Browse [examples/](https://github.com/cmoxiv/wArgs/tree/main/examples/) directory
- **Issues**: Search [existing issues](https://github.com/cmoxiv/wArgs/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/cmoxiv/wArgs/discussions)
- **Troubleshooting**: See [troubleshooting guide](troubleshooting.md)

---

*Don't see your question? [Open a discussion](https://github.com/cmoxiv/wArgs/discussions/new?category=q-a) or [create an issue](https://github.com/cmoxiv/wArgs/issues/new).*
