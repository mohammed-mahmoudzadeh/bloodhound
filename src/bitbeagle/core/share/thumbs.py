"""Thumbnail generation (ffmpeg) and serving."""
from __future__ import annotations

import hashlib
import re
import subprocess
import time
from pathlib import Path

from flask import Response, abort, url_for

from .config import (
    FFMPEG_BIN,
    THUMB_SIZE_IMG, THUMB_SIZE_VID, THUMB_VID_SEEK,
    THUMB_QUALITY, THUMB_MAX_AGE_S,
    get_thumb_dir, set_thumb_dir,
)
from .range import file_stream


def ensure_thumb_dir() -> Path | None:
    """Create the thumbnail cache directory and register it globally."""
    p = Path.home() / ".cache" / "shared-files-thumbs"
    try:
        p.mkdir(parents=True, exist_ok=True)
        set_thumb_dir(p)
        return p
    except OSError:
        set_thumb_dir(None)
        return None


def _thumb_path(src: Path) -> Path:
    thumb_dir = get_thumb_dir()
    key = hashlib.md5(str(src).encode()).hexdigest()
    return thumb_dir / (key + ".jpg")


def _thumb_is_fresh(thumb: Path, src: Path) -> bool:
    try:
        if not thumb.exists():
            return False
        t_mtime = thumb.stat().st_mtime
        s_mtime = src.stat().st_mtime
        if t_mtime < s_mtime:
            return False
        if time.time() - t_mtime > THUMB_MAX_AGE_S:
            return False
        return True
    except OSError:
        return False


def _make_image_thumb(src: Path, dst: Path) -> bool:
    if not FFMPEG_BIN:
        return False
    try:
        result = subprocess.run(
            [
                FFMPEG_BIN, "-y", "-loglevel", "error",
                "-i", str(src),
                "-vf", f"scale={THUMB_SIZE_IMG}:{THUMB_SIZE_IMG}:force_original_aspect_ratio=decrease",
                "-frames:v", "1",
                "-q:v", THUMB_QUALITY,
                str(dst),
            ],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0 and dst.exists()
    except (subprocess.SubprocessError, OSError):
        return False


def _make_video_thumb(src: Path, dst: Path) -> bool:
    if not FFMPEG_BIN:
        return False
    try:
        result = subprocess.run(
            [
                FFMPEG_BIN, "-y", "-loglevel", "error",
                "-ss", THUMB_VID_SEEK,
                "-i", str(src),
                "-vf", f"scale={THUMB_SIZE_VID}:{THUMB_SIZE_VID}:force_original_aspect_ratio=decrease",
                "-frames:v", "1",
                "-q:v", THUMB_QUALITY,
                str(dst),
            ],
            capture_output=True, timeout=15,
        )
        if result.returncode == 0 and dst.exists():
            return True

        result = subprocess.run(
            [
                FFMPEG_BIN, "-y", "-loglevel", "error",
                "-i", str(src),
                "-vf", f"scale={THUMB_SIZE_VID}:{THUMB_SIZE_VID}:force_original_aspect_ratio=decrease",
                "-frames:v", "1",
                "-q:v", THUMB_QUALITY,
                str(dst),
            ],
            capture_output=True, timeout=15,
        )
        return result.returncode == 0 and dst.exists()
    except (subprocess.SubprocessError, OSError):
        return False


def get_or_create_thumb(src: Path, kind: str):
    """Return URL to a thumbnail for `src`, generating if needed."""
    thumb_dir = get_thumb_dir()
    if kind not in ("image", "video"):
        return None
    if thumb_dir is None or FFMPEG_BIN is None:
        return None

    thumb = _thumb_path(src)
    if _thumb_is_fresh(thumb, src):
        v = int(src.stat().st_mtime)
        return url_for("serve_thumb", name=thumb.name, v=v)

    try:
        thumb_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    ok = False
    if kind == "image":
        ok = _make_image_thumb(src, thumb)
    elif kind == "video":
        ok = _make_video_thumb(src, thumb)

    if ok:
        try:
            v = int(src.stat().st_mtime)
        except OSError:
            v = 0
        return url_for("serve_thumb", name=thumb.name, v=v)
    return None


def serve_thumb_route(name: str):
    """Serve a cached thumbnail by its hashed filename."""
    thumb_dir = get_thumb_dir()
    if thumb_dir is None:
        abort(404)

    if not re.fullmatch(r"[a-f0-9]{32}\.jpg", name):
        abort(404)

    path = thumb_dir / name
    try:
        st = path.stat()
    except OSError:
        abort(404)

    return Response(
        file_stream(path, 0, st.st_size - 1),
        mimetype="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "ETag": f'"{name}-{int(st.st_mtime)}"',
            "X-Content-Type-Options": "nosniff",
        },
        direct_passthrough=True,
    )
