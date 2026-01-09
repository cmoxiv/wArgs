"""Unit tests for argument configuration builder."""

from __future__ import annotations

from typing import Annotated

from wargs.builders.arguments import (
    _format_default_help,
    _get_enum_metavar,
    _get_nargs,
    build_argument_config,
    build_parser_config,
)
from wargs.core.arg import Arg
from wargs.core.config import (
    MISSING,
    FunctionInfo,
    ParameterInfo,
    ParameterKind,
    TypeInfo,
)


class TestInternalFunctions:
    """Tests for internal helper functions."""

    def test_get_nargs_var_positional(self) -> None:
        """Test _get_nargs for VAR_POSITIONAL parameter kind."""
        type_info = TypeInfo(origin=str, converter=str)

        result = _get_nargs(type_info, ParameterKind.VAR_POSITIONAL)

        assert result == "*"

    def test_format_default_help_missing(self) -> None:
        """Test _format_default_help with MISSING sentinel."""
        result = _format_default_help(MISSING, True)

        assert result == ""

    def test_format_default_help_no_default(self) -> None:
        """Test _format_default_help with has_default=False."""
        result = _format_default_help("value", False)

        assert result == ""

    def test_get_enum_metavar_none(self) -> None:
        """Test _get_enum_metavar with None type_info."""
        result = _get_enum_metavar(None)

        assert result is None


class TestExtractArgMetadata:
    """Tests for Arg metadata extraction from Annotated types."""

    def test_annotated_without_arg(self) -> None:
        """Test Annotated type without Arg metadata."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            parameters=[
                ParameterInfo(
                    name="value",
                    annotation=Annotated[str, "some string metadata"],
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
            ],
        )

        config = build_parser_config(func_info)

        # Should use default flags since no Arg metadata
        assert config.arguments[0].flags == ["--value"]

    def test_annotated_with_multiple_metadata(self) -> None:
        """Test Annotated type with Arg and other metadata."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            parameters=[
                ParameterInfo(
                    name="value",
                    annotation=Annotated[str, "doc", Arg(short="-v"), 42],
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
            ],
        )

        config = build_parser_config(func_info)

        # Should find Arg even among other metadata
        assert config.arguments[0].flags == ["-v", "--value"]


