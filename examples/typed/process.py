#!/usr/bin/env python3
"""Type-aware file processing CLI example.

Demonstrates:
- Path types
- List types
- Literal for choices
- Boolean flags

Usage:
    python process.py --input-file data.txt --output-dir ./out
    python process.py --input-file data.txt --format json --verbose
"""

from pathlib import Path
from typing import Literal

from wargs import wargs


@wargs
def process(
    input_file: Path,
    output_dir: Path = Path("output"),
    format: Literal["text", "json", "csv"] = "text",
    verbose: bool = False,
    compress: bool = False,
) -> None:
    """Process a file and save results.

    Args:
        input_file: Path to the input file.
        output_dir: Directory for output files.
        format: Output format.
        verbose: Enable verbose output.
        compress: Compress the output.
    """
    if verbose:
        print(f"Input: {input_file}")
        print(f"Output dir: {output_dir}")
        print(f"Format: {format}")
        print(f"Compress: {compress}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read input
    if input_file.exists():
        content = input_file.read_text()
        print(f"Read {len(content)} characters")
    else:
        print(f"File not found: {input_file}")
        return

    # Write output
    output_file = output_dir / f"output.{format}"
    if format == "json":
        import json

        output_file.write_text(json.dumps({"content": content}))
    elif format == "csv":
        output_file.write_text(f"content\n{content}")
    else:
        output_file.write_text(content)

    print(f"Written to: {output_file}")


if __name__ == "__main__":
    process()
