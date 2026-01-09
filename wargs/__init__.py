"""wArgs - Decorator-based argparse automation.

Just decorate and you're done.

wArgs automatically generates argparse CLI interfaces from your function
signatures, type hints, and docstrings.

Basic usage:
    from wargs import wargs

    @wargs
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

CLI:
    $ python greet.py --name World --count 3
    Hello, World!
    Hello, World!
    Hello, World!
"""

from wargs._version import __version__
from wargs.completion import (
    generate_completion,
    get_install_instructions,
    install_completion,
)
from wargs.converters.registry import ConverterRegistry, converter, get_default_registry
from wargs.core.arg import Arg
from wargs.core.exceptions import (
    ConfigurationError,
    ConversionError,
    ErrorContext,
    IntrospectionError,
    WargsError,
)
from wargs.core.groups import WargsGroup, group
from wargs.decorator import WargsClassWrapper, WargsWrapper, wargs
from wargs.utilities import explain, get_config, get_parser

# Attach group as attribute of wargs for @wargs.group() pattern
wargs.group = group  # type: ignore[attr-defined]

__all__ = [
    "Arg",
    "ConfigurationError",
    "ConversionError",
    "ConverterRegistry",
    "ErrorContext",
    "IntrospectionError",
    "WargsClassWrapper",
    "WargsError",
    "WargsGroup",
    "WargsWrapper",
    "__version__",
    "converter",
    "explain",
    "generate_completion",
    "get_config",
    "get_default_registry",
    "get_install_instructions",
    "get_parser",
    "group",
    "install_completion",
    "wargs",
]
