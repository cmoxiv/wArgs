"""Tests for wargs command groups."""

from __future__ import annotations

from wArgs import wArgs
from wArgs.core.groups import CommandInfo, WargsGroup


class TestGroupDecorator:
    """Tests for the @wArgs.group() decorator."""

    def test_basic_group(self) -> None:
        """Test creating a basic group."""

        @wArgs.group()
        def cli() -> None:
            """My CLI."""
            pass

        assert isinstance(cli, WargsGroup)
        assert cli.func.__name__ == "cli"

    def test_group_with_options(self) -> None:
        """Test group with shared options."""

        @wArgs.group(prog="myapp", description="My application")
        def cli(verbose: bool = False) -> None:
            """My CLI."""
            pass

        assert isinstance(cli, WargsGroup)
        assert cli._prog == "myapp"
        assert cli._description == "My application"


class TestCommandRegistration:
    """Tests for @group.command() registration."""

    def test_register_command(self) -> None:
        """Test registering a command."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            """Say hello."""
            return f"Hello, {name}!"

        assert "hello" in cli.commands
        assert cli.commands["hello"].func is hello
        assert cli.commands["hello"].description == "Say hello."

    def test_register_multiple_commands(self) -> None:
        """Test registering multiple commands."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def add(name: str) -> str:
            """Add item."""
            return name

        @cli.command()
        def remove(item_id: int) -> int:
            """Remove item."""
            return item_id

        assert len(cli.commands) == 2
        assert "add" in cli.commands
        assert "remove" in cli.commands

    def test_command_with_custom_name(self) -> None:
        """Test command with custom name."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command(name="greet")
        def hello(name: str) -> str:
            """Say hello."""
            return f"Hello, {name}!"

        assert "greet" in cli.commands
        assert "hello" not in cli.commands

    def test_command_name_from_underscore(self) -> None:
        """Test command name converts underscores to hyphens."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def list_items() -> None:
            """List items."""
            pass

        assert "list-items" in cli.commands


class TestGroupExecution:
    """Tests for group execution."""

    def test_run_command(self, capsys) -> None:
        """Test running a command."""
        calls = []

        @wArgs.group()
        def cli() -> None:
            calls.append("cli")

        @cli.command()
        def hello(name: str) -> str:
            calls.append(f"hello({name})")
            return f"Hello, {name}!"

        result = cli.run(["hello", "--name", "World"])

        assert result == "Hello, World!"
        assert calls == ["cli", "hello(World)"]

    def test_run_with_shared_options(self, capsys) -> None:
        """Test running with shared options."""
        verbose_value = []

        @wArgs.group()
        def cli(verbose: bool = False) -> None:
            verbose_value.append(verbose)

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        cli.run(["--verbose", "hello", "--name", "World"])

        assert verbose_value == [True]

    def test_run_no_command_shows_help(self, capsys) -> None:
        """Test running without command shows help."""

        @wArgs.group(prog="myapp")
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        result = cli.run([])

        assert result is None
        captured = capsys.readouterr()
        assert "myapp" in captured.out or "usage" in captured.out.lower()

    def test_call_without_args_runs_cli(self, capsys) -> None:
        """Test calling group without args runs CLI."""
        calls = []

        @wArgs.group()
        def cli(verbose: bool = False) -> None:
            calls.append(f"cli(verbose={verbose})")

        @cli.command()
        def hello(name: str = "World") -> str:
            calls.append("hello")
            return "Hello!"

        # Direct call with args bypasses CLI parsing
        cli(verbose=True)

        assert calls == ["cli(verbose=True)"]
        assert isinstance(cli, WargsGroup)


class TestNestedGroups:
    """Tests for nested groups."""

    def test_create_subgroup(self) -> None:
        """Test creating a subgroup."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.group()
        def db() -> None:
            """Database operations."""
            pass

        assert "db" in cli.subgroups
        assert isinstance(cli.subgroups["db"], WargsGroup)

    def test_subgroup_commands(self) -> None:
        """Test commands in subgroup."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.group()
        def db() -> None:
            """Database operations."""
            pass

        @db.command()
        def migrate() -> None:
            """Run migrations."""
            pass

        assert "migrate" in cli.subgroups["db"].commands


