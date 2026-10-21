"""LANShare web server package — façade + entry point."""
from __future__ import annotations

from flask import Flask

from .config import (
    get_share_dir, set_share_dir,
    get_port, set_port,
    get_thumb_dir, set_thumb_dir,
)

__all__ = [
    "create_app",
    "get_share_dir", "set_share_dir",
    "get_port", "set_port",
    "get_thumb_dir", "set_thumb_dir",
]


def create_app(
    share_dir: str | None = None,
    port: int = 8000,
    thumb_dir: str | None = None,
) -> Flask:
    """Build and configure the Flask app with all routes registered."""
    from .thumbs import ensure_thumb_dir
    from .access_log import setup_request_logger
    from .routes import register_routes
    from .watcher import start_watcher
    from .probe import clear_probe_cache

    if share_dir is not None:
        set_share_dir(share_dir)
    set_port(port)

    if thumb_dir is not None:
        set_thumb_dir(thumb_dir)
    else:
        ensure_thumb_dir()

    # Drop any stale None entries from a previous run
    clear_probe_cache()

    setup_request_logger()

    app = Flask(__name__)
    register_routes(app)
    start_watcher()
    return app
