"""Unit tests for built-in type converters."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from uuid import UUID

import pytest

from wargs.converters.builtin import (
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
from wargs.converters.registry import ConverterRegistry
from wargs.core.exceptions import ConversionError


class TestDatetimeConverter:
    """Tests for datetime converter."""

    def test_iso_format_with_time(self) -> None:
        """Test ISO format with time."""
        result = convert_datetime("2024-01-15T10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_iso_format_with_microseconds(self) -> None:
        """Test ISO format with microseconds."""
        result = convert_datetime("2024-01-15T10:30:00.123456")
        assert result == datetime(2024, 1, 15, 10, 30, 0, 123456)

    def test_space_separated(self) -> None:
        """Test space-separated format."""
        result = convert_datetime("2024-01-15 10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_date_only(self) -> None:
        """Test date-only format."""
        result = convert_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15, 0, 0, 0)

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_datetime("not-a-date")
        assert "datetime" in str(exc_info.value).lower()


class TestDateConverter:
    """Tests for date converter."""

    def test_iso_format(self) -> None:
        """Test ISO format."""
        result = convert_date("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_slash_format(self) -> None:
        """Test slash-separated format."""
        result = convert_date("2024/01/15")
        assert result == date(2024, 1, 15)

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_date("not-a-date")
        assert "date" in str(exc_info.value).lower()


class TestTimeConverter:
    """Tests for time converter."""

    def test_full_format(self) -> None:
        """Test HH:MM:SS format."""
        result = convert_time("10:30:45")
        assert result == time(10, 30, 45)

    def test_short_format(self) -> None:
        """Test HH:MM format."""
        result = convert_time("10:30")
        assert result == time(10, 30)

    def test_with_microseconds(self) -> None:
        """Test format with microseconds."""
        result = convert_time("10:30:45.123456")
        assert result == time(10, 30, 45, 123456)

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_time("not-a-time")
        assert "time" in str(exc_info.value).lower()


class TestUUIDConverter:
    """Tests for UUID converter."""

    def test_standard_format(self) -> None:
        """Test standard UUID format."""
        result = convert_uuid("123e4567-e89b-12d3-a456-426614174000")
        assert result == UUID("123e4567-e89b-12d3-a456-426614174000")

    def test_uppercase(self) -> None:
        """Test uppercase UUID."""
        result = convert_uuid("123E4567-E89B-12D3-A456-426614174000")
        assert result == UUID("123e4567-e89b-12d3-a456-426614174000")

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_uuid("not-a-uuid")
        assert "uuid" in str(exc_info.value).lower()


class TestDecimalConverter:
    """Tests for Decimal converter."""

    def test_integer(self) -> None:
        """Test integer string."""
        result = convert_decimal("42")
        assert result == Decimal("42")

    def test_float(self) -> None:
        """Test float string."""
        result = convert_decimal("3.14159")
        assert result == Decimal("3.14159")

    def test_negative(self) -> None:
        """Test negative number."""
        result = convert_decimal("-123.45")
        assert result == Decimal("-123.45")

    def test_scientific(self) -> None:
        """Test scientific notation."""
        result = convert_decimal("1.5E10")
        assert result == Decimal("1.5E10")

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_decimal("not-a-number")
        assert "decimal" in str(exc_info.value).lower()


class TestPathConverter:
    """Tests for Path converter."""

    def test_unix_path(self) -> None:
        """Test Unix-style path."""
        result = convert_path("/home/user/file.txt")
        assert result == Path("/home/user/file.txt")

    def test_relative_path(self) -> None:
        """Test relative path."""
        result = convert_path("./file.txt")
        assert result == Path("./file.txt")


class TestComplexConverter:
    """Tests for complex number converter."""

    def test_standard_format(self) -> None:
        """Test standard complex format."""
        result = convert_complex("3+4j")
        assert result == complex(3, 4)

    def test_negative_imaginary(self) -> None:
        """Test negative imaginary part."""
        result = convert_complex("1-2j")
        assert result == complex(1, -2)

    def test_real_only(self) -> None:
        """Test real number only."""
        result = convert_complex("5")
        assert result == complex(5, 0)

    def test_imaginary_only(self) -> None:
        """Test imaginary only."""
        result = convert_complex("3j")
        assert result == complex(0, 3)

    def test_with_spaces(self) -> None:
        """Test with spaces (should be stripped)."""
        result = convert_complex("3 + 4j")
        assert result == complex(3, 4)

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_complex("not-complex")
        assert "complex" in str(exc_info.value).lower()


class TestFractionConverter:
    """Tests for Fraction converter."""

    def test_fraction_format(self) -> None:
        """Test fraction format."""
        result = convert_fraction("1/2")
        assert result == Fraction(1, 2)

    def test_decimal_format(self) -> None:
        """Test decimal format."""
        result = convert_fraction("0.5")
        assert result == Fraction(1, 2)

    def test_integer(self) -> None:
        """Test integer input."""
        result = convert_fraction("3")
        assert result == Fraction(3)

    def test_invalid_format(self) -> None:
        """Test invalid format raises ConversionError."""
        with pytest.raises(ConversionError) as exc_info:
            convert_fraction("not/valid/fraction")
        assert "fraction" in str(exc_info.value).lower()


class TestRegisterBuiltinConverters:
    """Tests for register_builtin_converters function."""

    def test_registers_all_converters(self) -> None:
        """Test that all built-in converters are registered."""
        registry = ConverterRegistry()
        register_builtin_converters(registry)

        assert registry.has(datetime)
        assert registry.has(date)
        assert registry.has(time)
        assert registry.has(UUID)
        assert registry.has(Decimal)
        assert registry.has(Path)
        assert registry.has(complex)
        assert registry.has(Fraction)

    def test_converters_work(self) -> None:
        """Test that registered converters work correctly."""
        registry = ConverterRegistry()
        register_builtin_converters(registry)

        dt_converter = registry.get(datetime)
        assert dt_converter is not None
        result = dt_converter("2024-01-15T10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)
