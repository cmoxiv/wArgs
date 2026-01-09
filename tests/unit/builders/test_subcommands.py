"""Unit tests for the subcommands builder."""

from __future__ import annotations

from wargs.builders.subcommands import (
    build_subcommand_config,
    extract_init_info,
    extract_method_info,
    extract_methods,
    is_public_method,
)


class TestIsPublicMethod:
    """Tests for is_public_method function."""

    def test_public_method(self) -> None:
        """Test that public methods are detected."""

        class Example:
            def public_method(self) -> None:
                pass

        assert is_public_method("public_method", Example.public_method)

    def test_private_method_excluded(self) -> None:
        """Test that private methods (single underscore) are excluded."""

        class Example:
            def _private_method(self) -> None:
                pass

        assert not is_public_method("_private_method", Example._private_method)

    def test_dunder_method_excluded(self) -> None:
        """Test that dunder methods are excluded."""

        class Example:
            def __init__(self) -> None:
                pass

        assert not is_public_method("__init__", Example.__init__)

    def test_non_callable_excluded(self) -> None:
        """Test that non-callable attributes are excluded."""
        assert not is_public_method("value", 42)
        assert not is_public_method("text", "hello")


class TestExtractMethods:
    """Tests for extract_methods function."""

    def test_extract_public_methods(self) -> None:
        """Test extracting public methods from a class."""

        class Example:
            def add(self) -> None:
                pass

            def remove(self) -> None:
                pass

            def _private(self) -> None:
                pass

        methods = extract_methods(Example)
        assert "add" in methods
        assert "remove" in methods
        assert "_private" not in methods
        assert "__init__" not in methods

    def test_empty_class(self) -> None:
        """Test extracting from a class with no public methods."""

        class Empty:
            pass

        methods = extract_methods(Empty)
        assert len(methods) == 0

    def test_excludes_inherited_object_methods(self) -> None:
        """Test that inherited object methods are excluded."""

        class Example:
            def custom(self) -> None:
                pass

        methods = extract_methods(Example)
        # Should only have our custom method, not __str__, __repr__, etc.
        assert "custom" in methods
        assert "__str__" not in methods


class TestExtractInitInfo:
    """Tests for extract_init_info function."""

    def test_extract_init_with_params(self) -> None:
        """Test extracting __init__ with parameters."""

        class Example:
            def __init__(self, name: str, count: int = 1) -> None:
                pass

        info = extract_init_info(Example)
        assert info is not None
        assert len(info.parameters) == 2
        assert info.parameters[0].name == "name"
        assert info.parameters[1].name == "count"

    def test_no_custom_init(self) -> None:
        """Test class without custom __init__ returns None."""

        class Example:
            pass

        info = extract_init_info(Example)
        assert info is None

    def test_init_docstring_descriptions(self) -> None:
        """Test that docstring descriptions are extracted."""

        class Example:
            def __init__(self, verbose: bool = False) -> None:
                """Initialize.

                Args:
                    verbose: Enable verbose output.
                """
                pass

        info = extract_init_info(Example)
        assert info is not None
        assert info.parameters[0].description == "Enable verbose output."


class TestExtractMethodInfo:
    """Tests for extract_method_info function."""

    def test_extract_method_params(self) -> None:
        """Test extracting method parameters."""

        class Example:
            def add(self, name: str, count: int = 1) -> None:
                pass

        info = extract_method_info(Example.add)
        assert len(info.parameters) == 2
        assert info.parameters[0].name == "name"
        assert info.parameters[1].name == "count"

    def test_method_docstring(self) -> None:
        """Test extracting method docstring."""

        class Example:
            def add(self, name: str) -> None:
                """Add an item.

                Args:
                    name: The item name.
                """
                pass

        info = extract_method_info(Example.add)
        assert info.description is not None
        assert "Add an item" in info.description
        assert info.parameters[0].description == "The item name."


