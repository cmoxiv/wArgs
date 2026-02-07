# Utilities

## explain

Get a human-readable explanation of a wargs-decorated function.

::: wargs.utilities.explain
    options:
      show_root_heading: true

### Example

```python
from wArgs import wArgs, explain

@wArgs
def greet(name: str, count: int = 1) -> None:
    """Greet someone.

    Args:
        name: Person to greet
        count: Number of times
    """
    pass

print(explain(greet))
```

Output:

```
Function: greet
Type: Single-command CLI

Arguments:
  --name (str) [required]
  --count (int) [default: 1]
```

With `verbose=True`:

```python
print(explain(greet, verbose=True))
```

```
Function: greet
Type: Single-command CLI

Arguments:
  --name (str) [required]
    Help: Person to greet
  --count (int) [default: 1]
    Help: Number of times
```

## get_parser

Get the ArgumentParser for a wargs-decorated function.

::: wargs.utilities.get_parser
    options:
      show_root_heading: true

### Example

```python
from wArgs import wArgs, get_parser

@wArgs
def my_command(name: str) -> None:
    pass

parser = get_parser(my_command)

# Extend the parser
parser.add_argument("--extra", help="Extra option")

# Use the parser directly
args = parser.parse_args(["--name", "test", "--extra", "value"])
```

## get_config

Get the ParserConfig for a wargs-decorated function.

::: wargs.utilities.get_config
    options:
      show_root_heading: true

### Example

```python
from wArgs import wArgs, get_config

@wArgs
def my_command(name: str, count: int = 1) -> None:
    pass

config = get_config(my_command)

# Inspect arguments
for arg in config.arguments:
    print(f"{arg.name}: flags={arg.flags}, required={arg.required}")
```

## Debug Utilities

### is_debug_enabled

Check if WARGS_DEBUG environment variable is set.

::: wargs.utilities.is_debug_enabled
    options:
      show_root_heading: true

### debug_print

Print debug output if WARGS_DEBUG is enabled.

::: wargs.utilities.debug_print
    options:
      show_root_heading: true

### WARGS_DEBUG Environment Variable

Set `WARGS_DEBUG=1` to enable debug output:

```bash
$ WARGS_DEBUG=1 python myapp.py --name test
[wargs] Building parser for function: myapp
[wargs] Parsing args: ['--name', 'test']
[wargs] Parsed result: Namespace(name='test')
```

Valid values: `1`, `true`, `yes`, `on` (case-insensitive)
