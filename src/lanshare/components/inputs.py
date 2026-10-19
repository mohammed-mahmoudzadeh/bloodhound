"""Inputs — animated focus, flat."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Motion, Type


def LabeledField(P, label, field, helper=None, width=None):
    children = [
        ft.Text(label, color=P["text_muted"], **Type.label_md),
        ft.Container(height=Space.xs),
        field,
    ]
    if helper:
        children.append(ft.Container(height=Space.xs))
        children.append(
            ft.Text(helper, color=P["text_faint"], **Type.label_sm))
    return ft.Container(
        content=ft.Column(children, spacing=0, tight=True),
        width=width,
    )


def TextInput(P, hint="", value="", width=None,
              on_change=None, password=False):
    tf = ft.TextField(
        value=value,
        hint_text=hint,
        width=width,
        password=password,
        on_change=on_change,
        height=44,
        border_radius=Radius.lg,
        bgcolor=P["surface_2"],
        border_color=P["border"],
        focused_border_color=P["primary"],
        color=P["text"],
        hint_style=ft.TextStyle(color=P["text_faint"], size=13),
        text_style=ft.TextStyle(color=P["text"], size=14),
        content_padding=ft.Padding.symmetric(
            horizontal=Space.md, vertical=0),
        cursor_color=P["primary"],
        border_width=1,
    )
    return tf
