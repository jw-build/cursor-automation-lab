"""
Production-style CLI: hello, time, sysinfo, inspect.
"""

import argparse
import getpass
import shutil
import socket
from datetime import datetime


# -----------------------------------------------------------------------------
# Formatting
# -----------------------------------------------------------------------------

LABEL_WIDTH = 10


def fmt_field(label: str, value: str) -> str:
    """Format a single key-value line with aligned labels."""
    return f"  {label:<{LABEL_WIDTH}} {value}"


def format_bytes(n: float) -> str:
    """Convert bytes to human-readable string (KiB, MiB, GiB, ...)."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PiB"


# -----------------------------------------------------------------------------
# Data helpers (pure, return values)
# -----------------------------------------------------------------------------


def _read_uptime_seconds() -> float:
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])


def _format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    rem = int(seconds % 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if days:
        return f"{days} day(s), {h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def _get_disk_usage() -> tuple[float, str]:
    usage = shutil.disk_usage("/")
    pct = 100 * usage.used / usage.total if usage.total else 0.0
    s = f"{format_bytes(usage.used)} used / {format_bytes(usage.total)} total ({pct:.0f}%)"
    return (pct, s)


def _get_memory_usage_str() -> str:
    with open("/proc/meminfo") as f:
        lines = {k: int(v.split()[0]) * 1024 for k, v in (line.split(":", 1) for line in f)}
    total = lines.get("MemTotal", 0)
    available = lines.get("MemAvailable", lines.get("MemFree", 0))
    used = total - available
    pct = 100 * used / total if total else 0
    return f"{format_bytes(used)} used / {format_bytes(total)} total ({pct:.0f}%)"


# -----------------------------------------------------------------------------
# Commands (each command is a function; no args used for these)
# -----------------------------------------------------------------------------


def cmd_hello(_args: argparse.Namespace) -> None:
    print("hello cursor")


def cmd_time(_args: argparse.Namespace) -> None:
    print(datetime.now())


def cmd_sysinfo(_args: argparse.Namespace) -> None:
    uptime_str = _format_uptime(_read_uptime_seconds())
    print(fmt_field("hostname", socket.gethostname()))
    print(fmt_field("user", getpass.getuser()))
    print(fmt_field("uptime", uptime_str))


def cmd_inspect(_args: argparse.Namespace) -> None:
    uptime_str = _format_uptime(_read_uptime_seconds())
    print(fmt_field("hostname", socket.gethostname()))
    print(fmt_field("user", getpass.getuser()))
    print(fmt_field("uptime", uptime_str))
    disk_pct, disk_str = _get_disk_usage()
    print(fmt_field("disk", disk_str))
    print(fmt_field("disk status", "WARNING" if disk_pct > 80 else "OK"))
    print(fmt_field("memory", _get_memory_usage_str()))


# -----------------------------------------------------------------------------
# CLI setup and main
# -----------------------------------------------------------------------------

COMMANDS = (
    ("hello", "Print hello cursor", cmd_hello),
    ("time", "Print current time", cmd_time),
    ("sysinfo", "Print hostname, user, uptime", cmd_sysinfo),
    ("inspect", "Print hostname, user, uptime, disk, memory", cmd_inspect),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple CLI tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text, _ in COMMANDS:
        subparsers.add_parser(name, help=help_text)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    handlers = {name: fn for name, _, fn in COMMANDS}
    handlers[args.command](args)


if __name__ == "__main__":
    main()
