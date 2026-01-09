"""Unit tests for ConverterRegistry."""

from __future__ import annotations

from wargs.converters.registry import (
    ConverterRegistry,
    converter,
    get_default_registry,
)


class TestConverterRegistry:
    """Tests for ConverterRegistry class."""

    def test_register_and_get(self) -> None:
        """Test registering and retrieving a converter."""
        registry = ConverterRegistry()

        def my_converter(s: str) -> int:
            return int(s) * 2

        registry.register(int, my_converter)
        result = registry.get(int)

        assert result is my_converter
        assert result("5") == 10

    def test_last_wins(self) -> None:
        """Test that registering twice replaces the first converter."""
        registry = ConverterRegistry()

        def first(s: str) -> int:
            return 1

        def second(s: str) -> int:
            return 2

        registry.register(int, first)
        registry.register(int, second)

        result = registry.get(int)
        assert result is second

    def test_get_nonexistent(self) -> None:
        """Test getting a converter that doesn't exist."""
        registry = ConverterRegistry()
        result = registry.get(str)
        assert result is None

    def test_inheritance_lookup(self) -> None:
        """Test that converters are found via inheritance."""
        registry = ConverterRegistry()

        class Base:
            pass

        class Child(Base):
            pass

        def base_converter(s: str) -> Base:
            return Base()

        registry.register(Base, base_converter)

        # Child should find parent's converter
        result = registry.get(Child)
        assert result is base_converter

    def test_inheritance_lookup_disabled(self) -> None:
        """Test that inheritance lookup can be disabled."""
        registry = ConverterRegistry()

        class Base:
            pass

        class Child(Base):
            pass

        def base_converter(s: str) -> Base:
            return Base()

        registry.register(Base, base_converter)

        # Child should NOT find parent's converter with check_inheritance=False
        result = registry.get(Child, check_inheritance=False)
        assert result is None

    def test_has(self) -> None:
        """Test has() method."""
        registry = ConverterRegistry()
        registry.register(int, int)

        assert registry.has(int)
        assert not registry.has(str)

    def test_unregister(self) -> None:
        """Test unregistering a converter."""
        registry = ConverterRegistry()
        registry.register(int, int)

        assert registry.unregister(int) is True
        assert registry.get(int) is None
        assert registry.unregister(int) is False  # Already removed

    def test_clear(self) -> None:
        """Test clearing all converters."""
        registry = ConverterRegistry()
        registry.register(int, int)
        registry.register(str, str)

        registry.clear()

        assert len(registry) == 0
        assert registry.get(int) is None

    def test_len(self) -> None:
        """Test __len__ method."""
        registry = ConverterRegistry()
        assert len(registry) == 0

        registry.register(int, int)
        assert len(registry) == 1

        registry.register(str, str)
        assert len(registry) == 2

    def test_contains(self) -> None:
        """Test __contains__ method."""
        registry = ConverterRegistry()
        registry.register(int, int)

        assert int in registry
        assert str not in registry

    def test_registered_types(self) -> None:
        """Test registered_types() method."""
        registry = ConverterRegistry()
        registry.register(int, int)
        registry.register(str, str)

        types = registry.registered_types()
        assert int in types
        assert str in types
        assert len(types) == 2

    def test_repr(self) -> None:
        """Test __repr__ method."""
        registry = ConverterRegistry()
        registry.register(int, int)

        result = repr(registry)
        assert "ConverterRegistry" in result
        assert "1" in result


class TestConverterDecorator:
    """Tests for the @converter decorator."""

    def test_converter_decorator_on_registry(self) -> None:
        """Test using @registry.converter() decorator."""
        registry = ConverterRegistry()

        @registry.converter(int)
        def double_int(s: str) -> int:
            return int(s) * 2

        result = registry.get(int)
        assert result is double_int
        assert result("5") == 10

    def test_global_converter_decorator(self) -> None:
        """Test using global @converter() decorator."""
        # Get a fresh registry
        registry = get_default_registry()
        registry.clear()

        @converter(float)
        def my_float(s: str) -> float:
            return float(s) + 0.5

        result = registry.get(float)
        assert result is my_float
        assert result("1.0") == 1.5

        # Clean up
        registry.unregister(float)


class TestDefaultRegistry:
    """Tests for the default registry singleton."""

    def test_get_default_registry_singleton(self) -> None:
        """Test that get_default_registry returns same instance."""
        r1 = get_default_registry()
        r2 = get_default_registry()
        assert r1 is r2

    def test_default_registry_is_converter_registry(self) -> None:
        """Test that default registry is a ConverterRegistry."""
        registry = get_default_registry()
        assert isinstance(registry, ConverterRegistry)


class TestLoadEntryPoints:
    """Tests for entry point loading."""

    def test_load_entry_points_empty(self) -> None:
        """Test load_entry_points with no plugins."""
        from unittest.mock import patch

        registry = ConverterRegistry()

        with patch("wargs.converters.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            count = registry.load_entry_points()

        assert count == 0

    def test_load_entry_points_only_once(self) -> None:
        """Test that load_entry_points only loads once."""
        from unittest.mock import patch

        registry = ConverterRegistry()

        with patch("wargs.converters.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            count1 = registry.load_entry_points()
            count2 = registry.load_entry_points()

        assert count1 == 0
        assert count2 == 0  # Returns 0 because already loaded
        mock_eps.assert_called_once()  # Only called once

    def test_load_entry_points_success(self) -> None:
        """Test successful entry point loading."""
        from unittest.mock import MagicMock, patch

        registry = ConverterRegistry()

        # Create mock entry point
        mock_ep = MagicMock()
        mock_ep.load.return_value = lambda r: r.register(int, lambda x: int(x) * 2)

        with patch("wargs.converters.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            count = registry.load_entry_points()

        assert count == 1
        assert registry.has(int)
        assert registry.get(int)("5") == 10

    def test_load_entry_points_failure_silent(self) -> None:
        """Test that entry point failures are silently ignored."""
        from unittest.mock import MagicMock, patch

        registry = ConverterRegistry()

        mock_ep = MagicMock()
        mock_ep.load.side_effect = ImportError("Module not found")

        with patch("wargs.converters.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            count = registry.load_entry_points()

        # Should return 0 since loading failed
        assert count == 0

    def test_load_entry_points_custom_group(self) -> None:
        """Test loading from a custom group."""
        from unittest.mock import MagicMock, patch

        registry = ConverterRegistry()

        mock_ep = MagicMock()
        mock_ep.load.return_value = lambda r: None

        with patch("wargs.converters.registry.entry_points") as mock_eps:
            mock_eps.return_value = [mock_ep]
            count = registry.load_entry_points(group="custom.group")

        assert count == 1
        mock_eps.assert_called_once_with(group="custom.group")

    def test_clear_resets_plugins_loaded(self) -> None:
        """Test that clear() resets the plugins_loaded flag."""
        from unittest.mock import patch

        registry = ConverterRegistry()

        with patch("wargs.converters.registry.entry_points") as mock_eps:
            mock_eps.return_value = []
            registry.load_entry_points()
            assert registry._plugins_loaded is True

            registry.clear()
            assert registry._plugins_loaded is False

            # Can load again after clear
            registry.load_entry_points()
            assert mock_eps.call_count == 2
