"""Unit tests for MRO traversal."""

from __future__ import annotations

import warnings

from wargs.introspection.mro import (
    get_inherited_function_info,
    get_init_parameters,
    merge_parameters,
    traverse_mro,
)


class TestGetInitParameters:
    """Tests for get_init_parameters function."""

    def test_class_with_init(self) -> None:
        """Test extracting parameters from __init__."""

        class Example:
            def __init__(self, name: str, count: int = 1) -> None:
                pass

        params = get_init_parameters(Example)
        assert len(params) == 2
        assert params[0].name == "name"
        assert params[1].name == "count"

    def test_class_without_custom_init(self) -> None:
        """Test class with default __init__ returns empty list."""

        class Example:
            pass

        params = get_init_parameters(Example)
        assert len(params) == 0

    def test_docstring_descriptions_extracted(self) -> None:
        """Test that docstring descriptions are extracted."""

        class Example:
            def __init__(self, verbose: bool = False) -> None:
                """Initialize.

                Args:
                    verbose: Enable verbose mode.
                """
                pass

        params = get_init_parameters(Example)
        assert params[0].description == "Enable verbose mode."


class TestMergeParameters:
    """Tests for merge_parameters function."""

    def test_child_overrides_parent(self) -> None:
        """Test that child parameters override parent."""

        class Parent:
            def __init__(self, name: str = "parent") -> None:
                pass

        class Child:
            def __init__(self, name: str = "child") -> None:
                pass

        parent_params = get_init_parameters(Parent)
        child_params = get_init_parameters(Child)

        merged = merge_parameters(
            child_params, parent_params, Child, Parent, warn_on_conflict=False
        )

        assert len(merged) == 1
        assert merged[0].default == "child"

    def test_parent_params_added(self) -> None:
        """Test that parent-only parameters are added."""

        class Parent:
            def __init__(self, debug: bool = False) -> None:
                pass

        class Child:
            def __init__(self, name: str) -> None:
                pass

        parent_params = get_init_parameters(Parent)
        child_params = get_init_parameters(Child)

        merged = merge_parameters(
            child_params, parent_params, Child, Parent, warn_on_conflict=False
        )

        assert len(merged) == 2
        names = [p.name for p in merged]
        assert "name" in names
        assert "debug" in names

    def test_type_conflict_warning(self) -> None:
        """Test that type conflicts produce warnings."""

        class Parent:
            def __init__(self, value: str) -> None:
                pass

        class Child:
            def __init__(self, value: int) -> None:
                pass

        parent_params = get_init_parameters(Parent)
        child_params = get_init_parameters(Child)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            merge_parameters(
                child_params, parent_params, Child, Parent, warn_on_conflict=True
            )
            assert len(w) == 1
            assert "type" in str(w[0].message).lower()
            assert "Child" in str(w[0].message)
            assert "Parent" in str(w[0].message)

    def test_no_warning_when_disabled(self) -> None:
        """Test that warnings can be disabled."""

        class Parent:
            def __init__(self, value: str) -> None:
                pass

        class Child:
            def __init__(self, value: int) -> None:
                pass

        parent_params = get_init_parameters(Parent)
        child_params = get_init_parameters(Child)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            merge_parameters(
                child_params, parent_params, Child, Parent, warn_on_conflict=False
            )
            assert len(w) == 0


