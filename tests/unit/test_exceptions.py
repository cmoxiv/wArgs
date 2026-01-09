"""Unit tests for wArgs exception hierarchy."""

from __future__ import annotations

import pytest

from wArgs import (
    ConfigurationError,
    ConversionError,
    ErrorContext,
    IntrospectionError,
    WargsError,
)


class TestErrorContext:
    """Tests for ErrorContext dataclass."""

    def test_format_location_with_file_and_line(
        self, sample_error_context: ErrorContext
    ) -> None:
        """Test location formatting with full context."""
        assert sample_error_context.format_location() == "test_module.py:42"

    def test_format_location_with_file_only(self) -> None:
        """Test location formatting with only file."""
        context = ErrorContext(
            function_name="func",
            source_file="module.py",
        )
        assert context.format_location() == "module.py"

    def test_format_location_unknown(self, minimal_error_context: ErrorContext) -> None:
        """Test location formatting with no location info."""
        assert minimal_error_context.format_location() == "<unknown>"

    def test_format_context_full(self, sample_error_context: ErrorContext) -> None:
        """Test full context formatting."""
        formatted = sample_error_context.format_context()
        assert "Function: test_function" in formatted
        assert "Parameter: test_param" in formatted
        assert "Location: test_module.py:42" in formatted

    def test_format_context_minimal(self, minimal_error_context: ErrorContext) -> None:
        """Test context formatting with minimal info."""
        formatted = minimal_error_context.format_context()
        assert "Function: minimal_function" in formatted
        assert "Parameter:" not in formatted


class TestWargsError:
    """Tests for the base WargsError exception."""

    def test_inherits_from_exception(self) -> None:
        """Verify WargsError inherits from Exception."""
        assert issubclass(WargsError, Exception)

    def test_simple_message(self) -> None:
        """Test error with simple message."""
        error = WargsError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.context is None

    def test_message_with_context(self, sample_error_context: ErrorContext) -> None:
        """Test error message includes context."""
        error = WargsError("Something went wrong", context=sample_error_context)
        message = str(error)
        assert "Something went wrong" in message
        assert "test_function" in message
        assert "test_param" in message
        assert "test_module.py:42" in message

    def test_can_be_caught_as_exception(self) -> None:
        """Verify WargsError can be caught as Exception."""
        with pytest.raises(Exception, match="test"):
            raise WargsError("test")

    def test_can_be_caught_as_wargs_error(self) -> None:
        """Verify WargsError can be caught specifically."""
        with pytest.raises(WargsError):
            raise WargsError("test")


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_inherits_from_wargs_error(self) -> None:
        """Verify ConfigurationError inherits from WargsError."""
        assert issubclass(ConfigurationError, WargsError)

    def test_can_be_caught_as_wargs_error(self) -> None:
        """Verify ConfigurationError can be caught as WargsError."""
        with pytest.raises(WargsError):
            raise ConfigurationError("invalid config")

    def test_simple_message(self) -> None:
        """Test ConfigurationError with simple message."""
        error = ConfigurationError("Invalid option 'foo'")
        assert "Invalid option 'foo'" in str(error)

    def test_message_with_context(self, sample_error_context: ErrorContext) -> None:
        """Test ConfigurationError includes context in message."""
        error = ConfigurationError(
            "Invalid option 'foo'",
            context=sample_error_context,
        )
        message = str(error)
        assert "Invalid option 'foo'" in message
        assert "test_function" in message


class TestIntrospectionError:
    """Tests for IntrospectionError."""

    def test_inherits_from_wargs_error(self) -> None:
        """Verify IntrospectionError inherits from WargsError."""
        assert issubclass(IntrospectionError, WargsError)

    def test_can_be_caught_as_wargs_error(self) -> None:
        """Verify IntrospectionError can be caught as WargsError."""
        with pytest.raises(WargsError):
            raise IntrospectionError("cannot introspect")

    def test_simple_message(self) -> None:
        """Test IntrospectionError with simple message."""
        error = IntrospectionError("Missing type annotation")
        assert "Missing type annotation" in str(error)


