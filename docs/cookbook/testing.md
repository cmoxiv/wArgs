# Testing CLIs

This guide covers strategies for testing wArgs CLI applications.

## Basic Testing

### Test Direct Calls

The simplest approach - call the function directly:

```python
from wargs import wargs

@wargs
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def test_add_direct():
    result = add(a=2, b=3)
    assert result == 5

def test_add_positional():
    result = add(2, 3)
    assert result == 5
```

### Test CLI Parsing

Use `.run()` to test CLI argument parsing:

```python
def test_add_cli():
    result = add.run(["--a", "2", "--b", "3"])
    assert result == 5

def test_add_cli_negative():
    result = add.run(["--a", "-5", "--b", "10"])
    assert result == 5
```

### Test Argument Parsing Only

Use `.parse_args()` to test just the parsing:

```python
def test_parse_args():
    args = add.parse_args(["--a", "10", "--b", "20"])
    assert args.a == 10
    assert args.b == 20
```

## Testing with pytest

### Fixtures for CLI Testing

```python
import pytest
from wargs import wargs

@wargs
def greet(name: str, loud: bool = False) -> str:
    msg = f"Hello, {name}!"
    return msg.upper() if loud else msg

@pytest.fixture
def greet_cli():
    """Provide the greet CLI for testing."""
    return greet

class TestGreetCLI:
    def test_basic(self, greet_cli):
        result = greet_cli.run(["--name", "World"])
        assert result == "Hello, World!"

    def test_loud(self, greet_cli):
        result = greet_cli.run(["--name", "World", "--loud"])
        assert result == "HELLO, WORLD!"

    def test_direct_call(self, greet_cli):
        result = greet_cli(name="Test")
        assert result == "Hello, Test!"
```

### Parameterized Tests

```python
import pytest
from wargs import wargs

@wargs
def calculate(op: str, a: int, b: int) -> int:
    ops = {
        "add": lambda x, y: x + y,
        "sub": lambda x, y: x - y,
        "mul": lambda x, y: x * y,
    }
    return ops[op](a, b)

@pytest.mark.parametrize("op,a,b,expected", [
    ("add", 2, 3, 5),
    ("sub", 10, 4, 6),
    ("mul", 3, 7, 21),
])
def test_calculate(op, a, b, expected):
    result = calculate.run(["--op", op, "--a", str(a), "--b", str(b)])
    assert result == expected
```

## Testing Output

### Capture stdout

```python
from wargs import wargs

@wargs
def echo(message: str) -> None:
    print(message)

def test_echo_output(capsys):
    echo.run(["--message", "Hello"])
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"
```

### Capture stderr

```python
import sys
from wargs import wargs

@wargs
def warn(message: str) -> None:
    print(message, file=sys.stderr)

def test_warn_output(capsys):
    warn.run(["--message", "Warning!"])
    captured = capsys.readouterr()
    assert captured.err == "Warning!\n"
```

## Testing Class-Based CLIs

```python
from wargs import wargs

@wargs
class Calculator:
    def __init__(self, precision: int = 2) -> None:
        self.precision = precision

    def add(self, a: float, b: float) -> None:
        result = round(a + b, self.precision)
        print(result)

def test_calculator_add(capsys):
    Calculator.run(["add", "--a", "1.234", "--b", "2.345"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "3.58"

def test_calculator_precision(capsys):
    Calculator.run(["--precision", "4", "add", "--a", "1.2345", "--b", "2.3456"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "3.5801"
```

## Testing Error Handling

### Test Required Arguments

```python
import pytest
from wargs import wargs

@wargs
def greet(name: str) -> str:
    return f"Hello, {name}!"

def test_missing_required_argument():
    with pytest.raises(SystemExit) as exc_info:
        greet.run([])
    assert exc_info.value.code == 2  # argparse exit code for errors
```

### Test Invalid Arguments

```python
@wargs
def process(count: int) -> int:
    return count

def test_invalid_type():
    with pytest.raises(SystemExit):
        process.run(["--count", "not-a-number"])
```

### Test Conversion Errors

```python
from datetime import datetime
from wargs import wargs, ConversionError

@wargs
def schedule(when: datetime) -> None:
    print(f"Scheduled: {when}")

def test_invalid_datetime():
    with pytest.raises(SystemExit):
        schedule.run(["--when", "invalid-date"])
```

## Testing Help Output

```python
def test_help_output(capsys):
    with pytest.raises(SystemExit) as exc_info:
        greet.run(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Hello" in captured.out or "greet" in captured.out
```

## Integration Testing with subprocess

For full integration testing:

```python
import subprocess
import sys

def test_cli_integration():
    result = subprocess.run(
        [sys.executable, "greet.py", "--name", "World"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Hello, World!" in result.stdout

def test_cli_help():
    result = subprocess.run(
        [sys.executable, "greet.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout
```

## Mocking Dependencies

```python
from unittest.mock import patch, MagicMock
from wargs import wargs

@wargs
def fetch(url: str) -> str:
    import requests
    return requests.get(url).text

def test_fetch_mocked():
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(text="mocked content")
        result = fetch.run(["--url", "http://example.com"])
        assert result == "mocked content"
        mock_get.assert_called_once_with("http://example.com")
```

## Best Practices

1. **Test both CLI and direct calls** - Ensure both work correctly
2. **Use parameterized tests** - Cover multiple input combinations
3. **Test error cases** - Invalid input, missing arguments
4. **Capture output** - Verify what's printed
5. **Test help output** - Ensure documentation is correct
6. **Mock external dependencies** - Keep tests fast and isolated
