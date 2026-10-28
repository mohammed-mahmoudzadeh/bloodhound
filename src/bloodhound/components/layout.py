"""Layout helpers."""
from __future__ import annotations

import flet as ft

from ..theme import Space


def vspace(h: int = Space.md) -> ft.Container:
    return ft.Container(height=h)


def centered_content(content: ft.Control, max_width: int) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [content], spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=max_width,
        alignment=ft.Alignment.TOP_CENTER,
    )
