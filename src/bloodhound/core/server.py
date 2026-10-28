"""Flask server wrapper — runs the web UI in a background thread."""
from __future__ import annotations

import threading

from werkzeug.serving import ThreadedWSGIServer

from .share import create_app
from .share.config import set_share_dir, set_port


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
            name="bloodhound-flask",
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
