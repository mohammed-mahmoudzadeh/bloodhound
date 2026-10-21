"""Log row — monochrome except errors/warnings."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Type


def LogRow(P, time_str, message, level="info"):
    """Log entry. Only warn/err use color; ok/info are monochrome."""
    tone = {
        "info": P["text_dim"],
        "ok":   P["text"],        # brighter than dim
        "warn": P["warning"],     # soft yellow
        "err":  P["error"],       # soft red
    }.get(level, P["text_dim"])

    return ft.Row(
        [
            # Time column
            ft.Text(
                time_str, color=P["text_faint"], size=12, font_family="Inter",
                width=64, text_align=ft.TextAlign.RIGHT,
            ),
            ft.Container(width=Space.md), # Spacing
            
            # Bullet dot
            ft.Container(
                width=6, height=6, border_radius=3, bgcolor=tone,
                margin=ft.Margin.only(top=6),
            ),
            ft.Container(width=Space.sm + 2),
            
            # Log message
            ft.Text(
                message, color=tone, size=14, font_family="Inter",
                expand=True, selectable=True,
            ),
        ],
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )