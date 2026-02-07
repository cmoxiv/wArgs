# Building a Database CLI

Learn how to build a powerful database administration CLI using wArgs and SQLAlchemy.

## Overview

In this tutorial, you'll build a CLI tool that can:
- Connect to PostgreSQL/MySQL databases
- List tables and inspect schemas
- Run queries and export results
- Backup and restore databases
- Manage database migrations

**Prerequisites:**
- Python 3.8+
- Basic SQL knowledge
- wArgs installed: `pip install git+https://github.com/cmoxiv/wArgs.git`

## Step 1: Project Setup

```bash
mkdir dbcli
cd dbcli
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install git+https://github.com/cmoxiv/wArgs.git
pip install sqlalchemy psycopg2-binary  # For PostgreSQL
pip install pymysql  # For MySQL (optional)
```

## Step 2: Basic Structure

Create `dbcli.py`:

```python
from wArgs import wArgs
from typing import Literal
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
import json

@wArgs
class DBCLI:
    """Database CLI for PostgreSQL and MySQL."""

    def __init__(
        self,
        db_type: Literal["postgres", "mysql"] = "postgres",
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str = "",
    ):
        """Initialize database connection.

        Args:
            db_type: Database type (postgres or mysql)
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.db_type = db_type

        # Build connection string
        if db_type == "postgres":
            url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

        self.engine = create_engine(url)
        self.inspector = inspect(self.engine)

    def tables(self):
        """List all tables in the database."""
        tables = self.inspector.get_table_names()

        if not tables:
            print("No tables found.")
            return

        print(f"\nFound {len(tables)} tables:\n")
        for table in sorted(tables):
            print(f"  • {table}")

    def schema(self, table: str):
        """Show schema for a specific table.

        Args:
            table: Table name to inspect
        """
        if table not in self.inspector.get_table_names():
            print(f"Error: Table '{table}' not found")
            return

        columns = self.inspector.get_columns(table)
        pk = self.inspector.get_pk_constraint(table)
        indexes = self.inspector.get_indexes(table)

        print(f"\nTable: {table}")
        print("=" * 60)

        # Show columns
        print("\nColumns:")
        for col in columns:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            default = f"DEFAULT {col['default']}" if col.get("default") else ""
            pk_marker = "🔑" if col["name"] in pk.get("constrained_columns", []) else "  "

            print(f"  {pk_marker} {col['name']:<20} {str(col['type']):<15} {nullable:<10} {default}")

        # Show indexes
        if indexes:
            print("\nIndexes:")
            for idx in indexes:
                unique = "UNIQUE" if idx["unique"] else ""
                cols = ", ".join(idx["column_names"])
                print(f"  • {idx['name']}: ({cols}) {unique}")

    def query(self, sql: str, output: Path | None = None):
        """Execute a SQL query and show results.

        Args:
            sql: SQL query to execute
            output: Optional JSON file to save results
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))

            if result.returns_rows:
                rows = result.fetchall()
                keys = result.keys()

                # Convert to list of dicts
                data = [dict(zip(keys, row)) for row in rows]

                # Print to console
                print(f"\nQuery returned {len(data)} rows:\n")

                if data:
                    # Print as table
                    widths = {k: max(len(k), max(len(str(row[k])) for row in data))
                             for k in keys}

                    # Header
                    header = " | ".join(k.ljust(widths[k]) for k in keys)
                    print(header)
                    print("-" * len(header))

                    # Rows
                    for row in data[:10]:  # Limit to 10 rows in console
                        print(" | ".join(str(row[k]).ljust(widths[k]) for k in keys))

                    if len(data) > 10:
                        print(f"\n... and {len(data) - 10} more rows")

                # Save to file if requested
                if output:
                    output.write_text(json.dumps(data, indent=2, default=str))
                    print(f"\n✓ Results saved to {output}")
            else:
                print("Query executed successfully (no rows returned)")

    def backup(self, output: Path):
        """Backup database schema to SQL file.

        Args:
            output: Output SQL file path
        """
        # This is a simplified version - in production, use pg_dump or mysqldump
        tables = self.inspector.get_table_names()

        sql_statements = []

        for table in tables:
            # Get table definition
            columns = self.inspector.get_columns(table)
            pk = self.inspector.get_pk_constraint(table)

            # Build CREATE TABLE statement
            col_defs = []
            for col in columns:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                col_def = f"  {col['name']} {col['type']} {nullable}"
                col_defs.append(col_def)

            # Add primary key
            if pk.get("constrained_columns"):
                pk_cols = ", ".join(pk["constrained_columns"])
                col_defs.append(f"  PRIMARY KEY ({pk_cols})")

            create_stmt = f"CREATE TABLE {table} (\n" + ",\n".join(col_defs) + "\n);"
            sql_statements.append(create_stmt)

        # Write to file
        output.write_text("\n\n".join(sql_statements))
        print(f"✓ Backed up {len(tables)} tables to {output}")

if __name__ == "__main__":
    DBCLI()
```

