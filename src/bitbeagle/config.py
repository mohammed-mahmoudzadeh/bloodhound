"""Application configuration and runtime flags."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ------------------------------------------------------------
# Environment detection
# ------------------------------------------------------------
IS_ANDROID = (
    sys.platform == "android"
    or "ANDROID_ARGUMENT" in os.environ
    or "ANDROID_BOOTLOGO" in os.environ
)

# IMPORTANT: Android reports sys.platform == "linux", so we must
# explicitly exclude it from IS_LINUX.
IS_LINUX = sys.platform.startswith("linux") and not IS_ANDROID
IS_DESKTOP = not IS_ANDROID

# ------------------------------------------------------------
# Window defaults (desktop)
# ------------------------------------------------------------
WINDOW_DEFAULT_WIDTH = 1100
WINDOW_DEFAULT_HEIGHT = 780
WINDOW_MIN_WIDTH = 400
WINDOW_MIN_HEIGHT = 600

# ------------------------------------------------------------
# Server defaults
# ------------------------------------------------------------
DEFAULT_PORT = 8000
PORT_MIN = 1024
PORT_MAX = 65535

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
PACKAGE_DIR = Path(__file__).parent
CORE_DIR = PACKAGE_DIR / "core"
