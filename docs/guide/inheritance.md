# Inheritance

wArgs supports inheriting CLI options from parent classes, enabling reusable option sets through mixins.

## Basic Inheritance

Child classes inherit parent `__init__` parameters:

```python
from wargs import wargs

class BaseOptions:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

@wargs
class CLI(BaseOptions):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def run(self) -> None:
        """Run the command."""
        if self.verbose:
            print(f"Running with name: {self.name}")
        print(f"Hello, {self.name}!")
```

```bash
$ python app.py --help
usage: app.py [-h] --name NAME [--verbose] {run} ...

options:
  --name NAME
  --verbose

$ python app.py --verbose --name World run
Running with name: World
Hello, World!
```

## Mixin Pattern

Create reusable option sets with mixins:

```python
from wargs import wargs

class VerboseMixin:
    """Adds --verbose option."""
    def __init__(self, verbose: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.verbose = verbose

class DryRunMixin:
    """Adds --dry-run option."""
    def __init__(self, dry_run: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dry_run = dry_run

class ConfigMixin:
    """Adds --config option."""
    def __init__(self, config: str = "config.yml", **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config

@wargs
class CLI(VerboseMixin, DryRunMixin, ConfigMixin):
    """A CLI with multiple inherited options."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def deploy(self, env: str) -> None:
        """Deploy to an environment."""
        if self.verbose:
            print(f"Using config: {self.config}")
            print(f"Deploying to: {env}")
        if self.dry_run:
            print("(dry run)")
        else:
            print(f"Deployed to {env}!")
```

```bash
$ python app.py --help
options:
  --verbose
  --dry-run
  --config CONFIG

$ python app.py --verbose --dry-run deploy --env prod
Using config: config.yml
Deploying to: prod
(dry run)
```

## How MRO Traversal Works

wArgs traverses the Method Resolution Order (MRO) to collect parameters:

```python
class A:
    def __init__(self, a: str = "a") -> None:
        self.a = a

class B(A):
    def __init__(self, b: str = "b") -> None:
        super().__init__()
        self.b = b

@wargs
class C(B):
    def __init__(self, c: str = "c") -> None:
        super().__init__()
        self.c = c

    def run(self) -> None:
        print(f"a={self.a}, b={self.b}, c={self.c}")
```

The MRO for `C` is: `[C, B, A, object]`

wArgs collects parameters from all classes, resulting in `--a`, `--b`, and `--c` options.

## Parameter Override

Child parameters override parent parameters with the same name:

```python
class Base:
    def __init__(self, level: int = 1) -> None:
        self.level = level

@wargs
class Child(Base):
    def __init__(self, level: int = 5) -> None:  # Override default
        super().__init__(level)
        self.level = level

    def show(self) -> None:
        print(f"Level: {self.level}")
```

```bash
$ python app.py show
Level: 5  # Uses child's default
```

## Type Conflict Warning

wArgs warns when child and parent have conflicting types:

```python
class Base:
    def __init__(self, value: str = "default") -> None:
        self.value = value

@wargs
class Child(Base):
    def __init__(self, value: int = 0) -> None:  # Different type!
        super().__init__(str(value))
        self.value = value
```

```
UserWarning: Parameter 'value' in Child has type int but parent Base
has type str. Using child type.
```

## Disabling MRO Traversal

Use `traverse_mro=False` to disable inheritance:

```python
class Base:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

@wargs(traverse_mro=False)
class CLI(Base):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def run(self) -> None:
        print(f"Name: {self.name}")
```

```bash
$ python app.py --help
# Only shows --name, not --debug
```

## Cooperative Inheritance

For multiple inheritance to work correctly, use `**kwargs`:

```python
class Mixin1:
    def __init__(self, opt1: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.opt1 = opt1

class Mixin2:
    def __init__(self, opt2: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.opt2 = opt2

@wargs
class CLI(Mixin1, Mixin2):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name

    def run(self) -> None:
        print(f"name={self.name}, opt1={self.opt1}, opt2={self.opt2}")
```

The `**kwargs` pattern ensures all parameters are passed through the chain.

## Best Practices

1. **Use `**kwargs` in mixins** for cooperative inheritance
2. **Keep mixin options optional** with sensible defaults
3. **Document inherited options** in the class docstring
4. **Avoid type conflicts** between parent and child

```python
class VerboseMixin:
    """Adds verbose output support.

    Inherited Options:
        --verbose: Enable verbose output
    """
    def __init__(self, verbose: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")
```
