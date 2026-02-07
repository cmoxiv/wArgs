#!/usr/bin/env python3
"""Mixin-based CLI with inherited options example.

Demonstrates:
- Mixin classes for reusable options
- Multiple inheritance
- Cooperative inheritance with **kwargs
- MRO traversal

Usage:
    python mixins.py --help
    python mixins.py --verbose deploy --env prod
    python mixins.py --dry-run --verbose build
"""

from __future__ import annotations

from typing import Annotated, Any, Callable

from wArgs import Arg, wArgs


class VerboseMixin:
    """Adds --verbose option for detailed output."""

    def __init__(self, verbose: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")


class DryRunMixin:
    """Adds --dry-run option for simulation mode."""

    def __init__(self, dry_run: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.dry_run = dry_run

    def execute(self, description: str, action: Callable[[], None]) -> None:
        """Execute an action or simulate it in dry-run mode."""
        if self.dry_run:
            print(f"[DRY RUN] Would: {description}")
        else:
            action()
            print(f"Done: {description}")


class ConfigMixin:
    """Adds --config option for configuration file."""

    def __init__(
        self,
        config: Annotated[str, Arg("-c", help="Configuration file")] = "config.yml",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.config = config

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        # In a real app, this would load the actual config
        return {"loaded_from": self.config}


@wArgs(prog="devops")
class DevOps(VerboseMixin, DryRunMixin, ConfigMixin):
    """DevOps CLI tool with multiple inherited options.

    This CLI inherits options from multiple mixins:
    - VerboseMixin: --verbose for detailed output
    - DryRunMixin: --dry-run for simulation mode
    - ConfigMixin: --config for configuration file
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def deploy(self, env: str, tag: str = "latest") -> None:
        """Deploy application to an environment.

        Args:
            env: Target environment (dev, staging, prod).
            tag: Docker image tag to deploy.
        """
        self.log(f"Loading config from: {self.config}")
        config = self.load_config()
        self.log(f"Config: {config}")

        self.log(f"Deploying {tag} to {env}")
        self.execute(
            f"deploy {tag} to {env}",
            lambda: print(f"Deployed {tag} to {env}"),
        )

    def build(self, target: str = "all") -> None:
        """Build the application.

        Args:
            target: Build target (all, frontend, backend).
        """
        self.log(f"Building target: {target}")
        self.execute(
            f"build {target}",
            lambda: print(f"Built {target}"),
        )

    def test(self, coverage: bool = False) -> None:
        """Run tests.

        Args:
            coverage: Enable coverage reporting.
        """
        self.log(f"Running tests with coverage={coverage}")
        self.execute(
            "run tests" + (" with coverage" if coverage else ""),
            lambda: print("Tests passed!"),
        )


if __name__ == "__main__":
    DevOps()
