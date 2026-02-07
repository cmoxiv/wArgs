# Django Management Commands with wArgs

Integrate wArgs with Django to create powerful custom management commands.

## Why wArgs for Django?

Django's built-in `BaseCommand` is verbose and requires lots of boilerplate. With wArgs:
- ✅ **Type-safe arguments** from type hints
- ✅ **Auto-generated help** from docstrings
- ✅ **Less code** - just decorate and go
- ✅ **Full Django ORM access** in your functions

## Basic Integration

### Step 1: Create Management Command

Create `myapp/management/commands/process_users.py`:

```python
from django.core.management.base import BaseCommand
from wArgs import wArgs
from myapp.models import User
from typing import Literal

@wArgs
def process_users(
    status: Literal["active", "inactive", "all"] = "all",
    limit: int = 100,
    dry_run: bool = False,
):
    """Process user accounts.

    Args:
        status: Filter users by status
        limit: Maximum number of users to process
        dry_run: Preview changes without committing
    """
    # Query users
    users = User.objects.all()

    if status != "all":
        users = users.filter(status=status)

    users = users[:limit]

    print(f"Processing {users.count()} users...")

    for user in users:
        print(f"  • {user.username} ({user.email})")

        if not dry_run:
            # Perform actual processing
            user.last_processed = timezone.now()
            user.save()

    if dry_run:
        print("\n[DRY RUN] No changes committed")
    else:
        print(f"\n✓ Processed {users.count()} users")

class Command(BaseCommand):
    help = "Process user accounts"

    def handle(self, *args, **options):
        # Let wArgs handle argument parsing
        process_users()
```

### Step 2: Run Command

```bash
python manage.py process_users --help
python manage.py process_users --process_users-status active --process_users-limit 50
python manage.py process_users --process_users-dry-run
```

## Advanced Pattern: Direct Django Integration

For better integration, create a base class:

```python
# myapp/management/base.py
from django.core.management.base import BaseCommand
from wArgs import wArgs
import sys

class WargsCommand(BaseCommand):
    """Base class for wArgs-powered Django commands."""

    # Override in subclass
    cli_function = None

    def handle(self, *args, **options):
        if self.cli_function is None:
            raise NotImplementedError("cli_function must be set")

        # Run the wArgs function
        self.cli_function()
```

Now create commands more easily:

```python
# myapp/management/commands/export_data.py
from myapp.management.base import WargsCommand
from wArgs import wArgs
from pathlib import Path
import json

@wArgs
def export_data(
    model: str,
    output: Path,
    format: str = "json",
):
    """Export model data to file.

    Args:
        model: Model name to export (e.g., 'User', 'Article')
        output: Output file path
        format: Export format (json, csv)
    """
    from django.apps import apps

    # Get model class
    try:
        Model = apps.get_model('myapp', model)
    except LookupError:
        print(f"Error: Model '{model}' not found")
        return

    # Export data
    data = list(Model.objects.values())

    if format == "json":
        output.write_text(json.dumps(data, indent=2, default=str))
    elif format == "csv":
        import csv
        if data:
            with output.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    print(f"✓ Exported {len(data)} {model} records to {output}")

class Command(WargsCommand):
    help = "Export model data"
    cli_function = export_data
```

## Real-World Examples

### Data Migration Command

```python
@wArgs
def migrate_data(
    source_db: str,
    batch_size: int = 1000,
    skip_validation: bool = False,
):
    """Migrate data from legacy database.

    Args:
        source_db: Source database alias (in settings.DATABASES)
        batch_size: Number of records per batch
        skip_validation: Skip data validation
    """
    from django.db import connections
    from myapp.models import Product

    cursor = connections[source_db].cursor()
    cursor.execute("SELECT * FROM legacy_products")

    batch = []
    total = 0

    for row in cursor.fetchall():
        product = Product(
            name=row[1],
            price=row[2],
            # ... map fields
        )

        if not skip_validation:
            product.full_clean()

        batch.append(product)

        if len(batch) >= batch_size:
            Product.objects.bulk_create(batch)
            total += len(batch)
            print(f"Migrated {total} products...")
            batch = []

    # Final batch
    if batch:
        Product.objects.bulk_create(batch)
        total += len(batch)

    print(f"✓ Migrated {total} products total")

class Command(WargsCommand):
    help = "Migrate data from legacy database"
    cli_function = migrate_data
```

### Cache Management Command

