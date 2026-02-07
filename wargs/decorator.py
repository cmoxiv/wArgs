"""The @wArgs decorator for automatic CLI generation.

This is the main user-facing API for wArgs.

Example (function):
    from wArgs import wArgs

    @wArgs
    def greet(name: str, count: int = 1):
        '''Greet someone.

        Args:
            name: The person to greet
            count: Number of greetings
        '''
        for _ in range(count):
            print(f"Hello, {name}!")

    if __name__ == "__main__":
        greet()

Example (class with subcommands):
    from wArgs import wArgs

    @wArgs
    class CLI:
        def __init__(self, verbose: bool = False):
            '''Global options.

            Args:
                verbose: Enable verbose output
            '''
            self.verbose = verbose

        def add(self, name: str):
            '''Add an item.

            Args:
                name: Item name
            '''
            print(f"Adding {name}")

        def remove(self, item_id: int):
            '''Remove an item.

            Args:
                item_id: Item ID
            '''
            print(f"Removing {item_id}")

    if __name__ == "__main__":
        CLI()
"""

from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, overload

from wArgs.builders.arguments import build_parser_config
from wArgs.builders.parser import build_parser
from wArgs.builders.subcommands import build_subcommand_config, extract_methods
from wArgs.core.config import ParameterKind
from wArgs.introspection.docstrings import parse_docstring
from wArgs.introspection.signatures import extract_function_info
from wArgs.introspection.types import resolve_type
from wArgs.utilities import debug_print

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace

    from wArgs.core.config import FunctionInfo, ParserConfig


class WargsWrapper:
    """Wrapper class for functions decorated with @wArgs.

    Provides access to the underlying function, parser, and CLI execution.

    Attributes:
        func: The wrapped function.
        parser: The generated ArgumentParser.
        prog: Program name override.
        description: Description override.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        *,
        prog: str | None = None,
        description: str | None = None,
        add_help: bool = True,
        formatter_class: str | None = None,
        completion: bool = False,
        prefix: bool | str = False,
    ) -> None:
        """Initialize the wrapper.

        Args:
            func: The function to wrap.
            prog: Program name override.
            description: Description override.
            add_help: Whether to add -h/--help.
            formatter_class: Help formatter class name.
            completion: Whether to add --completion flag for shell completion.
            prefix: Argument prefixing mode. False (default) = no prefix, True = use
                function name as prefix, str = use custom prefix string.
        """
        self._func = func
        self._prog = prog
        self._description = description
        self._add_help = add_help
        self._formatter_class = formatter_class
        self._completion = completion
        self._prefix = prefix
        self._parser: ArgumentParser | None = None
        self._func_info: FunctionInfo | None = None
        self._parser_config: ParserConfig | None = None

        # Copy function metadata
        wraps(func)(self)

    @property
    def func(self) -> Callable[..., Any]:
        """Get the wrapped function."""
        return self._func

    @property
    def parser(self) -> ArgumentParser:
        """Get or build the ArgumentParser (lazy construction)."""
        if self._parser is None:
            self._build_parser()
        return self._parser  # type: ignore[return-value]

    @property
    def _wargs_config(self) -> ParserConfig | None:
        """Get the parser configuration (for debugging/testing)."""
        return self._parser_config

    def _build_parser(self) -> None:
        """Build the parser from function introspection."""
        debug_print(f"Building parser for function: {self._func.__name__}")

        # Extract function info
        func_info = extract_function_info(self._func)

        # Parse docstring for parameter descriptions
        docstring_info = parse_docstring(func_info.description)

        # Resolve types and add descriptions from docstring
        for param in func_info.parameters:
            # Resolve type annotation
            if param.annotation is not None:
                param.type_info = resolve_type(param.annotation)

            # Add description from docstring if not already set
            if param.description is None and param.name in docstring_info.params:
                param.description = docstring_info.params[param.name]

        # Store for later use
        self._func_info = func_info

        # Determine prefix for arguments
        if self._prefix is False:
            # No prefix (default)
            arg_prefix = None
        elif self._prefix is True:
            # Use function name as prefix
            arg_prefix = func_info.name
        else:
            # Use custom prefix string
            arg_prefix = str(self._prefix)

        # Build parser config
        self._parser_config = build_parser_config(
            func_info,
            prog=self._prog,
            description=self._description,
            prefix=arg_prefix,
        )

        # Apply options
        if self._formatter_class:
            self._parser_config.formatter_class = self._formatter_class
        self._parser_config.add_help = self._add_help

        # Build the actual parser
        self._parser = build_parser(self._parser_config)

        # Add completion argument if enabled
        if self._completion:
            self._parser.add_argument(
                "--completion",
                choices=["bash", "zsh", "fish"],
                metavar="SHELL",
                help="Generate shell completion script and exit",
            )

    def parse_args(self, args: list[str] | None = None) -> Namespace:
        """Parse command-line arguments.

        Args:
            args: Arguments to parse. Defaults to sys.argv[1:].

        Returns:
            Namespace with parsed arguments.
        """
        debug_print(f"Parsing args: {args}")
        result = self.parser.parse_args(args)
        debug_print(f"Parsed result: {result}")
        return result

    def _convert_namespace_to_kwargs(self, namespace: Namespace) -> dict[str, Any]:
        """Convert parsed Namespace to function kwargs.

        Args:
            namespace: The parsed argument namespace.

        Returns:
            Dictionary of keyword arguments for the function.
        """
        kwargs: dict[str, Any] = {}

        if self._func_info is None:
            self._build_parser()

        assert self._func_info is not None
        assert self._parser_config is not None

        # Reconstruct dict parameters from expanded args
        for param_name, expansion in self._parser_config.dict_expansions.items():
            reconstructed: dict[str, Any] = dict(expansion.default_dict)
            for key in expansion.keys:
                expanded_name = f"{param_name}_{key}"
                value = getattr(namespace, expanded_name, None)
                if value is not None:
                    reconstructed[key] = value
            kwargs[param_name] = reconstructed

        for param in self._func_info.parameters:
            # Skip *args and **kwargs
            if param.kind in (ParameterKind.VAR_POSITIONAL, ParameterKind.VAR_KEYWORD):
                continue

            # Skip dict-expanded parameters (already handled above)
            if param.name in self._parser_config.dict_expansions:
                continue

            # Get value from namespace
            value = getattr(namespace, param.name, None)
            if value is not None or param.has_default is False:
                kwargs[param.name] = value

        return kwargs

    def run(self, args: list[str] | None = None) -> Any:
        """Parse arguments and call the function.

        Args:
            args: Arguments to parse. Defaults to sys.argv[1:].

        Returns:
            The return value of the wrapped function.
        """
        # Handle completion before full parsing (to avoid required arg errors)
        if self._completion:
            import sys

            check_args = args if args is not None else sys.argv[1:]
            if "--completion" in check_args:
                idx = check_args.index("--completion")
                if idx + 1 < len(check_args):
                    shell = check_args[idx + 1]
                    if shell in ("bash", "zsh", "fish"):
                        from wArgs.completion import generate_completion

                        print(generate_completion(self, shell=shell))
                        return None

        namespace = self.parse_args(args)
        kwargs = self._convert_namespace_to_kwargs(namespace)
        return self._func(**kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the wrapped function.

        If called with no arguments and running as __main__,
        parses CLI arguments. Otherwise, calls the function directly.

        Returns:
            The return value of the wrapped function.
        """
        # If arguments are provided, call directly
        if args or kwargs:
            return self._func(*args, **kwargs)

        # No arguments - check if we should parse CLI
        # This enables the pattern: if __name__ == "__main__": func()
        return self.run()

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<WargsWrapper({self._func.__name__})>"


