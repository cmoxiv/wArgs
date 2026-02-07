#!/usr/bin/env python3
"""Database CLI example - simplified version for help output."""

from wArgs import wArgs
from pathlib import Path
from typing import Literal

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
        print(f"Connected to {db_type} at {host}:{port}/{database}")

    def tables(self):
        """List all tables in the database."""
        print("Listing tables...")

    def schema(self, table: str):
        """Show schema for a specific table.

        Args:
            table: Table name to inspect
        """
        print(f"Showing schema for {table}")

    def query(self, sql: str, output: Path | None = None):
        """Execute a SQL query and show results.

        Args:
            sql: SQL query to execute
            output: Optional JSON file to save results
        """
        print(f"Executing query: {sql}")

    def backup(self, output: Path):
        """Backup database schema to SQL file.

        Args:
            output: Output SQL file path
        """
        print(f"Backing up to {output}")

if __name__ == "__main__":
    DBCLI()
