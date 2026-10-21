"""Tuned threaded WSGI server — socket-level tuning for video streaming."""
from __future__ import annotations

import inspect as _inspect
import socket

from flask import Flask
from werkzeug.serving import ThreadedWSGIServer


def run_tuned_server(app: Flask, host: str, port: int) -> None:
    class StreamingServer(ThreadedWSGIServer):
        daemon_threads = True
        request_queue_size = 256
        allow_reuse_address = True

        def server_bind(self):
            super().server_bind()

            try:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512 * 1024)
            except OSError:
                pass
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 512 * 1024)
            except OSError:
                pass
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except OSError:
                pass
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass

        def get_request(self):
            conn, addr = super().get_request()

            try:
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            except OSError:
                pass

            # Disable TCP_NODELAY so Nagle coalesces packets.
            try:
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
            except OSError:
                pass

            try:
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512 * 1024)
            except OSError:
                pass

            # Prefer BBR, fall back to CUBIC
            TCP_CONGESTION = getattr(socket, "TCP_CONGESTION", 13)
            for cc in ("bbr", "cubic"):
                try:
                    conn.setsockopt(
                        socket.IPPROTO_TCP,
                        TCP_CONGESTION,
                        cc.encode() + b"\0" * (15 - len(cc)),
                    )
                    break
                except (OSError, AttributeError):
                    continue

            try:
                conn.setsockopt(
                    socket.IPPROTO_TCP,
                    getattr(socket, "TCP_QUICKACK", 12),
                    1,
                )
            except (OSError, AttributeError):
                pass

            return conn, addr

    sig = _inspect.signature(ThreadedWSGIServer.__init__)
    kwargs = {}
    if "threaded" in sig.parameters:
        kwargs["threaded"] = True

    server = StreamingServer(host, port, app, **kwargs)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("  Server stopped.")
        print()
    finally:
        try:
            server.server_close()
        except Exception:
            pass
