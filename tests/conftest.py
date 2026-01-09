"""Shared pytest fixtures for wArgs tests."""

from __future__ import annotations

import pytest

from wArgs.core.exceptions import ErrorContext


@pytest.fixture
def sample_error_context() -> ErrorContext:
    """Create a sample ErrorContext for testing."""
    return ErrorContext(
        function_name="test_function",
        parameter_name="test_param",
        source_file="test_module.py",
        line_number=42,
    )


@pytest.fixture
def minimal_error_context() -> ErrorContext:
    """Create a minimal ErrorContext with only required fields."""
    return ErrorContext(function_name="minimal_function")
