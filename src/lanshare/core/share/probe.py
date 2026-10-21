"""Video probing — cross-platform.

- Android: MediaMetadataRetriever (pyjnius, part of the OS)
- Desktop: pymediainfo (bundled MediaInfo, no external binary needed)
- Fallback: ffprobe binary if pymediainfo is unavailable
- Final fallback: None (no badge shown)
"""
from __future__ import annotations

import json
import subprocess
from functools import lru_cache
from pathlib import Path

from .config import (
    IS_ANDROID, MEDIAINFO_BIN, FFPROBE_BIN, QUALITY_LABELS,
)


# ============================================================
# Quality labels
# ============================================================
def quality_label_from_height(h: int) -> str:
    for height, label in QUALITY_LABELS:
        if h >= height:
            return label
    return f"{h}p"


def standard_name_from_height(h: int) -> str:
    if h >= 4320: return "8K"
    if h >= 2160: return "4K"
    if h >= 1440: return "2K"
    if h >= 1080: return "FHD"
    if h >= 720:  return "HD"
    return "SD"


# ============================================================
# Android path — MediaMetadataRetriever (no binary)
# ============================================================
def _probe_android(path_str: str):
    try:
        from jnius import autoclass
    except ImportError:
        return None

    try:
        R = autoclass("android.media.MediaMetadataRetriever")
        retriever = R()
        try:
            retriever.setDataSource(path_str)
            h_s = retriever.extractMetadata(R.METADATA_KEY_VIDEO_HEIGHT)
            w_s = retriever.extractMetadata(R.METADATA_KEY_VIDEO_WIDTH)
            if not h_s:
                return None
            height = int(h_s)
            width = int(w_s) if w_s else 0
            if height <= 0:
                return None
            return {
                "width": width,
                "height": height,
                "label": quality_label_from_height(height),
                "standard": standard_name_from_height(height),
            }
        finally:
            try:
                retriever.release()
            except Exception:
                pass
    except Exception:
        return None


# ============================================================
# Desktop path 1 — pymediainfo (bundled MediaInfo)
# ============================================================
def _probe_pymediainfo(path_str: str):
    try:
        from pymediainfo import MediaInfo
    except ImportError:
        return None

    try:
        info = MediaInfo.parse(path_str)
        for track in info.video_tracks:
            if track.height:
                height = int(track.height)
                width = int(track.width) if track.width else 0
                return {
                    "width": width,
                    "height": height,
                    "label": quality_label_from_height(height),
                    "standard": standard_name_from_height(height),
                }
    except Exception:
        return None
    return None


# ============================================================
# Desktop path 2 — ffprobe binary fallback
# ============================================================
def _probe_ffprobe(path_str: str):
    if not FFPROBE_BIN:
        return None

    try:
        cmd = [
            FFPROBE_BIN, "-v", "quiet", "-print_format", "json",
            "-show_streams", path_str,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode != 0 or not result.stdout.strip():
            return None
        data = json.loads(result.stdout)

        video = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )
        if not video or not video.get("height"):
            return None

        height = int(video["height"])
        width = int(video.get("width", 0))
        return {
            "width": width,
            "height": height,
            "label": quality_label_from_height(height),
            "standard": standard_name_from_height(height),
        }
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError, ValueError):
        return None


# ============================================================
# Public API
# ============================================================
@lru_cache(maxsize=1024)
def probe_video(path_str: str, mtime: float):
    """Return {width, height, label, standard} or None.

    Cached by (path, mtime) so a file's mtime bump forces a re-probe.
    """
    if IS_ANDROID:
        return _probe_android(path_str)

    info = _probe_pymediainfo(path_str)
    if info:
        return info

    return _probe_ffprobe(path_str)


def probe_video_path(p: Path):
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return None
    return probe_video(str(p), mtime)


def clear_probe_cache() -> None:
    """Force the next probe to actually run (drop the lru_cache)."""
    probe_video.cache_clear()
