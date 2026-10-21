"""Buttons — flat, monochrome, animated."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def _label(icon, text, color):
    children = []
    if icon:
        children.append(ft.Icon(icon, size=18, color=color))  # Increased icon size
        children.append(ft.Container(width=Space.sm))
    children.append(ft.Text(text, color=color, size=14, weight=ft.FontWeight.W_500))  # Increased text size
    return ft.Row(children, spacing=0,
                  alignment=ft.MainAxisAlignment.CENTER, tight=True)


def _btn(*, content, bg, border, hover_bg, on_click, width, disabled=False):
    c = ft.Container(
        content=content,
        height=44,
        width=width,
        bgcolor=bg,
        border=ft.Border.all(1, border) if border else None,
        border_radius=Radius.lg,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=None if disabled else on_click,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        scale=1.0,
    )

    if not disabled and on_click:
        def _on_hover(e):
            try:
                c.bgcolor = hover_bg if e.data == "true" else bg
                c.scale = 1.02 if e.data == "true" else 1.0
                c.update()
            except Exception:
                pass
        c.on_hover = _on_hover

    return c


def PrimaryButton(P, text, icon=None, on_click=None, width=None,
                  disabled=False):
    """Filled — white in dark, black in light."""
    return _btn(
        content=_label(icon, text, P["on_primary"]),
        bg=P["primary"],
        border=None,
        hover_bg=P["primary_hover"],
        on_click=on_click,
        width=width,
        disabled=disabled,
    )


def SecondaryButton(P, text, icon=None, on_click=None, width=None,
                    disabled=False):
    """Outlined — border only."""
    return _btn(
        content=_label(icon, text, P["text_dim"]),
        bg="transparent",
        border=P["border_strong"],
        hover_bg=P["surface_hover"],
        on_click=on_click,
        width=width,
        disabled=disabled,
    )


def DestructiveButton(P, text, icon=None, on_click=None, width=None):
    """Outlined red — for destructive actions."""
    return _btn(
        content=_label(icon, text, P["error"]),
        bg="transparent",
        border=P["error"],
        hover_bg=P["error_bg"],
        on_click=on_click,
        width=width,
    )


def IconActionButton(P, icon, on_click=None, tooltip=None, size=40):
    """Square icon-only button."""
    c = ft.Container(
        content=ft.Icon(icon, size=20, color=P["text_dim"]),
        width=size, height=size,
        border_radius=Radius.md,
        bgcolor="transparent",
        alignment=ft.Alignment.CENTER,
        ink=True,
        tooltip=tooltip,
        on_click=on_click,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
    )
    return c