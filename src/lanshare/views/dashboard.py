"""Dashboard — polished, monochrome."""
from __future__ import annotations

import flet as ft

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


def build_dashboard(P, state, handlers, page_width=1200):
    toggle_server = handlers["toggle_server"]
    is_narrow = page_width < BP.sm

    # ============================================================
    # Warning Banners (Android only)
    # ============================================================
    banners = []
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
    if is_narrow:
        url_display = state.access_url.replace("http://", "", 1)
        hero_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WIFI_ROUNDED, size=18, color=P["text"]),
                            width=36, height=36, bgcolor=P["surface_2"],
                            border=ft.Border.all(1, P["border"]), border_radius=Radius.lg,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(width=Space.sm + 2),
                        ft.Text("ACCESS URL", color=P["text_muted"], **Type.label_sm),
                        ft.Container(expand=True),
                        StatusChip(
                            P, "Online" if state.server_running else "Offline",
                            "online" if state.server_running else "offline",
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=Space.md),
                ft.Row(
                    [
                        ft.Text(
                            url_display, color=P["text"], size=14, weight=ft.FontWeight.W_700,
                            selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True,
                        ),
                        ft.Container(width=Space.xs),
                        IconActionButton(P, icon=ft.Icons.CONTENT_COPY_ROUNDED, on_click=lambda e: handlers["copy_url"](), tooltip="Copy URL", size=32),
                        ft.Container(width=2),
                        IconActionButton(P, icon=ft.Icons.OPEN_IN_NEW_ROUNDED, on_click=lambda e: handlers["open_url"](), tooltip="Open in browser", size=32),
                        ft.Container(width=2),
                        IconActionButton(P, icon=ft.Icons.QR_CODE_ROUNDED, on_click=lambda e: handlers["show_qr"](), tooltip="Show QR code", size=32),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=0, tight=True,
        )
    else:
        hero_content = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.WIFI_ROUNDED, size=18, color=P["text"]),
                    width=40, height=40, bgcolor=P["surface_2"],
                    border=ft.Border.all(1, P["border"]), border_radius=Radius.lg,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(width=Space.md),
                ft.Column(
                    [
                        ft.Text("ACCESS URL", color=P["text_muted"], **Type.label_sm),
                        ft.Container(height=2),
                        ft.Text(
                            state.access_url, color=P["text"], size=16, weight=ft.FontWeight.W_700,
                            selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=0, tight=True, expand=True,
                ),
                IconActionButton(P, icon=ft.Icons.CONTENT_COPY_ROUNDED, on_click=lambda e: handlers["copy_url"](), tooltip="Copy URL", size=36),
                ft.Container(width=Space.xs),
                IconActionButton(P, icon=ft.Icons.OPEN_IN_NEW_ROUNDED, on_click=lambda e: handlers["open_url"](), tooltip="Open in browser", size=36),
                ft.Container(width=Space.xs),
                IconActionButton(P, icon=ft.Icons.QR_CODE_ROUNDED, on_click=lambda e: handlers["show_qr"](), tooltip="Show QR code", size=36),
                ft.Container(width=Space.sm),
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
    port_field = TextInput(P, hint="8000", value=state.port)

    iface_options = [
        ft.dropdown.Option(key=str(i), text=f"{label} · {ip}")
        for i, (label, ip) in enumerate(state.interfaces)
    ] or [ft.dropdown.Option(key="0", text="All Interfaces · 0.0.0.0")]

    iface_dropdown = ft.Dropdown(
        value=str(state.iface_index),
        options=iface_options,
        on_select=lambda e: handlers["on_iface_change"](int(e.control.value or "0")),
        height=44, border_radius=Radius.lg, bgcolor=P["surface_2"],
        border_color=P["border"], focused_border_color=P["text"],
        color=P["text"], text_style=ft.TextStyle(color=P["text"], size=14),
        border_width=1, content_padding=ft.Padding.symmetric(horizontal=Space.md, vertical=0),
    )

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
                            DestructiveButton(P, "Stop Server", icon=ft.Icons.STOP_ROUNDED, on_click=toggle_server)
                            if state.server_running else
                            PrimaryButton(P, "Start Server", icon=ft.Icons.PLAY_ARROW_ROUNDED, on_click=toggle_server)
                        ),
                        expand=True,
                    ),
                    ft.Container(width=Space.sm),
                    ft.Container(
                        content=SecondaryButton(P, "Refresh IP", icon=ft.Icons.REFRESH_ROUNDED, on_click=lambda e: handlers["refresh_ip"]()),
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
            folder_info_text = info.summary
        except Exception:
            folder_info_text = "Unable to read folder"
    else:
        folder_info_text = "No folder selected"

    # Improved folder info block with larger icon and text
    folder_info = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.FOLDER_ROUNDED, size=20, color=P["text_muted"]),
                    width=40, height=40, bgcolor=P["surface_2"],
                    border_radius=Radius.md, alignment=ft.Alignment.CENTER,
                ),
                ft.Container(width=Space.md),
                ft.Column(
                    [
                        ft.Text("Current Folder", color=P["text_muted"], size=12, weight=ft.FontWeight.W_500),
                        ft.Container(height=4),
                        ft.Text(
                            folder_info_text, color=P["text"], size=14, weight=ft.FontWeight.W_500,
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=0, tight=True, expand=True,
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
            folder_info,
        ],
        spacing=0, tight=True,
    )

    folder = SectionCard(
        P, dark=state.dark,
        title="Shared Folder", subtitle=None,
        padding=ft.Padding.symmetric(horizontal=Space.lg, vertical=Space.lg),
        content=folder_content,
    )

    # ============================================================
    # Recent activity
    # ============================================================
    recent_content = ft.Column(
        [LogRow(P, e.time, e.message, e.level) for e in state.logs[-5:]] or
        [ft.Text("No activity yet.", color=P["text_muted"], **Type.body_sm)],
        spacing=Space.sm, tight=True,
    )
    recent = SectionCard(P, dark=state.dark, title="Recent Activity", content=recent_content)

    # ============================================================
    # Layout with Optimized Equal Height Cards
    # ============================================================
    CARD_HEIGHT = 235  # Reduced to minimize empty space

    if is_narrow:
        cards_section = ft.Column(
            [
                server_card,
                ft.Container(height=Space.md),
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
        ft.Container(height=Space.md),
        recent,
    ]

    body_content = ft.Column(layout_items, spacing=0, tight=True)

    return page_scaffold(
        P,
        title="Dashboard",
        subtitle="Server status and controls",
        content=body_content,
        page_width=page_width,
    )