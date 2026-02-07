# Examples Gallery

Browse real-world examples organized by use case and complexity level.

## Quick Links

All examples are in the [`examples/`](https://github.com/cmoxiv/wArgs/tree/main/examples) directory. Each example is a complete, runnable script with inline documentation.

```bash
# Run any example from the repository root
python examples/simple/greet.py --help
python examples/simple/greet.py --greet-name World
```

## By Complexity

### Beginner

**Simple Function Decoration**
- [`simple/greet.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/simple/greet.py) - Basic `@wArgs` usage with strings and integers
- [`simple/flags.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/simple/flags.py) - Boolean flags and optional parameters

**Type Hints and Conversion**
- [`typed/process.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/typed/process.py) - `Path` type handling, file I/O
- [`typed/numbers.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/typed/numbers.py) - Integer, float, and numeric validation

**What you'll learn**:
- Applying the `@wArgs` decorator
- Using type hints for automatic conversion
- Default values and optional parameters
- Accessing parsed arguments

### Intermediate

**Class-Based CLIs**
- [`subcommands/git_clone.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/subcommands/git_clone.py) - Git-style CLI with multiple subcommands
- [`subcommands/docker.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/subcommands/docker.py) - Docker-style nested commands

**Custom Type Converters**
- [`advanced/custom_types.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/custom_types.py) - Registering converters for custom types
- [`advanced/enum_types.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/enum_types.py) - Using Enum for constrained choices

**Docstring Integration**
- [`docstrings/google_style.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/docstrings/google_style.py) - Google-style docstrings
- [`docstrings/numpy_style.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/docstrings/numpy_style.py) - NumPy-style docstrings

**What you'll learn**:
- Creating subcommands from class methods
- Global options vs command-specific arguments
- Custom type conversion and validation
- Generating help from docstrings

### Advanced

**Inheritance Patterns**
- [`inheritance/mixins.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/inheritance/mixins.py) - Cooperative inheritance with mixins
- [`inheritance/abstract.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/inheritance/abstract.py) - Abstract base classes for CLIs

**Complex Type Handling**
- [`advanced/generics.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/generics.py) - Generic types and containers
- [`advanced/dataclasses.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/dataclasses.py) - Dataclass parameters

**Configuration & Customization**
- [`advanced/dict_expansion.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/dict_expansion.py) - Dictionary expansion to CLI args
- [`advanced/arg_config.py`](https://github.com/cmoxiv/wArgs/blob/main/examples/advanced/arg_config.py) - Fine-grained `Arg()` configuration

**What you'll learn**:
- Method resolution order (MRO) traversal
- Complex type hierarchies
- Advanced argument configuration
- Custom help formatting

## By Use Case

### Data Processing

**File Processing**
```python
# examples/use-cases/data/file_processor.py
from pathlib import Path
from wArgs import wArgs

@wArgs
def process_csv(
    input: Path,
    output: Path,
    delimiter: str = ",",
    skip_header: bool = False,
):
    """Process CSV files with custom delimiter."""
    # Implementation
```

**Data Transformation**
```python
# examples/use-cases/data/transformer.py
from typing import Literal
from wArgs import wArgs

@wArgs
def transform(
    input_format: Literal["json", "yaml", "csv"],
    output_format: Literal["json", "yaml", "csv"],
    input_file: Path,
    output_file: Path,
):
    """Transform data between formats."""
    # Implementation
```

### System Administration

**Process Management**
```python
# examples/use-cases/sysadmin/process_manager.py
from wArgs import wArgs

@wArgs
class ProcessManager:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def start(self, service: str, port: int = 8080):
        """Start a service."""
        pass

    def stop(self, service: str, force: bool = False):
        """Stop a service."""
        pass

    def restart(self, service: str):
        """Restart a service."""
        pass
```

**Log Analysis**
```python
# examples/use-cases/sysadmin/log_analyzer.py
from pathlib import Path
from datetime import datetime
from wArgs import wArgs

@wArgs
def analyze_logs(
    log_file: Path,
    since: datetime,
    level: str = "ERROR",
    output: Path | None = None,
):
    """Analyze log files for errors."""
    # Implementation
```

### Web Services

**API Client**
```python
# examples/use-cases/web/api_client.py
from wArgs import wArgs
from typing import Literal

@wArgs
class APIClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url
        self.token = token

    def get(self, endpoint: str):
        """GET request."""
        pass

    def post(self, endpoint: str, data: str):
        """POST request with JSON data."""
        pass
```

**Web Scraper**
```python
# examples/use-cases/web/scraper.py
from wArgs import wArgs
from pathlib import Path

@wArgs
def scrape(
    url: str,
    output: Path,
    timeout: int = 30,
    user_agent: str = "wArgs-Scraper/1.0",
):
    """Scrape a website and save results."""
    # Implementation
```

### Development Tools

**Build Tool**
```python
# examples/use-cases/devtools/builder.py
from wArgs import wArgs

@wArgs
class Build:
    def __init__(self, config: Path = Path("build.toml")):
        self.config = config

    def clean(self):
        """Remove build artifacts."""
        pass

    def compile(self, target: str = "release"):
        """Compile the project."""
        pass

    def test(self, verbose: bool = False):
        """Run tests."""
        pass
```

## Running Examples

### From the Repository

```bash
# Clone the repository
git clone https://github.com/cmoxiv/wArgs.git
cd wArgs

# Install wArgs
pip install -e .

# Run any example
python examples/simple/greet.py --greet-name "World"
python examples/subcommands/git_clone.py --help
python examples/advanced/custom_types.py --help
```

### Standalone Scripts

Each example is self-contained and can be copied directly:

```bash
# Copy an example to your project
cp examples/simple/greet.py my_cli.py

# Customize and run
python my_cli.py --help
```

## Example Structure

Each example follows this pattern:

```python
#!/usr/bin/env python3
"""
Example: Brief description

Demonstrates:
- Feature 1
- Feature 2
- Feature 3
"""

from wArgs import wArgs
# Other imports

@wArgs
def example_function(param: Type):
    """Function docstring."""
    # Implementation
    pass

if __name__ == "__main__":
    example_function()
```

## Contributing Examples

Have a great example? We'd love to include it!

### Requirements

- **Self-contained**: Minimal external dependencies (prefer stdlib)
- **Documented**: Clear docstrings and inline comments
- **Focused**: Demonstrates one main concept
- **Realistic**: Solves a real-world problem
- **Tested**: Works correctly with current wArgs version

### Submission Process

1. Add your example to `examples/` in an appropriate subdirectory
2. Follow the existing naming convention: `feature_name.py`
3. Include a docstring explaining what it demonstrates
4. Test it thoroughly
5. Submit a PR with description

See [CONTRIBUTING.md](https://github.com/cmoxiv/wArgs/blob/main/CONTRIBUTING.md) for more details.

## Example Categories

### Current Categories

- `simple/` - Basic usage patterns
- `typed/` - Type system examples
- `subcommands/` - Class-based CLIs
- `advanced/` - Complex features
- `inheritance/` - Inheritance patterns
- `docstrings/` - Documentation styles

### Proposed Categories

Help us expand the examples! We'd love examples for:

- Database CLIs (SQLAlchemy, raw SQL)
- Testing tools (pytest plugins, test runners)
- Deployment scripts (Docker, K8s)
- CI/CD tools
- Configuration management
- Monitoring and alerting
- Code generation
- Project scaffolding

## Learn More

- **Tutorial**: [getting-started/tutorial.md](getting-started/tutorial.md) - Step-by-step guide
- **User Guide**: [guide/basic-usage.md](guide/basic-usage.md) - Comprehensive documentation
- **Cookbook**: [cookbook/patterns.md](cookbook/patterns.md) - Common patterns and recipes
- **API Reference**: [api/decorators.md](api/decorators.md) - Complete API documentation

---

*Browse all examples on [GitHub](https://github.com/cmoxiv/wArgs/tree/main/examples) or [suggest new examples](https://github.com/cmoxiv/wArgs/discussions).*
