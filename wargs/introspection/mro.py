"""MRO (Method Resolution Order) traversal for parameter inheritance.

Collects parameters from parent classes' __init__ methods and merges
them with child class parameters.
"""

from __future__ import annotations

import warnings

from wArgs.core.config import FunctionInfo, ParameterInfo
from wArgs.introspection.docstrings import parse_docstring
from wArgs.introspection.signatures import extract_function_info
from wArgs.introspection.types import resolve_type


def get_init_parameters(cls: type) -> list[ParameterInfo]:
    """Extract __init__ parameters from a single class.

    Args:
        cls: The class to extract parameters from.

    Returns:
        List of ParameterInfo for __init__ parameters.
    """
    init_method = cls.__dict__.get("__init__")
    if init_method is None:
        return []

    # Extract function info
    func_info = extract_function_info(init_method)

    # Parse docstring for descriptions
    docstring_info = parse_docstring(func_info.description)

    # Resolve types and add descriptions
    for param in func_info.parameters:
        if param.annotation is not None:
            param.type_info = resolve_type(param.annotation)
        if param.description is None and param.name in docstring_info.params:
            param.description = docstring_info.params[param.name]

    return func_info.parameters


def _check_type_conflict(
    child_param: ParameterInfo,
    parent_param: ParameterInfo,
    child_cls: type,
    parent_cls: type,
) -> None:
    """Check for type conflicts between child and parent parameters.

    Warns if the types don't match.

    Args:
        child_param: The child class parameter.
        parent_param: The parent class parameter.
        child_cls: The child class.
        parent_cls: The parent class.
    """
    child_type = child_param.annotation
    parent_type = parent_param.annotation

    # If either is None, no conflict check needed
    if child_type is None or parent_type is None:
        return

    # Compare types
    if child_type != parent_type:
        warnings.warn(
            f"Parameter '{child_param.name}' in {child_cls.__name__} has type "
            f"{child_type} but parent {parent_cls.__name__} has type {parent_type}. "
            f"Using child type.",
            UserWarning,
            stacklevel=4,
        )


def merge_parameters(
    child_params: list[ParameterInfo],
    parent_params: list[ParameterInfo],
    child_cls: type,
    parent_cls: type,
    *,
    warn_on_conflict: bool = True,
) -> list[ParameterInfo]:
    """Merge child and parent parameters.

    Child parameters override parent parameters with the same name.
    Warns on type mismatches if warn_on_conflict is True.

    Args:
        child_params: Parameters from child class.
        parent_params: Parameters from parent class.
        child_cls: The child class (for warning messages).
        parent_cls: The parent class (for warning messages).
        warn_on_conflict: Whether to warn on type conflicts.

    Returns:
        Merged list of parameters (child overrides parent).
    """
    # Build lookup of child params by name
    child_by_name = {p.name: p for p in child_params}

    merged: list[ParameterInfo] = []
    seen_names: set[str] = set()

    # First, add all child parameters
    for param in child_params:
        merged.append(param)
        seen_names.add(param.name)

    # Then, add parent parameters that aren't overridden
    for param in parent_params:
        if param.name in seen_names:
            # Check for type conflict
            if warn_on_conflict and param.name in child_by_name:
                _check_type_conflict(
                    child_by_name[param.name],
                    param,
                    child_cls,
                    parent_cls,
                )
            continue

        merged.append(param)
        seen_names.add(param.name)

    return merged


def traverse_mro(
    cls: type,
    *,
    warn_on_conflict: bool = True,
) -> list[ParameterInfo]:
    """Traverse class MRO to collect all __init__ parameters.

    Walks the Method Resolution Order, collecting parameters from each
    class's __init__ method. Child parameters override parent parameters.

    Args:
        cls: The class to traverse.
        warn_on_conflict: Whether to warn on type conflicts.

    Returns:
        Merged list of all __init__ parameters.
    """
    # Get MRO, excluding object
    mro = [c for c in cls.__mro__ if c is not object]

    if not mro:
        return []

    # Start with the most derived class (first in MRO)
    result = get_init_parameters(mro[0])
    seen_classes = {mro[0]}

    # Merge in parameters from parent classes
    for parent_cls in mro[1:]:
        if parent_cls in seen_classes:
            continue
        seen_classes.add(parent_cls)

        parent_params = get_init_parameters(parent_cls)
        if parent_params:
            result = merge_parameters(
                result,
                parent_params,
                mro[0],  # Always compare against the original class
                parent_cls,
                warn_on_conflict=warn_on_conflict,
            )

    return result


def get_inherited_function_info(
    cls: type,
    *,
    warn_on_conflict: bool = True,
) -> FunctionInfo:
    """Get FunctionInfo with inherited parameters from MRO.

    Args:
        cls: The class to get info for.
        warn_on_conflict: Whether to warn on type conflicts.

    Returns:
        FunctionInfo with merged parameters from class hierarchy.
    """
    parameters = traverse_mro(cls, warn_on_conflict=warn_on_conflict)

    # Get class docstring
    import inspect

    doc = inspect.getdoc(cls)

    return FunctionInfo(
        name=cls.__name__,
        qualname=cls.__qualname__,
        description=doc,
        parameters=parameters,
        return_type=None,
        module=cls.__module__,
        source_file=None,
        line_number=None,
    )


__all__ = [
    "get_inherited_function_info",
    "get_init_parameters",
    "merge_parameters",
    "traverse_mro",
]
