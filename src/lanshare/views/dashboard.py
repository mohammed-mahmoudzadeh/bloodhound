"""Dashboard — polished, monochrome."""
from __future__ import annotations

import flet as ft

from ..config import IS_ANDROID
from ..core.fileinfo import scan_folder
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
    # Hero — access URL
    # ============================================================
    if is_narrow:
        # On mobile, hide the "http://" prefix — space is tight.
        url_display = state.access_url.replace("http://", "", 1)

        hero_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WIFI_ROUNDED, size=18,
                                            color=P["text"]),
                            width=36, height=36,
                            bgcolor=P["surface_2"],
                            border=ft.Border.all(1, P["border"]),
                            border_radius=Radius.lg,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(width=Space.sm + 2),
                        ft.Text("ACCESS URL", color=P["text_muted"],
                                **Type.label_sm),
                        ft.Container(expand=True),
                        StatusChip(
                            P,
                            "Online" if state.server_running else "Offline",
                            "online" if state.server_running else "offline",
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=Space.md),
                ft.Row(
                    [
                        ft.Text(
                            url_display,
                            color=P["text"],
                            size=14,
                            weight=ft.FontWeight.W_700,
                            selectable=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            expand=True,
                        ),
                        ft.Container(width=Space.xs),
                        IconActionButton(
                            P,
                            icon=ft.Icons.CONTENT_COPY_ROUNDED,
                            on_click=lambda e: handlers["copy_url"](),
                            tooltip="Copy URL",
                            size=32,
                        ),
                        ft.Container(width=2),
                        IconActionButton(
                            P,
                            icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                            on_click=lambda e: handlers["open_url"](),
                            tooltip="Open in browser",
                            size=32,
                        ),
                        ft.Container(width=2),
                        IconActionButton(
                            P,
                            icon=ft.Icons.QR_CODE_ROUNDED,
                            on_click=lambda e: handlers["show_qr"](),
                            tooltip="Show QR code",
                            size=32,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=0,
            tight=True,
        )
    else:
        hero_content = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.WIFI_ROUNDED, size=18,
                                    color=P["text"]),
                    width=40, height=40,
                    bgcolor=P["surface_2"],
                    border=ft.Border.all(1, P["border"]),
                    border_radius=Radius.lg,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(width=Space.md),
                ft.Column(
                    [
                        ft.Text("ACCESS URL", color=P["text_muted"],
                                **Type.label_sm),
                        ft.Container(height=2),
                        ft.Text(
                            state.access_url,
                            color=P["text"],
                            size=16,
                            weight=ft.FontWeight.W_700,
                            selectable=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=0, tight=True, expand=True,
                ),
                IconActionButton(
                    P,
                    icon=ft.Icons.CONTENT_COPY_ROUNDED,
                    on_click=lambda e: handlers["copy_url"](),
                    tooltip="Copy URL",
                    size=36,
                ),
                ft.Container(width=Space.xs),
                IconActionButton(
                    P,
                    icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                    on_click=lambda e: handlers["open_url"](),
                    tooltip="Open in browser",
                    size=36,
                ),
                ft.Container(width=Space.xs),
                IconActionButton(
                    P,
                    icon=ft.Icons.QR_CODE_ROUNDED,
                    on_click=lambda e: handlers["show_qr"](),
                    tooltip="Show QR code",
                    size=36,
                ),
                ft.Container(width=Space.sm),
                StatusChip(
                    P,
                    "Online" if state.server_running else "Offline",
                    "online" if state.server_running else "offline",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    hero = SectionCard(
        P, dark=state.dark, padding=Space.lg,
        content=hero_content,
    )

    # ============================================================
    # Server card
    # ============================================================
    port_field = TextInput(P, hint="8000", value=state.port)

    iface_options = [
        ft.dropdown.Option(
            key=str(i),
            text=f"{label} · {ip}",
        )
        for i, (label, ip) in enumerate(state.interfaces)
    ] or [
        ft.dropdown.Option(key="0", text="All Interfaces · 0.0.0.0"),
    ]

    iface_dropdown = ft.Dropdown(
        value=str(state.iface_index),
        options=iface_options,
        on_select=lambda e: handlers["on_iface_change"](
            int(e.control.value or "0")),
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

    server_card = SectionCard(
        P, dark=state.dark,
        title="Server",
        subtitle="Choose interface and port, then start.",
        padding=ft.Padding.symmetric(
            horizontal=Space.lg,
            vertical=Space.lg,
        ),
        content=ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=LabeledField(P, "Port", port_field),
                            col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                        ),
                        ft.Container(
                            content=LabeledField(
                                P, "Interface", iface_dropdown,
                            ),
                            col={"xs": 12, "sm": 6, "md": 8, "lg": 9},
                        ),
                    ],
                    spacing=Space.md,
                    run_spacing=Space.md,
                ),
                vspace(Space.lg),
                ft.Row(
                    [
                        ft.Container(
                            content=(
                                DestructiveButton(
                                    P, "Stop Server",
                                    icon=ft.Icons.STOP_ROUNDED,
                                    on_click=toggle_server)
                                if state.server_running else
                                PrimaryButton(
                                    P, "Start Server",
                                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                    on_click=toggle_server)
                            ),
                            width=160,
                        ),
                        ft.Container(
                            content=SecondaryButton(
                                P, "Refresh IP",
                                icon=ft.Icons.REFRESH_ROUNDED,
                                on_click=lambda e: handlers["refresh_ip"]()),
                            width=140,
                        ),
                    ],
                    spacing=Space.sm,
                    wrap=True,
                    run_spacing=Space.sm,
                ),
            ],
            spacing=0, tight=True,
        ),
    )

    # ============================================================
    # Shared folder card
    # ============================================================
    folder_buttons_children = [
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=SecondaryButton(
                        P, "Pick folder",
                        icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                        on_click=lambda e: handlers["pick_folder"]()),
                    col={"xs": 12, "sm": 6},
                ),
                ft.Container(
                    content=SecondaryButton(
                        P, "Share all",
                        icon=ft.Icons.PUBLIC_ROUNDED,
                        on_click=lambda e: handlers["share_all"]()),
                    col={"xs": 12, "sm": 6},
                ),
            ],
            spacing=Space.sm,
            run_spacing=Space.sm,
        ),
    ]

    if IS_ANDROID:
        folder_buttons_children.append(ft.Container(height=Space.sm))
        folder_buttons_children.append(
            SecondaryButton(
                P, "Permissions",
                icon=ft.Icons.SHIELD_ROUNDED,
                on_click=lambda e: handlers["request_permissions"]()),
        )
        folder_buttons_children.append(ft.Container(height=Space.sm))
        folder_buttons_children.append(
            SecondaryButton(
                P, "Battery Exemption",
                icon=ft.Icons.BATTERY_ALERT_ROUNDED,
                on_click=lambda e: handlers["request_battery_exemption"]()),
        )

    if state.share_dir:
        try:
            info = scan_folder(state.share_dir)
            folder_info_text = info.summary
        except Exception:
            folder_info_text = "Unable to read folder"
    else:
        folder_info_text = "No folder selected"

    folder_info = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.FOLDER_ROUNDED,
                        size=14, color=P["text_faint"]),
                ft.Container(width=Space.sm),
                ft.Text(
                    folder_info_text,
                    color=P["text_faint"],
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    **Type.label_sm,
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(top=Space.lg),
    )

    folder = SectionCard(
        P, dark=state.dark,
        title="Shared Folder",
        subtitle=state.share_dir_display,
        padding=ft.Padding.symmetric(
            horizontal=Space.lg,
            vertical=Space.lg,
        ),
        content=ft.Column(
            folder_buttons_children + [folder_info],
            spacing=0,
            tight=True,
        ),
    )

    # ============================================================
    # Recent activity
    # ============================================================
    recent_content = ft.Column(
        [LogRow(P, e.time, e.message, e.level)
         for e in state.logs[-5:]] or
        [ft.Text("No activity yet.", color=P["text_muted"],
                 **Type.body_sm)],
        spacing=Space.sm,
        tight=True,
    )

    recent = SectionCard(
        P, dark=state.dark,
        title="Recent Activity",
        content=recent_content,
    )

    # ============================================================
    # Layout
    # ============================================================
    body_content = ft.Column(
        [
            hero,
            ft.Container(height=Space.md),
            ft.ResponsiveRow(
                [
                    ft.Container(server_card, col={"xs": 12, "md": 6, "lg": 7}),
                    ft.Container(folder, col={"xs": 12, "md": 6, "lg": 5}),
                ],
                spacing=Space.md,
                run_spacing=Space.md,
            ),
            ft.Container(height=Space.md),
            recent,
        ],
        spacing=0,
        tight=True,
    )

    return page_scaffold(
        P,
        title="Dashboard",
        subtitle="Server status and controls",
        content=body_content,
        page_width=page_width,
    )
