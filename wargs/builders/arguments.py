"""Argument configuration builder for wArgs.

Converts ParameterInfo to ArgumentConfig for argparse.
"""

from __future__ import annotations

from typing import Any, get_args, get_origin

from wArgs.core.arg import Arg
from wArgs.core.config import (
    MISSING,
    ArgumentConfig,
    DictExpansion,
    FunctionInfo,
    ParameterInfo,
    ParameterKind,
    ParserConfig,
    TypeInfo,
)

# Check for Annotated support (Python 3.9+)
try:
    from typing import Annotated
except ImportError:  # pragma: no cover
    from typing_extensions import Annotated  # pragma: no cover


def _extract_arg_metadata(annotation: Any) -> Arg | None:
    """Extract Arg metadata from an Annotated type.

    Args:
        annotation: The type annotation to check.

    Returns:
        Arg metadata if found, None otherwise.
    """
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        for arg in args[1:]:  # Skip the first arg (actual type)
            if isinstance(arg, Arg):
                return arg
    return None


def _param_to_flag(name: str, prefix: str | None = None) -> str:
    """Convert a parameter name to a CLI flag.

    Converts snake_case to kebab-case with -- prefix.

    Args:
        name: The parameter name.
        prefix: Optional prefix (callable name) to add before the param name.

    Returns:
        The CLI flag (e.g., "--my-param" or "--func-my-param").
    """
    # Convert underscores to hyphens
    flag_name = name.replace("_", "-")
    if prefix:
        prefix_kebab = prefix.replace("_", "-")
        return f"--{prefix_kebab}-{flag_name}"
    return f"--{flag_name}"


def _get_type_action(type_info: TypeInfo | None) -> tuple[str | None, Any]:
    """Determine argparse action and type from TypeInfo.

    Args:
        type_info: Resolved type information.

    Returns:
        Tuple of (action, type_converter).
    """
    if type_info is None:
        return None, str

    # Boolean types use store_true/store_false
    if type_info.origin is bool:
        return "store_true", None

    # For other types, use the converter
    return None, type_info.converter


def _get_nargs(
    type_info: TypeInfo | None, param_kind: ParameterKind
) -> str | int | None:
    """Determine nargs value from type info.

    Args:
        type_info: Resolved type information.
        param_kind: The parameter kind.

    Returns:
        nargs value for argparse.
    """
    if type_info is None:
        return None

    # Collection types need nargs
    if type_info.origin in (list, set, frozenset):
        return "*"
    elif type_info.origin is tuple:
        # For tuple, use the number of type args
        if type_info.args and type_info.args[-1] is not ...:
            return len(type_info.args)
        return "*"

    # *args parameter
    if param_kind == ParameterKind.VAR_POSITIONAL:
        return "*"

    return None


def _get_choices(type_info: TypeInfo | None) -> list[Any] | None:
    """Extract choices from type info.

    Args:
        type_info: Resolved type information.

    Returns:
        List of choices or None.
    """
    if type_info is None:
        return None

    # Literal types become choices
    if type_info.is_literal and type_info.literal_values:
        return list(type_info.literal_values)

    # Note: Enums don't use choices because argparse validates choices
    # AFTER type conversion, which breaks enum converters. Instead,
    # we use metavar to display valid options and let the converter validate.

    return None


def _get_enum_metavar(type_info: TypeInfo | None) -> str | None:
    """Get metavar for enum types to display valid options.

    Args:
        type_info: Resolved type information.

    Returns:
        Metavar string like "{RED,GREEN,BLUE}" or None.
    """
    if type_info is None:
        return None

    if type_info.is_enum and type_info.enum_class is not None:
        names = [member.name for member in type_info.enum_class]
        return "{" + ",".join(names) + "}"

    return None


def _format_default_help(default: Any, has_default: bool) -> str:
    """Format default value for help text.

    Args:
        default: The default value.
        has_default: Whether there is a default.

    Returns:
        Formatted string like "(default: value)".
    """
    if not has_default or default is MISSING:
        return ""

    if default is None:
        return ""

    if isinstance(default, str):
        return f" (default: {default!r})"

    return f" (default: {default})"


def build_argument_config(
    param: ParameterInfo,
    *,
    arg_metadata: Arg | None = None,
    prefix: str | None = None,
) -> ArgumentConfig:
    """Build ArgumentConfig from ParameterInfo.

    Args:
        param: The parameter information.
        arg_metadata: Optional Arg metadata from Annotated.
        prefix: Optional prefix (callable name) for the flag.

    Returns:
        ArgumentConfig for this parameter.
    """
    # Check for skip
    if arg_metadata and arg_metadata.skip:
        return ArgumentConfig(
            name=param.name,
            skip=True,
        )

    # Determine if positional
    is_positional = (
        arg_metadata and arg_metadata.positional
    ) or param.kind == ParameterKind.POSITIONAL_ONLY

    # Build flags
    flags: list[str] = []
    if not is_positional:
        # Add long flag
        if arg_metadata and arg_metadata.long:
            flags.append(arg_metadata.long)
        else:
            flags.append(_param_to_flag(param.name, prefix=prefix))

        # Add short flag
        if arg_metadata and arg_metadata.short:
            flags.insert(0, arg_metadata.short)

    # Determine type and action
    action, type_converter = _get_type_action(param.type_info)

    # Override with Arg metadata
    if arg_metadata and arg_metadata.action:
        action = arg_metadata.action
        # Actions like store_true/store_false don't need type
        if action in ("store_true", "store_false", "store_const", "count"):
            type_converter = None

    # Determine nargs
    nargs = _get_nargs(param.type_info, param.kind)
    if arg_metadata and arg_metadata.nargs is not None:
        nargs = arg_metadata.nargs

    # Determine choices
    choices = _get_choices(param.type_info)
    if arg_metadata and arg_metadata.choices is not None:
        choices = arg_metadata.choices

    # Determine required
    required = not param.has_default and not is_positional
    if arg_metadata and arg_metadata.required is not None:
        required = arg_metadata.required

    # Determine default
    default = param.default if param.has_default else None
    if arg_metadata and arg_metadata.default is not None:
        default = arg_metadata.default

    # Build help text
    help_text = param.description or ""
    if arg_metadata and arg_metadata.help:
        help_text = arg_metadata.help

    # Add default to help if not already there
    if help_text and param.has_default:
        default_suffix = _format_default_help(param.default, param.has_default)
        if default_suffix and default_suffix not in help_text:
            help_text = f"{help_text}{default_suffix}"

    # Determine metavar
    metavar = None
    if arg_metadata and arg_metadata.metavar:
        metavar = arg_metadata.metavar
    elif param.type_info:
        # Use enum metavar if this is an enum type
        metavar = _get_enum_metavar(param.type_info)

    # Determine dest
    # When using prefixed flags, always set dest to param.name so argparse
    # stores values under the original parameter name, not the prefixed flag name
    dest = param.name if prefix else None
    if arg_metadata and arg_metadata.dest:
        dest = arg_metadata.dest

    # Determine group info
    group = arg_metadata.group if arg_metadata else None
    mutually_exclusive = arg_metadata.mutually_exclusive if arg_metadata else None

    # Determine hidden
    hidden = arg_metadata.hidden if arg_metadata else False

    return ArgumentConfig(
        name=param.name,
        flags=flags,
        type=type_converter,
        default=default,
        required=required,
        help=help_text if help_text else None,
        choices=choices,
        action=action,
        nargs=nargs,
        metavar=metavar,
        dest=dest,
        group=group,
        mutually_exclusive=mutually_exclusive,
        positional=is_positional,
        hidden=hidden,
        skip=False,
    )


def _infer_type_converter(value: Any) -> type | None:
    """Infer a type converter from a value.

    Args:
        value: The value to infer type from.

    Returns:
        Type converter function or None.
    """
    if value is None:
        return str
    return type(value)


