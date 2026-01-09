"""Unit tests for parser builder."""

from __future__ import annotations

import argparse

from wargs.builders.parser import ParserBuilder, build_parser
from wargs.core.config import ArgumentConfig, ParserConfig


class TestParserBuilder:
    """Tests for ParserBuilder class."""

    def test_build_simple_parser(self) -> None:
        """Test building a simple parser."""
        config = ParserConfig(
            prog="myapp",
            description="My application.",
            arguments=[
                ArgumentConfig(
                    name="name",
                    flags=["--name", "-n"],
                    type=str,
                    required=True,
                    help="The name to use.",
                ),
            ],
        )

        builder = ParserBuilder(config)
        parser = builder.build()

        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "myapp"

    def test_parser_caching(self) -> None:
        """Test that parser property caches the parser."""
        config = ParserConfig(prog="myapp")
        builder = ParserBuilder(config)

        parser1 = builder.parser
        parser2 = builder.parser

        assert parser1 is parser2

    def test_build_returns_new_parser(self) -> None:
        """Test that build() returns a new parser each time."""
        config = ParserConfig(prog="myapp")
        builder = ParserBuilder(config)

        parser1 = builder.build()
        parser2 = builder.build()

        assert parser1 is not parser2

    def test_required_argument(self) -> None:
        """Test parsing required argument."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="name",
                    flags=["--name"],
                    type=str,
                    required=True,
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["--name", "Alice"])

        assert args.name == "Alice"

    def test_optional_argument_with_default(self) -> None:
        """Test parsing optional argument with default."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="count",
                    flags=["--count"],
                    type=int,
                    default=10,
                    required=False,
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args([])

        assert args.count == 10

    def test_boolean_store_true(self) -> None:
        """Test parsing boolean with store_true action."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="verbose",
                    flags=["--verbose", "-v"],
                    action="store_true",
                ),
            ],
        )

        parser = build_parser(config)

        args_with = parser.parse_args(["--verbose"])
        assert args_with.verbose is True

        args_without = parser.parse_args([])
        assert args_without.verbose is False

    def test_choices(self) -> None:
        """Test parsing argument with choices."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="format",
                    flags=["--format"],
                    choices=["json", "xml", "csv"],
                    default="json",
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["--format", "xml"])

        assert args.format == "xml"

    def test_nargs_multiple(self) -> None:
        """Test parsing argument with nargs='*'."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="files",
                    flags=["--files"],
                    type=str,
                    nargs="*",
                    default=[],
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["--files", "a.txt", "b.txt", "c.txt"])

        assert args.files == ["a.txt", "b.txt", "c.txt"]

    def test_positional_argument(self) -> None:
        """Test parsing positional argument."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="filename",
                    positional=True,
                    type=str,
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["input.txt"])

        assert args.filename == "input.txt"

    def test_hidden_argument(self) -> None:
        """Test that hidden argument has suppressed help."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="debug",
                    flags=["--debug"],
                    action="store_true",
                    hidden=True,
                ),
            ],
        )

        parser = build_parser(config)
        # Hidden arguments should still work
        args = parser.parse_args(["--debug"])

        assert args.debug is True

    def test_dest_override(self) -> None:
        """Test argument with custom dest."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="output",
                    flags=["--out"],
                    type=str,
                    dest="output_file",
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["--out", "result.txt"])

        assert args.output_file == "result.txt"

    def test_metavar(self) -> None:
        """Test argument with custom metavar."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="config",
                    flags=["--config"],
                    type=str,
                    metavar="FILE",
                ),
            ],
        )

        parser = build_parser(config)
        # Just verify it builds without error
        assert parser is not None


class TestArgumentGroups:
    """Tests for argument groups."""

    def test_argument_group(self) -> None:
        """Test arguments in a group."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="input",
                    flags=["--input"],
                    type=str,
                    group="Input/Output",
                ),
                ArgumentConfig(
                    name="output",
                    flags=["--output"],
                    type=str,
                    group="Input/Output",
                ),
                ArgumentConfig(
                    name="verbose",
                    flags=["--verbose"],
                    action="store_true",
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["--input", "in.txt", "--output", "out.txt"])

        assert args.input == "in.txt"
        assert args.output == "out.txt"

    def test_mutually_exclusive_group(self) -> None:
        """Test mutually exclusive arguments."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="json",
                    flags=["--json"],
                    action="store_true",
                    mutually_exclusive="format",
                ),
                ArgumentConfig(
                    name="xml",
                    flags=["--xml"],
                    action="store_true",
                    mutually_exclusive="format",
                ),
            ],
        )

        parser = build_parser(config)

        # Should work with one option
        args = parser.parse_args(["--json"])
        assert args.json is True
        assert args.xml is False


class TestSubcommands:
    """Tests for subcommand support."""

    def test_simple_subcommands(self) -> None:
        """Test parser with subcommands."""
        config = ParserConfig(
            prog="myapp",
            subcommands={
                "add": ParserConfig(
                    description="Add an item",
                    arguments=[
                        ArgumentConfig(
                            name="name",
                            flags=["--name"],
                            type=str,
                            required=True,
                        ),
                    ],
                ),
                "remove": ParserConfig(
                    description="Remove an item",
                    arguments=[
                        ArgumentConfig(
                            name="id",
                            flags=["--id"],
                            type=int,
                            required=True,
                        ),
                    ],
                ),
            },
        )

        parser = build_parser(config)

        args = parser.parse_args(["add", "--name", "item1"])
        assert args.command == "add"
        assert args.name == "item1"


class TestParserBuilderAdvanced:
    """Additional tests for ParserBuilder edge cases."""

    def test_config_property(self) -> None:
        """Test that config property returns the configuration."""
        config = ParserConfig(prog="myapp", description="Test app")
        builder = ParserBuilder(config)

        assert builder.config is config
        assert builder.config.prog == "myapp"

    def test_formatter_class_raw_description(self) -> None:
        """Test RawDescriptionHelpFormatter."""
        config = ParserConfig(
            prog="myapp",
            formatter_class="RawDescriptionHelpFormatter",
        )

        builder = ParserBuilder(config)
        parser = builder.build()

        assert parser.formatter_class is argparse.RawDescriptionHelpFormatter

    def test_formatter_class_raw_text(self) -> None:
        """Test RawTextHelpFormatter."""
        config = ParserConfig(
            prog="myapp",
            formatter_class="RawTextHelpFormatter",
        )

        builder = ParserBuilder(config)
        parser = builder.build()

        assert parser.formatter_class is argparse.RawTextHelpFormatter

    def test_formatter_class_argument_defaults(self) -> None:
        """Test ArgumentDefaultsHelpFormatter."""
        config = ParserConfig(
            prog="myapp",
            formatter_class="ArgumentDefaultsHelpFormatter",
        )

        builder = ParserBuilder(config)
        parser = builder.build()

        assert parser.formatter_class is argparse.ArgumentDefaultsHelpFormatter

    def test_formatter_class_unknown_falls_back(self) -> None:
        """Test unknown formatter falls back to default."""
        config = ParserConfig(
            prog="myapp",
            formatter_class="UnknownFormatter",
        )

        builder = ParserBuilder(config)
        parser = builder.build()

        assert parser.formatter_class is argparse.HelpFormatter

    def test_hidden_argument_without_help_text(self) -> None:
        """Test hidden argument without help text gets SUPPRESS."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="secret",
                    flags=["--secret"],
                    type=str,
                    hidden=True,
                    # No help text set
                ),
            ],
        )

        parser = build_parser(config)
        # Hidden arguments should work but not appear in help
        args = parser.parse_args(["--secret", "value"])

        assert args.secret == "value"

    def test_hidden_argument_with_help_text(self) -> None:
        """Test hidden argument with help text still gets SUPPRESS."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="debug",
                    flags=["--debug"],
                    action="store_true",
                    hidden=True,
                    help="Enable debug mode",  # Has help but hidden
                ),
            ],
        )

        parser = build_parser(config)
        # Hidden arguments should still work
        args = parser.parse_args(["--debug"])

        assert args.debug is True

    def test_skip_argument_is_not_added(self) -> None:
        """Test that skip=True arguments are not added to parser."""
        config = ParserConfig(
            arguments=[
                ArgumentConfig(
                    name="visible",
                    flags=["--visible"],
                    type=str,
                ),
                ArgumentConfig(
                    name="internal",
                    flags=["--internal"],
                    type=str,
                    skip=True,
                ),
            ],
        )

        parser = build_parser(config)
        args = parser.parse_args(["--visible", "test"])

        assert args.visible == "test"
        assert not hasattr(args, "internal")


class TestBuildParser:
    """Tests for build_parser convenience function."""

    def test_build_parser_returns_parser(self) -> None:
        """Test that build_parser returns an ArgumentParser."""
        config = ParserConfig(prog="test")
        parser = build_parser(config)

        assert isinstance(parser, argparse.ArgumentParser)

    def test_build_parser_with_all_options(self) -> None:
        """Test building parser with various options."""
        config = ParserConfig(
            prog="myapp",
            description="My application",
            epilog="For more info, see docs.",
            add_help=True,
        )

        parser = build_parser(config)

        assert parser.prog == "myapp"
        assert parser.description == "My application"
        assert parser.epilog == "For more info, see docs."
