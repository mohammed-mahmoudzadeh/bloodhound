"""Android permission helpers (permission_handler wrapper)."""
from __future__ import annotations

from ..config import IS_ANDROID, IS_LINUX

try:
    import flet_permission_handler as fph
    PH_AVAILABLE = True
except ImportError:
    PH_AVAILABLE = False


def build_handler():
    """Create a PermissionHandler instance or return None."""
    if not (PH_AVAILABLE and not IS_LINUX):
        return None
    try:
        return fph.PermissionHandler()
    except Exception:
        return None


async def request_storage_permission(ph, log_fn):
    """Ask for MANAGE_EXTERNAL_STORAGE on Android."""
    if not IS_ANDROID or ph is None:
        log_fn("Not available.", "warn")
        return
    log_fn("Checking permission…", "info")
    try:
        loc = await ph.get_status(fph.Permission.LOCATION)
        if not loc or loc.name != "GRANTED":
            await ph.request(fph.Permission.LOCATION)
    except Exception:
        pass
    try:
        status = await ph.get_status(fph.Permission.MANAGE_EXTERNAL_STORAGE)
        if status and status.name == "GRANTED":
            log_fn("Already granted.", "ok")
            return
        status = await ph.request(fph.Permission.MANAGE_EXTERNAL_STORAGE)
        if not (status and status.name == "GRANTED"):
            log_fn("Opening settings…", "warn")
            await ph.open_app_settings()
    except Exception as ex:
        log_fn(f"Perm error: {ex}", "err")
