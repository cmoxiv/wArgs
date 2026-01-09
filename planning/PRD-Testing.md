# PRD: Testing & Quality

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document outlines the testing strategy, quality standards, and quality assurance processes for wArgs. The project follows Test-Driven Development (TDD) with a target of 100% code coverage.

## Testing Philosophy

**Test-Driven Development:**
1. Write failing test first
2. Write minimal code to pass test
3. Refactor while keeping tests green
4. Repeat

**Coverage Target:** 100% line coverage (with justified exclusions)

---

## Testing Framework & Tools

### Core Tools

| Tool | Purpose | Version |
|------|---------|---------|
| pytest | Test runner | ^8.0 |
| pytest-cov | Coverage reporting | ^5.0 |
| hypothesis | Property-based testing | ^6.100 |
| tox | Multi-Python testing | ^4.0 |

### Additional Tools

| Tool | Purpose | Version |
|------|---------|---------|
| pytest-xdist | Parallel test execution | ^3.5 |
| pytest-timeout | Test timeouts | ^2.3 |
| pytest-randomly | Test order randomization | ^3.15 |
| mypy | Static type checking | ^1.8 |
| ruff | Linting and formatting | ^0.5 |

### Configuration

**pyproject.toml:**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "-p", "no:cacheprovider",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
]

[tool.coverage.run]
source = ["wargs"]
branch = true
parallel = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "@overload",
    "raise NotImplementedError",
]
fail_under = 100
show_missing = true

[tool.hypothesis]
deadline = 500
max_examples = 100
```

---

## Test Structure

```
tests/
├── conftest.py               # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── introspection/
│   │   ├── test_types.py         # Type annotation parsing
│   │   ├── test_docstrings.py    # Docstring parsing
│   │   ├── test_mro.py           # MRO traversal
│   │   └── test_signatures.py    # Function signatures
│   ├── builders/
│   │   ├── test_parser.py        # Parser construction
│   │   ├── test_arguments.py     # Argument configuration
│   │   └── test_subcommands.py   # Subcommand handling
│   ├── converters/
│   │   ├── test_builtin.py       # Built-in converters
│   │   └── test_registry.py      # Converter registry
│   ├── completion/
│   │   ├── test_bash.py          # Bash completion
│   │   ├── test_zsh.py           # Zsh completion
│   │   └── test_fish.py          # Fish completion
│   └── test_decorator.py         # @wArgs decorator
├── integration/
│   ├── __init__.py
│   ├── test_basic_cli.py         # Simple CLI scenarios
│   ├── test_subcommands.py       # Subcommand integration
│   ├── test_inheritance.py       # MRO integration
│   ├── test_type_handling.py     # Complex type scenarios
│   └── test_completion.py        # Completion integration
├── e2e/
│   ├── __init__.py
│   ├── test_subprocess.py        # Actual CLI invocation
│   └── fixtures/                 # Example CLI scripts
│       ├── simple_cli.py
│       ├── subcommand_cli.py
│       └── complex_cli.py
└── property/
    ├── __init__.py
    ├── test_type_roundtrip.py    # Type conversion properties
    └── test_parser_generation.py # Parser generation properties
```

---

## Test Categories

### Unit Tests

**Purpose:** Test individual components in isolation.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-TEST-001 | Unit test each module independently | Must |
| REQ-TEST-002 | Mock external dependencies | Must |
| REQ-TEST-003 | Test edge cases and error conditions | Must |
| REQ-TEST-004 | Fast execution (< 1s per test) | Should |

**Example:**

```python
# tests/unit/introspection/test_types.py
import pytest
from typing import Optional, List, Literal
from wargs.introspection.types import resolve_type

class TestResolveType:
    def test_resolves_str(self):
        result = resolve_type(str)
        assert result.type_converter == str
        assert result.nargs is None

    def test_resolves_optional(self):
        result = resolve_type(Optional[int])
        assert result.type_converter == int
        assert result.required is False

    def test_resolves_list(self):
        result = resolve_type(List[str])
        assert result.type_converter == str
        assert result.nargs == "*"

    def test_resolves_literal(self):
        result = resolve_type(Literal["a", "b", "c"])
        assert result.choices == ("a", "b", "c")

    def test_raises_on_unsupported_type(self):
        with pytest.raises(TypeError, match="Unsupported type"):
            resolve_type(object)
```

### Integration Tests

**Purpose:** Test component interactions.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-TEST-005 | Test decorator with real functions | Must |
| REQ-TEST-006 | Test parser with real argument parsing | Must |
| REQ-TEST-007 | Test subcommand routing | Must |
| REQ-TEST-008 | Test MRO with real inheritance | Must |

**Example:**

```python
# tests/integration/test_basic_cli.py
import pytest
from wArgs import wArgs

class TestBasicCLI:
    def test_simple_function_parses_args(self):
        @wArgs
        def greet(name: str, count: int = 1):
            return f"Hello, {name}!" * count

        result = greet(["--name", "World", "--count", "2"])
        assert result == "Hello, World!Hello, World!"

    def test_bool_flag_default_false(self):
        @wArgs
        def process(verbose: bool = False):
            return verbose

        assert process([]) is False
        assert process(["--verbose"]) is True

    def test_missing_required_arg_exits(self):
        @wArgs
        def process(name: str):
            return name

        with pytest.raises(SystemExit) as exc_info:
            process([])
        assert exc_info.value.code == 2
```

### End-to-End Tests (Subprocess)

**Purpose:** Test actual CLI invocation via subprocess.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-TEST-009 | Test CLI via subprocess.run() | Must |
| REQ-TEST-010 | Capture stdout and stderr | Must |
| REQ-TEST-011 | Verify exit codes | Must |
| REQ-TEST-012 | Test --help output | Must |

**Example:**

```python
# tests/e2e/test_subprocess.py
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

class TestSubprocessCLI:
    def test_simple_cli_runs(self):
        result = subprocess.run(
            [sys.executable, FIXTURES / "simple_cli.py", "--name", "World"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Hello, World!" in result.stdout

    def test_help_output(self):
        result = subprocess.run(
            [sys.executable, FIXTURES / "simple_cli.py", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--name" in result.stdout
        assert "NAME" in result.stdout

    def test_missing_arg_error(self):
        result = subprocess.run(
            [sys.executable, FIXTURES / "simple_cli.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "required" in result.stderr.lower()
```

### Property-Based Tests

**Purpose:** Generate test cases automatically to find edge cases.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-TEST-013 | Property tests for type conversion | Should |
| REQ-TEST-014 | Property tests for docstring parsing | Should |
| REQ-TEST-015 | Reproduce failures with seeds | Should |

**Example:**

```python
# tests/property/test_type_roundtrip.py
from hypothesis import given, strategies as st
from wargs.introspection.types import resolve_type

class TestTypeRoundtrip:
    @given(st.integers())
    def test_int_roundtrip(self, value):
        config = resolve_type(int)
        converted = config.type_converter(str(value))
        assert converted == value

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_float_roundtrip(self, value):
        config = resolve_type(float)
        converted = config.type_converter(str(value))
        assert abs(converted - value) < 1e-10

    @given(st.text(min_size=1, max_size=100))
    def test_str_roundtrip(self, value):
        config = resolve_type(str)
        converted = config.type_converter(value)
        assert converted == value
```

---

## Multi-Python Testing

**tox.ini:**

```ini
[tox]
envlist = py38, py39, py310, py311, py312, lint, typecheck

[testenv]
deps =
    pytest>=8.0
    pytest-cov>=5.0
    hypothesis>=6.100
commands =
    pytest --cov=wargs --cov-report=term-missing {posargs}

[testenv:lint]
deps = ruff>=0.5
commands = ruff check wargs tests

[testenv:typecheck]
deps = mypy>=1.8
commands = mypy wargs

[testenv:coverage]
deps =
    pytest>=8.0
    pytest-cov>=5.0
commands =
    pytest --cov=wargs --cov-report=html --cov-fail-under=100
```

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-TEST-016 | Test on Python 3.8, 3.9, 3.10, 3.11, 3.12 | Must |
| REQ-TEST-017 | All tests pass on all Python versions | Must |

---

## Quality Gates

### Pre-Commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### CI Checks

| Check | Tool | Threshold |
|-------|------|-----------|
| Code coverage | pytest-cov | 100% |
| Type checking | mypy | Strict mode |
| Linting | ruff | Zero errors |
| Formatting | ruff format | Zero changes |
| All Python versions | tox | All pass |

---

## Test Data & Fixtures

### Shared Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def temp_script(tmp_path):
    """Create a temporary Python script."""
    def _create(content: str) -> Path:
        script = tmp_path / "script.py"
        script.write_text(content)
        return script
    return _create

@pytest.fixture
def capture_cli_output():
    """Capture CLI output without subprocess."""
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr

    def _capture(func, args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                result = func(args)
                exit_code = 0
            except SystemExit as e:
                result = None
                exit_code = e.code
        return result, stdout.getvalue(), stderr.getvalue(), exit_code
    return _capture
```

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-TEST-001 | Unit test each module | Must | Isolation |
| REQ-TEST-002 | Mock external dependencies | Must | Isolation |
| REQ-TEST-003 | Test edge cases and errors | Must | Robustness |
| REQ-TEST-004 | Fast unit tests (< 1s) | Should | Developer experience |
| REQ-TEST-005 | Integration test decorator | Must | Real functions |
| REQ-TEST-006 | Integration test parsing | Must | Real parsing |
| REQ-TEST-007 | Integration test subcommands | Must | Routing |
| REQ-TEST-008 | Integration test MRO | Must | Inheritance |
| REQ-TEST-009 | E2E test via subprocess | Must | Real invocation |
| REQ-TEST-010 | Capture stdout/stderr | Must | Output verification |
| REQ-TEST-011 | Verify exit codes | Must | Error handling |
| REQ-TEST-012 | Test --help output | Must | User experience |
| REQ-TEST-013 | Property tests for types | Should | Edge cases |
| REQ-TEST-014 | Property tests for docstrings | Should | Edge cases |
| REQ-TEST-015 | Reproducible hypothesis failures | Should | Debugging |
| REQ-TEST-016 | Test Python 3.8-3.12 | Must | Compatibility |
| REQ-TEST-017 | All versions pass | Must | Compatibility |

## Coverage Exclusions

Justified exclusions from 100% coverage target:

```python
# pragma: no cover - only used for type checking
if TYPE_CHECKING:
    from typing import Protocol

# pragma: no cover - CLI entry point
if __name__ == "__main__":
    main()

# pragma: no cover - defensive, should never execute
raise NotImplementedError("This should not be reachable")
```

## Decisions

- [x] **Benchmark suite:** Yes - add performance benchmarks to CI to catch regressions (import time, parse time vs raw argparse)
- [x] **Mutation testing:** No for v1.0 - 100% coverage with property-based testing is sufficient; evaluate mutmut for v2.0

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Flaky tests | CI failures | Deterministic seeds, no timing deps |
| Slow tests | Developer friction | Parallel execution, fast unit tests |
| Python version differences | Compatibility bugs | tox matrix, conditional tests |
