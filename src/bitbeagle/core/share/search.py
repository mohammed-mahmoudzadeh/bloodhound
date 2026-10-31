"""Recursive search + /api/search route."""
from __future__ import annotations

import datetime
import os
from pathlib import Path

from flask import request, url_for

from .config import (
    SEARCH_MAX_RESULTS, SEARCH_MAX_DEPTH, SEARCH_MIN_QUERY_LEN,
    SEARCH_SKIP_DIRS, THUMB_BUDGET_PER_PAGE,
    PREVIEW_VIDEO,
    get_share_dir,
)
from .icons import ICON_SVG
from .probe import probe_video_path
from .thumbs import get_or_create_thumb
from .utils import get_ext, get_icon_key, human_size, preview_kind


def _should_skip_dir(name: str) -> bool:
    if name.startswith("."):
        return True
    return name in SEARCH_SKIP_DIRS


def _make_search_result_item(entry, is_dir: bool, st, thumb_budget: int):
    share_root = get_share_dir()
    name = entry.name
    rel = os.path.relpath(entry.path, share_root).replace(os.sep, "/")
    icon_key = "folder" if is_dir else get_icon_key(name)
    svg, color = ICON_SVG[icon_key]

    kind = None if is_dir else preview_kind(name)

    quality = None
    quality_tag = None
    if not is_dir and get_ext(name) in PREVIEW_VIDEO:
        info = probe_video_path(Path(entry.path))
        if info:
            quality = info["label"]
            quality_tag = info["standard"]

    thumb_url = None
    if kind in ("image", "video") and thumb_budget > 0:
        thumb_url = get_or_create_thumb(Path(entry.path), kind)

    return {
        "name": name,
        "path": rel,
        "url": url_for("browse", subpath=os.path.relpath(entry.path, share_root)),
        "is_dir": is_dir,
        "size": "" if is_dir else human_size(st.st_size),
        "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
        "kind": kind,
        "svg": svg,
        "color": color,
        "quality": quality,
        "quality_tag": quality_tag,
        "thumb": thumb_url,
    }


def _do_search(root: Path, query: str, limit: int = SEARCH_MAX_RESULTS):
    q = query.lower()
    results = []

    stack = [(root, 0)]
    visited = 0
    max_visited = 200_000
    thumb_budget = THUMB_BUDGET_PER_PAGE

    while stack and len(results) < limit and visited < max_visited:
        current, depth = stack.pop()
        if depth > SEARCH_MAX_DEPTH:
            continue

        try:
            with os.scandir(current) as it:
                for entry in it:
                    visited += 1
                    if visited >= max_visited:
                        break

                    name = entry.name

                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                    except OSError:
                        continue

                    if is_dir and _should_skip_dir(name):
                        if q in name.lower():
                            try:
                                st = entry.stat()
                                results.append(_make_search_result_item(entry, True, st, 0))
                            except OSError:
                                pass
                        continue

                    if q in name.lower():
                        try:
                            st = entry.stat()
                        except OSError:
                            continue
                        item = _make_search_result_item(entry, is_dir, st, thumb_budget)
                        if item.get("thumb"):
                            thumb_budget -= 1
                        results.append(item)
                        if len(results) >= limit:
                            break

                    if is_dir:
                        stack.append((Path(entry.path), depth + 1))

        except (PermissionError, FileNotFoundError, NotADirectoryError):
            continue

    return results


def api_search_route():
    q = (request.args.get("q") or "").strip()
    if len(q) < SEARCH_MIN_QUERY_LEN:
        return {"query": q, "results": [], "truncated": False, "count": 0}

    results = _do_search(get_share_dir(), q, SEARCH_MAX_RESULTS)
    return {
        "query": q,
        "results": results,
        "truncated": len(results) >= SEARCH_MAX_RESULTS,
        "count": len(results),
    }
