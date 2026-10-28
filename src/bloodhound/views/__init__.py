"""View builders."""
from .dashboard import build_dashboard
from .activity import build_activity
from .settings import build_settings


def build_view(index: int, P, state, handlers, page_width=1200):
    """Dispatch to the right view builder with consistent signature."""
    if index == 0:
        return build_dashboard(P, state, handlers, page_width)
    if index == 1:
        return build_activity(P, state, handlers, page_width)
    if index == 2:
        return build_settings(P, state, handlers, page_width)
    return build_dashboard(P, state, handlers, page_width)


__all__ = [
    "build_view",
    "build_dashboard",
    "build_activity",
    "build_settings",
]
