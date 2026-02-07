# Docstrings

wArgs extracts help text from docstrings automatically. It supports three major docstring formats.

## Supported Formats

wArgs auto-detects and parses:

- **Google style** (recommended)
- **NumPy style**
- **Sphinx (reST) style**

## Google Style

The most common format, used by Google and many Python projects:

```python
@wArgs
def greet(name: str, times: int = 1) -> None:
    """Greet someone multiple times.

    A longer description can go here. It will be used
    as the epilog in help output.

    Args:
        name: The name of the person to greet.
        times: How many times to greet them.

    Returns:
        None

    Raises:
        ValueError: If times is negative.
    """
    for _ in range(times):
        print(f"Hello, {name}!")
```

```bash
$ python greet.py --help
usage: greet.py [-h] --name NAME [--times TIMES]

Greet someone multiple times.

options:
  -h, --help     show this help message and exit
  --name NAME    The name of the person to greet.
  --times TIMES  How many times to greet them. (default: 1)
```

## NumPy Style

Popular in scientific Python projects:

```python
@wArgs
def process(data: str, verbose: bool = False) -> None:
    """Process input data.

    Parameters
    ----------
    data : str
        The input data to process.
    verbose : bool, optional
        Enable verbose output.

    Returns
    -------
    None
    """
    ...
```

## Sphinx Style

Used in Sphinx documentation:

```python
@wArgs
def calculate(x: float, y: float) -> None:
    """Calculate something.

    :param x: The first value.
    :param y: The second value.
    :type x: float
    :type y: float
    :returns: None
    :raises ValueError: If values are invalid.
    """
    ...
```

## Description Extraction

The first line or paragraph becomes the CLI description:

```python
@wArgs
def my_command() -> None:
    """This is the description.

    This is additional detail that may be shown
    in extended help.
    """
    ...
```

```bash
$ python app.py --help
usage: app.py [-h]

This is the description.
```

## Parameter Descriptions

Parameter descriptions become argument help text:

```python
@wArgs
def copy(
    source: str,
    dest: str,
    recursive: bool = False,
) -> None:
    """Copy files.

    Args:
        source: Source file or directory path.
        dest: Destination path.
        recursive: Copy directories recursively.
    """
    ...
```

```bash
$ python copy.py --help
  --source SOURCE      Source file or directory path.
  --dest DEST          Destination path.
  --recursive          Copy directories recursively.
```

## Multi-line Descriptions

Long descriptions are preserved:

```python
@wArgs
def deploy(env: str) -> None:
    """Deploy the application.

    Args:
        env: Target environment. Valid values are 'dev',
            'staging', and 'prod'. The deployment process
            varies based on the environment.
    """
    ...
```

## Class Docstrings

For class-based CLIs, the class docstring becomes the main description:

```python
@wArgs
class CLI:
    """File management utility.

    A comprehensive tool for managing files and directories.
    Supports common operations like copy, move, and delete.
    """

    def copy(self, source: str, dest: str) -> None:
        """Copy a file.

        Args:
            source: Source file path.
            dest: Destination path.
        """
        ...

    def move(self, source: str, dest: str) -> None:
        """Move a file.

        Args:
            source: Source file path.
            dest: Destination path.
        """
        ...
```

```bash
$ python files.py --help
usage: files.py [-h] {copy,move} ...

File management utility.

positional arguments:
  {copy,move}
    copy       Copy a file.
    move       Move a file.
```

## Combining with Arg

When using `Arg`, the `help` parameter overrides the docstring:

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def greet(
    name: Annotated[str, Arg(help="Name to greet (overrides docstring)")],
) -> None:
    """Greet someone.

    Args:
        name: This description is ignored.
    """
    ...
```

## Best Practices

1. **Keep the first line concise** - It becomes the CLI description
2. **Document all parameters** - They become --help text
3. **Be consistent** - Pick one docstring style and stick with it
4. **Include defaults context** - Explain what default values mean

```python
@wArgs
def backup(
    path: str,
    compress: bool = True,
    level: int = 6,
) -> None:
    """Backup files to archive.

    Args:
        path: Directory to backup.
        compress: Enable compression. Enabled by default for
            smaller archive sizes.
        level: Compression level from 1 (fastest) to 9 (smallest).
            Default of 6 provides good balance.
    """
    ...
```
