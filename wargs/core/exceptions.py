"""Exception hierarchy for wArgs.

All wArgs exceptions inherit from WargsError, making it easy to catch
all wArgs-related errors with a single except clause.

Exception Hierarchy:
    WargsError
    ├── ConfigurationError  - Invalid decorator configuration (raised at import)
    ├── IntrospectionError  - Error analyzing function/class (raised at import)
    └── ConversionError     - Error converting argument value (raised at runtime)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ErrorContext:
    """Context information for error messages.

    Provides source location and parameter context for debugging.
    """

    function_name: str
    parameter_name: str | None = None
    source_file: str | None = None
    line_number: int | None = None

    def format_location(self) -> str:
        """Format the source location for display."""
        if self.source_file and self.line_number:
            return f"{self.source_file}:{self.line_number}"
        elif self.source_file:
            return self.source_file
        return "<unknown>"

    def format_context(self) -> str:
        """Format the full context for display."""
        parts = [f"Function: {self.function_name}"]
        if self.parameter_name:
            parts.append(f"Parameter: {self.parameter_name}")
        parts.append(f"Location: {self.format_location()}")
        return "\n  ".join(parts)


class WargsError(Exception):
    """Base exception for all wArgs errors.

    All wArgs exceptions inherit from this class, making it easy to catch
    all wArgs-related errors:

        try:
            my_cli()
        except WargsError as e:
            print(f"CLI error: {e}")

    Attributes:
        message: The error message.
        context: Optional context about where the error occurred.
    """

    def __init__(
        self,
        message: str,
        context: ErrorContext | None = None,
    ) -> None:
        self.message = message
        self.context = context
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the complete error message with context."""
        if self.context is None:
            return self.message

        return f"{self.message}\n\n  {self.context.format_context()}"


class ConfigurationError(WargsError):
    """Error in decorator configuration.

    Raised at import time when the @wargs decorator is misconfigured.

    Examples:
        - Invalid decorator options
        - Conflicting argument configurations
        - Unsupported parameter patterns

    Example:
        @wargs(invalid_option=True)  # Raises ConfigurationError
        def my_func():
            pass
    """


class IntrospectionError(WargsError):
    """Error during function or class introspection.

    Raised at import time when wArgs cannot analyze a decorated
    function or class.

    Examples:
        - Unsupported type annotation
        - Missing type annotation on required parameter
        - Unparseable docstring format

    Example:
        @wargs
        def my_func(x):  # Missing type annotation
            pass
    """


class ConversionError(WargsError):
    """Error converting an argument value.

    Raised at runtime when a command-line argument cannot be
    converted to the expected type.

    Examples:
        - Invalid integer format
        - File path that doesn't exist
        - Custom converter failure

    Example:
        # CLI: my_script --count abc
        # Raises: ConversionError("Cannot convert 'abc' to int")
    """

    def __init__(
        self,
        message: str,
        value: str | None = None,
        target_type: type | None = None,
        context: ErrorContext | None = None,
    ) -> None:
        self.value = value
        self.target_type = target_type
        super().__init__(message, context)


__all__ = [
    "ConfigurationError",
    "ConversionError",
    "ErrorContext",
    "IntrospectionError",
    "WargsError",
]
