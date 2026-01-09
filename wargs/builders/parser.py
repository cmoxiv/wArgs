"""Parser builder for wArgs.

Builds argparse.ArgumentParser from ParserConfig.
"""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any

from wargs.core.config import ArgumentConfig, ParserConfig

if TYPE_CHECKING:
    from argparse import ArgumentParser, _ArgumentGroup


class ParserBuilder:
    """Builds ArgumentParser instances from ParserConfig.

    Supports lazy construction and caching of parsers.

    Example:
        config = build_parser_config(func_info)
        builder = ParserBuilder(config)
        parser = builder.build()
        args = parser.parse_args()
    """

    def __init__(self, config: ParserConfig) -> None:
        """Initialize the parser builder.

        Args:
            config: The parser configuration.
        """
        self._config = config
        self._parser: ArgumentParser | None = None
        self._groups: dict[str, _ArgumentGroup] = {}
        self._exclusive_groups: dict[str, argparse._MutuallyExclusiveGroup] = {}

    @property
    def config(self) -> ParserConfig:
        """Get the parser configuration."""
        return self._config

    @property
    def parser(self) -> ArgumentParser:
        """Get or build the ArgumentParser (lazy construction)."""
        if self._parser is None:
            self._parser = self.build()
        return self._parser

    def build(self) -> ArgumentParser:
        """Build and return an ArgumentParser.

        Returns:
            Configured ArgumentParser instance.
        """
        # Create the parser
        parser = argparse.ArgumentParser(
            prog=self._config.prog,
            description=self._config.description,
            epilog=self._config.epilog,
            add_help=self._config.add_help,
            formatter_class=self._get_formatter_class(),
        )

        # Reset group caches
        self._groups = {}
        self._exclusive_groups = {}

        # Add arguments
        for arg_config in self._config.arguments:
            self._add_argument(parser, arg_config)

        # Add subcommands if any
        if self._config.subcommands:
            self._add_subcommands(parser)

        return parser

    def _get_formatter_class(self) -> type[argparse.HelpFormatter]:
        """Get the help formatter class.

        Returns:
            The formatter class to use.
        """
        if self._config.formatter_class:
            # Map string names to formatter classes
            formatters = {
                "RawDescriptionHelpFormatter": argparse.RawDescriptionHelpFormatter,
                "RawTextHelpFormatter": argparse.RawTextHelpFormatter,
                "ArgumentDefaultsHelpFormatter": argparse.ArgumentDefaultsHelpFormatter,
            }
            return formatters.get(
                self._config.formatter_class,
                argparse.HelpFormatter,
            )
        return argparse.HelpFormatter

    def _get_or_create_group(
        self,
        parser: ArgumentParser,
        group_name: str,
    ) -> _ArgumentGroup:
        """Get or create an argument group.

        Args:
            parser: The parser to add the group to.
            group_name: Name of the group.

        Returns:
            The argument group.
        """
        if group_name not in self._groups:
            self._groups[group_name] = parser.add_argument_group(group_name)
        return self._groups[group_name]

    def _get_or_create_exclusive_group(
        self,
        parser: ArgumentParser,
        group_name: str,
        *,
        required: bool = False,
    ) -> argparse._MutuallyExclusiveGroup:
        """Get or create a mutually exclusive group.

        Args:
            parser: The parser to add the group to.
            group_name: Name of the exclusive group.
            required: Whether one option must be provided.

        Returns:
            The mutually exclusive group.
        """
        if group_name not in self._exclusive_groups:
            self._exclusive_groups[group_name] = parser.add_mutually_exclusive_group(
                required=required
            )
        return self._exclusive_groups[group_name]

    def _add_argument(
        self,
        parser: ArgumentParser,
        config: ArgumentConfig,
    ) -> None:
        """Add a single argument to the parser.

        Args:
            parser: The parser or group to add to.
            config: The argument configuration.
        """
        # Skip if marked to skip
        if config.skip:
            return

        # Determine where to add the argument
        target: ArgumentParser | _ArgumentGroup | argparse._MutuallyExclusiveGroup = (
            parser
        )

        if config.mutually_exclusive:
            target = self._get_or_create_exclusive_group(
                parser,
                config.mutually_exclusive,
            )
        elif config.group:
            target = self._get_or_create_group(parser, config.group)

        # Build kwargs for add_argument
        kwargs = self._build_add_argument_kwargs(config)

        # Add the argument
        if config.positional:
            target.add_argument(config.name, **kwargs)
        else:
            target.add_argument(*config.flags, **kwargs)

    def _build_add_argument_kwargs(self, config: ArgumentConfig) -> dict[str, Any]:
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

    def _add_subcommands(self, parser: ArgumentParser) -> None:
        """Add subcommands to the parser.

        Args:
            parser: The parser to add subcommands to.
        """
        subparsers = parser.add_subparsers(dest="command")

        for name, subconfig in self._config.subcommands.items():
            subparser = subparsers.add_parser(
                name,
                help=subconfig.description,
                description=subconfig.description,
            )

            # Recursively add arguments to subparser
            sub_builder = ParserBuilder(subconfig)
            for arg_config in subconfig.arguments:
                sub_builder._add_argument(subparser, arg_config)


def build_parser(config: ParserConfig) -> ArgumentParser:
    """Convenience function to build a parser from config.

    Args:
        config: The parser configuration.

    Returns:
        Configured ArgumentParser.
    """
    return ParserBuilder(config).build()


__all__ = [
    "ParserBuilder",
    "build_parser",
]
