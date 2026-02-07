# Troubleshooting Guide

This guide helps you diagnose and fix common issues with wArgs.

## Debugging Techniques

### Using explain()

The `explain()` utility shows exactly what wArgs extracted from your function:

```python
from wArgs import wArgs, explain

@wArgs
def greet(name: str, count: int = 1):
    """Greet someone multiple times."""
    for _ in range(count):
        print(f"Hello, {name}!")

# See full introspection details
explain(greet)
```

**Output includes**:
- Function signature and docstring
- Detected parameters with types, defaults, and descriptions
- Type resolution details (origin, args, is_optional)
- Registered converters
- Argument configuration (flags, choices, help text)

Use this when:
- Arguments aren't appearing as expected
- Type conversion is failing
- Docstring parsing seems wrong

### Enable Debug Output

Set the `WARGS_DEBUG` environment variable to see detailed parsing information:

```bash
WARGS_DEBUG=1 python my_cli.py --help
```

This shows:
- `[wargs] Building parser for function: ...`
- `[wargs] Parsing args: [...]`
- `[wargs] Parsed result: Namespace(...)`

### Inspect the Generated Parser

Use `get_parser()` to examine the `ArgumentParser` object:

```python
from wArgs import wArgs, get_parser

@wArgs
def my_cli(name: str):
    pass

parser = get_parser(my_cli)
parser.print_help()  # See generated help
```

### Test Argument Parsing

Test what arguments are being parsed without running your function:

```python
import sys
from wArgs import get_parser

parser = get_parser(my_cli)
args = parser.parse_args(sys.argv[1:])
print(f"Parsed arguments: {args}")
```

## Common Errors

### Import Errors

#### "cannot import name 'wargs'"

**Problem**: Using lowercase `wargs` instead of mixed-case `wArgs`.

**Solution**: Update your import:

```python
# ❌ Wrong
from wargs import wArgs

# ✅ Correct
from wArgs import wArgs
```

**Note**: The PyPI package name is `wargs` (lowercase), but the module exports are `wArgs` (mixed-case).

#### "ModuleNotFoundError: No module named 'wArgs'"

**Problem**: Package not installed or wrong Python environment.

**Solution**:

```bash
# Install from PyPI
pip install wargs

# Or install from source
pip install -e .

# Verify installation
python -c "from wArgs import wArgs; print('Success!')"
```

### Type Resolution Issues

#### "TypeError: unsupported type for argument 'param'"

**Problem**: wArgs doesn't have a converter for your type.

**Solutions**:

1. **Use a built-in type**:
   ```python
   # Supported: str, int, float, bool, Path, list, dict, etc.
   def my_cli(value: int):  # ✅ Works
       pass
   ```

2. **Register a converter**:
   ```python
   from wArgs import wArgs, converter

   @converter(MyCustomType)
   def convert_my_type(value: str) -> MyCustomType:
       return MyCustomType(value)

   @wArgs
   def my_cli(value: MyCustomType):  # ✅ Now works
       pass
   ```

3. **Check type annotation syntax**:
   ```python
   # ❌ Wrong - typo or undefined type
   def my_cli(value: Paht):
       pass

   # ✅ Correct
   from pathlib import Path
   def my_cli(value: Path):
       pass
   ```

#### "AttributeError: 'NoneType' has no attribute ..."

**Problem**: Type hint resolved to `None` (missing import or forward reference issue).

**Solution**:

```python
# ✅ Add missing import
from __future__ import annotations
from pathlib import Path

@wArgs
def process(file: Path):  # Now Path is defined
    pass
```

### Subcommand Problems

#### Methods not appearing as subcommands

**Checklist**:

1. **Is the class decorated?**
   ```python
   @wArgs  # ✅ Required
   class CLI:
       def hello(self):
           pass
   ```

2. **Are methods public?**
   ```python
   class CLI:
       def hello(self):  # ✅ Public - becomes subcommand
           pass

       def _internal(self):  # ❌ Private - ignored
           pass
   ```

3. **Is `__init__` used correctly?**
   ```python
   @wArgs
   class CLI:
       def __init__(self, verbose: bool = False):  # ✅ Global options
           self.verbose = verbose

       def deploy(self, env: str):  # ✅ Subcommand
           pass
   ```

#### Wrong arguments for subcommands

**Problem**: Seeing both `__init__` and method parameters, or wrong prefixes.

**Explanation**: By default, `__init__` parameters become global options:

```bash
# With @wArgs
my_cli --CLI-verbose deploy --deploy-env prod

# If you don't want __init__ params, set traverse_mro=False
@wArgs(traverse_mro=False)
class CLI:
    ...
```

### Docstring Parsing Issues

