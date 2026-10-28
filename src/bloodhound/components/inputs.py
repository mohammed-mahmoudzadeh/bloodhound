"""Inputs — animated focus, flat."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def LabeledField(P, label, field, helper=None, width=None):
    children = [
        ft.Text(label, color=P["text_muted"], size=12, weight=ft.FontWeight.W_500),
        ft.Container(height=Space.xs),
        field,
    ]
    if helper:
        children.append(ft.Container(height=Space.xs))
        children.append(ft.Text(helper, color=P["text_faint"], size=11))
        
    return ft.Container(
        content=ft.Column(children, spacing=0, tight=True),
        width=width,
    )


def TextInput(P, hint="", value="", width=None, on_change=None, password=False):
    return ft.TextField(
        value=value,
        hint_text=hint,
        width=width,
        password=password,
        on_change=on_change,
        height=46,
        border_radius=Radius.lg,
        bgcolor=P["surface_2"],
        border_color=P["border"],
        focused_border_color=P["primary"],
        color=P["text"],
        hint_style=ft.TextStyle(color=P["text_faint"], size=14),
        text_style=ft.TextStyle(color=P["text"], size=15),
        content_padding=ft.Padding.symmetric(horizontal=Space.md, vertical=0),
        cursor_color=P["primary"],
        border_width=1,
    )