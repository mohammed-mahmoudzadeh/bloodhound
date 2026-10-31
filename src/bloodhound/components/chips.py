"""Status chip — minimal, monochrome, with a pulsing green online dot."""
from __future__ import annotations

import asyncio

import flet as ft

from ..theme import Space, Radius


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

    is_online = (tone == "online")
    dot_color = "#22c55e" if is_online else P["text_faint"]

    if is_online:
        # Layered dot: soft halo + solid center (matches the sidebar status dot).
        halo = ft.Container(
            width=14, height=14, border_radius=7,
            bgcolor=dot_color, opacity=0.25,
        )
        core = ft.Container(
            width=7, height=7, border_radius=3.5,
            bgcolor=dot_color,
            alignment=ft.Alignment.CENTER,
        )
        dot: ft.Control = ft.Stack(
            [halo, core],
            width=14, height=14,
            alignment=ft.Alignment.CENTER,
        )
        pulse_halo = halo
    else:
        dot = ft.Container(
            width=7, height=7,
            border_radius=3.5,
            bgcolor=dot_color,
        )
        pulse_halo = None

    chip = ft.Container(
        content=ft.Row(
            [
                dot,
                ft.Container(width=Space.sm),
                ft.Text(text, color=fg, size=12, weight=ft.FontWeight.W_500),
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

    # Kick off the async pulse once the chip is mounted on a page.
    if pulse_halo is not None:
        async def _pulse():
            while True:
                pulse_halo.opacity = 0.45
                try: pulse_halo.update()
                except Exception: pass
                await asyncio.sleep(0.9)
                pulse_halo.opacity = 0.10
                try: pulse_halo.update()
                except Exception: pass
                await asyncio.sleep(0.9)

        def _start_pulse(_e=None):
            try:
                chip.page.run_task(_pulse)
            except Exception:
                pass

        chip.on_update = _start_pulse

    return chip