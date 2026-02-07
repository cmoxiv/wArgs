# Common Patterns

This cookbook contains common patterns and recipes for wArgs.

## 1. File Input/Output

```python
from pathlib import Path
from wArgs import wArgs

@wArgs
def process(
    input_file: Path,
    output_file: Path = Path("output.txt"),
) -> None:
    """Process a file.

    Args:
        input_file: Input file to process
        output_file: Output file path
    """
    content = input_file.read_text()
    processed = content.upper()
    output_file.write_text(processed)
    print(f"Processed {input_file} -> {output_file}")
```

```bash
$ python process.py --input-file data.txt --output-file result.txt
```

## 2. Multiple Input Files

```python
from pathlib import Path
from wArgs import wArgs

@wArgs
def concat(files: list[Path], output: Path) -> None:
    """Concatenate multiple files.

    Args:
        files: Files to concatenate
        output: Output file
    """
    contents = [f.read_text() for f in files]
    output.write_text("\n".join(contents))
    print(f"Concatenated {len(files)} files to {output}")
```

```bash
$ python concat.py --files a.txt b.txt c.txt --output combined.txt
```

## 3. Verbose Mode Mixin

```python
from wArgs import wArgs

class VerboseMixin:
    """Adds verbose output support."""

    def __init__(self, verbose: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.verbose = verbose

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"[INFO] {message}")

@wArgs
class CLI(VerboseMixin):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def process(self, data: str) -> None:
        """Process data."""
        self.log(f"Processing: {data}")
        print(f"Result: {data.upper()}")
```

```bash
$ python app.py --verbose process --data "hello"
[INFO] Processing: hello
Result: HELLO
```

## 4. Configuration File Support

```python
import json
from pathlib import Path
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
class CLI:
    def __init__(
        self,
        config: Annotated[Path, Arg("-c", help="Config file")] = Path("config.json"),
    ) -> None:
        self.config_data = {}
        if config.exists():
            self.config_data = json.loads(config.read_text())

    def show(self) -> None:
        """Show current configuration."""
        print(json.dumps(self.config_data, indent=2))

    def get(self, key: str) -> None:
        """Get a config value."""
        print(self.config_data.get(key, "Not found"))
```

## 5. Progress Output

```python
from wArgs import wArgs

@wArgs
def download(
    urls: list[str],
    quiet: bool = False,
) -> None:
    """Download files from URLs.

    Args:
        urls: URLs to download
        quiet: Suppress progress output
    """
    for i, url in enumerate(urls, 1):
        if not quiet:
            print(f"[{i}/{len(urls)}] Downloading {url}...")
        # download logic here
        if not quiet:
            print(f"  Done!")
```

## 6. Output Format Selection

```python
import json
from typing import Literal
from wArgs import wArgs

@wArgs
def export(
    data: str,
    format: Literal["json", "csv", "text"] = "text",
) -> None:
    """Export data in various formats.

    Args:
        data: Data to export
        format: Output format
    """
    if format == "json":
        print(json.dumps({"data": data}))
    elif format == "csv":
        print(f"data\n{data}")
    else:
        print(data)
```

```bash
$ python export.py --data "hello" --format json
{"data": "hello"}
```

## 7. Confirmation Prompt

```python
from wArgs import wArgs

@wArgs
def delete(
    path: str,
    force: bool = False,
) -> None:
    """Delete a file.

    Args:
        path: File to delete
        force: Skip confirmation
    """
    if not force:
        response = input(f"Delete {path}? [y/N] ")
        if response.lower() != "y":
            print("Cancelled.")
            return
    print(f"Deleted: {path}")
```

```bash
$ python delete.py --path test.txt
Delete test.txt? [y/N] y
Deleted: test.txt

$ python delete.py --path test.txt --force
Deleted: test.txt
```

## 8. Environment-Based Defaults

```python
import os
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def deploy(
    env: str = os.environ.get("DEPLOY_ENV", "dev"),
    host: str = os.environ.get("DEPLOY_HOST", "localhost"),
) -> None:
    """Deploy to an environment.

    Args:
        env: Target environment (default from DEPLOY_ENV)
        host: Target host (default from DEPLOY_HOST)
    """
    print(f"Deploying to {env} on {host}")
```

```bash
$ DEPLOY_ENV=prod DEPLOY_HOST=example.com python deploy.py
Deploying to prod on example.com

$ python deploy.py --env staging
Deploying to staging on localhost
```

## 9. Logging Integration

```python
import logging
from wArgs import wArgs

@wArgs
def process(
    data: str,
    log_level: str = "INFO",
) -> None:
    """Process data with logging.

    Args:
        data: Data to process
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(level=getattr(logging, log_level))
    logger = logging.getLogger(__name__)

    logger.debug(f"Starting processing: {data}")
    logger.info(f"Processing: {data}")
    result = data.upper()
    logger.debug(f"Result: {result}")
    print(result)
```

```bash
$ python process.py --data hello --log-level DEBUG
DEBUG:__main__:Starting processing: hello
INFO:__main__:Processing: hello
DEBUG:__main__:Result: HELLO
HELLO
```

## 10. Dry Run Mode

```python
from wArgs import wArgs

class DryRunMixin:
    """Adds dry-run support."""

    def __init__(self, dry_run: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dry_run = dry_run

    def execute(self, action: str, func: callable) -> None:
        if self.dry_run:
            print(f"[DRY RUN] Would {action}")
        else:
            func()
            print(f"Done: {action}")

@wArgs
class FileManager(DryRunMixin):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def delete(self, path: str) -> None:
        """Delete a file."""
        self.execute(f"delete {path}", lambda: print(f"Deleting {path}"))

    def copy(self, src: str, dest: str) -> None:
        """Copy a file."""
        self.execute(f"copy {src} to {dest}", lambda: print(f"Copying..."))
```

```bash
$ python files.py --dry-run delete --path test.txt
[DRY RUN] Would delete test.txt
```

## 11. Subcommand with Shared State

```python
from wArgs import wArgs

@wArgs
class Database:
    """Database management tool."""

    def __init__(self, connection: str = "sqlite:///data.db") -> None:
        self.connection = connection
        self._connected = False

    def _connect(self) -> None:
        if not self._connected:
            print(f"Connecting to {self.connection}...")
            self._connected = True

    def query(self, sql: str) -> None:
        """Execute a SQL query."""
        self._connect()
        print(f"Executing: {sql}")

    def migrate(self, version: str) -> None:
        """Run migrations."""
        self._connect()
        print(f"Migrating to version {version}")
```

## 12. Plugin-Style Commands

```python
from wArgs import wArgs

@wArgs
class CLI:
    """Extensible CLI with plugins."""

    def __init__(self) -> None:
        self.plugins: dict[str, callable] = {}

    def register(self, name: str, func: callable) -> None:
        """Register a plugin command."""
        self.plugins[name] = func

    def run_plugin(self, name: str, args: str = "") -> None:
        """Run a registered plugin.

        Args:
            name: Plugin name
            args: Arguments to pass
        """
        if name in self.plugins:
            self.plugins[name](args)
        else:
            print(f"Plugin not found: {name}")
            print(f"Available: {list(self.plugins.keys())}")
```

## 13. Batch Processing

```python
from pathlib import Path
from wArgs import wArgs

@wArgs
def batch(
    input_dir: Path,
    output_dir: Path,
    pattern: str = "*.txt",
    parallel: int = 1,
) -> None:
    """Process files in batch.

    Args:
        input_dir: Input directory
        output_dir: Output directory
        pattern: File pattern to match
        parallel: Number of parallel workers
    """
    files = list(input_dir.glob(pattern))
    print(f"Found {len(files)} files matching {pattern}")
    print(f"Processing with {parallel} workers...")

    for f in files:
        out = output_dir / f.name
        print(f"  {f} -> {out}")
```

```bash
$ python batch.py --input-dir ./data --output-dir ./out --pattern "*.csv" --parallel 4
```
