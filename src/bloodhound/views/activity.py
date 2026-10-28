"""Activity — full log history, structured."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Radius, Type
from ..components import SectionCard, LogRow
from ._scaffold import page_scaffold


def build_activity(P, state, handlers, page_width=1200):
    entries = list(reversed(state.logs)) # Newest first

    if entries:
        rows = []
        for i, e in enumerate(entries):
            rows.append(LogRow(P, e.time, e.message, e.level))
            # Add a subtle divider between entries, except for the last one
            if i < len(entries) - 1:
                rows.append(
                    ft.Container(
                        height=1, 
                        bgcolor=P["border"], 
                        margin=ft.Margin.symmetric(vertical=Space.sm, horizontal=Space.xl),
                        opacity=0.5 # Make the divider subtle
                    )
                )
        
        list_content = ft.Column(rows, spacing=0, tight=True)
    else:
        list_content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, size=32, color=P["text_faint"]),
                    ft.Container(height=Space.sm),
                    ft.Text("No activity yet.", color=P["text_muted"], size=14, font_family="Inter"),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            padding=ft.Padding.symmetric(vertical=Space.xl),
            alignment=ft.Alignment.CENTER,
        )

    log_card = SectionCard(
        P, dark=state.dark,
        title="All Activity",
        subtitle=f"{len(entries)} entries",
        content=list_content,
    )

    body = ft.Column(
        [log_card],
        spacing=0,
        tight=True,
    )

    return page_scaffold(
        P,
        title="Activity",
        subtitle="Server log history",
        content=body,
        page_width=page_width,
    )