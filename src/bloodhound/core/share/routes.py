"""Register all URL rules on a Flask app."""
from __future__ import annotations

import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import (
    Flask, abort, render_template, request, url_for,
)

from .access_log import register_access_log
from .config import (
    THUMB_BUDGET_PER_PAGE, PREVIEW_VIDEO,
    get_share_dir,
)
from .files import serve_file
from .icons import ICON_SVG
from .probe import probe_video_path
from .search import api_search_route
from .template import FAVICON_SVG
from .thumbs import get_or_create_thumb, serve_thumb_route
from .utils import get_ext, get_icon_key, human_size, preview_kind, safe_path
from .watcher import sse_route


def _build_items(target: Path, show_hidden: bool):
    """Scan `target` and build the list of item dicts for the template."""
    try:
        with os.scandir(target) as it:
            entries = sorted(
                it,
                key=lambda e: (not e.is_dir(), e.name.lower()),
            )
    except PermissionError:
        abort(403)
    except FileNotFoundError:
        abort(404)

    video_paths = []
    raw = []
    for entry in entries:
        name = entry.name
        if not show_hidden and name.startswith("."):
            continue
        try:
            stat = entry.stat()
        except OSError:
            continue
        is_dir = entry.is_dir()
        raw.append((entry, name, stat, is_dir))
        if not is_dir and get_ext(name) in PREVIEW_VIDEO:
            video_paths.append(Path(entry.path))

    # Probe videos in parallel
    video_infos: dict[Path, dict | None] = {}
    if video_paths:
        with ThreadPoolExecutor(max_workers=min(8, len(video_paths))) as pool:
            futures = {pool.submit(probe_video_path, p): p for p in video_paths}
            for fut, p in futures.items():
                try:
                    video_infos[p] = fut.result()
                except Exception:
                    video_infos[p] = None

    share_root = get_share_dir()
    items = []
    total = 0
    thumb_budget = THUMB_BUDGET_PER_PAGE

    for entry, name, stat, is_dir in raw:
        key = "folder" if is_dir else get_icon_key(name)
        svg, color = ICON_SVG[key]
        rel = os.path.relpath(entry.path, share_root)
        url = url_for("browse", subpath=rel)
        size = "" if is_dir else human_size(stat.st_size)
        if not is_dir:
            total += stat.st_size
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

        kind = None if is_dir else preview_kind(name)

        quality = None
        quality_tag = None
        if not is_dir and get_ext(name) in PREVIEW_VIDEO:
            info = video_infos.get(Path(entry.path))
            if info:
                quality = info["label"]
                quality_tag = info["standard"]

        thumb_url = None
        if kind in ("image", "video") and thumb_budget > 0:
            thumb_url = get_or_create_thumb(Path(entry.path), kind)
            if thumb_url:
                thumb_budget -= 1

        items.append({
            "name": name,
            "is_dir": is_dir,
            "svg": svg,
            "color": color,
            "size": size,
            "mtime": mtime,
            "url": url,
            "kind": kind,
            "quality": quality,
            "quality_tag": quality_tag,
            "thumb": thumb_url,
        })

    return items, total


def register_routes(app: Flask) -> None:

    @app.route("/")
    @app.route("/browse/", defaults={"subpath": ""})
    @app.route("/browse/<path:subpath>")
    def browse(subpath: str = ""):
        target = safe_path(subpath)
        if not target.exists():
            abort(404)

        if target.is_file():
            return serve_file(target)

        show_hidden = request.args.get("hidden") == "1"
        items, total = _build_items(target, show_hidden)

        parent = None
        if subpath:
            parent = os.path.dirname(subpath.rstrip("/"))

        return render_template(
            "index.html",
            items=items,
            parent=parent,
            count=len(items),
            total_size=human_size(total) if total else "0 B",
            display_path=str(target),
            host=request.host,
            icons=ICON_SVG,
        )

    @app.route("/thumb/<name>")
    def serve_thumb(name: str):
        return serve_thumb_route(name)

    @app.route("/events")
    def sse_events():
        return sse_route()

    @app.route("/api/search")
    def api_search():
        return api_search_route()

    register_access_log(app)