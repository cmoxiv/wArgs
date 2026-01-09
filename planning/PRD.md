# Project Requirement Document

> **Project:** wArgs
> **Version:** 1.0
> **Date:** 2026-01-09
> **Status:** Draft

---

## Executive Summary

**wArgs** is a Python decorator library that automatically generates argparse-based CLI interfaces through function introspection. It eliminates boilerplate by extracting arguments, types, and documentation directly from decorated functions and their class hierarchies via MRO (Method Resolution Order).

**Tagline:** *"Just decorate and you're done."*

### Key Value Propositions

1. **Zero boilerplate** - Single decorator transforms functions into CLI commands
2. **Full type support** - Leverages Python type hints for argument validation
3. **Docstring parsing** - Extracts help text from existing documentation
4. **Inheritance support** - MRO traversal for reusable argument patterns
5. **argparse compatibility** - Stays close to the standard library

### Target Users

- CLI tool authors building command-line applications
- Script writers creating quick utility scripts
- Framework developers building CLI-based libraries
- Any Python developer who uses argparse

---

## Table of Contents

1. [Product Vision](PRD-Product.md)
2. [Features & User Stories](PRD-Features.md)
3. [User Experience](PRD-UX.md)
4. [Technical Architecture](PRD-Technical.md)
5. [Backend Requirements](PRD-Backend.md)
6. [Frontend Requirements](PRD-Frontend.md)
7. [Security & Privacy](PRD-Security.md)
8. [Testing & Quality](PRD-Testing.md)
9. [Integration & Deployment](PRD-Integration.md)
10. [Operations & Support](PRD-Operations.md)

---

## Key Requirements Summary

### Must-Have (v1.0)

| ID | Requirement | Aspect |
|----|-------------|--------|
| REQ-FEAT-001 | Basic `@wArgs` decorator | Features |
| REQ-FEAT-002 | Full Python type hint support (str, int, float, bool, Path, collections, Optional, Union, Literal, Enum) | Features |
| REQ-FEAT-003 | Custom class type support via constructors or converters | Features |
| REQ-FEAT-004 | Docstring parsing (Google, NumPy, Sphinx auto-detect) | Features |
| REQ-FEAT-005 | Class-based subcommands (methods as subcommands) | Features |
| REQ-FEAT-006 | MRO traversal for inherited parameters | Features |
| REQ-FEAT-007 | Full argparse feature parity | Features |
| REQ-BE-008 | `*args` captures remaining positional arguments | Backend |
| REQ-BE-010 | `**kwargs` captures unknown `--key value` pairs | Backend |
| REQ-TECH-001 | Support Python 3.8+ | Technical |
| REQ-TECH-002 | Zero runtime dependencies (core) | Technical |
| REQ-TECH-004 | Plugin architecture via entry points | Technical |
| REQ-TEST-016 | Test on Python 3.8-3.12 | Testing |
| REQ-UX-005 | Standard argparse HelpFormatter | UX |

### Should-Have (v1.x)

| ID | Requirement | Aspect |
|----|-------------|--------|
| REQ-FEAT-008 | Shell completion with auto-install (bash/zsh/fish) | Features |
| REQ-FEAT-009 | Nested decorator pattern (`@wArgs.group()`, `@command()`) | Features |
| REQ-FE-005 | `@wArgs.group()` creates command groups | Frontend |
| REQ-TECH-005 | < 5ms import overhead per function | Technical |
| REQ-TECH-006 | < 10% parse time overhead vs argparse | Technical |

### Future (v2.0+)

| ID | Requirement | Aspect |
|----|-------------|--------|
| REQ-FEAT-011 | Config file support (TOML/YAML/JSON) | Features |
| REQ-FEAT-012 | Module-based command hierarchy | Features |
| REQ-BE-043 | Async function support | Backend |

---

## Technical Overview

### Architecture

```
wArgs Package Structure:
├── wargs/
│   ├── core/           # Main decorator and configuration
│   ├── introspection/  # Type, docstring, MRO analysis
│   ├── builders/       # ArgumentParser construction
│   ├── completion/     # Shell completion generation
│   ├── plugins/        # Plugin system
│   └── converters/     # Type converters
```

### Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Python versions | 3.8+ | Broad compatibility while having adequate typing |
| Dependencies | Zero (core) | Minimize supply chain risk |
| Parser | argparse | Standard library, familiar to users |
| Type hints | Annotated + Arg() | Clean, explicit configuration |
| Subcommands | Class-based + decorator | Flexibility for different patterns |

### API Example

