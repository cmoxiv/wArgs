# Building a System Monitor CLI

Create a system monitoring tool with wArgs for tracking CPU, memory, disk, network, and processes.

## Overview

Build a CLI that can:
- Monitor CPU and memory usage
- Track disk space and I/O
- Monitor network statistics
- List and manage processes
- Show system information
- Log metrics to file
- Send alerts on thresholds

**Prerequisites:**
- Python 3.8+
- wArgs: `pip install git+https://github.com/cmoxiv/wArgs.git`
- psutil: `pip install psutil`

## Complete Implementation

```python
from wArgs import wArgs
from pathlib import Path
from typing import Literal
import psutil
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class SystemMetrics:
    """System metrics snapshot."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int

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
        print("\n=== System Status ===\n")

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        print(f"CPU:")
        print(f"  Usage: {cpu_percent}%")
        print(f"  Cores: {cpu_count}")
        print(f"  Frequency: {psutil.cpu_freq().current:.0f} MHz")

        # Memory
        mem = psutil.virtual_memory()
        print(f"\nMemory:")
        print(f"  Total: {self._format_bytes(mem.total)}")
        print(f"  Used: {self._format_bytes(mem.used)} ({mem.percent}%)")
        print(f"  Available: {self._format_bytes(mem.available)}")

        # Disk
        disk = psutil.disk_usage("/")
        print(f"\nDisk (/):")
        print(f"  Total: {self._format_bytes(disk.total)}")
        print(f"  Used: {self._format_bytes(disk.used)} ({disk.percent}%)")
        print(f"  Free: {self._format_bytes(disk.free)}")

        # Network
        net = psutil.net_io_counters()
        print(f"\nNetwork:")
        print(f"  Sent: {self._format_bytes(net.bytes_sent)}")
        print(f"  Received: {self._format_bytes(net.bytes_recv)}")

    def cpu(self, per_cpu: bool = False, interval: int = 1):
        """Show CPU information and usage.

        Args:
            per_cpu: Show per-CPU statistics
            interval: Measurement interval in seconds
        """
        print("\n=== CPU Information ===\n")

        # Overall usage
        cpu_percent = psutil.cpu_percent(interval=interval)
        print(f"Overall Usage: {cpu_percent}%")

        # Per-CPU usage
        if per_cpu:
            per_cpu_percent = psutil.cpu_percent(interval=interval, percpu=True)
            print(f"\nPer-CPU Usage:")
            for i, percent in enumerate(per_cpu_percent):
                bar = self._make_bar(percent, 20)
                print(f"  CPU {i}: {bar} {percent}%")

        # CPU times
        cpu_times = psutil.cpu_times()
        print(f"\nCPU Times:")
        print(f"  User: {cpu_times.user:.2f}s")
        print(f"  System: {cpu_times.system:.2f}s")
        print(f"  Idle: {cpu_times.idle:.2f}s")

        # CPU frequency
        freq = psutil.cpu_freq()
        if freq:
            print(f"\nFrequency:")
            print(f"  Current: {freq.current:.0f} MHz")
            print(f"  Min: {freq.min:.0f} MHz")
            print(f"  Max: {freq.max:.0f} MHz")

    def memory(self):
        """Show memory information and usage."""
        print("\n=== Memory Information ===\n")

        # Virtual memory
        mem = psutil.virtual_memory()
        print("Virtual Memory:")
        print(f"  Total: {self._format_bytes(mem.total)}")
        print(f"  Available: {self._format_bytes(mem.available)}")
        print(f"  Used: {self._format_bytes(mem.used)} ({mem.percent}%)")
        print(f"  Free: {self._format_bytes(mem.free)}")

        # Memory bar
        bar = self._make_bar(mem.percent, 40)
        print(f"\n  Usage: {bar} {mem.percent}%")

        # Swap memory
        swap = psutil.swap_memory()
        if swap.total > 0:
            print(f"\nSwap Memory:")
            print(f"  Total: {self._format_bytes(swap.total)}")
            print(f"  Used: {self._format_bytes(swap.used)} ({swap.percent}%)")
            print(f"  Free: {self._format_bytes(swap.free)}")

    def disk(self, path: Path = Path("/")):
        """Show disk information and usage.

        Args:
            path: Disk path to check
        """
        print(f"\n=== Disk Information ({path}) ===\n")

        # Disk usage
        usage = psutil.disk_usage(str(path))
        print("Usage:")
        print(f"  Total: {self._format_bytes(usage.total)}")
        print(f"  Used: {self._format_bytes(usage.used)} ({usage.percent}%)")
        print(f"  Free: {self._format_bytes(usage.free)}")

        # Usage bar
        bar = self._make_bar(usage.percent, 40)
        print(f"\n  {bar} {usage.percent}%")

        # Disk partitions
        print("\nAll Partitions:")
        for partition in psutil.disk_partitions():
            try:
                part_usage = psutil.disk_usage(partition.mountpoint)
                print(f"\n  {partition.device}")
                print(f"    Mountpoint: {partition.mountpoint}")
                print(f"    Type: {partition.fstype}")
                print(f"    Usage: {part_usage.percent}%")
            except PermissionError:
                continue

    def network(self, interval: int = 1):
        """Show network information and statistics.

        Args:
            interval: Measurement interval for speed
        """
        print("\n=== Network Information ===\n")

        # Network interfaces
        print("Interfaces:")
        for interface, addrs in psutil.net_if_addrs().items():
            print(f"\n  {interface}:")
            for addr in addrs:
                if addr.family == 2:  # IPv4
                    print(f"    IPv4: {addr.address}")
                elif addr.family == 30:  # IPv6
                    print(f"    IPv6: {addr.address}")

        # Network I/O
        net1 = psutil.net_io_counters()
        time.sleep(interval)
        net2 = psutil.net_io_counters()

        sent_per_sec = (net2.bytes_sent - net1.bytes_sent) / interval
        recv_per_sec = (net2.bytes_recv - net1.bytes_recv) / interval

        print(f"\nTotal Transfer:")
        print(f"  Sent: {self._format_bytes(net2.bytes_sent)}")
        print(f"  Received: {self._format_bytes(net2.bytes_recv)}")

        print(f"\nCurrent Speed:")
        print(f"  Upload: {self._format_bytes(sent_per_sec)}/s")
        print(f"  Download: {self._format_bytes(recv_per_sec)}/s")

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
        print(f"\n=== Top {limit} Processes (by {sort_by}) ===\n")

        # Get all processes
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort processes
        if sort_by == "cpu":
            processes.sort(key=lambda p: p["cpu_percent"] or 0, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda p: p["memory_percent"] or 0, reverse=True)
        else:
            processes.sort(key=lambda p: p["name"] or "")

        # Print table
        print(f"{'PID':<8} {'Name':<30} {'CPU%':<8} {'Memory%':<8}")
        print("-" * 60)

        for proc in processes[:limit]:
            print(
                f"{proc['pid']:<8} "
                f"{proc['name'][:30]:<30} "
                f"{proc['cpu_percent'] or 0:<8.1f} "
                f"{proc['memory_percent'] or 0:<8.1f}"
            )

    def kill(self, pid: int, force: bool = False):
        """Kill a process by PID.

        Args:
            pid: Process ID to kill
            force: Use SIGKILL instead of SIGTERM
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()

            if force:
                proc.kill()
                print(f"✓ Killed process {pid} ({name})")
            else:
                proc.terminate()
                print(f"✓ Terminated process {pid} ({name})")

        except psutil.NoSuchProcess:
            print(f"Error: Process {pid} not found")
        except psutil.AccessDenied:
            print(f"Error: Permission denied to kill process {pid}")

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
        print(f"\nMonitoring system for {duration}s (interval: {interval}s)...")
        print("Press Ctrl+C to stop\n")

        metrics_log = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # Collect metrics
                net = psutil.net_io_counters()
                metrics = SystemMetrics(
                    timestamp=datetime.now().isoformat(),
                    cpu_percent=psutil.cpu_percent(interval=0.1),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_percent=psutil.disk_usage("/").percent,
                    network_sent=net.bytes_sent,
                    network_recv=net.bytes_recv,
                )

                metrics_log.append(metrics)

                # Display
                print(
                    f"[{metrics.timestamp}] "
                    f"CPU: {metrics.cpu_percent:5.1f}% | "
                    f"Mem: {metrics.memory_percent:5.1f}% | "
                    f"Disk: {metrics.disk_percent:5.1f}%"
                )

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")

        # Save to file
        if output and metrics_log:
            data = [asdict(m) for m in metrics_log]
            output.write_text(json.dumps(data, indent=2))
            print(f"\n✓ Saved {len(metrics_log)} measurements to {output}")

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
        print(f"\nMonitoring {metric} (alert at {threshold}%)...")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                # Get current value
                if metric == "cpu":
                    value = psutil.cpu_percent(interval=1)
                elif metric == "memory":
                    value = psutil.virtual_memory().percent
                elif metric == "disk":
                    value = psutil.disk_usage("/").percent

                # Check threshold
                if value >= threshold:
                    print(f"🚨 ALERT: {metric.upper()} at {value:.1f}% (threshold: {threshold}%)")
                else:
                    print(f"✓ {metric.upper()}: {value:.1f}%")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")

    def _format_bytes(self, bytes: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} PB"

    def _make_bar(self, percent: float, width: int = 20) -> str:
        """Create a text progress bar."""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

if __name__ == "__main__":
    SystemMonitor()
```

