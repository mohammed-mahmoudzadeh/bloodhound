"""Flask server wrapper — runs the web UI in a background thread."""
from __future__ import annotations

import sys
import threading
from pathlib import Path

from ..config import CORE_DIR


class FlaskServer:
    """Thin wrapper around the Flask app defined in core/share.py."""

    def __init__(self, share_dir=None, port=8000):
        self.share_dir = share_dir
        self.port = port
        self.bind_host = "0.0.0.0"
        self.thread = None
        self.running = False
        self._srv = None
        self.last_error = None

    def start(self):
        if self.running:
            return
        if not self.share_dir:
            raise RuntimeError("No share directory selected.")

        # Make core/ importable
        if str(CORE_DIR) not in sys.path:
            sys.path.insert(0, str(CORE_DIR))

        # Import the Flask app (cached after first import)
        import share  # type: ignore  # noqa

        # Configure
        share.set_share_dir(str(self.share_dir))
        share.PORT = self.port

        from werkzeug.serving import ThreadedWSGIServer

        class _Srv(ThreadedWSGIServer):
            allow_reuse_address = True
            daemon_threads = True

        # Create the server socket (this is where "port busy" is raised)
        try:
            self._srv = _Srv(self.bind_host, self.port, share.app)
        except OSError as ex:
            self.last_error = str(ex)
            raise

        # Run in a daemon thread
        self.thread = threading.Thread(
            target=self._srv.serve_forever,
            daemon=True,
            name="lanshare-flask",
        )
        self.thread.start()
        self.running = True
        self.last_error = None

    def stop(self):
        if not self.running:
            return
        try:
            if self._srv is not None:
                self._srv.shutdown()
                self._srv.server_close()
        except Exception:
            pass
        self.running = False
        self._srv = None
        self.thread = None

    def is_alive(self) -> bool:
        return (
            self.running
            and self.thread is not None
            and self.thread.is_alive()
        )