class TestBuildSubcommandConfig:
    """Tests for build_subcommand_config function."""

    def test_basic_subcommands(self) -> None:
        """Test building config with basic subcommands."""

        class CLI:
            def add(self, name: str) -> None:
                pass

            def remove(self, item_id: int) -> None:
                pass

        config = build_subcommand_config(CLI)
        assert "add" in config.subcommands
        assert "remove" in config.subcommands

    def test_global_options_from_init(self) -> None:
        """Test that __init__ params become global options."""

        class CLI:
            def __init__(self, verbose: bool = False) -> None:
                pass

            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI)
        assert len(config.arguments) == 1
        assert config.arguments[0].name == "verbose"

    def test_subcommand_arguments(self) -> None:
        """Test that method params become subcommand arguments."""

        class CLI:
            def add(self, name: str, count: int = 1) -> None:
                pass

        config = build_subcommand_config(CLI)
        subconfig = config.subcommands["add"]
        assert len(subconfig.arguments) == 2
        param_names = [arg.name for arg in subconfig.arguments]
        assert "name" in param_names
        assert "count" in param_names

    def test_prog_override(self) -> None:
        """Test program name override."""

        class CLI:
            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI, prog="myapp")
        assert config.prog == "myapp"

    def test_description_override(self) -> None:
        """Test description override."""

        class CLI:
            """Original description."""

            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI, description="Custom description")
        assert config.description == "Custom description"

    def test_description_from_docstring(self) -> None:
        """Test description from class docstring."""

        class CLI:
            """A command-line tool for managing items."""

            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI)
        assert config.description is not None
        assert "command-line tool" in config.description

    def test_method_with_underscores_becomes_hyphenated(self) -> None:
        """Test that method names with underscores become hyphenated."""

        class CLI:
            def add_item(self) -> None:
                pass

            def remove_all_items(self) -> None:
                pass

        config = build_subcommand_config(CLI)
        assert "add-item" in config.subcommands
        assert "remove-all-items" in config.subcommands

    def test_subcommand_description_from_docstring(self) -> None:
        """Test subcommand description from method docstring."""

        class CLI:
            def add(self, name: str) -> None:
                """Add a new item to the list."""
                pass

        config = build_subcommand_config(CLI)
        subconfig = config.subcommands["add"]
        assert subconfig.description is not None
        assert "Add a new item" in subconfig.description


class TestSubcommandCoverageGaps:
    """Additional tests for coverage gaps."""

    def test_callable_class_attribute_not_method(self) -> None:
        """Test that callable class attributes are not methods."""

        class CallableClass:
            def __call__(self) -> str:
                return "called"

        # is_public_method should return False for callable non-function
        instance = CallableClass()
        assert not is_public_method("my_callable", instance)

    def test_class_attribute_excluded_from_methods(self) -> None:
        """Test that class attributes are excluded from extract_methods."""

        class CLI:
            my_value = 42

            def run(self) -> None:
                pass

        methods = extract_methods(CLI)
        assert "run" in methods
        assert "my_value" not in methods

    def test_init_is_object_init(self) -> None:
        """Test that class inheriting object.__init__ returns None."""

        class SimpleClass:
            pass

        info = extract_init_info(SimpleClass)
        assert info is None

    def test_description_without_period(self) -> None:
        """Test description extraction when no period in first sentence."""

        class CLI:
            """This is a description without periods just one long line"""

            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI)
        assert "without periods" in config.description

    def test_description_with_short_first_sentence(self) -> None:
        """Test description extraction with short first sentence."""

        class CLI:
            """Short description. This is more detail that should be excluded."""

            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI)
        assert config.description == "Short description."

    def test_traverse_mro_false(self) -> None:
        """Test building config without MRO traversal."""

        class Base:
            def __init__(self, debug: bool = False) -> None:
                pass

        class CLI(Base):
            def __init__(self, name: str) -> None:
                super().__init__()

            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI, traverse_mro=False)
        arg_names = [a.name for a in config.arguments]
        assert "name" in arg_names
        # debug should NOT be present since traverse_mro=False
        assert "debug" not in arg_names

    def test_class_without_init_traverse_mro(self) -> None:
        """Test MRO traversal when class has no custom __init__."""

        class CLI:
            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI, traverse_mro=True)
        # No __init__ parameters, so arguments should be empty
        assert config.arguments == []

    def test_class_without_init_no_traverse(self) -> None:
        """Test no MRO traversal when class has no custom __init__."""

        class CLI:
            def run(self) -> None:
                pass

        config = build_subcommand_config(CLI, traverse_mro=False)
        # No __init__ parameters, so arguments should be empty
        assert config.arguments == []
