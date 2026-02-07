# Framework Integrations

Learn how to integrate wArgs with popular Python frameworks and tools.

## Available Integrations

### 🎯 [Django](django.md)
Create custom Django management commands with wArgs. Features:
- Type-safe command arguments
- Auto-generated help from docstrings
- Less boilerplate than BaseCommand
- Full Django ORM access
- Database migrations and seeding
- Cache management

**Use cases**: Data migration, database maintenance, cache management, custom admin tools

### 🌶️ [Flask](flask.md)
Build Flask CLI commands with wArgs integration. Includes:
- Flask app context handling
- Database initialization and seeding
- Route inspection
- Configuration management

**Use cases**: Database setup, seeding, admin tasks, deployment scripts

## Coming Soon

### ⚡ FastAPI
Create CLI tools for FastAPI applications:
- Database migrations
- API testing utilities
- Data seeding
- Admin commands

### 🗄️ SQLAlchemy
Advanced database schema management:
- Schema inspection
- Migration generation
- Data validation
- Multi-database support

### 📊 Pydantic
Enhanced data validation and configuration:
- Config file validation
- API request testing
- Data transformation
- Schema generation

## Integration Patterns

### App Context Pattern
```python
@wArgs
class AppCLI:
    def __init__(self, app_context: bool = True):
        if app_context:
            with app.app_context():
                # Commands run in app context
                pass
```

### Database Pattern
```python
def init_db(self):
    """Initialize database."""
    with app.app_context():
        db.create_all()
```

### Configuration Pattern
```python
def __init__(self, config: Path = Path("config.py")):
    app.config.from_pyfile(config)
```

## Best Practices

1. **App Context** - Run commands in the app context when needed
2. **Environment Variables** - Use environment-specific configs
3. **Error Handling** - Gracefully handle database/network errors
4. **Testing** - Test CLI commands like regular code
5. **Documentation** - Use docstrings for auto-generated help

## Related

- [User Guide](../guide/basic-usage.md) - wArgs fundamentals
- [API Reference](../api/decorators.md) - Decorator documentation
- [Tutorials](../tutorials/index.md) - Step-by-step guides

## Contributing

Have an integration guide to share? We welcome contributions for:
- Other web frameworks (Tornado, Pyramid, etc.)
- ORMs (Peewee, Tortoise, etc.)
- Task queues (Celery, RQ, etc.)
- Testing frameworks (pytest plugins, etc.)

See [CONTRIBUTING.md](https://github.com/cmoxiv/wArgs/blob/main/CONTRIBUTING.md) for guidelines.
