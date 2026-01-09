"""Core completion generator for wArgs.

This module provides the foundation for generating shell completion scripts
from wargs-decorated functions and classes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from argparse import ArgumentParser

    from wArgs.core.config import ArgumentConfig, ParserConfig


@dataclass
class CompletionOption:
    """Represents an option for shell completion.

    Attributes:
        flags: List of option flags (e.g., ["-n", "--name"]).
        description: Help text for the option.
        takes_value: Whether the option takes a value.
        choices: List of valid choices (for Literal/Enum types).
        file_completion: Whether to complete with files.
        directory_completion: Whether to complete with directories.
    """

    flags: list[str]
    description: str = ""
    takes_value: bool = True
    choices: list[str] = field(default_factory=list)
    file_completion: bool = False
    directory_completion: bool = False


@dataclass
class CompletionSubcommand:
    """Represents a subcommand for shell completion.

    Attributes:
        name: The subcommand name.
        description: Help text for the subcommand.
        options: List of options for this subcommand.
    """

    name: str
    description: str = ""
    options: list[CompletionOption] = field(default_factory=list)


@dataclass
class CompletionSpec:
    """Complete specification for shell completion.

    Attributes:
        prog: Program name.
        description: Program description.
        global_options: Options available to all subcommands.
        subcommands: List of subcommands.
    """

    prog: str
    description: str = ""
    global_options: list[CompletionOption] = field(default_factory=list)
    subcommands: list[CompletionSubcommand] = field(default_factory=list)


def _extract_completion_option(arg_config: ArgumentConfig) -> CompletionOption:
    """Extract completion option from ArgumentConfig.

    Args:
        arg_config: The argument configuration.

    Returns:
        CompletionOption for the argument.
    """
    # Use flags if available, otherwise build from name
    if arg_config.flags:
        flags = list(arg_config.flags)
    elif arg_config.positional:
        flags = [arg_config.name]
    else:
        # Build long flag from name
        long_flag = f"--{arg_config.name.replace('_', '-')}"
        flags = [long_flag]

    # Determine if takes value
    takes_value = arg_config.action not in (
        "store_true",
        "store_false",
        "count",
        "store_const",
    )

    # Get choices
    choices: list[str] = []
    if arg_config.choices:
        choices = [str(c) for c in arg_config.choices]

    # Detect file/directory completion from type
    file_completion = False
    directory_completion = False
    if arg_config.type is not None:
        type_name = getattr(arg_config.type, "__name__", str(arg_config.type))
        if "Path" in type_name:
            file_completion = True

    return CompletionOption(
        flags=flags,
        description=arg_config.help or "",
        takes_value=takes_value,
        choices=choices,
        file_completion=file_completion,
        directory_completion=directory_completion,
    )


def extract_completion_spec(parser_config: ParserConfig) -> CompletionSpec:
    """Extract completion specification from ParserConfig.

    Args:
        parser_config: The parser configuration.

    Returns:
        CompletionSpec for shell completion generation.
    """
    # Extract global options
    global_options = [
        _extract_completion_option(arg) for arg in parser_config.arguments
    ]

    # Add help option (always present)
    global_options.append(
        CompletionOption(
            flags=["-h", "--help"],
            description="Show help message and exit",
            takes_value=False,
        )
    )

    # Extract subcommands
    subcommands = []
    for name, subconfig in parser_config.subcommands.items():
        sub_options = [_extract_completion_option(arg) for arg in subconfig.arguments]
        # Add help for subcommand
        sub_options.append(
            CompletionOption(
                flags=["-h", "--help"],
                description="Show help message and exit",
                takes_value=False,
            )
        )

        subcommands.append(
            CompletionSubcommand(
                name=name,
                description=subconfig.description or "",
                options=sub_options,
            )
        )

    return CompletionSpec(
        prog=parser_config.prog or "program",
        description=parser_config.description or "",
        global_options=global_options,
        subcommands=subcommands,
    )


def extract_completion_spec_from_parser(parser: ArgumentParser) -> CompletionSpec:
    """Extract completion specification from ArgumentParser.

    This is a fallback for when ParserConfig is not available.

    Args:
        parser: The ArgumentParser instance.

    Returns:
        CompletionSpec for shell completion generation.
    """
    global_options = []

    # Extract options from parser actions
    for action in parser._actions:
        if action.dest == "help":
            continue  # Skip help, we add it manually

        flags = list(action.option_strings) if action.option_strings else [action.dest]

        takes_value = action.nargs != 0 and not isinstance(
            action,
            (type(parser._actions[0]),),  # Skip special actions
        )
        if hasattr(action, "const") and action.const is not None:
            takes_value = False

        choices = [str(c) for c in action.choices] if action.choices else []

        global_options.append(
            CompletionOption(
                flags=flags,
                description=action.help or "",
                takes_value=takes_value,
                choices=choices,
            )
        )

    # Add help
    global_options.append(
        CompletionOption(
            flags=["-h", "--help"],
            description="Show help message and exit",
            takes_value=False,
        )
    )

    # Extract subcommands
    subcommands = []
    if hasattr(parser, "_subparsers") and parser._subparsers:
        for action in parser._subparsers._actions:
            if hasattr(action, "_parser_class") and hasattr(action, "choices"):
                choices_dict = getattr(action, "choices", None)
                if choices_dict is None or not hasattr(choices_dict, "items"):
                    continue
                for name, subparser in choices_dict.items():
                    sub_options = []
                    for sub_action in subparser._actions:
                        if sub_action.dest == "help":
                            continue
                        sub_flags = (
                            list(sub_action.option_strings)
                            if sub_action.option_strings
                            else [sub_action.dest]
                        )
                        sub_options.append(
                            CompletionOption(
                                flags=sub_flags,
                                description=sub_action.help or "",
                                takes_value=sub_action.nargs != 0,
                                choices=(
                                    [str(c) for c in sub_action.choices]
                                    if sub_action.choices
                                    else []
                                ),
                            )
                        )
                    sub_options.append(
                        CompletionOption(
                            flags=["-h", "--help"],
                            description="Show help message and exit",
                            takes_value=False,
                        )
                    )
                    subcommands.append(
                        CompletionSubcommand(
                            name=name,
                            description=subparser.description or "",
                            options=sub_options,
                        )
                    )

    return CompletionSpec(
        prog=parser.prog or "program",
        description=parser.description or "",
        global_options=global_options,
        subcommands=subcommands,
    )


def get_completion_spec(func_or_class: Any) -> CompletionSpec:
    """Get completion specification from a wargs-decorated function or class.

    Args:
        func_or_class: A wargs-decorated function or class.

    Returns:
        CompletionSpec for shell completion generation.

    Raises:
        ValueError: If the argument is not a wargs-decorated function or class.
    """
    # Check for wargs wrapper
    if hasattr(func_or_class, "_wargs_config") and func_or_class._wargs_config:
        return extract_completion_spec(func_or_class._wargs_config)

    # Fallback to parser extraction
    if hasattr(func_or_class, "parser"):
        return extract_completion_spec_from_parser(func_or_class.parser)

    raise ValueError(
        f"{func_or_class} is not a wargs-decorated function or class, "
        "or has no parser configuration available"
    )


def detect_shell() -> str:
    """Detect the current shell.

    Returns:
        Shell name: "bash", "zsh", "fish", or "unknown".
    """
    shell = os.environ.get("SHELL", "")

    if "zsh" in shell:
        return "zsh"
    elif "fish" in shell:
        return "fish"
    elif "bash" in shell:
        return "bash"

    # Try to detect from parent process
    parent_shell = os.environ.get("0", "")
    if "zsh" in parent_shell:
        return "zsh"
    elif "fish" in parent_shell:
        return "fish"
    elif "bash" in parent_shell:
        return "bash"

    return "bash"  # Default to bash


__all__ = [
    "CompletionOption",
    "CompletionSpec",
    "CompletionSubcommand",
    "detect_shell",
    "extract_completion_spec",
    "extract_completion_spec_from_parser",
    "get_completion_spec",
]
