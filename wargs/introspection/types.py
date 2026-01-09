"""Type annotation resolution for wArgs.

Resolves type annotations into actionable type information for
argument parsing.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Union, get_args, get_origin

from wargs.core.config import TypeInfo

if TYPE_CHECKING:
    from wargs.converters.registry import ConverterRegistry

# Types that are natively supported by argparse
BASIC_TYPES: dict[type, Callable[[str], Any]] = {
    str: str,
    int: int,
    float: float,
    bool: bool,  # Special handling needed
    Path: Path,
}

# Collection types that need nargs handling
COLLECTION_TYPES: set[type] = {list, tuple, set, frozenset}


def _is_optional_type(annotation: Any) -> tuple[bool, Any]:
    """Check if a type is Optional[T] and extract T.

    Optional[T] is equivalent to Union[T, None].

    Args:
        annotation: The type annotation to check.

    Returns:
        Tuple of (is_optional, inner_type). inner_type is None if
        the annotation is just Optional without an inner type.
    """
    origin = get_origin(annotation)

    # Handle Union types (including Optional)
    # In Python 3.10+, `str | None` creates types.UnionType
    # get_origin returns types.UnionType for that
    if origin is Union:
        args = get_args(annotation)
        # Optional[T] is Union[T, None]
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1 and type(None) in args:
            return True, non_none_args[0]
        elif type(None) in args:
            # Union with None and multiple other types
            return True, Union[tuple(non_none_args)]

    # Python 3.10+ union syntax: str | None creates types.UnionType
    import types

    union_type = getattr(types, "UnionType", None)
    if union_type is not None and isinstance(annotation, union_type):
        args = get_args(annotation)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1 and type(None) in args:
            return True, non_none_args[0]
        elif type(None) in args:
            return True, Union[tuple(non_none_args)]

    return False, annotation


def _is_literal_type(annotation: Any) -> tuple[bool, tuple[Any, ...]]:
    """Check if a type is Literal and extract values.

    Args:
        annotation: The type annotation to check.

    Returns:
        Tuple of (is_literal, literal_values).
    """
    origin = get_origin(annotation)

    # Check for Literal
    if origin is Literal:
        return True, get_args(annotation)

    # Python 3.8+ has typing.Literal
    try:
        from typing import Literal as TypingLiteral

        if origin is TypingLiteral:
            return True, get_args(annotation)
    except ImportError:
        pass

    return False, ()


def _is_enum_type(annotation: Any) -> tuple[bool, type[Enum] | None]:
    """Check if a type is an Enum subclass.

    Args:
        annotation: The type annotation to check.

    Returns:
        Tuple of (is_enum, enum_class).
    """
    try:
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return True, annotation
    except TypeError:  # pragma: no cover
        # Can happen with some generic types
        pass

    return False, None


def _make_enum_converter(enum_class: type[Enum]) -> Callable[[str], Enum]:
    """Create a converter function for an Enum type.

    Args:
        enum_class: The Enum class to convert to.

    Returns:
        A function that converts string names to enum members.
    """

    def convert(s: str) -> Enum:
        return enum_class[s]

    return convert


def _get_collection_element_type(annotation: Any) -> Any:
    """Get the element type of a collection annotation.

    Args:
        annotation: A collection type annotation (e.g., list[str]).

    Returns:
        The element type, or None if not determinable.
    """
    args = get_args(annotation)
    if args:
        return args[0]
    return None  # pragma: no cover (only called when args exist)


def _get_converter(
    annotation: Any, registry: ConverterRegistry | None = None
) -> Callable[[str], Any] | None:
    """Get the appropriate converter function for a type.

    Args:
        annotation: The type annotation.
        registry: Optional converter registry to check for custom converters.

    Returns:
        A converter function, or None if no special conversion needed.
    """
    # Handle None and NoneType
    if annotation is None or annotation is type(None):
        return None

    # Check registry first for custom converters
    if registry is not None and isinstance(annotation, type):
        custom_converter = registry.get(annotation)
        if custom_converter is not None:
            return custom_converter

    # Check basic types
    if annotation in BASIC_TYPES:
        return BASIC_TYPES[annotation]

    # Check if it's a class with a string constructor
    if isinstance(annotation, type):
        # Most types that can be constructed from a string will work
        return annotation

    return None  # pragma: no cover (only reached for non-type annotations)


def resolve_type(
    annotation: Any, registry: ConverterRegistry | None = None
) -> TypeInfo:
    """Resolve a type annotation into TypeInfo.

    Handles complex types including:
    - Basic types (str, int, float, bool, Path)
    - Optional types (Optional[T], T | None)
    - Collection types (list, tuple, set)
    - Literal types (Literal["a", "b"])
    - Enum types
    - Union types
    - Nested types
    - Custom types with registered converters

    Args:
        annotation: The type annotation to resolve.
        registry: Optional converter registry for custom type converters.

    Returns:
        TypeInfo with resolved type information.
    """
    if annotation is None:
        return TypeInfo()

    # Check for Optional first
    is_optional, inner_type = _is_optional_type(annotation)
    if is_optional and inner_type is not annotation:
        # Recursively resolve the inner type
        inner_info = resolve_type(inner_type, registry)
        return TypeInfo(
            origin=inner_info.origin,
            args=inner_info.args,
            is_optional=True,
            is_literal=inner_info.is_literal,
            literal_values=inner_info.literal_values,
            is_enum=inner_info.is_enum,
            enum_class=inner_info.enum_class,
            converter=inner_info.converter,
        )

    # Check for Literal
    is_literal, literal_values = _is_literal_type(annotation)
    if is_literal:
        return TypeInfo(
            origin=type(literal_values[0]) if literal_values else str,
            is_literal=True,
            literal_values=literal_values,
            converter=type(literal_values[0]) if literal_values else str,
        )

    # Check for Enum
    is_enum, enum_class = _is_enum_type(annotation)
    if is_enum and enum_class is not None:
        return TypeInfo(
            origin=enum_class,
            is_enum=True,
            enum_class=enum_class,
            converter=_make_enum_converter(enum_class),
        )

    # Get origin for generic types
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle collection types
    if origin in COLLECTION_TYPES or annotation in COLLECTION_TYPES:
        actual_origin = origin if origin else annotation
        element_type = _get_collection_element_type(annotation) if args else str
        element_converter = _get_converter(element_type, registry)

        return TypeInfo(
            origin=actual_origin,
            args=args,
            converter=element_converter,
        )

    # Handle basic types
    if annotation in BASIC_TYPES:
        return TypeInfo(
            origin=annotation,
            converter=BASIC_TYPES[annotation],
        )

    # Handle other types - check registry first, then class constructor
    converter = _get_converter(annotation, registry)

    return TypeInfo(
        origin=annotation if isinstance(annotation, type) else origin,
        args=args,
        converter=converter,
    )


__all__ = [
    "resolve_type",
]
