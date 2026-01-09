# wArgs Examples

This directory contains example CLI applications built with wArgs.

## Examples

### simple/greet.py

A basic greeting CLI demonstrating:
- Simple function decoration
- Required and optional arguments
- Docstring-based help text

```bash
python simple/greet.py --name World --times 3
```

### typed/process.py

A file processing CLI demonstrating:
- Path type handling
- Literal types for choices
- Boolean flags

```bash
python typed/process.py --input-file data.txt --format json --verbose
```

### subcommands/git_clone.py

A git-like CLI demonstrating:
- Class-based CLI with subcommands
- Global options in `__init__`
- Short flags with `Arg`

```bash
python subcommands/git_clone.py --verbose clone --url https://github.com/user/repo
python subcommands/git_clone.py status
python subcommands/git_clone.py commit -m "Initial commit"
```

### inheritance/mixins.py

A DevOps CLI demonstrating:
- Mixin classes for reusable options
- Multiple inheritance
- Cooperative inheritance pattern

```bash
python inheritance/mixins.py --verbose --dry-run deploy --env prod
python inheritance/mixins.py -c prod.yml build --target frontend
```

### advanced/custom_types.py

An advanced messaging CLI demonstrating:
- Custom type converters
- Argument groups
- Mutually exclusive options
- Hidden arguments

```bash
python advanced/custom_types.py send --to user@example.com --body "Hello"
python advanced/custom_types.py --json list --unread
python advanced/custom_types.py lookup --ip 192.168.1.1
```

## Running Examples

From the repository root:

```bash
# Install wargs in development mode
pip install -e .

# Run any example
python examples/simple/greet.py --name World
```