## Example --help Output

```
$ python monitor.py --help
usage: monitor.py [-h] [--SystemMonitor-verbose]
                  {status,cpu,memory,disk,network,processes,kill,monitor,alert} ...

System monitoring and management CLI.

positional arguments:
  {status,cpu,memory,disk,network,processes,kill,monitor,alert}
    status              Show current system status
    cpu                 Show CPU information and usage
    memory              Show memory information and usage
    disk                Show disk information and usage
    network             Show network information and statistics
    processes           Show running processes
    kill                Kill a process by PID
    monitor             Monitor system metrics over time
    alert               Alert when metric exceeds threshold

options:
  -h, --help            show this help message and exit
  --SystemMonitor-verbose
                        Show detailed output (default: False)
```

## Usage Examples

### Show system status
```bash
$ python monitor.py status

=== System Status ===

CPU:
  Usage: 15.2%
  Cores: 8
  Frequency: 2400 MHz

Memory:
  Total: 16.0 GB
  Used: 8.5 GB (53.1%)
  Available: 7.5 GB

Disk (/):
  Total: 500.0 GB
  Used: 250.0 GB (50.0%)
  Free: 250.0 GB

Network:
  Sent: 1.2 GB
  Received: 5.3 GB
```

### Monitor CPU usage
```bash
$ python monitor.py cpu --cpu-per-cpu

=== CPU Information ===

Overall Usage: 18.5%

Per-CPU Usage:
  CPU 0: [████████░░░░░░░░░░░░] 42.1%
  CPU 1: [███░░░░░░░░░░░░░░░░░] 15.3%
  CPU 2: [██████░░░░░░░░░░░░░░] 28.7%
  CPU 3: [██░░░░░░░░░░░░░░░░░░] 9.2%
  ...
```

