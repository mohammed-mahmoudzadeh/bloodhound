"""Settings — structured preferences."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type
from ..components import (
    SectionCard, LabeledField, TextInput, SecondaryButton,
)
from ._scaffold import page_scaffold


def _row_setting(
    P,
    title: str,
    subtitle: str,
    control: ft.Control,
) -> ft.Control:
    """A settings row — title + subtitle on left, control on right."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(title, color=P["text"], **Type.title_sm),
                        ft.Container(height=2),
                        ft.Text(subtitle, color=P["text_muted"],
                                **Type.body_sm),
                    ],
                    spacing=0, tight=True, expand=True,
                ),
                control,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Space.md,
        ),
        padding=ft.Padding.symmetric(vertical=Space.md),
    )


def _divider(P):
    return ft.Container(
        height=1,
        bgcolor=P["border"],
        margin=ft.Margin.symmetric(vertical=Space.xs),
    )


def build_settings(P, state, handlers, page_width=1200):
    # ---- Appearance ----
    current_mode = "dark" if state.dark else "light"

    theme_dropdown = ft.Dropdown(
        value=current_mode,
        options=[
            ft.dropdown.Option(key="auto", text="Auto (system)"),
            ft.dropdown.Option(key="light", text="Light"),
            ft.dropdown.Option(key="dark", text="Dark"),
        ],
        on_select=lambda e: handlers["set_theme"](
            e.control.value or "auto"),
        width=200,
        height=44,
        border_radius=Radius.lg,
        bgcolor=P["surface_2"],
        border_color=P["border"],
        focused_border_color=P["text"],
        color=P["text"],
        text_style=ft.TextStyle(color=P["text"], size=14),
        border_width=1,
        content_padding=ft.Padding.symmetric(
            horizontal=Space.md, vertical=0,
        ),
    )

    appearance_card = SectionCard(
        P, dark=state.dark,
        title="Appearance",
        content=ft.Column(
            [
                _row_setting(
                    P,
                    "Theme",
                    "Choose light, dark, or follow the system.",
                    theme_dropdown,
                ),
            ],
            spacing=0, tight=True,
        ),
    )

    # ---- Server ----
    device_field = TextInput(
        P, hint="Device name", value="My Phone", width=200,
    )
    default_port_field = TextInput(
        P, hint="8000", value=state.port or "8000", width=120,
    )

    server_card = SectionCard(
        P, dark=state.dark,
        title="Server",
        content=ft.Column(
            [
                _row_setting(
                    P,
                    "Device name",
                    "Shown in the web page header.",
                    device_field,
                ),
                _divider(P),
                _row_setting(
                    P,
                    "Default port",
                    "Used when starting the server.",
                    default_port_field,
                ),
            ],
            spacing=0, tight=True,
        ),
    )

    # ---- About ----
    about_card = SectionCard(
        P, dark=state.dark,
        title="About",
        content=ft.Column(
            [
                _row_setting(
                    P,
                    "LANShare",
                    "Version 1.0.0 — Local file sharing.",
                    ft.Icon(ft.Icons.FOLDER_SHARED_ROUNDED, size=24,
                            color=P["text_muted"]),
                ),
                _divider(P),
                _row_setting(
                    P,
                    "Share directory",
                    state.share_dir_display,
                    ft.Container(),  # spacer
                ),
            ],
            spacing=0, tight=True,
        ),
    )

    body = ft.Column(
        [
            appearance_card,
            ft.Container(height=Space.md),
            server_card,
            ft.Container(height=Space.md),
            about_card,
        ],
        spacing=0,
        tight=True,
    )

    return page_scaffold(
        P,
        title="Settings",
        subtitle="Preferences and information",
        content=body,
        page_width=page_width,
    )
