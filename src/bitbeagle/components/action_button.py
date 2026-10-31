"""A button that shows a spinner and disables itself while an action runs."""
from __future__ import annotations

import asyncio
import flet as ft

from ..theme import Space, Radius


def ActionButton(
    P,
    text: str,
    icon=None,
    on_click=None,
    kind: str = "primary",   # "primary" | "secondary" | "destructive"
    width=None,
    disabled: bool = False,
) -> ft.Control:
    """A button that runs an action and shows a loading spinner while waiting.

    The `on_click` callback can be either:
    - a plain function (sync) → button is disabled only during the callback
    - a coroutine function (async) → spinner shows until the coroutine completes
    """

    is_loading = {"value": False}

    # --- Palette per kind ------------------------------------------------
    if kind == "primary":
        bg, fg, border = P["primary"], P["on_primary"], None
        hover_bg = P["primary_hover"]
    elif kind == "destructive":
        bg, fg, border = "transparent", P["error"], P["error"]
        hover_bg = P["error_bg"]
    else:  # secondary
        bg, fg, border = "transparent", P["text_dim"], P["border_strong"]
        hover_bg = P["surface_hover"]

    # --- Inner content (label / spinner) --------------------------------
    label_row = ft.Row(
        [
            ft.Icon(icon, size=18, color=fg) if icon else ft.Container(),
            ft.Container(width=Space.sm) if icon else ft.Container(),
            ft.Text(text, color=fg, size=14, weight=ft.FontWeight.W_500),
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
    )

    spinner = ft.ProgressRing(
        width=18, height=18, stroke_width=2,
        color=fg,
        visible=False,
    )

    content = ft.Stack(
        [label_row, spinner],
        width=None,
        height=None,
    )

    btn = ft.Container(
        content=content,
        height=44,
        width=width,
        bgcolor=bg,
        border=ft.Border.all(1, border) if border else None,
        border_radius=Radius.lg,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=None,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        opacity=0.5 if disabled else 1.0,
    )

    def _set_loading(value: bool):
        is_loading["value"] = value
        label_row.visible = not value
        spinner.visible = value
        btn.disabled = value
        btn.opacity = 0.6 if value else (0.5 if disabled else 1.0)
        try:
            btn.update()
        except Exception:
            pass

    def _handle_click(e):
        if is_loading["value"] or disabled:
            return
        if on_click is None:
            return

        _set_loading(True)

        if asyncio.iscoroutinefunction(on_click):
            async def _run_async():
                try:
                    await on_click(e)
                finally:
                    _set_loading(False)
            try:
                e.page.run_task(_run_async)
            except Exception:
                _set_loading(False)
        else:
            try:
                on_click(e)
            finally:
                _set_loading(False)

    if not disabled:
        btn.on_click = _handle_click

        def _on_hover(e):
            if is_loading["value"]:
                return
            try:
                btn.bgcolor = hover_bg if e.data == "true" else bg
                btn.update()
            except Exception:
                pass
        btn.on_hover = _on_hover

    return btn