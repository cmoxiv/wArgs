# Type System

wArgs automatically converts CLI string arguments to Python types based on type hints.

## Primitive Types

### Strings

```python
@wargs
def greet(name: str) -> None:
    print(f"Hello, {name}!")
```

```bash
$ python app.py --name "World"
Hello, World!
```

### Integers

```python
@wargs
def repeat(count: int) -> None:
    print(f"Count: {count}")
```

```bash
$ python app.py --count 42
Count: 42
```

### Floats

```python
@wargs
def scale(factor: float) -> None:
    print(f"Factor: {factor}")
```

```bash
$ python app.py --factor 3.14
Factor: 3.14
```

### Booleans

Boolean with `False` default becomes a flag:

```python
@wargs
def build(debug: bool = False) -> None:
    print(f"Debug: {debug}")
```

```bash
$ python app.py --debug
Debug: True
```

## Collection Types

### Lists

```python
@wargs
def process(files: list[str]) -> None:
    for f in files:
        print(f"Processing: {f}")
```

```bash
$ python app.py --files a.txt b.txt c.txt
Processing: a.txt
Processing: b.txt
Processing: c.txt
```

With typed elements:

```python
@wargs
def sum_numbers(numbers: list[int]) -> None:
    print(f"Sum: {sum(numbers)}")
```

```bash
$ python app.py --numbers 1 2 3 4 5
Sum: 15
```

### Tuples

Fixed-length tuples:

```python
@wargs
def point(coords: tuple[int, int]) -> None:
    x, y = coords
    print(f"Point: ({x}, {y})")
```

```bash
$ python app.py --coords 10 20
Point: (10, 20)
```

### Sets

```python
@wargs
def tags(items: set[str]) -> None:
    print(f"Unique tags: {items}")
```

```bash
$ python app.py --items foo bar foo baz
Unique tags: {'foo', 'bar', 'baz'}
```

## Optional Types

### Union with None

```python
@wargs
def greet(name: str | None = None) -> None:
    if name:
        print(f"Hello, {name}!")
    else:
        print("Hello, stranger!")
```

```bash
$ python app.py
Hello, stranger!

$ python app.py --name World
Hello, World!
```

### Optional (typing module)

```python
from typing import Optional

@wargs
def greet(name: Optional[str] = None) -> None:
    ...
```

## Literal Types

Use `Literal` for choices:

```python
from typing import Literal

@wargs
def export(format: Literal["json", "xml", "csv"]) -> None:
    print(f"Exporting as {format}")
```

```bash
$ python app.py --help
  --format {json,xml,csv}  ...

$ python app.py --format json
Exporting as json

$ python app.py --format yaml
# Error: invalid choice
```

## Enum Types

Enums provide named choices:

```python
from enum import Enum
from wargs import wargs

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

@wargs
def paint(color: Color) -> None:
    print(f"Painting with {color.value}")
```

```bash
$ python app.py --help
  --color {RED,GREEN,BLUE}  ...

$ python app.py --color RED
Painting with red
```

## Path Types

```python
from pathlib import Path

@wargs
def process(input_file: Path, output_dir: Path) -> None:
    print(f"Input: {input_file}")
    print(f"Output dir: {output_dir}")
    print(f"Exists: {input_file.exists()}")
```

```bash
$ python app.py --input-file data.txt --output-dir ./out
Input: data.txt
Output dir: out
Exists: True
```

## Date and Time Types

### datetime

```python
from datetime import datetime

@wargs
def schedule(when: datetime) -> None:
    print(f"Scheduled for: {when}")
```

```bash
$ python app.py --when "2024-01-15T10:30:00"
Scheduled for: 2024-01-15 10:30:00
```

### date

```python
from datetime import date

@wargs
def birthday(day: date) -> None:
    print(f"Birthday: {day}")
```

```bash
$ python app.py --day 2024-01-15
Birthday: 2024-01-15
```

### time

```python
from datetime import time

@wargs
def alarm(at: time) -> None:
    print(f"Alarm at: {at}")
```

```bash
$ python app.py --at 07:30:00
Alarm at: 07:30:00
```

## Other Types

### UUID

```python
from uuid import UUID

@wargs
def lookup(id: UUID) -> None:
    print(f"Looking up: {id}")
```

```bash
$ python app.py --id "123e4567-e89b-12d3-a456-426614174000"
Looking up: 123e4567-e89b-12d3-a456-426614174000
```

### Decimal

```python
from decimal import Decimal

@wargs
def price(amount: Decimal) -> None:
    print(f"Price: ${amount}")
```

```bash
$ python app.py --amount 19.99
Price: $19.99
```

## Custom Type Converters

Register custom converters for your types:

```python
from wargs import wargs, converter

class EmailAddress:
    def __init__(self, address: str) -> None:
        if "@" not in address:
            raise ValueError("Invalid email")
        self.address = address

@converter(EmailAddress)
def convert_email(value: str) -> EmailAddress:
    return EmailAddress(value)

@wargs
def send(to: EmailAddress) -> None:
    print(f"Sending to: {to.address}")
```

```bash
$ python app.py --to user@example.com
Sending to: user@example.com

$ python app.py --to invalid
# Error: Invalid email
```

## Type Summary

| Type | CLI Representation |
|------|-------------------|
| `str` | String value |
| `int` | Integer value |
| `float` | Float value |
| `bool` (default False) | Flag (`--name`) |
| `list[T]` | Multiple values |
| `tuple[T, ...]` | Fixed number of values |
| `set[T]` | Multiple unique values |
| `T \| None` | Optional value |
| `Literal["a", "b"]` | Choices |
| `Enum` | Enum member names |
| `Path` | File system path |
| `datetime` | ISO 8601 datetime |
| `date` | ISO 8601 date |
| `time` | ISO 8601 time |
| `UUID` | UUID string |
| `Decimal` | Decimal number |
