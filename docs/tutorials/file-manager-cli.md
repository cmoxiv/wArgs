# Building a File Manager CLI

Create a powerful file management CLI tool with wArgs for common file operations, search, and organization.

## Overview

Build a CLI that can:
- List and search files
- Copy, move, and delete files safely
- Find duplicates
- Organize files by type/date
- Calculate directory sizes
- Batch rename files

## Quick Start

```python
from wArgs import wArgs
from pathlib import Path
import shutil
import hashlib
from typing import Literal
from datetime import datetime

@wArgs
class FileManager:
    """File management CLI tool."""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        """Initialize file manager.

        Args:
            verbose: Show detailed output
            dry_run: Preview changes without executing
        """
        self.verbose = verbose
        self.dry_run = dry_run

    def ls(
        self,
        directory: Path = Path("."),
        recursive: bool = False,
        pattern: str = "*",
        show_size: bool = False,
    ):
        """List files in a directory.

        Args:
            directory: Directory to list
            recursive: Search recursively
            pattern: File pattern (e.g., "*.py")
            show_size: Show file sizes
        """
        if not directory.exists():
            print(f"Error: {directory} does not exist")
            return

        # Get files
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))

        # Sort by path
        files.sort()

        print(f"\nFound {len(files)} file(s) in {directory}\n")

        for file in files:
            if show_size and file.is_file():
                size = file.stat().st_size
                size_str = self._format_size(size)
                print(f"{size_str:>10}  {file.relative_to(directory)}")
            else:
                marker = "📁" if file.is_dir() else "📄"
                print(f"{marker} {file.relative_to(directory)}")

    def find(
        self,
        pattern: str,
        directory: Path = Path("."),
        case_sensitive: bool = False,
        file_type: Literal["all", "file", "dir"] = "all",
    ):
        """Find files by name pattern.

        Args:
            pattern: Search pattern (supports wildcards)
            directory: Directory to search in
            case_sensitive: Case-sensitive search
            file_type: Filter by type (all, file, dir)
        """
        if not case_sensitive:
            pattern = pattern.lower()

        matches = []
        for item in directory.rglob("*"):
            name = item.name if case_sensitive else item.name.lower()

            # Check pattern match
            if pattern in name or Path(name).match(pattern):
                # Filter by type
                if file_type == "file" and not item.is_file():
                    continue
                if file_type == "dir" and not item.is_dir():
                    continue

                matches.append(item)

        print(f"\nFound {len(matches)} match(es):\n")
        for match in sorted(matches):
            print(f"  {match}")

    def copy(self, source: Path, destination: Path):
        """Copy file or directory.

        Args:
            source: Source path
            destination: Destination path
        """
        if not source.exists():
            print(f"Error: {source} does not exist")
            return

        if self.dry_run:
            print(f"[DRY RUN] Would copy: {source} → {destination}")
            return

        if source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination, dirs_exist_ok=True)

        if self.verbose:
            print(f"✓ Copied: {source} → {destination}")

    def move(self, source: Path, destination: Path):
        """Move file or directory.

        Args:
            source: Source path
            destination: Destination path
        """
        if not source.exists():
            print(f"Error: {source} does not exist")
            return

        if self.dry_run:
            print(f"[DRY RUN] Would move: {source} → {destination}")
            return

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))

        if self.verbose:
            print(f"✓ Moved: {source} → {destination}")

    def delete(self, path: Path, confirm: bool = True):
        """Delete file or directory.

        Args:
            path: Path to delete
            confirm: Ask for confirmation
        """
        if not path.exists():
            print(f"Error: {path} does not exist")
            return

        if confirm and not self.dry_run:
            response = input(f"Delete {path}? [y/N]: ")
            if response.lower() != "y":
                print("Cancelled")
                return

        if self.dry_run:
            print(f"[DRY RUN] Would delete: {path}")
            return

        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)

        if self.verbose:
            print(f"✓ Deleted: {path}")

    def size(self, directory: Path = Path(".")):
        """Calculate directory size.

        Args:
            directory: Directory to analyze
        """
        if not directory.exists():
            print(f"Error: {directory} does not exist")
            return

        total_size = 0
        file_count = 0

        for file in directory.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1

        print(f"\nDirectory: {directory}")
        print(f"Files: {file_count:,}")
        print(f"Total size: {self._format_size(total_size)}")

    def duplicates(self, directory: Path = Path(".")):
        """Find duplicate files by content hash.

        Args:
            directory: Directory to scan
        """
        print("Scanning for duplicates...")

        hashes = {}
        for file in directory.rglob("*"):
            if file.is_file():
                file_hash = self._hash_file(file)

                if file_hash in hashes:
                    hashes[file_hash].append(file)
                else:
                    hashes[file_hash] = [file]

        # Find duplicates
        duplicates = {h: files for h, files in hashes.items() if len(files) > 1}

        if not duplicates:
            print("\n✓ No duplicates found")
            return

        print(f"\nFound {len(duplicates)} duplicate set(s):\n")

        for file_hash, files in duplicates.items():
            size = files[0].stat().st_size
            print(f"\nDuplicates ({self._format_size(size)}):")
            for file in files:
                print(f"  • {file}")

    def organize(
        self,
        directory: Path = Path("."),
        by: Literal["type", "date"] = "type",
    ):
        """Organize files into subdirectories.

        Args:
            directory: Directory to organize
            by: Organization method (type or date)
        """
        files = [f for f in directory.iterdir() if f.is_file()]

        print(f"Organizing {len(files)} files by {by}...")

        for file in files:
            if by == "type":
                # Organize by extension
                ext = file.suffix.lower() or "no_extension"
                target_dir = directory / ext.lstrip(".")
            else:
                # Organize by modification date (year/month)
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                target_dir = directory / f"{mtime.year}" / f"{mtime.month:02d}"

            if self.dry_run:
                print(f"[DRY RUN] Would move: {file.name} → {target_dir / file.name}")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                file.rename(target_dir / file.name)

                if self.verbose:
                    print(f"✓ Moved: {file.name} → {target_dir.name}/")

    def rename(
        self,
        directory: Path = Path("."),
        pattern: str = "*",
        replace: str = "",
        with_text: str = "",
    ):
        """Batch rename files.

        Args:
            directory: Directory containing files
            pattern: File pattern to match
            replace: Text to replace in filenames
            with_text: Replacement text
        """
        files = list(directory.glob(pattern))

        print(f"Renaming {len(files)} file(s)...\n")

        for file in files:
            new_name = file.name.replace(replace, with_text)

            if new_name == file.name:
                continue

            new_path = file.parent / new_name

            if self.dry_run:
                print(f"[DRY RUN] {file.name} → {new_name}")
            else:
                file.rename(new_path)
                if self.verbose:
                    print(f"✓ {file.name} → {new_name}")

    def _format_size(self, size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def _hash_file(self, path: Path) -> str:
        """Calculate MD5 hash of file."""
        hasher = hashlib.md5()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

if __name__ == "__main__":
    FileManager()
```