```python
from django.core.cache import cache

@wArgs
class CacheManager:
    """Django cache management."""

    def clear(self, pattern: str = "*"):
        """Clear cache keys matching pattern.

        Args:
            pattern: Key pattern to match (supports wildcards)
        """
        # Implementation depends on cache backend
        cache.clear()
        print(f"✓ Cleared cache (pattern: {pattern})")

    def stats(self):
        """Show cache statistics."""
        # Get cache stats (backend-specific)
        print("Cache Statistics:")
        print(f"  Backend: {cache.__class__.__name__}")
        # ... show stats

    def warm(self, model: str):
        """Warm cache for a model.

        Args:
            model: Model to cache
        """
        from django.apps import apps

        Model = apps.get_model('myapp', model)
        objects = Model.objects.all()

        for obj in objects:
            cache_key = f"{model}:{obj.pk}"
            cache.set(cache_key, obj, timeout=3600)

        print(f"✓ Warmed cache for {objects.count()} {model} objects")

class Command(BaseCommand):
    help = "Manage Django cache"

    def handle(self, *args, **options):
        CacheManager()
```

Usage:
```bash
python manage.py cache_manager clear --clear-pattern "user:*"
python manage.py cache_manager stats
python manage.py cache_manager warm --warm-model User
```

### Database Maintenance Command

```python
@wArgs
class DBMaintenance:
    """Database maintenance tasks."""

    def vacuum(self, tables: list[str] | None = None):
        """Vacuum database tables (PostgreSQL).

        Args:
            tables: Specific tables to vacuum (default: all)
        """
        from django.db import connection

        with connection.cursor() as cursor:
            if tables:
                for table in tables:
                    cursor.execute(f"VACUUM ANALYZE {table}")
                    print(f"✓ Vacuumed table: {table}")
            else:
                cursor.execute("VACUUM ANALYZE")
                print("✓ Vacuumed all tables")

    def reindex(self, models: list[str] | None = None):
        """Rebuild database indexes.

        Args:
            models: Models to reindex (default: all)
        """
        from django.apps import apps
        from django.db import connection

        if models:
            model_classes = [apps.get_model('myapp', m) for m in models]
        else:
            model_classes = apps.get_models()

        with connection.cursor() as cursor:
            for Model in model_classes:
                table = Model._meta.db_table
                cursor.execute(f"REINDEX TABLE {table}")
                print(f"✓ Reindexed: {table}")

    def analyze(self):
        """Analyze database and show statistics."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)

            print("\nTable Sizes:")
            for schema, table, size in cursor.fetchall():
                print(f"  {table}: {size}")
```

## Best Practices

### 1. Use Type Hints
```python
from typing import Literal
from pathlib import Path

@wArgs
def my_command(
    mode: Literal["create", "update", "delete"],  # Constrained choices
    file: Path,  # Automatic Path conversion
    count: int = 10,  # Type-safe integers
):
    ...
```

### 2. Add Docstrings
```python
@wArgs
def my_command(name: str, count: int = 1):
    """Short description.

    Longer description with more details about what
    this command does and when to use it.

    Args:
        name: Description of name parameter
        count: Description of count parameter
    """
```

### 3. Handle Django Setup
```python
import django
import os

# Ensure Django is configured before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

@wArgs
def my_command():
    from myapp.models import User  # Import after django.setup()
    ...
```

### 4. Add Progress Indication
```python
from django.db.models import Count

@wArgs
def process_items(batch_size: int = 100):
    """Process items in batches."""
    total = Item.objects.count()
    processed = 0

    for batch in Item.objects.iterator(chunk_size=batch_size):
        # Process batch
        processed += 1
        print(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")
```

## Testing Commands

```python
# tests/test_commands.py
from django.test import TestCase
from django.core.management import call_command
from io import StringIO

class CommandTests(TestCase):
    def test_process_users_command(self):
        # Create test data
        User.objects.create(username="test", status="active")

        # Capture output
        out = StringIO()
        call_command('process_users', '--process_users-status', 'active', stdout=out)

        self.assertIn('Processing', out.getvalue())
```

## Complete Example

See [Django CLI example](https://github.com/cmoxiv/wArgs/tree/main/examples/frameworks/django) for a complete Django project with:
- Model export/import
- Database migrations
- Cache management
- User management
- Data validation
- Background tasks

## Related

- [[SQLAlchemy Schema Tools]]
- [[Flask CLI Integration]]
- [wArgs Documentation](https://cmoxiv.github.io/wArgs/)
