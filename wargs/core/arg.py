"""Arg metadata class for parameter annotations.

Use with typing.Annotated to configure CLI argument behavior:

    from typing import Annotated
    from wargs import Arg

    def greet(
        name: str,
        count: Annotated[int, Arg("-c", help="Number of greetings")] = 1,
    ) -> None:
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Arg:
    """Metadata for configuring a CLI argument.

    Use with typing.Annotated to customize argument behavior.

    Attributes:
        short: Short flag (e.g., "-n").
        long: Long flag override (default: "--{param_name}").
        help: Help text for the argument.
        metavar: Placeholder in help text.
        choices: List of valid choices.
        action: argparse action (e.g., "store_true", "count").
        nargs: Number of arguments.
        const: Constant value for certain actions.
        default: Default value override.
        required: Override required status.
        dest: Destination attribute name.
        group: Argument group name.
        mutually_exclusive: Mutually exclusive group name.
        positional: Make this a positional argument.
        hidden: Hide from help output.
        skip: Skip this parameter entirely.
        envvar: Environment variable to read default from.
    """

    short: str | None = None
    long: str | None = None
    help: str | None = None
    metavar: str | None = None
    choices: list[Any] | None = None
    action: str | None = None
    nargs: str | int | None = None
    const: Any = None
    default: Any = field(default=None, repr=False)
    required: bool | None = None
    dest: str | None = None
    group: str | None = None
    mutually_exclusive: str | None = None
    positional: bool = False
    hidden: bool = False
    skip: bool = False
    envvar: str | None = None

    def __post_init__(self) -> None:
        """Validate Arg configuration."""
        # Validate short flag format
        if self.short is not None:
            if not self.short.startswith("-") or self.short.startswith("--"):
                raise ValueError(
                    f"Short flag must start with single dash: {self.short!r}"
                )
            if len(self.short) != 2:
                raise ValueError(
                    f"Short flag must be exactly 2 characters: {self.short!r}"
                )

        # Validate long flag format
        if self.long is not None and not self.long.startswith("--"):
            raise ValueError(f"Long flag must start with double dash: {self.long!r}")

        # Positional arguments can't have flags
        if self.positional and (self.short or self.long):
            raise ValueError("Positional arguments cannot have flags")

        # Hidden and positional are mutually exclusive
        if self.hidden and self.positional:
            raise ValueError("Positional arguments cannot be hidden")


__all__ = ["Arg"]
