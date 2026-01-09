# PRD: Operations & Support

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document outlines the support model, issue management, and ongoing maintenance strategy for wArgs. As an open-source library with community support, operations focus on documentation, issue triage, and sustainable maintenance.

## Support Model

**Level:** Community Support (no SLA)

| Aspect | Policy |
|--------|--------|
| Response time | No guaranteed response time |
| Support channels | GitHub Issues only |
| Bug priority | Critical bugs prioritized |
| Feature requests | Community-driven prioritization |
| Security issues | Handled privately via security@... or GitHub Security Advisories |

---

## Issue Management

### GitHub Issues

**Single channel for all feedback:**
- Bug reports
- Feature requests
- Questions (if not covered in docs)
- Documentation issues

### Issue Templates

**Bug Report Template:**

```markdown
---
name: Bug Report
about: Report a bug in wArgs
title: "[BUG] "
labels: bug
---

## Description
A clear description of the bug.

## To Reproduce
Steps to reproduce:
1. ...
2. ...

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- wArgs version:
- Python version:
- OS:

## Minimal Reproducible Example
```python
# Paste minimal code that reproduces the issue
```

## Additional Context
Any other relevant information.
```

**Feature Request Template:**

```markdown
---
name: Feature Request
about: Suggest a new feature
title: "[FEATURE] "
labels: enhancement
---

## Problem
What problem does this solve?

## Proposed Solution
Describe the feature you'd like.

## Alternatives Considered
Other solutions you've thought about.

## Use Case
Example of how you'd use this feature.
```

### Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature request |
| `documentation` | Documentation improvement |
| `good first issue` | Good for newcomers |
| `help wanted` | Community help welcome |
| `wontfix` | Not planned to address |
| `duplicate` | Duplicate of existing issue |
| `question` | Question (should be in docs) |
| `priority: critical` | Critical bug, affects many |
| `priority: high` | Important issue |
| `priority: low` | Nice to have |

### Issue Triage Process

```
1. New issue arrives
2. Validate issue (reproducible? clear? duplicate?)
3. Apply labels
4. If bug: attempt to reproduce
5. If feature: evaluate fit with project vision
6. Prioritize based on:
   - Severity (bugs)
   - User demand (features)
   - Alignment with roadmap
7. Respond to user
8. Move to backlog or close
```

---

## Maintenance

### Ongoing Tasks

| Task | Frequency |
|------|-----------|
| Dependency updates | Monthly |
| Security patches | As needed |
| Python version support | On new Python release |
| Bug fixes | As reported |
| Documentation updates | With changes |

### Python Version Policy

| Policy | Description |
|--------|-------------|
| Support new versions | Within 3 months of stable release |
| Drop old versions | 1 year after Python EOL |
| Security backports | Critical only for older versions |

**Example Timeline:**
- Python 3.13 stable: October 2024
- wArgs 3.13 support: By January 2025
- Python 3.8 EOL: October 2024
- wArgs drops 3.8: October 2025

### Dependency Management

```bash
# Check for outdated dependencies
pip list --outdated

# Update dev dependencies
pip install --upgrade pytest pytest-cov hypothesis mypy ruff

# Run tests after updates
tox
```

---

## Documentation

### Documentation Locations

| Content | Location |
|---------|----------|
| README | GitHub repo root |
| API Reference | ReadTheDocs / GitHub Pages |
| Changelog | CHANGELOG.md |
| Contributing | CONTRIBUTING.md |
| Security | SECURITY.md |

### Documentation Maintenance

| Trigger | Action |
|---------|--------|
| New feature | Update docs before merge |
| API change | Update API reference |
| New release | Update changelog |
| Bug fix | Consider adding FAQ entry |

### CONTRIBUTING.md

```markdown
# Contributing to wArgs

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment: `python -m venv .venv`
4. Install dev dependencies: `pip install -e ".[dev]"`
5. Run tests: `pytest`

## Making Changes

1. Create a feature branch
2. Write tests first (TDD)
3. Implement your changes
4. Ensure all tests pass: `tox`
5. Submit a pull request

## Code Style

- Format with `ruff format`
- Lint with `ruff check`
- Type check with `mypy`

## Commit Messages

Use conventional commits:
- `feat: add new feature`
- `fix: fix bug`
- `docs: update documentation`
- `test: add tests`
- `refactor: improve code structure`

## Pull Request Process

1. Update documentation if needed
2. Add changelog entry
3. Ensure CI passes
4. Request review
```

### SECURITY.md

```markdown
# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |
| < 1.0   | No        |

## Reporting a Vulnerability

Please report security vulnerabilities via GitHub Security Advisories
or email security@example.com.

Do NOT open a public issue for security vulnerabilities.

We will respond within 48 hours and work with you to understand
and address the issue.
```

---

## Deprecation Policy

### Deprecation Process

1. **Announce:** Document in changelog and release notes
2. **Warn:** Add `DeprecationWarning` to code
3. **Maintain:** Keep working for at least 2 minor versions
4. **Remove:** Remove in next major version

### Example

```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead. "
        "It will be removed in wArgs 2.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_function()
```

---

## Community

### Code of Conduct

Adopt a standard Code of Conduct (e.g., Contributor Covenant) to ensure
a welcoming community.

### Recognition

- Credit contributors in release notes
- Add contributors to AUTHORS file
- Highlight significant contributions in README

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-OPS-001 | GitHub Issues for bug reports | Must | Single channel |
| REQ-OPS-002 | Issue templates | Should | Quality reports |
| REQ-OPS-003 | Issue labels | Should | Organization |
| REQ-OPS-004 | CONTRIBUTING.md | Must | Contributor guidance |
| REQ-OPS-005 | SECURITY.md | Must | Vulnerability reporting |
| REQ-OPS-006 | Changelog maintenance | Must | Release transparency |
| REQ-OPS-007 | Python version policy | Should | Predictability |
| REQ-OPS-008 | Deprecation warnings | Should | Smooth upgrades |
| REQ-OPS-009 | Code of Conduct | Should | Community health |
| REQ-OPS-010 | Contributor recognition | Should | Community motivation |

## Decisions

- [x] **Discord/Slack:** No - keep it simple, use GitHub Issues for now
- [x] **GitHub Discussions:** Enable if Issue volume becomes unmanageable (questions vs bugs)
- [x] **Bus factor:** Document architecture decisions, accept co-maintainers after v1.0 stable

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Maintainer burnout | Stale project | Clear boundaries, accept help |
| Issue backlog growth | User frustration | Triage ruthlessly, close stale |
| Breaking changes | User disruption | Semver, deprecation warnings |
