# PRD: Integration & Deployment

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document outlines the CI/CD pipeline, build process, and deployment strategy for wArgs. As a Python library published to PyPI, the deployment process focuses on testing, building, and publishing packages.

## CI/CD Platform

**Decision:** GitHub Actions

GitHub Actions is the primary CI/CD platform for wArgs. It offers the best ecosystem for open source Python projects, with extensive community examples and free usage for public repositories.

### Primary: GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest --cov=wargs --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check wargs tests
      - run: ruff format --check wargs tests

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install mypy
      - run: mypy wargs
```

### Alternative: GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - lint
  - publish

test:
  stage: test
  image: python:3.12
  script:
    - pip install -e ".[dev]"
    - pytest --cov=wargs
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.8", "3.9", "3.10", "3.11", "3.12"]

lint:
  stage: lint
  image: python:3.12
  script:
    - pip install ruff mypy
    - ruff check wargs tests
    - mypy wargs
```

---

## Build Process

### Package Build

```bash
# Build source distribution and wheel
python -m build

# Output:
# dist/
#   wargs-1.0.0.tar.gz      # Source distribution
#   wargs-1.0.0-py3-none-any.whl  # Pure Python wheel
```

### pyproject.toml Configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "wargs"
dynamic = ["version"]
description = "Decorator-based argparse automation"
readme = "README.md"
license = "MIT"
requires-python = ">=3.8"
authors = [
    { name = "Your Name", email = "you@example.com" }
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",
]
keywords = ["argparse", "cli", "decorator", "arguments", "command-line"]

[project.urls]
Homepage = "https://github.com/yourname/wargs"
Documentation = "https://wargs.readthedocs.io"
Repository = "https://github.com/yourname/wargs"
Issues = "https://github.com/yourname/wargs/issues"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "hypothesis>=6.100",
    "mypy>=1.8",
    "ruff>=0.5",
    "tox>=4.0",
]
docs = [
    "mkdocs>=1.5",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]

[tool.hatch.version]
path = "wargs/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["wargs"]
```

---

## Release Process

**Strategy:** Manual release with documented checklist.

### Pre-Release Checklist

```markdown
## Release Checklist for v{VERSION}

- [ ] All tests passing on main branch
- [ ] Coverage at 100%
- [ ] No mypy errors
- [ ] No ruff errors
- [ ] CHANGELOG.md updated
- [ ] Version bumped in wargs/_version.py
- [ ] Documentation updated
- [ ] README examples verified
```

### Release Steps

```bash
# 1. Ensure clean working directory
git status  # Should be clean

# 2. Update version
# Edit wargs/_version.py: __version__ = "1.0.0"

# 3. Update CHANGELOG.md
# Add release notes under ## [1.0.0] - YYYY-MM-DD

# 4. Commit version bump
git add wargs/_version.py CHANGELOG.md
git commit -m "Release v1.0.0"

# 5. Create git tag
git tag -a v1.0.0 -m "Release v1.0.0"

# 6. Build package
python -m build

# 7. Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# 8. Verify on Test PyPI
pip install --index-url https://test.pypi.org/simple/ wargs

# 9. Upload to PyPI
python -m twine upload dist/*

# 10. Push tag
git push origin main --tags
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

| Version | Meaning |
|---------|---------|
| MAJOR | Breaking API changes |
| MINOR | New features, backward compatible |
| PATCH | Bug fixes, backward compatible |

**Pre-release tags:**
- `1.0.0a1` - Alpha (incomplete features)
- `1.0.0b1` - Beta (feature complete, testing)
- `1.0.0rc1` - Release candidate (final testing)

---

## Environment Strategy

### Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests locally
pytest

# Run full test matrix
tox

# Run specific Python version
tox -e py312
```

### Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

---

## Quality Gates

### Merge Requirements

Pull requests must pass:

| Check | Requirement |
|-------|-------------|
| Tests | All Python versions pass |
| Coverage | 100% (or justified exclusions) |
| Type check | mypy strict mode passes |
| Lint | ruff check passes |
| Format | ruff format --check passes |

### Release Requirements

Releases require:

| Check | Requirement |
|-------|-------------|
| All merge requirements | ✓ |
| CHANGELOG updated | ✓ |
| Version bumped | ✓ |
| Documentation current | ✓ |
| Test PyPI verification | ✓ |

---

## Monitoring

### Package Health

| Metric | Tool |
|--------|------|
| Downloads | PyPI Stats, pepy.tech |
| Stars/Forks | GitHub |
| Issues | GitHub Issues |
| Test status | CI badges |
| Coverage | Codecov badge |

### Recommended Badges

```markdown
[![PyPI version](https://badge.fury.io/py/wargs.svg)](https://pypi.org/project/wargs/)
[![Python versions](https://img.shields.io/pypi/pyversions/wargs.svg)](https://pypi.org/project/wargs/)
[![Tests](https://github.com/yourname/wargs/workflows/CI/badge.svg)](https://github.com/yourname/wargs/actions)
[![Coverage](https://codecov.io/gh/yourname/wargs/branch/main/graph/badge.svg)](https://codecov.io/gh/yourname/wargs)
[![License](https://img.shields.io/pypi/l/wargs.svg)](https://github.com/yourname/wargs/blob/main/LICENSE)
```

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-INT-001 | CI runs on all PRs | Must | Quality gate |
| REQ-INT-002 | Test matrix for Python 3.8-3.12 | Must | Compatibility |
| REQ-INT-003 | Coverage reporting to Codecov | Should | Visibility |
| REQ-INT-004 | Build source dist and wheel | Must | Distribution |
| REQ-INT-005 | Publish to PyPI manually | Must | Release |
| REQ-INT-006 | Semantic versioning | Must | Predictability |
| REQ-INT-007 | Pre-release versions (alpha/beta/rc) | Should | Testing |
| REQ-INT-008 | Test PyPI verification before release | Should | Safety |
| REQ-INT-009 | Documented release checklist | Must | Process |
| REQ-INT-010 | Quality gate badges in README | Should | Visibility |

## Decisions

- [x] **CI platform:** GitHub Actions (primary), GitLab CI config provided as alternative
- [x] **Release automation:** Manual for v1.0, consider tag-triggered for future versions
- [x] **Changelog generation:** Manual for now, evaluate towncrier if contribution volume increases

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| PyPI credentials exposure | Package hijacking | Use trusted publishing |
| Breaking release | User frustration | Test PyPI first, semver |
| Stale CI config | Undetected failures | Regular CI review |
