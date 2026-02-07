# Advanced Usage

This guide covers advanced wArgs features and patterns.

## The Arg Class

Use `Arg` with `Annotated` for fine-grained control:

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def process(
    input_file: Annotated[str, Arg("-i", help="Input file path")],
    output: Annotated[str, Arg("-o", "--out", help="Output file")] = "out.txt",
    verbose: Annotated[bool, Arg("-v")] = False,
) -> None:
    """Process files."""
    ...
```

```bash
$ python app.py -i data.txt -o result.txt -v
$ python app.py --input-file data.txt --out result.txt --verbose
```

### Arg Parameters

| Parameter | Description |
|-----------|-------------|
| `short` | Short flag like `-n` |
| `long` | Long flag override |
| `help` | Help text |
| `metavar` | Placeholder in help |
| `choices` | Valid values |
| `action` | argparse action |
| `nargs` | Number of values |
| `default` | Default value override |
| `required` | Override required status |
| `dest` | Destination attribute |
| `group` | Argument group name |
| `mutually_exclusive` | Exclusive group name |
| `positional` | Make positional |
| `hidden` | Hide from help |
| `skip` | Skip this parameter |
| `envvar` | Environment variable |

## Positional Arguments

Make arguments positional:

```python
@wArgs
def copy(
    source: Annotated[str, Arg(positional=True)],
    dest: Annotated[str, Arg(positional=True)],
) -> None:
    """Copy source to dest."""
    print(f"Copying {source} to {dest}")
```

```bash
$ python copy.py source.txt dest.txt
Copying source.txt to dest.txt
```

## Hidden Arguments

Hide arguments from help (useful for debugging):

```python
@wArgs
def deploy(
    env: str,
    debug_mode: Annotated[bool, Arg(hidden=True)] = False,
) -> None:
    """Deploy application."""
    if debug_mode:
        print("Debug mode enabled")
```

```bash
$ python app.py --help
# --debug-mode is not shown

$ python app.py --env prod --debug-mode
Debug mode enabled
```

## Skipping Parameters

Skip parameters that shouldn't become arguments:

```python
@wArgs
def process(
    data: str,
    _internal: Annotated[str, Arg(skip=True)] = "default",
) -> None:
    """Process data."""
    print(f"Data: {data}, Internal: {_internal}")
```

## Argument Groups

Organize arguments into groups:

```python
@wArgs
def server(
    host: Annotated[str, Arg(group="Network")] = "localhost",
    port: Annotated[int, Arg(group="Network")] = 8080,
    debug: Annotated[bool, Arg(group="Development")] = False,
    reload: Annotated[bool, Arg(group="Development")] = False,
) -> None:
    """Start the server."""
    ...
```

```bash
$ python server.py --help
Network:
  --host HOST
  --port PORT

Development:
  --debug
  --reload
```

## Mutually Exclusive Options

```python
@wArgs
def output(
    json: Annotated[bool, Arg(mutually_exclusive="format")] = False,
    xml: Annotated[bool, Arg(mutually_exclusive="format")] = False,
    csv: Annotated[bool, Arg(mutually_exclusive="format")] = False,
) -> None:
    """Output data in a format."""
    if json:
        print("JSON output")
    elif xml:
        print("XML output")
    elif csv:
        print("CSV output")
```

```bash
$ python app.py --json --xml
# Error: --json and --xml are mutually exclusive
```

## Custom Metavar

```python
@wArgs
def download(
    url: Annotated[str, Arg(metavar="URL")],
    output: Annotated[str, Arg("-o", metavar="FILE")] = "output.html",
) -> None:
    """Download a file."""
    ...
```

```bash
$ python app.py --help
  url URL
  -o FILE, --output FILE
```

## Custom Converters

Register converters for custom types:

```python
from wArgs import wArgs, converter

class IPAddress:
    def __init__(self, address: str) -> None:
        parts = address.split(".")
        if len(parts) != 4:
            raise ValueError("Invalid IP address")
        self.parts = [int(p) for p in parts]

    def __str__(self) -> str:
        return ".".join(str(p) for p in self.parts)

@converter(IPAddress)
def convert_ip(value: str) -> IPAddress:
    return IPAddress(value)

@wArgs
def ping(host: IPAddress) -> None:
    """Ping a host."""
    print(f"Pinging {host}")
```

### Converter Registry

```python
from wArgs import ConverterRegistry, get_default_registry

# Get the default registry
registry = get_default_registry()

# Register a converter
registry.register(MyType, my_converter)

# Check if registered
if registry.has(MyType):
    ...

# Get a converter
conv = registry.get(MyType)
```

## Accessing Internal Config

```python
from wArgs import wArgs, get_config, get_parser

@wArgs
def my_command(name: str) -> None:
    ...

# Get the ParserConfig
config = get_config(my_command)
for arg in config.arguments:
    print(f"{arg.name}: {arg.flags}")

# Get the ArgumentParser
parser = get_parser(my_command)
```

## Environment Variables

```python
import os
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def connect(
    host: Annotated[str, Arg(envvar="DB_HOST")] = "localhost",
    password: Annotated[str, Arg(envvar="DB_PASSWORD")] = "",
) -> None:
    """Connect to database."""
    print(f"Connecting to {host}")
```

```bash
$ DB_HOST=prod.example.com python app.py
Connecting to prod.example.com
```

## Debugging

### explain() Function

```python
from wArgs import explain

print(explain(my_command))
print(explain(my_command, verbose=True))
```

### WARGS_DEBUG Environment Variable

```bash
$ WARGS_DEBUG=1 python app.py --name test
[wargs] Building parser for function: app
[wargs] Parsing args: ['--name', 'test']
[wargs] Parsed result: Namespace(name='test')
```

### _wargs_config Attribute

```python
@wArgs
def my_command(name: str) -> None:
    ...

# After parser is built
_ = my_command.parser
config = my_command._wargs_config
```

## Testing CLIs

```python
import pytest
from wArgs import wArgs

@wArgs
def greet(name: str) -> str:
    return f"Hello, {name}!"

def test_greet_cli():
    result = greet.run(["--name", "World"])
    assert result == "Hello, World!"

def test_greet_direct():
    result = greet(name="Test")
    assert result == "Hello, Test!"

def test_greet_parser():
    args = greet.parse_args(["--name", "Parse"])
    assert args.name == "Parse"
```

## Best Practices

1. **Use type hints** for automatic conversion
2. **Write docstrings** for help text
3. **Use Arg sparingly** - only when needed
4. **Keep global options simple** in class CLIs
5. **Test both CLI and direct** call modes
