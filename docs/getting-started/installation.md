# Installation

## Requirements

- Python 3.8 or higher
- No runtime dependencies

## Install from PyPI

The recommended way to install wArgs is via pip:

```bash
pip install wargs
```

## Install from Source

To install the latest development version:

```bash
pip install git+https://github.com/wargs/wargs.git
```

Or clone and install locally:

```bash
git clone https://github.com/wargs/wargs.git
cd wargs
pip install -e .
```

## Development Installation

For contributing to wArgs:

```bash
git clone https://github.com/wargs/wargs.git
cd wargs
pip install -e ".[dev]"
```

This installs all development dependencies including:

- pytest for testing
- mypy for type checking
- ruff for linting and formatting

## Verify Installation

```python
>>> import wargs
>>> wargs.__version__
'0.1.0'
```

Or from the command line:

```bash
python -c "import wargs; print(wargs.__version__)"
```

## Optional Dependencies

### Documentation

To build the documentation locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

### All Dependencies

To install everything:

```bash
pip install -e ".[all]"
```
