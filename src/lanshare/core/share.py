#!/usr/bin/env python3
"""
LANShare — web file browser served by the app.

Exposes a Flask app that lists and streams files from SHARE_DIR.
`SHARE_DIR` is set externally by `lanshare.core.server.FlaskServer`
via `set_share_dir()`.
"""
from __future__ import annotations

import datetime
import json
import mimetypes as _mt
import os
import shutil
import socket
import struct
import subprocess
from functools import lru_cache
from pathlib import Path

from flask import (
    Flask,
    abort,
    jsonify,
    render_template_string,
    request,
    send_file,
    url_for,
)

app = Flask(__name__)

# ------------------------------------------------------------
# SHARE_DIR — set externally via set_share_dir()
# ------------------------------------------------------------
SHARE_DIR: Path | None = None
PORT: int = 8000


def set_share_dir(path: str) -> Path:
    """Set the directory being shared. Created if missing."""
    global SHARE_DIR
    p = Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    SHARE_DIR = p
    return SHARE_DIR


def _require_share_dir() -> Path:
    if SHARE_DIR is None:
        abort(500, "Share directory not configured.")
    return SHARE_DIR


# ------------------------------------------------------------
# Network helpers (kept here for standalone use)
# ------------------------------------------------------------
MEDIAINFO_BIN = shutil.which("mediainfo") or shutil.which("ffprobe")


def list_network_interfaces():
    """Best-effort list of (iface, ip) for local IPv4 addresses."""
    results = []

    try:
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                parts = line.strip().split()
                if len(parts) >= 3 and parts[1] == "00000000":
                    iface = parts[0]
                    try:
                        import fcntl
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        packed = struct.pack("256s", iface[:15].encode())
                        ip = socket.inet_ntoa(
                            fcntl.ioctl(s.fileno(), 0x8915, packed)[20:24]
                        )
                        s.close()
                        if ip and not ip.startswith("127."):
                            results.append((iface, ip))
                    except Exception:
                        pass
    except Exception:
        pass

    if not results:
        try:
            hostname = socket.gethostname()
            _, _, addrs = socket.gethostbyname_ex(hostname)
            for a in addrs:
                if not a.startswith("127."):
                    results.append(("local", a))
        except OSError:
            pass

    if not results:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if not ip.startswith("127."):
                results.append(("wlan", ip))
        except Exception:
            pass

    seen = set()
    unique = []
    for name, ip in results:
        if ip not in seen:
            seen.add(ip)
            unique.append((name, ip))
    return unique


def get_local_ip() -> str:
    """Get the primary local IP — works on desktop and Android."""
    try:
        # Android: use our own network module if available
        import sys
        from pathlib import Path
        core_dir = Path(__file__).parent
        if str(core_dir) not in sys.path:
            sys.path.insert(0, str(core_dir))
        from network import get_primary_ip
        return get_primary_ip()
    except Exception:
        pass

    # Desktop fallback
    ifaces = list_network_interfaces()
    return ifaces[0][1] if ifaces else "127.0.0.1"

# ============================================================
# Icons — inline SVG paths keyed by file group
# ============================================================
ICON_SVG = {
    "folder":  ('<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>', "#f5b544"),
    "image":   ('<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>', "#e879f9"),
    "video":   ('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M10 9l5 3-5 3V9z"/>', "#a78bfa"),
    "audio":   ('<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>', "#f472b6"),
    "pdf":     ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 15h6"/>', "#f87171"),
    "doc":     ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h5"/>', "#60a5fa"),
    "sheet":   ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h8M12 11v8"/>', "#34d399"),
    "slide":   ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><rect x="8" y="12" width="8" height="6" rx="1"/>', "#fb923c"),
    "archive": ('<path d="M21 8v13H3V8"/><path d="M1 3h22v5H1z"/><path d="M10 12h4"/>', "#facc15"),
    "code":    ('<path d="M16 18l6-6-6-6"/><path d="M8 6l-6 6 6 6"/>', "#22d3ee"),
    "text":    ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h8M8 9h2"/>', "#94a3b8"),
    "font":    ('<path d="M4 20l8-16 8 16"/><path d="M8 14h8"/>', "#c084fc"),
    "exe":     ('<path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/><circle cx="12" cy="12" r="3"/>', "#a1a1aa"),
    "file":    ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>', "#71717a"),
    "up":      ('<path d="M12 19V5"/><path d="M5 12l7-7 7 7"/>', "#a1a1aa"),
    "down":    ('<path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/>', "#a1a1aa"),
    "right":   ('<path d="M9 18l6-6-6-6"/>', "#a1a1aa"),
    "grid":    ('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>', "#d4d4d8"),
    "list":    ('<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>', "#d4d4d8"),
    "quality": ('<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="10" cy="18" r="2"/>', "#d4d4d8"),
    "sun":     ('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>', "#d4d4d8"),
    "moon":    ('<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>', "#d4d4d8"),
    "eye":     ('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>', "#d4d4d8"),
    "eye-off": ('<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>', "#d4d4d8"),
}

