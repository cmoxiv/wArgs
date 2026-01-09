"""Plugin interface definitions for wArgs.

This module defines the protocols and interfaces that plugins must implement
to extend wArgs functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from wArgs.converters.registry import ConverterRegistry


@runtime_checkable
class ConverterPlugin(Protocol):
    """Protocol for converter plugins.

    Converter plugins are discovered via entry points and called to
    register custom type converters.

    Entry point group: wargs.converters

    Example pyproject.toml:
        [project.entry-points."wargs.converters"]
        mypackage = "mypackage.converters:register"

    Example implementation:
        def register(registry: ConverterRegistry) -> None:
            @registry.converter(MyType)
            def convert_mytype(value: str) -> MyType:
                return MyType.parse(value)
    """

    def __call__(self, registry: ConverterRegistry) -> None:
        """Register converters on the provided registry.

        Args:
            registry: The converter registry to register on.
        """
        ...


__all__ = [
    "ConverterPlugin",
]
