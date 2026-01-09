"""Subcommand builder for class-based CLIs.

Extracts subcommands from class methods and builds subparser configurations.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from wArgs.builders.arguments import build_parser_config
from wArgs.core.config import DictExpansion, FunctionInfo, ParserConfig
from wArgs.introspection.docstrings import parse_docstring
from wArgs.introspection.mro import get_inherited_function_info
from wArgs.introspection.signatures import extract_function_info
from wArgs.introspection.types import resolve_type


def is_public_method(name: str, method: Any) -> bool:
    """Check if a method should be exposed as a subcommand.

    Args:
        name: The method name.
        method: The method object.

    Returns:
        True if the method should be a subcommand.
    """
    # Skip private/dunder methods
    if name.startswith("_"):
        return False

    # Must be callable
    if not callable(method):
        return False

    # Must be a function/method, not a class or other callable
    return not (not inspect.isfunction(method) and not inspect.ismethod(method))


def extract_methods(cls: type) -> dict[str, Callable[..., Any]]:
    """Extract public methods from a class.

    Args:
        cls: The class to extract methods from.

    Returns:
        Dictionary mapping method names to method objects.
    """
    methods: dict[str, Callable[..., Any]] = {}

    for name in dir(cls):
        # Get attribute from class (not instance)
        try:
            attr = getattr(cls, name)
        except AttributeError:
            continue

        if is_public_method(name, attr):
            methods[name] = attr

    return methods


def extract_init_info(cls: type) -> FunctionInfo | None:
    """Extract FunctionInfo from class __init__ method.

    Args:
        cls: The class to extract __init__ from.

    Returns:
        FunctionInfo for __init__, or None if no custom __init__.
    """
    init_method = getattr(cls, "__init__", None)
    if init_method is None:
        return None

    # Check if it's the default object.__init__
    if init_method is object.__init__:
        return None

    # Extract info, excluding 'self'
    func_info = extract_function_info(init_method)

    # Parse docstring for descriptions
    docstring_info = parse_docstring(func_info.description)

    # Resolve types and add descriptions
    for param in func_info.parameters:
        if param.annotation is not None:
            param.type_info = resolve_type(param.annotation)
        if param.description is None and param.name in docstring_info.params:
            param.description = docstring_info.params[param.name]

    return func_info


def extract_method_info(method: Callable[..., Any]) -> FunctionInfo:
    """Extract FunctionInfo from a method.

    Args:
        method: The method to extract info from.

    Returns:
        FunctionInfo for the method.
    """
    func_info = extract_function_info(method)

    # Parse docstring for descriptions
    docstring_info = parse_docstring(func_info.description)

    # Resolve types and add descriptions
    for param in func_info.parameters:
        if param.annotation is not None:
            param.type_info = resolve_type(param.annotation)
        if param.description is None and param.name in docstring_info.params:
            param.description = docstring_info.params[param.name]

    return func_info


def build_subcommand_config(
    cls: type,
    *,
    prog: str | None = None,
    description: str | None = None,
    traverse_mro: bool = True,
    warn_on_conflict: bool = True,
) -> ParserConfig:
    """Build ParserConfig for a class with subcommands.

    Args:
        cls: The class to build config for.
        prog: Program name override.
        description: Description override.
        traverse_mro: Whether to collect __init__ params from parent classes.
        warn_on_conflict: Whether to warn when child/parent types conflict.

    Returns:
        ParserConfig with subcommands.
    """
    # Get class docstring for description
    class_doc = inspect.getdoc(cls)
    desc = description if description is not None else class_doc

    # Extract first sentence/paragraph for description
    if desc:
        first_para = desc.split("\n\n")[0]
        if ". " in first_para and len(first_para.split(". ")[0]) < 200:
            desc = first_para.split(". ")[0] + "."
        else:
            desc = first_para.strip()

    # Build main parser config
    dict_expansions: dict[str, DictExpansion] = {}
    config = ParserConfig(
        prog=prog,
        description=desc,
        arguments=[],
        subcommands={},
        dict_expansions=dict_expansions,
    )

    # Extract global options from __init__ (with optional MRO traversal)
    # Always use class name as prefix for init args
    if traverse_mro:
        # Use MRO traversal to get inherited parameters
        init_info = get_inherited_function_info(cls, warn_on_conflict=warn_on_conflict)
        if init_info.parameters:
            init_config = build_parser_config(init_info, prefix=cls.__name__)
            config.arguments = init_config.arguments
            config.dict_expansions.update(init_config.dict_expansions)
    else:
        # Only get __init__ from the class itself
        maybe_init_info = extract_init_info(cls)
        if maybe_init_info is not None:
            init_config = build_parser_config(maybe_init_info, prefix=cls.__name__)
            config.arguments = init_config.arguments
            config.dict_expansions.update(init_config.dict_expansions)

    # Extract methods as subcommands
    methods = extract_methods(cls)
    for method_name, method in methods.items():
        method_info = extract_method_info(method)
        method_config = build_parser_config(method_info)

        # Use method name (with underscores replaced by hyphens) as subcommand
        subcommand_name = method_name.replace("_", "-")
        config.subcommands[subcommand_name] = method_config

    return config


__all__ = [
    "build_subcommand_config",
    "extract_init_info",
    "extract_method_info",
    "extract_methods",
    "is_public_method",
]
