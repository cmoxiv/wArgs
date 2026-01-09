"""Unit tests for wArgs configuration dataclasses."""

from __future__ import annotations

from wargs.core.config import (
    MISSING,
    FunctionInfo,
    ParameterInfo,
    ParameterKind,
    TypeInfo,
)


class TestMissing:
    """Tests for MISSING sentinel."""

    def test_missing_is_singleton(self) -> None:
        """MISSING should be a singleton."""
        from wargs.core.config import _Missing

        m1 = _Missing()
        m2 = _Missing()
        assert m1 is m2
        assert m1 is MISSING

    def test_missing_repr(self) -> None:
        """MISSING should have readable repr."""
        assert repr(MISSING) == "<MISSING>"

    def test_missing_is_falsy(self) -> None:
        """MISSING should be falsy."""
        assert not MISSING
        assert bool(MISSING) is False


class TestParameterKind:
    """Tests for ParameterKind enum."""

    def test_all_kinds_exist(self) -> None:
        """All expected parameter kinds should exist."""
        assert ParameterKind.POSITIONAL_ONLY
        assert ParameterKind.POSITIONAL_OR_KEYWORD
        assert ParameterKind.VAR_POSITIONAL
        assert ParameterKind.KEYWORD_ONLY
        assert ParameterKind.VAR_KEYWORD

    def test_kind_values(self) -> None:
        """Kind values should be strings."""
        assert ParameterKind.VAR_POSITIONAL.value == "var_positional"
        assert ParameterKind.VAR_KEYWORD.value == "var_keyword"


class TestTypeInfo:
    """Tests for TypeInfo dataclass."""

    def test_default_values(self) -> None:
        """TypeInfo should have sensible defaults."""
        info = TypeInfo()
        assert info.origin is None
        assert info.args == ()
        assert info.is_optional is False
        assert info.is_literal is False
        assert info.literal_values == ()
        assert info.is_enum is False
        assert info.enum_class is None
        assert info.converter is None

    def test_with_values(self) -> None:
        """TypeInfo should accept all values."""
        info = TypeInfo(
            origin=str,
            args=(int,),
            is_optional=True,
            is_literal=False,
            converter=str,
        )
        assert info.origin is str
        assert info.args == (int,)
        assert info.is_optional is True
        assert info.converter is str


class TestParameterInfo:
    """Tests for ParameterInfo dataclass."""

    def test_minimal_creation(self) -> None:
        """ParameterInfo should work with just name."""
        param = ParameterInfo(name="test")
        assert param.name == "test"
        assert param.annotation is None
        assert param.type_info is None
        assert param.default is None
        assert param.has_default is False
        assert param.kind == ParameterKind.POSITIONAL_OR_KEYWORD
        assert param.description is None

    def test_full_creation(self) -> None:
        """ParameterInfo should accept all values."""
        type_info = TypeInfo(origin=str, converter=str)
        param = ParameterInfo(
            name="name",
            annotation=str,
            type_info=type_info,
            default="default",
            has_default=True,
            kind=ParameterKind.KEYWORD_ONLY,
            description="A name parameter",
        )
        assert param.name == "name"
        assert param.annotation is str
        assert param.type_info is type_info
        assert param.default == "default"
        assert param.has_default is True
        assert param.kind == ParameterKind.KEYWORD_ONLY
        assert param.description == "A name parameter"


class TestFunctionInfo:
    """Tests for FunctionInfo dataclass."""

    def test_minimal_creation(self) -> None:
        """FunctionInfo should work with minimal info."""
        info = FunctionInfo(name="func", qualname="func")
        assert info.name == "func"
        assert info.qualname == "func"
        assert info.description is None
        assert info.parameters == []
        assert info.return_type is None
        assert info.module is None
        assert info.source_file is None
        assert info.line_number is None

    def test_full_creation(self) -> None:
        """FunctionInfo should accept all values."""
        params = [ParameterInfo(name="x"), ParameterInfo(name="y")]
        info = FunctionInfo(
            name="add",
            qualname="Calculator.add",
            description="Add two numbers.",
            parameters=params,
            return_type=int,
            module="mymodule",
            source_file="/path/to/module.py",
            line_number=42,
        )
        assert info.name == "add"
        assert info.qualname == "Calculator.add"
        assert info.description == "Add two numbers."
        assert len(info.parameters) == 2
        assert info.return_type is int
        assert info.module == "mymodule"
        assert info.source_file == "/path/to/module.py"
        assert info.line_number == 42

    def test_parameters_is_mutable(self) -> None:
        """Each FunctionInfo should have its own parameters list."""
        info1 = FunctionInfo(name="f1", qualname="f1")
        info2 = FunctionInfo(name="f2", qualname="f2")

        info1.parameters.append(ParameterInfo(name="x"))
        assert len(info2.parameters) == 0
