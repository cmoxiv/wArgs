# PRD: Product Vision

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

wArgs is a Python decorator library that automatically generates argparse-based CLI interfaces through function introspection. It eliminates boilerplate by extracting arguments, types, and documentation directly from decorated functions and their class hierarchies via MRO (Method Resolution Order).

## Problem Statement

Python developers building CLI tools face significant friction:

1. **Boilerplate overhead** - argparse requires verbose, repetitive code for argument definitions
2. **Synchronization burden** - Function signatures and argparse definitions must be kept in sync manually
3. **Documentation duplication** - Docstrings and help text often contain redundant information
4. **Inheritance complexity** - Reusing argument patterns across related commands is cumbersome

## Target Users

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| CLI Tool Author | Developers building command-line applications | Rapid development, full argparse feature support |
| Script Writer | Developers creating quick utility scripts | Minimal boilerplate, zero learning curve |
| Framework Developer | Developers building CLI frameworks/libraries | Extensibility, customization hooks |
| Python Developer | Any developer who uses argparse | Seamless integration with existing code |

## Core Value Proposition

**"Just decorate and you're done."**

wArgs transforms any Python function into a CLI command with a single decorator. No duplicate definitions, no synchronization issues, no boilerplate.

## Key Features (Vision)

| Feature | Description |
|---------|-------------|
| Decorator-based | Single `@wargs` decorator transforms functions to CLI commands |
| Type introspection | Automatically extracts types from annotations for argument parsing |
| Docstring parsing | Extracts help text from function and parameter docstrings |
| MRO traversal | Discovers arguments from parent classes for inheritance-based CLIs |
| Nested subcommands | Support for git-style `command subcommand` hierarchies |
| Shell completion | Auto-generation of bash/zsh/fish completion scripts |

## Competitive Landscape

| Tool | Approach | wArgs Differentiator |
|------|----------|---------------------|
| argparse (stdlib) | Explicit definition | Zero boilerplate with wArgs |
| Click | Decorator-based, own ecosystem | wArgs stays closer to argparse, better for existing codebases |
| Typer | Type hints + Click | wArgs uses MRO for deeper introspection, argparse-native |
| Fire | Automatic from any object | wArgs provides more control, explicit decorator pattern |

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| PyPI Downloads | 1,000+ monthly | Indicates adoption |
| GitHub Stars | 100+ | Community interest |
| LOC Reduction | 60-80% | Measurable productivity gain |
| Feature Coverage | 95% of argparse | Must handle real-world use cases |
| Personal Utility | Daily use | Dogfooding drives quality |

## Release Strategy

- **License:** MIT (simple, permissive, widely used in Python ecosystem)
- **Distribution:** PyPI package (`pip install wargs`)
- **Repository:** Public GitHub repository
- **Documentation:** ReadTheDocs or GitHub Pages

## Decisions

- [x] **Python versions:** 3.8+ (broad compatibility with adequate typing support)
- [x] **Async functions:** Future feature (v2.0+)
- [x] **Tagline:** "Just decorate and you're done."
- [x] **License:** MIT

## Assumptions

- Users are familiar with Python type hints
- Users have basic understanding of argparse concepts
- Primary use case is new CLI development, not retrofitting existing argparse code

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Crowded space (Click, Typer) | Low adoption | Focus on argparse compatibility niche |
| Python version fragmentation | Maintenance burden | Clear version support policy |
| Complex edge cases | Feature creep | Prioritize common patterns, extensibility for edge cases |

## Next Steps

Proceed to Features & User Stories to detail specific functionality.
