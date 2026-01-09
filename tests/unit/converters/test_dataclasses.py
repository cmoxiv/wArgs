"""Unit tests for dataclass expansion."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from wargs.converters.dataclasses import (
    expand_dataclass,
    is_dataclass_type,
    reconstruct_dataclass,
)
from wargs.core.config import ParameterKind


class TestIsDataclassType:
    """Tests for is_dataclass_type function."""

    def test_dataclass(self) -> None:
        """Test that dataclass types are detected."""

        @dataclass
        class Config:
            host: str
            port: int

        assert is_dataclass_type(Config) is True

    def test_regular_class(self) -> None:
        """Test that regular classes are not dataclasses."""

        class NotDataclass:
            pass

        assert is_dataclass_type(NotDataclass) is False

    def test_dataclass_instance(self) -> None:
        """Test that dataclass instances are not types."""

        @dataclass
        class Config:
            host: str

        instance = Config(host="localhost")
        assert is_dataclass_type(instance) is False

    def test_builtin_types(self) -> None:
        """Test that builtin types are not dataclasses."""
        assert is_dataclass_type(int) is False
        assert is_dataclass_type(str) is False
        assert is_dataclass_type(list) is False


class TestExpandDataclass:
    """Tests for expand_dataclass function."""

    def test_basic_expansion(self) -> None:
        """Test basic dataclass expansion."""

        @dataclass
        class Config:
            host: str
            port: int

        params = expand_dataclass("config", Config)

        assert len(params) == 2
        names = [p.name for p in params]
        assert "config-host" in names
        assert "config-port" in names

    def test_expansion_preserves_types(self) -> None:
        """Test that field types are preserved."""

        @dataclass
        class Config:
            name: str
            count: int
            enabled: bool

        params = expand_dataclass("cfg", Config)

        param_dict = {p.name: p for p in params}
        assert param_dict["cfg-name"].annotation is str
        assert param_dict["cfg-count"].annotation is int
        assert param_dict["cfg-enabled"].annotation is bool

    def test_expansion_with_defaults(self) -> None:
        """Test expansion of fields with defaults."""

        @dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080

        params = expand_dataclass("config", Config)

        param_dict = {p.name: p for p in params}
        assert param_dict["config-host"].has_default is True
        assert param_dict["config-host"].default == "localhost"
        assert param_dict["config-port"].has_default is True
        assert param_dict["config-port"].default == 8080

    def test_expansion_with_required_fields(self) -> None:
        """Test expansion of required fields (no default)."""

        @dataclass
        class Config:
            required_field: str
            optional_field: str = "default"

        params = expand_dataclass("config", Config)

        param_dict = {p.name: p for p in params}
        assert param_dict["config-required_field"].has_default is False
        assert param_dict["config-optional_field"].has_default is True

    def test_custom_prefix(self) -> None:
        """Test using a custom prefix."""

        @dataclass
        class Config:
            host: str

        params = expand_dataclass("config", Config, prefix="server")

        assert len(params) == 1
        assert params[0].name == "server-host"

    def test_empty_prefix(self) -> None:
        """Test using an empty prefix."""

        @dataclass
        class Config:
            host: str

        params = expand_dataclass("config", Config, prefix="")

        assert len(params) == 1
        assert params[0].name == "host"

    def test_custom_separator(self) -> None:
        """Test using a custom separator."""

        @dataclass
        class Config:
            host: str

        params = expand_dataclass("config", Config, separator="_")

        assert len(params) == 1
        assert params[0].name == "config_host"

    def test_skips_init_false_fields(self) -> None:
        """Test that init=False fields are skipped."""

        @dataclass
        class Config:
            host: str
            internal: str = field(init=False, default="internal")

        params = expand_dataclass("config", Config)

        assert len(params) == 1
        assert params[0].name == "config-host"

    def test_raises_for_non_dataclass(self) -> None:
        """Test that non-dataclass raises TypeError."""

        class NotDataclass:
            pass

        with pytest.raises(TypeError):
            expand_dataclass("config", NotDataclass)

    def test_parameter_kind(self) -> None:
        """Test that expanded parameters are KEYWORD_ONLY."""

        @dataclass
        class Config:
            host: str

        params = expand_dataclass("config", Config)
        assert params[0].kind == ParameterKind.KEYWORD_ONLY


class TestReconstructDataclass:
    """Tests for reconstruct_dataclass function."""

    def test_basic_reconstruction(self) -> None:
        """Test basic dataclass reconstruction."""

        @dataclass
        class Config:
            host: str
            port: int

        values = {"config-host": "localhost", "config-port": 8080}
        result = reconstruct_dataclass(Config, values, "config")

        assert isinstance(result, Config)
        assert result.host == "localhost"
        assert result.port == 8080

    def test_reconstruction_with_defaults(self) -> None:
        """Test reconstruction uses defaults for missing values."""

        @dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080

        values = {"config-host": "example.com"}  # port not provided
        result = reconstruct_dataclass(Config, values, "config")

        assert result.host == "example.com"
        assert result.port == 8080  # default value

    def test_reconstruction_with_none_values(self) -> None:
        """Test that None values are skipped."""

        @dataclass
        class Config:
            host: str = "localhost"
            port: int = 8080

        values = {"config-host": None, "config-port": 9000}
        result = reconstruct_dataclass(Config, values, "config")

        assert result.host == "localhost"  # default, since None was skipped
        assert result.port == 9000

    def test_reconstruction_with_custom_separator(self) -> None:
        """Test reconstruction with custom separator."""

        @dataclass
        class Config:
            host: str

        values = {"config_host": "localhost"}
        result = reconstruct_dataclass(Config, values, "config", separator="_")

        assert result.host == "localhost"

    def test_raises_for_non_dataclass(self) -> None:
        """Test that non-dataclass raises TypeError."""

        class NotDataclass:
            pass

        with pytest.raises(TypeError):
            reconstruct_dataclass(NotDataclass, {}, "config")


class TestDataclassIntegration:
    """Integration tests for dataclass expansion and reconstruction."""

    def test_roundtrip(self) -> None:
        """Test that expand and reconstruct work together."""

        @dataclass
        class ServerConfig:
            host: str = "localhost"
            port: int = 8080
            debug: bool = False

        # Expand
        expand_dataclass("server", ServerConfig)

        # Simulate CLI values
        values = {
            "server-host": "example.com",
            "server-port": 9000,
            "server-debug": True,
        }

        # Reconstruct
        result = reconstruct_dataclass(ServerConfig, values, "server")

        assert result.host == "example.com"
        assert result.port == 9000
        assert result.debug is True

    def test_nested_dataclass(self) -> None:
        """Test that nested dataclasses are detected correctly."""

        @dataclass
        class Inner:
            value: int

        @dataclass
        class Outer:
            inner: Inner  # Nested dataclass field

        # This should expand, but the inner field will need special handling
        params = expand_dataclass("outer", Outer)

        assert len(params) == 1
        assert params[0].name == "outer-inner"
        # The annotation should be the Inner dataclass type
        # (may be string due to PEP 563 annotations)
        assert params[0].annotation is Inner or params[0].annotation == "Inner"


class TestDataclassCoverageGaps:
    """Additional tests for coverage gaps."""

    def test_field_with_default_factory(self) -> None:
        """Test expansion of field with default_factory."""

        @dataclass
        class Config:
            items: list = field(default_factory=list)
            name: str = "default"

        params = expand_dataclass("config", Config)

        param_dict = {p.name: p for p in params}
        # Field with default_factory should have has_default=True but default=None
        assert param_dict["config-items"].has_default is True
        assert param_dict["config-items"].default is None

    def test_reconstruct_skips_init_false_fields(self) -> None:
        """Test that reconstruction skips init=False fields."""

        @dataclass
        class Config:
            host: str
            internal: str = field(init=False, default="internal")

        values = {"config-host": "localhost"}
        result = reconstruct_dataclass(Config, values, "config")

        assert result.host == "localhost"
        assert result.internal == "internal"  # Uses default, not from values

    def test_reconstruct_with_empty_prefix(self) -> None:
        """Test reconstruction with empty prefix."""

        @dataclass
        class Config:
            host: str

        values = {"host": "localhost"}
        result = reconstruct_dataclass(Config, values, "", separator="-")

        assert result.host == "localhost"