# ============================================================
# File-type groups
# ============================================================
PREVIEW_IMAGE = {"png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "ico", "avif"}
PREVIEW_VIDEO = {"mp4", "webm", "ogv", "mov", "m4v", "mkv"}
PREVIEW_AUDIO = {"mp3", "wav", "ogg", "flac", "m4a", "aac", "opus"}
PREVIEW_PDF   = {"pdf"}
PREVIEW_TEXT  = {
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
}

QUALITY_LABELS = [
    (2160, "2160p"), (1440, "1440p"), (1080, "1080p"),
    (720, "720p"),   (480, "480p"),   (360, "360p"),
    (240, "240p"),   (144, "144p"),
]


# ============================================================
# Utility functions
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


def _to_int(x, default=0) -> int:
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return default


@lru_cache(maxsize=1024)
def probe_video(path_str: str, mtime: float):
    """Probe a video file via mediainfo or ffprobe. Cached by (path, mtime)."""
    if not MEDIAINFO_BIN:
        return None
    try:
        if MEDIAINFO_BIN.endswith("ffprobe"):
            cmd = [MEDIAINFO_BIN, "-v", "quiet", "-print_format", "json",
                   "-show_streams", "-show_format", path_str]
        else:
            cmd = [MEDIAINFO_BIN, path_str, "--Output=JSON"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode != 0 or not result.stdout.strip():
            return None
        data = json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return None

    # ---- ffprobe ----
    if "streams" in data:
        video = next(
            (s for s in data["streams"] if s.get("codec_type") == "video"),
            None,
        )
        if not video:
            return None
        height = _to_int(video.get("height"))
        width = _to_int(video.get("width"))
        if not height:
            return None
        bitrate = _to_int(video.get("bit_rate"))
        if not bitrate:
            bitrate = _to_int(data.get("format", {}).get("bit_rate"))
        fps = 0.0
        try:
            fr = video.get("r_frame_rate", "0/1")
            num, den = fr.split("/")
            fps = round(float(num) / float(den), 2) if float(den) else 0.0
        except Exception:
            pass
        duration = 0.0
        try:
            duration = float(data.get("format", {}).get("duration", 0))
        except Exception:
            pass
        return {
            "width": width, "height": height, "bitrate": bitrate,
            "codec": (video.get("codec_name") or "").lower(),
            "fps": fps, "duration": duration,
            "label": quality_label_from_height(height),
            "standard": standard_name_from_height(height),
        }

    # ---- mediainfo ----
    media = data.get("media") or {}
    tracks = media.get("track") or []
    if isinstance(tracks, dict):
        tracks = [tracks]
    video = next((t for t in tracks if t.get("@type") == "Video"), None)
    if not video:
        return None
    height = _to_int(video.get("Height"))
    width = _to_int(video.get("Width"))
    if not height:
        return None
    bitrate = _to_int(video.get("BitRate")) or _to_int(video.get("BitRate_Nominal"))
    if not bitrate:
        general = next((t for t in tracks if t.get("@type") == "General"), None)
        if general:
            bitrate = _to_int(general.get("OverallBitRate"))
    fps = 0.0
    try:
        if video.get("FrameRate"):
            fps = round(float(video["FrameRate"]), 2)
    except (TypeError, ValueError):
        fps = 0.0
    duration = 0.0
    try:
        gen = next((t for t in tracks if t.get("@type") == "General"), None)
        if gen and gen.get("Duration"):
            duration = float(gen["Duration"])
    except (TypeError, ValueError):
        duration = 0.0
    return {
        "width": width, "height": height, "bitrate": bitrate,
        "codec": (video.get("Format") or "").lower(),
        "fps": fps, "duration": duration,
        "label": quality_label_from_height(height),
        "standard": standard_name_from_height(height),
    }


def probe_video_path(p: Path):
    try:
        mtime = p.stat().st_mtime
    except OSError:
        return None
    return probe_video(str(p), mtime)


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


def human_size(num: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.1f} {unit}" if unit != "B" else f"{num} B"
        num /= 1024
    return f"{num:.1f} PB"


def safe_path(rel: str) -> Path:
    """Resolve `rel` under SHARE_DIR, refusing path-traversal."""
    root = _require_share_dir()
    target = (root / rel).resolve()
    if root not in target.parents and target != root:
        abort(403)
    return target


FAVICON_SVG = (
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Cpath d='M4 8a2 2 0 0 1 2-2h6.5l2.2 2.5H26a2 2 0 0 1 2 2V23a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z' "
    "fill='%23fbbf24'/%3E"
    "%3Cpath d='M4 10h24' stroke='%23f59e0b' stroke-width='1.2'/%3E"
    "%3C/svg%3E"
)


# ============================================================
# Web UI template
# ============================================================
TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#000000">
<title>LANShare</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,__FAVICON__">
<link rel="apple-touch-icon" href="data:image/svg+xml,__FAVICON__">
<script>
  (function(){
    try {
      var KEY = 'lanshare_theme';
      var saved = localStorage.getItem(KEY);
      var theme;
      if (saved === 'dark' || saved === 'light') {
        theme = saved;
      } else {
        var mq = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)');
        theme = (mq && mq.matches) ? 'light' : 'dark';
        localStorage.setItem(KEY, theme);
      }
      document.documentElement.setAttribute('data-theme', theme);
    } catch(e) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  })();
</script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root, [data-theme="dark"] {
    --bg: #000000;
    --bg-grad: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(255,255,255,0.04), transparent 70%);
    --card: #0a0a0a;
    --card-hover: #111111;
    --border: #1a1a1a;
    --border-hover: #2a2a2a;
    --text: #f5f5f7;
    --text-dim: #d4d4d8;
    --muted: #6b6b75;
    --muted-2: #4a4a52;
    --chip: #080808;
    --btn-bg: #0a0a0a;
    --menu-bg: rgba(10,10,10,0.95);
    --overlay: rgba(0,0,0,0.96);
    --topbar-bg: rgba(0,0,0,0.5);
    --green: #34d399;
    --purple-badge-bg: rgba(167,139,250,0.14);
    --purple-badge-fg: #c4b5fd;
    --scroll-thumb: #2a2a2e;
    --scroll-thumb-hover: #3a3a40;
    --scroll-track: transparent;
    --gap-xs: 0.375rem;
    --gap-sm: 0.625rem;
    --gap-md: 1rem;
    --gap-lg: 1.5rem;
    --gap-xl: 2.25rem;
    --page-x: 1.5rem;
    --page-y: 3rem;
    --radius: 12px;
    --radius-sm: 10px;
  }
  [data-theme="light"] {
    --bg: #ffffff;
    --bg-grad: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(0,0,0,0.035), transparent 70%);
    --card: #fafafa;
    --card-hover: #f1f1f3;
    --border: #e6e6ea;
    --border-hover: #d4d4d8;
    --text: #18181b;
    --text-dim: #3f3f46;
    --muted: #71717a;
    --muted-2: #a1a1aa;
    --chip: #f4f4f5;
    --btn-bg: #fafafa;
    --menu-bg: rgba(255,255,255,0.97);
    --overlay: rgba(255,255,255,0.97);
    --topbar-bg: rgba(255,255,255,0.7);
    --green: #10b981;
    --purple-badge-bg: rgba(139,92,246,0.12);
    --purple-badge-fg: #6d28d9;
    --scroll-thumb: #d4d4d8;
    --scroll-thumb-hover: #a1a1aa;
    --scroll-track: transparent;
  }

  html, body { background: var(--bg); }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    color: var(--text);
    min-height: 100vh;
    padding: var(--page-y) var(--page-x);
    background: var(--bg);
    background-image: var(--bg-grad);
    -webkit-font-smoothing: antialiased;
    transition: background-color 0.25s, color 0.25s;
  }
  .container { max-width: 1000px; margin: 0 auto; }

  @media (min-width: 900px) {
    html, body, * {
      scrollbar-width: thin;
      scrollbar-color: var(--scroll-thumb) var(--scroll-track);
    }
    ::-webkit-scrollbar { width: 12px; height: 12px; }
    ::-webkit-scrollbar-track { background: var(--scroll-track); border-radius: 999px; }
    ::-webkit-scrollbar-thumb {
      background: var(--scroll-thumb);
      border-radius: 999px;
      border: 3px solid var(--bg);
      background-clip: padding-box;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--scroll-thumb-hover);
      background-clip: padding-box;
      border: 3px solid var(--bg);
    }
    ::-webkit-scrollbar-thumb:active {
      background: var(--text-dim);
      background-clip: padding-box;
      border: 3px solid var(--bg);
    }
    ::-webkit-scrollbar-corner { background: transparent; }
  }
  @media (max-width: 899px) {
    ::-webkit-scrollbar { width: 0; height: 0; }
    * { scrollbar-width: none; }
  }

  header { margin-bottom: var(--gap-xl); }
  h1 {
    font-size: 1.5rem; font-weight: 600;
    letter-spacing: -0.02em;
    display: flex; align-items: center;
    gap: var(--gap-sm); flex-wrap: wrap;
    color: var(--text); line-height: 1.2;
  }
  h1 .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 10px var(--green); flex-shrink: 0;
  }
  h1 .badge {
    font-size: 0.72rem; font-weight: 500;
    background: var(--chip); color: var(--muted);
    padding: 0.35rem 0.75rem;
    border-radius: 999px; border: 1px solid var(--border);
    letter-spacing: 0; line-height: 1;
    display: inline-flex; align-items: center;
    margin-left: var(--gap-xs); white-space: nowrap;
  }
  .subtitle {
    color: var(--muted); font-size: 0.85rem;
    margin-top: var(--gap-md);
    display: flex; align-items: center;
    gap: var(--gap-sm); flex-wrap: wrap;
  }
  .path-chip {
    background: var(--chip); border: 1px solid var(--border);
    padding: 0.3rem 0.7rem; border-radius: 6px;
    font-family: ui-monospace, 'SF Mono', Menlo, monospace;
    font-size: 0.78rem; color: var(--text-dim);
    word-break: break-all; line-height: 1.4;
  }

  .toolbar {
    display: flex; gap: var(--gap-sm);
    margin-bottom: var(--gap-lg);
    flex-wrap: wrap; align-items: stretch;
  }
  .toolbar input {
    flex: 1; min-width: 200px;
    background: var(--chip); border: 1px solid var(--border);
    color: var(--text); padding: 0 1rem;
    height: 44px; border-radius: var(--radius-sm);
    font-size: 0.9rem; outline: none;
    transition: border-color 0.2s, background 0.2s;
  }
  .toolbar input::placeholder { color: var(--muted-2); }
  .toolbar input:focus { border-color: var(--border-hover); }
  .stat {
    background: var(--chip); border: 1px solid var(--border);
    padding: 0 1rem; height: 44px;
    border-radius: var(--radius-sm);
    font-size: 0.82rem; color: var(--muted);
    white-space: nowrap; display: flex; align-items: center;
  }
  .stat b { color: var(--text-dim); font-weight: 500; margin-left: 0.4rem; }

  .view-toggle, .theme-toggle, .hidden-toggle {
    display: flex; background: var(--chip);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 3px; gap: 2px; height: 44px; align-items: center;
  }
  .view-toggle button, .theme-toggle button, .hidden-toggle button {
    background: transparent; border: none;
    color: var(--muted); width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 7px; cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }
  .view-toggle button:hover, .theme-toggle button:hover, .hidden-toggle button:hover { color: var(--text-dim); }
  .view-toggle button.active, .theme-toggle button.active, .hidden-toggle button.active {
    background: var(--card-hover); color: var(--text);
    box-shadow: inset 0 0 0 1px var(--border);
  }
  .view-toggle button svg, .theme-toggle button svg, .hidden-toggle button svg {
    width: 18px; height: 18px;
    stroke: currentColor; stroke-width: 1.7;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }

  ul.files { list-style: none; display: flex; flex-direction: column; gap: var(--gap-xs); }
  ul.files li a {
    display: flex; align-items: center;
    gap: var(--gap-md); padding: 0.85rem 1rem;
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); text-decoration: none;
    color: var(--text); cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.15s;
  }
  ul.files li a:hover {
    background: var(--card-hover);
    border-color: var(--border-hover);
    transform: translateX(2px);
  }
  .icon {
    width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center;
    border-radius: var(--radius-sm); flex-shrink: 0;
    background: var(--chip); border: 1px solid var(--border);
    transition: border-color 0.15s;
  }
  ul.files li a:hover .icon { border-color: var(--border-hover); }
  .icon svg {
    width: 20px; height: 20px;
    stroke: currentColor; stroke-width: 1.6;
    stroke-linecap: round; stroke-linejoin: round; fill: none;
  }
  .info { flex: 1; min-width: 0; }
  .name {
    font-weight: 500; font-size: 0.92rem;
    white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; color: var(--text);
    letter-spacing: -0.01em;
  }
  .meta {
    color: var(--muted); font-size: 0.75rem;
    margin-top: 0.3rem; display: flex;
    gap: 0.85rem; flex-wrap: wrap;
    font-variant-numeric: tabular-nums;
  }
  .meta span::before {
    content: ''; display: inline-block;
    width: 3px; height: 3px; border-radius: 50%;
    background: var(--muted-2); margin-right: 0.5rem;
    vertical-align: middle;
  }
  .meta span:first-child::before { display: none; }
  .quality-badge {
    display: inline-flex; align-items: center;
    padding: 0.1rem 0.45rem;
    border-radius: 5px;
    background: var(--purple-badge-bg);
    color: var(--purple-badge-fg);
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  .meta .quality-badge::before { display: none; }

  .arrow {
    color: var(--muted-2); display: flex; align-items: center;
    transition: color 0.15s, transform 0.15s; flex-shrink: 0;
  }
  .arrow svg { width: 16px; height: 16px; stroke: currentColor; stroke-width: 1.8; fill: none; stroke-linecap: round; stroke-linejoin: round; }
  ul.files li a:hover .arrow { color: var(--text-dim); transform: translateX(3px); }
  ul.files li a:hover .arrow svg.dl { transform: translateY(2px); }
  .arrow svg.dl { transition: transform 0.15s; }

  body.view-grid ul.files {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--gap-sm);
  }
  body.view-grid ul.files li a {
    flex-direction: column; align-items: flex-start;
    padding: 1rem; gap: var(--gap-sm);
    height: 100%; transform: none; min-height: 150px;
  }
  body.view-grid ul.files li a:hover { transform: translateY(-2px); }
  body.view-grid .icon { width: 46px; height: 46px; border-radius: var(--radius); }
  body.view-grid .icon svg { width: 24px; height: 24px; }
  body.view-grid .info {
    width: 100%; display: flex; flex-direction: column;
    gap: 0.35rem; margin-top: auto;
  }
  body.view-grid .name {
    white-space: normal; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.35; word-break: break-word;
  }
  body.view-grid .meta {
    margin-top: 0; flex-direction: column;
    gap: 0.2rem; font-size: 0.72rem;
  }
  body.view-grid .meta span::before { display: none; }
  body.view-grid .arrow { display: none; }

  @media (max-width: 640px) {
    body { padding: 2rem 1rem; }
    h1 { font-size: 1.25rem; }
    .stat { display: none; }
    body.view-grid ul.files {
      display: flex; flex-direction: column; gap: var(--gap-xs);
    }
    body.view-grid ul.files li a {
      flex-direction: row; align-items: center;
      padding: 0.85rem 1rem; min-height: auto;
      gap: var(--gap-md); transform: none;
    }
    body.view-grid .icon { width: 38px; height: 38px; border-radius: var(--radius-sm); }
    body.view-grid .icon svg { width: 20px; height: 20px; }
    body.view-grid .info { width: auto; flex: 1; margin-top: 0; gap: 0; }
    body.view-grid .name { white-space: nowrap; display: block; -webkit-line-clamp: unset; }
    body.view-grid .meta {
      flex-direction: row; gap: 0.85rem;
      margin-top: 0.3rem; font-size: 0.75rem;
    }
    body.view-grid .meta span::before { display: inline-block; }
    body.view-grid .meta span:first-child::before { display: none; }
    body.view-grid .arrow { display: flex; }
    .view-toggle { display: none; }
  }

  .empty {
    text-align: center; padding: 4rem 1rem;
    color: var(--muted); grid-column: 1 / -1;
  }
  .empty .big {
    width: 64px; height: 64px;
    margin: 0 auto var(--gap-md); opacity: 0.35;
  }
  .empty .big svg { width: 100%; height: 100%; stroke: currentColor; stroke-width: 1.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }

  footer {
    margin-top: var(--gap-xl);
    padding-top: var(--gap-lg);
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--muted-2); font-size: 0.75rem;
    letter-spacing: 0.02em;
    display: flex; align-items: center;
    justify-content: center; gap: 0.5rem; line-height: 1;
  }
  footer .pulse {
    display: inline-block;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 8px var(--green);
    animation: pulse 2s ease-in-out infinite; flex-shrink: 0;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .fs-fab {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    width: 48px; height: 48px;
    border-radius: 50%;
    background: var(--card);
    color: var(--text);
    border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    z-index: 900;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    transition: transform 0.15s, background 0.15s, opacity 0.2s;
  }
  .fs-fab:hover { transform: scale(1.06); background: var(--card-hover); }
  .fs-fab:active { transform: scale(0.96); }
  .fs-fab svg {
    width: 22px; height: 22px;
    stroke: currentColor; stroke-width: 1.8;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }
  .fs-fab.hidden { opacity: 0; pointer-events: none; }

  .viewer {
    position: fixed; inset: 0;
    background: var(--overlay);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    z-index: 1000; display: none; flex-direction: column;
    opacity: 0; transition: opacity 0.2s ease;
  }
  .viewer.open { display: flex; opacity: 1; }

  .viewer-top {
    display: flex; align-items: center;
    gap: var(--gap-md); padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
    background: var(--topbar-bg); z-index: 3;
    transition: opacity 0.25s ease, transform 0.25s ease, padding 0.25s ease, border-color 0.25s ease;
  }

  .viewer.video-fullscreen .viewer-top {
    opacity: 0;
    transform: translateY(-8px);
    padding-top: 0; padding-bottom: 0;
    border-color: transparent;
    pointer-events: none;
    height: 0;
    overflow: hidden;
  }

  .viewer-title {
    flex: 1; min-width: 0; color: var(--text);
    font-size: 0.9rem; font-weight: 500;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .viewer-meta {
    color: var(--muted); font-size: 0.75rem;
    white-space: nowrap; font-variant-numeric: tabular-nums;
  }
  .viewer-btn {
    width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px; color: var(--text-dim);
    background: var(--btn-bg); border: 1px solid var(--border);
    cursor: pointer; text-decoration: none;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    flex-shrink: 0;
  }
  .viewer-btn:hover { color: var(--text); border-color: var(--border-hover); }
  .viewer-btn svg {
    width: 18px; height: 18px;
    stroke: currentColor; stroke-width: 1.7;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }

  .viewer-body {
    flex: 1; position: relative;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; padding: 1.5rem;
  }
  .viewer-content {
    max-width: 100%; max-height: 100%;
    display: flex; align-items: center; justify-content: center;
    width: 100%; height: 100%;
  }
  .viewer-content img {
    max-width: 100%; max-height: 100%;
    object-fit: contain; border-radius: 8px; user-select: none;
  }
  .viewer-content iframe {
    width: 100%; height: 100%;
    border: none; border-radius: 8px;
    background: var(--card);
  }
  .viewer-content pre {
    width: 100%; height: 100%; overflow: auto;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem;
    color: var(--text-dim);
    font-family: ui-monospace, 'SF Mono', Menlo, monospace;
    font-size: 0.82rem; line-height: 1.6;
    white-space: pre-wrap; word-break: break-word;
  }

  .video-wrap {
    position: relative; width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    background: #000; border-radius: 10px; overflow: hidden;
  }
  .video-wrap video {
    width: 100%; height: 100%; max-height: 100%;
    object-fit: contain; background: #000; display: block;
  }

  .v-ctrl {
    position: absolute; left: 0; right: 0; bottom: 0;
    padding: 3rem 1rem 0.9rem;
    background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0.5) 60%, transparent);
    display: flex; flex-direction: column; gap: 0.5rem;
    opacity: 1;
    transform: translateY(0);
    transition: opacity 0.35s ease, transform 0.35s ease;
    pointer-events: auto;
    color: #fff;
  }
  .video-wrap.idle .v-ctrl {
    opacity: 0;
    transform: translateY(12px);
    pointer-events: none;
  }
  .video-wrap.hide-cursor { cursor: none; }

  .v-progress {
    position: relative; height: 14px;
    cursor: pointer; display: flex; align-items: center;
  }
  .v-progress-track {
    position: relative; width: 100%; height: 4px;
    background: rgba(255,255,255,0.15);
    border-radius: 999px; overflow: hidden;
    transition: height 0.15s;
  }
  .v-progress:hover .v-progress-track { height: 6px; }
  .v-buffered {
    position: absolute; top: 0; left: 0; bottom: 0;
    background: rgba(255,255,255,0.2); width: 0%;
    transition: width 0.2s;
  }
  .v-played {
    position: absolute; top: 0; left: 0; bottom: 0;
    background: #fff; width: 0%; border-radius: 999px;
  }
  .v-thumb {
    position: absolute; top: 50%;
    width: 12px; height: 12px; background: #fff;
    border-radius: 50%;
    transform: translate(-50%, -50%) scale(0);
    transition: transform 0.15s;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.15);
    pointer-events: none;
  }
  .v-progress:hover .v-thumb { transform: translate(-50%, -50%) scale(1); }

  .v-row {
    display: flex; align-items: center;
    gap: 0.4rem; color: #fff;
    flex-wrap: nowrap;
  }
  .v-row button {
    background: transparent; border: none;
    color: #fff; width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px; cursor: pointer;
    transition: background 0.15s, transform 0.1s;
    flex-shrink: 0;
  }
  .v-row button:hover { background: rgba(255,255,255,0.1); }
  .v-row button:active { transform: scale(0.92); }
  .v-row button svg {
    width: 20px; height: 20px;
    stroke: currentColor; stroke-width: 1.7;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }
  .v-time {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.85);
    font-variant-numeric: tabular-nums;
    padding: 0 0.4rem;
    user-select: none;
    white-space: nowrap;
  }
  .v-spacer { flex: 1; }

  .v-volume { display: flex; align-items: center; gap: 0.4rem; }
  .v-volume-slider {
    width: 0; overflow: hidden;
    transition: width 0.2s;
    display: flex; align-items: center;
  }
  .v-volume:hover .v-volume-slider,
  .v-volume-slider.active { width: 80px; }
  .v-volume-slider input {
    width: 80px;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    background: rgba(255,255,255,0.2);
    border-radius: 999px;
    outline: none; cursor: pointer;
  }
  .v-volume-slider input::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px; height: 12px;
    background: #fff; border-radius: 50%; cursor: pointer;
  }
  .v-volume-slider input::-moz-range-thumb {
    width: 12px; height: 12px;
    background: #fff; border-radius: 50%;
    border: none; cursor: pointer;
  }

  .v-bigplay {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 96px;
    height: 96px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.15);
    border: 2.5px solid rgba(255, 255, 255, 0.95);
    color: #ffffff;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 0;
    cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    z-index: 2;
    box-shadow: none;
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
  }
  .v-bigplay.show { display: flex; }
  .v-bigplay:hover {
    transform: translate(-50%, -50%) scale(1.06);
    border-color: #ffffff;
    background: rgba(0, 0, 0, 0.28);
  }
  .v-bigplay:active {
    transform: translate(-50%, -50%) scale(0.97);
  }
  .v-bigplay svg {
    width: 38px;
    height: 38px;
    display: block;
    fill: none;
    stroke: #ffffff;
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
    margin-left: 3px;
  }
  .video-wrap.idle .v-bigplay.show {
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.4s ease;
  }

  .v-loading {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 40px; height: 40px;
    border: 3px solid rgba(255,255,255,0.15);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: none; z-index: 2;
  }
  .v-loading.show { display: block; }
  @keyframes spin { to { transform: translate(-50%,-50%) rotate(360deg); } }

  .v-menu {
    position: absolute;
    bottom: 60px; right: 1rem;
    background: var(--menu-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 6px;
    display: none; flex-direction: column;
    gap: 2px; z-index: 5; min-width: 90px;
    max-height: 60%;
    overflow-y: auto;
    transition: opacity 0.25s;
  }
  .video-wrap.idle .v-menu { opacity: 0; pointer-events: none; }
  .v-menu.show { display: flex; }
  .v-menu button {
    background: transparent; border: none;
    color: var(--text-dim);
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.82rem;
    transition: background 0.15s, color 0.15s;
    white-space: nowrap;
  }
  .v-menu button:hover { background: var(--card-hover); color: var(--text); }
  .v-menu button.active { color: var(--text); font-weight: 500; }

  .v-quality {
    width: auto !important;
    padding: 0 0.6rem !important;
    gap: 0.4rem;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.01em;
    cursor: default !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    pointer-events: none;
    transition: none !important;
    display: inline-flex;
    align-items: center;
    color: #fff;
  }
  .v-quality:hover,
  .v-quality:active,
  .v-quality:focus {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transform: none !important;
    outline: none !important;
  }
  .v-quality:active { transform: none !important; }

  .v-quality::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0;
    left: -40%;
    width: 40%;
    background: linear-gradient(
      90deg,
      rgba(255,255,255,0) 0%,
      rgba(255,255,255,0.18) 50%,
      rgba(255,255,255,0) 100%
    );
    filter: blur(6px);
    animation: qshine 3.2s ease-in-out infinite;
    pointer-events: none;
    border-radius: inherit;
  }

  @keyframes qshine {
    0%   { left: -40%; }
    60%  { left: 100%; }
    100% { left: 100%; }
  }

  .v-quality .v-quality-label {
    min-width: 2.6rem;
    text-align: left;
    white-space: nowrap;
    position: relative;
    z-index: 1;
  }
  .v-quality .v-quality-tag {
    display: inline-block;
    padding: 0.05rem 0.35rem;
    border-radius: 4px;
    background: var(--purple-badge-bg);
    color: var(--purple-badge-fg);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    position: relative;
    z-index: 1;
  }

  .audio-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    width: min(100%, 520px);
    display: flex; flex-direction: column; gap: 1.25rem;
  }
  .audio-head { display: flex; align-items: center; gap: 1rem; }
  .audio-head .a-icon {
    width: 56px; height: 56px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: var(--chip); border: 1px solid var(--border);
    color: #f472b6; flex-shrink: 0;
  }
  .audio-head .a-icon svg { width: 26px; height: 26px; stroke: currentColor; stroke-width: 1.6; fill: none; stroke-linecap: round; stroke-linejoin: round; }
  .audio-head .a-name {
    font-size: 0.95rem; font-weight: 500;
    word-break: break-word; line-height: 1.35;
    color: var(--text);
  }
  .audio-card .v-ctrl {
    background: none;
    padding: 0;
    transform: none;
    color: var(--text);
  }
  .audio-card .v-row { color: var(--text); }
  .audio-card .v-row button { color: var(--text); }
  .audio-card .v-row button:hover { background: var(--card-hover); }
  .audio-card .v-time { color: var(--muted); }
  .audio-card .v-progress-track { background: var(--border-hover); }
  .audio-card .v-played { background: var(--text); }
  .audio-card .v-thumb { background: var(--text); box-shadow: 0 0 0 4px var(--purple-badge-bg); }
  .audio-card .v-volume-slider input { background: var(--border-hover); }
  .audio-card .v-volume-slider input::-webkit-slider-thumb { background: var(--text); }
  .audio-card .v-volume-slider input::-moz-range-thumb { background: var(--text); }

  .video-wrap:fullscreen,
  .video-wrap:-webkit-full-screen {
    border-radius: 0;
    width: 100vw; height: 100vh;
  }

  @media (max-width: 640px) and (orientation: portrait) {
    .v-hide-mobile { display: none !important; }
    .v-row { gap: 0.2rem; }
    .v-row button { width: 34px; height: 34px; }
    .v-row button svg { width: 19px; height: 19px; }
    .v-time { font-size: 0.72rem; padding: 0 0.25rem; }
    .v-ctrl { padding: 2rem 0.75rem 0.75rem; }
    .v-quality { padding: 0 0.45rem !important; font-size: 0.72rem; }
    .v-quality .v-quality-label { min-width: 2rem; }
    .v-bigplay { width: 78px; height: 78px; border-width: 2px; }
    .v-bigplay svg { width: 32px; height: 32px; margin-left: 2px; }
    .v-menu { bottom: 54px; right: 0.5rem; }
  }
  @media (max-width: 380px) and (orientation: portrait) {
    .v-hide-narrow { display: none !important; }
  }

  .splash {
    position: fixed;
    inset: 0;
    background: var(--bg);
    background-image: var(--bg-grad);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    opacity: 1;
    transition: opacity 0.55s ease;
    pointer-events: all;
  }
  .splash.hidden {
    opacity: 0;
    pointer-events: none;
  }
  .splash-icon {
    width: 88px;
    height: 88px;
    border-radius: 22px;
    background: var(--chip);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    animation: splash-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  [data-theme="light"] .splash-icon {
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  }
  .splash-icon svg {
    width: 46px;
    height: 46px;
  }
  .splash-title {
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--text);
    animation: splash-fade-up 0.7s ease 0.15s backwards;
  }
  .splash-sub {
    font-size: 0.78rem;
    color: var(--muted);
    letter-spacing: 0.02em;
    animation: splash-fade-up 0.7s ease 0.25s backwards;
  }
  .splash-bar {
    width: 140px;
    height: 3px;
    border-radius: 999px;
    background: var(--border);
    overflow: hidden;
    position: relative;
    margin-top: 0.25rem;
    animation: splash-fade-up 0.7s ease 0.35s backwards;
  }
  .splash-bar::after {
    content: '';
    position: absolute;
    top: 0; left: -40%;
    width: 40%;
    height: 100%;
    border-radius: 999px;
    background: var(--text);
    opacity: 0.75;
    animation: splash-slide 1.4s ease-in-out infinite;
  }
  @keyframes splash-pop {
    0%   { transform: scale(0.85); opacity: 0; }
    100% { transform: scale(1);    opacity: 1; }
  }
  @keyframes splash-fade-up {
    0%   { transform: translateY(6px); opacity: 0; }
    100% { transform: translateY(0);   opacity: 1; }
  }
  @keyframes splash-slide {
    0%   { left: -40%; }
    100% { left: 100%; }
  }
