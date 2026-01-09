"""Command group decorator for wArgs.

Provides a Click-style group/command pattern as an alternative to class-based subcommands.

Example:
    from wargs import wargs

    @wargs.group()
    def cli(verbose: bool = False):
        '''My CLI application.

        Args:
            verbose: Enable verbose output
        '''
        pass

    @cli.command()
    def add(name: str):
        '''Add an item.

        Args:
            name: Item name
        '''
        print(f"Adding {name}")

    @cli.command()
    def remove(item_id: int):
        '''Remove an item.

        Args:
            item_id: Item ID
        '''
        print(f"Removing {item_id}")

    if __name__ == "__main__":
        cli()
"""

from __future__ import annotations

import argparse
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

from wargs.builders.arguments import build_parser_config
from wargs.builders.parser import build_parser
from wargs.core.config import ArgumentConfig, ParserConfig
from wargs.introspection.docstrings import parse_docstring
from wargs.introspection.signatures import extract_function_info
from wargs.introspection.types import resolve_type
from wargs.utilities import debug_print


def _build_add_argument_kwargs(config: ArgumentConfig) -> dict[str, Any]:
    """Build kwargs dict for add_argument.

    Args:
        config: The argument configuration.

    Returns:
        kwargs dict for add_argument.
    """
    kwargs: dict[str, Any] = {}

    # Type converter
    if config.type is not None:
        kwargs["type"] = config.type

    # Default value
    if config.default is not None:
        kwargs["default"] = config.default

    # Required (only for optional arguments)
    if not config.positional and config.required:
        kwargs["required"] = True

    # Help text
    if config.help:
        if config.hidden:
            kwargs["help"] = argparse.SUPPRESS
        else:
            kwargs["help"] = config.help
    elif config.hidden:
        kwargs["help"] = argparse.SUPPRESS

    # Choices
    if config.choices is not None:
        kwargs["choices"] = config.choices

    # Action
    if config.action:
        kwargs["action"] = config.action

    # nargs
    if config.nargs is not None:
        kwargs["nargs"] = config.nargs

    # metavar
    if config.metavar:
        kwargs["metavar"] = config.metavar

    # dest (only for optional arguments)
    if config.dest and not config.positional:
        kwargs["dest"] = config.dest

    return kwargs


@dataclass
class CommandInfo:
    """Information about a registered command.

    Attributes:
        name: Command name (derived from function name).
        func: The command function.
        description: Command description.
        config: Parser configuration for this command.
    """

    name: str
    func: Callable[..., Any]
    description: str = ""
    config: ParserConfig | None = None


class WargsGroup:
    """A command group that can have subcommands registered to it.

    Created via the @wargs.group() decorator.

    Attributes:
        func: The group function (defines shared options).
        commands: Dictionary of registered commands.
        subgroups: Dictionary of nested subgroups.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        *,
        prog: str | None = None,
        description: str | None = None,
        add_help: bool = True,
        formatter_class: str | None = None,
        completion: bool = False,
    ) -> None:
        """Initialize the group.

        Args:
            func: The group function.
            prog: Program name override.
            description: Description override.
            add_help: Whether to add -h/--help.
            formatter_class: Help formatter class name.
            completion: Whether to add --completion flag.
        """
        self._func = func
        self._prog = prog
        self._description = description
        self._add_help = add_help
        self._formatter_class = formatter_class
        self._completion = completion
        self._commands: dict[str, CommandInfo] = {}
        self._subgroups: dict[str, WargsGroup] = {}
        self._parser: ArgumentParser | None = None
        self._parser_config: ParserConfig | None = None
        self._group_config: ParserConfig | None = None

        # Copy function metadata
        wraps(func)(self)

    @property
    def func(self) -> Callable[..., Any]:
        """Get the group function."""
        return self._func

    @property
    def commands(self) -> dict[str, CommandInfo]:
        """Get registered commands."""
        return self._commands

    @property
    def subgroups(self) -> dict[str, WargsGroup]:
        """Get nested subgroups."""
        return self._subgroups

    @property
    def parser(self) -> ArgumentParser:
        """Get or build the ArgumentParser (lazy construction)."""
        if self._parser is None:
            self._build_parser()
        return self._parser  # type: ignore[return-value]

    @property
    def _wargs_config(self) -> ParserConfig | None:
        """Get the parser configuration (for debugging/testing)."""
        if self._parser_config is None:
            self._build_parser()
        return self._parser_config

    def command(
        self,
        name: str | None = None,
        *,
        help: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a command with this group.

        Args:
            name: Command name override (default: function name).
            help: Help text override.

        Returns:
            Decorator function.

        Example:
            @cli.command()
            def add(name: str):
                '''Add an item.'''
                print(f"Adding {name}")
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cmd_name = name or func.__name__.replace("_", "-")
            description = help or (func.__doc__ or "").split("\n")[0].strip()

            self._commands[cmd_name] = CommandInfo(
                name=cmd_name,
                func=func,
                description=description,
            )

            # Invalidate cached parser
            self._parser = None
            self._parser_config = None

            return func

        return decorator

    def group(
        self,
        name: str | None = None,
        *,
        help: str | None = None,
    ) -> Callable[[Callable[..., Any]], WargsGroup]:
        """Create a nested subgroup.

        Args:
            name: Subgroup name override (default: function name).
            help: Help text override.

        Returns:
            Decorator that creates a WargsGroup.

        Example:
            @cli.group()
            def db(verbose: bool = False):
                '''Database operations.'''
                pass

            @db.command()
            def migrate():
                '''Run migrations.'''
                pass
        """

        def decorator(func: Callable[..., Any]) -> WargsGroup:
            subgroup_name = name or func.__name__.replace("_", "-")
            description = help or (func.__doc__ or "").split("\n")[0].strip()

            subgroup = WargsGroup(
                func,
                prog=f"{self._prog or ''} {subgroup_name}".strip(),
                description=description,
                add_help=self._add_help,
                formatter_class=self._formatter_class,
            )

            self._subgroups[subgroup_name] = subgroup

            # Invalidate cached parser
            self._parser = None
            self._parser_config = None

            return subgroup

        return decorator

    def _build_group_config(self) -> ParserConfig:
        """Build parser config from the group function."""
        debug_print(f"Building group config for: {self._func.__name__}")

        # Extract function info for the group function
        func_info = extract_function_info(self._func)

        # Parse docstring
        docstring_info = parse_docstring(func_info.description)

        # Resolve types and add descriptions
        for param in func_info.parameters:
            if param.annotation is not None:
                param.type_info = resolve_type(param.annotation)
            if param.description is None and param.name in docstring_info.params:
                param.description = docstring_info.params[param.name]

        # Build config
        config = build_parser_config(
            func_info,
            prog=self._prog,
            description=self._description,
        )

        if self._formatter_class:
            config.formatter_class = self._formatter_class
        config.add_help = self._add_help

        return config

    def _build_command_config(self, cmd_info: CommandInfo) -> ParserConfig:
        """Build parser config for a command."""
        debug_print(f"Building command config for: {cmd_info.name}")

        func_info = extract_function_info(cmd_info.func)
        docstring_info = parse_docstring(func_info.description)

        for param in func_info.parameters:
            if param.annotation is not None:
                param.type_info = resolve_type(param.annotation)
            if param.description is None and param.name in docstring_info.params:
                param.description = docstring_info.params[param.name]

        config = build_parser_config(
            func_info,
            prog=f"{self._prog or ''} {cmd_info.name}".strip(),
            description=cmd_info.description,
        )

        cmd_info.config = config
        return config

    def _build_parser(self) -> None:
        """Build the parser with all commands as subparsers."""
        debug_print(f"Building parser for group: {self._func.__name__}")

        # Build group config (shared options)
        self._group_config = self._build_group_config()

        # Create main parser with group options
        self._parser = build_parser(self._group_config)

        # Add completion argument if enabled
        if self._completion:
            self._parser.add_argument(
                "--completion",
                choices=["bash", "zsh", "fish"],
                metavar="SHELL",
                help="Generate shell completion script and exit",
            )

        # Add subparsers for commands
        if self._commands or self._subgroups:
            subparsers = self._parser.add_subparsers(
                dest="command",
                title="commands",
                description="Available commands",
            )

            # Add commands
            for cmd_name, cmd_info in self._commands.items():
                cmd_config = self._build_command_config(cmd_info)
                subparser = subparsers.add_parser(
                    cmd_name,
                    help=cmd_info.description,
                    description=cmd_config.description,
                )

                # Add command arguments
                for arg_config in cmd_config.arguments:
                    kwargs = _build_add_argument_kwargs(arg_config)
                    if arg_config.positional:
                        subparser.add_argument(arg_config.name, **kwargs)
                    else:
                        flags = list(arg_config.flags) or [
                            f"--{arg_config.name.replace('_', '-')}"
                        ]
                        subparser.add_argument(*flags, **kwargs)

            # Add subgroups as nested commands
            for subgroup_name, subgroup in self._subgroups.items():
                # Force build subgroup parser
                _ = subgroup.parser
                subparsers.add_parser(
                    subgroup_name,
                    help=subgroup._description or "",
                    add_help=False,
                )

        # Create combined parser config for completion
        self._parser_config = ParserConfig(
            prog=self._group_config.prog,
            description=self._group_config.description,
            arguments=list(self._group_config.arguments),
            add_help=self._add_help,
        )

        # Add subcommand configs
        for cmd_name, cmd_info in self._commands.items():
            if cmd_info.config:
                self._parser_config.subcommands[cmd_name] = cmd_info.config

    def parse_args(self, args: list[str] | None = None) -> Any:
        """Parse command-line arguments.

        Args:
            args: Arguments to parse. Defaults to sys.argv[1:].

        Returns:
            Namespace with parsed arguments.
        """
        debug_print(f"Parsing args for group: {args}")
        result = self.parser.parse_args(args)
        debug_print(f"Parsed result: {result}")
        return result

    def _get_group_kwargs(self, namespace: Any) -> dict[str, Any]:
        """Extract group function kwargs from namespace."""
        kwargs: dict[str, Any] = {}

        if self._group_config is None:
            self._build_parser()

        assert self._group_config is not None

        for arg in self._group_config.arguments:
            value = getattr(namespace, arg.name, None)
            if value is not None:
                kwargs[arg.name] = value

        return kwargs

    def _get_command_kwargs(self, namespace: Any, cmd_name: str) -> dict[str, Any]:
        """Extract command kwargs from namespace."""
        kwargs: dict[str, Any] = {}

        cmd_info = self._commands.get(cmd_name)
        if cmd_info is None or cmd_info.config is None:
            return kwargs

        for arg in cmd_info.config.arguments:
            value = getattr(namespace, arg.name, None)
            if value is not None:
                kwargs[arg.name] = value

        return kwargs

    def run(self, args: list[str] | None = None) -> Any:
        """Parse arguments and run the appropriate command.

        Args:
            args: Arguments to parse. Defaults to sys.argv[1:].

        Returns:
            The return value of the command function.
        """
        # Handle completion before full parsing
        if self._completion:
            check_args = args if args is not None else sys.argv[1:]
            if "--completion" in check_args:
                idx = check_args.index("--completion")
                if idx + 1 < len(check_args):
                    shell = check_args[idx + 1]
                    if shell in ("bash", "zsh", "fish"):
                        from wargs.completion import generate_completion

                        print(generate_completion(self, shell=shell))
                        return None

        namespace = self.parse_args(args)

        # Run group function first (for shared setup)
        group_kwargs = self._get_group_kwargs(namespace)
        self._func(**group_kwargs)

        # Get the command
        command = getattr(namespace, "command", None)
        if command is None:
            # No command specified - print help
            self.parser.print_help()
            return None

        # Check for subgroup
        if command in self._subgroups:
            subgroup = self._subgroups[command]
            # Parse remaining args with subgroup
            remaining = args[args.index(command) + 1 :] if args else sys.argv[2:]
            return subgroup.run(remaining)

        # Run the command
        cmd_info = self._commands.get(command)
        if cmd_info is None:  # pragma: no cover
            self.parser.error(f"Unknown command: {command}")
            return None

        cmd_kwargs = self._get_command_kwargs(namespace, command)
        return cmd_info.func(**cmd_kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the group.

        If called with no arguments, parses CLI arguments.
        Otherwise, calls the group function directly.
        """
        if args or kwargs:
            return self._func(*args, **kwargs)

        return self.run()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<WargsGroup({self._func.__name__})>"


def group(
    *,
    prog: str | None = None,
    description: str | None = None,
    add_help: bool = True,
    formatter_class: str | None = None,
    completion: bool = False,
) -> Callable[[Callable[..., Any]], WargsGroup]:
    """Create a command group.

    Args:
        prog: Program name override.
        description: Description override.
        add_help: Whether to add -h/--help.
        formatter_class: Help formatter class name.
        completion: Whether to add --completion flag.

    Returns:
        Decorator that creates a WargsGroup.

    Example:
        from wargs import wargs

        @wargs.group()
        def cli(verbose: bool = False):
            '''My CLI.'''
            pass

        @cli.command()
        def hello(name: str):
            '''Say hello.'''
            print(f"Hello, {name}!")

        if __name__ == "__main__":
            cli()
    """

    def decorator(func: Callable[..., Any]) -> WargsGroup:
        return WargsGroup(
            func,
            prog=prog,
            description=description,
            add_help=add_help,
            formatter_class=formatter_class,
            completion=completion,
        )

    return decorator


__all__ = [
    "CommandInfo",
    "WargsGroup",
    "group",
]
