"""Configuration dataclasses for wArgs introspection.

These dataclasses represent the internal representation of function
metadata extracted during introspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ParameterKind(Enum):
    """Kind of function parameter.

    Maps to inspect.Parameter kinds but simplified for CLI purposes.
    """

    POSITIONAL_ONLY = "positional_only"
    POSITIONAL_OR_KEYWORD = "positional_or_keyword"
    VAR_POSITIONAL = "var_positional"  # *args
    KEYWORD_ONLY = "keyword_only"
    VAR_KEYWORD = "var_keyword"  # **kwargs


@dataclass
class TypeInfo:
    """Information about a resolved type annotation.

    Attributes:
        origin: The origin type (e.g., list for list[str]).
        args: Type arguments (e.g., (str,) for list[str]).
        is_optional: Whether the type is Optional (allows None).
        is_literal: Whether the type is a Literal.
        literal_values: Values if this is a Literal type.
        is_enum: Whether the type is an Enum subclass.
        enum_class: The Enum class if is_enum is True.
        converter: Function to convert string to this type.
    """

    origin: type | None = None
    args: tuple[Any, ...] = field(default_factory=tuple)
    is_optional: bool = False
    is_literal: bool = False
    literal_values: tuple[Any, ...] = field(default_factory=tuple)
    is_enum: bool = False
    enum_class: type[Enum] | None = None
    converter: Callable[[str], Any] | None = None


@dataclass
class ParameterInfo:
    """Information about a function parameter.

    Extracted from function signature, type hints, and docstrings.

    Attributes:
        name: Parameter name.
        annotation: The raw type annotation (may be None).
        type_info: Resolved type information.
        default: Default value (MISSING if no default).
        has_default: Whether the parameter has a default value.
        kind: The parameter kind (positional, keyword, etc.).
        description: Help text from docstring.
    """

    name: str
    annotation: Any = None
    type_info: TypeInfo | None = None
    default: Any = None
    has_default: bool = False
    kind: ParameterKind = ParameterKind.POSITIONAL_OR_KEYWORD
    description: str | None = None


# Sentinel for missing default values
class _Missing:
    """Sentinel class for missing default values."""

    _instance: _Missing | None = None

    def __new__(cls) -> _Missing:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<MISSING>"

    def __bool__(self) -> bool:
        return False


MISSING = _Missing()


@dataclass
class FunctionInfo:
    """Information about a function or method.

    Contains all metadata extracted during introspection.

    Attributes:
        name: Function name.
        qualname: Qualified name (includes class name for methods).
        description: Function description from docstring.
        parameters: List of parameter information.
        return_type: Return type annotation.
        module: Module where the function is defined.
        source_file: Source file path.
        line_number: Line number in source file.
    """

    name: str
    qualname: str
    description: str | None = None
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: Any = None
    module: str | None = None
    source_file: str | None = None
    line_number: int | None = None


@dataclass
class ArgumentConfig:
    """Configuration for a single CLI argument.

    Represents the argparse configuration for one parameter.

    Attributes:
        name: The parameter name (used as dest).
        flags: List of flags (e.g., ['--name', '-n']).
        type: Type converter function.
        default: Default value.
        required: Whether the argument is required.
        help: Help text for the argument.
        choices: List of valid choices.
        action: argparse action (e.g., 'store_true').
        nargs: Number of arguments (e.g., '*', '+', '?', int).
        metavar: Placeholder in help text.
        dest: Destination attribute name.
        group: Argument group name.
        mutually_exclusive: Mutually exclusive group name.
        positional: Whether this is a positional argument.
        hidden: Whether to hide from help.
        skip: Whether to skip this argument entirely.
    """

    name: str
    flags: list[str] = field(default_factory=list)
    type: Callable[[str], Any] | None = None
    default: Any = None
    required: bool = False
    help: str | None = None
    choices: list[Any] | None = None
    action: str | None = None
    nargs: str | int | None = None
    metavar: str | None = None
    dest: str | None = None
    group: str | None = None
    mutually_exclusive: str | None = None
    positional: bool = False
    hidden: bool = False
    skip: bool = False


@dataclass
class ParserConfig:
    """Configuration for an ArgumentParser.

    Contains all the information needed to build an ArgumentParser.

    Attributes:
        prog: Program name.
        description: Parser description.
        epilog: Text to display after argument help.
        arguments: List of argument configurations.
        subcommands: Mapping of subcommand names to their ParserConfigs.
        add_help: Whether to add -h/--help option.
        formatter_class: Help formatter class name.
    """

    prog: str | None = None
    description: str | None = None
    epilog: str | None = None
    arguments: list[ArgumentConfig] = field(default_factory=list)
    subcommands: dict[str, ParserConfig] = field(default_factory=dict)
    add_help: bool = True
    formatter_class: str | None = None


__all__ = [
    "MISSING",
    "ArgumentConfig",
    "FunctionInfo",
    "ParameterInfo",
    "ParameterKind",
    "ParserConfig",
    "TypeInfo",
]
