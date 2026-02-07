# Flask CLI Integration with wArgs

Integrate wArgs with Flask to create powerful custom CLI commands for your Flask applications.

## Quick Start

```python
from flask import Flask
from wArgs import wArgs

app = Flask(__name__)

@wArgs
class FlaskCLI:
    """Flask application commands."""
    
    def __init__(self, app_context: bool = True):
        """Initialize Flask CLI.
        
        Args:
            app_context: Run commands in Flask app context
        """
        self.app_context = app_context
        if app_context:
            with app.app_context():
                pass  # Commands run in context
    
    def init_db(self):
        """Initialize the database."""
        with app.app_context():
            from models import db
            db.create_all()
            print("✓ Database initialized")
    
    def seed(self, count: int = 10):
        """Seed database with sample data.
        
        Args:
            count: Number of records to create
        """
        with app.app_context():
            from models import db, User
            
            for i in range(count):
                user = User(
                    username=f"user{i}",
                    email=f"user{i}@example.com"
                )
                db.session.add(user)
            
            db.session.commit()
            print(f"✓ Created {count} users")
    
    def routes(self):
        """List all registered routes."""
        with app.app_context():
            for rule in app.url_map.iter_rules():
                print(f"{rule.endpoint:30s} {rule.rule}")

if __name__ == "__main__":
    FlaskCLI()
```

## --help Output

```
$ python cli.py --help
usage: cli.py [-h] [--FlaskCLI-app-context] {init_db,seed,routes} ...

Flask application commands.

positional arguments:
  {init_db,seed,routes}
    init_db             Initialize the database
    seed                Seed database with sample data
    routes              List all registered routes

options:
  -h, --help            show this help message and exit
  --FlaskCLI-app-context
                        Run commands in Flask app context (default: True)
```

## Usage

```bash
# Initialize database
python cli.py init_db

# Seed with data
python cli.py seed --seed-count 100

# List routes
python cli.py routes
```

## Integration with Flask CLI

```python
import click
from flask.cli import with_appcontext

@app.cli.command()
@click.argument('count', default=10)
def wargs_seed(count):
    """Seed using wArgs (called via flask command)."""
    # Import and use wArgs function
    pass
```

## Related

- [[Django Management Commands]]
- [[FastAPI CLI Tools]]
