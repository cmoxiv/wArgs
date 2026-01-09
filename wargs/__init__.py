"""wArgs - Decorator-based argparse automation.

Just decorate and you're done.

wArgs automatically generates argparse CLI interfaces from your function
signatures, type hints, and docstrings.

Basic usage:
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

CLI:
    $ python greet.py --name World --count 3
    Hello, World!
    Hello, World!
    Hello, World!
"""

from wArgs._version import __version__
from wArgs.completion import (
    generate_completion,
    get_install_instructions,
    install_completion,
)
from wArgs.converters.registry import ConverterRegistry, converter, get_default_registry
from wArgs.core.arg import Arg
from wArgs.core.exceptions import (
    ConfigurationError,
    ConversionError,
    ErrorContext,
    IntrospectionError,
    WargsError,
)
from wArgs.core.groups import WargsGroup, group
from wArgs.decorator import WargsClassWrapper, WargsWrapper, wArgs
from wArgs.utilities import explain, get_config, get_parser

# Attach group as attribute of wArgs for @wArgs.group() pattern
wArgs.group = group  # type: ignore[attr-defined]

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
    "wArgs",
]
