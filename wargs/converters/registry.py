"""Converter registry for custom type converters.

This module provides a central registry for registering and looking up
type converters used to convert command-line string arguments to Python types.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, TypeVar

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points  # pragma: no cover

T = TypeVar("T")

# Type alias for converter functions
Converter = Callable[[str], Any]


class ConverterRegistry:
    """Registry for type converters.

    Converters are functions that take a string and return a typed value.
    The registry supports:
    - Explicit registration via register() or @converter decorator
    - Inheritance-based lookup (if no exact match, check base classes)
    - Entry point discovery for plugins

    Example:
        registry = ConverterRegistry()

        @registry.converter(MyClass)
        def convert_myclass(value: str) -> MyClass:
            return MyClass.from_string(value)

        # Or register directly
        registry.register(MyClass, MyClass.from_string)

        # Lookup
        converter = registry.get(MyClass)
        result = converter("some value")
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._converters: dict[type, Converter] = {}
        self._plugins_loaded = False

    def register(self, type_: type, converter: Converter) -> None:
        """Register a converter for a type.

        If a converter is already registered for this type, it will be
        replaced (last-wins semantics).

        Args:
            type_: The type to register the converter for.
            converter: A callable that takes a string and returns the type.
        """
        self._converters[type_] = converter

    def converter(
        self, type_: type[T]
    ) -> Callable[[Callable[[str], T]], Callable[[str], T]]:
        """Decorator to register a converter function.

        Args:
            type_: The type to register the converter for.

        Returns:
            A decorator that registers the function.

        Example:
            @registry.converter(MyClass)
            def convert_myclass(value: str) -> MyClass:
                return MyClass(value)
        """

        def decorator(func: Callable[[str], T]) -> Callable[[str], T]:
            self.register(type_, func)
            return func

        return decorator

    def get(self, type_: type, *, check_inheritance: bool = True) -> Converter | None:
        """Look up a converter for a type.

        Args:
            type_: The type to look up.
            check_inheritance: If True, check base classes if no exact match.

        Returns:
            The converter function, or None if not found.
        """
        # Exact match first
        if type_ in self._converters:
            return self._converters[type_]

        # Check inheritance chain
        if check_inheritance:
            for base in type_.__mro__[1:]:  # Skip the type itself
                if base in self._converters:
                    return self._converters[base]

        return None

    def has(self, type_: type) -> bool:
        """Check if a converter is registered for a type.

        Args:
            type_: The type to check.

        Returns:
            True if a converter is registered (including via inheritance).
        """
        return self.get(type_) is not None

    def unregister(self, type_: type) -> bool:
        """Remove a converter registration.

        Args:
            type_: The type to unregister.

        Returns:
            True if a converter was removed, False if none was registered.
        """
        if type_ in self._converters:
            del self._converters[type_]
            return True
        return False

    def clear(self) -> None:
        """Remove all registered converters."""
        self._converters.clear()
        self._plugins_loaded = False

    def load_entry_points(self, group: str = "wargs.converters") -> int:
        """Load converters from entry points.

        Entry points should be functions that take a ConverterRegistry
        and register converters on it.

        Args:
            group: The entry point group name.

        Returns:
            Number of entry points loaded.

        Example pyproject.toml:
            [project.entry-points."wargs.converters"]
            mypackage = "mypackage.converters:register_converters"

        Example register function:
            def register_converters(registry: ConverterRegistry) -> None:
                @registry.converter(MyType)
                def convert_mytype(value: str) -> MyType:
                    return MyType(value)
        """
        if self._plugins_loaded:
            return 0

        count = 0
        eps = entry_points(group=group)

        for ep in eps:
            try:
                register_func = ep.load()
                register_func(self)
                count += 1
            except Exception:
                # Silently skip failed entry points
                # In a production system, we might want to log this
                pass

        self._plugins_loaded = True
        return count

    def registered_types(self) -> list[type]:
        """Get all types with registered converters.

        Returns:
            List of registered types.
        """
        return list(self._converters.keys())

    def __len__(self) -> int:
        """Return the number of registered converters."""
        return len(self._converters)

    def __contains__(self, type_: type) -> bool:
        """Check if a type has a registered converter."""
        return type_ in self._converters

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ConverterRegistry({len(self._converters)} converters)>"


# Global default registry
_default_registry: ConverterRegistry | None = None


def get_default_registry() -> ConverterRegistry:
    """Get the default global converter registry.

    Returns:
        The default ConverterRegistry instance.
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = ConverterRegistry()
    return _default_registry


def converter(type_: type[T]) -> Callable[[Callable[[str], T]], Callable[[str], T]]:
    """Decorator to register a converter on the default registry.

    This is a convenience function that delegates to the default registry.

    Args:
        type_: The type to register the converter for.

    Returns:
        A decorator that registers the function.

    Example:
        from wargs import converter

        @converter(MyClass)
        def convert_myclass(value: str) -> MyClass:
            return MyClass(value)
    """
    return get_default_registry().converter(type_)


__all__ = [
    "Converter",
    "ConverterRegistry",
    "converter",
    "get_default_registry",
]
