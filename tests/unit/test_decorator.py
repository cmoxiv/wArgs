"""Unit tests for the @wargs decorator."""

from __future__ import annotations

import argparse
from enum import Enum
from typing import Annotated, Literal

import pytest

from wargs import Arg, WargsWrapper, wargs


# Define enums at module level so they work with from __future__ import annotations
class Color(Enum):
    """Test enum for color choices."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class TestWargsDecoratorBasic:
    """Basic tests for the @wargs decorator."""

    def test_decorator_without_parentheses(self) -> None:
        """Test @wargs without parentheses."""

        @wargs
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert isinstance(greet, WargsWrapper)

    def test_decorator_with_parentheses(self) -> None:
        """Test @wargs() with parentheses but no arguments."""

        @wargs()
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert isinstance(greet, WargsWrapper)

    def test_decorator_with_options(self) -> None:
        """Test @wargs(prog=..., description=...)."""

        @wargs(prog="myapp", description="My application")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert isinstance(greet, WargsWrapper)
        assert greet.parser.prog == "myapp"
        assert greet.parser.description == "My application"

    def test_parser_property(self) -> None:
        """Test that parser property returns ArgumentParser."""

        @wargs
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert isinstance(greet.parser, argparse.ArgumentParser)

    def test_parser_caching(self) -> None:
        """Test that parser property is cached."""

        @wargs
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        parser1 = greet.parser
        parser2 = greet.parser
        assert parser1 is parser2

    def test_func_property(self) -> None:
        """Test that func property returns the wrapped function."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        wrapped = wargs(greet)
        assert wrapped.func is greet


class TestWargsDecoratorParsing:
    """Tests for argument parsing with @wargs."""

    def test_parse_required_string(self) -> None:
        """Test parsing a required string argument."""

        @wargs
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        args = greet.parse_args(["--name", "World"])
        assert args.name == "World"

    def test_parse_integer(self) -> None:
        """Test parsing an integer argument."""

        @wargs
        def repeat(count: int) -> int:
            return count * 2

        args = repeat.parse_args(["--count", "5"])
        assert args.count == 5

    def test_parse_with_default(self) -> None:
        """Test parsing argument with default value."""

        @wargs
        def greet(name: str = "World") -> str:
            return f"Hello, {name}!"

        args = greet.parse_args([])
        assert args.name == "World"

    def test_parse_boolean_flag(self) -> None:
        """Test parsing boolean flag (store_true)."""

        @wargs
        def process(verbose: bool = False) -> bool:
            return verbose

        args_on = process.parse_args(["--verbose"])
        assert args_on.verbose is True

        args_off = process.parse_args([])
        assert args_off.verbose is False

    def test_parse_list(self) -> None:
        """Test parsing list argument."""

        @wargs
        def process(files: list[str]) -> list[str]:
            return files

        args = process.parse_args(["--files", "a.txt", "b.txt"])
        assert args.files == ["a.txt", "b.txt"]

    def test_parse_choices_literal(self) -> None:
        """Test parsing Literal type as choices."""

        @wargs
        def export(format: Literal["json", "xml", "csv"]) -> str:
            return format

        args = export.parse_args(["--format", "json"])
        assert args.format == "json"


class TestWargsDecoratorExecution:
    """Tests for executing decorated functions."""

    def test_run_method(self) -> None:
        """Test run() method parses and calls function."""

        @wargs
        def add(a: int, b: int) -> int:
            return a + b

        result = add.run(["--a", "2", "--b", "3"])
        assert result == 5

    def test_call_with_args(self) -> None:
        """Test calling wrapper directly with arguments."""

        @wargs
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)
        assert result == 5

    def test_call_with_kwargs(self) -> None:
        """Test calling wrapper with keyword arguments."""

        @wargs
        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = greet(name="World", greeting="Hi")
        assert result == "Hi, World!"

    def test_repr(self) -> None:
        """Test string representation."""

        @wargs
        def my_function() -> None:
            pass

        assert "<WargsWrapper(my_function)>" in repr(my_function)


class TestWargsDecoratorDocstrings:
    """Tests for docstring parsing in @wargs."""

    def test_google_docstring_descriptions(self) -> None:
        """Test that Google docstring param descriptions are used."""

        @wargs
        def greet(name: str, count: int = 1) -> None:
            """Greet someone multiple times.

            Args:
                name: The person to greet.
                count: Number of greetings.
            """
            pass

        # Check help text contains descriptions
        help_text = greet.parser.format_help()
        assert "The person to greet" in help_text
        assert "Number of greetings" in help_text

    def test_description_from_docstring(self) -> None:
        """Test that description comes from docstring summary."""

        @wargs
        def process(data: str) -> None:
            """Process the input data."""
            pass

        description = process.parser.description
        assert description is not None
        assert "Process the input data" in description


class TestWargsDecoratorAnnotated:
    """Tests for Annotated type with Arg metadata."""

    def test_short_flag(self) -> None:
        """Test Arg with short flag."""

        @wargs
        def greet(name: Annotated[str, Arg(short="-n")]) -> str:
            return f"Hello, {name}!"

        args = greet.parse_args(["-n", "World"])
        assert args.name == "World"

    def test_custom_help(self) -> None:
        """Test Arg with custom help text."""

        @wargs
        def greet(name: Annotated[str, Arg(help="Name to greet")]) -> str:
            return f"Hello, {name}!"

        help_text = greet.parser.format_help()
        assert "Name to greet" in help_text

    def test_positional_argument(self) -> None:
        """Test Arg with positional=True."""

        @wargs
        def process(filename: Annotated[str, Arg(positional=True)]) -> str:
            return filename

        args = process.parse_args(["input.txt"])
        assert args.filename == "input.txt"


class TestWargsDecoratorEnums:
    """Tests for Enum type support."""

    def test_enum_choices(self) -> None:
        """Test that Enum members become choices."""

        @wargs
        def paint(color: Color) -> Color:
            return color

        args = paint.parse_args(["--color", "RED"])
        assert args.color == Color.RED


class TestWargsDecoratorOptions:
    """Tests for decorator options."""

    def test_add_help_false(self) -> None:
        """Test disabling automatic help."""

        @wargs(add_help=False)
        def process(data: str) -> None:
            pass

        # Should not have -h/--help
        with pytest.raises(SystemExit):
            process.parse_args(["-h"])

    def test_formatter_class(self) -> None:
        """Test custom formatter class."""

        @wargs(formatter_class="RawDescriptionHelpFormatter")
        def process(data: str) -> None:
            """Process data.

            This is a longer description
            that preserves
            newlines.
            """
            pass

        assert process.parser.formatter_class is argparse.RawDescriptionHelpFormatter


class TestWargsDecoratorEdgeCases:
    """Edge case tests for @wargs."""

    def test_function_with_no_parameters(self) -> None:
        """Test decorating function with no parameters."""

        @wargs
        def noop() -> None:
            pass

        result = noop.run([])
        assert result is None

    def test_function_with_optional_type(self) -> None:
        """Test Optional type annotation."""

        @wargs
        def greet(name: str | None = None) -> str:
            return f"Hello, {name or 'World'}!"

        result = greet.run([])
        assert result == "Hello, World!"

    def test_preserves_function_metadata(self) -> None:
        """Test that function name and docstring are preserved."""

        @wargs
        def documented_function(x: int) -> int:
            """This is the docstring."""
            return x

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is the docstring."

    def test_multiple_parameters(self) -> None:
        """Test function with multiple parameters of different types."""

        @wargs
        def process(
            input_file: str,
            output_file: str,
            count: int = 1,
            verbose: bool = False,
        ) -> dict:
            return {
                "input": input_file,
                "output": output_file,
                "count": count,
                "verbose": verbose,
            }

        result = process.run(
            [
                "--input-file",
                "in.txt",
                "--output-file",
                "out.txt",
                "--count",
                "5",
                "--verbose",
            ]
        )

        assert result["input"] == "in.txt"
        assert result["output"] == "out.txt"
        assert result["count"] == 5
        assert result["verbose"] is True


