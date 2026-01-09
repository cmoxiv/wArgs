"""Unit tests for function signature analysis."""

from __future__ import annotations

from pathlib import Path

import pytest

from wArgs.core.config import MISSING, ParameterKind
from wArgs.core.exceptions import IntrospectionError
from wArgs.introspection.signatures import extract_function_info, extract_parameters


class TestExtractParameters:
    """Tests for extract_parameters function."""

    def test_extract_no_parameters(self) -> None:
        """Test function with no parameters."""

        def func() -> None:
            pass

        params = extract_parameters(func)
        assert params == []

    def test_extract_single_parameter(self) -> None:
        """Test function with single parameter."""

        def func(name: str) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 1
        assert params[0].name == "name"
        assert params[0].annotation is str
        assert params[0].has_default is False
        assert params[0].default is MISSING

    def test_extract_multiple_parameters(self) -> None:
        """Test function with multiple parameters."""

        def func(a: int, b: str, c: float) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 3
        assert [p.name for p in params] == ["a", "b", "c"]
        assert [p.annotation for p in params] == [int, str, float]

    def test_extract_with_defaults(self) -> None:
        """Test parameters with default values."""

        def func(required: str, optional: int = 42) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 2

        assert params[0].name == "required"
        assert params[0].has_default is False
        assert params[0].default is MISSING

        assert params[1].name == "optional"
        assert params[1].has_default is True
        assert params[1].default == 42

    def test_extract_with_none_default(self) -> None:
        """Test parameter with None as default."""

        def func(value: str | None = None) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 1
        assert params[0].name == "value"
        assert params[0].has_default is True
        assert params[0].default is None

    def test_extract_without_annotations(self) -> None:
        """Test parameters without type annotations."""

        def func(a, b=10):
            pass

        params = extract_parameters(func)
        assert len(params) == 2
        assert params[0].annotation is None
        assert params[1].annotation is None

    def test_skip_self_parameter(self) -> None:
        """Test that self is skipped by default."""

        class MyClass:
            def method(self, value: str) -> None:
                pass

        params = extract_parameters(MyClass.method)
        assert len(params) == 1
        assert params[0].name == "value"

    def test_skip_cls_parameter(self) -> None:
        """Test that cls is skipped by default."""

        class MyClass:
            @classmethod
            def method(cls, value: str) -> None:
                pass

        params = extract_parameters(MyClass.method)
        assert len(params) == 1
        assert params[0].name == "value"

    def test_include_self_parameter(self) -> None:
        """Test including self when requested."""

        class MyClass:
            def method(self, value: str) -> None:
                pass

        params = extract_parameters(MyClass.method, include_self=True)
        assert len(params) == 2
        assert params[0].name == "self"
        assert params[1].name == "value"

    def test_var_positional_parameter(self) -> None:
        """Test *args parameter."""

        def func(*args: str) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 1
        assert params[0].name == "args"
        assert params[0].kind == ParameterKind.VAR_POSITIONAL

    def test_var_keyword_parameter(self) -> None:
        """Test **kwargs parameter."""

        def func(**kwargs: str) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 1
        assert params[0].name == "kwargs"
        assert params[0].kind == ParameterKind.VAR_KEYWORD

    def test_keyword_only_parameters(self) -> None:
        """Test keyword-only parameters (after *)."""

        def func(pos: int, *, kwonly: str) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 2
        assert params[0].kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert params[1].kind == ParameterKind.KEYWORD_ONLY

    def test_complex_type_annotations(self) -> None:
        """Test complex type annotations are preserved."""

        def func(paths: list[Path], mapping: dict[str, int]) -> None:
            pass

        params = extract_parameters(func)
        assert len(params) == 2
        # Annotations should be the actual types
        assert params[0].annotation == list[Path]
        assert params[1].annotation == dict[str, int]


class TestExtractFunctionInfo:
    """Tests for extract_function_info function."""

    def test_extract_basic_info(self) -> None:
        """Test extraction of basic function information."""

        def greet(name: str) -> str:
            """Greet someone."""
            return f"Hello, {name}"

        info = extract_function_info(greet)

        assert info.name == "greet"
        assert (
            info.qualname
            == "TestExtractFunctionInfo.test_extract_basic_info.<locals>.greet"
        )
        assert info.description == "Greet someone."
        assert len(info.parameters) == 1
        assert info.return_type is str

    def test_extract_multiline_docstring(self) -> None:
        """Test extraction with multiline docstring."""

        def process(data: str) -> None:
            """Process some data.

            This function does important processing
            on the input data.

            Args:
                data: The data to process.
            """

        info = extract_function_info(process)
        assert "Process some data" in (info.description or "")

    def test_extract_no_docstring(self) -> None:
        """Test extraction without docstring."""

        def nodoc(x: int) -> int:
            return x * 2

        info = extract_function_info(nodoc)
        assert info.description is None

    def test_extract_no_return_type(self) -> None:
        """Test extraction without return type annotation."""

        def func(x: int):
            return x

        info = extract_function_info(func)
        assert info.return_type is None

    def test_extract_source_location(self) -> None:
        """Test that source location is extracted."""

        def local_func() -> None:
            pass

        info = extract_function_info(local_func)
        assert info.source_file is not None
        assert info.source_file.endswith(".py")
        assert info.line_number is not None
        assert info.line_number > 0

    def test_extract_module(self) -> None:
        """Test module information extraction."""

        def func() -> None:
            pass

        info = extract_function_info(func)
        assert info.module is not None

    def test_lambda_function(self) -> None:
        """Test extraction from lambda function."""
        func = lambda x: x * 2  # noqa: E731

        info = extract_function_info(func)
        assert info.name == "<lambda>"

    def test_method_qualname(self) -> None:
        """Test qualified name for methods."""

        class Calculator:
            def add(self, a: int, b: int) -> int:
                """Add two numbers."""
                return a + b

        info = extract_function_info(Calculator.add)
        assert "Calculator" in info.qualname
        assert "add" in info.qualname


class TestIntrospectionErrors:
    """Tests for error handling in introspection."""

    def test_non_callable_raises_error(self) -> None:
        """Test handling of non-callable objects."""

        # A class instance without __call__ can't be introspected as a function
        class NotCallable:
            pass

        obj = NotCallable()
        with pytest.raises(IntrospectionError, match="Cannot get signature"):
            extract_parameters(obj)  # type: ignore[arg-type]

    def test_extract_function_info_non_callable(self) -> None:
        """Test extract_function_info with non-callable."""

        class NotCallable:
            pass

        obj = NotCallable()
        with pytest.raises(IntrospectionError):
            extract_function_info(obj)  # type: ignore[arg-type]
