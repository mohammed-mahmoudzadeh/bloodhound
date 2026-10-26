"""Centralized application state."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class LogEntry:
    time: str
    message: str
    level: str = "info"          # info | ok | warn | err


@dataclass
class AppState:
    # Theme
    dark: bool = False
    theme_mode: str = "auto"     # auto | light | dark

    # Navigation
    view: int = 0

    # Server
    server_running: bool = False
    share_dir: str = ""
    port: str = "8000"

    # Interfaces
    interfaces: List[Tuple[str, str]] = field(default_factory=list)
    iface_index: int = 0
    iface_label: str = "All Interfaces"
    iface_ip: str = "0.0.0.0"
    iface_picked: bool = False

    # Logs
    logs: List[LogEntry] = field(default_factory=list)

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def add_log(self, time_str: str, message: str, level: str = "info"):
        self.logs.append(LogEntry(time_str, message, level))
        if len(self.logs) > 500:
            self.logs = self.logs[-500:]

    @property
    def bind_host(self) -> str:
        return self.iface_ip

    @property
    def display_ip(self) -> str:
        ip = self.iface_ip
        if ip == "0.0.0.0":
            for _, iip in self.interfaces:
                if iip not in ("0.0.0.0", "127.0.0.1"):
                    return iip
        return ip

    @property
    def access_url(self) -> str:
        return f"http://{self.display_ip}:{self.port}"

    @property
    def share_dir_display(self) -> str:
        return self.share_dir or "No folder selected"