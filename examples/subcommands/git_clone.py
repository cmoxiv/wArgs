#!/usr/bin/env python3
"""Git-like CLI with subcommands example.

Demonstrates:
- Class-based CLI
- Global options in __init__
- Multiple subcommands
- Method to subcommand naming

Usage:
    python git_clone.py --help
    python git_clone.py clone --url https://github.com/user/repo
    python git_clone.py --verbose status
    python git_clone.py add --files file1.py file2.py
"""

from typing import Annotated

from wArgs import Arg, wArgs


@wArgs(prog="mygit")
class Git:
    """A simplified git-like CLI tool.

    Demonstrates subcommand patterns with wArgs.
    """

    def __init__(
        self,
        verbose: Annotated[bool, Arg("-v", help="Enable verbose output")] = False,
        directory: Annotated[str, Arg("-C", help="Run as if started in this directory")] = ".",
    ) -> None:
        """Initialize with global options.

        Args:
            verbose: Enable verbose output.
            directory: Working directory.
        """
        self.verbose = verbose
        self.directory = directory

    def _log(self, message: str) -> None:
        """Print message if verbose mode is on."""
        if self.verbose:
            print(f"[verbose] {message}")

    def clone(self, url: str, dest: str = "") -> None:
        """Clone a repository.

        Args:
            url: Repository URL to clone.
            dest: Destination directory.
        """
        self._log(f"Working in: {self.directory}")
        destination = dest or url.split("/")[-1].replace(".git", "")
        print(f"Cloning {url} into {destination}...")
        print("Done!")

    def status(self) -> None:
        """Show working tree status."""
        self._log(f"Checking status in: {self.directory}")
        print("On branch main")
        print("nothing to commit, working tree clean")

    def add(self, files: list[str], all: Annotated[bool, Arg("-A")] = False) -> None:
        """Add files to staging area.

        Args:
            files: Files to add.
            all: Add all changed files.
        """
        self._log(f"Adding files in: {self.directory}")
        if all:
            print("Adding all changed files...")
        else:
            for f in files:
                print(f"Adding: {f}")

    def commit(
        self,
        message: Annotated[str, Arg("-m", help="Commit message")],
        all: Annotated[bool, Arg("-a", help="Commit all changed files")] = False,
    ) -> None:
        """Record changes to the repository.

        Args:
            message: Commit message.
            all: Automatically stage modified files.
        """
        self._log(f"Committing in: {self.directory}")
        if all:
            print("Staging all modified files...")
        print(f"Committing with message: {message}")
        print("[main abc1234] {message}")

    def push(
        self,
        remote: str = "origin",
        branch: str = "main",
        force: Annotated[bool, Arg("-f")] = False,
    ) -> None:
        """Push changes to remote.

        Args:
            remote: Remote name.
            branch: Branch to push.
            force: Force push.
        """
        self._log(f"Pushing from: {self.directory}")
        force_str = " (force)" if force else ""
        print(f"Pushing to {remote}/{branch}{force_str}...")
        print("Done!")


if __name__ == "__main__":
    Git()
