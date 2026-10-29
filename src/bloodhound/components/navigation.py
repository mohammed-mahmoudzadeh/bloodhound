"""Adaptive navigation — sidebar on desktop, floating bar on mobile."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def NavSidebar(P, selected_index, on_change, destinations, state=None):
    """Sidebar for desktop. Brand is in the top bar; sidebar holds nav + status."""
    items = []
    for i, d in enumerate(destinations):
        selected = (i == selected_index)
        if selected:
            bg = P["surface_2"]
            fg = P["text"]
            icon_color = P["text"]
        else:
            bg = "transparent"
            fg = P["text_dim"]
            icon_color = P["text_muted"]

        item = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(d["icon"], size=22, color=icon_color),
                    ft.Container(width=Space.md),
                    ft.Text(
                        d["label"],
                        size=14,
                        weight=ft.FontWeight.W_500 if selected else ft.FontWeight.W_400,
                        color=fg,
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=Space.md, vertical=12),
            margin=ft.Margin.symmetric(horizontal=Space.sm, vertical=2),
            bgcolor=bg,
            border_radius=Radius.md,
            ink=True,
            on_click=lambda e, idx=i: _dispatch_nav(on_change, idx),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )
        items.append(item)

    nav_block = ft.Container(
        content=ft.Column(items, spacing=0, tight=True),
        padding=ft.Padding.symmetric(vertical=Space.md),
    )

    is_online = bool(state and state.server_running)
    status_color = P["status_online"] if is_online else P["status_offline"]

    status_dot = ft.Container(
        width=8, height=8, 
        border_radius=4, 
        bgcolor=status_color,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            blur_radius=6 if is_online else 0,
            color=status_color,
            spread_radius=1,
        ) if is_online else None,
    )

    status_label = ft.Text(
        "Online" if is_online else "Offline",
        size=13,
        weight=ft.FontWeight.W_600,
        color=P["status_online"] if is_online else P["text_dim"],
    )

    port_label = ft.Text(
        f"Port {state.port}" if state else "Port 8000",
        size=12,
        color=P["text_muted"],
    )

    status_block = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        status_dot,
                        ft.Container(width=Space.sm + 2),
                        status_label,
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                port_label,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=Space.md, vertical=Space.md),
        border=ft.Border.only(top=ft.BorderSide(1, P["border"])),
    )

    sidebar_content = ft.Column(
        [nav_block, ft.Container(expand=True), status_block],
        spacing=0, tight=True, expand=True,
    )

    return ft.Container(
        content=sidebar_content,
        width=220, bgcolor=P["bg"],
        border=ft.Border.only(right=ft.BorderSide(1, P["border"])),
        expand=True,
    )


def NavBar(P, selected_index, on_change, destinations):
    """Mobile — Floating, modern bottom nav bar."""
    
    nav_bar = ft.NavigationBar(
        selected_index=selected_index,
        on_change=on_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icon(d["icon"], size=24, color=P["text_muted"]),
                selected_icon=ft.Icon(d["icon"], size=24, color=P["text"]),
                label=d["label"],
            )
            for d in destinations
        ],
        bgcolor="transparent",
        indicator_color=P["surface_2"],
        elevation=0,
        height=68,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
    )

    return ft.Container(
        content=nav_bar,
        bgcolor=P["surface"],
        border=ft.Border.all(1, P["border"]),
        border_radius=24,
        margin=ft.Margin.only(left=16, right=16, bottom=16),
        shadow=ft.BoxShadow(
            blur_radius=20,
            color="#000000" if P["bg"] == "#000000" else "#00000010",
            offset=ft.Offset(0, 4),
        ),
    )


def _dispatch_nav(on_change, index: int):
    class _E:
        def __init__(self, idx):
            self.control = self
            self.selected_index = idx
    try:
        on_change(_E(index))
    except Exception:
        pass


def NavRail(P, selected_index, on_change, destinations, state=None):
    return NavSidebar(P, selected_index, on_change, destinations, state=state)