class TestWargsDecoratorIntegration:
    """Integration tests for @wargs."""

    def test_complete_cli_workflow(self) -> None:
        """Test a complete CLI workflow."""

        @wargs(prog="greet", description="A greeting program")
        def greet(
            name: str,
            greeting: str = "Hello",
            count: int = 1,
            uppercase: bool = False,
        ) -> list[str]:
            """Greet someone.

            Args:
                name: The person to greet.
                greeting: The greeting to use.
                count: Number of times to greet.
                uppercase: Whether to uppercase the output.
            """
            result = f"{greeting}, {name}!"
            if uppercase:
                result = result.upper()
            return [result] * count

        # Test parsing
        args = greet.parse_args(
            [
                "--name",
                "World",
                "--greeting",
                "Hi",
                "--count",
                "3",
                "--uppercase",
            ]
        )
        assert args.name == "World"
        assert args.greeting == "Hi"
        assert args.count == 3
        assert args.uppercase is True

        # Test execution
        result = greet.run(
            [
                "--name",
                "World",
                "--greeting",
                "Hi",
                "--count",
                "2",
                "--uppercase",
            ]
        )
        assert result == ["HI, WORLD!", "HI, WORLD!"]

        # Test direct call
        result = greet(name="Alice")
        assert result == ["Hello, Alice!"]


class TestWargsClassDecorator:
    """Tests for class-based @wargs decorator."""

    def test_class_decorator_basic(self) -> None:
        """Test basic class decoration."""
        from wargs import WargsClassWrapper

        @wargs
        class CLI:
            def add(self, name: str) -> str:
                return f"Added {name}"

        assert isinstance(CLI, WargsClassWrapper)

    def test_class_decorator_with_options(self) -> None:
        """Test class decorator with options."""

        @wargs(prog="myapp", description="My application")
        class CLI:
            def run(self) -> None:
                pass

        assert CLI.parser.prog == "myapp"
        assert CLI.parser.description == "My application"

    def test_subcommands_from_methods(self) -> None:
        """Test that methods become subcommands."""

        @wargs
        class CLI:
            def add(self, name: str) -> str:
                return f"Added {name}"

            def remove(self, item_id: int) -> str:
                return f"Removed {item_id}"

        # Check subcommands are in help
        help_text = CLI.parser.format_help()
        assert "add" in help_text
        assert "remove" in help_text

    def test_global_options_from_init(self) -> None:
        """Test that __init__ params become global options."""

        @wargs
        class CLI:
            def __init__(self, verbose: bool = False) -> None:
                self.verbose = verbose

            def run(self) -> bool:
                return self.verbose

        # Check global option in help
        help_text = CLI.parser.format_help()
        assert "--verbose" in help_text

    def test_subcommand_execution(self) -> None:
        """Test executing a subcommand."""

        @wargs
        class CLI:
            def add(self, name: str) -> str:
                return f"Added {name}"

        result = CLI.run(["add", "--name", "foo"])
        assert result == "Added foo"

    def test_global_options_passed_to_instance(self) -> None:
        """Test that global options are passed to __init__."""

        @wargs
        class CLI:
            def __init__(self, verbose: bool = False) -> None:
                self.verbose = verbose

            def run(self) -> bool:
                return self.verbose

        result = CLI.run(["--verbose", "run"])
        assert result is True

        result = CLI.run(["run"])
        assert result is False

    def test_private_methods_excluded(self) -> None:
        """Test that private methods are not subcommands."""

        @wargs
        class CLI:
            def public(self) -> str:
                return "public"

            def _private(self) -> str:
                return "private"

        help_text = CLI.parser.format_help()
        assert "public" in help_text
        assert "_private" not in help_text

    def test_method_with_underscores(self) -> None:
        """Test that method underscores become hyphens."""

        @wargs
        class CLI:
            def add_item(self) -> str:
                return "added"

        help_text = CLI.parser.format_help()
        assert "add-item" in help_text

        result = CLI.run(["add-item"])
        assert result == "added"

    def test_direct_instantiation(self) -> None:
        """Test that calling with args creates instance directly."""

        @wargs
        class CLI:
            def __init__(self, verbose: bool = False) -> None:
                self.verbose = verbose

            def run(self) -> None:
                pass

        instance = CLI(verbose=True)
        assert instance.verbose is True

    def test_subcommand_with_arguments(self) -> None:
        """Test subcommand with multiple arguments."""

        @wargs
        class CLI:
            def process(
                self,
                input_file: str,
                output_file: str,
                count: int = 1,
            ) -> dict:
                return {
                    "input": input_file,
                    "output": output_file,
                    "count": count,
                }

        result = CLI.run(
            [
                "process",
                "--input-file",
                "in.txt",
                "--output-file",
                "out.txt",
                "--count",
                "5",
            ]
        )
        assert result["input"] == "in.txt"
        assert result["output"] == "out.txt"
        assert result["count"] == 5

    def test_repr(self) -> None:
        """Test string representation."""

        @wargs
        class MyCLI:
            def run(self) -> None:
                pass

        assert "WargsClassWrapper" in repr(MyCLI)
        assert "MyCLI" in repr(MyCLI)


