"""Plugin registry and discovery for wArgs.

This module provides functionality for discovering and loading plugins
via entry points.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points  # pragma: no cover

if TYPE_CHECKING:
    from wargs.converters.registry import ConverterRegistry


class PluginError(Exception):
    """Error loading or executing a plugin."""

    pass


class PluginRegistry:
    """Registry for managing wArgs plugins.

    Discovers and loads plugins from entry points.

    Entry point groups:
        - wargs.converters: Type converter plugins
        - wargs.hooks: Pre/post processing hooks (future)
        - wargs.formatters: Custom help formatters (future)
    """

    def __init__(self) -> None:
        """Initialize the plugin registry."""
        self._loaded_plugins: dict[str, list[str]] = {}
        self._failed_plugins: dict[str, list[tuple[str, str]]] = {}

    def load_converters(
        self,
        converter_registry: ConverterRegistry,
        *,
        group: str = "wargs.converters",
        raise_on_error: bool = False,
    ) -> int:
        """Load converter plugins from entry points.

        Args:
            converter_registry: The converter registry to register on.
            group: The entry point group name.
            raise_on_error: If True, raise PluginError on load failure.

        Returns:
            Number of plugins successfully loaded.

        Raises:
            PluginError: If raise_on_error is True and a plugin fails to load.
        """
        if group in self._loaded_plugins:
            # Already loaded
            return len(self._loaded_plugins[group])

        self._loaded_plugins[group] = []
        self._failed_plugins[group] = []

        eps = entry_points(group=group)
        count = 0

        for ep in eps:
            try:
                register_func = ep.load()
                register_func(converter_registry)
                self._loaded_plugins[group].append(ep.name)
                count += 1
            except Exception as e:
                error_msg = f"{type(e).__name__}: {e}"
                self._failed_plugins[group].append((ep.name, error_msg))
                if raise_on_error:
                    raise PluginError(
                        f"Failed to load plugin '{ep.name}' from group '{group}': {e}"
                    ) from e

        return count

    def get_loaded_plugins(self, group: str) -> list[str]:
        """Get list of successfully loaded plugins for a group.

        Args:
            group: The entry point group name.

        Returns:
            List of plugin names that were successfully loaded.
        """
        return self._loaded_plugins.get(group, [])

    def get_failed_plugins(self, group: str) -> list[tuple[str, str]]:
        """Get list of plugins that failed to load.

        Args:
            group: The entry point group name.

        Returns:
            List of (plugin_name, error_message) tuples.
        """
        return self._failed_plugins.get(group, [])

    def is_loaded(self, group: str) -> bool:
        """Check if plugins for a group have been loaded.

        Args:
            group: The entry point group name.

        Returns:
            True if load_converters() has been called for this group.
        """
        return group in self._loaded_plugins

    def clear(self) -> None:
        """Clear all loaded plugin state.

        This allows plugins to be reloaded on the next call.
        """
        self._loaded_plugins.clear()
        self._failed_plugins.clear()


def discover_entry_points(group: str) -> list[dict[str, Any]]:
    """Discover available entry points for a group.

    Args:
        group: The entry point group name.

    Returns:
        List of entry point info dictionaries with keys:
        - name: The entry point name
        - value: The entry point value (module:attr)
        - group: The entry point group
    """
    eps = entry_points(group=group)
    return [
        {
            "name": ep.name,
            "value": ep.value,
            "group": group,
        }
        for ep in eps
    ]


# Global plugin registry
_plugin_registry: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry.

    Returns:
        The global PluginRegistry instance.
    """
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
    return _plugin_registry


__all__ = [
    "PluginError",
    "PluginRegistry",
    "discover_entry_points",
    "get_plugin_registry",
]
