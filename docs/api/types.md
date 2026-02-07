# Types

## Configuration Types

### ParserConfig

Configuration for an ArgumentParser.

::: wargs.core.config.ParserConfig
    options:
      show_root_heading: true

### ArgumentConfig

Configuration for a single CLI argument.

::: wargs.core.config.ArgumentConfig
    options:
      show_root_heading: true

### ParameterInfo

Information about a function parameter.

::: wargs.core.config.ParameterInfo
    options:
      show_root_heading: true

### FunctionInfo

Information about a function.

::: wargs.core.config.FunctionInfo
    options:
      show_root_heading: true

### TypeInfo

Information about a resolved type.

::: wargs.core.config.TypeInfo
    options:
      show_root_heading: true

## Converter Types

### ConverterRegistry

Registry for type converters.

::: wargs.ConverterRegistry
    options:
      show_root_heading: true
      members:
        - register
        - converter
        - get
        - has
        - unregister
        - clear
        - load_entry_points

### converter decorator

Decorator to register a converter on the default registry.

::: wargs.converters.registry.converter
    options:
      show_root_heading: true

### get_default_registry

Get the default global converter registry.

::: wargs.converters.registry.get_default_registry
    options:
      show_root_heading: true

## Built-in Converters

wArgs includes converters for common types:

| Type | Converter | Format |
|------|-----------|--------|
| `datetime` | `convert_datetime` | ISO 8601 |
| `date` | `convert_date` | YYYY-MM-DD |
| `time` | `convert_time` | HH:MM:SS |
| `UUID` | `convert_uuid` | Standard UUID |
| `Decimal` | `convert_decimal` | Decimal string |
| `Path` | `convert_path` | File path |
| `complex` | `convert_complex` | a+bj |
| `Fraction` | `convert_fraction` | a/b |

### Registering Built-in Converters

```python
from wargs.converters.builtin import register_builtin_converters

# Register on default registry
register_builtin_converters()

# Or on custom registry
from wArgs import ConverterRegistry
registry = ConverterRegistry()
register_builtin_converters(registry)
```

## Custom Converter Example

```python
from wArgs import converter

class EmailAddress:
    def __init__(self, address: str) -> None:
        if "@" not in address:
            raise ValueError("Invalid email")
        self.address = address

@converter(EmailAddress)
def convert_email(value: str) -> EmailAddress:
    return EmailAddress(value)
```