class WargsClassWrapper:
    """Wrapper class for classes decorated with @wArgs.

    Provides subcommand support where methods become subcommands and
    __init__ parameters become global options.

    Attributes:
        cls: The wrapped class.
        parser: The generated ArgumentParser with subparsers.
    """

    def __init__(
        self,
        cls: type,
        *,
        prog: str | None = None,
        description: str | None = None,
        add_help: bool = True,
        formatter_class: str | None = None,
        traverse_mro: bool = True,
        completion: bool = False,
        prefix: bool | str = False,
    ) -> None:
        """Initialize the class wrapper.

        Args:
            cls: The class to wrap.
            prog: Program name override.
            description: Description override.
            add_help: Whether to add -h/--help.
            formatter_class: Help formatter class name.
            traverse_mro: Whether to collect __init__ params from parent classes.
            completion: Whether to add --completion flag for shell completion.
            prefix: Argument prefixing mode. False (default) = no prefix, True = use
                class/method names as prefix, str = use custom prefix for __init__ args.
        """
        self._cls = cls
        self._prog = prog
        self._description = description
        self._add_help = add_help
        self._formatter_class = formatter_class
        self._traverse_mro = traverse_mro
        self._completion = completion
        self._prefix = prefix
        self._parser: ArgumentParser | None = None
        self._parser_config: ParserConfig | None = None
        self._methods: dict[str, Any] = {}

        # Copy class metadata
        self.__name__ = cls.__name__
        self.__doc__ = cls.__doc__
        self.__module__ = cls.__module__

    @property
    def cls(self) -> type:
        """Get the wrapped class."""
        return self._cls

    @property
    def parser(self) -> ArgumentParser:
        """Get or build the ArgumentParser (lazy construction)."""
        if self._parser is None:
            self._build_parser()
        return self._parser  # type: ignore[return-value]

    @property
    def _wargs_config(self) -> ParserConfig | None:
        """Get the parser configuration (for debugging/testing)."""
        return self._parser_config

    def _build_parser(self) -> None:
        """Build the parser from class introspection."""
        debug_print(f"Building parser for class: {self._cls.__name__}")

        # Build parser config with subcommands
        parser_config = build_subcommand_config(
            self._cls,
            prog=self._prog,
            description=self._description,
            traverse_mro=self._traverse_mro,
            prefix=self._prefix,
        )

        # Apply options
        if self._formatter_class:
            parser_config.formatter_class = self._formatter_class
        parser_config.add_help = self._add_help

        # Store for later use
        self._parser_config = parser_config

        # Build the actual parser
        self._parser = build_parser(parser_config)

        # Add completion argument if enabled
        if self._completion:
            self._parser.add_argument(
                "--completion",
                choices=["bash", "zsh", "fish"],
                metavar="SHELL",
                help="Generate shell completion script and exit",
            )

        # Cache method references
        self._methods = extract_methods(self._cls)

    def parse_args(self, args: list[str] | None = None) -> Namespace:
        """Parse command-line arguments.

        Args:
            args: Arguments to parse. Defaults to sys.argv[1:].

        Returns:
            Namespace with parsed arguments.
        """
        debug_print(f"Parsing args for class: {args}")
        result = self.parser.parse_args(args)
        debug_print(f"Parsed result: {result}")
        return result

    def _get_init_kwargs(self, namespace: Namespace) -> dict[str, Any]:
        """Extract __init__ kwargs from namespace.

        Only returns kwargs that the actual __init__ accepts (not inherited ones
        that are only for CLI display).

        Args:
            namespace: The parsed argument namespace.

        Returns:
            Dictionary of keyword arguments for __init__.
        """
        kwargs: dict[str, Any] = {}

        if self._parser_config is None:
            self._build_parser()

        assert self._parser_config is not None

        # Get the actual __init__ signature to know what it accepts
        init_method = self._cls.__dict__.get("__init__")
        if init_method is not None:
            import inspect as insp

            sig = insp.signature(init_method)
            valid_params = set(sig.parameters.keys()) - {"self"}
            has_var_keyword = any(
                p.kind == insp.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
        else:
            valid_params = set()
            has_var_keyword = False

        # Reconstruct dict parameters from expanded args
        for param_name, expansion in self._parser_config.dict_expansions.items():
            if param_name in valid_params or has_var_keyword:
                reconstructed: dict[str, Any] = dict(expansion.default_dict)
                for key in expansion.keys:
                    expanded_name = f"{param_name}_{key}"
                    value = getattr(namespace, expanded_name, None)
                    if value is not None:
                        reconstructed[key] = value
                kwargs[param_name] = reconstructed

        # Build set of expanded arg names to skip
        expanded_arg_names: set[str] = set()
        for expansion in self._parser_config.dict_expansions.values():
            for key in expansion.keys:
                expanded_arg_names.add(f"{expansion.param_name}_{key}")

        # Get arguments that belong to __init__ (global options)
        for arg in self._parser_config.arguments:
            # Skip expanded dict args (already handled above)
            if arg.name in expanded_arg_names:
                continue

            # Only include if __init__ accepts it (or has **kwargs)
            if arg.name in valid_params or has_var_keyword:
                value = getattr(namespace, arg.name, None)
                if value is not None:
                    kwargs[arg.name] = value

        return kwargs

    def _get_method_kwargs(
        self, namespace: Namespace, method_name: str
    ) -> dict[str, Any]:
        """Extract method kwargs from namespace.

        Args:
            namespace: The parsed argument namespace.
            method_name: The subcommand/method name.

        Returns:
            Dictionary of keyword arguments for the method.
        """
        kwargs: dict[str, Any] = {}

        if self._parser_config is None:
            self._build_parser()

        assert self._parser_config is not None

        # Get subcommand config
        subconfig = self._parser_config.subcommands.get(method_name)
        if subconfig is None:
            return kwargs

        # Get arguments for this subcommand
        for arg in subconfig.arguments:
            value = getattr(namespace, arg.name, None)
            if value is not None:
                kwargs[arg.name] = value

        return kwargs

    def run(self, args: list[str] | None = None) -> Any:
        """Parse arguments and call the appropriate method.

        Args:
            args: Arguments to parse. Defaults to sys.argv[1:].

        Returns:
            The return value of the called method.
        """
        # Handle completion before full parsing (to avoid required arg errors)
        if self._completion:
            import sys

            check_args = args if args is not None else sys.argv[1:]
            if "--completion" in check_args:
                idx = check_args.index("--completion")
                if idx + 1 < len(check_args):
                    shell = check_args[idx + 1]
                    if shell in ("bash", "zsh", "fish"):
                        from wArgs.completion import generate_completion

                        print(generate_completion(self, shell=shell))
                        return None

        namespace = self.parse_args(args)

        # Get the subcommand (method) name
        command = getattr(namespace, "command", None)
        if command is None:
            # No subcommand specified - print help
            self.parser.print_help()
            return None

        # Create instance with global options
        init_kwargs = self._get_init_kwargs(namespace)
        instance = self._cls(**init_kwargs)

        # Get method kwargs
        method_kwargs = self._get_method_kwargs(namespace, command)

        # Convert hyphenated command to Python method name
        method_name = command.replace("-", "_")

        # Call the method
        method = getattr(instance, method_name)
        return method(**method_kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the wrapper.

        Parses CLI arguments and creates an instance of the class.
        Explicit kwargs override CLI-parsed values.

        Args:
            *args: Positional arguments passed directly to __init__.
            **kwargs: Keyword arguments that override CLI-parsed values.

        Returns:
            Instance of the wrapped class.
        """
        # If positional args are provided, pass them directly
        # (can't merge positional args with CLI parsing)
        if args:
            return self._cls(*args, **kwargs)

        # Parse CLI arguments
        namespace = self.parse_args()

        # Get init kwargs from CLI
        cli_kwargs = self._get_init_kwargs(namespace)

        # Merge: explicit kwargs override CLI kwargs
        merged_kwargs = {**cli_kwargs, **kwargs}

        # Create and return instance
        return self._cls(**merged_kwargs)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<WargsClassWrapper({self._cls.__name__})>"


# Note: type overload must come first because type is a subtype of Callable
# mypy reports overlap but runtime behavior is correct (classes are checked first)
@overload
def wArgs(func: type) -> WargsClassWrapper: ...  # type: ignore[overload-overlap]


@overload
def wArgs(func: Callable[..., Any]) -> WargsWrapper: ...


@overload
def wArgs(
    *,
    prog: str | None = None,
    description: str | None = None,
    add_help: bool = True,
    formatter_class: str | None = None,
    traverse_mro: bool = True,
    completion: bool = False,
    prefix: bool | str = False,
) -> Callable[[Callable[..., Any] | type], WargsWrapper | WargsClassWrapper]: ...


def wArgs(
    func: Callable[..., Any] | type | None = None,
    *,
    prog: str | None = None,
    description: str | None = None,
    add_help: bool = True,
    formatter_class: str | None = None,
    traverse_mro: bool = True,
    completion: bool = False,
    prefix: bool | str = False,
) -> (
    WargsWrapper
    | WargsClassWrapper
    | Callable[[Callable[..., Any] | type], WargsWrapper | WargsClassWrapper]
):
    """Decorator to generate CLI from function or class.

    Can be used with or without arguments on functions or classes:

        # Function-based CLI
        @wArgs
        def my_func(name: str): ...

        # Class-based CLI with subcommands
        @wArgs
        class CLI:
            def __init__(self, verbose: bool = False): ...
            def add(self, name: str): ...
            def remove(self, item_id: int): ...

        @wArgs(prog="myapp", description="My application")
        def my_func(name: str): ...

        # Disable MRO traversal for inherited parameters
        @wArgs(traverse_mro=False)
        class CLI(BaseClass): ...

        # Enable shell completion support
        @wArgs(completion=True)
        def cli(name: str): ...
        # Then run: python script.py --completion bash

    Args:
        func: The function or class to decorate (when used without parentheses).
        prog: Program name override.
        description: Description override.
        add_help: Whether to add -h/--help option.
        formatter_class: Help formatter class name.
        traverse_mro: Whether to collect __init__ params from parent classes
            (only applies to class decoration).
        completion: Whether to add --completion flag for shell completion.
        prefix: Argument prefixing mode. False (default) = no prefix, True = use
            callable name as prefix, str = use custom prefix string.

    Returns:
        WargsWrapper for functions, WargsClassWrapper for classes,
        or a decorator function.
    """
    if func is not None:
        # Called as @wArgs without parentheses
        if inspect.isclass(func):
            return WargsClassWrapper(func)
        return WargsWrapper(func)

    # Called as @wArgs(...) with arguments
    def decorator(f: Callable[..., Any] | type) -> WargsWrapper | WargsClassWrapper:
        if inspect.isclass(f):
            return WargsClassWrapper(
                f,
                prog=prog,
                description=description,
                add_help=add_help,
                formatter_class=formatter_class,
                traverse_mro=traverse_mro,
                completion=completion,
                prefix=prefix,
            )
        return WargsWrapper(
            f,
            prog=prog,
            description=description,
            add_help=add_help,
            formatter_class=formatter_class,
            completion=completion,
            prefix=prefix,
        )

    return decorator


__all__ = [
    "WargsClassWrapper",
    "WargsWrapper",
    "wArgs",
]
