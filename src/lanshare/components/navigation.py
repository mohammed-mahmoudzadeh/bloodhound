"""Adaptive navigation — sidebar on desktop, bar on mobile."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type


def NavSidebar(P, selected_index, on_change, destinations, state=None):
    """Sidebar for desktop. Brand is in the top bar; sidebar holds nav + status."""
    # ---- Nav items ----
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
                    ft.Icon(d["icon"], size=18, color=icon_color),
                    ft.Container(width=Space.md),
                    ft.Text(
                        d["label"],
                        size=13,
                        weight=ft.FontWeight.W_500 if selected
                               else ft.FontWeight.W_400,
                        color=fg,
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(
                horizontal=Space.md, vertical=10),
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

    # ---- Status block (bottom) ----
    is_online = bool(state and state.server_running)
    status_color = P["status_online"] if is_online else P["status_offline"]

    status_dot = ft.Container(
        width=8,
        height=8,
        border_radius=4,
        bgcolor=status_color,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    status_label = ft.Text(
        "Online" if is_online else "Offline",
        size=12,
        weight=ft.FontWeight.W_500,
        color=P["status_online"] if is_online else P["text_muted"],
    )

    port_label = ft.Text(
        f"Port {state.port}" if state else "Port 8000",
        size=11,
        color=P["text_faint"],
    )

    status_block = ft.Container(
        content=ft.Column(
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
                ft.Container(height=2),
                ft.Container(
                    content=port_label,
                    padding=ft.Padding.only(left=16),
                ),
            ],
            spacing=0,
            tight=True,
        ),
        padding=ft.Padding.symmetric(
            horizontal=Space.md, vertical=Space.md),
        border=ft.Border.only(top=ft.BorderSide(1, P["border"])),
    )

    sidebar_content = ft.Column(
        [
            nav_block,
            ft.Container(expand=True),
            status_block,
        ],
        spacing=0,
        tight=True,
        expand=True,
    )

    return ft.Container(
        content=sidebar_content,
        width=220,
        bgcolor=P["bg"],
        border=ft.Border.only(right=ft.BorderSide(1, P["border"])),
        expand=True,
    )


def NavBar(P, selected_index, on_change, destinations):
    """Mobile — bottom nav bar without selected-item shadow."""
    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=on_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icon(d["icon"], color=P["text_muted"]),
                selected_icon=ft.Icon(d["icon"], color=P["text"]),
                label=d["label"],
            )
            for d in destinations
        ],
        bgcolor=P["bg"],
        indicator_color="transparent",
        elevation=0,
        height=64,
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


# Backwards-compat alias
def NavRail(P, selected_index, on_change, destinations, state=None):
    return NavSidebar(
        P, selected_index, on_change, destinations, state=state)
