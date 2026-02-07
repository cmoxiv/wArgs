#!/usr/bin/env python3
"""System Monitor CLI example - simplified version for help output."""

from wArgs import wArgs
from pathlib import Path
from typing import Literal

@wArgs
class SystemMonitor:
    """System monitoring and management CLI."""

    def __init__(self, verbose: bool = False):
        """Initialize system monitor.

        Args:
            verbose: Show detailed output
        """
        self.verbose = verbose

    def status(self):
        """Show current system status."""
        print("System status...")

    def cpu(self, per_cpu: bool = False, interval: int = 1):
        """Show CPU information and usage.

        Args:
            per_cpu: Show per-CPU statistics
            interval: Measurement interval in seconds
        """
        print("CPU information...")

    def memory(self):
        """Show memory information and usage."""
        print("Memory information...")

    def disk(self, path: Path = Path("/")):
        """Show disk information and usage.

        Args:
            path: Disk path to check
        """
        print(f"Disk information for {path}")

    def network(self, interval: int = 1):
        """Show network information and statistics.

        Args:
            interval: Measurement interval for speed
        """
        print("Network information...")

    def processes(
        self,
        sort_by: Literal["cpu", "memory", "name"] = "cpu",
        limit: int = 10,
    ):
        """Show running processes.

        Args:
            sort_by: Sort processes by metric
            limit: Number of processes to show
        """
        print(f"Top {limit} processes by {sort_by}")

    def kill(self, pid: int, force: bool = False):
        """Kill a process by PID.

        Args:
            pid: Process ID to kill
            force: Use SIGKILL instead of SIGTERM
        """
        print(f"Killing process {pid}")

    def monitor(
        self,
        interval: int = 5,
        duration: int = 60,
        output: Path | None = None,
    ):
        """Monitor system metrics over time.

        Args:
            interval: Seconds between measurements
            duration: Total monitoring duration in seconds
            output: Optional JSON file to save metrics
        """
        print(f"Monitoring for {duration}s")

    def alert(
        self,
        metric: Literal["cpu", "memory", "disk"] = "cpu",
        threshold: float = 80.0,
        interval: int = 5,
    ):
        """Alert when metric exceeds threshold.

        Args:
            metric: Metric to monitor
            threshold: Alert threshold percentage
            interval: Check interval in seconds
        """
        print(f"Monitoring {metric} with threshold {threshold}%")

if __name__ == "__main__":
    SystemMonitor()
