"""Plugin system for wArgs.

This module provides plugin discovery and loading via entry points.
"""

from wArgs.plugins.interface import ConverterPlugin
from wArgs.plugins.registry import (
    PluginError,
    PluginRegistry,
    discover_entry_points,
    get_plugin_registry,
)

__all__ = [
    "ConverterPlugin",
    "PluginError",
    "PluginRegistry",
    "discover_entry_points",
    "get_plugin_registry",
]
