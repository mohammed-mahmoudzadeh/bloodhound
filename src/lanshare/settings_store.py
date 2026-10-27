"""Local persistence for user-configurable application settings."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from .state import AppState


def _settings_path() -> Path:
    flet_data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
    if flet_data_dir:
        data_dir = Path(flet_data_dir)
    elif sys.platform == "win32":
        data_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "LANShare"
    elif sys.platform == "darwin":
        data_dir = Path.home() / "Library" / "Application Support" / "LANShare"
    else:
        data_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "lanshare"
    return data_dir / "settings.json"


def load_settings(state: AppState) -> None:
    path = _settings_path()
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    if not isinstance(data, dict):
        raise ValueError("Settings file must contain a JSON object.")

    settings: dict[str, str] = {}
    for key in ("theme_mode", "share_dir", "port", "iface_label", "iface_ip", "device_name"):
        value = data.get(key)
        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"Setting {key!r} must be a string.")
            settings[key] = value

    iface_picked = data.get("iface_picked", False)
    if not isinstance(iface_picked, bool):
        raise ValueError("Setting 'iface_picked' must be a boolean.")
    if "theme_mode" in settings and settings["theme_mode"] not in ("auto", "light", "dark"):
        raise ValueError("Setting 'theme_mode' must be auto, light, or dark.")
    if "port" in settings:
        try:
            port = int(settings["port"])
        except ValueError as ex:
            raise ValueError("Setting 'port' must be an integer.") from ex
        if not 1024 <= port <= 65535:
            raise ValueError("Setting 'port' must be between 1024 and 65535.")

    state.theme_mode = settings.get("theme_mode", state.theme_mode)
    state.share_dir = settings.get("share_dir", state.share_dir)
    state.port = settings.get("port", state.port)
    state.iface_label = settings.get("iface_label", state.iface_label)
    state.iface_ip = settings.get("iface_ip", state.iface_ip)
    state.device_name = settings.get("device_name", state.device_name)
    state.iface_picked = iface_picked


def save_settings(state: AppState) -> None:
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "theme_mode": state.theme_mode,
        "share_dir": state.share_dir,
        "port": state.port,
        "iface_label": state.iface_label,
        "iface_ip": state.iface_ip,
        "iface_picked": state.iface_picked,
        "device_name": state.device_name,
    }

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(data, temp_file, ensure_ascii=False, indent=2)
            temp_file.write("\n")
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
