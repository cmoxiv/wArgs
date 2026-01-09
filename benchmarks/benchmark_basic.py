#!/usr/bin/env python3
"""Basic performance benchmarks for wArgs.

Run with: python benchmarks/benchmark_basic.py
"""

from __future__ import annotations

import argparse
import time
from typing import Literal

from wargs import Arg, wargs
from wargs.introspection.signatures import extract_function_info
from wargs.introspection.types import resolve_type


def benchmark(name: str, iterations: int = 1000):
    """Decorator to benchmark a function."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            for _ in range(iterations):
                result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            avg = elapsed / iterations * 1000  # ms
            print(f"{name}: {avg:.4f} ms/op ({iterations} iterations)")
            return result

        return wrapper

    return decorator


# Sample functions for benchmarking
def simple_function(name: str, count: int = 1) -> str:
    """A simple function."""
    return f"{name}: {count}"


def complex_function(
    name: str,
    output: Literal["json", "csv", "text"] = "text",
    verbose: bool = False,
    count: int = 10,
    tags: list[str] = [],
) -> dict:
    """A complex function with many parameters."""
    return {"name": name, "output": output, "verbose": verbose, "count": count}


@benchmark("extract_function_info (simple)")
def bench_extract_simple():
    """Benchmark extract_function_info for simple function."""
    return extract_function_info(simple_function)


@benchmark("extract_function_info (complex)")
def bench_extract_complex():
    """Benchmark extract_function_info for complex function."""
    return extract_function_info(complex_function)


@benchmark("resolve_type (str)")
def bench_resolve_str():
    """Benchmark type resolution for str."""
    return resolve_type(str)


@benchmark("resolve_type (list[str])")
def bench_resolve_list():
    """Benchmark type resolution for list[str]."""
    return resolve_type(list[str])


@benchmark("resolve_type (Literal)")
def bench_resolve_literal():
    """Benchmark type resolution for Literal."""
    return resolve_type(Literal["a", "b", "c"])


@benchmark("@wargs decoration")
def bench_wargs_decoration():
    """Benchmark applying @wargs decorator."""

    @wargs
    def temp_func(name: str, count: int = 1) -> str:
        return f"{name}: {count}"

    return temp_func


@benchmark("parser building")
def bench_parser_building():
    """Benchmark building ArgumentParser."""

    @wargs
    def temp_func(name: str, count: int = 1, verbose: bool = False) -> str:
        return f"{name}: {count}"

    # Force parser construction
    return temp_func.parser


@benchmark("argument parsing", iterations=100)
def bench_argument_parsing():
    """Benchmark parsing arguments."""

    @wargs
    def temp_func(name: str, count: int = 1, verbose: bool = False) -> str:
        return f"{name}: {count}"

    return temp_func.parse_args(["--name", "test", "--count", "5"])


@benchmark("full run cycle", iterations=100)
def bench_full_run():
    """Benchmark full decorator + parse + run cycle."""

    @wargs
    def temp_func(name: str, count: int = 1, verbose: bool = False) -> str:
        return f"{name}: {count}"

    return temp_func.run(["--name", "test", "--count", "5"])


@benchmark("argparse baseline (for comparison)", iterations=100)
def bench_argparse_baseline():
    """Benchmark raw argparse for comparison."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(["--name", "test", "--count", "5"])


def main():
    """Run all benchmarks."""
    print("=" * 60)
    print("wArgs Performance Benchmarks")
    print("=" * 60)
    print()

    print("Introspection Benchmarks:")
    print("-" * 40)
    bench_extract_simple()
    bench_extract_complex()
    print()

    print("Type Resolution Benchmarks:")
    print("-" * 40)
    bench_resolve_str()
    bench_resolve_list()
    bench_resolve_literal()
    print()

    print("Decorator Benchmarks:")
    print("-" * 40)
    bench_wargs_decoration()
    bench_parser_building()
    print()

    print("Runtime Benchmarks:")
    print("-" * 40)
    bench_argument_parsing()
    bench_full_run()
    bench_argparse_baseline()
    print()

    print("=" * 60)
    print("Benchmarks complete!")


if __name__ == "__main__":
    main()
