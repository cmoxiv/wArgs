"""Utility functions for wArgs debugging and testing.

This module provides functions to inspect and debug wArgs-decorated
functions and classes.

Example:
    from wargs import wArgs, explain, get_parser, get_config

    @wargs
    def greet(name: str, count: int = 1):
        '''Greet someone.'''
        pass

    # Print human-readable configuration
    print(explain(greet))

    # Get the ArgumentParser directly
    parser = get_parser(greet)

    # Get the internal configuration
    config = get_config(greet)
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from argparse import ArgumentParser

    from wArgs.core.config import ParserConfig
    from wArgs.decorator import WargsClassWrapper, WargsWrapper


# Environment variable for debug output
WARGS_DEBUG_VAR = "WARGS_DEBUG"


def is_debug_enabled() -> bool:
    """Check if WARGS_DEBUG environment variable is set.

    Returns:
        True if WARGS_DEBUG is set to a truthy value (1, true, yes, on).
    """
    value = os.environ.get(WARGS_DEBUG_VAR, "").lower()
    return value in ("1", "true", "yes", "on")


def debug_print(*args: Any, **kwargs: Any) -> None:
    """Print debug output if WARGS_DEBUG is enabled.

    Args:
        *args: Arguments to print.
        **kwargs: Keyword arguments for print.
    """
    if is_debug_enabled():
        print("[wargs]", *args, file=sys.stderr, **kwargs)


def _get_wrapper(
    func: Callable[..., Any] | WargsWrapper | WargsClassWrapper,
) -> WargsWrapper | WargsClassWrapper:
    """Get the WargsWrapper or WargsClassWrapper from a function.

    Args:
        func: A wargs-decorated function/class or wrapper instance.

    Returns:
        The wrapper instance.

    Raises:
        TypeError: If func is not a wargs-decorated function.
    """
    from wArgs.decorator import WargsClassWrapper, WargsWrapper

    if isinstance(func, (WargsWrapper, WargsClassWrapper)):
        return func

    raise TypeError(
        f"Expected a @wargs decorated function or class, got {type(func).__name__}. "
        "Make sure you're passing a function decorated with @wargs."
    )


def get_parser(
    func: Callable[..., Any] | WargsWrapper | WargsClassWrapper,
) -> ArgumentParser:
    """Get the ArgumentParser for a wargs-decorated function.

    This is useful for testing or extending the parser with additional
    arguments not derived from the function signature.

    Args:
        func: A wargs-decorated function or class.

    Returns:
        The ArgumentParser instance.

    Raises:
        TypeError: If func is not a wargs-decorated function.

    Example:
        @wargs
        def greet(name: str):
            pass

        parser = get_parser(greet)
        parser.add_argument("--extra", help="Extra option")
    """
    wrapper = _get_wrapper(func)
    return wrapper.parser


def get_config(
    func: Callable[..., Any] | WargsWrapper | WargsClassWrapper,
) -> ParserConfig:
    """Get the ParserConfig for a wargs-decorated function.

    This returns the internal configuration used to build the parser,
    useful for debugging or advanced customization.

    Args:
        func: A wargs-decorated function or class.

    Returns:
        The ParserConfig instance.

    Raises:
        TypeError: If func is not a wargs-decorated function.

    Example:
        @wargs
        def greet(name: str):
            pass

        config = get_config(greet)
        for arg in config.arguments:
            print(f"{arg.name}: {arg.flags}")
    """
    wrapper = _get_wrapper(func)

    # Ensure parser is built (which also builds config)
    _ = wrapper.parser

    # Access the internal config
    return wrapper._parser_config  # type: ignore[return-value]


def explain(
    func: Callable[..., Any] | WargsWrapper | WargsClassWrapper,
    *,
    verbose: bool = False,
) -> str:
    """Return a human-readable explanation of a wargs-decorated function.

    This is useful for debugging and understanding how wargs interprets
    your function signature and docstring.

    Args:
        func: A wargs-decorated function or class.
        verbose: If True, include additional details.

    Returns:
        Human-readable string describing the configuration.

    Raises:
        TypeError: If func is not a wargs-decorated function.

    Example:
        @wargs
        def greet(name: str, count: int = 1):
            '''Greet someone.

            Args:
                name: The person to greet.
                count: Number of greetings.
            '''
            pass

        print(explain(greet))
    """
    from wArgs.decorator import WargsClassWrapper

    wrapper = _get_wrapper(func)
    config = get_config(func)

    lines: list[str] = []

    # Header
    if isinstance(wrapper, WargsClassWrapper):
        lines.append(f"Class: {wrapper._cls.__name__}")
        lines.append("Type: Subcommand-based CLI")
    else:
        lines.append(f"Function: {wrapper._func.__name__}")
        lines.append("Type: Single-command CLI")

    # Program info
    if config.prog:
        lines.append(f"Program: {config.prog}")
    if config.description:
        lines.append(f"Description: {config.description}")

    lines.append("")

    # Arguments
    if config.arguments:
        lines.append("Arguments:")
        for arg in config.arguments:
            if arg.skip:
                continue

            # Build flag string
            if arg.positional:
                flag_str = arg.name
            else:
                flag_str = ", ".join(arg.flags) if arg.flags else f"--{arg.name}"

            # Build type string
            type_str = ""
            if arg.type:
                type_name = getattr(arg.type, "__name__", str(arg.type))
                type_str = f" ({type_name})"

            # Build required/default string
            req_str = ""
            if arg.required:
                req_str = " [required]"
            elif arg.default is not None:
                req_str = f" [default: {arg.default!r}]"

            # Build choices string
            choice_str = ""
            if arg.choices:
                choice_str = f" choices: {arg.choices}"

            lines.append(f"  {flag_str}{type_str}{req_str}{choice_str}")

            if verbose and arg.help:
                lines.append(f"    Help: {arg.help}")

    # Subcommands
    if config.subcommands:
        lines.append("")
        lines.append("Subcommands:")
        for name, subconfig in config.subcommands.items():
            desc = subconfig.description or ""
            if desc and len(desc) > 60:
                desc = desc[:57] + "..."
            lines.append(f"  {name}: {desc}")

            if verbose and subconfig.arguments:
                for arg in subconfig.arguments:
                    if arg.skip:
                        continue
                    flag_str = ", ".join(arg.flags) if arg.flags else arg.name
                    lines.append(f"    {flag_str}")

    return "\n".join(lines)


__all__ = [
    "WARGS_DEBUG_VAR",
    "debug_print",
    "explain",
    "get_config",
    "get_parser",
    "is_debug_enabled",
]
