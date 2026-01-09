"""Introspection engine for wArgs.

This module extracts metadata from functions and classes for CLI generation.
"""

from wargs.introspection.docstrings import (
    DocstringFormat,
    DocstringInfo,
    detect_docstring_format,
    parse_docstring,
)
from wargs.introspection.mro import (
    get_inherited_function_info,
    get_init_parameters,
    merge_parameters,
    traverse_mro,
)
from wargs.introspection.signatures import extract_function_info, extract_parameters
from wargs.introspection.types import resolve_type

__all__ = [
    "DocstringFormat",
    "DocstringInfo",
    "detect_docstring_format",
    "extract_function_info",
    "extract_parameters",
    "get_inherited_function_info",
    "get_init_parameters",
    "merge_parameters",
    "parse_docstring",
    "resolve_type",
    "traverse_mro",
]
