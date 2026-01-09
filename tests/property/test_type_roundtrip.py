"""Property-based tests for type conversion roundtrips."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from wargs.introspection.types import resolve_type


class TestTypeRoundtrip:
    """Property-based tests for type conversion."""

    @given(st.integers())
    def test_int_roundtrip(self, value: int) -> None:
        """Integer values survive type conversion."""
        info = resolve_type(int)
        assert info.converter is not None
        converted = info.converter(str(value))
        assert converted == value

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_float_roundtrip(self, value: float) -> None:
        """Float values survive type conversion."""
        info = resolve_type(float)
        assert info.converter is not None
        converted = info.converter(str(value))
        # Use approximate comparison for floats
        assert abs(converted - value) < 1e-10 or converted == value

    @given(st.text(min_size=1, max_size=100))
    def test_str_roundtrip(self, value: str) -> None:
        """String values survive type conversion."""
        info = resolve_type(str)
        assert info.converter is not None
        converted = info.converter(value)
        assert converted == value

    @given(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=("L", "N"), whitelist_characters="_-."
            ),
        )
    )
    def test_path_roundtrip(self, value: str) -> None:
        """Path-like strings survive type conversion."""
        info = resolve_type(Path)
        assert info.converter is not None
        converted = info.converter(value)
        assert isinstance(converted, Path)
        assert str(converted) == value
