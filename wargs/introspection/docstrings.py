"""Docstring parsing for wArgs.

Supports Google, NumPy, and Sphinx docstring formats.
Auto-detects the format and extracts parameter descriptions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto


class DocstringFormat(Enum):
    """Supported docstring formats."""

    UNKNOWN = auto()
    GOOGLE = auto()
    NUMPY = auto()
    SPHINX = auto()


@dataclass
class DocstringInfo:
    """Parsed docstring information.

    Attributes:
        summary: The first line/paragraph of the docstring.
        description: Full description (may include summary).
        params: Mapping of parameter names to descriptions.
        returns: Description of return value.
        raises: Mapping of exception types to descriptions.
        format: Detected docstring format.
    """

    summary: str | None = None
    description: str | None = None
    params: dict[str, str] = field(default_factory=dict)
    returns: str | None = None
    raises: dict[str, str] = field(default_factory=dict)
    format: DocstringFormat = DocstringFormat.UNKNOWN


# Patterns for format detection
_GOOGLE_ARGS_PATTERN = re.compile(r"^\s*Args?:\s*$", re.MULTILINE)
_GOOGLE_RETURNS_PATTERN = re.compile(r"^\s*Returns?:\s*$", re.MULTILINE)
_GOOGLE_RAISES_PATTERN = re.compile(r"^\s*Raises?:\s*$", re.MULTILINE)

_NUMPY_PARAMS_PATTERN = re.compile(r"^\s*Parameters\s*$", re.MULTILINE)
_NUMPY_DASHES_PATTERN = re.compile(r"^\s*-{3,}\s*$", re.MULTILINE)

_SPHINX_PARAM_PATTERN = re.compile(r"^\s*:param\s+\w+:", re.MULTILINE)
_SPHINX_TYPE_PATTERN = re.compile(r"^\s*:type\s+\w+:", re.MULTILINE)
_SPHINX_RETURNS_PATTERN = re.compile(r"^\s*:returns?:", re.MULTILINE)
_SPHINX_RAISES_PATTERN = re.compile(r"^\s*:raises?\s+\w+:", re.MULTILINE)


def detect_docstring_format(docstring: str | None) -> DocstringFormat:
    """Detect the format of a docstring.

    Args:
        docstring: The docstring to analyze.

    Returns:
        The detected DocstringFormat.
    """
    if not docstring:
        return DocstringFormat.UNKNOWN

    # Check for Sphinx-style first (most specific)
    if (
        _SPHINX_PARAM_PATTERN.search(docstring)
        or _SPHINX_TYPE_PATTERN.search(docstring)
        or _SPHINX_RETURNS_PATTERN.search(docstring)
        or _SPHINX_RAISES_PATTERN.search(docstring)
    ):
        return DocstringFormat.SPHINX

    # Check for NumPy-style (has Parameters with dashes)
    if _NUMPY_PARAMS_PATTERN.search(docstring) and _NUMPY_DASHES_PATTERN.search(
        docstring
    ):
        return DocstringFormat.NUMPY

    # Check for Google-style
    if (
        _GOOGLE_ARGS_PATTERN.search(docstring)
        or _GOOGLE_RETURNS_PATTERN.search(docstring)
        or _GOOGLE_RAISES_PATTERN.search(docstring)
    ):
        return DocstringFormat.GOOGLE

    return DocstringFormat.UNKNOWN


def _parse_google_docstring(docstring: str) -> DocstringInfo:
    """Parse a Google-style docstring.

    Google style example:
        '''Summary line.

        Longer description.

        Args:
            param1: Description of param1.
            param2: Description of param2.
                Continuation of description.

        Returns:
            Description of return value.

        Raises:
            ValueError: When something is wrong.
        '''
    """
    info = DocstringInfo(format=DocstringFormat.GOOGLE)
    lines = docstring.split("\n")

    # Extract summary (first non-empty line)
    for line in lines:
        stripped = line.strip()
        if stripped:
            info.summary = stripped
            break

    # Find section boundaries
    sections: dict[str, tuple[int, int]] = {}
    current_section = "description"
    section_start = 0

    section_headers = {
        "args": re.compile(r"^\s*Args?:\s*$"),
        "returns": re.compile(r"^\s*Returns?:\s*$"),
        "raises": re.compile(r"^\s*Raises?:\s*$"),
        "yields": re.compile(r"^\s*Yields?:\s*$"),
        "examples": re.compile(r"^\s*Examples?:\s*$"),
        "attributes": re.compile(r"^\s*Attributes?:\s*$"),
        "note": re.compile(r"^\s*Notes?:\s*$"),
    }

    for i, line in enumerate(lines):
        for section_name, pattern in section_headers.items():
            if pattern.match(line):
                if current_section:
                    sections[current_section] = (section_start, i)
                current_section = section_name
                section_start = i + 1
                break

    # Close the last section
    if current_section:
        sections[current_section] = (section_start, len(lines))

    # Extract description (before Args section)
    if "description" in sections:
        start, end = sections["description"]
        desc_lines = lines[start:end]
        # Stop at first section header
        desc_text = "\n".join(desc_lines).strip()
        if desc_text:
            info.description = desc_text

    # Parse Args section
    if "args" in sections:
        start, end = sections["args"]
        info.params = _parse_google_params(lines[start:end])

    # Parse Returns section
    if "returns" in sections:
        start, end = sections["returns"]
        returns_text = "\n".join(lines[start:end]).strip()
        info.returns = returns_text if returns_text else None

    # Parse Raises section
    if "raises" in sections:
        start, end = sections["raises"]
        info.raises = _parse_google_params(lines[start:end])

    return info


def _parse_google_params(lines: list[str]) -> dict[str, str]:
    """Parse parameter/raises entries from Google-style docstring lines.

    Format: param_name: Description that may
                continue on next line.
    """
    params: dict[str, str] = {}
    current_param: str | None = None
    current_desc: list[str] = []
    base_indent: int | None = None

    # Pattern for "name: description" or "name (type): description"
    # Allow any amount of leading whitespace
    param_pattern = re.compile(r"^(\s*)(\w+)(?:\s*\([^)]+\))?\s*:\s*(.*)$")

    for line in lines:
        if not line.strip():
            continue

        param_match = param_pattern.match(line)
        if param_match:
            indent = len(param_match.group(1))

            # First param defines the base indentation
            if base_indent is None:
                base_indent = indent

            # Only match if at base indent level (not a continuation)
            if indent == base_indent:
                # Save previous parameter
                if current_param is not None:
                    params[current_param] = " ".join(current_desc).strip()

                current_param = param_match.group(2)
                desc = param_match.group(3).strip()
                current_desc = [desc] if desc else []
                continue

        # Check for continuation (more indented than base)
        if current_param is not None and base_indent is not None:
            line_indent = len(line) - len(line.lstrip())
            if line_indent > base_indent:
                current_desc.append(line.strip())

    # Save last parameter
    if current_param is not None:
        params[current_param] = " ".join(current_desc).strip()

    return params


def _parse_numpy_docstring(docstring: str) -> DocstringInfo:
    """Parse a NumPy-style docstring.

    NumPy style example:
        '''Summary line.

        Longer description.

        Parameters
        ----------
        param1 : type
            Description of param1.
        param2 : type
            Description of param2.

        Returns
        -------
        type
            Description of return value.
        '''
    """
    info = DocstringInfo(format=DocstringFormat.NUMPY)
    lines = docstring.split("\n")

    # Extract summary
    for line in lines:
        stripped = line.strip()
        if stripped:
            info.summary = stripped
            break

    # Find sections (marked by underlines)
    sections: dict[str, tuple[int, int]] = {}
    i = 0
    current_section: str | None = None
    section_start = 0

    while i < len(lines):
        line = lines[i].strip()

        # Check if next line is a dashes line (section header)
        if i + 1 < len(lines) and re.match(r"^-{3,}$", lines[i + 1].strip()):
            # This line is a section header
            if current_section:
                sections[current_section] = (section_start, i)
            current_section = line.lower()
            section_start = i + 2  # Skip header and dashes
            i += 2
            continue

        i += 1

    # Close last section
    if current_section:
        sections[current_section] = (section_start, len(lines))

    # Parse Parameters section
    if "parameters" in sections:
        start, end = sections["parameters"]
        info.params = _parse_numpy_params(lines[start:end])

    # Parse Returns section
    if "returns" in sections:
        start, end = sections["returns"]
        returns_lines = [line.strip() for line in lines[start:end] if line.strip()]
        if returns_lines:
            # Skip the type line, get description
            info.returns = (
                " ".join(returns_lines[1:])
                if len(returns_lines) > 1
                else returns_lines[0]
            )

    # Parse Raises section
    if "raises" in sections:
        start, end = sections["raises"]
        info.raises = _parse_numpy_params(lines[start:end])

    return info


def _parse_numpy_params(lines: list[str]) -> dict[str, str]:
    """Parse parameter entries from NumPy-style docstring lines.

    Format:
        param_name : type
            Description of parameter.
    """
    params: dict[str, str] = {}
    current_param: str | None = None
    current_desc: list[str] = []
    base_indent: int | None = None

    # Pattern for "name : type" or just "name"
    param_pattern = re.compile(r"^(\w+)\s*(?::\s*.*)?$")

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if not stripped:
            continue

        # Detect base indentation from first non-empty line
        if base_indent is None:
            base_indent = indent

        # Check if this is a parameter line (at base indent level)
        if indent == base_indent:
            param_match = param_pattern.match(stripped)
            if param_match:
                # Save previous parameter
                if current_param is not None:
                    params[current_param] = " ".join(current_desc).strip()

                current_param = param_match.group(1)
                current_desc = []
        elif current_param is not None and indent > base_indent:
            # This is a description line
            current_desc.append(stripped)

    # Save last parameter
    if current_param is not None:
        params[current_param] = " ".join(current_desc).strip()

    return params


def _parse_sphinx_docstring(docstring: str) -> DocstringInfo:
    """Parse a Sphinx-style docstring.

    Sphinx style example:
        '''Summary line.

        Longer description.

        :param param1: Description of param1.
        :type param1: type
        :param param2: Description of param2.
        :returns: Description of return value.
        :raises ValueError: When something is wrong.
        '''
    """
    info = DocstringInfo(format=DocstringFormat.SPHINX)
    lines = docstring.split("\n")

    # Extract summary
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith(":"):
            info.summary = stripped
            break

    # Extract description (everything before first :param, :returns, etc.)
    desc_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(":"):
            break
        desc_lines.append(line)

    desc_text = "\n".join(desc_lines).strip()
    if desc_text:
        info.description = desc_text

    # Parse :param directives
    param_pattern = re.compile(r":param\s+(\w+):\s*(.+)")
    returns_pattern = re.compile(r":returns?:\s*(.+)")
    raises_pattern = re.compile(r":raises?\s+(\w+):\s*(.+)")

    full_text = docstring

    # Find all :param entries
    for match in param_pattern.finditer(full_text):
        param_name = match.group(1)
        description = match.group(2).strip()
        info.params[param_name] = description

    # Find :returns
    returns_match = returns_pattern.search(full_text)
    if returns_match:
        info.returns = returns_match.group(1).strip()

    # Find :raises entries
    for match in raises_pattern.finditer(full_text):
        exc_name = match.group(1)
        description = match.group(2).strip()
        info.raises[exc_name] = description

    return info


def parse_docstring(docstring: str | None) -> DocstringInfo:
    """Parse a docstring and extract structured information.

    Auto-detects the docstring format and delegates to the appropriate
    parser.

    Args:
        docstring: The docstring to parse.

    Returns:
        DocstringInfo containing extracted information.
    """
    if not docstring:
        return DocstringInfo()

    format_type = detect_docstring_format(docstring)

    if format_type == DocstringFormat.GOOGLE:
        return _parse_google_docstring(docstring)
    elif format_type == DocstringFormat.NUMPY:
        return _parse_numpy_docstring(docstring)
    elif format_type == DocstringFormat.SPHINX:
        return _parse_sphinx_docstring(docstring)
    else:
        # For unknown format, just extract summary
        info = DocstringInfo(format=DocstringFormat.UNKNOWN)
        lines = docstring.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped:
                info.summary = stripped
                info.description = docstring.strip()
                break
        return info


__all__ = [
    "DocstringFormat",
    "DocstringInfo",
    "detect_docstring_format",
    "parse_docstring",
]
