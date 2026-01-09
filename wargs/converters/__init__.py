"""Converter registry and built-in converters for wArgs.

This module provides:
- ConverterRegistry: Central registry for type converters
- converter: Decorator for registering converters
- Built-in converters for datetime, date, time, UUID, Decimal, Path, etc.
- Dataclass expansion support
"""

from wArgs.converters.builtin import (
    convert_complex,
    convert_date,
    convert_datetime,
    convert_decimal,
    convert_fraction,
    convert_path,
    convert_time,
    convert_uuid,
    register_builtin_converters,
)
from wArgs.converters.dataclasses import (
    expand_dataclass,
    is_dataclass_type,
    reconstruct_dataclass,
)
from wArgs.converters.registry import (
    Converter,
    ConverterRegistry,
    converter,
    get_default_registry,
)

__all__ = [
    "Converter",
    "ConverterRegistry",
    "convert_complex",
    "convert_date",
    "convert_datetime",
    "convert_decimal",
    "convert_fraction",
    "convert_path",
    "convert_time",
    "convert_uuid",
    "converter",
    "expand_dataclass",
    "get_default_registry",
    "is_dataclass_type",
    "reconstruct_dataclass",
    "register_builtin_converters",
]
