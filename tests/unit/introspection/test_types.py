"""Unit tests for type annotation resolution."""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Literal, Optional, Set, Tuple, Union

import pytest

from wargs.introspection.types import resolve_type


class Color(Enum):
    """Test enum for type resolution tests."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class TestResolveBasicTypes:
    """Tests for resolving basic types."""

    def test_resolve_str(self) -> None:
        """Test resolving str type."""
        info = resolve_type(str)
        assert info.origin is str
        assert info.converter is str
        assert info.is_optional is False

    def test_resolve_int(self) -> None:
        """Test resolving int type."""
        info = resolve_type(int)
        assert info.origin is int
        assert info.converter is int

    def test_resolve_float(self) -> None:
        """Test resolving float type."""
        info = resolve_type(float)
        assert info.origin is float
        assert info.converter is float

    def test_resolve_bool(self) -> None:
        """Test resolving bool type."""
        info = resolve_type(bool)
        assert info.origin is bool
        assert info.converter is bool

    def test_resolve_path(self) -> None:
        """Test resolving Path type."""
        info = resolve_type(Path)
        assert info.origin is Path
        assert info.converter is Path

    def test_resolve_none(self) -> None:
        """Test resolving None annotation."""
        info = resolve_type(None)
        assert info.origin is None
        assert info.converter is None


class TestResolveOptionalTypes:
    """Tests for resolving Optional types."""

    def test_resolve_optional_str(self) -> None:
        """Test resolving Optional[str]."""
        info = resolve_type(Optional[str])
        assert info.is_optional is True
        assert info.origin is str
        assert info.converter is str

    def test_resolve_optional_int(self) -> None:
        """Test resolving Optional[int]."""
        info = resolve_type(Optional[int])
        assert info.is_optional is True
        assert info.origin is int

    def test_resolve_union_with_none(self) -> None:
        """Test resolving Union[str, None]."""
        info = resolve_type(Union[str, None])
        assert info.is_optional is True
        assert info.origin is str

    @pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="Pipe union syntax requires Python 3.10+",
    )
    def test_resolve_pipe_none_syntax(self) -> None:
        """Test resolving str | None syntax."""
        # This is equivalent to Optional[str]
        info = resolve_type(str | None)  # type: ignore[operator]
        assert info.is_optional is True
        assert info.origin is str


class TestResolveCollectionTypes:
    """Tests for resolving collection types."""

    def test_resolve_list_str(self) -> None:
        """Test resolving list[str]."""
        info = resolve_type(list[str])
        assert info.origin is list
        assert info.args == (str,)
        assert info.converter is str

    def test_resolve_list_int(self) -> None:
        """Test resolving list[int]."""
        info = resolve_type(list[int])
        assert info.origin is list
        assert info.converter is int

    def test_resolve_list_generic(self) -> None:
        """Test resolving List[str] (typing module)."""
        info = resolve_type(List[str])
        assert info.origin is list
        assert info.args == (str,)

    def test_resolve_bare_list(self) -> None:
        """Test resolving bare list type."""
        info = resolve_type(list)
        assert info.origin is list
        # Bare list has no element type, so no args
        assert info.converter is str  # defaults to str for bare collections

    def test_resolve_tuple(self) -> None:
        """Test resolving tuple[int, str]."""
        info = resolve_type(tuple[int, str])
        assert info.origin is tuple
        assert info.args == (int, str)

    def test_resolve_tuple_generic(self) -> None:
        """Test resolving Tuple[int, ...]."""
        info = resolve_type(Tuple[int, ...])
        assert info.origin is tuple

    def test_resolve_set(self) -> None:
        """Test resolving set[str]."""
        info = resolve_type(set[str])
        assert info.origin is set
        assert info.args == (str,)

    def test_resolve_set_generic(self) -> None:
        """Test resolving Set[int]."""
        info = resolve_type(Set[int])
        assert info.origin is set

    def test_resolve_frozenset(self) -> None:
        """Test resolving frozenset[str]."""
        info = resolve_type(frozenset[str])
        assert info.origin is frozenset

    def test_resolve_dict(self) -> None:
        """Test resolving dict[str, int]."""
        # dict is not in COLLECTION_TYPES but should still work
        info = resolve_type(dict[str, int])
        assert info.args == (str, int)

    def test_resolve_dict_generic(self) -> None:
        """Test resolving Dict[str, int]."""
        info = resolve_type(Dict[str, int])
        assert info.args == (str, int)


class TestResolveLiteralTypes:
    """Tests for resolving Literal types."""

    def test_resolve_literal_strings(self) -> None:
        """Test resolving Literal with string values."""
        info = resolve_type(Literal["a", "b", "c"])
        assert info.is_literal is True
        assert info.literal_values == ("a", "b", "c")
        assert info.origin is str

    def test_resolve_literal_ints(self) -> None:
        """Test resolving Literal with int values."""
        info = resolve_type(Literal[1, 2, 3])
        assert info.is_literal is True
        assert info.literal_values == (1, 2, 3)
        assert info.origin is int

    def test_resolve_literal_mixed(self) -> None:
        """Test resolving Literal with mixed types."""
        info = resolve_type(Literal["debug", "info", 1, 2])
        assert info.is_literal is True
        assert info.literal_values == ("debug", "info", 1, 2)


class TestResolveEnumTypes:
    """Tests for resolving Enum types."""

    def test_resolve_enum(self) -> None:
        """Test resolving Enum type."""
        info = resolve_type(Color)
        assert info.is_enum is True
        assert info.enum_class is Color
        assert info.origin is Color

    def test_enum_converter(self) -> None:
        """Test Enum converter function."""
        info = resolve_type(Color)
        assert info.converter is not None
        # The converter should accept enum member names
        assert info.converter("RED") == Color.RED
        assert info.converter("GREEN") == Color.GREEN

    def test_enum_converter_invalid(self) -> None:
        """Test Enum converter with invalid value."""
        info = resolve_type(Color)
        assert info.converter is not None
        with pytest.raises(KeyError):
            info.converter("INVALID")


class TestResolveUnionTypes:
    """Tests for resolving Union types."""

    def test_resolve_union_two_types(self) -> None:
        """Test resolving Union of two non-None types."""
        info = resolve_type(Union[str, int])
        # Union without None is not optional
        assert info.is_optional is False

    def test_resolve_union_with_none_multiple(self) -> None:
        """Test resolving Union with None and multiple types."""
        info = resolve_type(Union[str, int, None])
        assert info.is_optional is True

    @pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="Pipe union syntax requires Python 3.10+",
    )
    def test_resolve_pipe_union_multiple_with_none(self) -> None:
        """Test resolving str | int | None syntax."""
        info = resolve_type(str | int | None)  # type: ignore[operator]
        assert info.is_optional is True

    @pytest.mark.skipif(
        sys.version_info < (3, 10),
        reason="Pipe union syntax requires Python 3.10+",
    )
    def test_resolve_pipe_union_no_none(self) -> None:
        """Test resolving str | int syntax (no None)."""
        info = resolve_type(str | int)  # type: ignore[operator]
        assert info.is_optional is False


class TestResolveOptionalCollections:
    """Tests for resolving Optional collection types."""

    def test_optional_list(self) -> None:
        """Test resolving Optional[list[str]]."""
        info = resolve_type(Optional[list[str]])
        assert info.is_optional is True
        assert info.origin is list
        assert info.args == (str,)

    def test_optional_literal(self) -> None:
        """Test resolving Optional[Literal['a', 'b']]."""
        info = resolve_type(Optional[Literal["a", "b"]])
        assert info.is_optional is True
        assert info.is_literal is True
        assert info.literal_values == ("a", "b")


class TestResolveCustomTypes:
    """Tests for resolving custom class types."""

    def test_resolve_custom_class(self) -> None:
        """Test resolving a custom class type."""

        class MyClass:
            def __init__(self, value: str) -> None:
                self.value = value

        info = resolve_type(MyClass)
        assert info.origin is MyClass
        # Custom classes should use their constructor as converter
        assert info.converter is MyClass

    def test_resolve_path_subclass(self) -> None:
        """Test that Path works as a converter."""
        info = resolve_type(Path)
        assert info.converter is Path
        # Should be able to construct paths
        result = info.converter("/some/path")
        assert isinstance(result, Path)

    def test_resolve_none_type(self) -> None:
        """Test resolving type(None)."""
        info = resolve_type(type(None))
        assert info.converter is None

    def test_resolve_non_type_annotation(self) -> None:
        """Test resolving a non-type annotation (string)."""
        # A string annotation should not have a converter
        info = resolve_type("SomeForwardRef")
        assert info.origin is None


class TestResolveWithRegistry:
    """Tests for resolving types with a custom converter registry."""

    def test_resolve_with_registry_converter(self) -> None:
        """Test that registry converters take precedence."""
        from wargs.converters.registry import ConverterRegistry

        # Create a custom class
        class CustomType:
            def __init__(self, value: str) -> None:
                self.value = value

        # Create registry with custom converter
        registry = ConverterRegistry()

        def custom_converter(s: str) -> CustomType:
            return CustomType(s.upper())

        registry.register(CustomType, custom_converter)

        # Resolve with registry
        info = resolve_type(CustomType, registry=registry)
        assert info.converter is custom_converter

        # The converter should work
        result = info.converter("hello")
        assert isinstance(result, CustomType)
        assert result.value == "HELLO"

    def test_resolve_without_registry(self) -> None:
        """Test that custom class uses constructor without registry."""

        class CustomType:
            def __init__(self, value: str) -> None:
                self.value = value

        # Resolve without registry
        info = resolve_type(CustomType, registry=None)
        assert info.converter is CustomType

    def test_resolve_basic_type_not_overridden_by_registry(self) -> None:
        """Test that basic types are NOT overridden by the registry.

        Basic types (int, str, float, bool, Path) are handled specially
        and always use the built-in converters regardless of registry.
        """
        from wargs.converters.registry import ConverterRegistry

        registry = ConverterRegistry()

        def custom_int(s: str) -> int:
            return int(s) * 100

        registry.register(int, custom_int)

        # Basic types should NOT use registry converter - they use built-in
        info = resolve_type(int, registry=registry)
        assert info.converter is int  # Built-in, not custom
        assert info.converter("5") == 5  # Not 500

    def test_resolve_collection_element_with_registry(self) -> None:
        """Test that collection element types use registry converters."""
        from wargs.converters.registry import ConverterRegistry

        class Item:
            def __init__(self, value: str) -> None:
                self.value = value

        registry = ConverterRegistry()

        def item_converter(s: str) -> Item:
            return Item(s.lower())

        registry.register(Item, item_converter)

        # Resolve list[Item] with registry
        info = resolve_type(list[Item], registry=registry)
        assert info.origin is list
        assert info.converter is item_converter
