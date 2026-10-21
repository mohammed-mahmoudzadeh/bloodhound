"""Serve a single file with full Range / ETag / 304 / HEAD / 416 support."""
from __future__ import annotations

import datetime
import stat as _stat
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

from flask import Response, abort, request

from .config import PREVIEW_MIMES_INLINE
from .range import parse_range_header, etag_for, file_stream
from .utils import guess_mimetype, preview_kind


def serve_file(path: Path):
    try:
        st = path.stat()
    except FileNotFoundError:
        abort(404)
    except PermissionError:
        abort(403)

    if not _stat.S_ISREG(st.st_mode):
        abort(404)

    file_size = st.st_size
    mimetype = guess_mimetype(path)
    etag = etag_for(path, st)
    last_mod = formatdate(st.st_mtime, usegmt=True)

    kind = preview_kind(path.name)
    inline = kind in PREVIEW_MIMES_INLINE

    def base_headers():
        safe_name = path.name.replace('"', "")
        h = {
            "Content-Type": mimetype,
            "Accept-Ranges": "bytes",
            "ETag": etag,
            "Last-Modified": last_mod,
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
            "Vary": "Range",
        }
        h["Content-Disposition"] = (
            f'inline; filename="{safe_name}"' if inline
            else f'attachment; filename="{safe_name}"'
        )
        return h

    range_header = request.headers.get("Range")
    rng = parse_range_header(range_header, file_size) if range_header else None

    if range_header and rng is None:
        resp = Response(status=416)
        resp.headers["Content-Range"] = f"bytes */{file_size}"
        resp.headers.update(base_headers())
        return resp

    if_none_match = request.headers.get("If-None-Match")
    if_modified_since = request.headers.get("If-Modified-Since")

    not_modified = False
    if if_none_match and etag in if_none_match:
        not_modified = True
    elif if_modified_since:
        try:
            since = parsedate_to_datetime(if_modified_since)
            if since.tzinfo is None:
                since = since.replace(tzinfo=datetime.timezone.utc)
            if st.st_mtime <= since.timestamp() + 1:
                not_modified = True
        except (TypeError, ValueError):
            pass

    if request.method == "HEAD":
        resp = Response(status=200)
        resp.headers.update(base_headers())
        if rng is not None:
            start, end = rng
            resp.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
            resp.headers["Content-Length"] = str(end - start + 1)
        else:
            resp.headers["Content-Length"] = str(file_size)
        return resp

    if not_modified and rng is None:
        resp = Response(status=304)
        resp.headers.update({
            "ETag": etag,
            "Last-Modified": last_mod,
            "Cache-Control": "public, max-age=3600",
        })
        return resp

    if rng is not None:
        start, end = rng
        length = end - start + 1
        headers = base_headers()
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        headers["Content-Length"] = str(length)
        return Response(
            file_stream(path, start, end),
            status=206,
            headers=headers,
            direct_passthrough=True,
        )

    headers = base_headers()
    headers["Content-Length"] = str(file_size)
    return Response(
        file_stream(path, 0, file_size - 1),
        status=200,
        headers=headers,
        direct_passthrough=True,
    )
