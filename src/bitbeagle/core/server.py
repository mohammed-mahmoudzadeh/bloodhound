"""Flask server wrapper — runs the web UI in a background thread."""
from __future__ import annotations

import socket
import threading

from werkzeug.serving import ThreadedWSGIServer

from .share import create_app
from .share.config import set_share_dir, set_port


class PortInUseError(OSError):
    """Raised when the requested port is already bound by another process."""


def _port_is_free(host: str, port: int) -> bool:
    """Return True if we can bind (host, port) right now.

    Uses SO_REUSEADDR so it mirrors the actual server binding behaviour.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            return False
    return True


class FlaskServer:
    """Thin wrapper around the Flask app defined in core/share/."""

    def __init__(self, share_dir=None, port=8000):
        self.share_dir = share_dir
        self.port = port
        self.bind_host = "0.0.0.0"
        self.thread = None
        self.running = False
        self._srv = None
        self._app = None
        self.last_error = None

    def start(self):
        if self.running:
            return
        if not self.share_dir:
            raise RuntimeError("No share directory selected.")

        # Fail fast with a clear, catchable error when the port is busy.
        # This prevents the WSGI server from being half-constructed and
        # leaves no dangling daemon thread behind.
        if not _port_is_free(self.bind_host, self.port):
            self.last_error = f"Port {self.port} is already in use."
            raise PortInUseError(self.last_error)

        # Build the app once, reuse on restart
        if self._app is None:
            self._app = create_app(share_dir=str(self.share_dir), port=self.port)
        else:
            set_share_dir(str(self.share_dir))
            set_port(self.port)

        class _Srv(ThreadedWSGIServer):
            allow_reuse_address = True
            daemon_threads = True

        try:
            self._srv = _Srv(self.bind_host, self.port, self._app)
        except OSError as ex:
            self.last_error = str(ex)
            raise

        self.thread = threading.Thread(
            target=self._srv.serve_forever,
            daemon=True,
            name="bitbeagle-flask",
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