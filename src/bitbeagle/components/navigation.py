"""Sidebar navigation component — modern, minimal, and balanced."""
from __future__ import annotations

import asyncio

import flet as ft

from ..theme import Space, Radius


def NavSidebar(P, selected_index, on_change, items, state=None):
    """Modern sidebar with subtle active indicators and hover effects."""

    def _nav_item(index, icon, label):
        is_active = selected_index == index

        text_color = P["text"] if is_active else P["text_muted"]
        icon_color = P["primary"] if is_active else P["text_muted"]
        bg_color = P["surface_2"] if is_active else "transparent"
        font_weight = ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500

        indicator = ft.Container(
            width=3,
            height=18,
            border_radius=ft.BorderRadius.only(top_right=4, bottom_right=4),
            bgcolor=P["primary"] if is_active else "transparent",
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        icon_widget = ft.Icon(icon, size=20, color=icon_color)
        text_widget = ft.Text(label, size=14, color=text_color, weight=font_weight)

        item_content = ft.Container(
            content=ft.Row(
                [
                    indicator,
                    ft.Container(width=Space.sm),
                    icon_widget,
                    ft.Container(width=Space.md),
                    text_widget,
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=10, horizontal=Space.md),
            border_radius=Radius.md,
            bgcolor=bg_color,
            ink=True,
            on_click=lambda e: on_change(index),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        if not is_active:
            def _on_hover(e):
                try:
                    if e.data == "true":
                        item_content.bgcolor = P["surface"]
                        icon_widget.color = P["text_dim"]
                        text_widget.color = P["text_dim"]
                    else:
                        item_content.bgcolor = "transparent"
                        icon_widget.color = P["text_muted"]
                        text_widget.color = P["text_muted"]
                    item_content.update()
                except Exception:
                    pass
            item_content.on_hover = _on_hover

        return item_content

    nav_items = []
    for i, item in enumerate(items):
        nav_items.append(_nav_item(i, item["icon"], item["label"]))
        if i < len(items) - 1:
            nav_items.append(ft.Container(height=2))

    # ----- Footer: server status with pulsing online dot -----
    footer_controls = []
    pulse_target = {"control": None}

    if state is not None:
        server_running = getattr(state, "server_running", False)
        status_text = "Online" if server_running else "Offline"
        port_text = getattr(state, "port", "8000")

        if server_running:
            dot_color = "#22c55e"
            # Layered dot: soft halo + solid center
            halo = ft.Container(
                width=14, height=14, border_radius=7,
                bgcolor=dot_color, opacity=0.25,
            )
            core = ft.Container(
                width=7, height=7, border_radius=3.5,
                bgcolor=dot_color,
                alignment=ft.Alignment.CENTER,
            )
            status_dot: ft.Control = ft.Stack(
                [halo, core],
                width=14, height=14,
                alignment=ft.Alignment.CENTER,
            )
            pulse_target["control"] = halo
        else:
            status_dot = ft.Container(
                width=7, height=7, border_radius=3.5,
                bgcolor=P["text_faint"],
            )

        footer_controls = [
            ft.Container(
                height=1,
                bgcolor=P["border"],
                margin=ft.Margin.symmetric(vertical=Space.md, horizontal=Space.md),
            ),
            ft.Container(
                content=ft.Row(
                    [
                        status_dot,
                        ft.Container(width=Space.sm),
                        ft.Text(status_text, size=12, color=P["text_muted"],
                                weight=ft.FontWeight.W_500),
                        ft.Container(expand=True),
                        ft.Text(f"Port {port_text}", size=12, color=P["text_muted"]),
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=Space.md, vertical=Space.sm),
            ),
        ]

    root = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(nav_items, spacing=0, tight=True),
                    padding=ft.Padding.symmetric(horizontal=Space.sm, vertical=Space.md),
                ),
                ft.Container(expand=True),
                ft.Column(footer_controls, spacing=0, tight=True),
            ],
            spacing=0,
            expand=True,
        ),
        width=200,
        bgcolor=P["bg"],
        border=ft.Border.only(right=ft.BorderSide(1, P["border"])),
        expand=True,
    )

    # Kick off the async pulse once the control is mounted on a page.
    halo_ctrl = pulse_target["control"]
    if halo_ctrl is not None:
        async def _pulse():
            while True:
                halo_ctrl.opacity = 0.45
                try: halo_ctrl.update()
                except Exception: pass
                await asyncio.sleep(0.9)
                halo_ctrl.opacity = 0.10
                try: halo_ctrl.update()
                except Exception: pass
                await asyncio.sleep(0.9)

        def _start_pulse(_e=None):
            try:
                root.page.run_task(_pulse)
            except Exception:
                pass

        root.on_update = _start_pulse

    return root