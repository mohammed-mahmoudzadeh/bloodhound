"""Aligned terminal access logger — green/yellow/red status colors."""
from __future__ import annotations

import logging
import time
from datetime import datetime as _dt

from flask import Flask, Response, request


def setup_request_logger():
    for name in ("werkzeug", "werkzeug.serving", "werkzeug._internal"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = False
        lg.setLevel(logging.CRITICAL)

    logger = logging.getLogger("sf.access")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    return logger


_access_logger = setup_request_logger()
_seen_range_requests: dict[str, float] = {}


def register_access_log(app: Flask) -> None:
    @app.before_request
    def _log_request_start():
        request._sf_start = time.perf_counter()

    @app.after_request
    def _log_request_end(resp: Response):
        method = request.method
        path = request.path
        status = resp.status_code

        if path == "/events":
            return resp

        # Collapse repeated thumb/range hits within a 2s window
        if status == 206 or path.startswith("/thumb/"):
            now = time.time()
            last = _seen_range_requests.get(path, 0)
            _seen_range_requests[path] = now
            if now - last < 2.0:
                return resp

        start = getattr(request, "_sf_start", None)
        dur_ms = (time.perf_counter() - start) * 1000 if start else 0

        size = resp.content_length
        if size is None:
            size_h = "—"
        elif size < 1024:
            size_h = f"{size} B"
        elif size < 1024 * 1024:
            size_h = f"{size / 1024:.1f} K"
        elif size < 1024 * 1024 * 1024:
            size_h = f"{size / (1024 * 1024):.1f} M"
        else:
            size_h = f"{size / (1024 * 1024 * 1024):.2f} G"

        if 200 <= status < 300:
            sc = "\033[32m"; sym = "●"
        elif 300 <= status < 400:
            sc = "\033[36m"; sym = "◆"
        elif 400 <= status < 500:
            sc = "\033[33m"; sym = "▲"
        else:
            sc = "\033[31m"; sym = "✖"
        reset = "\033[0m"
        dim = "\033[2m"
        bold = "\033[1m"

        max_path = 42
        if len(path) > max_path:
            half = (max_path - 3) // 2
            path_disp = path[:half] + "…" + path[-half:]
        else:
            path_disp = path

        now_str = _dt.now().strftime("%H:%M:%S")

        _access_logger.info(
            f"{dim}{now_str}{reset}  "
            f"{sc}{sym}{reset}  "
            f"{dim}{method:<4}{reset}  "
            f"{path_disp:<{max_path}}  "
            f"{sc}{bold}{status}{reset}  "
            f"{dim}{size_h:>7}{reset}  "
            f"{dim}{dur_ms:>5.0f}ms{reset}"
        )

        return resp

    @app.after_request
    def add_security_headers(resp: Response):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        return resp
