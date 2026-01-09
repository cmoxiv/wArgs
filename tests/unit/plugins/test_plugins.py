"""Unit tests for the wArgs plugin system."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from wArgs.converters.registry import ConverterRegistry
from wArgs.plugins import (
    ConverterPlugin,
    PluginError,
    PluginRegistry,
    discover_entry_points,
    get_plugin_registry,
)


class TestConverterPlugin:
    """Tests for the ConverterPlugin protocol."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """Test that ConverterPlugin is runtime checkable."""

        def register_func(registry: ConverterRegistry) -> None:
            pass

        # Functions that match the protocol should be considered instances
        assert isinstance(register_func, ConverterPlugin)

    def test_callable_matches_protocol(self) -> None:
        """Test that a callable with correct signature matches."""

        class MyPlugin:
            def __call__(self, registry: ConverterRegistry) -> None:
                pass

        plugin = MyPlugin()
        assert isinstance(plugin, ConverterPlugin)


class TestPluginRegistry:
    """Tests for the PluginRegistry class."""

    def test_init(self) -> None:
        """Test PluginRegistry initialization."""
        registry = PluginRegistry()
        assert registry._loaded_plugins == {}
        assert registry._failed_plugins == {}

    def test_is_loaded_before_loading(self) -> None:
        """Test is_loaded returns False before loading."""
        registry = PluginRegistry()
        assert registry.is_loaded("wargs.converters") is False

    def test_is_loaded_after_loading(self) -> None:
        """Test is_loaded returns True after loading."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            registry.load_converters(converter_registry)

        assert registry.is_loaded("wargs.converters") is True

    def test_load_converters_empty(self) -> None:
        """Test loading with no entry points."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            count = registry.load_converters(converter_registry)

        assert count == 0
        assert registry.get_loaded_plugins("wargs.converters") == []
        assert registry.get_failed_plugins("wargs.converters") == []

    def test_load_converters_success(self) -> None:
        """Test successful plugin loading."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        mock_ep = MagicMock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = lambda r: None

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            count = registry.load_converters(converter_registry)

        assert count == 1
        assert registry.get_loaded_plugins("wargs.converters") == ["test_plugin"]
        assert registry.get_failed_plugins("wargs.converters") == []

    def test_load_converters_failure_silent(self) -> None:
        """Test plugin loading failure with silent mode."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        mock_ep = MagicMock()
        mock_ep.name = "bad_plugin"
        mock_ep.load.side_effect = ImportError("Module not found")

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            count = registry.load_converters(converter_registry)

        assert count == 0
        assert registry.get_loaded_plugins("wargs.converters") == []
        assert len(registry.get_failed_plugins("wargs.converters")) == 1
        assert "bad_plugin" in registry.get_failed_plugins("wargs.converters")[0][0]

    def test_load_converters_failure_raise(self) -> None:
        """Test plugin loading failure with raise_on_error=True."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        mock_ep = MagicMock()
        mock_ep.name = "bad_plugin"
        mock_ep.load.side_effect = ImportError("Module not found")

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            with pytest.raises(PluginError) as exc_info:
                registry.load_converters(converter_registry, raise_on_error=True)

        assert "bad_plugin" in str(exc_info.value)

    def test_load_converters_already_loaded(self) -> None:
        """Test that plugins are only loaded once per group."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        mock_ep = MagicMock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = lambda r: None

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            count1 = registry.load_converters(converter_registry)
            count2 = registry.load_converters(converter_registry)

        assert count1 == 1
        assert count2 == 1  # Returns cached count
        mock_ep.load.assert_called_once()  # Only loaded once

    def test_load_converters_custom_group(self) -> None:
        """Test loading from a custom group."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            registry.load_converters(converter_registry, group="custom.group")

        assert registry.is_loaded("custom.group")
        assert not registry.is_loaded("wargs.converters")

    def test_clear(self) -> None:
        """Test clearing the registry."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            registry.load_converters(converter_registry)

        assert registry.is_loaded("wargs.converters")

        registry.clear()

        assert not registry.is_loaded("wargs.converters")

    def test_get_loaded_plugins_unknown_group(self) -> None:
        """Test get_loaded_plugins for unknown group."""
        registry = PluginRegistry()
        assert registry.get_loaded_plugins("unknown") == []

    def test_get_failed_plugins_unknown_group(self) -> None:
        """Test get_failed_plugins for unknown group."""
        registry = PluginRegistry()
        assert registry.get_failed_plugins("unknown") == []

    def test_plugin_executes_registration(self) -> None:
        """Test that plugin registration function is actually called."""
        registry = PluginRegistry()
        converter_registry = ConverterRegistry()

        registered_types: list[type] = []

        def mock_register(r: ConverterRegistry) -> None:
            r.register(int, lambda x: int(x) * 2)
            registered_types.append(int)

        mock_ep = MagicMock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = mock_register

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            registry.load_converters(converter_registry)

        assert int in registered_types
        assert converter_registry.has(int)


class TestDiscoverEntryPoints:
    """Tests for the discover_entry_points function."""

    def test_discover_empty(self) -> None:
        """Test discovery with no entry points."""
        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            result = discover_entry_points("wargs.converters")

        assert result == []

    def test_discover_with_entries(self) -> None:
        """Test discovery with entry points."""
        mock_ep1 = MagicMock()
        mock_ep1.name = "plugin1"
        mock_ep1.value = "pkg1.module:register"

        mock_ep2 = MagicMock()
        mock_ep2.name = "plugin2"
        mock_ep2.value = "pkg2.module:register"

        with patch("wArgs.plugins.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep1, mock_ep2]
            result = discover_entry_points("wargs.converters")

        assert len(result) == 2
        assert result[0]["name"] == "plugin1"
        assert result[0]["value"] == "pkg1.module:register"
        assert result[0]["group"] == "wargs.converters"


class TestGetPluginRegistry:
    """Tests for the get_plugin_registry function."""

    def test_returns_registry(self) -> None:
        """Test that get_plugin_registry returns a PluginRegistry."""
        # Reset the global registry
        import wArgs.plugins.registry as reg_module

        reg_module._plugin_registry = None

        registry = get_plugin_registry()
        assert isinstance(registry, PluginRegistry)

    def test_returns_same_instance(self) -> None:
        """Test that get_plugin_registry returns the same instance."""
        registry1 = get_plugin_registry()
        registry2 = get_plugin_registry()
        assert registry1 is registry2


class TestPluginError:
    """Tests for the PluginError exception."""

    def test_plugin_error_message(self) -> None:
        """Test PluginError with message."""
        error = PluginError("Failed to load plugin")
        assert str(error) == "Failed to load plugin"

    def test_plugin_error_is_exception(self) -> None:
        """Test that PluginError is an Exception."""
        assert issubclass(PluginError, Exception)
