"""Log row — monochrome except errors/warnings."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Type


def LogRow(P, time_str, message, level="info"):
    """Log entry. Only warn/err use color; ok/info are monochrome."""
    tone = {
        "info": P["text_dim"],
        "ok":   P["text"],       # brighter than dim, not green
        "warn": P["warning"],    # soft yellow
        "err":  P["error"],      # soft red
    }.get(level, P["text_dim"])

    return ft.Row(
        [
            ft.Container(width=6, height=6, border_radius=3, bgcolor=tone,
                         margin=ft.Margin.only(top=5)),
            ft.Container(width=Space.sm + 2),
            ft.Text(time_str, color=P["text_faint"],
                    **Type.label_sm, width=56),
            ft.Text(message, color=tone, **Type.body_sm,
                    expand=True, selectable=True),
        ],
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
