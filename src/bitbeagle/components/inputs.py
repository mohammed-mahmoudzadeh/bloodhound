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


def TextInput(P, hint="", value="", width=None, on_change=None, password=False, read_only=False):
    """A themed text field using the Flet 1.0.4 border API."""
    return ft.TextField(
        value=value,
        hint_text=hint,
        width=width,
        password=password,
        read_only=read_only,
        on_change=on_change,
        height=46,
        bgcolor=P["surface_2"],
        color=P["text"],
        hint_style=ft.TextStyle(color=P["text_faint"], size=14),
        text_style=ft.TextStyle(color=P["text"], size=15),
        content_padding=ft.Padding.symmetric(horizontal=Space.md, vertical=0),
        cursor_color=P["primary"],
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=Radius.lg,
                side=ft.BorderSide(1, P["border"]),
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=Radius.lg,
                side=ft.BorderSide(1, P["primary"]),
            ),
        },
    )