class TestTraverseMro:
    """Tests for traverse_mro function."""

    def test_single_class(self) -> None:
        """Test MRO traversal for single class."""

        class CLI:
            def __init__(self, name: str) -> None:
                pass

        params = traverse_mro(CLI, warn_on_conflict=False)
        assert len(params) == 1
        assert params[0].name == "name"

    def test_single_inheritance(self) -> None:
        """Test MRO traversal with single inheritance."""

        class Base:
            def __init__(self, debug: bool = False) -> None:
                pass

        class Child(Base):
            def __init__(self, name: str) -> None:
                super().__init__()

        params = traverse_mro(Child, warn_on_conflict=False)
        assert len(params) == 2
        names = [p.name for p in params]
        assert "name" in names
        assert "debug" in names

    def test_child_override_preserved(self) -> None:
        """Test that child override is preserved in MRO."""

        class Base:
            def __init__(self, name: str = "base") -> None:
                pass

        class Child(Base):
            def __init__(self, name: str = "child") -> None:
                super().__init__(name)

        params = traverse_mro(Child, warn_on_conflict=False)
        assert len(params) == 1
        assert params[0].default == "child"

    def test_multiple_inheritance(self) -> None:
        """Test MRO traversal with multiple inheritance (mixins)."""

        class LogMixin:
            def __init__(self, log_level: str = "INFO") -> None:
                pass

        class CacheMixin:
            def __init__(self, cache_size: int = 100) -> None:
                pass

        class CLI(LogMixin, CacheMixin):
            def __init__(self, name: str) -> None:
                super().__init__()

        params = traverse_mro(CLI, warn_on_conflict=False)
        names = [p.name for p in params]
        assert "name" in names
        assert "log_level" in names
        assert "cache_size" in names

    def test_diamond_inheritance(self) -> None:
        """Test MRO traversal with diamond inheritance."""

        class Base:
            def __init__(self, debug: bool = False) -> None:
                pass

        class Left(Base):
            def __init__(self, left_opt: str = "left") -> None:
                super().__init__()

        class Right(Base):
            def __init__(self, right_opt: str = "right") -> None:
                super().__init__()

        class Child(Left, Right):
            def __init__(self, name: str) -> None:
                super().__init__()

        params = traverse_mro(Child, warn_on_conflict=False)
        names = [p.name for p in params]
        # Should have all unique parameters
        assert "name" in names
        assert "left_opt" in names
        assert "right_opt" in names
        assert "debug" in names
        # debug should only appear once
        assert names.count("debug") == 1


class TestGetInheritedFunctionInfo:
    """Tests for get_inherited_function_info function."""

    def test_returns_function_info(self) -> None:
        """Test that FunctionInfo is returned."""

        class CLI:
            """A CLI application."""

            def __init__(self, name: str) -> None:
                pass

        info = get_inherited_function_info(CLI)
        assert info.name == "CLI"
        assert info.description is not None
        assert "CLI application" in info.description
        assert len(info.parameters) == 1

    def test_includes_inherited_params(self) -> None:
        """Test that inherited parameters are included."""

        class Base:
            def __init__(self, debug: bool = False) -> None:
                pass

        class CLI(Base):
            def __init__(self, name: str) -> None:
                super().__init__()

        info = get_inherited_function_info(CLI)
        assert len(info.parameters) == 2
        names = [p.name for p in info.parameters]
        assert "name" in names
        assert "debug" in names


class TestMroCoverageGaps:
    """Additional tests for coverage gaps."""

    def test_type_conflict_with_none_annotation(self) -> None:
        """Test that type conflict is skipped when annotation is None."""

        class Parent:
            def __init__(self, value) -> None:  # No annotation
                pass

        class Child:
            def __init__(self, value: int) -> None:
                pass

        parent_params = get_init_parameters(Parent)
        child_params = get_init_parameters(Child)

        # No warning since parent has no type
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            merge_parameters(
                child_params, parent_params, Child, Parent, warn_on_conflict=True
            )
            # No warning because parent annotation is None
            type_warnings = [x for x in w if "type" in str(x.message).lower()]
            assert len(type_warnings) == 0

    def test_type_conflict_child_none_annotation(self) -> None:
        """Test that type conflict is skipped when child annotation is None."""

        class Parent:
            def __init__(self, value: str) -> None:
                pass

        class Child:
            def __init__(self, value) -> None:  # No annotation
                pass

        parent_params = get_init_parameters(Parent)
        child_params = get_init_parameters(Child)

        # No warning since child has no type
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            merge_parameters(
                child_params, parent_params, Child, Parent, warn_on_conflict=True
            )
            type_warnings = [x for x in w if "type" in str(x.message).lower()]
            assert len(type_warnings) == 0

    def test_empty_class_mro(self) -> None:
        """Test traverse_mro with class that has no __init__ (empty parameters)."""

        class EmptyClass:
            pass

        params = traverse_mro(EmptyClass, warn_on_conflict=False)
        assert params == []

    def test_class_with_only_object_init(self) -> None:
        """Test class that only has object.__init__ in MRO."""

        # Create a class dynamically that inherits from object only
        class SimpleClass:
            pass

        # MRO is [SimpleClass, object], but object is filtered out
        params = traverse_mro(SimpleClass, warn_on_conflict=False)
        assert params == []
