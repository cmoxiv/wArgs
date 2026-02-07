# wArgs Roadmap

## Vision

Simplify Python CLI development through intelligent introspection and type-aware argument parsing.

## Current Status (v1.0)

- 600+ passing tests
- Full decorator-based API (`@wArgs`)
- Comprehensive type system with custom converters
- Shell completion (bash/zsh/fish)
- Class-based subcommands with method introspection
- Inheritance support with MRO traversal
- Dictionary parameter expansion to CLI arguments
- Argument prefixing for namespacing
- Plugin system via entry points

## Planned Features

### v1.1 - Enhanced Shell Integration

- [ ] Dynamic completion from external sources (files, APIs, databases)
- [ ] PowerShell completion support
- [ ] Completion for custom type values (Enum, Literal, custom converters)
- [ ] Context-aware completion (suggest valid paths, command history)
- [ ] Completion caching and performance optimization

### v1.2 - Extended Type Support

- [ ] TypedDict support for structured configuration
- [ ] Pydantic model integration for validation
- [ ] attrs and dataclass enhancements (nested structures)
- [ ] Union type handling improvements (better error messages)
- [ ] Generic container types: Better List[T], Dict[K,V], Set[T] handling
- [ ] Protocol support for duck typing
- [ ] NewType and type aliases

### v1.3 - Configuration & Persistence

- [ ] Config file support (TOML/YAML/JSON)
- [ ] Environment variable integration with precedence
- [ ] Configuration merging and precedence rules (env < config < CLI)
- [ ] Save/load argument presets
- [ ] XDG Base Directory specification compliance
- [ ] Config validation using type hints
- [ ] Generate example config from decorated function

### v2.0 - Interactive & Advanced Features

- [ ] Interactive prompt mode (like inquirer.py)
- [ ] Async function support (`async def` decorated functions)
- [ ] Middleware/plugin hooks (pre-parse, post-parse, pre-execute)
- [ ] Colorized help output (optional, with NO_COLOR support)
- [ ] Man page generation from docstrings
- [ ] Rich terminal output integration
- [ ] Progress bars and spinners for long-running commands

### v2.1 - Developer Experience

- [ ] Better error messages with suggestions (typo correction)
- [ ] Debug mode with step-through argument parsing
- [ ] Visual argument tree explorer (show hierarchy)
- [ ] Performance profiling tools (parsing overhead, conversion time)
- [ ] Argument validation reports
- [ ] CLI scaffolding tool (generate boilerplate from templates)
- [ ] Live reload during development

### Community Ideas

- [ ] FastAPI-style dependency injection for CLI arguments
- [ ] Multi-language CLI (i18n) with gettext support
- [ ] CLI testing framework integration (snapshot testing, fixtures)
- [ ] Auto-generated web UI for CLIs (like FastAPI docs)
- [ ] GraphQL-style query interface for complex CLIs
- [ ] REPL mode for interactive CLI sessions
- [ ] Telemetry and usage analytics (opt-in)

## Feature Brainstorming

### Configuration Management

**Multi-source config**
- Merge from files, env vars, CLI args with clear precedence
- Support multiple config file locations (system, user, project)
- Watch config files for changes and reload

**Config validation**
- Use type hints to validate config files at startup
- Provide detailed error messages for invalid config
- Schema generation for IDE autocomplete

**Config generation**
- Generate example config from decorated function
- Document all options with descriptions from docstrings
- Show default values and valid ranges

### Type System Enhancements

**JSON Schema integration**
- Generate JSON Schema from type hints
- Validate against JSON Schema for external data
- Generate TypeScript types from Python types

**Protocol support**
- Duck typing for CLI arguments
- Allow any object implementing a protocol
- Runtime protocol checking with helpful errors

**Generic container types**
- Better List[T], Dict[K,V] handling with nested validation
- Support for custom collection types
- Automatic flattening/expansion of complex structures

### Developer Tools

**CLI scaffolding**
- Generate boilerplate from templates
- Create subcommand structure automatically
- Generate tests from CLI definition

**Argument diff**
- Compare CLI changes between versions
- Show what arguments were added/removed/changed
- Generate migration guides

**Usage analytics**
- Track which commands/args are most used
- Identify unused features
- Performance metrics per command

### Testing & Quality

**Snapshot testing**
- Capture/replay CLI interactions
- Test output formatting and help text
- Regression testing for CLI changes

**Fuzzing support**
- Generate random valid inputs based on types
- Test edge cases automatically
- Property-based testing integration

**Type coverage report**
- Show which args lack type hints
- Identify missing converters
- Suggest type annotations

### Documentation

**Auto-generated tutorials**
- Create docs from docstrings
- Step-by-step guides from command definitions
- Code examples extracted from tests

**Interactive examples**
- Try CLI in browser (WASM/PyScript)
- Live playground for testing commands
- Share CLI examples via URL

**Video generation**
- Auto-create demo videos from CLI definitions
- Screen recording automation
- GIF generation for README

### Advanced Features

**Command chaining**
- Pipe output between commands
- Unix-style command composition
- Lazy evaluation of command chains

**Plugin system expansion**
- Third-party converter plugins
- Custom completion providers
- Middleware ecosystem

**Performance optimization**
- Lazy loading of modules
- Incremental parsing for large CLIs
- Caching of introspection results

**Security features**
- Input sanitization and validation
- Secret parameter masking in logs
- Rate limiting for command execution
- Audit logging for sensitive commands

### Ecosystem Integration

**Framework integrations**
- Django management commands
- Flask CLI integration
- FastAPI admin commands
- SQLAlchemy schema tools

**Cloud platform support**
- AWS Lambda CLI handlers
- Google Cloud Functions
- Azure Functions
- CLI deployment automation

**Container integration**
- Docker ENTRYPOINT generation
- Kubernetes job definitions
- CLI containerization helpers

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md#suggesting-features) for how to propose features.

## Feedback

Have ideas not listed here? We'd love to hear them!

- Open a [Feature Request](https://github.com/cmoxiv/wArgs/issues/new?template=feature_request.yml)
- Start a [Discussion](https://github.com/cmoxiv/wArgs/discussions)
- Comment on existing issues with your use case

---

*This roadmap is a living document and will evolve based on community feedback and project priorities.*
