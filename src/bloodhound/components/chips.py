"""Status chip — minimal, monochrome, with green online state."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def StatusChip(P, text, tone="neutral"):
    """Small pill.

    Tones:
        neutral — unknown state
        online  — green (running)
        offline — muted (not running)
        error, warning, info — for other statuses
    """
    map_ = {
        "neutral": (P["text_muted"],    P["surface_2"],  P["border"]),
        "online":  (P["status_online"], P["success_bg"], P["status_online"]),
        "offline": (P["text_muted"],    P["surface_2"],  P["border"]),
        "error":   (P["error"],         P["error_bg"],   P["error"]),
        "warning": (P["warning"],       P["warning_bg"], P["warning"]),
        "info":    (P["text_dim"],      P["surface_2"],  P["border"]),
    }
    fg, bg, border = map_.get(tone, map_["neutral"])
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(width=7, height=7,
                             border_radius=3.5, bgcolor=fg),
                ft.Container(width=Space.sm),
                ft.Text(text, color=fg, size=12,
                        weight=ft.FontWeight.W_500),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        padding=ft.Padding.symmetric(
            horizontal=Space.md, vertical=Space.xs + 2),
        bgcolor=bg,
        border=ft.Border.all(1, border),
        border_radius=Radius.pill,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )
