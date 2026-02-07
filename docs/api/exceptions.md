# Exceptions

wArgs defines a hierarchy of exceptions for different error scenarios.

## Exception Hierarchy

```
WargsError (base)
├── ConfigurationError  # Invalid decorator config
├── IntrospectionError  # Function analysis errors
└── ConversionError     # Argument conversion errors
```

## WargsError

Base exception for all wArgs errors.

::: wArgs.WargsError
    options:
      show_root_heading: true

## ConfigurationError

Raised when decorator configuration is invalid.

::: wArgs.ConfigurationError
    options:
      show_root_heading: true

### When It's Raised

- Invalid `Arg` configuration
- Conflicting options
- Invalid decorator arguments

### Example

```python
from wArgs import wArgs, Arg
from typing import Annotated

# This raises ConfigurationError at import time
@wArgs
def bad_config(
    name: Annotated[str, Arg(positional=True, short="-n")],  # Can't have both!
) -> None:
    pass
```

## IntrospectionError

Raised when function introspection fails.

::: wArgs.IntrospectionError
    options:
      show_root_heading: true

### When It's Raised

- Unable to inspect function signature
- Invalid type annotations
- Unresolvable forward references

### Example

```python
from wArgs import wArgs

# This might raise IntrospectionError
@wArgs
def problematic(x: "NonExistentType") -> None:
    pass
```

## ConversionError

Raised when argument conversion fails.

::: wArgs.ConversionError
    options:
      show_root_heading: true

### When It's Raised

- Invalid value for type
- Custom converter failure
- Type coercion failure

### Example

```python
from wArgs import wArgs
from datetime import datetime

@wArgs
def schedule(when: datetime) -> None:
    print(f"Scheduled: {when}")

# This raises ConversionError at runtime
schedule.run(["--when", "not-a-date"])
# ConversionError: Cannot convert 'not-a-date' to datetime.
```

## ErrorContext

Context information for exceptions.

::: wArgs.ErrorContext
    options:
      show_root_heading: true

## Handling Exceptions

```python
from wArgs import wArgs, WargsError, ConversionError
import sys

@wArgs
def my_command(count: int) -> None:
    print(f"Count: {count}")

try:
    my_command()
except ConversionError as e:
    print(f"Invalid argument: {e}", file=sys.stderr)
    sys.exit(1)
except WargsError as e:
    print(f"CLI error: {e}", file=sys.stderr)
    sys.exit(1)
```

## Best Practices

1. **Catch specific exceptions** when you need specific handling
2. **Catch WargsError** as a fallback for all wArgs errors
3. **Let ConfigurationError propagate** - it indicates a bug in your code
4. **Handle ConversionError** for user-friendly error messages
