"""Global config + constants. Single source of truth for runtime state."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


# ============================================================
# Platform detection
# ============================================================
IS_ANDROID = (
    sys.platform == "android"
    or "ANDROID_ARGUMENT" in os.environ
    or "ANDROID_BOOTLOGO" in os.environ
)


# ============================================================
# Live globals (set at runtime)
# ============================================================
_SHARE_DIR: Path = Path.cwd().resolve()
_PORT: int = 8000
_THUMB_DIR: Path | None = None


def get_share_dir() -> Path:
    return _SHARE_DIR


def set_share_dir(p: str | Path) -> Path:
    global _SHARE_DIR
    _SHARE_DIR = Path(p).expanduser().resolve()
    return _SHARE_DIR


def get_port() -> int:
    return _PORT


def set_port(p: int) -> None:
    global _PORT
    _PORT = int(p)


def get_thumb_dir() -> Path | None:
    return _THUMB_DIR


def set_thumb_dir(p: str | Path | None) -> Path | None:
    global _THUMB_DIR
    _THUMB_DIR = Path(p).expanduser().resolve() if p else None
    return _THUMB_DIR


# ============================================================
# External tools — only meaningful on desktop.
# Android uses MediaMetadataRetriever via pyjnius (no binary needed).
# ============================================================
if IS_ANDROID:
    MEDIAINFO_BIN: str | None = None
    FFPROBE_BIN: str | None = None
    FFMPEG_BIN: str | None = None
else:
    MEDIAINFO_BIN = shutil.which("mediainfo")
    FFPROBE_BIN = shutil.which("ffprobe")
    FFMPEG_BIN = shutil.which("ffmpeg")


# ============================================================
# Thumbnail tuning
# ============================================================
THUMB_SIZE_IMG = 320
THUMB_SIZE_VID = 320
THUMB_VID_SEEK = "00:00:05"
THUMB_QUALITY = "6"
THUMB_MAX_AGE_S = 60 * 60 * 24 * 7
THUMB_BUDGET_PER_PAGE = 30


# ============================================================
# Search tuning
# ============================================================
SEARCH_MAX_RESULTS = 500
SEARCH_MAX_DEPTH = 12
SEARCH_MIN_QUERY_LEN = 1

SEARCH_SKIP_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".cache",
    ".thumbnails", ".Trash", ".trash",
}


# ============================================================
# Ranges / streaming
# ============================================================
STREAM_CHUNK_SIZE = 64 * 1024
PREVIEW_MIMES_INLINE = {"image", "video", "audio", "pdf", "text"}


# ============================================================
# SSE / watcher
# ============================================================
WATCHER_INTERVAL = 1.5
WATCHER_THROTTLE = 1.0


# ============================================================
# File-type groups
# ============================================================
PREVIEW_IMAGE = {"png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "ico", "avif"}
PREVIEW_VIDEO = {"mp4", "webm", "ogv", "mov", "m4v", "mkv"}
PREVIEW_AUDIO = {"mp3", "wav", "ogg", "flac", "m4a", "aac", "opus"}
PREVIEW_PDF = {"pdf"}
PREVIEW_TEXT = {
    "txt", "md", "log", "json", "xml", "yml", "yaml", "csv", "ini",
    "conf", "cfg", "py", "js", "ts", "html", "css", "sh",
}

EXT_GROUPS = {
    "image":   PREVIEW_IMAGE | {"tiff", "heic"},
    "video":   PREVIEW_VIDEO | {"avi", "flv", "wmv"},
    "audio":   PREVIEW_AUDIO,
    "pdf":     PREVIEW_PDF,
    "doc":     {"doc", "docx", "odt", "rtf"},
    "sheet":   {"xls", "xlsx", "ods"},
    "slide":   {"ppt", "pptx", "odp"},
    "archive": {"zip", "rar", "7z", "tar", "gz", "bz2", "xz"},
    "code":    {"java", "c", "cpp", "h", "hpp", "cs", "go", "rs", "rb",
                "php", "toml", "sql"},
    "text":    PREVIEW_TEXT - {"json", "xml", "yml", "yaml", "csv"},
    "font":    {"ttf", "otf", "woff", "woff2"},
    "exe":     {"exe", "msi", "deb", "rpm", "apk", "dmg", "appimage"},
}

MIME_OVERRIDES = {
    "mkv": "video/webm",
    "mov": "video/mp4",
    "m4v": "video/mp4",
    "ogv": "video/ogg",
    "flac": "audio/flac",
}

QUALITY_LABELS = [
    (2160, "2160p"), (1440, "1440p"), (1080, "1080p"),
    (720, "720p"),   (480, "480p"),   (360, "360p"),
    (240, "240p"),   (144, "144p"),
]
