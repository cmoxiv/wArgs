# PRD: User Experience

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

wArgs has two distinct user experiences to consider:
1. **Developer Experience (DX)** - The experience of developers using wArgs to build CLIs
2. **End-User Experience (UX)** - The experience of users running CLIs built with wArgs

## Developer Experience

### DX-001: Onboarding

**Principle:** Comprehensive documentation with multiple learning paths.

| Resource | Purpose | Format |
|----------|---------|--------|
| README.md | Quick start, installation, basic example | Markdown |
| Documentation site | Full reference, tutorials, API docs | Sphinx/MkDocs |
| Cookbook | Common patterns and recipes | Code examples |
| Interactive examples | Runnable demos | Python scripts |

**Onboarding Flow:**

```
1. pip install wargs
2. Copy basic example from README
3. Run and see it work
4. Explore documentation for advanced features
5. Reference cookbook for specific patterns
```

**Quick Start Example (README):**

```python
from wArgs import wArgs

@wArgs
def greet(name: str, excited: bool = False):
    """Greet someone by name."""
    msg = f"Hello, {name}!"
    if excited:
        msg = msg.upper()
    print(msg)

if __name__ == "__main__":
    greet()
```

### DX-002: Error Handling (Developer Errors)

**Principle:** Fail fast at import time for decorator misuse.

| Error Type | Behavior | Example |
|------------|----------|---------|
| Invalid type annotation | `TypeError` at import | `def f(x: "invalid"): ...` |
| Unsupported parameter kind | `ValueError` at import | `*args` without handler |
| Conflicting decorators | `ValueError` at import | Incompatible options |
| Missing required metadata | `ValueError` at import | No way to determine type |

**Error Message Format:**

```
wargs.ConfigurationError: Cannot create CLI for function 'process'

  Problem: Parameter 'data' has no type annotation and no default value.

  Solution: Add a type annotation:
    def process(data: str):
              ^^^^^^^^

  Or provide a default value:
    def process(data="default"):
                    ^^^^^^^^^^
```

### DX-003: IDE Integration

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-001 | Full type hints for all public APIs | Must |
| REQ-UX-002 | Docstrings on all public functions/classes | Must |
| REQ-UX-003 | `py.typed` marker for PEP 561 compliance | Must |
| REQ-UX-004 | Compatible with mypy, pyright, pylance | Must |

### DX-004: Debugging Support

| Feature | Description |
|---------|-------------|
| `WARGS_DEBUG=1` | Environment variable for verbose output |
| `.wargs_config` attribute | Access generated argparse config on decorated function |
| `wargs.explain(func)` | Print what wArgs detected from a function |

**Example:**

```python
@wArgs
def mytool(name: str):
    """My tool."""
    pass

# Debug what wArgs detected
print(mytool._wargs_config)
# {'arguments': [{'name': 'name', 'type': str, 'required': True, 'help': '...'}]}

# Or use explain helper
wargs.explain(mytool)
# Detected configuration for 'mytool':
#   Description: My tool.
#   Arguments:
#     --name (str, required): No description found
```

---

## End-User Experience

### UX-001: Help Output

**Principle:** Standard argparse formatting (familiar to Python users).

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-005 | Use argparse's default HelpFormatter | Must |
| REQ-UX-006 | Support `--help` and `-h` flags | Must |
| REQ-UX-007 | Show defaults in help text | Should |
| REQ-UX-008 | Group related arguments logically | Should |

**Example Output:**

```
$ myapp --help
usage: myapp [-h] --name NAME [--count COUNT] [--verbose]

Process data with the given parameters.

options:
  -h, --help     show this help message and exit
  --name NAME    Name of the dataset to process
  --count COUNT  Number of iterations (default: 10)
  --verbose      Enable verbose output
```

### UX-002: Error Messages

**Principle:** Standard argparse error formatting.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-009 | Use argparse's default error formatting | Must |
| REQ-UX-010 | Exit with code 2 on argument errors | Must |
| REQ-UX-011 | Show usage hint on error | Must |

**Example Error:**

```
$ myapp --name
usage: myapp [-h] --name NAME [--count COUNT]
myapp: error: argument --name: expected one argument
```

### UX-003: Subcommand Navigation

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-012 | List subcommands in top-level help | Must |
| REQ-UX-013 | Support `myapp command --help` | Must |
| REQ-UX-014 | Error clearly on unknown subcommand | Must |

**Example:**

```
$ myapp --help
usage: myapp [-h] {init,build,deploy} ...

My application.

subcommands:
  {init,build,deploy}
    init               Initialize a new project
    build              Build the project
    deploy             Deploy to production

$ myapp unknown
usage: myapp [-h] {init,build,deploy} ...
myapp: error: argument command: invalid choice: 'unknown' (choose from 'init', 'build', 'deploy')
```

