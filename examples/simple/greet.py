#!/usr/bin/env python3
"""Simple greeting CLI example.

Usage:
    python greet.py --name World
    python greet.py --name Alice --greeting Hi
    python greet.py --name Bob --times 3
"""

from wArgs import wArgs


@wArgs
def greet(name: str, greeting: str = "Hello", times: int = 1) -> None:
    """Greet someone.

    Args:
        name: The name of the person to greet.
        greeting: The greeting to use.
        times: Number of times to greet.
    """
    for _ in range(times):
        print(f"{greeting}, {name}!")


if __name__ == "__main__":
    greet()
