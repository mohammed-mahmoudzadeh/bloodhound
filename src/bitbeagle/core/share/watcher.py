"""Filesystem watcher -> SSE broadcast."""
from __future__ import annotations

import os
import queue
import threading
import time
from pathlib import Path

from flask import Response

from .config import WATCHER_INTERVAL, WATCHER_THROTTLE, get_share_dir


# ============================================================
# SSE clients + emit throttle
# ============================================================
_sse_clients: set[queue.Queue] = set()
_sse_clients_lock = threading.Lock()

_sse_last_emit: dict[str, float] = {}
_sse_emit_lock = threading.Lock()


def _notify_clients(path: str):
    payload = f"event: changed\ndata: {path}\n\n"
    with _sse_clients_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(payload)
            except Exception:
                dead.append(q)
        for q in dead:
            _sse_clients.discard(q)


# ============================================================
# Directory scanning
# ============================================================
def _scan_dir(path: Path):
    result = {}
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    st = entry.stat()
                    result[entry.name] = (st.st_mtime_ns, st.st_size)
                except OSError:
                    continue
    except (PermissionError, FileNotFoundError, NotADirectoryError):
        pass
    return result


def _build_snapshot():
    snapshots = {}
    base = get_share_dir()

    try:
        snapshots[base] = _scan_dir(base)
    except Exception:
        pass

    try:
        with os.scandir(base) as it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        snapshots[Path(entry.path)] = _scan_dir(Path(entry.path))
                except OSError:
                    continue
    except (PermissionError, FileNotFoundError):
        pass

    return snapshots


# ============================================================
# Watcher loop
# ============================================================
def _watcher_loop():
    last_snapshot = _build_snapshot()

    while True:
        time.sleep(WATCHER_INTERVAL)
        try:
            current = _build_snapshot()
            changed_dirs = set()

            for path, snap in current.items():
                old = last_snapshot.get(path)
                if old != snap:
                    changed_dirs.add(path)

            for path in list(last_snapshot.keys()):
                if path not in current:
                    changed_dirs.add(path.parent)

            last_snapshot = current

            if not changed_dirs:
                continue

            now = time.time()
            with _sse_emit_lock:
                for d in changed_dirs:
                    key = str(d)
                    last = _sse_last_emit.get(key, 0)
                    if now - last < WATCHER_THROTTLE:
                        continue
                    _sse_last_emit[key] = now
                    try:
                        rel = "/" + os.path.relpath(d, get_share_dir()).replace(os.sep, "/")
                        if rel == "/.":
                            rel = "/"
                        _notify_clients(rel)
                    except Exception:
                        pass
        except Exception:
            pass


def start_watcher():
    t = threading.Thread(target=_watcher_loop, daemon=True, name="sf-watcher")
    t.start()
    return t


# ============================================================
# SSE route
# ============================================================
def sse_route():
    def gen():
        q: queue.Queue = queue.Queue(maxsize=64)
        with _sse_clients_lock:
            _sse_clients.add(q)

        try:
            yield "event: hello\ndata: connected\n\n"

            last_beat = time.time()
            while True:
                try:
                    msg = q.get(timeout=1.0)
                    yield msg
                except queue.Empty:
                    pass

                if time.time() - last_beat > 20:
                    last_beat = time.time()
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sse_clients_lock:
                _sse_clients.discard(q)

    resp = Response(gen(), mimetype="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    resp.headers["Connection"] = "keep-alive"
    return resp
