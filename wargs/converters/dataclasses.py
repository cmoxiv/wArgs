"""Dataclass expansion support for wArgs.

This module provides functionality to expand dataclass parameters into
multiple CLI arguments with a prefix.

Example:
    @dataclass
    class Config:
        host: str = "localhost"
        port: int = 8080

    @wargs
    def server(config: Annotated[Config, Arg(expand=True)]):
        ...

    # Generates: --config-host, --config-port
"""

from __future__ import annotations

import dataclasses
from typing import Any, get_type_hints

from wargs.core.config import ParameterInfo, ParameterKind


def is_dataclass_type(annotation: Any) -> bool:
    """Check if an annotation is a dataclass type.

    Args:
        annotation: The type annotation to check.

    Returns:
        True if the annotation is a dataclass.
    """
    return dataclasses.is_dataclass(annotation) and isinstance(annotation, type)


def expand_dataclass(
    param_name: str,
    dataclass_type: type,
    *,
    prefix: str | None = None,
    separator: str = "-",
) -> list[ParameterInfo]:
    """Expand a dataclass into multiple ParameterInfo objects.

    Each field of the dataclass becomes a separate parameter with a
    prefixed name.

    Args:
        param_name: The original parameter name (used as prefix).
        dataclass_type: The dataclass type to expand.
        prefix: Optional custom prefix. Defaults to param_name.
        separator: Separator between prefix and field name.

    Returns:
        List of ParameterInfo objects for each dataclass field.

    Example:
        @dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080

        params = expand_dataclass("config", Config)
        # Returns parameters for --config-host and --config-port
    """
    if not is_dataclass_type(dataclass_type):
        raise TypeError(f"{dataclass_type} is not a dataclass")

    actual_prefix = prefix if prefix is not None else param_name
    parameters: list[ParameterInfo] = []

    # Get type hints for proper annotation resolution
    try:
        hints = get_type_hints(dataclass_type)
    except Exception:
        hints = {}

    for field in dataclasses.fields(dataclass_type):
        # Skip class variables and init=False fields
        if not field.init:
            continue

        # Build parameter name with prefix
        if actual_prefix:
            full_name = f"{actual_prefix}{separator}{field.name}"
        else:
            full_name = field.name

        # Determine if has default
        has_default = (
            field.default is not dataclasses.MISSING
            or field.default_factory is not dataclasses.MISSING
        )

        # Get default value
        if field.default is not dataclasses.MISSING:
            default = field.default
        elif field.default_factory is not dataclasses.MISSING:
            default = None  # We don't call factory, just mark as optional
        else:
            default = None

        # Get annotation from type hints or field
        annotation = hints.get(field.name, field.type)

        param = ParameterInfo(
            name=full_name,
            kind=ParameterKind.KEYWORD_ONLY,
            has_default=has_default,
            default=default,
            annotation=annotation,
            description=field.metadata.get("help") if field.metadata else None,
        )
        parameters.append(param)

    return parameters


def reconstruct_dataclass(
    dataclass_type: type,
    values: dict[str, Any],
    prefix: str,
    separator: str = "-",
) -> Any:
    """Reconstruct a dataclass instance from expanded argument values.

    Args:
        dataclass_type: The dataclass type to construct.
        values: Dictionary of argument name -> value.
        prefix: The prefix used when expanding.
        separator: The separator used when expanding.

    Returns:
        An instance of the dataclass.

    Example:
        values = {"config-host": "localhost", "config-port": 8080}
        config = reconstruct_dataclass(Config, values, "config")
        # Returns Config(host="localhost", port=8080)
    """
    if not is_dataclass_type(dataclass_type):
        raise TypeError(f"{dataclass_type} is not a dataclass")

    # Map from full argument names back to field names
    kwargs: dict[str, Any] = {}
    prefix_with_sep = f"{prefix}{separator}" if prefix else ""

    for field in dataclasses.fields(dataclass_type):
        if not field.init:
            continue

        full_name = f"{prefix_with_sep}{field.name}"

        if full_name in values and values[full_name] is not None:
            kwargs[field.name] = values[full_name]

    return dataclass_type(**kwargs)


__all__ = [
    "expand_dataclass",
    "is_dataclass_type",
    "reconstruct_dataclass",
]