#### Descriptions not appearing in help

**Problem**: Unsupported docstring format.

**Solution**: Use Google, NumPy, or Sphinx style:

```python
# ✅ Google style (recommended)
def greet(name: str, count: int = 1):
    """Greet someone.

    Args:
        name: The person's name
        count: Number of greetings
    """

# ✅ NumPy style
def greet(name: str, count: int = 1):
    """Greet someone.

    Parameters
    ----------
    name : str
        The person's name
    count : int
        Number of greetings
    """
```

#### Multi-line descriptions truncated

**Problem**: Only first line showing in help.

**Cause**: This is expected behavior - only the first line of parameter descriptions appears in `--help` for brevity.

**Solution**: Keep important info in the first line.

### Argument Value Issues

#### Boolean flags always True

**Problem**: Using boolean arguments incorrectly.

**Explanation**: Boolean parameters become flags (no value needed):

```python
@wArgs
def my_cli(verbose: bool = False):
    pass

# ✅ Correct usage
my_cli --my_cli-verbose      # verbose=True
my_cli                       # verbose=False

# ❌ Wrong - this will fail
my_cli --my_cli-verbose true
```

#### Optional arguments still required

**Problem**: Type hint says `Optional` but CLI still requires the argument.

**Solution**: Add a default value:

```python
# ❌ Still required
def my_cli(name: Optional[str]):
    pass

# ✅ Optional
def my_cli(name: Optional[str] = None):
    pass
```

## Stack Traces

### Understanding wArgs Stack Traces

When errors occur, wArgs stack traces show:

```
Traceback (most recent call last):
  File "my_cli.py", line 10, in <module>
    @wArgs
  File "wArgs/decorator.py", line 45, in wArgs
    return WargsWrapper(func, **kwargs)
  File "wArgs/decorator.py", line 78, in __init__
    self.config = build_parser_config(func)
  File "wArgs/builders/parser.py", line 23, in build_parser_config
    function_info = extract_function_info(func)
  File "wArgs/introspection/signatures.py", line 56, in extract_function_info
    raise IntrospectionError(f"Cannot extract signature: {e}")
wArgs.core.exceptions.IntrospectionError: Cannot extract signature: ...
```

**Key files to check**:

- `decorator.py`: Decorator application and wrapper creation
- `introspection/signatures.py`: Function signature extraction
- `introspection/types.py`: Type resolution
- `builders/arguments.py`: Argument configuration
- `converters/registry.py`: Type converter lookup

### Common Stack Trace Patterns

#### IntrospectionError during decoration

**Cause**: Problem analyzing function signature or docstring.

**Fix**: Use `explain()` to see what was detected, check function definition.

#### ConversionError during execution

**Cause**: Invalid argument value provided by user.

**Fix**: Check converter implementation, validate input in converter.

#### ConfigurationError during decoration

**Cause**: Invalid decorator parameters.

**Fix**: Check `@wArgs(...)` parameters match documented options.

## Advanced Debugging

### Run Tests

If you suspect a bug in wArgs:

```bash
# Clone repo
git clone https://github.com/cmoxiv/wArgs.git
cd wArgs

# Install dev dependencies
pip install -e ".[dev]"

# Run relevant tests
pytest tests/unit/test_decorator.py -v
pytest tests/unit/introspection/test_signatures.py -v
```

### Create Minimal Reproduction

When reporting issues, create a minimal example:

```python
# minimal_repro.py
from wArgs import wArgs

@wArgs
def my_cli(param: SomeType):
    """Description."""
    pass

if __name__ == "__main__":
    my_cli()
```

Include:
- Python version: `python --version`
- wArgs version: `pip show wargs`
- Full error message and stack trace
- Expected vs actual behavior

## Getting Help

If you're still stuck after trying these steps:

1. **Check the FAQ**: [faq.md](faq.md) covers common questions
2. **Search issues**: [GitHub Issues](https://github.com/cmoxiv/wArgs/issues)
3. **Browse examples**: [examples/](../examples/) directory
4. **Ask for help**:
   - [GitHub Discussions](https://github.com/cmoxiv/wArgs/discussions) - Questions and community help
   - [Create an issue](https://github.com/cmoxiv/wArgs/issues/new) - Bug reports and problems

### When Creating an Issue

Include:

1. **Environment**:
   ```bash
   python --version
   pip show wargs
   ```

2. **Minimal code example** that reproduces the issue

3. **Full error message** with stack trace

4. **Expected behavior** - what should happen

5. **Actual behavior** - what actually happens

6. **Debugging attempted** - what you've tried from this guide

---

*For more help, see [FAQ](faq.md) or [join the discussion](https://github.com/cmoxiv/wArgs/discussions).*