## CLI Help Output

```
$ python filemanager.py --help
usage: filemanager.py [-h] [--verbose] [--dry-run]
                      {copy,delete,duplicates,find,ls,move,organize,rename,size}
                      ...

File management CLI tool.

positional arguments:
  {copy,delete,duplicates,find,ls,move,organize,rename,size}
    copy                Copy file or directory.
    delete              Delete file or directory.
    duplicates          Find duplicate files by content hash.
    find                Find files by name pattern.
    ls                  List files in a directory.
    move                Move file or directory.
    organize            Organize files into subdirectories.
    rename              Batch rename files.
    size                Calculate directory size.

options:
  -h, --help            show this help message and exit
  --verbose             Show detailed output (default: False)
  --dry-run             Preview changes without executing (default: False)
```


## Usage Examples

### List files
```bash
# List current directory
python fm.py ls

# List with sizes
python fm.py ls --ls-show-size

# List recursively with pattern
python fm.py ls --ls-recursive --ls-pattern "*.py"
```

### Find files
```bash
# Find all Python files
python fm.py find --find-pattern "*.py"

# Case-sensitive search
python fm.py find --find-pattern "Test" --find-case-sensitive

# Find only directories
python fm.py find --find-pattern "lib" --find-file-type dir
```

### File operations
```bash
# Copy file (dry run first)
python fm.py --FileManager-dry-run copy --copy-source old.txt --copy-destination new.txt

# Move files
python fm.py --FileManager-verbose move --move-source temp/ --move-destination archive/

# Delete with confirmation
python fm.py delete --delete-path old_file.txt
```

### Analysis
```bash
# Calculate directory size
python fm.py size --size-directory /path/to/dir

# Find duplicates
python fm.py duplicates --duplicates-directory /path/to/dir
```

### Organization
```bash
# Organize by file type (dry run)
python fm.py --FileManager-dry-run organize --organize-by type

# Organize by date
python fm.py organize --organize-by date

# Batch rename
python fm.py rename --rename-pattern "*.txt" --rename-replace " " --rename-with-text "_"
```

## Advanced Features

Add these methods for more functionality:

### Search file contents
```python
def grep(self, pattern: str, directory: Path = Path("."), file_pattern: str = "*"):
    """Search file contents.

    Args:
        pattern: Text pattern to search for
        directory: Directory to search in
        file_pattern: File pattern filter
    """
    import re

    matches = []
    for file in directory.rglob(file_pattern):
        if file.is_file():
            try:
                content = file.read_text()
                if re.search(pattern, content):
                    matches.append(file)
            except (UnicodeDecodeError, PermissionError):
                continue

    print(f"\nFound pattern in {len(matches)} file(s):\n")
    for match in matches:
        print(f"  {match}")
```

### Create file archive
```python
def archive(self, source: Path, output: Path, format: Literal["zip", "tar", "tgz"] = "zip"):
    """Create archive of directory.

    Args:
        source: Source directory
        output: Output archive path
        format: Archive format
    """
    import tarfile
    import zipfile

    if format == "zip":
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in source.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(source.parent))
    else:
        mode = "w:gz" if format == "tgz" else "w"
        with tarfile.open(output, mode) as tf:
            tf.add(source, arcname=source.name)

    print(f"✓ Created archive: {output}")
```

## Complete Example

See [complete example](https://github.com/cmoxiv/wArgs/tree/main/examples/use-cases/filemanager) with:
- Progress bars for long operations
- File filtering by size/date
- Watch mode for monitoring changes
- Trash/recycle bin instead of permanent delete
- Undo functionality

## Related

- [[Building a System Monitor CLI]]
- [Official Examples](https://cmoxiv.github.io/wArgs/examples/)
