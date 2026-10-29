"""Status chip — minimal, monochrome, with a pulsing green online dot."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def StatusChip(P, text, tone="neutral"):
    """Small pill.

    Tones:
        neutral — unknown state
        online  — running; the status dot is green and pulses
        offline — not running
        error, warning, info — for other statuses
    """
    # Chip colors follow the monochrome palette.
    map_ = {
        "neutral": (P["text_muted"],    P["surface_2"],  P["border"]),
        "online":  (P["text"],          P["surface_2"],  P["border"]),
        "offline": (P["text_muted"],    P["surface_2"],  P["border"]),
        "error":   (P["error"],         P["error_bg"],   P["error"]),
        "warning": (P["warning"],       P["warning_bg"], P["warning"]),
        "info":    (P["text_dim"],      P["surface_2"],  P["border"]),
    }
    fg, bg, border = map_.get(tone, map_["neutral"])

    # The status dot: green when online, muted otherwise.
    is_online = (tone == "online")
    dot_color = "#22c55e" if is_online else P["text_faint"]

    dot = ft.Container(
        width=7, height=7,
        border_radius=3.5,
        bgcolor=dot_color,
        animate_opacity=ft.Animation(900, ft.AnimationCurve.EASE_IN_OUT),
        opacity=1.0,
        shadow=ft.BoxShadow(
            blur_radius=6,
            color=dot_color,
            spread_radius=0,
        ) if is_online else None,
    )

    chip = ft.Container(
        content=ft.Row(
            [
                dot,
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

    # Start a slow pulse on the dot (only when online).
    if is_online:
        try:
            async def _pulse():
                import asyncio
                while True:
                    dot.opacity = 0.5
                    try: dot.update()
                    except Exception: pass
                    await asyncio.sleep(0.6)
                    dot.opacity = 1.0
                    try: dot.update()
                    except Exception: pass
                    await asyncio.sleep(0.9)

            # `chip.page` is set once the control is attached to the page.
            # Flet calls `did_mount` on the control, but we can also defer
            # the task start via `chip.on_update` if `page` is available.
            def _start_pulse():
                try:
                    chip.page.run_task(_pulse)
                except Exception:
                    pass

            chip.on_update = lambda e: _start_pulse()
        except Exception:
            pass

    return chip