def _expand_dict_param(
    param: ParameterInfo,
    default_dict: dict[str, Any],
    prefix: str | None = None,
) -> tuple[list[ArgumentConfig], DictExpansion]:
    """Expand a dict parameter into multiple CLI arguments.

    Args:
        param: The parameter with a dict default.
        default_dict: The default dict value.
        prefix: Optional prefix (callable name) for the flags.

    Returns:
        Tuple of (list of ArgumentConfigs, DictExpansion metadata).
    """
    arguments: list[ArgumentConfig] = []
    keys: list[str] = []
    key_types: dict[str, type] = {}

    for key, value in default_dict.items():
        keys.append(key)
        value_type = _infer_type_converter(value)
        key_types[key] = value_type if value_type else str

        # Create expanded argument name: param_key
        expanded_name = f"{param.name}_{key}"
        # Create flag: --[prefix-]param-key
        param_kebab = param.name.replace("_", "-")
        key_kebab = key.replace("_", "-")
        if prefix:
            prefix_kebab = prefix.replace("_", "-")
            flag = f"--{prefix_kebab}-{param_kebab}-{key_kebab}"
        else:
            flag = f"--{param_kebab}-{key_kebab}"

        # Build help text
        help_text = f"{param.name}[{key!r}]"
        if param.description:
            help_text = f"{param.description} [{key}]"
        help_text += f" (default: {value!r})"

        arg_config = ArgumentConfig(
            name=expanded_name,
            flags=[flag],
            type=value_type,
            default=value,
            required=False,
            help=help_text,
            dest=expanded_name,  # Ensure argparse uses the expanded name as dest
        )
        arguments.append(arg_config)

    expansion = DictExpansion(
        param_name=param.name,
        keys=keys,
        key_types=key_types,
        default_dict=dict(default_dict),
    )

    return arguments, expansion


def build_parser_config(
    func_info: FunctionInfo,
    *,
    prog: str | None = None,
    description: str | None = None,
    prefix: str | None = None,
) -> ParserConfig:
    """Build ParserConfig from FunctionInfo.

    Args:
        func_info: The function information.
        prog: Program name override.
        description: Description override.
        prefix: Optional prefix for argument flags. If None, uses func_info.name.

    Returns:
        ParserConfig for building an ArgumentParser.
    """
    # Get description from function docstring if not overridden
    desc = description if description is not None else func_info.description

    # Extract first line/sentence as description
    if desc:
        # Take first paragraph
        first_para = desc.split("\n\n")[0]
        # Take first sentence if it's reasonable length
        if ". " in first_para and len(first_para.split(". ")[0]) < 200:
            desc = first_para.split(". ")[0] + "."
        else:
            desc = first_para.strip()

    # Use provided prefix for argument flags (None = no prefix)
    arg_prefix = prefix

    # Build argument configs
    arguments: list[ArgumentConfig] = []
    dict_expansions: dict[str, DictExpansion] = {}

    for param in func_info.parameters:
        # Skip *args and **kwargs for now (handled specially)
        if param.kind in (ParameterKind.VAR_POSITIONAL, ParameterKind.VAR_KEYWORD):
            continue

        # Check if this param has a dict default that should be expanded
        if (
            param.has_default
            and isinstance(param.default, dict)
            and param.default  # Non-empty dict
            and all(isinstance(k, str) for k in param.default.keys())
        ):
            # Expand dict into multiple arguments
            expanded_args, expansion = _expand_dict_param(
                param, param.default, prefix=arg_prefix
            )
            arguments.extend(expanded_args)
            dict_expansions[param.name] = expansion
            continue

        # Extract Arg metadata from annotation
        arg_metadata = _extract_arg_metadata(param.annotation)

        arg_config = build_argument_config(
            param, arg_metadata=arg_metadata, prefix=arg_prefix
        )

        # Skip if marked to skip
        if not arg_config.skip:
            arguments.append(arg_config)

    return ParserConfig(
        prog=prog,
        description=desc,
        arguments=arguments,
        dict_expansions=dict_expansions,
    )


__all__ = [
    "build_argument_config",
    "build_parser_config",
]
