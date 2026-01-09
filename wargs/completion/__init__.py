"""Shell completion support for wArgs.

This module provides shell completion script generation for Bash, Zsh, and Fish.

Example:
    from wArgs.completion import generate_completion, install_completion

    @wargs
    def cli(name: str, count: int = 1):
        ...

    # Generate completion script
    script = generate_completion(cli, shell="bash")

    # Or install directly
    install_completion(cli)
"""

from __future__ import annotations

from typing import Any

from wArgs.completion.bash import (
    generate_bash_completion,
    get_bash_completion_install_instructions,
)
from wArgs.completion.fish import (
    generate_fish_completion,
    get_fish_completion_install_instructions,
)
from wArgs.completion.generator import (
    CompletionOption,
    CompletionSpec,
    CompletionSubcommand,
    detect_shell,
    get_completion_spec,
)
from wArgs.completion.zsh import (
    generate_zsh_completion,
    get_zsh_completion_install_instructions,
)

__all__ = [
    "CompletionOption",
    "CompletionSpec",
    "CompletionSubcommand",
    "detect_shell",
    "generate_bash_completion",
    "generate_completion",
    "generate_fish_completion",
    "generate_zsh_completion",
    "get_bash_completion_install_instructions",
    "get_completion_spec",
    "get_fish_completion_install_instructions",
    "get_install_instructions",
    "get_zsh_completion_install_instructions",
    "install_completion",
]


def generate_completion(func_or_class: Any, shell: str | None = None) -> str:
    """Generate a shell completion script for a wargs-decorated function or class.

    Args:
        func_or_class: A wargs-decorated function or class.
        shell: Shell type ("bash", "zsh", "fish"). Auto-detected if None.

    Returns:
        Shell completion script as a string.

    Raises:
        ValueError: If shell type is unknown or func_or_class is not wargs-decorated.

    Example:
        @wargs
        def cli(name: str):
            ...

        # Auto-detect shell
        script = generate_completion(cli)

        # Specify shell
        script = generate_completion(cli, shell="zsh")
    """
    if shell is None:
        shell = detect_shell()

    spec = get_completion_spec(func_or_class)

    if shell == "bash":
        return generate_bash_completion(spec)
    elif shell == "zsh":
        return generate_zsh_completion(spec)
    elif shell == "fish":
        return generate_fish_completion(spec)
    else:
        raise ValueError(f"Unknown shell type: {shell}. Use 'bash', 'zsh', or 'fish'.")


def get_install_instructions(func_or_class: Any, shell: str | None = None) -> str:
    """Get installation instructions for shell completion.

    Args:
        func_or_class: A wargs-decorated function or class.
        shell: Shell type ("bash", "zsh", "fish"). Auto-detected if None.

    Returns:
        Human-readable installation instructions.

    Example:
        @wargs
        def cli(name: str):
            ...

        print(get_install_instructions(cli))
    """
    if shell is None:
        shell = detect_shell()

    spec = get_completion_spec(func_or_class)
    prog = spec.prog

    if shell == "bash":
        return get_bash_completion_install_instructions(prog)
    elif shell == "zsh":
        return get_zsh_completion_install_instructions(prog)
    elif shell == "fish":
        return get_fish_completion_install_instructions(prog)
    else:
        raise ValueError(f"Unknown shell type: {shell}. Use 'bash', 'zsh', or 'fish'.")


def install_completion(
    func_or_class: Any,
    shell: str | None = None,
    *,
    path: str | None = None,
    stdout: bool = False,
) -> str | None:
    """Install shell completion for a wargs-decorated function or class.

    Args:
        func_or_class: A wargs-decorated function or class.
        shell: Shell type ("bash", "zsh", "fish"). Auto-detected if None.
        path: Custom path to install completion script. If None, uses default.
        stdout: If True, print to stdout instead of installing.

    Returns:
        The path where completion was installed, or None if stdout=True.

    Raises:
        ValueError: If shell type is unknown.
        OSError: If installation fails.

    Example:
        @wargs
        def cli(name: str):
            ...

        # Print to stdout
        install_completion(cli, stdout=True)

        # Install to default location
        install_completion(cli)

        # Install to custom path
        install_completion(cli, path="~/.my-completions/cli.bash")
    """
    import os
    import sys

    if shell is None:
        shell = detect_shell()

    script = generate_completion(func_or_class, shell=shell)
    spec = get_completion_spec(func_or_class)
    prog = spec.prog

    if stdout:
        print(script)
        return None

    # Determine installation path
    if path is None:
        home = os.path.expanduser("~")
        if shell == "bash":
            # Try to install to user's bash completion directory
            path = os.path.join(home, f".{prog}-completion.bash")
        elif shell == "zsh":
            # Install to user's zsh completions
            zsh_dir = os.path.join(home, ".zsh", "completions")
            os.makedirs(zsh_dir, exist_ok=True)
            path = os.path.join(zsh_dir, f"_{prog}")
        elif shell == "fish":
            # Install to user's fish completions
            fish_dir = os.path.join(home, ".config", "fish", "completions")
            os.makedirs(fish_dir, exist_ok=True)
            path = os.path.join(fish_dir, f"{prog}.fish")
        else:
            raise ValueError(f"Unknown shell type: {shell}")
    else:
        path = os.path.expanduser(path)
        # Ensure parent directory exists
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    # Write completion script
    with open(path, "w") as f:
        f.write(script)

    print(f"Completion script installed to: {path}", file=sys.stderr)
    print(get_install_instructions(func_or_class, shell=shell), file=sys.stderr)

    return path