### Show top processes
```bash
$ python monitor.py processes --processes-sort-by memory --processes-limit 5

=== Top 5 Processes (by memory) ===

PID      Name                           CPU%     Memory%
------------------------------------------------------------
1234     Google Chrome                  12.5     15.3
5678     Python                         45.2     8.7
9012     VSCode                         8.1      7.2
3456     Terminal                       2.3      3.1
7890     Safari                         5.4      2.9
```

### Monitor metrics over time
```bash
$ python monitor.py monitor \
  --monitor-interval 10 \
  --monitor-duration 300 \
  --monitor-output metrics.json

Monitoring system for 300s (interval: 10s)...
Press Ctrl+C to stop

[2024-02-07T12:00:00] CPU:  15.2% | Mem:  53.1% | Disk:  50.0%
[2024-02-07T12:00:10] CPU:  18.5% | Mem:  54.2% | Disk:  50.0%
[2024-02-07T12:00:20] CPU:  22.1% | Mem:  55.1% | Disk:  50.0%
...

✓ Saved 30 measurements to metrics.json
```

### Set up alerts
```bash
$ python monitor.py alert \
  --alert-metric cpu \
  --alert-threshold 80.0 \
  --alert-interval 5

Monitoring cpu (alert at 80.0%)...
Press Ctrl+C to stop

✓ CPU: 45.2%
✓ CPU: 52.1%
🚨 ALERT: CPU at 85.3% (threshold: 80.0%)
✓ CPU: 72.4%
```

## Advanced Features

### System info command
```python
def info(self):
    """Show detailed system information."""
    import platform

    print("\n=== System Information ===\n")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {platform.python_version()}")

    # Boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    print(f"\nBoot time: {boot_time}")
    print(f"Uptime: {uptime}")
```

### Export metrics to CSV
```python
def export_metrics(self, output: Path, duration: int = 60):
    """Export metrics to CSV for analysis."""
    import csv

    with output.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'cpu', 'memory', 'disk'])

        for _ in range(duration // 5):
            writer.writerow([
                datetime.now().isoformat(),
                psutil.cpu_percent(),
                psutil.virtual_memory().percent,
                psutil.disk_usage('/').percent
            ])
            time.sleep(5)
```

## Complete Example

See [complete monitor example](https://github.com/cmoxiv/wArgs/tree/main/examples/use-cases/sysmonitor) with:
- Real-time dashboard with curses
- Email/Slack alerts
- Historical data visualization
- Service management
- Log file analysis

## Best Practices

1. **Permissions** - Some operations require root/admin
2. **Intervals** - Balance accuracy vs performance
3. **Alerts** - Set realistic thresholds
4. **Logging** - Keep historical data for trends
5. **Cross-platform** - Test on target OS

## Related

- [[Building a Database CLI]] - Store metrics in database
- [[Building a File Manager CLI]] - Manage log files
- [Official Examples](https://cmoxiv.github.io/wArgs/examples/)