class TestConversionError:
    """Tests for ConversionError."""

    def test_inherits_from_wargs_error(self) -> None:
        """Verify ConversionError inherits from WargsError."""
        assert issubclass(ConversionError, WargsError)

    def test_can_be_caught_as_wargs_error(self) -> None:
        """Verify ConversionError can be caught as WargsError."""
        with pytest.raises(WargsError):
            raise ConversionError("cannot convert")

    def test_simple_message(self) -> None:
        """Test ConversionError with simple message."""
        error = ConversionError("Cannot convert 'abc' to int")
        assert "Cannot convert 'abc' to int" in str(error)

    def test_stores_value_and_type(self) -> None:
        """Test ConversionError stores value and target type."""
        error = ConversionError(
            "Cannot convert 'abc' to int",
            value="abc",
            target_type=int,
        )
        assert error.value == "abc"
        assert error.target_type is int

    def test_value_and_type_optional(self) -> None:
        """Test ConversionError works without value and type."""
        error = ConversionError("Generic conversion error")
        assert error.value is None
        assert error.target_type is None

    def test_message_with_context(self, sample_error_context: ErrorContext) -> None:
        """Test ConversionError includes context."""
        error = ConversionError(
            "Cannot convert 'abc' to int",
            value="abc",
            target_type=int,
            context=sample_error_context,
        )
        message = str(error)
        assert "Cannot convert" in message
        assert "test_function" in message


class TestExceptionHierarchy:
    """Tests for the overall exception hierarchy."""

    def test_all_exceptions_inherit_from_wargs_error(self) -> None:
        """Verify all custom exceptions inherit from WargsError."""
        exceptions = [
            ConfigurationError,
            IntrospectionError,
            ConversionError,
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, WargsError), (
                f"{exc_class} should inherit from WargsError"
            )

    def test_catch_all_with_wargs_error(self) -> None:
        """Test that WargsError catches all wargs exceptions."""
        exceptions_to_raise = [
            ConfigurationError("config error"),
            IntrospectionError("introspection error"),
            ConversionError("conversion error"),
        ]

        for exc in exceptions_to_raise:
            with pytest.raises(WargsError):
                raise exc

    def test_exceptions_are_distinct(self) -> None:
        """Test that exception types are distinct."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("test")

        with pytest.raises(IntrospectionError):
            raise IntrospectionError("test")

        with pytest.raises(ConversionError):
            raise ConversionError("test")

        # ConfigurationError should not catch IntrospectionError
        with pytest.raises(IntrospectionError):
            try:
                raise IntrospectionError("test")
            except ConfigurationError:
                pytest.fail("ConfigurationError should not catch IntrospectionError")


class TestExceptionImports:
    """Tests for exception imports from package root."""

    def test_import_from_wargs(self) -> None:
        """Test exceptions can be imported from wargs package."""
        from wArgs import (
            ConfigurationError,
            ConversionError,
            ErrorContext,
            IntrospectionError,
            WargsError,
        )

        # Verify they're the correct classes
        assert WargsError.__name__ == "WargsError"
        assert ConfigurationError.__name__ == "ConfigurationError"
        assert IntrospectionError.__name__ == "IntrospectionError"
        assert ConversionError.__name__ == "ConversionError"
        assert ErrorContext.__name__ == "ErrorContext"

    def test_import_from_core(self) -> None:
        """Test exceptions can be imported from wArgs.core."""
        from wArgs.core import (
            WargsError,
        )

        assert WargsError.__name__ == "WargsError"

    def test_import_from_core_exceptions(self) -> None:
        """Test exceptions can be imported from wArgs.core.exceptions."""
        from wArgs.core.exceptions import (
            ErrorContext,
            WargsError,
        )

        assert WargsError.__name__ == "WargsError"
        assert ErrorContext.__name__ == "ErrorContext"
