"""HTTP Range header parsing, ETag, and chunked file streaming."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .config import STREAM_CHUNK_SIZE


RANGE_RE = re.compile(r"^(\d*)-(\d*)$")


def parse_range_header(header: str, file_size: int):
    if not header:
        return None
    header = header.strip()
    if not header.lower().startswith("bytes="):
        return None

    spec = header[6:].split(",")[0].strip()
    m = RANGE_RE.match(spec)
    if not m:
        return None

    start_s, end_s = m.group(1), m.group(2)
    if start_s == "" and end_s == "":
        return None

    if start_s == "":
        try:
            length = int(end_s)
        except ValueError:
            return None
        if length <= 0:
            return None
        start = max(0, file_size - length)
        end = file_size - 1
    else:
        try:
            start = int(start_s)
        except ValueError:
            return None
        if end_s == "":
            end = file_size - 1
        else:
            try:
                end = int(end_s)
            except ValueError:
                return None

    if start > end or start >= file_size:
        return None
    end = min(end, file_size - 1)
    return (start, end)


def etag_for(path: Path, st) -> str:
    raw = f"{st.st_mtime_ns}-{st.st_size}-{getattr(st, 'st_ino', 0)}"
    return '"' + hashlib.md5(raw.encode()).hexdigest()[:16] + '"'


def file_stream(path: Path, start: int, end: int,
                chunk_size: int = STREAM_CHUNK_SIZE):
    """Yield bytes from start..end (inclusive) in small chunks.

    Small chunks let the kernel TCP stack coalesce writes with Nagle's
    algorithm, avoiding IP fragmentation and pixel artifacts.
    """
    remaining = end - start + 1
    with open(path, "rb", buffering=0) as f:
        f.seek(start)
        while remaining > 0:
            chunk = f.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk
