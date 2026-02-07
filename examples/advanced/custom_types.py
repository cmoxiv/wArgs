#!/usr/bin/env python3
"""Advanced CLI with custom types example.

Demonstrates:
- Custom type converters
- Complex type annotations
- Hidden arguments
- Argument groups
- Mutually exclusive options

Usage:
    python custom_types.py send --to user@example.com --body "Hello"
    python custom_types.py --json list
    python custom_types.py lookup --ip 192.168.1.1
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from wArgs import Arg, converter, wArgs


# Custom types
class EmailAddress:
    """A validated email address."""

    def __init__(self, address: str) -> None:
        if "@" not in address or "." not in address.split("@")[1]:
            raise ValueError(f"Invalid email address: {address}")
        self.address = address

    def __str__(self) -> str:
        return self.address

    def __repr__(self) -> str:
        return f"EmailAddress({self.address!r})"


class IPAddress:
    """A validated IPv4 address."""

    def __init__(self, address: str) -> None:
        parts = address.split(".")
        if len(parts) != 4:
            raise ValueError(f"Invalid IP address: {address}")
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                raise ValueError(f"Invalid IP address: {address}")
        self.parts = [int(p) for p in parts]

    def __str__(self) -> str:
        return ".".join(str(p) for p in self.parts)

    def __repr__(self) -> str:
        return f"IPAddress({str(self)!r})"


# Register custom converters
@converter(EmailAddress)
def convert_email(value: str) -> EmailAddress:
    """Convert string to EmailAddress."""
    return EmailAddress(value)


@converter(IPAddress)
def convert_ip(value: str) -> IPAddress:
    """Convert string to IPAddress."""
    return IPAddress(value)


@wArgs(prog="messenger")
class Messenger:
    """Advanced messaging CLI with custom types.

    Demonstrates custom type converters, argument groups,
    and mutually exclusive options.
    """

    def __init__(
        self,
        # Output format options (mutually exclusive)
        json: Annotated[bool, Arg(mutually_exclusive="format", help="JSON output")] = False,
        csv: Annotated[bool, Arg(mutually_exclusive="format", help="CSV output")] = False,
        # Hidden debug option
        debug: Annotated[bool, Arg(hidden=True)] = False,
    ) -> None:
        """Initialize with global options.

        Args:
            json: Output in JSON format.
            csv: Output in CSV format.
            debug: Enable debug mode (hidden).
        """
        self.output_format = "json" if json else "csv" if csv else "text"
        self.debug = debug

    def _output(self, data: dict[str, Any]) -> None:
        """Output data in the selected format."""
        if self.debug:
            print(f"[DEBUG] Format: {self.output_format}")
            print(f"[DEBUG] Data: {data}")

        if self.output_format == "json":
            import json

            print(json.dumps(data, indent=2, default=str))
        elif self.output_format == "csv":
            keys = list(data.keys())
            print(",".join(keys))
            print(",".join(str(data[k]) for k in keys))
        else:
            for key, value in data.items():
                print(f"{key}: {value}")

    def send(
        self,
        to: Annotated[EmailAddress, Arg(group="Message", help="Recipient email")],
        body: Annotated[str, Arg(group="Message", help="Message body")],
        subject: Annotated[str, Arg(group="Message", help="Subject line")] = "No Subject",
        cc: Annotated[list[EmailAddress], Arg(group="Recipients")] = [],
        priority: Annotated[int, Arg(group="Options", help="Priority 1-5")] = 3,
        schedule: Annotated[datetime | None, Arg(group="Options")] = None,
    ) -> None:
        """Send a message.

        Args:
            to: Primary recipient email address.
            body: The message body.
            subject: Email subject line.
            cc: CC recipients.
            priority: Message priority (1=low, 5=high).
            schedule: Schedule for later delivery.
        """
        result = {
            "to": str(to),
            "subject": subject,
            "body": body[:50] + "..." if len(body) > 50 else body,
            "priority": priority,
            "cc": [str(e) for e in cc] if cc else [],
        }
        if schedule:
            result["scheduled"] = schedule.isoformat()

        print("Message sent!")
        self._output(result)

    def list(self, limit: int = 10, unread: bool = False) -> None:
        """List messages.

        Args:
            limit: Maximum messages to show.
            unread: Only show unread messages.
        """
        # Simulated message list
        messages = [
            {"id": 1, "from": "alice@example.com", "subject": "Hello", "unread": True},
            {"id": 2, "from": "bob@example.com", "subject": "Meeting", "unread": False},
            {"id": 3, "from": "carol@example.com", "subject": "Report", "unread": True},
        ]

        if unread:
            messages = [m for m in messages if m["unread"]]

        messages = messages[:limit]

        for msg in messages:
            self._output(msg)
            print()

    def lookup(self, ip: IPAddress) -> None:
        """Lookup information about an IP address.

        Args:
            ip: IP address to lookup.
        """
        # Simulated lookup
        result = {
            "ip": str(ip),
            "hostname": f"host-{ip.parts[-1]}.example.com",
            "country": "US",
            "city": "San Francisco",
        }
        self._output(result)


if __name__ == "__main__":
    Messenger()