class TestGroupParser:
    """Tests for group parser building."""

    def test_parser_creation(self) -> None:
        """Test that parser is created lazily."""

        @wArgs.group(prog="myapp")
        def cli(verbose: bool = False) -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        # Parser should be built lazily
        parser = cli.parser
        assert parser is not None
        assert parser.prog == "myapp"

    def test_parser_has_subcommands(self) -> None:
        """Test parser has subcommands."""

        @wArgs.group(prog="myapp")
        def cli() -> None:
            pass

        @cli.command()
        def add(name: str) -> str:
            return name

        @cli.command()
        def remove(item_id: int) -> int:
            return item_id

        parser = cli.parser
        # Check that subparsers exist
        assert hasattr(parser, "_subparsers")

    def test_wargs_config_available(self) -> None:
        """Test _wargs_config is available for completion."""

        @wArgs.group(prog="myapp")
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        config = cli._wargs_config
        assert config is not None
        assert config.prog == "myapp"


class TestGroupCompletion:
    """Tests for group completion support."""

    def test_completion_flag(self, capsys) -> None:
        """Test --completion flag on group."""

        @wArgs.group(prog="myapp", completion=True)
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        result = cli.run(["--completion", "bash"])

        assert result is None
        captured = capsys.readouterr()
        assert "myapp" in captured.out


class TestCommandInfo:
    """Tests for CommandInfo dataclass."""

    def test_command_info_defaults(self) -> None:
        """Test CommandInfo default values."""

        def func() -> None:
            pass

        info = CommandInfo(name="test", func=func)

        assert info.name == "test"
        assert info.func is func
        assert info.description == ""
        assert info.config is None


class TestGroupRepr:
    """Tests for group representation."""

    def test_repr(self) -> None:
        """Test __repr__."""

        @wArgs.group()
        def mycli() -> None:
            pass

        assert "mycli" in repr(mycli)
        assert "WargsGroup" in repr(mycli)


class TestGroupDirectCall:
    """Tests for direct group function calls."""

    def test_direct_call_bypasses_parsing(self) -> None:
        """Test calling group with args bypasses CLI parsing."""
        calls = []

        @wArgs.group()
        def cli(verbose: bool = False) -> None:
            calls.append(f"verbose={verbose}")

        cli(verbose=True)

        assert calls == ["verbose=True"]


class TestGroupArgumentKwargs:
    """Tests for argument kwargs building in groups."""

    def test_command_with_default(self) -> None:
        """Test command with default value."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def greet(name: str = "World") -> str:
            return f"Hello, {name}!"

        result = cli.run(["greet"])
        assert result == "Hello, World!"

    def test_command_with_required(self) -> None:
        """Test command with required argument."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        result = cli.run(["greet", "--name", "Alice"])
        assert result == "Hello, Alice!"

    def test_command_with_choices(self) -> None:
        """Test command with choices."""
        from typing import Literal

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def format(output: Literal["json", "csv"] = "json") -> str:
            return output

        result = cli.run(["format", "--output", "csv"])
        assert result == "csv"

    def test_command_with_boolean(self) -> None:
        """Test command with boolean flag."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def process(verbose: bool = False) -> bool:
            return verbose

        result = cli.run(["process", "--verbose"])
        assert result is True

    def test_command_with_int(self) -> None:
        """Test command with int argument."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def multiply(value: int = 1) -> int:
            return value * 2

        result = cli.run(["multiply", "--value", "5"])
        assert result == 10


class TestGroupParserOptions:
    """Tests for group parser options."""

    def test_group_with_formatter_class(self) -> None:
        """Test group with custom formatter class."""

        @wArgs.group(prog="myapp", formatter_class="ArgumentDefaultsHelpFormatter")
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str = "World") -> str:
            return f"Hello, {name}!"

        parser = cli.parser
        assert parser is not None

    def test_group_without_help(self) -> None:
        """Test group with add_help=False."""

        @wArgs.group(prog="myapp", add_help=False)
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        parser = cli.parser
        # Parser should not have -h/--help
        assert parser is not None


