"""Best-effort IPv4 interface discovery."""
from __future__ import annotations

import re
import socket
import subprocess


def list_network_interfaces():
    results = []
    try:
        raw = subprocess.run(
            ["ifconfig"], capture_output=True, text=True, timeout=5
        ).stdout
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        raw = ""

    if raw:
        current_iface = None
        for line in raw.splitlines():
            m = re.match(r"^([A-Za-z0-9_.:\-]+):?\s", line)
            if m and not line.startswith((" ", "\t")):
                current_iface = m.group(1).rstrip(":")
                continue
            inet_match = re.search(r"inet (?:addr:)?(\d+\.\d+\.\d+\.\d+)", line)
            if inet_match and current_iface:
                ip = inet_match.group(1)
                if ip != "127.0.0.1":
                    results.append((current_iface, ip))

    if not results:
        try:
            hostname = socket.gethostname()
            _, _, addrs = socket.gethostbyname_ex(hostname)
            for a in addrs:
                if a != "127.0.0.1":
                    results.append(("local", a))
        except OSError:
            pass

    seen = set()
    unique = []
    for name, ip in results:
        if ip not in seen:
            seen.add(ip)
            unique.append((name, ip))
    return unique
