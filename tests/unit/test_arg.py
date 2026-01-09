"""Unit tests for Arg metadata class."""

from __future__ import annotations

import pytest

from wArgs.core.arg import Arg


class TestArgCreation:
    """Tests for Arg dataclass creation."""

    def test_default_values(self) -> None:
        """Test Arg has correct defaults."""
        arg = Arg()
        assert arg.short is None
        assert arg.long is None
        assert arg.help is None
        assert arg.metavar is None
        assert arg.choices is None
        assert arg.action is None
        assert arg.nargs is None
        assert arg.const is None
        assert arg.default is None
        assert arg.required is None
        assert arg.dest is None
        assert arg.group is None
        assert arg.mutually_exclusive is None
        assert arg.positional is False
        assert arg.hidden is False
        assert arg.skip is False
        assert arg.envvar is None

    def test_short_flag(self) -> None:
        """Test creating Arg with short flag."""
        arg = Arg(short="-n")
        assert arg.short == "-n"

    def test_long_flag(self) -> None:
        """Test creating Arg with long flag."""
        arg = Arg(long="--name")
        assert arg.long == "--name"

    def test_both_flags(self) -> None:
        """Test creating Arg with both flags."""
        arg = Arg(short="-n", long="--name")
        assert arg.short == "-n"
        assert arg.long == "--name"

    def test_help_text(self) -> None:
        """Test creating Arg with help text."""
        arg = Arg(help="The name to use")
        assert arg.help == "The name to use"

    def test_positional(self) -> None:
        """Test creating positional Arg."""
        arg = Arg(positional=True)
        assert arg.positional is True

    def test_hidden(self) -> None:
        """Test creating hidden Arg."""
        arg = Arg(hidden=True)
        assert arg.hidden is True

    def test_skip(self) -> None:
        """Test creating skipped Arg."""
        arg = Arg(skip=True)
        assert arg.skip is True

    def test_choices(self) -> None:
        """Test creating Arg with choices."""
        arg = Arg(choices=["a", "b", "c"])
        assert arg.choices == ["a", "b", "c"]

    def test_group(self) -> None:
        """Test creating Arg with group."""
        arg = Arg(group="Advanced options")
        assert arg.group == "Advanced options"

    def test_mutually_exclusive(self) -> None:
        """Test creating Arg with mutually exclusive group."""
        arg = Arg(mutually_exclusive="output_format")
        assert arg.mutually_exclusive == "output_format"

    def test_is_frozen(self) -> None:
        """Test that Arg is immutable."""
        arg = Arg(short="-n")
        with pytest.raises(AttributeError):
            arg.short = "-x"  # type: ignore[misc]


class TestArgValidation:
    """Tests for Arg validation."""

    def test_invalid_short_flag_double_dash(self) -> None:
        """Test that double-dash short flag is rejected."""
        with pytest.raises(ValueError, match="single dash"):
            Arg(short="--n")

    def test_invalid_short_flag_no_dash(self) -> None:
        """Test that short flag without dash is rejected."""
        with pytest.raises(ValueError, match="single dash"):
            Arg(short="n")

    def test_invalid_short_flag_too_long(self) -> None:
        """Test that long short flag is rejected."""
        with pytest.raises(ValueError, match="exactly 2 characters"):
            Arg(short="-name")

    def test_invalid_long_flag_single_dash(self) -> None:
        """Test that single-dash long flag is rejected."""
        with pytest.raises(ValueError, match="double dash"):
            Arg(long="-name")

    def test_positional_with_short_flag(self) -> None:
        """Test that positional with short flag is rejected."""
        with pytest.raises(ValueError, match="cannot have flags"):
            Arg(positional=True, short="-n")

    def test_positional_with_long_flag(self) -> None:
        """Test that positional with long flag is rejected."""
        with pytest.raises(ValueError, match="cannot have flags"):
            Arg(positional=True, long="--name")

    def test_hidden_positional(self) -> None:
        """Test that hidden positional is rejected."""
        with pytest.raises(ValueError, match="cannot be hidden"):
            Arg(positional=True, hidden=True)


class TestArgUseCases:
    """Tests for common Arg use cases."""

    def test_count_action(self) -> None:
        """Test Arg for counting (like -v for verbosity)."""
        arg = Arg(short="-v", action="count", default=0)
        assert arg.action == "count"
        assert arg.default == 0

    def test_store_const(self) -> None:
        """Test Arg for storing constant value."""
        arg = Arg(action="store_const", const="DEBUG")
        assert arg.action == "store_const"
        assert arg.const == "DEBUG"

    def test_envvar_fallback(self) -> None:
        """Test Arg with environment variable fallback."""
        arg = Arg(envvar="MY_APP_NAME")
        assert arg.envvar == "MY_APP_NAME"
