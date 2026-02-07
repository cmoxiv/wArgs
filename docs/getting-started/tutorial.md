# Tutorial: Building a Task Manager CLI

In this tutorial, we'll build a complete task manager CLI application from scratch, demonstrating all the key features of wArgs.

## What We'll Build

A command-line task manager with these features:

- Add, list, complete, and delete tasks
- Filter tasks by status
- Global options for output format
- Persistent storage in a JSON file

## Step 1: Basic Structure

Let's start with the project structure:

```
tasks/
├── tasks.py      # Main CLI
└── tasks.json    # Data file (auto-created)
```

Create `tasks.py` with a basic class structure:

```python
from wArgs import wArgs

@wArgs(prog="tasks", description="A simple task manager")
class Tasks:
    """Manage your tasks from the command line."""

    def add(self, title: str) -> None:
        """Add a new task."""
        print(f"Adding task: {title}")

    def list(self) -> None:
        """List all tasks."""
        print("Listing tasks...")

if __name__ == "__main__":
    Tasks()
```

Test it:

```bash
$ python tasks.py --help
usage: tasks [-h] {add,list} ...

Manage your tasks from the command line.

$ python tasks.py add --title "Buy groceries"
Adding task: Buy groceries
```

## Step 2: Add Data Persistence

Let's add actual storage functionality:

```python
from __future__ import annotations
import json
from pathlib import Path
from wArgs import wArgs

DATA_FILE = Path("tasks.json")

def load_tasks() -> list[dict]:
    """Load tasks from JSON file."""
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_tasks(tasks: list[dict]) -> None:
    """Save tasks to JSON file."""
    DATA_FILE.write_text(json.dumps(tasks, indent=2))

@wArgs(prog="tasks")
class Tasks:
    """Manage your tasks from the command line."""

    def add(self, title: str, priority: int = 1) -> None:
        """Add a new task.

        Args:
            title: The task description
            priority: Priority level (1=low, 2=medium, 3=high)
        """
        tasks = load_tasks()
        task = {
            "id": len(tasks) + 1,
            "title": title,
            "priority": priority,
            "done": False,
        }
        tasks.append(task)
        save_tasks(tasks)
        print(f"Added task #{task['id']}: {title}")

    def list(self) -> None:
        """List all tasks."""
        tasks = load_tasks()
        if not tasks:
            print("No tasks found.")
            return
        for task in tasks:
            status = "x" if task["done"] else " "
            print(f"[{status}] #{task['id']} (P{task['priority']}): {task['title']}")

if __name__ == "__main__":
    Tasks()
```

Test it:

```bash
$ python tasks.py add --title "Buy groceries" --priority 2
Added task #1: Buy groceries

$ python tasks.py add --title "Call mom" --priority 3
Added task #2: Call mom

$ python tasks.py list
[ ] #1 (P2): Buy groceries
[ ] #2 (P3): Call mom
```

## Step 3: Add More Commands

Let's add complete and delete commands:

```python
from __future__ import annotations
import json
from pathlib import Path
from wArgs import wArgs

DATA_FILE = Path("tasks.json")

def load_tasks() -> list[dict]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_tasks(tasks: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2))

def find_task(tasks: list[dict], task_id: int) -> dict | None:
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

@wArgs(prog="tasks")
class Tasks:
    """Manage your tasks from the command line."""

    def add(self, title: str, priority: int = 1) -> None:
        """Add a new task.

        Args:
            title: The task description
            priority: Priority level (1=low, 2=medium, 3=high)
        """
        tasks = load_tasks()
        task = {
            "id": len(tasks) + 1,
            "title": title,
            "priority": priority,
            "done": False,
        }
        tasks.append(task)
        save_tasks(tasks)
        print(f"Added task #{task['id']}: {title}")

    def list(self, all: bool = False) -> None:
        """List tasks.

        Args:
            all: Show completed tasks too
        """
        tasks = load_tasks()
        if not all:
            tasks = [t for t in tasks if not t["done"]]
        if not tasks:
            print("No tasks found.")
            return
        for task in tasks:
            status = "x" if task["done"] else " "
            print(f"[{status}] #{task['id']} (P{task['priority']}): {task['title']}")

    def complete(self, task_id: int) -> None:
        """Mark a task as complete.

        Args:
            task_id: The task ID to complete
        """
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if task is None:
            print(f"Task #{task_id} not found.")
            return
        task["done"] = True
        save_tasks(tasks)
        print(f"Completed task #{task_id}: {task['title']}")

    def delete(self, task_id: int) -> None:
        """Delete a task.

        Args:
            task_id: The task ID to delete
        """
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if task is None:
            print(f"Task #{task_id} not found.")
            return
        tasks.remove(task)
        save_tasks(tasks)
        print(f"Deleted task #{task_id}: {task['title']}")

if __name__ == "__main__":
    Tasks()
```

```bash
$ python tasks.py complete --task-id 1
Completed task #1: Buy groceries

$ python tasks.py list
[ ] #2 (P3): Call mom

$ python tasks.py list --all
[x] #1 (P2): Buy groceries
[ ] #2 (P3): Call mom
```

## Step 4: Add Global Options

Let's add a `--verbose` flag that affects all commands:

```python
from __future__ import annotations
import json
from pathlib import Path
from wArgs import wArgs

DATA_FILE = Path("tasks.json")

def load_tasks() -> list[dict]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_tasks(tasks: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2))

def find_task(tasks: list[dict], task_id: int) -> dict | None:
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

@wArgs(prog="tasks")
class Tasks:
    """Manage your tasks from the command line."""

    def __init__(self, verbose: bool = False) -> None:
        """Initialize with global options.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose

    def _log(self, message: str) -> None:
        """Print a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def add(self, title: str, priority: int = 1) -> None:
        """Add a new task.

        Args:
            title: The task description
            priority: Priority level (1=low, 2=medium, 3=high)
        """
        self._log(f"Loading tasks from {DATA_FILE}")
        tasks = load_tasks()
        task = {
            "id": len(tasks) + 1,
            "title": title,
            "priority": priority,
            "done": False,
        }
        tasks.append(task)
        self._log(f"Saving {len(tasks)} tasks")
        save_tasks(tasks)
        print(f"Added task #{task['id']}: {title}")

    def list(self, all: bool = False) -> None:
        """List tasks.

        Args:
            all: Show completed tasks too
        """
        self._log(f"Loading tasks from {DATA_FILE}")
        tasks = load_tasks()
        if not all:
            tasks = [t for t in tasks if not t["done"]]
        self._log(f"Showing {len(tasks)} tasks")
        if not tasks:
            print("No tasks found.")
            return
        for task in tasks:
            status = "x" if task["done"] else " "
            print(f"[{status}] #{task['id']} (P{task['priority']}): {task['title']}")

    def complete(self, task_id: int) -> None:
        """Mark a task as complete.

        Args:
            task_id: The task ID to complete
        """
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if task is None:
            print(f"Task #{task_id} not found.")
            return
        task["done"] = True
        save_tasks(tasks)
        print(f"Completed task #{task_id}: {task['title']}")

    def delete(self, task_id: int) -> None:
        """Delete a task.

        Args:
            task_id: The task ID to delete
        """
        tasks = load_tasks()
        task = find_task(tasks, task_id)
        if task is None:
            print(f"Task #{task_id} not found.")
            return
        tasks.remove(task)
        save_tasks(tasks)
        print(f"Deleted task #{task_id}: {task['title']}")

if __name__ == "__main__":
    Tasks()
```

The `--verbose` flag now appears as a global option:

```bash
$ python tasks.py --help
usage: tasks [-h] [--verbose] {add,list,complete,delete} ...

$ python tasks.py --verbose list
[DEBUG] Loading tasks from tasks.json
[DEBUG] Showing 1 tasks
[ ] #2 (P3): Call mom
```

## Step 5: Add Type Hints for Choices

Let's use `Literal` to restrict priority values:

```python
from __future__ import annotations
import json
from pathlib import Path
from typing import Literal
from wArgs import wArgs

# ... (same helper functions)

@wArgs(prog="tasks")
class Tasks:
    """Manage your tasks from the command line."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def add(
        self,
        title: str,
        priority: Literal["low", "medium", "high"] = "medium",
    ) -> None:
        """Add a new task.

        Args:
            title: The task description
            priority: Priority level
        """
        priority_map = {"low": 1, "medium": 2, "high": 3}
        tasks = load_tasks()
        task = {
            "id": len(tasks) + 1,
            "title": title,
            "priority": priority_map[priority],
            "done": False,
        }
        tasks.append(task)
        save_tasks(tasks)
        print(f"Added task #{task['id']}: {title}")

    # ... (rest of methods)
```

```bash
$ python tasks.py add --help
usage: tasks add [-h] --title TITLE [--priority {low,medium,high}]

$ python tasks.py add --title "Learn wArgs" --priority high
Added task #3: Learn wArgs
```

## Step 6: Using Arg for Fine Control

Use `Arg` with `Annotated` for more control:

```python
from typing import Annotated, Literal
from wArgs import wArgs, Arg

@wArgs(prog="tasks")
class Tasks:
    """Manage your tasks from the command line."""

    def __init__(
        self,
        verbose: Annotated[bool, Arg("-v", help="Enable verbose output")] = False,
    ) -> None:
        self.verbose = verbose

    def add(
        self,
        title: Annotated[str, Arg("-t", help="Task description")],
        priority: Annotated[
            Literal["low", "medium", "high"],
            Arg("-p", help="Priority level"),
        ] = "medium",
    ) -> None:
        """Add a new task."""
        # ...
```

Now you can use short flags:

```bash
$ python tasks.py -v add -t "Quick task" -p high
[DEBUG] Loading tasks...
Added task #4: Quick task
```

## Complete Example

See the full working example in the [examples/tasks](https://github.com/cmoxiv/wArgs/tree/main/examples/tasks) directory.

## What's Next?

- [Type System](../guide/type-system.md) - Learn about all supported types
- [Subcommands](../guide/subcommands.md) - More complex CLI hierarchies
- [Inheritance](../guide/inheritance.md) - Share options with mixins
- [Cookbook](../cookbook/patterns.md) - Common patterns and recipes