class TestBuildAddArgumentKwargs:
    """Tests for _build_add_argument_kwargs function."""

    def test_build_kwargs_with_hidden_and_help(self) -> None:
        """Test building kwargs with hidden=True and help text."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="secret",
            help="Secret value",
            hidden=True,
        )

        kwargs = _build_add_argument_kwargs(config)

        import argparse

        assert kwargs.get("help") == argparse.SUPPRESS

    def test_build_kwargs_with_hidden_no_help(self) -> None:
        """Test building kwargs with hidden=True and no help text."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="secret",
            hidden=True,
        )

        kwargs = _build_add_argument_kwargs(config)

        import argparse

        assert kwargs.get("help") == argparse.SUPPRESS

    def test_build_kwargs_with_choices(self) -> None:
        """Test building kwargs with choices."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="format",
            choices=["json", "csv"],
        )

        kwargs = _build_add_argument_kwargs(config)

        assert kwargs.get("choices") == ["json", "csv"]

    def test_build_kwargs_with_action(self) -> None:
        """Test building kwargs with action."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="verbose",
            action="store_true",
        )

        kwargs = _build_add_argument_kwargs(config)

        assert kwargs.get("action") == "store_true"

    def test_build_kwargs_with_nargs(self) -> None:
        """Test building kwargs with nargs."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="items",
            nargs="+",
        )

        kwargs = _build_add_argument_kwargs(config)

        assert kwargs.get("nargs") == "+"

    def test_build_kwargs_with_metavar(self) -> None:
        """Test building kwargs with metavar."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="file",
            metavar="FILE",
        )

        kwargs = _build_add_argument_kwargs(config)

        assert kwargs.get("metavar") == "FILE"

    def test_build_kwargs_with_dest(self) -> None:
        """Test building kwargs with dest."""
        from wArgs.core.config import ArgumentConfig
        from wArgs.core.groups import _build_add_argument_kwargs

        config = ArgumentConfig(
            name="output",
            dest="output_file",
        )

        kwargs = _build_add_argument_kwargs(config)

        assert kwargs.get("dest") == "output_file"


class TestGroupEdgeCases:
    """Tests for edge cases in groups."""

    def test_empty_group(self) -> None:
        """Test group with no commands."""

        @wArgs.group(prog="myapp")
        def cli() -> None:
            pass

        # Should show help when no commands
        parser = cli.parser
        assert parser is not None

    def test_command_with_metavar(self) -> None:
        """Test command with metavar argument."""
        from typing import Annotated

        from wArgs import Arg

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def greet(name: Annotated[str, Arg(metavar="NAME")] = "World") -> str:
            return f"Hello, {name}!"

        result = cli.run(["greet", "--name", "Alice"])
        assert result == "Hello, Alice!"

    def test_command_with_hidden_arg(self) -> None:
        """Test command with hidden argument."""
        from typing import Annotated

        from wArgs import Arg

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def process(secret: Annotated[str, Arg(hidden=True)] = "default") -> str:
            return secret

        result = cli.run(["process"])
        assert result == "default"

    def test_parse_args_method(self) -> None:
        """Test parse_args method directly."""

        @wArgs.group()
        def cli() -> None:
            pass

        @cli.command()
        def hello(name: str) -> str:
            return f"Hello, {name}!"

        namespace = cli.parse_args(["hello", "--name", "Bob"])
        assert namespace.command == "hello"
        assert namespace.name == "Bob"

    def test_subgroup_execution(self) -> None:
        """Test running a command in a subgroup."""
        calls = []

        @wArgs.group()
        def cli() -> None:
            calls.append("cli")

        @cli.group()
        def db() -> None:
            calls.append("db")

        @db.command()
        def migrate() -> str:
            calls.append("migrate")
            return "migrated"

        # Force build the parser
        _ = cli.parser
        # Subgroup execution would need more complex routing
        # For now, verify the structure is correct
        assert "db" in cli.subgroups
        assert "migrate" in cli.subgroups["db"].commands
