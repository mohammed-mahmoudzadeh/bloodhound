"""Dashboard — polished, monochrome."""
from __future__ import annotations

import flet as ft
import os
from typing import Union

from ..config import IS_ANDROID
from ..core.fileinfo import scan_folder
from ..core.share.android_services import (
    is_ignoring_battery_optimizations,
    has_storage_permission,
)
from ..theme import Space, Radius, Type, BP
from ..components import (
    PrimaryButton, SecondaryButton, DestructiveButton,
    SectionCard, LabeledField, TextInput, StatusChip, LogRow, vspace,
    IconActionButton,
)
from ._scaffold import page_scaffold


def _format_android_path(path: str) -> tuple[str, str]:
    """Returns (display_name, display_path) for a given path."""
    if not path:
        return "No folder selected", ""

    path = path.rstrip("/")

    if path == "/storage/emulated/0":
        return "Internal Storage", "Root of internal storage"
    
    if path.startswith("/storage/emulated/0/"):
        short_path = path.replace("/storage/emulated/0/", "~/")
        return os.path.basename(path) or path, short_path

    return os.path.basename(path) or path, path


def build_dashboard(P, state, handlers, page_width: int = 1200):
    toggle_server = handlers["toggle_server"]
    is_narrow = page_width < BP.md

    # ============================================================
    # Warning Banners (Android only)
    # ============================================================
    banners: list[ft.Control] = []
    if IS_ANDROID:
        if not has_storage_permission():
            banners.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER_OFF_ROUNDED, color=P["warning"], size=20),
                            ft.Container(width=Space.sm),
                            ft.Text(
                                "Storage permission not granted. Tap 'Fix' to allow file access.",
                                color=P["warning"], size=12, expand=True,
                            ),
                            ft.TextButton(
                                "Fix",
                                on_click=lambda e: handlers["request_permissions"](),
                                style=ft.ButtonStyle(color=P["warning"]),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.all(Space.md),
                    bgcolor=P["warning_bg"],
                    border=ft.Border.all(1, P["warning"]),
                    border_radius=Radius.md,
                )
            )
            banners.append(ft.Container(height=Space.sm))

        if not is_ignoring_battery_optimizations():
            banners.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.BATTERY_ALERT_ROUNDED, color=P["warning"], size=20),
                            ft.Container(width=Space.sm),
                            ft.Text(
                                "Background server may stop. Tap 'Fix' to allow background usage.",
                                color=P["warning"], size=12, expand=True,
                            ),
                            ft.TextButton(
                                "Fix",
                                on_click=lambda e: handlers["request_battery_exemption"](),
                                style=ft.ButtonStyle(color=P["warning"]),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.all(Space.md),
                    bgcolor=P["warning_bg"],
                    border=ft.Border.all(1, P["warning"]),
                    border_radius=Radius.md,
                )
            )
            banners.append(ft.Container(height=Space.md))

    # ============================================================
    # Hero — access URL
    # ============================================================
    link_icon_size = 22 if is_narrow else 24
    url_text_size = 17 if is_narrow else 20
    url_gap = Space.md

    link_icon = ft.Container(
        content=ft.Icon(ft.Icons.LINK_ROUNDED, size=link_icon_size, color=P["text_dim"]),
        padding=ft.Padding.only(top=2),
    )

    url_row = ft.Row(
        [
            link_icon,
            ft.Container(width=url_gap),
            ft.Text(
                state.access_url, color=P["text"], size=url_text_size, weight=ft.FontWeight.W_500,
                selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        tight=True,
    )

    if is_narrow:
        hero_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Access URL", color=P["text"], **Type.title_md,
                        ),
                        ft.Container(expand=True),
                        IconActionButton(P, icon=ft.Icons.CONTENT_COPY_ROUNDED, on_click=lambda e: handlers["copy_url"](), tooltip="Copy URL", size=32),
                        ft.Container(width=Space.sm),
                        IconActionButton(P, icon=ft.Icons.OPEN_IN_NEW_ROUNDED, on_click=lambda e: handlers["open_url"](), tooltip="Open in browser", size=32),
                        ft.Container(width=Space.sm),
                        IconActionButton(P, icon=ft.Icons.QR_CODE_ROUNDED, on_click=lambda e: handlers["show_qr"](), tooltip="Show QR code", size=32),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=Space.md),
                ft.Container(
                    content=url_row,
                    padding=ft.Padding.symmetric(horizontal=0, vertical=0),
                    bgcolor=ft.Colors.TRANSPARENT,
                ),
            ],
            spacing=0,
            tight=True,
        )
    else:
        hero_content = ft.Row(
            [
                ft.Container(
                    content=url_row,
                    padding=ft.Padding.symmetric(horizontal=0, vertical=0),
                    bgcolor=ft.Colors.TRANSPARENT,
                    expand=True,
                ),
                IconActionButton(P, icon=ft.Icons.CONTENT_COPY_ROUNDED, on_click=lambda e: handlers["copy_url"](), tooltip="Copy URL", size=36),
                ft.Container(width=Space.sm),
                IconActionButton(P, icon=ft.Icons.OPEN_IN_NEW_ROUNDED, on_click=lambda e: handlers["open_url"](), tooltip="Open in browser", size=36),
                ft.Container(width=Space.sm),
                IconActionButton(P, icon=ft.Icons.QR_CODE_ROUNDED, on_click=lambda e: handlers["show_qr"](), tooltip="Show QR code", size=36),
                ft.Container(width=Space.md),
                StatusChip(
                    P, "Online" if state.server_running else "Offline",
                    "online" if state.server_running else "offline",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    hero = SectionCard(P, dark=state.dark, padding=Space.lg, content=hero_content)

    # ============================================================
    # Server card
    # ============================================================
    port_field = TextInput(
        P, hint="8000", value=state.port,
        on_change=lambda e: handlers["set_port"](e.control.value),
    )
    if state.server_running:
        port_field.disabled = True
        port_field.bgcolor = P["surface"]
        port_field.color = P["text_muted"]

    iface_options = [
        ft.dropdown.Option(key=str(i), text=f"{label} · {ip}")
        for i, (label, ip) in enumerate(state.interfaces)
    ] or [ft.dropdown.Option(key="0", text="All Interfaces · 0.0.0.0")]

    iface_dropdown = ft.Dropdown(
        value=str(state.iface_index),
        options=iface_options,
        on_select=lambda e: handlers["on_iface_change"](int(e.control.value or "0")),
        height=46, 
        border_radius=Radius.lg, 
        bgcolor=P["surface_2"],
        border_color=P["border"], 
        focused_border_color=P["primary"],
        color=P["text"], 
        text_style=ft.TextStyle(color=P["text"], size=15),
        border_width=1, 
        content_padding=ft.Padding.symmetric(horizontal=Space.md, vertical=0),
        disabled=state.server_running,
    )
    if state.server_running:
        iface_dropdown.bgcolor = P["surface"]

    server_content = ft.Column(
        [
            ft.ResponsiveRow(
                [
                    ft.Container(content=LabeledField(P, "Port", port_field), col={"xs": 12, "sm": 6, "md": 4, "lg": 3}),
                    ft.Container(content=LabeledField(P, "Interface", iface_dropdown), col={"xs": 12, "sm": 6, "md": 8, "lg": 9}),
                ],
                spacing=Space.md, run_spacing=Space.md,
            ),
            vspace(Space.lg),
            ft.Row(
                [
                    ft.Container(
                        content=(
                            DestructiveButton(P, "Stop Server", icon=ft.Icons.POWER_SETTINGS_NEW_ROUNDED, on_click=toggle_server)
                            if state.server_running else
                            PrimaryButton(P, "Start Server", icon=ft.Icons.POWER_SETTINGS_NEW_ROUNDED, on_click=toggle_server)
                        ),
                        expand=True,
                    ),
                    ft.Container(width=Space.sm),
                    ft.Container(
                        content=SecondaryButton(
                            P, "Refresh IP",
                            icon=ft.Icons.SYNC_ROUNDED,
                            on_click=lambda e: handlers["refresh_ip"](),
                            disabled=state.server_running,
                        ),
                        expand=True,
                    ),
                ],
                spacing=0, wrap=False,
            ),
        ],
        spacing=0, tight=True,
    )

    server_card = SectionCard(
        P, dark=state.dark,
        title="Server",
        subtitle="Choose interface and port, then start.",
        padding=ft.Padding.symmetric(horizontal=Space.lg, vertical=Space.lg),
        content=server_content,
    )

    # ============================================================
    # Shared folder card
    # ============================================================
    folder_buttons = ft.Row(
        [
            ft.Container(
                content=SecondaryButton(P, "Pick folder", icon=ft.Icons.FOLDER_OPEN_ROUNDED, on_click=lambda e: handlers["pick_folder"]()),
                expand=True,
            ),
            ft.Container(width=Space.sm),
            ft.Container(
                content=SecondaryButton(P, "Share all", icon=ft.Icons.PUBLIC_ROUNDED, on_click=lambda e: handlers["share_all"]()),
                expand=True,
            ),
        ],
        spacing=0, wrap=False,
    )

    if state.share_dir:
        try:
            info = scan_folder(state.share_dir)
            folder_summary = info.summary_hidden_count
        except Exception:
            folder_summary = "Unable to read folder"
            
        folder_name, folder_path = _format_android_path(state.share_dir)
        
        if IS_ANDROID and folder_name == "Internal Storage":
            folder_icon = ft.Icons.PHONE_ANDROID_ROUNDED
        elif not IS_ANDROID and state.share_dir == str(os.path.expanduser("~")):
            folder_icon = ft.Icons.COMPUTER_ROUNDED
        else:
            folder_icon = ft.Icons.FOLDER_ROUNDED

        folder_info = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(folder_icon, size=24, color=P["text"]),
                        width=44, height=44,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(width=Space.md),
                    ft.Column(
                        [
                            ft.Text(
                                folder_name, color=P["text"], size=14, weight=ft.FontWeight.W_600,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{folder_path}  ·  {folder_summary}" if folder_path else folder_summary,
                                color=P["text_muted"], size=11, weight=ft.FontWeight.W_400,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=0, vertical=Space.sm),
            bgcolor=ft.Colors.TRANSPARENT,
        )

        divider = ft.Container(height=1, bgcolor=P["border"], margin=ft.Margin.only(top=Space.md, bottom=Space.sm))

        folder_content = ft.Column(
            [
                folder_buttons,
                divider,
                ft.Container(expand=True),
                folder_info,
                ft.Container(expand=True),
            ],
            spacing=0, tight=True,
            expand=True
        )
    else:
        placeholder = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.FOLDER_OFF_ROUNDED, size=24, color=P["text_faint"]),
                        width=44, height=44,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(width=Space.md),
                    ft.Text(
                        "Select a folder to start sharing",
                        color=P["text_faint"], size=13, italic=True,
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=0, vertical=Space.sm),
            bgcolor=ft.Colors.TRANSPARENT,
        )

        divider = ft.Container(height=1, bgcolor=P["border"], margin=ft.Margin.only(top=Space.md, bottom=Space.sm))

        folder_content = ft.Column(
            [
                folder_buttons,
                divider,
                ft.Container(expand=True),
                placeholder,
                ft.Container(expand=True),
            ],
            spacing=0, tight=True,
            expand=True
        )

    folder = SectionCard(
        P, dark=state.dark,
        title="Shared Folder", subtitle=None,
        padding=ft.Padding.symmetric(horizontal=Space.lg, vertical=Space.lg),
        content=folder_content,
    )

    # ============================================================
    # Layout 
    # ============================================================
    CARD_HEIGHT = 235

    if is_narrow:
        cards_section = ft.Column(
            [
                server_card,
                ft.Container(height=Space.sm),
                folder,
            ],
            spacing=0, tight=True,
        )
    else:
        cards_section = ft.Row(
            [
                ft.Container(content=server_card, expand=7, height=CARD_HEIGHT),
                ft.Container(content=folder, expand=5, height=CARD_HEIGHT),
            ],
            spacing=Space.md,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    layout_items = banners + [
        hero,
        ft.Container(height=Space.md),
        cards_section,
    ]

    body_content = ft.Column(layout_items, spacing=0, tight=True)

    return page_scaffold(
        P,
        title="Dashboard",
        subtitle="Server status and controls",
        content=body_content,
        page_width=page_width,
    )