</style>
</head>
<body class="view-grid">

<div class="splash" id="splash">
  <div class="splash-icon">
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 8a2 2 0 0 1 2-2h6.5l2.2 2.5H26a2 2 0 0 1 2 2V23a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z"
            fill="#fbbf24"/>
      <path d="M4 10h24" stroke="#f59e0b" stroke-width="1.2"/>
    </svg>
  </div>
  <div class="splash-title">LANShare</div>
  <div class="splash-sub">Loading your library…</div>
  <div class="splash-bar"></div>
</div>

<button class="fs-fab" id="fsFab" title="Fullscreen" aria-label="Toggle fullscreen">
  <svg viewBox="0 0 24 24">
    <path d="M8 3H5a2 2 0 0 0-2 2v3"/>
    <path d="M16 3h3a2 2 0 0 1 2 2v3"/>
    <path d="M8 21H5a2 2 0 0 1-2-2v-3"/>
    <path d="M16 21h3a2 2 0 0 0 2-2v-3"/>
  </svg>
</button>

<div class="container">
  <header>
    <h1>
      <span class="dot"></span>
      <span class="title">LANShare</span>
      <span class="badge">{{ count }} items</span>
    </h1>
    <div class="subtitle">
      <span>Path</span>
      <span class="path-chip">{{ display_path }}</span>
    </div>
  </header>

  <div class="toolbar">
    <input type="text" id="search" placeholder="Search files..." autocomplete="off">
    <div class="stat">Total <b>{{ total_size }}</b></div>
    <div class="view-toggle" role="group" aria-label="View mode">
      <button type="button" data-view="grid" title="Grid view" aria-label="Grid view">
        <svg viewBox="0 0 24 24">{{ icons.grid[0]|safe }}</svg>
      </button>
      <button type="button" data-view="list" title="List view" aria-label="List view">
        <svg viewBox="0 0 24 24">{{ icons.list[0]|safe }}</svg>
      </button>
    </div>
    <div class="hidden-toggle" role="group" aria-label="Hidden files">
      <button type="button" id="hiddenBtn" title="Show hidden files" aria-label="Toggle hidden files">
        <svg viewBox="0 0 24 24"></svg>
      </button>
    </div>
    <div class="theme-toggle" role="group" aria-label="Theme">
      <button type="button" data-theme-value="dark" title="Dark theme" aria-label="Dark theme">
        <svg viewBox="0 0 24 24">{{ icons.moon[0]|safe }}</svg>
      </button>
      <button type="button" data-theme-value="light" title="Light theme" aria-label="Light theme">
        <svg viewBox="0 0 24 24">{{ icons.sun[0]|safe }}</svg>
      </button>
    </div>
  </div>

  <ul class="files" id="fileList">
    {% if parent is not none %}
    <li data-name="__parent__">
      <a href="{{ url_for('browse', subpath=parent) }}" class="nav-link">
        <div class="icon" style="color: {{ icons.up[1] }};">
          <svg viewBox="0 0 24 24">{{ icons.up[0]|safe }}</svg>
        </div>
        <div class="info"><div class="name">Back to parent folder</div></div>
      </a>
    </li>
    {% endif %}

    {% for item in items %}
    <li data-name="{{ item.name|lower }}">
      {% if item.is_dir %}
      <a href="{{ item.url }}" class="nav-link">
        <div class="icon" style="color: {{ item.color }};"><svg viewBox="0 0 24 24">{{ item.svg|safe }}</svg></div>
        <div class="info">
          <div class="name">{{ item.name }}/</div>
          <div class="meta"><span>{{ item.mtime }}</span></div>
        </div>
        <div class="arrow"><svg viewBox="0 0 24 24">{{ icons.right[0]|safe }}</svg></div>
      </a>
      {% else %}
      <a href="{{ item.url }}"
         class="file-row"
         data-url="{{ item.url }}"
         data-name="{{ item.name }}"
         data-kind="{{ item.kind or '' }}"
         data-size="{{ item.size }}"
         data-quality="{{ item.quality or '' }}"
         data-quality-tag="{{ item.quality_tag or '' }}"
         {% if not item.kind %}download{% endif %}>
        <div class="icon" style="color: {{ item.color }};"><svg viewBox="0 0 24 24">{{ item.svg|safe }}</svg></div>
        <div class="info">
          <div class="name">{{ item.name }}</div>
          <div class="meta">
            <span>{{ item.size }}</span>
            <span>{{ item.mtime }}</span>
            {% if item.quality %}<span class="quality-badge">{{ item.quality }}{% if item.quality_tag %} · {{ item.quality_tag }}{% endif %}</span>{% endif %}
          </div>
        </div>
        <div class="arrow">
          {% if item.kind %}
          <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
          {% else %}
          <svg class="dl" viewBox="0 0 24 24">{{ icons.down[0]|safe }}</svg>
          {% endif %}
        </div>
      </a>
      {% endif %}
    </li>
    {% endfor %}
  </ul>

  {% if not items and parent is none %}
  <div class="empty">
    <div class="big">
      <svg viewBox="0 0 24 24">
        <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>
        <path d="M9 14l3 3 3-3"/>
      </svg>
    </div>
    <div>No files found in this directory</div>
  </div>
  {% endif %}

  <footer>
    <span>Local server</span>
    <span class="pulse"></span>
    <span>port {{ port }}</span>
  </footer>
