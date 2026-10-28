"""Shared page scaffold — consistent layout across all views."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Type, BP


def page_scaffold(
    P,
    title: str,
    subtitle: str = "",
    content: ft.Control = None,
    page_width: int = 1200,
    actions: list | None = None,
) -> ft.Control:
    """Wrap a view's content in a consistent, responsive page structure.

    - Desktop (>= md): centered, max-width 880, WITH header
    - Mobile: full-width with 16px gutters, NO header
    """
    is_desktop = page_width >= BP.md
    max_w = 880 if is_desktop else None

    # ---- Header: only on desktop ----
    header = ft.Container()
    if is_desktop:
        title_col = ft.Column(
            [
                ft.Text(title, color=P["text"], **Type.headline_sm),
                ft.Text(subtitle, color=P["text_muted"], **Type.body_sm)
                if subtitle else ft.Container(),
            ],
            spacing=2,
            tight=True,
            expand=True,
        )
        header_row = ft.Row(
            [title_col, *(actions or [])],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        header = ft.Column(
            [
                header_row,
                ft.Container(
                    height=1,
                    bgcolor=P["border"],
                    margin=ft.Margin.only(top=Space.md),
                ),
                ft.Container(height=Space.lg),
            ],
            spacing=0,
            tight=True,
        )

    # ---- Body ----
    body = ft.Column(
        [
            header,
            content,
        ],
        spacing=0,
        tight=True,
    )

    if max_w:
        # Desktop: centered container
        return ft.Row(
            [
                ft.Container(
                    content=body,
                    width=max_w,
                    padding=ft.Padding.symmetric(
                        horizontal=Space.lg,
                        vertical=Space.lg,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )

    # Mobile: full-width with 16px gutters
    return ft.Container(
        content=body,
        padding=ft.Padding.symmetric(
            horizontal=Space.md,
            vertical=Space.md,
        ),
        expand=True,
    )