class TestBuildArgumentConfig:
    """Tests for build_argument_config function."""

    def test_simple_string_parameter(self) -> None:
        """Test building config for simple string parameter."""
        param = ParameterInfo(
            name="name",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.name == "name"
        assert config.flags == ["--name"]
        assert config.type is str
        assert config.required is True
        assert config.positional is False

    def test_parameter_with_default(self) -> None:
        """Test building config for parameter with default."""
        param = ParameterInfo(
            name="count",
            annotation=int,
            type_info=TypeInfo(origin=int, converter=int),
            default=10,
            has_default=True,
        )

        config = build_argument_config(param)

        assert config.default == 10
        assert config.required is False

    def test_boolean_parameter(self) -> None:
        """Test building config for boolean parameter."""
        param = ParameterInfo(
            name="verbose",
            annotation=bool,
            type_info=TypeInfo(origin=bool, converter=bool),
            default=False,
            has_default=True,
        )

        config = build_argument_config(param)

        assert config.action == "store_true"
        assert config.type is None  # store_true doesn't need type

    def test_list_parameter(self) -> None:
        """Test building config for list parameter."""
        param = ParameterInfo(
            name="files",
            annotation=list[str],
            type_info=TypeInfo(origin=list, args=(str,), converter=str),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.nargs == "*"
        assert config.type is str

    def test_parameter_with_description(self) -> None:
        """Test building config with description."""
        param = ParameterInfo(
            name="output",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
            description="Output file path",
        )

        config = build_argument_config(param)

        assert config.help == "Output file path"

    def test_parameter_with_arg_metadata(self) -> None:
        """Test building config with Arg metadata."""
        param = ParameterInfo(
            name="name",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(short="-n", help="The name to use")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.flags == ["-n", "--name"]
        assert config.help == "The name to use"

    def test_skip_parameter(self) -> None:
        """Test building config for skipped parameter."""
        param = ParameterInfo(name="internal")

        arg = Arg(skip=True)
        config = build_argument_config(param, arg_metadata=arg)

        assert config.skip is True

    def test_positional_parameter(self) -> None:
        """Test building config for positional parameter."""
        param = ParameterInfo(
            name="filename",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(positional=True)
        config = build_argument_config(param, arg_metadata=arg)

        assert config.positional is True
        assert config.flags == []  # No flags for positional

    def test_hidden_parameter(self) -> None:
        """Test building config for hidden parameter."""
        param = ParameterInfo(
            name="debug_mode",
            annotation=bool,
            type_info=TypeInfo(origin=bool, converter=bool),
            default=False,
            has_default=True,
        )

        arg = Arg(hidden=True)
        config = build_argument_config(param, arg_metadata=arg)

        assert config.hidden is True

    def test_underscore_to_hyphen_conversion(self) -> None:
        """Test that underscores are converted to hyphens in flags."""
        param = ParameterInfo(
            name="output_file",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.flags == ["--output-file"]

    def test_custom_long_flag(self) -> None:
        """Test building config with custom long flag."""
        param = ParameterInfo(
            name="output",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(long="--out")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.flags == ["--out"]

    def test_group_assignment(self) -> None:
        """Test building config with group."""
        param = ParameterInfo(name="option")

        arg = Arg(group="Advanced")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.group == "Advanced"

    def test_mutually_exclusive_assignment(self) -> None:
        """Test building config with mutually exclusive group."""
        param = ParameterInfo(name="json_output")

        arg = Arg(mutually_exclusive="output_format")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.mutually_exclusive == "output_format"

    def test_literal_choices(self) -> None:
        """Test building config from Literal type."""
        from typing import Literal

        param = ParameterInfo(
            name="format",
            annotation=Literal["json", "xml", "csv"],
            type_info=TypeInfo(
                origin=str,
                is_literal=True,
                literal_values=("json", "xml", "csv"),
                converter=str,
            ),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.choices == ["json", "xml", "csv"]

    def test_enum_metavar(self) -> None:
        """Test building config from Enum type uses metavar instead of choices.

        Enums use metavar (e.g., "{RED,GREEN,BLUE}") rather than choices
        because argparse validates choices AFTER type conversion, which
        breaks enum converters.
        """
        from enum import Enum

        class Color(Enum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"

        param = ParameterInfo(
            name="color",
            annotation=Color,
            type_info=TypeInfo(
                origin=Color,
                is_enum=True,
                enum_class=Color,
            ),
            has_default=False,
        )

        config = build_argument_config(param)

        # Enum uses metavar for display, not choices
        assert config.choices is None
        assert config.metavar == "{RED,GREEN,BLUE}"


class TestBuildArgumentConfigAdvanced:
    """Additional tests for edge cases and full coverage."""

    def test_tuple_nargs_fixed_length(self) -> None:
        """Test nargs for fixed-length tuple types."""
        param = ParameterInfo(
            name="coords",
            annotation=tuple[int, int, int],
            type_info=TypeInfo(origin=tuple, args=(int, int, int), converter=int),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.nargs == 3  # Fixed length tuple

    def test_tuple_nargs_variable_length(self) -> None:
        """Test nargs for variable-length tuple with ellipsis."""
        param = ParameterInfo(
            name="values",
            annotation=tuple[int, ...],
            type_info=TypeInfo(origin=tuple, args=(int, ...), converter=int),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.nargs == "*"

    def test_no_type_info(self) -> None:
        """Test building config when type_info is None."""
        param = ParameterInfo(
            name="value",
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.type is str  # Default to str
        assert config.nargs is None

    def test_arg_metadata_nargs_override(self) -> None:
        """Test nargs override from Arg metadata."""
        param = ParameterInfo(
            name="items",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(nargs="+")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.nargs == "+"

    def test_arg_metadata_choices_override(self) -> None:
        """Test choices override from Arg metadata."""
        param = ParameterInfo(
            name="level",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(choices=["low", "medium", "high"])
        config = build_argument_config(param, arg_metadata=arg)

        assert config.choices == ["low", "medium", "high"]

    def test_arg_metadata_required_override(self) -> None:
        """Test required override from Arg metadata."""
        param = ParameterInfo(
            name="config",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            default="default.cfg",
            has_default=True,
        )

        arg = Arg(required=True)
        config = build_argument_config(param, arg_metadata=arg)

        assert config.required is True

    def test_arg_metadata_default_override(self) -> None:
        """Test default override from Arg metadata."""
        param = ParameterInfo(
            name="port",
            annotation=int,
            type_info=TypeInfo(origin=int, converter=int),
            default=8080,
            has_default=True,
        )

        arg = Arg(default=9000)
        config = build_argument_config(param, arg_metadata=arg)

        assert config.default == 9000

    def test_arg_metadata_metavar(self) -> None:
        """Test metavar from Arg metadata."""
        param = ParameterInfo(
            name="input_file",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(metavar="FILE")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.metavar == "FILE"

    def test_arg_metadata_dest(self) -> None:
        """Test dest from Arg metadata."""
        param = ParameterInfo(
            name="output",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(dest="output_path")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.dest == "output_path"

    def test_help_with_string_default(self) -> None:
        """Test help text includes string default properly quoted."""
        param = ParameterInfo(
            name="name",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            default="world",
            has_default=True,
            description="Name to greet",
        )

        config = build_argument_config(param)

        assert "(default: 'world')" in config.help

    def test_help_with_integer_default(self) -> None:
        """Test help text includes integer default."""
        param = ParameterInfo(
            name="count",
            annotation=int,
            type_info=TypeInfo(origin=int, converter=int),
            default=5,
            has_default=True,
            description="Number of times",
        )

        config = build_argument_config(param)

        assert "(default: 5)" in config.help

    def test_help_with_none_default(self) -> None:
        """Test help text does not include None default."""
        param = ParameterInfo(
            name="option",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            default=None,
            has_default=True,
            description="Optional value",
        )

        config = build_argument_config(param)

        assert "(default:" not in config.help

    def test_action_store_const(self) -> None:
        """Test store_const action clears type."""
        param = ParameterInfo(
            name="mode",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(action="store_const")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.action == "store_const"
        assert config.type is None

    def test_action_count(self) -> None:
        """Test count action clears type."""
        param = ParameterInfo(
            name="verbose",
            annotation=int,
            type_info=TypeInfo(origin=int, converter=int),
            has_default=False,
        )

        arg = Arg(action="count")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.action == "count"
        assert config.type is None

    def test_action_append_keeps_type(self) -> None:
        """Test append action keeps the type converter."""
        param = ParameterInfo(
            name="items",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
        )

        arg = Arg(action="append")
        config = build_argument_config(param, arg_metadata=arg)

        assert config.action == "append"
        assert config.type is str  # Should keep the type

    def test_set_type_nargs(self) -> None:
        """Test nargs for set types."""
        param = ParameterInfo(
            name="tags",
            annotation=set[str],
            type_info=TypeInfo(origin=set, args=(str,), converter=str),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.nargs == "*"

    def test_frozenset_type_nargs(self) -> None:
        """Test nargs for frozenset types."""
        param = ParameterInfo(
            name="ids",
            annotation=frozenset[int],
            type_info=TypeInfo(origin=frozenset, args=(int,), converter=int),
            has_default=False,
        )

        config = build_argument_config(param)

        assert config.nargs == "*"

    def test_positional_only_parameter(self) -> None:
        """Test positional-only parameter becomes positional argument."""
        param = ParameterInfo(
            name="filename",
            annotation=str,
            type_info=TypeInfo(origin=str, converter=str),
            has_default=False,
            kind=ParameterKind.POSITIONAL_ONLY,
        )

        config = build_argument_config(param)

        assert config.positional is True
        assert config.flags == []

    def test_extract_arg_from_annotated(self) -> None:
        """Test extraction of Arg from Annotated type annotation."""
        func_info = FunctionInfo(
            name="greet",
            qualname="greet",
            parameters=[
                ParameterInfo(
                    name="name",
                    annotation=Annotated[str, Arg(short="-n", help="The name")],
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
            ],
        )

        config = build_parser_config(func_info)

        assert config.arguments[0].flags == ["-n", "--name"]
        assert config.arguments[0].help == "The name"

    def test_skip_parameter_via_annotated(self) -> None:
        """Test skipping parameter via Annotated Arg(skip=True)."""
        func_info = FunctionInfo(
            name="process",
            qualname="process",
            parameters=[
                ParameterInfo(
                    name="visible",
                    annotation=str,
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
                ParameterInfo(
                    name="internal",
                    annotation=Annotated[str, Arg(skip=True)],
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
            ],
        )

        config = build_parser_config(func_info)

        assert len(config.arguments) == 1
        assert config.arguments[0].name == "visible"

    def test_description_sentence_extraction(self) -> None:
        """Test that long first paragraph is truncated to first sentence."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            description="This is the first sentence. This is more detail that should be excluded.",
        )

        config = build_parser_config(func_info)

        assert config.description == "This is the first sentence."

    def test_no_description(self) -> None:
        """Test building parser config with no description."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            description=None,
        )

        config = build_parser_config(func_info)

        assert config.description is None


class TestBuildParserConfig:
    """Tests for build_parser_config function."""

    def test_simple_function(self) -> None:
        """Test building parser config for simple function."""
        func_info = FunctionInfo(
            name="greet",
            qualname="greet",
            description="Greet someone.",
            parameters=[
                ParameterInfo(
                    name="name",
                    annotation=str,
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
            ],
        )

        config = build_parser_config(func_info)

        assert config.description == "Greet someone."
        assert len(config.arguments) == 1
        assert config.arguments[0].name == "name"

    def test_multiple_parameters(self) -> None:
        """Test building parser config with multiple parameters."""
        func_info = FunctionInfo(
            name="process",
            qualname="process",
            parameters=[
                ParameterInfo(
                    name="input_file",
                    annotation=str,
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
                ParameterInfo(
                    name="output_file",
                    annotation=str,
                    type_info=TypeInfo(origin=str, converter=str),
                    has_default=False,
                ),
                ParameterInfo(
                    name="verbose",
                    annotation=bool,
                    type_info=TypeInfo(origin=bool, converter=bool),
                    default=False,
                    has_default=True,
                ),
            ],
        )

        config = build_parser_config(func_info)

        assert len(config.arguments) == 3

    def test_skip_var_args(self) -> None:
        """Test that *args is skipped."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            parameters=[
                ParameterInfo(
                    name="args",
                    kind=ParameterKind.VAR_POSITIONAL,
                ),
            ],
        )

        config = build_parser_config(func_info)

        assert len(config.arguments) == 0

    def test_skip_var_kwargs(self) -> None:
        """Test that **kwargs is skipped."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            parameters=[
                ParameterInfo(
                    name="kwargs",
                    kind=ParameterKind.VAR_KEYWORD,
                ),
            ],
        )

        config = build_parser_config(func_info)

        assert len(config.arguments) == 0

    def test_custom_prog(self) -> None:
        """Test building parser config with custom prog."""
        func_info = FunctionInfo(name="func", qualname="func")

        config = build_parser_config(func_info, prog="myapp")

        assert config.prog == "myapp"

    def test_custom_description(self) -> None:
        """Test building parser config with custom description."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            description="Original description.",
        )

        config = build_parser_config(func_info, description="Custom description.")

        assert config.description == "Custom description."

    def test_multiline_description_truncation(self) -> None:
        """Test that multiline descriptions are truncated to first paragraph."""
        func_info = FunctionInfo(
            name="func",
            qualname="func",
            description="First paragraph.\n\nSecond paragraph with more details.",
        )

        config = build_parser_config(func_info)

        assert config.description == "First paragraph."