</div>

<div class="viewer" id="viewer">
  <div class="viewer-top">
    <div class="viewer-title" id="vTitle"></div>
    <div class="viewer-meta" id="vMeta"></div>
    <a class="viewer-btn" id="vDownload" href="#" download title="Download">
      <svg viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/></svg>
    </a>
    <button class="viewer-btn" id="vClose" title="Close (Esc)">
      <svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div class="viewer-body">
    <div class="viewer-content" id="vContent"></div>
  </div>
</div>

<script>
  (function(){
    const splash = document.getElementById('splash');
    if (!splash) return;
    const MIN_SHOW_MS = 1400;
    const startTime = performance.now();
    let hidden = false;
    function hideSplash(){
      if (hidden) return;
      hidden = true;
      const elapsed = performance.now() - startTime;
      const remaining = Math.max(0, MIN_SHOW_MS - elapsed);
      setTimeout(() => {
        splash.classList.add('hidden');
        setTimeout(() => { try { splash.remove(); } catch(e){} }, 700);
      }, remaining);
    }
    if (document.readyState === 'complete') hideSplash();
    else {
      window.addEventListener('load', hideSplash);
      setTimeout(hideSplash, 3500);
    }
  })();

  const THEME_KEY = 'lanshare_theme';
  const themeButtons = document.querySelectorAll('.theme-toggle button');
  function getSavedTheme(){
    try {
      const v = localStorage.getItem(THEME_KEY);
      return (v === 'dark' || v === 'light') ? v : 'dark';
    } catch { return 'dark'; }
  }
  function applyTheme(theme){
    document.documentElement.setAttribute('data-theme', theme);
    themeButtons.forEach(b => {
      b.classList.toggle('active', b.dataset.themeValue === theme);
    });
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) metaThemeColor.setAttribute('content', theme === 'light' ? '#ffffff' : '#000000');
  }
  themeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.dataset.themeValue;
      try { localStorage.setItem(THEME_KEY, theme); } catch {}
      applyTheme(theme);
    });
  });
  applyTheme(getSavedTheme());

  const HIDDEN_KEY = 'lanshare_hidden';
  const hiddenBtn = document.getElementById('hiddenBtn');
  const EYE_OPEN = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  const EYE_CLOSED = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
  function isHiddenEnabled(){
    try { return localStorage.getItem(HIDDEN_KEY) === '1'; } catch { return false; }
  }
  function setHiddenEnabled(v){
    try { localStorage.setItem(HIDDEN_KEY, v ? '1' : '0'); } catch {}
  }
  function applyHiddenButton(){
    const on = isHiddenEnabled();
    hiddenBtn.classList.toggle('active', on);
    hiddenBtn.title = on ? 'Hide hidden files' : 'Show hidden files';
    hiddenBtn.querySelector('svg').innerHTML = on ? EYE_OPEN : EYE_CLOSED;
  }
  function withHiddenParam(url){
    try {
      const u = new URL(url, location.origin);
      if (isHiddenEnabled()) u.searchParams.set('hidden', '1');
      else u.searchParams.delete('hidden');
      const q = u.searchParams.toString();
      return u.pathname + (q ? '?' + q : '');
    } catch { return url; }
  }
  hiddenBtn.addEventListener('click', () => {
    setHiddenEnabled(!isHiddenEnabled());
    applyHiddenButton();
    navigateTo(location.pathname, false);
  });
  applyHiddenButton();

  const fsFab = document.getElementById('fsFab');
  function isFS(){
    return !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
  }
  function requestFS(el){
    const fn = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
    if (!fn) return;
    try {
      const p = fn.call(el, { navigationUI: 'hide' });
      if (p && p.catch) p.catch(() => {});
    } catch(e){}
  }
  function exitFS(){
    const fn = document.exitFullscreen || document.webkitExitFullscreen || document.msExitFullscreen;
    if (!fn) return;
    try { const p = fn.call(document); if (p && p.catch) p.catch(() => {}); } catch(e){}
  }
  function updateFab(){
    const fs = isFS();
    fsFab.querySelector('svg').innerHTML = fs
      ? '<path d="M9 3v6H3"/><path d="M15 21v-6h6"/><path d="M3 9l7-7"/><path d="M21 15l-7 7"/>'
      : '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>';
    fsFab.title = fs ? 'Exit fullscreen' : 'Fullscreen';
    fsFab.classList.toggle('hidden', document.getElementById('viewer').classList.contains('open'));
  }
  fsFab.addEventListener('click', () => {
    if (isFS()) exitFS();
    else requestFS(document.documentElement);
  });
  document.addEventListener('fullscreenchange', updateFab);
  document.addEventListener('webkitfullscreenchange', updateFab);
  updateFab();

  const STORAGE_KEY = 'lanshare_view';
  function applyView(view) {
    const isMobile = window.matchMedia('(max-width: 640px)').matches;
    const effective = isMobile ? 'list' : view;
    document.body.classList.remove('view-grid', 'view-list');
    document.body.classList.add('view-' + effective);
    document.querySelectorAll('.view-toggle button').forEach(b => {
      b.classList.toggle('active', b.dataset.view === effective);
    });
  }
  function getSavedView() {
    try { return localStorage.getItem(STORAGE_KEY) || 'grid'; } catch { return 'grid'; }
  }
  function bindViewToggle(){
    document.querySelectorAll('.view-toggle button').forEach(btn => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        try { localStorage.setItem(STORAGE_KEY, view); } catch {}
        applyView(view);
      });
    });
  }
  bindViewToggle();
  applyView(getSavedView());
  let rt;
  window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => applyView(getSavedView()), 100); });

  const viewer    = document.getElementById('viewer');
  const vTitle    = document.getElementById('vTitle');
  const vMeta     = document.getElementById('vMeta');
  const vContent  = document.getElementById('vContent');
  const vDownload = document.getElementById('vDownload');
  const vClose    = document.getElementById('vClose');

  function openViewer(data) {
    vTitle.textContent = data.name;
    vMeta.textContent = data.size || '';
    vDownload.href = data.url;
    vContent.innerHTML = '';
    const kind = data.kind;
    const src  = data.url;
    if (kind === 'image') {
      const img = document.createElement('img');
      img.src = src; img.alt = data.name;
      vContent.appendChild(img);
    } else if (kind === 'video') {
      vContent.appendChild(buildVideoPlayer(src, data.name, data.quality || '', data.qualityTag || ''));
    } else if (kind === 'audio') {
      vContent.appendChild(buildAudioPlayer(src, data.name));
    } else if (kind === 'pdf') {
      const iframe = document.createElement('iframe');
      iframe.src = src;
      vContent.appendChild(iframe);
    } else if (kind === 'text') {
      const pre = document.createElement('pre');
      pre.textContent = 'Loading...';
      vContent.appendChild(pre);
      fetch(src).then(r => r.text()).then(t => { pre.textContent = t; })
               .catch(() => { pre.textContent = 'Could not load file.'; });
    }
    viewer.classList.add('open');
    document.body.style.overflow = 'hidden';
    updateFab();
  }

  function closeViewer() {
    viewer.classList.remove('open');
    viewer.classList.remove('video-fullscreen');
    document.body.style.overflow = '';
    vContent.querySelectorAll('video, audio').forEach(m => { try { m.pause(); m.src=''; } catch(e){} });
    setTimeout(() => { vContent.innerHTML = ''; }, 200);
    updateFab();
  }

  vClose.addEventListener('click', closeViewer);
  viewer.addEventListener('click', (e) => {
    if (e.target === viewer || e.target.classList.contains('viewer-body')) closeViewer();
  });
  document.addEventListener('keydown', (e) => {
    if (!viewer.classList.contains('open')) return;
    if (e.key === 'Escape' && !isFS()) closeViewer();
  });

  let navInProgress = false;
  async function navigateTo(url, pushState = true) {
    if (navInProgress) return;
    navInProgress = true;
    const target = withHiddenParam(url);
    try {
      const res = await fetch(target, {
        headers: { 'X-Requested-With': 'spa-nav' },
        cache: 'no-store'
      });
      if (!res.ok) { window.location.href = target; return; }
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const newList = doc.getElementById('fileList');
      const oldList = document.getElementById('fileList');
      if (newList && oldList) oldList.replaceWith(newList);
      const newHeader = doc.querySelector('header');
      const oldHeader = document.querySelector('header');
      if (newHeader && oldHeader) oldHeader.replaceWith(newHeader);
      const newStat = doc.querySelector('.stat');
      const oldStat = document.querySelector('.stat');
      if (newStat && oldStat) oldStat.replaceWith(newStat);
      const newEmpty = doc.querySelector('.empty');
      const oldEmpty = document.querySelector('.empty');
      if (newEmpty && oldEmpty) oldEmpty.replaceWith(newEmpty);
      else if (newEmpty && !oldEmpty) {
        const listParent = document.getElementById('fileList')?.parentNode;
        if (listParent) listParent.appendChild(newEmpty);
      } else if (!newEmpty && oldEmpty) {
        oldEmpty.remove();
      }
      if (pushState) history.pushState({ url: target }, '', target);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      bindNavLinks();
      bindFileRows();
      rebindSearch();
      bindViewToggle();
    } catch (err) {
      window.location.href = target;
    } finally {
      navInProgress = false;
    }
  }

  function bindNavLinks() {
    document.querySelectorAll('a.nav-link').forEach(a => {
      if (a.dataset.navBound === '1') return;
      a.dataset.navBound = '1';
      a.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const href = a.getAttribute('href');
        if (!href) return;
        navigateTo(href);
      });
    });
  }

  function bindFileRows() {
    document.querySelectorAll('a.file-row').forEach(a => {
      if (a.dataset.bound === '1') return;
      a.dataset.bound = '1';
      if (!a.dataset.kind) return;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        if (!isFS()) requestFS(document.documentElement);
        openViewer({
          url:  a.dataset.url,
          name: a.dataset.name,
          kind: a.dataset.kind,
          size: a.dataset.size,
          quality: a.dataset.quality,
          qualityTag: a.dataset.qualityTag,
        });
      });
    });
  }

  function rebindSearch() {
    const s = document.getElementById('search');
    if (!s || s.dataset.bound === '1') return;
    s.dataset.bound = '1';
    s.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      document.querySelectorAll('#fileList li[data-name]').forEach(li => {
        if (li.dataset.name === '__parent__') return;
        li.style.display = li.dataset.name.includes(q) ? '' : 'none';
      });
    });
  }

  window.addEventListener('popstate', (e) => {
    if (e.state && e.state.url) navigateTo(e.state.url, false);
    else navigateTo(location.pathname + location.search, false);
  });

  if (!history.state) {
    history.replaceState(
      { url: location.pathname + location.search },
      '',
      location.href
    );
  }

  bindNavLinks();
  bindFileRows();
  rebindSearch();

  function buildVideoPlayer(src, name, quality, qualityTag) {
    const wrap = document.createElement('div');
    wrap.className = 'video-wrap';
    const labelText = quality || '—';
    const tagText = qualityTag || '';
    wrap.innerHTML = `
      <video playsinline preload="metadata" src="${src}"></video>
      <div class="v-loading"></div>
      <button class="v-bigplay show" aria-label="Play">
        <svg viewBox="0 0 24 24">
          <path d="M9 5.5v13l11-6.5z"/>
        </svg>
      </button>
      <div class="v-menu v-speed-menu">
        ${[0.5,0.75,1,1.25,1.5,2].map(s =>
          `<button data-speed="${s}" class="${s===1?'active':''}">${s}x</button>`).join('')}
      </div>
      <div class="v-ctrl">
        <div class="v-progress">
          <div class="v-progress-track">
            <div class="v-buffered"></div>
            <div class="v-played"></div>
          </div>
          <div class="v-thumb"></div>
        </div>
        <div class="v-row">
          <button class="v-play" title="Play / Pause (Space)">
            <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>
          <button class="v-skip v-back v-hide-narrow" title="Back 10s">
            <svg viewBox="0 0 24 24"><path d="M11 19l-9-7 9-7v14zM22 19l-9-7 9-7v14z"/></svg>
          </button>
          <button class="v-skip v-fwd v-hide-narrow" title="Forward 10s">
            <svg viewBox="0 0 24 24"><path d="M13 5l9 7-9 7V5zM2 5l9 7-9 7V5z"/></svg>
          </button>
          <span class="v-time" data-role="time">0:00 / 0:00</span>
          <div class="v-spacer"></div>
          <div class="v-volume">
            <button class="v-mute" title="Mute (M)">
              <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
            </button>
            <div class="v-volume-slider">
              <input type="range" min="0" max="1" step="0.01" value="1">
            </div>
          </div>
          <button class="v-quality v-hide-mobile" title="Quality" tabindex="-1" aria-disabled="true">
            <svg viewBox="0 0 24 24">
              <path d="M4 6h16M4 12h16M4 18h16"/>
              <circle cx="8" cy="6" r="2"/>
              <circle cx="16" cy="12" r="2"/>
              <circle cx="10" cy="18" r="2"/>
            </svg>
            <span class="v-quality-label">${labelText}</span>
            ${tagText ? `<span class="v-quality-tag">${tagText}</span>` : ''}
          </button>
          <button class="v-speed" title="Playback speed">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
          </button>
          <button class="v-pip v-hide-mobile" title="Picture in Picture">
            <svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><rect x="12" y="12" width="8" height="6" rx="1"/></svg>
          </button>
          <button class="v-full v-hide-mobile" title="Fullscreen (F)">
            <svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>
          </button>
        </div>
      </div>
    `;
    const video    = wrap.querySelector('video');
    const loading  = wrap.querySelector('.v-loading');
    const bigPlay  = wrap.querySelector('.v-bigplay');
    const played   = wrap.querySelector('.v-played');
    const buffered = wrap.querySelector('.v-buffered');
    const prog     = wrap.querySelector('.v-progress');
    const thumb    = wrap.querySelector('.v-thumb');
    const timeEl   = wrap.querySelector('[data-role=time]');
    const btnPlay  = wrap.querySelector('.v-play');
    const btnBack  = wrap.querySelector('.v-back');
    const btnFwd   = wrap.querySelector('.v-fwd');
    const btnMute  = wrap.querySelector('.v-mute');
    const volIn    = wrap.querySelector('.v-volume-slider input');
    const btnSpeed = wrap.querySelector('.v-speed');
    const menu     = wrap.querySelector('.v-speed-menu');
    const btnPip   = wrap.querySelector('.v-pip');
    const btnFull  = wrap.querySelector('.v-full');
    const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
    const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';
    function fmt(t){
      if (!isFinite(t)) return '0:00';
      const h = Math.floor(t/3600), m = Math.floor((t%3600)/60), s = Math.floor(t%60);
      return (h ? h+':'+String(m).padStart(2,'0') : m) + ':' + String(s).padStart(2,'0');
    }
    function updateTime(){ timeEl.textContent = fmt(video.currentTime) + ' / ' + fmt(video.duration); }
    function updateProgress(){
      const p = video.duration ? (video.currentTime / video.duration) * 100 : 0;
      played.style.width = p + '%';
      thumb.style.left = p + '%';
      if (video.buffered.length) {
        const b = video.buffered.end(video.buffered.length - 1);
        buffered.style.width = (b / video.duration) * 100 + '%';
      }
    }
    function playPause(){ video.paused ? video.play() : video.pause(); }
    video.addEventListener('play',  () => { btnPlay.innerHTML = ICON_PAUSE; bigPlay.classList.remove('show'); });
    video.addEventListener('pause', () => { btnPlay.innerHTML = ICON_PLAY;  bigPlay.classList.add('show'); });
    video.addEventListener('timeupdate', () => { updateTime(); updateProgress(); });
    video.addEventListener('progress', updateProgress);
    video.addEventListener('loadedmetadata', updateTime);
    video.addEventListener('waiting', () => loading.classList.add('show'));
    video.addEventListener('playing', () => loading.classList.remove('show'));
    video.addEventListener('canplay', () => loading.classList.remove('show'));
    bigPlay.addEventListener('click', playPause);
    btnPlay.addEventListener('click', playPause);
    video.addEventListener('click', (e) => { if (e.target === video) playPause(); });
    if (btnBack) btnBack.addEventListener('click', () => video.currentTime = Math.max(0, video.currentTime - 10));
    if (btnFwd)  btnFwd .addEventListener('click', () => video.currentTime = Math.min(video.duration || 0, video.currentTime + 10));
    function seekFromEvent(e){
      const rect = prog.getBoundingClientRect();
      const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
      const p = Math.max(0, Math.min(1, x / rect.width));
      if (video.duration) video.currentTime = p * video.duration;
    }
    let seeking = false;
    prog.addEventListener('mousedown', (e) => { seeking = true; seekFromEvent(e); });
    window.addEventListener('mousemove', (e) => { if (seeking) seekFromEvent(e); });
    window.addEventListener('mouseup', () => seeking = false);
    prog.addEventListener('touchstart', seekFromEvent, { passive: true });
    prog.addEventListener('touchmove', seekFromEvent, { passive: true });
    btnMute.addEventListener('click', () => {
      video.muted = !video.muted;
      volIn.value = video.muted ? 0 : video.volume;
      updateMuteIcon();
    });
    volIn.addEventListener('input', () => {
      video.volume = parseFloat(volIn.value);
      video.muted = video.volume === 0;
      updateMuteIcon();
    });
    function updateMuteIcon(){
      btnMute.innerHTML = (video.muted || video.volume === 0)
        ? '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M22 9l-6 6M16 9l6 6"/></svg>'
        : '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
    }
    btnSpeed.addEventListener('click', (e) => { e.stopPropagation(); menu.classList.toggle('show'); });
    menu.querySelectorAll('button').forEach(b => {
      b.addEventListener('click', () => {
        video.playbackRate = parseFloat(b.dataset.speed);
        menu.querySelectorAll('button').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        menu.classList.remove('show');
      });
    });
    let idleTimer = null;
    function wake(){
      wrap.classList.remove('idle');
      wrap.classList.remove('hide-cursor');
      clearTimeout(idleTimer);
      if (!video.paused) {
        idleTimer = setTimeout(() => {
          wrap.classList.add('idle');
          wrap.classList.add('hide-cursor');
          menu.classList.remove('show');
        }, 3000);
      }
    }
    wrap.addEventListener('mousemove', wake);
    wrap.addEventListener('mousedown', wake);
    wrap.addEventListener('touchstart', wake, { passive: true });
    wrap.addEventListener('touchmove', wake, { passive: true });
    video.addEventListener('play', wake);
    video.addEventListener('pause', () => {
      clearTimeout(idleTimer);
      wrap.classList.remove('idle');
      wrap.classList.remove('hide-cursor');
    });
    menu.addEventListener('mousemove', wake);
    document.addEventListener('click', () => menu.classList.remove('show'));
    wrap.addEventListener('click', (e) => e.stopPropagation());
    if (btnPip) btnPip.addEventListener('click', async () => {
      try {
        if (document.pictureInPictureElement) await document.exitPictureInPicture();
        else await video.requestPictureInPicture();
      } catch(e){}
    });
    if (btnFull) btnFull.addEventListener('click', () => {
      if (isFS()) exitFS();
      else requestFS(wrap);
    });
    wrap.tabIndex = 0;
    wrap.addEventListener('keydown', (e) => {
      wake();
      if (e.key === ' ' || e.key === 'k') { e.preventDefault(); playPause(); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); video.currentTime = Math.min(video.duration||0, video.currentTime+5); }
      else if (e.key === 'ArrowLeft')  { e.preventDefault(); video.currentTime = Math.max(0, video.currentTime-5); }
      else if (e.key === 'ArrowUp')    { e.preventDefault(); video.volume = Math.min(1, video.volume+0.05); volIn.value = video.volume; updateMuteIcon(); }
      else if (e.key === 'ArrowDown')  { e.preventDefault(); video.volume = Math.max(0, video.volume-0.05); volIn.value = video.volume; updateMuteIcon(); }
      else if (e.key === 'm') { video.muted = !video.muted; updateMuteIcon(); }
      else if (e.key === 'f') { if (isFS()) exitFS(); else requestFS(wrap); }
    });
    function syncViewerFullscreen(){
      viewer.classList.toggle('video-fullscreen', isFS());
    }
    document.addEventListener('fullscreenchange', syncViewerFullscreen);
    document.addEventListener('webkitfullscreenchange', syncViewerFullscreen);
    syncViewerFullscreen();
    updateMuteIcon();
    setTimeout(() => wrap.focus(), 100);
    wake();
    return wrap;
  }

  function buildAudioPlayer(src, name) {
    const card = document.createElement('div');
    card.className = 'audio-card';
    card.innerHTML = `
      <div class="audio-head">
        <div class="a-icon">
          <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
        </div>
        <div class="a-name">${name}</div>
      </div>
      <div class="video-wrap" style="height:auto; background:transparent; border-radius:0;">
        <audio src="${src}" preload="metadata" style="width:100%;"></audio>
        <div class="v-ctrl" style="position:static;">
          <div class="v-progress">
            <div class="v-progress-track">
              <div class="v-buffered"></div>
              <div class="v-played"></div>
            </div>
            <div class="v-thumb"></div>
          </div>
          <div class="v-row">
            <button class="v-play" title="Play / Pause">
              <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </button>
            <span class="v-time" data-role="time">0:00 / 0:00</span>
            <div class="v-spacer"></div>
            <div class="v-volume">
              <button class="v-mute" title="Mute">
                <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
              </button>
              <div class="v-volume-slider">
                <input type="range" min="0" max="1" step="0.01" value="1">
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    const audio   = card.querySelector('audio');
    const btnPlay = card.querySelector('.v-play');
    const played  = card.querySelector('.v-played');
    const prog    = card.querySelector('.v-progress');
    const thumb   = card.querySelector('.v-thumb');
    const timeEl  = card.querySelector('[data-role=time]');
    const btnMute = card.querySelector('.v-mute');
    const volIn   = card.querySelector('.v-volume-slider input');
    const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
    const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';
    function fmt(t){
      if (!isFinite(t)) return '0:00';
      const m = Math.floor(t/60), s = Math.floor(t%60);
      return m + ':' + String(s).padStart(2,'0');
    }
    function update(){
      timeEl.textContent = fmt(audio.currentTime) + ' / ' + fmt(audio.duration);
      const p = audio.duration ? (audio.currentTime/audio.duration)*100 : 0;
      played.style.width = p + '%';
      thumb.style.left = p + '%';
    }
    audio.addEventListener('timeupdate', update);
    audio.addEventListener('loadedmetadata', update);
    audio.addEventListener('play',  () => btnPlay.innerHTML = ICON_PAUSE);
    audio.addEventListener('pause', () => btnPlay.innerHTML = ICON_PLAY);
    btnPlay.addEventListener('click', () => audio.paused ? audio.play() : audio.pause());
    function seek(e){
      const rect = prog.getBoundingClientRect();
      const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
      const p = Math.max(0, Math.min(1, x/rect.width));
      if (audio.duration) audio.currentTime = p * audio.duration;
    }
    let s = false;
    prog.addEventListener('mousedown', (e) => { s = true; seek(e); });
    window.addEventListener('mousemove', (e) => { if (s) seek(e); });
    window.addEventListener('mouseup', () => s = false);
    prog.addEventListener('touchstart', seek, { passive: true });
    prog.addEventListener('touchmove', seek, { passive: true });
    btnMute.addEventListener('click', () => { audio.muted = !audio.muted; });
    volIn.addEventListener('input', () => { audio.volume = parseFloat(volIn.value); audio.muted = audio.volume === 0; });
    return card;
  }
</script>
</body>
</html>
"""


# ============================================================
# Routes
# ============================================================
@app.route("/")
@app.route("/browse/", defaults={"subpath": ""})
@app.route("/browse/<path:subpath>")
def browse(subpath: str = ""):
    target = safe_path(subpath)
    if not target.exists():
        abort(404)

    # Direct file → download
    if target.is_file():
        mime = _mt.guess_type(str(target))[0]
        ext = target.suffix.lower().lstrip(".")
        if ext in MIME_OVERRIDES:
            mime = MIME_OVERRIDES[ext]
        return send_file(
            target,
            mimetype=mime,
            as_attachment=False,
            conditional=True,
        )

    show_hidden = request.args.get("hidden") == "1"
    root = _require_share_dir()

    items = []
    total = 0
    try:
        entries = sorted(
            os.scandir(target),
            key=lambda e: (not e.is_dir(), e.name.lower()),
        )
    except PermissionError:
        abort(403)

    for entry in entries:
        name = entry.name
        if not show_hidden and name.startswith("."):
            continue
        try:
            stat = entry.stat()
        except OSError:
            continue
        is_dir = entry.is_dir()
        key = "folder" if is_dir else get_icon_key(name)
        svg, color = ICON_SVG[key]
        rel = os.path.relpath(entry.path, root)
        url = url_for("browse", subpath=rel)
        size = "" if is_dir else human_size(stat.st_size)
        if not is_dir:
            total += stat.st_size
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
            "%Y-%m-%d %H:%M")

        quality = None
        quality_tag = None
        if not is_dir and get_ext(name) in PREVIEW_VIDEO:
            info = probe_video_path(Path(entry.path))
            if info:
                quality = info["label"]
                quality_tag = info["standard"]

        items.append({
            "name": name,
            "is_dir": is_dir,
            "svg": svg,
            "color": color,
            "size": size,
            "mtime": mtime,
            "url": url,
            "kind": None if is_dir else preview_kind(name),
            "quality": quality,
            "quality_tag": quality_tag,
        })

    parent = None
    if subpath:
        parent = os.path.dirname(subpath.rstrip("/"))

    return render_template_string(
        TEMPLATE.replace("__FAVICON__", FAVICON_SVG),
        items=items,
        parent=parent,
        count=len(items),
        total_size=human_size(total) if total else "0 B",
        display_path=str(target),
        port=PORT,
        icons=ICON_SVG,
    )


# ============================================================
# Optional JSON API
# ============================================================
@app.route("/api/list")
@app.route("/api/list/<path:subpath>")
def api_list(subpath: str = ""):
    target = safe_path(subpath)
    if not target.exists() or not target.is_dir():
        return jsonify({"error": "not found"}), 404
    root = _require_share_dir()
    out = []
    for entry in os.scandir(target):
        try:
            st = entry.stat()
        except OSError:
            continue
        out.append({
            "name": entry.name,
            "dir": entry.is_dir(),
            "size": None if entry.is_dir() else st.st_size,
            "mtime": st.st_mtime,
            "rel": os.path.relpath(entry.path, root),
        })
    return jsonify({"path": str(target), "entries": out})


@app.route("/api/info")
def api_info():
    root = _require_share_dir()
    return jsonify({
        "share_dir": str(root),
        "port": PORT,
        "interfaces": list_network_interfaces(),
    })


# ============================================================
# Standalone run
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LANShare standalone server")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to share (default: current)")
    parser.add_argument("-p", "--port", type=int, default=PORT,
                        help=f"Port (default: {PORT})")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Bind host (default: 0.0.0.0)")
    args = parser.parse_args()

    set_share_dir(args.directory)
    PORT = args.port
    ip = get_local_ip()
    print(f"LANShare serving {SHARE_DIR}")
    print(f"  → http://{ip}:{PORT}")
    app.run(host=args.host, port=PORT, threaded=True)
