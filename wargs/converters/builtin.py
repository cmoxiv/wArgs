"""Built-in type converters for common Python types.

This module provides converters for:
- datetime, date, time (ISO 8601 format)
- UUID
- Decimal
- Path (already handled by argparse, but included for completeness)
- Complex numbers
- Fractions
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from uuid import UUID

from wArgs.converters.registry import ConverterRegistry, get_default_registry
from wArgs.core.exceptions import ConversionError


def convert_datetime(value: str) -> datetime:
    """Convert string to datetime.

    Supports ISO 8601 format and common variations.

    Args:
        value: String representation of datetime.

    Returns:
        Parsed datetime object.

    Raises:
        ConversionError: If the string cannot be parsed.

    Examples:
        - "2024-01-15T10:30:00"
        - "2024-01-15 10:30:00"
        - "2024-01-15"
    """
    # Try ISO format first
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    # Try fromisoformat as fallback (handles timezone-aware strings)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    raise ConversionError(
        f"Cannot convert '{value}' to datetime. "
        "Expected ISO 8601 format (e.g., '2024-01-15T10:30:00')."
    )


def convert_date(value: str) -> date:
    """Convert string to date.

    Args:
        value: String representation of date (YYYY-MM-DD).

    Returns:
        Parsed date object.

    Raises:
        ConversionError: If the string cannot be parsed.
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    # Try fromisoformat as fallback
    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    raise ConversionError(
        f"Cannot convert '{value}' to date. Expected format: YYYY-MM-DD."
    )


def convert_time(value: str) -> time:
    """Convert string to time.

    Args:
        value: String representation of time (HH:MM:SS or HH:MM).

    Returns:
        Parsed time object.

    Raises:
        ConversionError: If the string cannot be parsed.
    """
    formats = [
        "%H:%M:%S.%f",
        "%H:%M:%S",
        "%H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    # Try fromisoformat as fallback
    try:
        return time.fromisoformat(value)
    except ValueError:
        pass

    raise ConversionError(
        f"Cannot convert '{value}' to time. Expected format: HH:MM:SS or HH:MM."
    )


def convert_uuid(value: str) -> UUID:
    """Convert string to UUID.

    Args:
        value: String representation of UUID.

    Returns:
        Parsed UUID object.

    Raises:
        ConversionError: If the string is not a valid UUID.
    """
    try:
        return UUID(value)
    except ValueError as e:
        raise ConversionError(
            f"Cannot convert '{value}' to UUID. "
            "Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx."
        ) from e


def convert_decimal(value: str) -> Decimal:
    """Convert string to Decimal.

    Args:
        value: String representation of decimal number.

    Returns:
        Parsed Decimal object.

    Raises:
        ConversionError: If the string is not a valid decimal.
    """
    try:
        return Decimal(value)
    except InvalidOperation as e:
        raise ConversionError(
            f"Cannot convert '{value}' to Decimal. Expected a valid decimal number."
        ) from e


def convert_path(value: str) -> Path:
    """Convert string to Path.

    Note: argparse handles Path natively, but this is included
    for completeness and consistency.

    Args:
        value: String path.

    Returns:
        Path object.
    """
    return Path(value)


def convert_complex(value: str) -> complex:
    """Convert string to complex number.

    Args:
        value: String representation of complex number.

    Returns:
        Parsed complex number.

    Raises:
        ConversionError: If the string is not a valid complex number.

    Examples:
        - "3+4j"
        - "1.5-2.5j"
        - "5"  (real only)
        - "3j"  (imaginary only)
    """
    try:
        return complex(value.replace(" ", ""))
    except ValueError as e:
        raise ConversionError(
            f"Cannot convert '{value}' to complex. "
            "Expected format: a+bj (e.g., '3+4j')."
        ) from e


def convert_fraction(value: str) -> Fraction:
    """Convert string to Fraction.

    Args:
        value: String representation of fraction.

    Returns:
        Parsed Fraction object.

    Raises:
        ConversionError: If the string is not a valid fraction.

    Examples:
        - "1/2"
        - "3/4"
        - "0.5"
        - "2"
    """
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as e:
        raise ConversionError(
            f"Cannot convert '{value}' to Fraction. "
            "Expected format: numerator/denominator (e.g., '1/2')."
        ) from e


def register_builtin_converters(registry: ConverterRegistry | None = None) -> None:
    """Register all built-in converters on a registry.

    Args:
        registry: The registry to register on. If None, uses the default.
    """
    reg = registry if registry is not None else get_default_registry()

    reg.register(datetime, convert_datetime)
    reg.register(date, convert_date)
    reg.register(time, convert_time)
    reg.register(UUID, convert_uuid)
    reg.register(Decimal, convert_decimal)
    reg.register(Path, convert_path)
    reg.register(complex, convert_complex)
    reg.register(Fraction, convert_fraction)


__all__ = [
    "convert_complex",
    "convert_date",
    "convert_datetime",
    "convert_decimal",
    "convert_fraction",
    "convert_path",
    "convert_time",
    "convert_uuid",
    "register_builtin_converters",
]
