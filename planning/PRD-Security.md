# PRD: Security & Privacy

> Project: wArgs
> Generated: 2026-01-09
> Status: Draft

## Overview

This document outlines security considerations for wArgs. As a CLI library, wArgs operates in a different threat model than web applications. The primary security concerns are:

1. Safe handling of user-provided command-line arguments
2. Preventing code injection through type converters
3. Guidance for developers building secure CLIs

## Security Philosophy

**wArgs follows a minimal intervention approach:**

- Type conversion is performed by argparse or registered converters
- No additional input sanitization beyond type conversion
- No special handling for sensitive data
- Security is the responsibility of the application developer

**Rationale:** CLI applications typically run with the user's own permissions in their own environment. Unlike web applications, there's no untrusted remote input. Overly aggressive sanitization would limit legitimate use cases.

---

## Threat Model

### In Scope

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Type confusion | User provides wrong type for argument | argparse type validation |
| Malformed input | Invalid format for complex types | Converter error handling |
| Converter bugs | Custom converters with vulnerabilities | Documentation, examples |

### Out of Scope

| Threat | Description | Rationale |
|--------|-------------|-----------|
| Shell injection | User injects shell commands | User runs their own commands |
| Path traversal | User accesses arbitrary files | User has filesystem access |
| Privilege escalation | Gaining elevated permissions | Application responsibility |
| Denial of service | Resource exhaustion | User controls their own system |

---

## Input Handling

### Type Conversion

wArgs relies on argparse and registered converters for type safety:

```python
@wArgs
def process(count: int, path: Path):
    """Process files."""
    # count is guaranteed to be int (argparse validates)
    # path is guaranteed to be Path object
```

**argparse Validation:**
- Invalid `int` → argparse error
- Missing required args → argparse error
- Unknown arguments → argparse error (unless **kwargs)

### Custom Converters

Developers are responsible for secure converter implementations:

```python
# Potentially unsafe converter
@converter(Path)
def unsafe_path(value: str) -> Path:
    return Path(value)  # No validation

# Safer converter (if needed)
@converter(Path)
def safer_path(value: str) -> Path:
    path = Path(value).resolve()
    if not path.is_relative_to(Path.cwd()):
        raise ValueError("Path must be within current directory")
    return path
```

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-SEC-001 | Rely on argparse for type validation | Must | Standard behavior |
| REQ-SEC-002 | Propagate converter exceptions cleanly | Must | Error visibility |
| REQ-SEC-003 | Document secure converter practices | Should | Developer guidance |

---

## Sensitive Data

wArgs does not provide special handling for sensitive data like passwords or API tokens.

**Recommendations for Developers:**

1. **Use environment variables** for secrets:
   ```python
   import os

   @wArgs
   def deploy(env: str):
       api_key = os.environ.get("API_KEY")
       if not api_key:
           raise SystemExit("API_KEY environment variable required")
   ```

2. **Use configuration files** with restricted permissions:
   ```python
   @wArgs
   def deploy(config: Path = Path("~/.myapp/config.toml")):
       config = config.expanduser()
       # Load secrets from config file
   ```

3. **Use getpass for interactive input**:
   ```python
   import getpass

   @wArgs
   def login(username: str):
       password = getpass.getpass("Password: ")
       # password not visible in command line
   ```

**Not Implemented:**
- `Secret` type annotation
- Masked command-line input
- Automatic environment variable fallback

**Rationale:** These features add complexity and may encourage insecure patterns (passwords on command line). Better to guide developers toward proper secret management.

---

## Code Execution Safety

### Decorator Safety

The `@wArgs` decorator executes at import time, not when user input is received:

```python
@wArgs  # Introspection happens here (import time)
def main(name: str):
    pass

main()  # Argument parsing happens here (runtime)
```

**No user input influences:**
- Decorator behavior
- Function introspection
- Parser construction

### Converter Safety

Converters execute with user-provided strings:

```python
@converter(MyClass)
def parse_myclass(value: str) -> MyClass:
    # 'value' is user-controlled
    return MyClass(value)
```

**Guidance:**
- Never use `eval()` or `exec()` in converters
- Validate input before processing
- Handle exceptions gracefully

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-SEC-004 | No eval/exec in built-in converters | Must | Code safety |
| REQ-SEC-005 | Document converter security practices | Should | Developer guidance |

---

## Dependency Security

### Core Dependencies

wArgs core has zero runtime dependencies, minimizing supply chain risk.

### Optional Dependencies

Optional extras should be:
- Well-maintained packages with security track records
- Pinned to minimum versions in pyproject.toml
- Reviewed for CVEs before adding

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-SEC-006 | Zero runtime dependencies for core | Must | Supply chain safety |
| REQ-SEC-007 | Review optional deps for security | Should | Supply chain safety |

---

## Shell Completion Security

Shell completion scripts execute in the user's shell environment.

**Considerations:**
- Generated scripts should not execute arbitrary code
- Scripts should only complete known arguments/values
- No network requests during completion

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-SEC-008 | Completion scripts don't execute arbitrary code | Must | Shell safety |
| REQ-SEC-009 | No network requests in completion | Must | Privacy/security |

---

## Documentation Requirements

Security documentation should include:

1. **Security considerations section** in main docs
2. **Secure converter examples** in cookbook
3. **Secret management guide** (env vars, config files)
4. **Shell completion safety** notes

**Requirements:**

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-SEC-010 | Security considerations in documentation | Should | User guidance |
| REQ-SEC-011 | Secure coding examples | Should | Best practices |

---

## Requirements Summary

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| REQ-SEC-001 | Rely on argparse for type validation | Must | Standard behavior |
| REQ-SEC-002 | Propagate converter exceptions cleanly | Must | Error visibility |
| REQ-SEC-003 | Document secure converter practices | Should | Developer guidance |
| REQ-SEC-004 | No eval/exec in built-in converters | Must | Code safety |
| REQ-SEC-005 | Document converter security practices | Should | Developer guidance |
| REQ-SEC-006 | Zero runtime dependencies for core | Must | Supply chain safety |
| REQ-SEC-007 | Review optional deps for security | Should | Supply chain safety |
| REQ-SEC-008 | Completion scripts don't execute arbitrary code | Must | Shell safety |
| REQ-SEC-009 | No network requests in completion | Must | Privacy/security |
| REQ-SEC-010 | Security considerations in docs | Should | User guidance |
| REQ-SEC-011 | Secure coding examples | Should | Best practices |

## Compliance

Not applicable - wArgs is a library without data persistence or network capabilities.

## Decisions

- [x] **Warn on sensitive parameter names:** No - too many false positives, document best practices for secrets instead
- [x] **Strict mode:** No - keep security model simple; users who need strict validation can add it in their converters

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Developer writes insecure converter | Application vulnerability | Documentation, examples |
| Malicious completion script injection | Shell compromise | Document risks, sandboxed completion |