```python
from typing import Annotated
from wArgs import wArgs, Arg

@wArgs
def process(
    input_file: Annotated[Path, Arg(positional=True, metavar="FILE")],
    output: Annotated[Path, Arg("-o", "--output")] = None,
    verbose: Annotated[int, Arg("-v", action="count")] = 0,
):
    """Process a file with optional output and verbosity."""
    if verbose > 0:
        print(f"Processing {input_file}")
    # ... implementation

if __name__ == "__main__":
    process()
```

---

## Open Questions (Consolidated)

### Product & Features
- [x] What Python versions should be supported? **Decision: 3.8+**
- [x] Should wArgs support async functions? **Decision: Future feature (v2.0+)**
- [x] What's the tagline? **Decision: "Just decorate and you're done."**

### Technical
- [x] Should positional arguments be opt-in or opt-out? **Decision: Opt-in via `Arg(positional=True)`** - matches argparse convention where flags are default
- [x] How to handle `*args` and `**kwargs`? **Decision: *args captures remaining positional, **kwargs captures unknown --key value pairs**
- [x] Should there be a compiled/Cython option for performance? **Decision: No** - focus on clean Python, optimize algorithms instead

### UX
- [x] Should there be a `wargs` CLI tool for project scaffolding? **Decision: No** - keep it simple, just a library
- [x] Should `Arg` be spelled `Argument` for clarity? **Decision: Keep `Arg`** - shorter, used frequently in annotations, matches CLI convention

### Operations
- [x] Which CI platform to use? **Decision: GitHub Actions** - better ecosystem for open source Python
- [x] Should there be a Discord/Slack for community discussion? **Decision: No** - GitHub Discussions if needed, keep it simple for now

### Licensing & Completion
- [x] License choice? **Decision: MIT** - simpler, widely used in Python ecosystem
- [x] How should decorated functions behave when called programmatically vs from CLI? **Decision: See PRD-Frontend Invocation Behavior**
- [x] Should `install-completion` be auto-added to simple functions? **Decision: No** - only for classes/groups with subcommands; provide `wargs.install_completion(func)` utility for simple functions

---

## Risk Summary

| Risk | Impact | Mitigation | Priority |
|------|--------|------------|----------|
| Crowded space (Click, Typer) | Low adoption | Focus on argparse compatibility | High |
| Type introspection edge cases | Broken CLIs | Comprehensive test suite | High |
| Python version fragmentation | Maintenance burden | Clear version policy | Medium |
| Maintainer burnout | Stale project | Clear boundaries, accept help | Medium |
| Complex MRO scenarios | Unexpected behavior | Document clearly, warn on conflicts | Medium |

---

## Implementation Roadmap

### Phase 1: Core (v1.0)
- [ ] Basic `@wArgs` decorator
- [ ] Type introspection engine
- [ ] Docstring parsing (all formats)
- [ ] Class-based subcommands
- [ ] MRO traversal
- [ ] Plugin architecture (converter registration via entry points)
- [ ] Full test suite (100% coverage)
- [ ] Documentation site
- [ ] PyPI release

### Phase 2: Enhancements (v1.x)
- [ ] Shell completion generation
- [ ] `@wArgs.group()` decorator pattern
- [ ] Performance optimization
- [ ] Additional docstring formats

### Phase 3: Extensions (v2.0)
- [ ] Config file support
- [ ] Module-based commands
- [ ] Async function support
- [ ] Enhanced error messages

---

## Next Steps

1. **Review this PRD** - Ensure all requirements are accurate
2. **Prioritize open questions** - Resolve blockers before implementation
3. **Create implementation plan** - Break Phase 1 into detailed tasks
4. **Set up project structure** - Repository, CI/CD, documentation
5. **Begin TDD implementation** - Start with core decorator

---

## Appendices

### Glossary

| Term | Definition |
|------|------------|
| argparse | Python standard library for CLI argument parsing |
| MRO | Method Resolution Order - Python's class inheritance order |
| Decorator | Python pattern for modifying functions/classes |
| Type hint | Python annotation for variable/parameter types |
| Subcommand | Nested command (e.g., `git commit`, `git push`) |

### Reference Documents

- [Python argparse documentation](https://docs.python.org/3/library/argparse.html)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 593 - Flexible function and variable annotations](https://peps.python.org/pep-0593/)
- [Click documentation](https://click.palletsprojects.com/) (competitor reference)
- [Typer documentation](https://typer.tiangolo.com/) (competitor reference)

### Interview Notes

PRD generated through structured interviews covering:
- Product Vision (core problem, target users, success metrics)
- Features (type support, subcommands, shell completion)
- User Experience (developer onboarding, error handling)
- Technical Architecture (package structure, performance)
- Backend (type resolution, MRO, converters)
- Frontend (public API design)
- Security (input handling, dependencies)
- Testing (TDD, 100% coverage, multi-Python)
- Integration (CI/CD, PyPI release)
- Operations (community support, maintenance)

---

*Generated with Claude Code PRD Generator*
