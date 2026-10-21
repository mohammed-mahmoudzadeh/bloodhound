"""Pure helper functions — no Flask app, no imports from routes."""
from __future__ import annotations

import mimetypes as _mt
from pathlib import Path

from flask import abort

from .config import (
    EXT_GROUPS, MIME_OVERRIDES,
    PREVIEW_IMAGE, PREVIEW_VIDEO, PREVIEW_AUDIO,
    PREVIEW_PDF, PREVIEW_TEXT,
    get_share_dir,
)


def get_ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def get_icon_key(filename: str) -> str:
    ext = get_ext(filename)
    for group, exts in EXT_GROUPS.items():
        if ext in exts:
            return group
    return "file"


def preview_kind(filename: str):
    ext = get_ext(filename)
    if ext in PREVIEW_IMAGE: return "image"
    if ext in PREVIEW_VIDEO: return "video"
    if ext in PREVIEW_AUDIO: return "audio"
    if ext in PREVIEW_PDF:   return "pdf"
    if ext in PREVIEW_TEXT:  return "text"
    return None


def human_size(num: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.1f} {unit}" if unit != "B" else f"{int(num)} B"
        num /= 1024
    return f"{num:.1f} PB"


def safe_path(rel: str) -> Path:
    root = get_share_dir()
    target = (root / rel).resolve()
    if root not in target.parents and target != root:
        abort(403)
    return target


def guess_mimetype(path: Path) -> str:
    ext = get_ext(path.name)
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    mt, _ = _mt.guess_type(str(path))
    return mt or "application/octet-stream"
