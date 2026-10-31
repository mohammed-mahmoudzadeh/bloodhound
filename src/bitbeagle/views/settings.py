"""Settings — structured preferences."""
from __future__ import annotations

import flet as ft
from pathlib import Path

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
                        ft.Text(title, color=P["text"], size=15, weight=ft.FontWeight.W_600),
                        ft.Container(height=4),
                        ft.Text(subtitle, color=P["text_muted"], size=13, weight=ft.FontWeight.W_400),
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
        margin=ft.Margin.symmetric(vertical=Space.sm),
    )


def build_settings(P, state, handlers, page_width=1200):
    # ---- Appearance ----
    current_mode = getattr(state, "theme_mode", "auto")

    theme_dropdown = ft.Dropdown(
        value=current_mode,
        options=[
            ft.dropdown.Option(key="auto", text="Auto (system)"),
            ft.dropdown.Option(key="light", text="Light"),
            ft.dropdown.Option(key="dark", text="Dark"),
        ],
        on_select=lambda e: handlers["set_theme"](e.control.value or "auto"),
        width=200,
        height=46,
        bgcolor=P["surface_2"],
        color=P["text"],
        text_style=ft.TextStyle(color=P["text"], size=15),
        content_padding=ft.Padding.symmetric(
            horizontal=Space.md, vertical=0,
        ),
        # Use the modern border API for Flet 1.0.4
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
        P, hint="Device name", value=state.device_name, width=220,
        on_change=lambda e: handlers["set_device_name"](e.control.value or ""),
    )
    if state.server_running:
        device_field.disabled = True
        device_field.bgcolor = P["surface"]
        device_field.color = P["text_muted"]

    default_port_field = TextInput(
        P, hint="8000", value=state.port or "8000", width=140,
        on_change=lambda e: handlers["set_port"](e.control.value),
    )
    if state.server_running:
        default_port_field.disabled = True
        default_port_field.bgcolor = P["surface"]
        default_port_field.color = P["text_muted"]

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
    # Load the logo image for the About section, and make it larger.
    _here = Path(__file__).resolve()
    _asset_candidates = [
        _here.parent.parent.parent / "assets",
        _here.parent.parent.parent.parent / "assets",
        Path.cwd() / "assets",
        Path.cwd() / "src" / "assets",
    ]
    assets_dir = next((p for p in _asset_candidates if p.is_dir() and (p / "logo_dark.png").exists()), None)
    
    if assets_dir:
        logo_filename = "logo_dark.png" if state.dark else "logo_light.png"
        about_icon = ft.Container(
            content=ft.Image(
                src=str(assets_dir / logo_filename),
                width=40, height=40,
                fit=ft.BoxFit.CONTAIN
            ),
            width=56, height=56,
            bgcolor=P["surface_2"],
            border=ft.Border.all(1, P["border"]),
            border_radius=Radius.md,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(6),
        )
    else:
        about_icon = ft.Icon(ft.Icons.FOLDER_SHARED_ROUNDED, size=40, color=P["text_muted"])

    about_card = SectionCard(
        P, dark=state.dark,
        title="About",
        content=ft.Column(
            [
                _row_setting(
                    P,
                    "BitBeagle",
                    "Version 1.0.0 — Local file sharing.",
                    about_icon,
                ),
                _divider(P),
                _row_setting(
                    P,
                    "Share directory",
                    state.share_dir_display,
                    ft.Container(),
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