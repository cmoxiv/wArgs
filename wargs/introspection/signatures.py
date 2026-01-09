"""Function signature analysis for wArgs.

Extracts parameter information from function signatures using the
inspect module.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, get_type_hints

from wArgs.core.config import (
    MISSING,
    FunctionInfo,
    ParameterInfo,
    ParameterKind,
)
from wArgs.core.exceptions import IntrospectionError


def _convert_parameter_kind(kind: inspect._ParameterKind) -> ParameterKind:
    """Convert inspect.Parameter kind to ParameterKind enum."""
    mapping = {
        inspect.Parameter.POSITIONAL_ONLY: ParameterKind.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD: ParameterKind.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.VAR_POSITIONAL: ParameterKind.VAR_POSITIONAL,
        inspect.Parameter.KEYWORD_ONLY: ParameterKind.KEYWORD_ONLY,
        inspect.Parameter.VAR_KEYWORD: ParameterKind.VAR_KEYWORD,
    }
    return mapping[kind]


def extract_parameters(
    func: Callable[..., Any],
    *,
    include_self: bool = False,
) -> list[ParameterInfo]:
    """Extract parameter information from a function.

    Args:
        func: The function to extract parameters from.
        include_self: Whether to include 'self' or 'cls' parameters.

    Returns:
        List of ParameterInfo objects for each parameter.

    Raises:
        IntrospectionError: If the function cannot be introspected.
    """
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError) as e:
        raise IntrospectionError(f"Cannot get signature for {func!r}: {e}") from e

    # Get type hints, handling forward references
    # Use include_extras=True to preserve Annotated metadata
    try:
        hints = get_type_hints(func, include_extras=True)
    except Exception:
        # Fall back to annotations if get_type_hints fails
        hints = getattr(func, "__annotations__", {})

    parameters: list[ParameterInfo] = []

    for name, param in sig.parameters.items():
        # Skip self/cls unless explicitly requested
        if not include_self and name in ("self", "cls"):
            continue

        # Get annotation from type hints (resolved) or signature
        annotation = hints.get(name, param.annotation)
        if annotation is inspect.Parameter.empty:
            annotation = None

        # Determine if there's a default value
        has_default = param.default is not inspect.Parameter.empty
        default = param.default if has_default else MISSING

        parameters.append(
            ParameterInfo(
                name=name,
                annotation=annotation,
                default=default,
                has_default=has_default,
                kind=_convert_parameter_kind(param.kind),
            )
        )

    return parameters


def extract_function_info(func: Callable[..., Any]) -> FunctionInfo:
    """Extract complete function information.

    Combines signature analysis with source location information.

    Args:
        func: The function to extract information from.

    Returns:
        FunctionInfo containing all extracted metadata.

    Raises:
        IntrospectionError: If the function cannot be introspected.
    """
    # Get basic function metadata
    name = getattr(func, "__name__", "<anonymous>")
    qualname = getattr(func, "__qualname__", name)
    module = getattr(func, "__module__", None)

    # Extract parameters
    parameters = extract_parameters(func)

    # Get return type
    try:
        hints = get_type_hints(func, include_extras=True)
        return_type = hints.get("return")
    except Exception:
        return_type = getattr(func, "__annotations__", {}).get("return")

    # Get source location
    source_file = None
    line_number = None
    try:
        source_file = inspect.getsourcefile(func)
        # Get the line number of the function definition
        _, line_number = inspect.getsourcelines(func)
    except (OSError, TypeError):
        # Source not available (e.g., built-in functions)
        pass

    # Get docstring (description will be parsed separately)
    doc = inspect.getdoc(func)

    return FunctionInfo(
        name=name,
        qualname=qualname,
        description=doc,
        parameters=parameters,
        return_type=return_type,
        module=module,
        source_file=source_file,
        line_number=line_number,
    )


__all__ = [
    "extract_function_info",
    "extract_parameters",
]