## Step 3: Usage Examples

### List all tables
```bash
python dbcli.py --DBCLI-host localhost --DBCLI-database mydb --DBCLI-user admin --DBCLI-password secret tables
```

### Show table schema
```bash
python dbcli.py --DBCLI-database mydb --DBCLI-user admin schema --schema-table users
```

### Run a query
```bash
python dbcli.py --DBCLI-database mydb --DBCLI-user admin query --query-sql "SELECT * FROM users LIMIT 10"
```

### Save query results to JSON
```bash
python dbcli.py --DBCLI-database mydb --DBCLI-user admin query \
  --query-sql "SELECT * FROM users WHERE active = true" \
  --query-output active_users.json
```

### Backup database schema
```bash
python dbcli.py --DBCLI-database mydb --DBCLI-user admin backup --backup-output schema.sql
```

## Step 4: Add Configuration File Support

Create `.dbcli.json`:

```json
{
  "db_type": "postgres",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "admin",
  "password": "secret"
}
```

Update the CLI to load config:

```python
import os
from pathlib import Path

# At the top of DBCLI.__init__
config_file = Path.home() / ".dbcli.json"
if config_file.exists():
    config = json.loads(config_file.read_text())
    # Use config values as defaults
    db_type = config.get("db_type", db_type)
    host = config.get("host", host)
    # ... etc
```

## Step 5: Enhancements

### Add transaction support
```python
def execute(self, sql: str, commit: bool = True):
    """Execute SQL with transaction control.

    Args:
        sql: SQL to execute
        commit: Whether to commit the transaction
    """
    with self.engine.connect() as conn:
        trans = conn.begin()
        try:
            result = conn.execute(text(sql))
            if commit:
                trans.commit()
                print("✓ Transaction committed")
            else:
                trans.rollback()
                print("✓ Transaction rolled back")
        except Exception as e:
            trans.rollback()
            print(f"✗ Error: {e}")
            raise
```

### Add migration support
```python
def migrate(self, migrations_dir: Path):
    """Run database migrations.

    Args:
        migrations_dir: Directory containing .sql migration files
    """
    # Create migrations table if not exists
    with self.engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

    # Get applied migrations
    with self.engine.connect() as conn:
        result = conn.execute(text("SELECT filename FROM migrations"))
        applied = {row[0] for row in result}

    # Run pending migrations
    for migration_file in sorted(migrations_dir.glob("*.sql")):
        if migration_file.name not in applied:
            print(f"Applying {migration_file.name}...")
            sql = migration_file.read_text()

            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.execute(
                    text("INSERT INTO migrations (filename) VALUES (:name)"),
                    {"name": migration_file.name}
                )
                conn.commit()

            print(f"✓ Applied {migration_file.name}")
```

## Complete Example

See the [complete example on GitHub](https://github.com/cmoxiv/wArgs/tree/main/examples/use-cases/database) for a full-featured database CLI with:
- Connection pooling
- Multiple database support (Postgres, MySQL, SQLite)
- Data export to CSV/JSON/Excel
- Query history
- Interactive mode
- Password encryption

## Next Steps

- Add support for database dumps using `pg_dump`/`mysqldump`
- Implement interactive query mode
- Add query result pagination
- Create data import commands
- Add database comparison tools

## Related

- [[SQLAlchemy Schema Tools]] - Advanced schema management
- [[Django Management Commands]] - Integrate with Django ORM
- Official docs: [Type System](https://cmoxiv.github.io/wArgs/guide/type-system/)
