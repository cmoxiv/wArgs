"""Unit tests for wargs utilities module."""

from __future__ import annotations

import argparse
from typing import Annotated, Literal

import pytest

from wArgs import Arg, wArgs
from wArgs.core.config import ParserConfig
from wArgs.utilities import (
    WARGS_DEBUG_VAR,
    debug_print,
    explain,
    get_config,
    get_parser,
    is_debug_enabled,
)


class TestIsDebugEnabled:
    """Tests for is_debug_enabled function."""

    def test_debug_disabled_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is disabled when env var is not set."""
        monkeypatch.delenv(WARGS_DEBUG_VAR, raising=False)
        assert is_debug_enabled() is False

    def test_debug_disabled_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is disabled when env var is empty."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "")
        assert is_debug_enabled() is False

    def test_debug_enabled_with_1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is enabled with '1'."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "1")
        assert is_debug_enabled() is True

    def test_debug_enabled_with_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is enabled with 'true'."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "true")
        assert is_debug_enabled() is True

    def test_debug_enabled_with_TRUE(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is enabled with 'TRUE' (case insensitive)."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "TRUE")
        assert is_debug_enabled() is True

    def test_debug_enabled_with_yes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is enabled with 'yes'."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "yes")
        assert is_debug_enabled() is True

    def test_debug_enabled_with_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is enabled with 'on'."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "on")
        assert is_debug_enabled() is True

    def test_debug_disabled_with_0(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is disabled with '0'."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "0")
        assert is_debug_enabled() is False

    def test_debug_disabled_with_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that debug is disabled with 'false'."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "false")
        assert is_debug_enabled() is False


class TestDebugPrint:
    """Tests for debug_print function."""

    def test_debug_print_when_disabled(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that debug_print does nothing when debug is disabled."""
        monkeypatch.delenv(WARGS_DEBUG_VAR, raising=False)
        debug_print("test message")
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_debug_print_when_enabled(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that debug_print outputs to stderr when enabled."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "1")
        debug_print("test message")
        captured = capsys.readouterr()
        assert "[wargs]" in captured.err
        assert "test message" in captured.err

    def test_debug_print_multiple_args(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test debug_print with multiple arguments."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "1")
        debug_print("arg1", "arg2", "arg3")
        captured = capsys.readouterr()
        assert "arg1" in captured.err
        assert "arg2" in captured.err
        assert "arg3" in captured.err


class TestGetParser:
    """Tests for get_parser function."""

    def test_get_parser_returns_parser(self) -> None:
        """Test that get_parser returns an ArgumentParser."""

        @wArgs(prefix=True)
        def my_func(name: str) -> str:
            return name

        parser = get_parser(my_func)
        assert isinstance(parser, argparse.ArgumentParser)

    def test_get_parser_same_as_property(self) -> None:
        """Test that get_parser returns the same parser as the property."""

        @wArgs(prefix=True)
        def my_func(name: str) -> str:
            return name

        assert get_parser(my_func) is my_func.parser

    def test_get_parser_with_class(self) -> None:
        """Test get_parser with a class decorator."""

        @wArgs(prefix=True)
        class CLI:
            def run(self) -> None:
                pass

        parser = get_parser(CLI)
        assert isinstance(parser, argparse.ArgumentParser)

    def test_get_parser_with_non_decorated(self) -> None:
        """Test get_parser raises TypeError for non-decorated function."""

        def regular_func(name: str) -> str:
            return name

        with pytest.raises(TypeError, match="Expected a @wargs decorated"):
            get_parser(regular_func)


class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_returns_parser_config(self) -> None:
        """Test that get_config returns a ParserConfig."""

        @wArgs(prefix=True)
        def my_func(name: str) -> str:
            return name

        config = get_config(my_func)
        assert isinstance(config, ParserConfig)

    def test_get_config_has_arguments(self) -> None:
        """Test that config has the expected arguments."""

        @wArgs(prefix=True)
        def my_func(name: str, count: int = 1) -> str:
            return name

        config = get_config(my_func)
        arg_names = [arg.name for arg in config.arguments]
        assert "name" in arg_names
        assert "count" in arg_names

    def test_get_config_with_class(self) -> None:
        """Test get_config with a class decorator."""

        @wArgs(prefix=True)
        class CLI:
            def add(self, name: str) -> str:
                return name

        config = get_config(CLI)
        assert isinstance(config, ParserConfig)
        assert "add" in config.subcommands

    def test_get_config_with_non_decorated(self) -> None:
        """Test get_config raises TypeError for non-decorated function."""

        def regular_func(name: str) -> str:
            return name

        with pytest.raises(TypeError, match="Expected a @wargs decorated"):
            get_config(regular_func)


class TestExplain:
    """Tests for explain function."""

    def test_explain_basic_function(self) -> None:
        """Test explain output for a basic function."""

        @wArgs(prefix=True)
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        output = explain(greet)
        assert "Function: greet" in output
        assert "Single-command CLI" in output
        assert "--greet-name" in output

    def test_explain_with_description(self) -> None:
        """Test explain includes description."""

        @wArgs(prog="myapp", description="My application", prefix=True)
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        output = explain(greet)
        assert "Program: myapp" in output
        assert "Description: My application" in output

    def test_explain_shows_default_values(self) -> None:
        """Test explain shows default values."""

        @wArgs(prefix=True)
        def greet(name: str = "World") -> str:
            return f"Hello, {name}!"

        output = explain(greet)
        assert "default:" in output
        assert "'World'" in output

    def test_explain_shows_required(self) -> None:
        """Test explain shows required arguments."""

        @wArgs(prefix=True)
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        output = explain(greet)
        assert "[required]" in output

    def test_explain_class_subcommands(self) -> None:
        """Test explain output for a class with subcommands."""

        @wArgs(prefix=True)
        class CLI:
            def add(self, name: str) -> str:
                """Add an item."""
                return name

            def remove(self, item_id: int) -> str:
                """Remove an item."""
                return str(item_id)

        output = explain(CLI)
        assert "Class: CLI" in output
        assert "Subcommand-based CLI" in output
        assert "Subcommands:" in output
        assert "add:" in output
        assert "remove:" in output

    def test_explain_verbose_mode(self) -> None:
        """Test explain with verbose mode."""

        @wArgs(prefix=True)
        def greet(name: str) -> str:
            """Greet someone.

            Args:
                name: The person to greet.
            """
            return f"Hello, {name}!"

        output = explain(greet, verbose=True)
        assert "Help:" in output
        assert "The person to greet" in output

    def test_explain_positional_argument(self) -> None:
        """Test explain with positional argument."""

        @wArgs(prefix=True)
        def process(filename: Annotated[str, Arg(positional=True)]) -> str:
            return filename

        output = explain(process)
        # Positional shows just the name, not --filename
        assert "filename" in output

    def test_explain_with_choices(self) -> None:
        """Test explain shows choices."""

        @wArgs(prefix=True)
        def export(format: Literal["json", "xml", "csv"]) -> str:
            return format

        output = explain(export)
        assert "choices:" in output


class TestWargsConfigAttribute:
    """Tests for _wargs_config attribute on decorated functions."""

    def test_function_has_wargs_config(self) -> None:
        """Test that decorated function has _wargs_config attribute."""

        @wArgs(prefix=True)
        def my_func(name: str) -> str:
            return name

        # Access parser to trigger building
        _ = my_func.parser

        config = my_func._wargs_config
        assert config is not None
        assert isinstance(config, ParserConfig)

    def test_class_has_wargs_config(self) -> None:
        """Test that decorated class has _wargs_config attribute."""

        @wArgs(prefix=True)
        class CLI:
            def run(self) -> None:
                pass

        # Access parser to trigger building
        _ = CLI.parser

        config = CLI._wargs_config
        assert config is not None
        assert isinstance(config, ParserConfig)

    def test_wargs_config_none_before_build(self) -> None:
        """Test that _wargs_config is None before parser is built."""

        @wArgs(prefix=True)
        def my_func(name: str) -> str:
            return name

        # Don't access parser
        assert my_func._wargs_config is None

    def test_wargs_config_matches_get_config(self) -> None:
        """Test that _wargs_config matches get_config result."""

        @wArgs(prefix=True)
        def my_func(name: str) -> str:
            return name

        config1 = get_config(my_func)
        config2 = my_func._wargs_config

        assert config1 is config2


class TestDebugOutputIntegration:
    """Integration tests for debug output during parsing."""

    def test_debug_output_on_parse(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that debug output is produced during parsing."""
        monkeypatch.setenv(WARGS_DEBUG_VAR, "1")

        @wArgs(prefix=True)
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        greet.run(["--greet-name", "World"])

        captured = capsys.readouterr()
        assert "Building parser" in captured.err
        assert "Parsing args" in captured.err
        assert "Parsed result" in captured.err

    def test_no_debug_output_when_disabled(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that no debug output is produced when disabled."""
        monkeypatch.delenv(WARGS_DEBUG_VAR, raising=False)

        @wArgs(prefix=True)
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        greet.run(["--greet-name", "World"])

        captured = capsys.readouterr()
        assert "[wargs]" not in captured.err