class TestWargsClassInheritance:
    """Tests for class inheritance with @wargs."""

    def test_inherits_parent_options(self) -> None:
        """Test that child inherits parent's __init__ parameters."""

        class BaseOptions:
            def __init__(self, debug: bool = False) -> None:
                self.debug = debug

        @wargs
        class CLI(BaseOptions):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

            def run(self) -> dict:
                return {"name": self.name, "debug": self.debug}

        # Check both options appear in help
        help_text = CLI.parser.format_help()
        assert "--name" in help_text
        assert "--debug" in help_text

    def test_inherited_options_work_with_kwargs(self) -> None:
        """Test that inherited options work when child uses **kwargs."""

        class BaseOptions:
            def __init__(self, debug: bool = False) -> None:
                self.debug = debug

        @wargs
        class CLI(BaseOptions):
            def __init__(self, name: str, **kwargs: bool) -> None:
                super().__init__(**kwargs)
                self.name = name

            def show(self) -> tuple:
                return (self.name, self.debug)

        result = CLI.run(["--debug", "--name", "test", "show"])
        assert result == ("test", True)

    def test_inherited_options_work_explicit(self) -> None:
        """Test inherited options when child explicitly accepts them."""

        class BaseOptions:
            def __init__(self, debug: bool = False) -> None:
                self.debug = debug

        @wargs
        class CLI(BaseOptions):
            def __init__(self, name: str, debug: bool = False) -> None:
                super().__init__(debug=debug)
                self.name = name

            def show(self) -> tuple:
                return (self.name, self.debug)

        result = CLI.run(["--debug", "--name", "test", "show"])
        assert result == ("test", True)

    def test_mixin_options_displayed(self) -> None:
        """Test that mixin options appear in help."""

        class VerboseMixin:
            def __init__(self, verbose: bool = False) -> None:
                self.verbose = verbose

        class DryRunMixin:
            def __init__(self, dry_run: bool = False) -> None:
                self.dry_run = dry_run

        @wargs
        class CLI(VerboseMixin, DryRunMixin):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

            def run(self) -> None:
                pass

        # All options from MRO appear in help
        help_text = CLI.parser.format_help()
        assert "--name" in help_text
        assert "--verbose" in help_text
        assert "--dry-run" in help_text

    def test_mixin_options_work_with_cooperative_inheritance(self) -> None:
        """Test mixin options with proper cooperative inheritance."""

        # For mixins to work with **kwargs, each must use cooperative inheritance
        class VerboseMixin:
            def __init__(self, verbose: bool = False, **kwargs: bool) -> None:
                super().__init__(**kwargs)
                self.verbose = verbose

        class DryRunMixin:
            def __init__(self, dry_run: bool = False, **kwargs: bool) -> None:
                super().__init__(**kwargs)
                self.dry_run = dry_run

        @wargs
        class CLI(VerboseMixin, DryRunMixin):
            def __init__(self, name: str, **kwargs: bool) -> None:
                super().__init__(**kwargs)
                self.name = name

            def show(self) -> dict:
                return {
                    "name": self.name,
                    "verbose": self.verbose,
                    "dry_run": self.dry_run,
                }

        result = CLI.run(["--verbose", "--name", "test", "show"])
        assert result["name"] == "test"
        assert result["verbose"] is True
        assert result["dry_run"] is False

    def test_disable_mro_traversal(self) -> None:
        """Test that traverse_mro=False disables inheritance."""

        class BaseOptions:
            def __init__(self, debug: bool = False) -> None:
                self.debug = debug

        @wargs(traverse_mro=False)
        class CLI(BaseOptions):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

            def run(self) -> None:
                pass

        help_text = CLI.parser.format_help()
        assert "--name" in help_text
        # debug should NOT appear because MRO traversal is disabled
        assert "--debug" not in help_text

    def test_child_overrides_parent_default(self) -> None:
        """Test that child's default overrides parent's default."""

        class Base:
            def __init__(self, value: str = "parent") -> None:
                self.value = value

        @wargs
        class CLI(Base):
            def __init__(self, value: str = "child") -> None:
                super().__init__(value)
                self.value = value

            def show(self) -> str:
                return self.value

        # Default should be "child"
        result = CLI.run(["show"])
        assert result == "child"


