"""Card and AppBar — flat, monochrome, no hover animation."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def SectionCard(P, content, dark=True, padding: int | ft.Padding = Space.lg,
                title=None, subtitle=None):
    """Flat surface card with visible border."""
    children: list[ft.Control] = []
    if title:
        children.append(ft.Text(
            title, color=P["text"],
            size=15, weight=ft.FontWeight.W_600, font_family="Inter",
        ))
    if subtitle:
        children.append(ft.Container(height=Space.xs))
        children.append(
            ft.Text(
                subtitle,
                color=P["text_muted"],
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
                size=13, weight=ft.FontWeight.W_400, font_family="Inter",
            )
        )
    if title or subtitle:
        children.append(ft.Container(height=Space.md))
    children.append(content)

    return ft.Container(
        content=ft.Column(children, spacing=0, tight=True),
        padding=padding,
        bgcolor=P["surface"],
        border=ft.Border.all(1, P["border"]),
        border_radius=Radius.xl,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


def AppBar(P, title, subtitle=None, trailing=None, leading=None):
    """Top application bar."""
    left_children: list[ft.Control] = []
    if leading is not None:
        left_children.append(leading)
        left_children.append(ft.Container(width=Space.sm + 2))

    left_children.append(
        ft.Column(
            [
                ft.Text(
                    title, color=P["text"],
                    size=18, weight=ft.FontWeight.W_600, font_family="Inter",
                ) if title else ft.Container(),
                ft.Text(
                    subtitle, color=P["text_muted"],
                    size=13, weight=ft.FontWeight.W_400, font_family="Inter",
                ) if subtitle else ft.Container(),
            ],
            spacing=0, tight=True,
        )
    )

    left = ft.Row(
        left_children,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )

    return ft.Container(
        content=ft.Row(
            [left, ft.Container(expand=True), *(trailing or [])],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=Space.md, vertical=Space.md),
        border=ft.Border.only(bottom=ft.BorderSide(1, P["border"])),
        bgcolor=P["bg"],
    )