### UX-004: Shell Completion

**User Flow:**

```
1. User runs: myapp install-completion
2. wArgs detects shell (bash/zsh/fish)
3. Writes completion script to appropriate location
4. Instructs user to restart shell or source file
5. Completions work on next shell session
```

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-015 | Detect current shell automatically | Should |
| REQ-UX-016 | Support `--shell` override | Should |
| REQ-UX-017 | Print success message with instructions | Should |
| REQ-UX-018 | Handle permission errors gracefully | Should |

---

## Documentation Requirements

### Documentation Structure

```
docs/
├── index.md                 # Landing page
├── getting-started/
│   ├── installation.md      # pip install, requirements
│   ├── quickstart.md        # First CLI in 5 minutes
│   └── tutorial.md          # Step-by-step guide
├── guide/
│   ├── basic-usage.md       # Core decorator usage
│   ├── type-system.md       # Supported types
│   ├── docstrings.md        # Docstring parsing
│   ├── subcommands.md       # Class-based and decorator patterns
│   ├── inheritance.md       # MRO and mixins
│   ├── advanced.md          # Custom types, actions, groups
│   └── shell-completion.md  # Completion scripts
├── cookbook/
│   ├── patterns.md          # Common CLI patterns
│   ├── migration.md         # Migrating from Click/argparse
│   └── testing.md           # Testing wArgs CLIs
├── api/
│   ├── decorators.md        # @wArgs, @wArgs.group, etc.
│   ├── types.md             # Arg, type converters
│   └── utilities.md         # Helper functions
└── changelog.md             # Version history
```

### Documentation Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-019 | README with complete quickstart example | Must |
| REQ-UX-020 | API reference for all public symbols | Must |
| REQ-UX-021 | At least 10 cookbook recipes | Should |
| REQ-UX-022 | Migration guide from Click | Should |
| REQ-UX-023 | Migration guide from raw argparse | Should |

---

## Accessibility

Since wArgs produces CLI applications, accessibility considerations focus on terminal compatibility:

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-UX-024 | No hard-coded ANSI colors in default mode | Must |
| REQ-UX-025 | Respect `NO_COLOR` environment variable | Should |
| REQ-UX-026 | Screen reader friendly help output | Should |

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-UX-001 | Full type hints for public APIs | Must | IDE support |
| REQ-UX-002 | Docstrings on public APIs | Must | IDE support |
| REQ-UX-003 | PEP 561 py.typed marker | Must | Type checker support |
| REQ-UX-004 | mypy/pyright compatible | Must | Type checker support |
| REQ-UX-005 | Standard argparse HelpFormatter | Must | Familiar UX |
| REQ-UX-006 | Support --help and -h | Must | Standard behavior |
| REQ-UX-007 | Show defaults in help | Should | User convenience |
| REQ-UX-008 | Logical argument grouping | Should | Organized help |
| REQ-UX-009 | Standard argparse errors | Must | Familiar UX |
| REQ-UX-010 | Exit code 2 on arg errors | Must | Standard behavior |
| REQ-UX-011 | Usage hint on error | Must | User guidance |
| REQ-UX-012 | List subcommands in help | Must | Discoverability |
| REQ-UX-013 | Subcommand --help | Must | Discoverability |
| REQ-UX-014 | Clear unknown subcommand error | Must | User guidance |
| REQ-UX-015 | Auto-detect shell for completion | Should | User convenience |
| REQ-UX-016 | --shell override | Should | Flexibility |
| REQ-UX-017 | Completion success message | Should | User guidance |
| REQ-UX-018 | Handle permission errors | Should | Robustness |
| REQ-UX-019 | README quickstart | Must | Onboarding |
| REQ-UX-020 | API reference | Must | Documentation |
| REQ-UX-021 | 10+ cookbook recipes | Should | Practical examples |
| REQ-UX-022 | Click migration guide | Should | Adoption |
| REQ-UX-023 | argparse migration guide | Should | Adoption |
| REQ-UX-024 | No hardcoded ANSI colors | Must | Accessibility |
| REQ-UX-025 | Respect NO_COLOR | Should | Accessibility |
| REQ-UX-026 | Screen reader friendly | Should | Accessibility |

## Decisions

- [x] **CLI scaffolding tool:** No - wArgs is a library, keep it simple; users just add the decorator
- [x] **Video tutorials:** No for v1.0 - focus on written docs with runnable examples; evaluate video for v2.0 based on demand

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Documentation gets stale | Frustrated developers | Doctest examples, CI checks |
| Error messages too terse | Poor debugging experience | Include source location hints |