class TestWargsDecoratorCoverageGaps:
    """Additional tests to cover missing lines."""

    def test_parameter_without_annotation(self) -> None:
        """Test handling parameters without type annotations."""

        @wargs
        def process(data) -> str:  # no annotation
            return str(data)

        # Should still work, treating as optional string
        result = process.run(["--data", "test"])
        assert result == "test"

    def test_class_no_subcommand_shows_help(self, capsys) -> None:
        """Test that calling class without subcommand shows help."""

        @wargs
        class CLI:
            def do_something(self) -> str:
                return "done"

        result = CLI.run([])
        assert result is None  # No subcommand means None is returned

        # Help should have been printed
        captured = capsys.readouterr()
        assert "do-something" in captured.out or "usage" in captured.out.lower()

    def test_class_with_no_init(self) -> None:
        """Test class without custom __init__."""

        @wargs
        class CLI:
            def run(self) -> str:
                return "running"

        result = CLI.run(["run"])
        assert result == "running"

    def test_class_cls_property(self) -> None:
        """Test accessing cls property on WargsClassWrapper."""
        from wargs import WargsClassWrapper

        @wargs
        class MyCLI:
            def run(self) -> None:
                pass

        assert isinstance(MyCLI, WargsClassWrapper)
        assert MyCLI.cls.__name__ == "MyCLI"

    def test_wrapper_wargs_config(self) -> None:
        """Test _wargs_config property on wrapper."""

        @wargs
        def process(name: str) -> str:
            return name

        # Access parser to trigger building
        _ = process.parser

        config = process._wargs_config
        assert config is not None
        assert len(config.arguments) > 0

    def test_class_wrapper_wargs_config(self) -> None:
        """Test _wargs_config property on class wrapper."""

        @wargs
        class CLI:
            def add(self, name: str) -> str:
                return name

        # Access parser to trigger building
        _ = CLI.parser

        config = CLI._wargs_config
        assert config is not None
        assert "add" in config.subcommands

    def test_class_init_not_in_dict(self) -> None:
        """Test class that inherits __init__ from object."""

        @wargs
        class MinimalCLI:
            def run(self) -> str:
                return "done"

        result = MinimalCLI.run(["run"])
        assert result == "done"

    def test_subcommand_method_kwargs_empty_subconfig(self) -> None:
        """Test getting kwargs for a subcommand that doesn't exist."""

        @wargs
        class CLI:
            def add(self, name: str) -> str:
                return name

        # Build the parser
        _ = CLI.parser

        # Try to get kwargs for non-existent subcommand
        namespace = CLI.parse_args(["add", "--name", "test"])
        kwargs = CLI._get_method_kwargs(namespace, "nonexistent")
        assert kwargs == {}

    def test_callable_non_method_excluded(self) -> None:
        """Test that callable non-methods are excluded from subcommands."""

        class CallableClass:
            def __call__(self) -> str:
                return "called"

        @wargs
        class CLI:
            callable_attr = CallableClass()

            def real_method(self) -> str:
                return "method"

        help_text = CLI.parser.format_help()
        assert "real-method" in help_text
        # callable_attr should not appear as a subcommand
        assert "callable-attr" not in help_text

    def test_class_call_without_args_runs_cli(self, capsys, monkeypatch) -> None:
        """Test that calling class wrapper without args runs CLI."""

        @wargs
        class CLI:
            def action(self) -> str:
                return "done"

        # Patch sys.argv to simulate no args
        monkeypatch.setattr("sys.argv", ["test"])

        # Calling without args should try to parse CLI
        result = CLI()
        # Without subcommand, it prints help and returns None
        assert result is None
        captured = capsys.readouterr()
        assert "action" in captured.out or "usage" in captured.out.lower()

    def test_function_call_without_args_runs_cli(self, monkeypatch) -> None:
        """Test that calling function wrapper without args runs CLI."""

        @wargs
        def process(name: str = "default") -> str:
            return f"processed: {name}"

        # Patch sys.argv to simulate no args
        monkeypatch.setattr("sys.argv", ["test"])

        # This should parse empty CLI args and use defaults
        result = process()
        assert result == "processed: default"

    def test_class_with_formatter_class(self) -> None:
        """Test class decorator with formatter_class option."""

        @wargs(formatter_class="RawDescriptionHelpFormatter")
        class CLI:
            """Description that should be preserved.

            With multiple lines.
            """

            def run(self) -> None:
                pass

        assert CLI.parser.formatter_class is argparse.RawDescriptionHelpFormatter

    def test_get_init_kwargs_build_parser_on_demand(self) -> None:
        """Test that _get_init_kwargs builds parser if needed."""

        @wargs
        class CLI:
            def __init__(self, verbose: bool = False) -> None:
                self.verbose = verbose

            def run(self) -> bool:
                return self.verbose

        # Don't access parser first
        assert CLI._parser_config is None

        # Run should trigger parser build
        result = CLI.run(["run"])
        assert result is False

    def test_get_method_kwargs_build_parser_on_demand(self) -> None:
        """Test that _get_method_kwargs builds parser if needed."""
        from argparse import Namespace

        @wargs
        class CLI:
            def run(self, value: str = "default") -> str:
                return value

        # Access parser to build it
        _ = CLI.parser

        # Get method kwargs
        ns = Namespace(command="run", value="test")
        kwargs = CLI._get_method_kwargs(ns, "run")
        assert kwargs["value"] == "test"

    def test_var_positional_skipped(self) -> None:
        """Test that *args parameters are skipped."""

        @wargs
        def process(*items: str, count: int = 1) -> dict:
            return {"items": items, "count": count}

        # Should only have count option, not items
        result = process.run(["--count", "5"])
        assert result["count"] == 5
        assert result["items"] == ()

    def test_var_keyword_skipped(self) -> None:
        """Test that **kwargs parameters are skipped."""

        @wargs
        def process(name: str, **options) -> dict:
            return {"name": name, "options": options}

        # Should only have name option
        result = process.run(["--name", "test"])
        assert result["name"] == "test"
        assert result["options"] == {}

    def test_convert_namespace_without_parser_built(self) -> None:
        """Test _convert_namespace_to_kwargs builds parser if needed."""
        from argparse import Namespace

        @wargs
        def process(name: str = "default") -> str:
            return name

        # Don't access parser first
        assert process._func_info is None

        # Manually call _convert_namespace_to_kwargs
        ns = Namespace(name="test")
        kwargs = process._convert_namespace_to_kwargs(ns)

        # Parser should now be built
        assert process._func_info is not None
        assert kwargs["name"] == "test"

    def test_class_get_init_kwargs_without_parser_built(self) -> None:
        """Test _get_init_kwargs builds parser if needed."""
        from argparse import Namespace

        @wargs
        class CLI:
            def __init__(self, verbose: bool = False) -> None:
                self.verbose = verbose

            def run(self) -> bool:
                return self.verbose

        # Don't access parser first
        assert CLI._parser_config is None

        # Manually call _get_init_kwargs
        ns = Namespace(verbose=True, command="run")
        kwargs = CLI._get_init_kwargs(ns)

        # Parser should now be built
        assert CLI._parser_config is not None
        assert kwargs["verbose"] is True

    def test_class_get_method_kwargs_without_parser_built(self) -> None:
        """Test _get_method_kwargs builds parser if needed."""
        from argparse import Namespace

        @wargs
        class CLI:
            def process(self, value: str = "default") -> str:
                return value

        # Don't access parser first
        assert CLI._parser_config is None

        # Manually call _get_method_kwargs
        ns = Namespace(command="process", value="test")
        kwargs = CLI._get_method_kwargs(ns, "process")

        # Parser should now be built
        assert CLI._parser_config is not None
        assert kwargs["value"] == "test"
